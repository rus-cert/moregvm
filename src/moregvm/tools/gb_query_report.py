#!/usr/bin/env python3

import argparse
import collections
import gvm.errors
import sys
import xml.etree.ElementTree as ET

import moregvm

from typing import Dict

# Globals
debug=False
quiet=False
status=False

DEFAULT_FILTERSTRING = "apply_overrides=1 sort=created rows=-1 notes=0 overrides=0"

DEFAULT_COLUMNS = {
    "result": ["uuid", "host", "port", "severity", "name"],
}

class GbQueryReport(moregvm.LazyTool):
    """
    Get results from a report

    The 'report' argument is to be specified as:
        * a report UUID
        * a task name (with -t/--task)
        * a path (with -f/--file)
        * '-' for standard input (with -f/--file)

    Refer to the results columns listed in "gb_querytool --help" for a list
    of possible columns.

    Examples:
        $ gb_query_report 5e4554ea-df35-45f4-8637-d14f1634466d name,severity
        $ gb_query_report -f ./export.xml name,severity
        $ gb_query_report -t uni-240305-UST-TS-EXAMPLE name,severity
    """

    @classmethod
    def custom_args(cls, parser: argparse.ArgumentParser):
        # Our arguments are too complex for the other methods
        parser.add_argument("report", help="Report to query")
        parser.add_argument("columns", default=[], nargs='?', help="What columns to include", type=moregvm.separated_list)
        parser.add_argument("-q", "--quiet", help="Suppress progress indication", action="store_true")
        parser.add_argument("-d", "--debug", help="Print debugging messages", action="store_true")
        parser.add_argument("-f", "--file", help="Read the report locally from a file", action="store_true")
        parser.add_argument("-t", "--task", help="Use task name instead of a report UUID", action="store_true")
        parser.add_argument("--fenced", help="Fence in the output with a type line and a 'LAST' line", action="store_true")
        parser.add_argument("--experimental", help=argparse.SUPPRESS, action="store_true")
        parser.add_argument("--all", help="Output ALL available columns", action="store_true")
        parser.add_argument("--format", default="csv", help="Output format", choices=moregvm.output_obj_names)

    def tool_main(self) -> None:
        global debug, quiet, status
        (debug, quiet) = (self.args["debug"], self.args["quiet"])
        status = not quiet and sys.stderr.isatty() and not sys.stdout.isatty()

        if '"' in self.args["report"]:
            raise moregvm.PermanentError("Double quote characters are not allowed")

        if self.args["file"] and self.args["task"]:
            raise moregvm.PermanentError("Options -f/--file and -t/--task are mutually exclusive")

        # columns
        col_names = self.args["columns"]
        available_cols = collections.ChainMap(moregvm.COLUMNS["result"], moregvm.GLOBAL_COLUMNS)
        cols = {}
        options = dict(moregvm.OPTIONS["result"])

        if self.args["experimental"]:
            self.errprint('WARNING: EXPERIMENTAL features are enabled. Semantics are subject to change and'
                    + ' the identical command line may fail in the future.')
        if not len(col_names):
            if not (self.args["experimental"] or self.args["all"]):
                raise moregvm.PermanentError('ERROR: Calling gb_querytool without a list of columns is'
                        + ' EXPERIMENTAL. If you really want to go ahead, pass "--experimental" or "--all".')
            if self.args["all"]:
                col_names = available_cols.keys()
            else:
                col_names = DEFAULT_COLUMNS["result"]
        else:
            if self.args["all"]:
                raise moregvm.PermanentError('ERROR: You cannot specify a list of columns and pass "--all"'
                        + ' at the same time.')
        for col in col_names:
            if col not in available_cols:
                raise moregvm.PermanentError(f'ERROR: Unknown column type "{col}"')
            if available_cols[col] == NotImplemented:
                raise NotImplementedError(f'ERROR: column type "{col}" is not yet implemented')
            cols[col] = available_cols[col]

        # format
        output = moregvm.output_obj_by_name(self.args["format"])

        # get the results
        if self.args["file"]:
            try:
                if self.args["report"] == "-":
                    xml_file = ET.parse(sys.stdin)
                else:
                    xml_file = ET.parse(self.args["report"])
            except OSError as ex:
                raise moregvm.PermanentError(f"{ex.strerror}: '{ex.filename}'")
            results = xml_file.findall('./report/results/result')
        else:
            self.connect()
            if self.gmp is None:
                raise moregvm.InternalError("GMP connection not established")
            if self.args["task"]:
                task = self.gmp.get_tasks(filter_string=f"name={self.args['report']}")
                if task.xpath('task_count/filtered')[0].text != "0":
                    last_report_id = task.xpath('./task/last_report/report')[0].attrib['id']
                    report = self.gmp.get_report(report_id=last_report_id, filter_string=DEFAULT_FILTERSTRING)
                else:
                    raise moregvm.PermanentError("Task not found")
            else:
                try:
                    report = self.gmp.get_report(report_id=self.args["report"], filter_string=DEFAULT_FILTERSTRING)
                except gvm.errors.GvmResponseError as ex:
                    if ex.status == "404":
                        raise moregvm.PermanentError("Report not found")
                    raise
            results = report.findall('./report/report/results/result')

        # actually run the query
        if self.args["fenced"]: self.output(f'gb_query_report:{self.args["format"]}:result')
        output.start(sys.stdout, col_names)
        for result in results:
            record = {}
            for cn in col_names:
                col_obj = cols[cn]
                col_value = col_obj.extract(result)
                record[cn] = col_value
            output.record(record)
        output.end()
        if self.args["fenced"]: self.output(f'LAST')

if __name__ == '__main__':
    GbQueryReport.run_from_sysargs()

