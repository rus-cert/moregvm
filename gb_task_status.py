#!/usr/bin/env python3
import sys

import moregvm

class GbTaskStatus(moregvm.Tool):
    """
    This script requests the given task and returns it status.

    Example:
        $ gb_task_status d34a201e-cf36-4a38-bcfe-811c43c65622
    """
    @classmethod
    def required_args(cls):
        return {
            "task_id": "UUID of task"
        }
    def tool_main(self) -> None:
        task_id = self.args["task_id"]

        task_response = self.gmp.get_task(task_id=task_id)
        content = task_response.find('./task/status').text
        self.output(content)

if __name__ == '__main__':
    GbTaskStatus.run_from_sysargs()
