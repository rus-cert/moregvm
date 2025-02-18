#!/usr/bin/env python3

from typing import Dict

import moregvm

PAGESIZE=25

class GbStatusSummary(moregvm.Tool):
    """
    Shows the status of reports (Running, Done, etc.)

    Examples:
        $ gb_status_summary
        $ gb_status_summary --all
        $ gb_status_summary --all --list
    """

    @classmethod
    def toggles(cls):
        return {
            "all":  "Shows all reports including those that are Done",
            "list": "Print a list rather than a count"
        }

    def tool_main(self) -> None:
        flag_all = self.args["all"]
        flag_list = self.args["list"]

        filter_string = 'apply_overrides=0 min_qod=70 sort=date'
        if not flag_all:
            filter_string += ' not status="Done"'

        totalcount_resp = self.gmp.get_reports(filter_string='rows=1 ' + filter_string)
        totalcount = int(totalcount_resp.find("./report_count/filtered").text)

        count: Dict[str, int] = {}

        pos = 1
        tcnt_errmsg = ''
        while pos <= totalcount:
            pagination = f"rows={PAGESIZE} first={pos}"
            pos += PAGESIZE

            reports = self.gmp.get_reports(filter_string=pagination + " " + filter_string, details=False, note_details=False, override_details=False)
            report_list = reports.xpath("./report/report")

            current_totalcount = int(reports.find("./report_count/filtered").text)
            if totalcount != current_totalcount:
                tcnt_errmsg += f' to {current_totalcount}'

            for report in report_list:
                status_xml = report.find("./scan_run_status")
                status = status_xml.text
                if flag_list:
                    self.output(report.attrib['id'], status)
                else:
                    if status in count:
                        count[status] += 1
                    else:
                        count[status] = 1

        for status in sorted(count):
            self.output(status, count[status])

        if tcnt_errmsg:
            raise moregvm.TemporaryError(f'Total count changed from {totalcount}{tcnt_errmsg} during execution. Results are probably inconsistent.')

if __name__ == "__main__":
    GbStatusSummary.run_from_sysargs()
