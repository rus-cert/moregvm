#!/usr/bin/env python3

import json

import moregvm

class GbGetReportFormatIds(moregvm.Tool):
    """
    This script requests report format IDs and writes them to /home/tools/.config/gb-tools-report-format-ids_v2.json

    Example:
        $ gb_get_report_format_ids
    """
    def tool_main(self) -> None:
        # dict to collect report formats
        dat_json = {}

        # requests report foramts
        report_format = self.gmp.get_report_formats()
        report_format_ids = report_format.findall('./report_format')
        report_format_extensions = report_format.findall('./')

        # iterates through elements
        # nested JSON 
        with open("/home/tools/.config/gb-tools-report-format-ids_v2.json", "w") as f:
            for ids in report_format_ids:
                id_type = {}
                id_type["uuid"] = ids.attrib['id']
                id_type["extension"] = ids.find('./extension').text
                dat_json[ids.find('./name').text] = id_type
            f.write(json.dumps(dat_json))

if __name__ == '__main__':
    GbGetReportFormatIds.run_from_sysargs()
