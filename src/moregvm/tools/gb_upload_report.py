#!/usr/bin/env python3

import sys

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


class GbUploadReport(moregvm.Tool):
    """
    Upload a report to a container task

    This tool reads XML from standard output unless --input is given. It pairs well
    with the gb_merge_reports and gb_download_report tools.

    Examples:
        $ zcat archived_report.xml.gz | gb_upload_report "target task"
        $ gb_upload_report -i ./file.xml "target task"
        $ gb_merge_reports --user=u1 -t TASK1 TASK2 | gb_upload_report --user=u2 -n NEWTASK
    """

    @classmethod
    def toggles(cls) -> dict[str | tuple[str, str], str]:
        return {("n", "new"): "Create a new container task by that name"}

    @classmethod
    def required_args(cls) -> dict[str, str]:
        return {"task_name": "Name of the container task to upload the report into"}

    @classmethod
    def option_args(cls) -> dict[str | tuple[str, str], tuple[str, object]]:
        return {("i", "input"): ("Input file. Defaults to '-' for stdin.", "-")}

    def tool_main(self) -> None:
        try:
            if self.args["input"] == "-":
                xml_file = lxml.etree.parse(sys.stdin)
            else:
                xml_file = lxml.etree.parse(self.args["input"])
        except OSError as ex:
            raise moregvm.PermanentError(f"{ex.strerror}: '{ex.filename}'")

        get_tasks_r = self.gmp.get_tasks(
            filter_string=f'name="{self.args['task_name']}"'
        )
        if self.args["new"]:
            if get_tasks_r.xpath("task_count/filtered")[0].text != "0":
                raise moregvm.PermanentError(
                    f"Task '{self.args['task_name']}' already exists in user "
                    f"'{self.user}' but you passed -n/--new on the command line."
                )
            task = self.gmp.create_container_task(self.args["task_name"])
            task_id = task.attrib["id"]
        else:
            if get_tasks_r.xpath("task_count/filtered")[0].text == "0":
                raise moregvm.PermanentError(
                    f"Task '{self.args['task_name']}' not found in user '{self.user}'. "
                    "Use -n/--new on the command line to create a new task by that name."
                )
            if get_tasks_r.xpath("./task/target")[0].attrib["id"]:
                raise moregvm.PermanentError(
                    f"The task '{self.args['task_name']}' is an ordinary task, not a "
                    "container task. Reports can only be uploaded into container tasks."
                )
            task_id = get_tasks_r.xpath("./task")[0].attrib["id"]

        self.gmp.import_report(
            report=lxml.etree.tostring(xml_file, encoding=str),
            task_id=task_id,
            in_assets=False,
        )


if __name__ == "__main__":
    GbUploadReport.run_from_sysargs()
