#!/usr/bin/env python3
import sys

import moregvm

from gvm.protocols.gmp.requests.v224 import FilterType

DEFAULT_FILTER_SETTINGS = {
    "alert": "b833a6f2-dcdc-4535-bfb0-a5154b5b5092",
    "asset": "0f040d06-abf9-43a2-8f94-9de178b0e978",
    "certbund": "e4cf514a-17e2-4ab9-9c90-336f15e24750",
    "cpe": "3414a107-ae46-4dea-872d-5c4479a48e8f",
    "credential": "186a5ac8-fe5a-4fb1-aa22-44031fb339f3",
    "cve": "def63b5a-41ef-43f4-b9ef-03ef1665db5d",
    "dfncert": "312350ed-bc06-44f3-8b3f-ab9eb828b80b",
    "filter": "f9691163-976c-47e7-ad9a-38f2d5c81649",
    "group": "f722e5a4-88d8-475f-95b9-e4dcafbc075b",
    "host": "37562dfe-1f7e-4cae-a7c0-fa95e6f194c5",
    "operatingsystem": "f608c3ec-ce73-4ff6-8e04-7532749783af",
    "override": "eaaaebf1-01ef-4c49-b7bb-955461c78e0a",
    "note": "96abcd5a-9b6d-456c-80b8-c3221bfa499d",
    "nvt": "bef08b33-075c-4f8c-84f5-51f6137e40a3",
    "permission": "ffb16b28-538c-11e3-b8f9-406186ea4fc5",
    "portlist": "7d52d575-baeb-4d98-bb68-e1730dbc6236",
    "report": "48ae588e-9085-41bc-abcb-3d6389cf7237",
    "reportformat": "249c7a55-065c-47fb-b453-78e11a665565",
    "result": "739ab810-163d-11e3-9af6-406186ea4fc5",
    "role": "f38e673a-bcd1-11e2-a19a-406186ea4fc5",
    "scanconfig": "1a9fbd91-0182-44cd-bc88-a13a9b3b1bef",
    "scanner": "ba00fe91-bdce-483c-b8df-2372e9774ad6",
    "schedule": "a83e321b-d994-4ae8-beec-bfb5fe3e7336",
    "tag": "108eea3b-fc61-483c-9da9-046762f137a8",
    "target": "236e2e41-9771-4e7a-8124-c432045985e0",
    "task": "1c981851-8244-466c-92c4-865ffe05e721",
    "ticket": "801544de-f06d-4377-bb77-bbb23369bad4",
    "tlscertificate": "34a176c1-0278-4c29-b84d-3d72117b2169",
    "user": "a33635be-7263-4549-bd80-c04d2dba89b4",
    "vulnerability": "17c9d269-95e7-4bfa-b1b2-bc106a2175c7",
};

ERRMSG_UNKNOWN_TYPE = "Invalid filter type."
ERRMSG_UNKNOWN_FILTER = "Filter not found."

class GbWebFilter(moregvm.Tool):
    """
    This script interacts with the stored filters in the greenbone web
    interface.

    Run "gb_web_filter SUBCOMMAND --help" for help for a specific command.

    Example:
        $ gb_web_filter list TYPE
        $ gb_web_filter show TYPE NAME
        $ gb_web_filter create TYPE NAME FILTERSTRING
        $ gb_web_filter update TYPE NAME FILTERSTRING
        $ gb_web_filter create-or-update TYPE NAME FILTERSTRING
        $ gb_web_filter delete TYPE NAME
        $ gb_web_filter get-default-filter TYPE
        $ gb_web_filter set-default-filter TYPE NAME
        $ gb_web_filter unset-default-filter TYPE
    """


    @classmethod
    def toggles(cls):
        return {
            "verbose": "Show an indication of the changes that have been made."
        }

    @classmethod
    def custom_args(cls, parser):

        subparsers = parser.add_subparsers(dest="command")

        list_parser = subparsers.add_parser("list", help="list all filters of a given type")
        list_parser.add_argument( "filter_type", help="the type of filter to operate on" )

        show_parser = subparsers.add_parser("show", help="shows a stored filter string")
        show_parser.add_argument( "filter_type", help="the type of filter to operate on" )
        show_parser.add_argument( "filter_name", help="the name of filter to show" )

        create_parser = subparsers.add_parser("create", help="create a new filter")
        create_parser.add_argument( "filter_type", help="the type of filter to be created" )
        create_parser.add_argument( "filter_name", help="the name of the new filter" )
        create_parser.add_argument( "filter_string", help="the filter string to be set" )
        
        update_parser = subparsers.add_parser("update", help="update a filter")
        update_parser.add_argument( "filter_type", help="the type of filter to be updated" )
        update_parser.add_argument( "filter_name", help="the name of the filter to be updated" )
        update_parser.add_argument( "filter_string", help="the filter string to be set" )

        create_or_update_parser = subparsers.add_parser("create-or-update", help="update a filter")
        create_or_update_parser.add_argument( "filter_type", help="the type of filter to operate on" )
        create_or_update_parser.add_argument( "filter_name", help="the name of the filter to be created or updated" )
        create_or_update_parser.add_argument( "filter_string", help="the filter string to be set" )

        delete_parser = subparsers.add_parser("delete", help="delete a filter")
        delete_parser.add_argument( "filter_type", help="the type of filter to be deleted" )
        delete_parser.add_argument( "filter_name", help="the name of the filter to be deleted" )

        get_default_filter_parser = subparsers.add_parser("get-default-filter", help="show the name of the default filter for a given type")
        get_default_filter_parser.add_argument( "filter_type", help="the filter type to check" )

        set_default_filter_parser = subparsers.add_parser("set-default-filter", help="set the default filter for a given type")
        set_default_filter_parser.add_argument( "filter_type", help="the type of filter to operate on" )
        set_default_filter_parser.add_argument( "filter_name", help="the name of the filter to be set as default" )

        unset_default_filter_parser = subparsers.add_parser("unset-default-filter", help="remove a default filter assignment for a given type")
        unset_default_filter_parser.add_argument( "filter_type", help="the type of filter to operate on" )

    def tool_main(self) -> None:

        filter_types = { "alert", "secinfo", "asset", "credential", "filter", "group", "host", "note", "os", "override",
                "permission", "port_list", "report", "report_format", "result", "role", "config", "schedule",
                "tag", "target", "task", "ticket", "tls_certificate", "user", "vuln" }

        if 'filter_name' in self.args and '"' in self.args['filter_name']:
            raise moregvm.PermanentError("Double quote characters are not allowed in filter names.")

        match self.args["command"]:
            case 'list':
                if self.args["filter_type"] in filter_types:
                    content = self.gmp.get_filters(filter_string=f"type={self.args['filter_type']}")
                    for element in content.xpath('filter/name'):
                        self.output(element.text)
                else:
                    raise moregvm.PermanentError(ERRMSG_UNKNOWN_TYPE)

            case 'show':
                if self.args["filter_type"] in filter_types:
                    response = self.gmp.get_filters(filter_string=f"type={self.args['filter_type']} and name=\"{self.args['filter_name']}\"")
                    empty_check = response.xpath('filter_count/filtered')[0].text
                    if empty_check != "0":
                        selected_filter = response.xpath('filter/term')[0].text
                    else:
                        raise moregvm.PermanentError(ERRMSG_UNKNOWN_FILTER)
                    self.output(selected_filter)
                else:
                    raise moregvm.PermanentError(ERRMSG_UNKNOWN_TYPE)

            case 'create':
                if self.args["filter_type"] in filter_types:
                    empty_check = self.gmp.get_filters(filter_string=f"type={self.args['filter_type']} and name=\"{self.args['filter_name']}\"").xpath('filter_count/filtered')[0].text
                    if empty_check == "0":
                        filtertype = FilterType.from_string(self.args['filter_type'])
                        self.gmp.create_filter(f"{self.args['filter_name']}", filter_type=filtertype, term=f"{self.args['filter_string']}")
                        if self.args["verbose"]:
                            self.output(f"Filter {self.args['filter_name']} with filter_type {self.args['filter_type']} and filter_string '{self.args['filter_string']}' was created.")
                    else:
                        raise moregvm.PermanentError("Name already in use.")
                else:
                    raise moregvm.PermanentError(ERRMSG_UNKNOWN_TYPE)
            
            case 'update':
                if self.args["filter_type"] in filter_types:
                    response = self.gmp.get_filters(filter_string=f"type={self.args['filter_type']} and name=\"{self.args['filter_name']}\"")
                    empty_check = response.xpath('filter_count/filtered')[0].text
                    if empty_check != "0":
                        filtertype = FilterType.from_string(self.args['filter_type'])
                        filter_id = response.xpath('filter')[0].attrib['id']
                    else:
                        raise moregvm.PermanentError(ERRMSG_UNKNOWN_FILTER)
                    self.gmp.modify_filter(filter_id, filter_type=filtertype, name=f"{self.args['filter_name']}", term=f"{self.args['filter_string']}")
                    if self.args["verbose"]:
                        self.output(f"Filter {self.args['filter_name']} with filter_type {self.args['filter_type']} and filter_string '{self.args['filter_string']}' was modified.")
                else:
                    raise moregvm.PermanentError(ERRMSG_UNKNOWN_TYPE)

            case 'create-or-update':
                if self.args["filter_type"] in filter_types:
                    filtertype = FilterType.from_string(self.args['filter_type'])
                    response = self.gmp.get_filters(filter_string=f"type={self.args['filter_type']} and name=\"{self.args['filter_name']}\"")
                    empty_check = response.xpath('filter_count/filtered')[0].text
                    if empty_check == "0":
                        self.gmp.create_filter(f"{self.args['filter_name']}", filter_type=filtertype, term=f"{self.args['filter_string']}")
                        if self.args["verbose"]:
                            self.output(f"Filter {self.args['filter_name']} with filter_type {self.args['filter_type']} and filter_string '{self.args['filter_string']}' was created.")
                    else:
                        filter_id = response.xpath('filter')[0].attrib['id']
                        self.gmp.modify_filter(filter_id, filter_type=filtertype, name=f"{self.args['filter_name']}", term=f"{self.args['filter_string']}")
                        if self.args["verbose"]:
                            self.output(f"Filter {self.args['filter_name']} with filter_type {self.args['filter_type']} and filter_string '{self.args['filter_string']}' was modified.")
                else:
                    raise moregvm.PermanentError(ERRMSG_UNKNOWN_TYPE)

            case 'delete':
                if self.args["filter_type"] in filter_types:
                    response = self.gmp.get_filters(filter_string=f"type={self.args['filter_type']} and name=\"{self.args['filter_name']}\"")
                    empty_check = response.xpath('filter_count/filtered')[0].text
                    if empty_check != "0":
                        filter_id = response.xpath('filter')[0].attrib['id']
                    else:
                        raise moregvm.PermanentError(ERRMSG_UNKNOWN_FILTER)
                    self.gmp.delete_filter(filter_id)
                    if self.args["verbose"]:
                        self.output(f"Filter {self.args['filter_name']} with type {self.args['filter_type']} deleted.")
                else:
                    raise moregvm.PermanentError(ERRMSG_UNKNOWN_TYPE)

            case 'get-default-filter':
                if self.args["filter_type"] in filter_types:
                    response = self.gmp.get_user_setting(DEFAULT_FILTER_SETTINGS[self.args['filter_type']])
                    filter_id = response.xpath('./setting/value')[0].text
                    filters = self.gmp.get_filters(filter_string=f"type={self.args['filter_type']} \"")
                    for filters in filters.findall('filter'):
                        if filters.xpath('.')[0].attrib['id'] == filter_id:
                            filter_name = filters.xpath('name')[0].text
                            if self.args["verbose"]:
                                print(f"Default filter for type {self.args['filter_type']}: {filter_name}")
                            else:
                                print(f"{filter_name}")
                        else:
                            if self.args["verbose"]:
                                raise moregvm.PermanentError(f"No default filter set for type {self.args['filter_type']}.")
                else:
                    raise moregvm.PermanentError(ERRMSG_UNKNOWN_TYPE)

            case 'set-default-filter':
                if self.args["filter_type"] in filter_types:
                    response = self.gmp.get_filters(filter_string=f"type={self.args['filter_type']} and name=\"{self.args['filter_name']}\"")
                    empty_check = response.xpath('filter_count/filtered')[0].text
                    if empty_check != "0":
                        filter_id = response.xpath('filter')[0].attrib['id']
                        self.gmp.modify_user_setting(setting_id=DEFAULT_FILTER_SETTINGS[self.args['filter_type']], value=filter_id)
                        if self.args["verbose"]:
                            print(f"Default filter for type {self.args['filter_type']} has been set to {self.args['filter_name']}.")
                    else:
                        raise moregvm.PermanentError(ERRMSG_UNKNOWN_FILTER)
                else:
                    raise moregvm.PermanentError(ERRMSG_UNKNOWN_TYPE)

            case 'unset-default-filter':
                if self.args["filter_type"] in filter_types:
                    self.gmp.modify_user_setting(setting_id=DEFAULT_FILTER_SETTINGS[self.args['filter_type']], value="0")
                    if self.args["verbose"]:
                        print(f"Default filter for type {self.args['filter_type']} has been reset.")
                else:
                    raise moregvm.PermanentError(ERRMSG_UNKNOWN_TYPE)
            case _:
                raise moregvm.PermanentError("No command supplied on the command line. Run 'gb_web_filter --help' for usage information.")

if __name__ == '__main__':
    GbWebFilter.run_from_sysargs()
