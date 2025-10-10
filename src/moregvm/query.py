import csv
import json
from abc import ABC, abstractmethod
from typing import Any, Iterator, TextIO

import gvm.xml

import moregvm.tool

FALLBACK_PAGE_SIZE = 25

DEFAULT_PAGE_SIZES = {
    "note": 200,
    "override": 50,
    "permission": 50,
    "result": 200,
    "target": 50,
    "task": 50,
}

class AbstractOutput(ABC):
    @abstractmethod
    def start(self, out: TextIO, colnames: list[str]) -> None:
        ...
    @abstractmethod
    def record(self, record: dict[str, Any]) -> None:
        ...
    def end(self) -> None:
        pass

class JSONOutput(AbstractOutput):
    def start(self, out: TextIO, colnames: list[str]) -> None:
        self.out = out
        self.started=False
        print("[", end='', file=self.out)
    def record(self, record: dict[str, Any]) -> None:
        if self.started:
            print(",", end='', file=self.out)
        self.started=True
        json.dump(record, self.out)
    def end(self) -> None:
        print("]", file=self.out)

class JSONLOutput(AbstractOutput):
    def start(self, out: TextIO, colnames: list[str]) -> None:
        self.out = out
    def record(self, record: dict[str, Any]) -> None:
        json.dump(record, self.out)
        print("", file=self.out)

class CSVNoHeaderOutput(AbstractOutput):
    def start(self, out: TextIO, colnames: list[str]) -> None:
        self.writer = csv.DictWriter(out, colnames)
    def record(self, record: dict[str, Any]) -> None:
        self.writer.writerow(record)

class CSVOutput(CSVNoHeaderOutput):
    def start(self, out: TextIO, colnames: list[str]) -> None:
        super().start(out, colnames)
        self.writer.writeheader()

class RawOutput(AbstractOutput):
    def start(self, out: TextIO, colnames: list[str]) -> None:
        self.out = out
    def record(self, record: dict[str, Any]) -> None:
        for column in record:
            print(record[column], file=self.out)

output_obj_names = ["csv", "csvnohead", "json", "jsonl", "raw"]
def output_obj_by_name(name: str) -> AbstractOutput:
    match name:
        case "csv":
            return CSVOutput()
        case "csvnohead":
            return CSVNoHeaderOutput()
        case "json":
            return JSONOutput()
        case "jsonl":
            return JSONLOutput()
        case "raw":
            return RawOutput()
        case _:
            raise RuntimeError(f"Output format {name} is unknown")


def resources_gen(
    tool: moregvm.tool.Tool,
    restype: str,
    filter: str,
    options: dict[str, object],
    page_size: int | None = None,
    debug: bool = False,
    status: bool = False,
) -> Iterator[gvm.xml.Element]:
    if page_size == None:
        if restype in DEFAULT_PAGE_SIZES:
            page_size = DEFAULT_PAGE_SIZES[restype]
        else:
            page_size = FALLBACK_PAGE_SIZE
    else:
        page_size = int(page_size)

    if not (page_size == -1 or page_size >= 1):
        raise moregvm.PermanentError('Page size must either be -1 or a positive integer')

    if restype == "config":
        getter = getattr(tool.gmp, f'get_scan_{restype}s')
    else:
        getter = getattr(tool.gmp, f'get_{restype}s')

    totalcount = None
    previous_totalcount = None

    pos = 1
    tcnt_errmsg = ''
    while True:
        if status and page_size != -1: moregvm.progress_indicator(pos-1, totalcount)
        pagination = f"rows={page_size} first={pos}"

        # Add a default sorting (sort=created) to the end - greenbone uses the
        # the first sort[-reverse]= so that any user-supplied sorting will
        # take precedence over this default.
        resources = getter(filter_string=pagination + " " + filter + " sort=created", **options)
        resource_list = resources.xpath(f"./{restype}")

        current_totalcount = int(resources.find(f"./{restype}_count/filtered").text)
        if totalcount is None: # only runs on first iteration
            totalcount = previous_totalcount = current_totalcount
        else:
            if previous_totalcount != current_totalcount:
                tcnt_errmsg += f' to {current_totalcount}'
                previous_totalcount = current_totalcount

        for resource in resource_list:
            if debug: tool.errprint(f"saw {restype} {resource.attrib['id']}")
            yield resource

        pos += page_size
        if pos > totalcount or page_size == -1:
            break

    if status and page_size != -1: moregvm.progress_indicator_erase()
    if tcnt_errmsg:
        raise moregvm.TemporaryError(f'Total count of {restype}s changed from {totalcount}{tcnt_errmsg} during execution. Results are probably inconsistent. Aborting.')
