#!/usr/bin/env python3

import moregvm

class GbDeleteReport(moregvm.Tool):
    """
    Delete a report, its task and its target.

    Example:
        $ gb_delete_report f94ff9ad-6911-477f-a0ab-189c6a81da8c
    """
    @classmethod
    def required_args(cls):
        return {
            "report_id": "UUID of report"
        }
    def tool_main(self) -> None:
        report_id = self.args["report_id"]

        response = self.gmp.get_report(
            report_id=report_id, report_format_id=None
        )

        # get task_id and target_id
        task_id = response.xpath('report/task')[0].attrib['id']
        target_id = response.xpath('report/report/task/target')[0].attrib['id']

        # delete given report
        self.gmp.delete_report(report_id)

        # delete given task
        self.gmp.delete_task(task_id, ultimate=False)

        # delete given target
        self.gmp.delete_target(target_id, ultimate=False)

if __name__ == '__main__':
    GbDeleteReport.run_from_sysargs()
