#!/usr/bin/env python3

import argparse
import sys
import uuid
from pathlib import Path

import gvm.errors
import lxml.etree

import moregvm

# Globals
debug = False
quiet = False
status = False

DEFAULT_FILTERSTRING = "apply_overrides=1 sort=created rows=-1 notes=0 overrides=0"

REPORT_OUTER_PROPS = {
    "format_id": "a994b278-1f62-11e1-96ac-406186ea4fc5",
    "extension": "xml",
    "content_type": "text/xml",
}

COMBINE_INNER = {
    "port": {"start": "1", "max": "-1"},
    "result": {"start": "1", "max": "-1"},
    "error": None,
    "tls_certificate": None,
}
COMBINE_OUTER = ["host"]


class GbMergeReports(moregvm.LazyTool):
    """
    Merge several reports into one

    The 'reports' argument is to be specified as:
        * report UUIDs
        * task name (with -t/--task)
        * paths to files (with -f/--file)
        * '-' for standard input (with -f/--file)

    This tool outputs XML to standard output unless --output is given. It pairs well
    with the gb_upload_report tool.

    Examples:
        $ gb_merge_reports 12345678-1234-1234-1234-1234567890ab 12345678-1234-1234-1234-1234567890ab
        $ gb_merge_reports -f ./first.xml ./second.xml
        $ gb_merge_reports -t uni-2510-SAMPLE uni-2510-SAMPLE2
        $ gb_merge_reports --user=u1 -t TASK1 TASK2 | gb_upload_report --user=u2 -n NEWTASK
    """

    @classmethod
    def toggles(cls) -> dict[str | tuple[str, str], str]:
        return {
            "force": "Combine --output with --force to overwrite a file",
            ("f", "file"): "Read the reports locally from files",
            ("t", "task"): "Use task names instead of report UUIDs",
        }

    @classmethod
    def custom_args(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("reports", nargs="+", help="Reports to merge")
        parser.add_argument(
            "-o",
            "--output",
            help="Destination for merged report. Defaults to '-' for stdout",
            default="-",
        )

    def tool_main(self) -> None:
        for reportspec in self.args["reports"]:
            if '"' in reportspec:
                raise moregvm.PermanentError("Double quote characters are not allowed")
        if self.args["file"] and self.args["task"]:
            raise moregvm.PermanentError(
                "Options -f/--file and -t/--task are mutually exclusive"
            )
        if self.args["file"] and self.args["reports"].count("-") > 1:
            raise moregvm.PermanentError(
                "file '-' (standard input) can be specified at most once"
            )
        if not self.args["file"]:
            self.connect()

        rid = str(uuid.uuid4())
        # combined_outer is the new report as etree
        combined_outer = lxml.etree.Element("report", {"id": rid, **REPORT_OUTER_PROPS})
        combined_outer.append(
            combined_inner := lxml.etree.Element("report", {"id": rid})
        )
        combined_inner.append(lxml.etree.Element("ports"))
        combined_inner.append(
            lxml.etree.Element("results", {"start": "1", "max": "-1"})
        )

        # get the results
        for reportspec in self.args["reports"]:
            if self.args["file"]:
                try:
                    if reportspec == "-":
                        xml_file = lxml.etree.parse(sys.stdin)
                    else:
                        xml_file = lxml.etree.parse(reportspec)
                except OSError as ex:
                    raise moregvm.PermanentError(f"{ex.strerror}: '{ex.filename}'")
                report = lxml.etree.Element(  # make a fake get_reports_response
                    "get_reports_response", status="200", status_text="OK"
                )
                report.append(xml_file.getroot())
            else:
                if self.gmp is None:
                    raise moregvm.InternalError("GMP connection not established")
                if self.args["task"]:
                    task = self.gmp.get_tasks(filter_string=f'name="{reportspec}"')
                    if task.xpath("task_count/filtered")[0].text != "0":
                        last_report_id = task.xpath("./task/last_report/report")[
                            0
                        ].attrib["id"]
                        report = self.gmp.get_report(
                            report_id=last_report_id, filter_string=DEFAULT_FILTERSTRING
                        )
                    else:
                        raise moregvm.PermanentError("Task not found")
                else:
                    try:
                        report = self.gmp.get_report(
                            report_id=reportspec, filter_string=DEFAULT_FILTERSTRING
                        )
                    except gvm.errors.GvmResponseError as ex:
                        if ex.status == "404":
                            raise moregvm.PermanentError("Report not found")
                        raise
            for tname, attrib in COMBINE_INNER.items():
                envelope = lxml.etree.Element(tname + "s", attrib)
                combined_inner.append(envelope)
                for e in report.findall(f"./report/report/{tname}s/{tname}"):
                    envelope.append(e)
            for tname in COMBINE_OUTER:
                for e in report.findall(f"./report/report/{tname}"):
                    combined_inner.append(e)

        if self.args["output"] == "-":
            sys.stdout.flush()
            sys.stdout.buffer.write(lxml.etree.tostring(combined_outer))
            sys.stdout.buffer.flush()
        else:
            out_path = Path(self.args["output"])
            if out_path.exists() and self.args["force"]:
                raise moregvm.PermanentError(
                    "File already exists. Use --force to overwrite."
                )
            out_path.write_bytes(lxml.etree.tostring(combined_outer))


if __name__ == "__main__":
    GbMergeReports.run_from_sysargs()
