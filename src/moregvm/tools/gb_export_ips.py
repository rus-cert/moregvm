#!/usr/bin/env python3

import sys
import argparse
from typing import Dict, List, Set, cast

import lxml.etree

import moregvm

class GbExportIps(moregvm.Tool):
    """
    Request results by filter string and return all matching IPs

    Example:
        $ gb_export_ips "name~uni-230601-UST"
    """
    @classmethod
    def custom_args(cls, parser: argparse.ArgumentParser):
        # Our arguments are too complex for the other methods
        parser.add_argument("filterstring", help="Filter string for greenbone")
        parser.add_argument("--pagesize", default=None, help="pagination size")
        parser.add_argument("--sort", help="Sorted output (doesn't output in real-time)", action="store_true")

    def tool_main(self) -> None:
        filterstring = self.args["filterstring"]
        options: Dict[str, object] = {}

        resource_iter = moregvm.resources_gen(self, "result", filterstring, options, self.args["pagesize"])
        ips: Set[str] = set()
        for resource in resource_iter:
            hosts = cast(List[lxml.etree._Element], resource.xpath("host"))
            for element in hosts:
                if not element.text:
                    raise moregvm.InternalError("Greenbone returned a result with an empty host")
                if not self.args["sort"] and element.text not in ips:
                    print(element.text)
                ips.add(element.text)
        if self.args["sort"]:
            for ip in sorted(ips):
                print(ip)

if __name__ == '__main__':
    GbExportIps.run_from_sysargs()

