#!/usr/bin/env python3

import json
import os

from gvm.protocols.gmp.requests.v226 import AliveTest, HostsOrdering

import moregvm

CONFIG_FILENAME = ".config/gb-tools-default-values.json"

CONFIG_VALUES = {
    "portlist": "UUID of greenbone port list",
    "scanner": "UUID of greenbone scanner",
    "scanconfig": "UUID of greenbone scan config",
    "alivetest": "Name of alive test (e.g. 'ICMP Ping')",
}

def read_config():
    configpath = os.path.join(os.environ['HOME'], CONFIG_FILENAME)
    if os.path.exists(configpath):
        with open(configpath, 'r') as cfg:
            return json.load(cfg)
    else:
        return {}

# get ips into right form
def split_hosts_ip(string):
    inc_ips = string.strip('[').strip(']').split(',')
    inc_ips = [a.strip() for a in inc_ips if len(a)]
    return inc_ips

class GbSetupAndStartScan(moregvm.Tool):
    """
    This script requests a target name and a list of IPs to create a
    target and task and starts it automatically.

    Example:
        $ gb_setup_and_start_scan "uni-240305-UST-TS-EXAMPLE" 127.0.0.1
    """

    @classmethod
    def required_args(cls):
        return {
            "target_name": "Name of the target",
            "hosts_ip": "List of hosts IP addresses",
        }

    @classmethod
    def option_args(cls):
        config = read_config()

        result=dict()
        for name, description in CONFIG_VALUES.items():
            if name in config:
                result[name] = (description, config[name])
            else:
                result[name] = (description, ...)
        return result

    @classmethod
    def toggles(cls):
        return {
            "overwrite": "Try deleting a target if one already exists with a conflicting name"
        }

    def tool_main(self) -> None:
        target_name = self.args["target_name"]
        hosts_ip = split_hosts_ip(self.args["hosts_ip"])
        portlist = self.args["portlist"]
        alivetest = self.args["alivetest"]
        scanconfig = self.args["scanconfig"]
        scanner = self.args["scanner"]
        overwrite = self.args["overwrite"]

        # conflicting target name handling
        get_targets_r = self.gmp.get_targets(
            filter_string=f'name="{target_name}"'
        )
        if get_targets_r.xpath("target_count/filtered")[0].text != "0":
            if overwrite:
                old_target_id = get_targets_r.xpath('target')[0].attrib['id']
                self.output(f"deleting conflicting target {old_target_id}")
                self.gmp.delete_target(old_target_id)
            else:
                raise moregvm.PermanentError(
                    f"Target '{target_name}' already exists in user "
                    f"'{self.user}' and you didn't pass --overwrite."
                )

        target = self.gmp.create_target(name=target_name, hosts=hosts_ip, port_list_id=portlist, alive_test=AliveTest(alivetest))
        target_id = target.attrib['id']

        task = self.gmp.create_task(name=target_name, config_id=scanconfig, target_id=target_id, scanner_id=scanner, alterable=True, schedule_id=None)

        task_id = task.attrib['id']
        started_task = self.gmp.start_task(task_id=task_id)
        report_id = started_task.find("./report_id").text

        self.output("target", target_id, sep='\t')
        self.output("task",   task_id,   sep='\t')
        self.output("report", report_id, sep='\t')
        self.output(f"(user {self.user}) https://{self.gmp_hostname}/report/{report_id}")

if __name__ == '__main__':
    GbSetupAndStartScan.run_from_sysargs()
