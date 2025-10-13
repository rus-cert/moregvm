import json
import os
from typing import Any

import moregvm

CREDENTIAL_FILENAME = "moregvm-credentials.json"
DATABASE_FILENAME = "moregvm-database.json"


def config_paths() -> list[str]:
    return [
        os.path.join(os.path.dirname(moregvm.__file__), "config", "default"),
        os.path.join(os.environ["HOME"], ".config"),
        os.path.join(os.path.dirname(moregvm.__file__), "config", "local"),
    ]


def load_json(path: str) -> dict[str, Any]:
    if os.path.exists(path):
        with open(path, "r") as cfg:
            return json.load(cfg)
    else:
        return {}


def load_layered_config(name: str) -> dict[str, Any]:
    conf = {}
    for confdir in config_paths():
        path = os.path.join(confdir, name)
        conf.update(load_json(path))
    return conf


def credentials() -> dict[str, Any]:
    return load_layered_config(CREDENTIAL_FILENAME)


def database() -> dict[str, Any]:
    return load_layered_config(DATABASE_FILENAME)
