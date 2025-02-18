#!/usr/bin/env python3

import moregvm

from datetime import date, datetime

class GbDeleteOld(moregvm.Tool):
    """
    Find all specified reports and deletes them along with their corresponding
    tasks and targets, selected by a prefix and an age threshold.

    Example:
        $ gb_delete_old "uni-240305-" 4
    """
    @classmethod
    def required_args(cls):
        return {
            "prefix": "Delete reports whose task name starts with this string",
            "days": "Age threshold in days"
        }
    def tool_main(self) -> None:
        prefix = self.args["prefix"]
        days_thresh = self.args["days"]

        try:
            days_thresh = int(days_thresh)
        except:
            raise moregvm.PermanentError("Threshold is in an incorrect format. Run with --help for help.")

        response = self.gmp.get_reports()

        report = response.xpath('report')

        time_now = datetime.now()

        for element in report:
            report_id = element.attrib['id']
            task_id = element.xpath('task')[0].attrib['id']
            task_name = element.xpath('task/name')[0].text
            target_id = element.xpath('report/task/target')[0].attrib['id']

            if (task_name.startswith(prefix)):
                report_creation_time = element.xpath('creation_time')[0].text
                report_creation_time_date = datetime.strptime(report_creation_time, "%Y-%m-%dT%H:%M:%SZ")
                diff = datetime.today() - report_creation_time_date
                diff_seconds = diff.total_seconds()

                if diff_seconds > days_thresh * 60 * 60 * 24: # scan is older
                    self.gmp.delete_report(report_id)
                    self.gmp.delete_task(task_id, ultimate=False)
                    self.gmp.delete_target(target_id, ultimate=False)

if __name__ == '__main__':
    GbDeleteOld.run_from_sysargs()
