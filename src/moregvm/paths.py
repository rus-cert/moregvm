import re
from abc import ABC, abstractmethod
from typing import Any

import gvm.xml


class AbstractPath(ABC):
    """Represents a way to extract a piece of information from a result XML object."""

    @abstractmethod
    def extract(self, xml: gvm.xml.Element) -> str | None: ...


class SimplePathText(AbstractPath):
    """Inner text of an element"""

    def __init__(self, path: str):
        self.path = path

    def extract(self, xml: gvm.xml.Element) -> str | None:
        el = xml.find(self.path)
        return None if el is None else el.text


class SimplePathAttr(AbstractPath):
    """Specific attribute of an element"""

    def __init__(self, path: str, attr: str):
        self.path = path
        self.attr = attr

    def extract(self, xml: gvm.xml.Element) -> str | None:
        el = xml.find(self.path)
        if el is None or self.attr not in el.attrib:
            return None
        return str(el.attrib[self.attr])


class SplitTagsPath(AbstractPath):
    """Split the inner text of an element (greenbone-specific pipe-separated format)"""

    def __init__(self, path: str, attr: str):
        self.path = path
        self.attr = attr
        self.pattern = re.compile(rf"(?:^|\|){self.attr}=([^|]*)(?:$|\|)")

    def extract(self, xml: gvm.xml.Element) -> str | None:
        el = xml.find(self.path)
        if el is None or el.text is None:
            return None
        match = self.pattern.search(el.text)
        return None if match is None else match.group(1)


class FanPathText(AbstractPath):
    """Extract from key-value structure <x><name>key</name><value>value</value></x>"""

    def __init__(self, path: str, key: str):
        self.path = path
        self.key = key

    def extract(self, xml: gvm.xml.Element) -> str | None:
        el = xml.find(self.path)
        if el is None:
            return None
        for detail in el:
            name = detail.find("./name")
            value = detail.find("./value")
            if name is not None and self.key == name.text:
                return None if value is None else value.text
        return None


# Constants
GLOBAL_COLUMNS = {
    "uuid": SimplePathAttr(".", "id"),
    "created": SimplePathText("./creation_time"),
    "modified": SimplePathText("./modification_time"),
    "owner": SimplePathText("./owner/name"),
}

COLUMNS: dict[str, dict[str, AbstractPath]] = {
    "task": {
        "name": SimplePathText("./name"),
        "alterable": SimplePathText("./alterable"),
        "comment": SimplePathText("./comment"),
        "severity": SimplePathText("./last_report/report/severity"),
        "status": SimplePathText("./status"),
        "progress": SimplePathText("./progress"),
        "config_id": SimplePathAttr("./config", "id"),
        "report_count": SimplePathText("./report_count"),
        "report_uuid": SimplePathAttr("./last_report/report", "id"),
        "findings_high": SimplePathText("./last_report/report/result_count/hole"),
        "findings_medium": SimplePathText("./last_report/report/result_count/warning"),
        "findings_low": SimplePathText("./last_report/report/result_count/info"),
        "findings_log": SimplePathText("./last_report/report/result_count/log"),
        "findings_false_positive": SimplePathText("./last_report/report/result_count/false_positive"),
    },
    "report": {
        "name": SimplePathText("./name"),
        "comment": SimplePathText("./comment"),
        "severity_full": SimplePathText("./report/severity/full"),
        "severity_filtered": SimplePathText("./report/severity/filtered"),
        "status": SimplePathText("./report/scan_run_status"),
        "progress": SimplePathText("./report/task/progress"),
        "task_uuid": SimplePathAttr("./task", "id"),
        "task_name": SimplePathText("./task/name"),
        "scan_start": SimplePathText("./report/scan_start"),
        "scan_end": SimplePathText("./report/scan_end"),
        "timezone": SimplePathText("./report/timezone"),
        "findings_high": SimplePathText("./report/result_count/hole/filtered"),
        "findings_medium": SimplePathText("./report/result_count/warning/filtered"),
        "findings_low": SimplePathText("./report/result_count/info/filtered"),
        "findings_log": SimplePathText("./report/result_count/log/filtered"),
        "findings_false_positive": SimplePathText("./report/result_count/false_positive/filtered"),
        "findings_high_full": SimplePathText("./report/result_count/hole/full"),
        "findings_medium_full": SimplePathText("./report/result_count/warning/full"),
        "findings_low_full": SimplePathText("./report/result_count/info/full"),
        "findings_log_full": SimplePathText("./report/result_count/log/full"),
        "findings_false_positive_full": SimplePathText("./report/result_count/false_positive/full"),
    },
    "result": {
        "name": SimplePathText("./name"),
        "comment": SimplePathText("./comment"),
        "detection_product": FanPathText("./detection/result/details", "product"),
        "detection_method": FanPathText("./detection/result/details", "source_name"),
        "detection_oid": FanPathText("./detection/result/details", "source_oid"),
        "host": SimplePathText("./host"),
        "hostname": SimplePathText("./host/hostname"),
        "port": SimplePathText("./port"),
        "nvt_oid": SimplePathAttr("./nvt", "oid"),
        "nvt_name": SimplePathText("./nvt/name"),
        "nvt_family": SimplePathText("./nvt/family"),
        "nvt_tags": SimplePathText("./nvt/tags"),
        "nvt_solution": SimplePathText("./nvt/solution"),
        "nvt_cvss_base_vector": SimplePathText("./nvt/severities/severity/value"),
        "nvt_summary": SplitTagsPath("./nvt/tags", "summary"),
        "nvt_insight": SplitTagsPath("./nvt/tags", "insight"),
        "nvt_affected": SplitTagsPath("./nvt/tags", "affected"),
        "nvt_impact": SplitTagsPath("./nvt/tags", "impact"),
        "nvt_vuldetect": SplitTagsPath("./nvt/tags", "vuldetect"),
        "nvt_solution_type": SimplePathAttr("./nvt/solution", "type"),
        "threat": SimplePathText("./threat"),
        "severity": SimplePathText("./severity"),
        "original_threat": SimplePathText("./original_threat"),
        "original_severity": SimplePathText("./original_severity"),
        "qod_value": SimplePathText("./qod/value"),
        "description": SimplePathText("./description"),
    },
    "note": {
        "text": SimplePathText("./text"),
        "nvt_oid": SimplePathAttr("./nvt", "oid"),
        "nvt_name": SimplePathText("./nvt/name"),
        "hosts": SimplePathText("./hosts"),
        "location": SimplePathText("./port"),
        "active": SimplePathText("./active"),
        "in_use": SimplePathText("./in_use"),
        "orphan": SimplePathText("./orphan"),
        "task_uuid": SimplePathAttr("./task", "id"),
        "result_uuid": SimplePathAttr("./result", "id"),
    },
    "override": {
        "text": SimplePathText("./text"),
        "nvt_oid": SimplePathAttr("./nvt", "oid"),
        "nvt_name": SimplePathText("./nvt/name"),
        "hosts": SimplePathText("./hosts"),
        "location": SimplePathText("./port"),
        "severity": SimplePathText("./severity"),
        "new_threat": SimplePathText("./new_threat"),
        "new_severity": SimplePathText("./new_severity"),
        "end_time": SimplePathText("./end_time"),
        "active": SimplePathText("./active"),
        "in_use": SimplePathText("./in_use"),
        "orphan": SimplePathText("./orphan"),
        "task_uuid": SimplePathAttr("./task", "id"),
        "result_uuid": SimplePathAttr("./result", "id"),
    },
    "target": {
        "name": SimplePathText("./name"),
        "comment": SimplePathText("./comment"),
        "hosts": SimplePathText("./hosts"),
        "exclude_hosts": SimplePathText("./exclude_hosts"),
        "writable": SimplePathText("./writable"),
        "allow_simultaneous_ips": SimplePathText("./allow_simultaneous_ips"),
        "alive_tests": SimplePathText("./alive_tests"),
    },
    "config": {
        "name": SimplePathText("./name"),
        "comment": SimplePathText("./comment"),
        "writable": SimplePathText("./writable"),
        "in_use": SimplePathText("./in_use"),
        "family_count": SimplePathText("./family_count"),
        "family_count_growing": SimplePathText("./family_count/growing"),
        "nvt_count": SimplePathText("./nvt_count"),
        "nvt_count_growing": SimplePathText("./nvt_count/growing"),
    },
    "report_format": {
        "name": SimplePathText("./name"),
        "summary": SimplePathText("./summary"),
        "description": SimplePathText("./description"),
        "extension": SimplePathText("./extension"),
        "content_type": SimplePathText("./content_type"),
    },
    "filter": {
        "name": SimplePathText("./name"),
        "comment": SimplePathText("./comment"),
        "term": SimplePathText("./term"),
        "type": SimplePathText("./type"),
    },
    "tag": {
        "name": SimplePathText("./name"),
        "comment": SimplePathText("./comment"),
        "resource_type": SimplePathText("./resources/type"),
        "resource_count": SimplePathText("./resources/count/total"),
        "active": SimplePathText("./active"),
    },
    "user": {
        "name": SimplePathText("./name"),
        "comment": SimplePathText("./comment"),
    },
    "group": {
        "name": SimplePathText("./name"),
        "comment": SimplePathText("./comment"),
    },
    "role": {
        "name": SimplePathText("./name"),
        "comment": SimplePathText("./comment"),
    },
    "permission": {
        "name": SimplePathText("./name"),
        "comment": SimplePathText("./comment"),
        "resource_uuid": SimplePathAttr("./resource", "id"),
        "resource_type": SimplePathText("./resource/type"),
        "resource_name": SimplePathText("./resource/name"),
        "subject_uuid": SimplePathAttr("./subject", "id"),
        "subject_type": SimplePathText("./subject/type"),
        "subject_name": SimplePathText("./subject/name"),
    },
}
OPTIONS: dict[str, dict[str, Any]] = {
    "task": {"details": False},
    "report": {"details": False},
    "result": {"details": False},
    "note": {"details": True},
    "override": {"details": True},
    "config": {"details": False},
    "target": {},
    "report_format": {"details": False},
    "filter": {},
    "tag": {},
    "user": {},
    "group": {},
    "role": {},
    "permission": {},
}
