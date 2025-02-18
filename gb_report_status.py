#!/usr/bin/env python3
import sys

import moregvm

class GbReportStatus(moregvm.Tool):
    """
    This script requests the given report and returns it status.

    Example:
        $ gb_report_status 0bdeb40a-b2a2-4e3a-ab9f-0809d89a3489
    """
    @classmethod
    def required_args(cls):
        return {
            "report_id": "UUID of report"
        }
    def tool_main(self) -> None:
        report_id = self.args["report_id"]

        report_response = self.gmp.get_report(report_id=report_id)
        task_id = report_response.find('./report/task').attrib['id']

        task_response = self.gmp.get_task(task_id=task_id)
        content = task_response.find('./task/status').text
        self.output(content)

if __name__ == '__main__':
    GbReportStatus.run_from_sysargs()
