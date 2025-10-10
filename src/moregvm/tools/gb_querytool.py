#!/usr/bin/env python3

import argparse
import collections
import sys
import textwrap

import moregvm

# Globals
debug = False
quiet = False
status = False

DEFAULT_COLUMNS = {
    "task": ["uuid", "name", "severity"],
    "report": ["uuid", "name", "task_name", "status", "severity_filtered"],
    "result": ["uuid", "host", "port", "severity", "name"],
    "note": ["uuid", "created", "owner", "nvt_oid", "hosts"],
    "override": ["uuid", "created", "owner", "new_severity", "nvt_oid", "hosts"],
    "target": ["uuid", "name", "alive_tests", "hosts"],
    "config": ["uuid", "owner", "writable", "in_use", "name"],
    "filter": ["uuid", "type", "name", "term"],
    "tag": ["uuid", "owner", "name"],
    "user": ["uuid", "created", "name", "owner"],
    "group": ["uuid", "created", "name", "owner"],
    "role": ["uuid", "created", "name", "owner"],
    "permission": ["uuid", "subject_type", "subject_name", "resource_type", "resource_uuid"],
}

class GbQuerytool(moregvm.Tool):
    """
    Run a search in greenbone

    Available columns per type:[PLACEHOLDER]

    Examples:
        $ gb_querytool --user=autoscan report "task~RUS-CERT" uuid,task_name,severity_filtered
        $ gb_querytool results 'severity=10' host,port,name
    """

    @classmethod
    def custom_args(cls, parser: argparse.ArgumentParser):
        # Our arguments are too complex for the other methods
        parser.add_argument("resource_type", help="Type of resource (e.g. 'report')")
        parser.add_argument("filter", help="Filter string for greenbone")
        parser.add_argument("columns", default=[], nargs='?', help="What columns to include", type=moregvm.separated_list)
        parser.add_argument("-q", "--quiet", help="Suppress progress indication", action="store_true")
        parser.add_argument("-d", "--debug", help="Print debugging messages", action="store_true")
        parser.add_argument("--fenced", help="Fence in the output with a type line and a 'LAST' line", action="store_true")
        parser.add_argument("--experimental", help=argparse.SUPPRESS, action="store_true")
        parser.add_argument("--all", help="Output ALL available columns", action="store_true")
        parser.add_argument("--format", default="csv", help="Output format", choices=moregvm.output_obj_names)
        parser.add_argument("--pagesize", default=None, help="pagination size")

    @classmethod
    def help_epilog(cls) -> str | None:
        text = ''
        global_colnames = moregvm.GLOBAL_COLUMNS.keys()
        for restype in moregvm.COLUMNS:
            colnames = moregvm.COLUMNS[restype].keys()
            line = f"{restype}: {' '.join(global_colnames)} {' '.join(colnames)}"
            text += "\n" + textwrap.fill(line, width=100, initial_indent=' '*2, subsequent_indent=' '*4)
        raw_epilog = super().help_epilog() or '[PLACEHOLDER]'
        return raw_epilog.replace('[PLACEHOLDER]', text)

    def tool_main(self) -> None:
        global debug, quiet, status
        (debug, quiet) = (self.args["debug"], self.args["quiet"])
        status = not quiet and sys.stderr.isatty() and not sys.stdout.isatty()
        resource_type = self.args["resource_type"]

        # resource_type
        if resource_type not in moregvm.COLUMNS.keys():
            if resource_type[-1] == 's' and resource_type[:-1] in moregvm.COLUMNS.keys():
                resource_type = resource_type[:-1] # strip off plural 's'
            else:
                raise moregvm.PermanentError(f'Currently only the types {sorted(moregvm.COLUMNS.keys())} are supported')

        # columns
        col_names = self.args["columns"]
        available_cols = collections.ChainMap(moregvm.COLUMNS[resource_type], moregvm.GLOBAL_COLUMNS)
        cols = {}
        options = dict(moregvm.OPTIONS[resource_type])

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
                col_names = DEFAULT_COLUMNS[resource_type]
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

        # actually run the query
        resource_iter = moregvm.resources_gen(self,
                                                resource_type,
                                                self.args["filter"], options,
                                                self.args["pagesize"], debug, status)
        if self.args["fenced"]: self.output(f'gb_querytool:{self.args["format"]}:{resource_type}')
        output.start(sys.stdout, col_names)
        for resource in resource_iter:
            record = {}
            for cn in col_names:
                col_obj = cols[cn]
                col_value = col_obj.extract(resource)
                record[cn] = col_value
                #print(f"-> {cn} {col_value}")
            output.record(record)
        output.end()
        if self.args["fenced"]: self.output(f'LAST')

if __name__ == '__main__':
    GbQuerytool.run_from_sysargs()
