#!/usr/bin/env python3

import json
import os
import sys
import uuid
from base64 import b64decode
from pathlib import Path

import lxml.etree

import moregvm

CONFIG_FILENAME = ".config/gb-tools-report-format-ids_v2.json"
DEFAULT_FORMAT_ID = "1fb9036c-1439-11eb-9d5d-b05cda5b0faa"
DEFAULT_FILTERSTRING = "apply_overrides=1 min_qod=70 sort-reverse=severity rows=-1 levels=hml notes=0 overrides=0"

def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False

def read_config():
    configpath = os.path.join(os.environ['HOME'], CONFIG_FILENAME)
    if os.path.exists(configpath):
        with open(configpath, 'r') as cfg:
            return json.load(cfg)
    else:
        return {}

class GbDownloadReport(moregvm.Tool):
    """
    This script requests a report and exports locally.

    Example:
        $ gb_download_report 123e4567-e89b-12d3-a456-426614174000 --format=1fb9036c-1439-11eb-9d5d-b05cda5b0faa --output=./example_path
    """
    @classmethod
    def toggles(cls):
        return {
            "force": "Use --force to overwrite a file."
        }
    @classmethod
    def required_args(cls):
        return {
            "report_id": "UUID of report"
        }
    @classmethod
    def option_args(cls):
        return {
            "format": ("UUID or name of report format. Defaults to TXT if outputting to"
                + " stdout, otherwise Vulernability Report PDF.", ""),
            "output": ("Filename for downloaded report. Default is '<uuid>.<ext>'."
                + " '-' means output to stdout instead.", ""),
            "replace-filter": ("The filter to pass to Greenbone, in Greenbone filter syntax.", ""),
            "add-filter": ("Additional filter in Greenbone filter syntax."
                + " Use if you want to add to the default filter.", ""),
        }

    def tool_main(self) -> None:
        # load values for report ids with corresponding name
        config = read_config()

        report_id = self.args["report_id"]
        report_format = self.args["format"]

        # checks if report_format_id is valid as uuid or identifier
        if not report_format:
            if self.args["output"] == '-':
                report_format_id = config['TXT']["uuid"]
            else:
                report_format_id = DEFAULT_FORMAT_ID
        elif not is_valid_uuid(report_format):
            if report_format not in config:
                raise moregvm.PermanentError(f"No value for '{report_format}' found in ~/{CONFIG_FILENAME}. An example is PDF or {DEFAULT_FORMAT_ID}.")
            report_format_id = config[report_format]["uuid"]
            report_format_extension = config[report_format]["extension"]

        filterstr = DEFAULT_FILTERSTRING
        if self.args["replace_filter"]:
            filterstr = self.args["replace_filter"]
        if self.args["add_filter"]:
            filterstr += " " + self.args["add_filter"]

        response = self.gmp.get_report(
            report_id=report_id, report_format_id=report_format_id, filter_string=filterstr
        )

        content_type_name = response.find('./report/report_format/name').text

        # checks if file path is given otherwise saves in ./<report_id>.<file_extension>
        if self.args["output"]:
            filename = self.args["output"]
        else:
            filename = report_id +'.'+ report_format_extension

        # get the content of the response
        report_element = response.find("report")

        if 'XML' in report_format:
            file_path = Path(filename)
            xml_report = lxml.etree.tostring(report_element, encoding="utf-8").decode()
            if filename == "-":
                self.output(xml_report)
            elif os.path.exists(file_path):
                if self.args["force"]:
                    output = open(str(file_path), "w")
                    output.write(xml_report)
                    output.close()
                    print("Done. File created: " + str(file_path))
                else:
                    raise moregvm.PermanentError(
                        "File already exists. Use --force or -f to overwrite."
                    )
            else:
                output = open(str(file_path), "w")
                output.write(xml_report)
                output.close()
                print("Done. File created: " + str(file_path))
        else:
            content = report_element.find("report_format").tail
            if not content:
                raise moregvm.PermanentError(
                    """Requested report is empty. Either the report does not contain any
                     results or the necessary tools for creating the report are
                     not installed."""
                    )

            # encodes and sets the path
            binary_base64_encoded_file = content.encode('ascii')
            binary_file = b64decode(binary_base64_encoded_file)
            file_path = Path(filename)

            # checks if file already exists and looks for an force option to overwrite
            # also checks for the case reports should be given out on stdout
            if filename == '-':
                sys.stdout.buffer.write(binary_file)
            elif os.path.exists(file_path):
                if self.args["force"]:
                    file_path.write_bytes(binary_file)
                    print('Done. File created: ' + str(file_path))
                else:
                    raise moregvm.PermanentError("File already exists. Use --force or -f to overwrite.")
            else:
                file_path.write_bytes(binary_file)
                print('Done. File created: ' + str(file_path))

if __name__ == '__main__':
    GbDownloadReport.run_from_sysargs()
