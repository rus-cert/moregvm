# moregvm

This repository contains various utilities built using [python-gvm](https://pypi.org/project/python-gvm/).
They are designed to allow easy scripting of workflows that involve a GVM instance (or appliance).

Refer to [TOOLS.md](TOOLS.md) for an overview of all included tools along with their help text.

## Setup from source

The source code repository is structured in the the python packaging format and includes a PEP 621 pyproject.toml.

For convenience, the following scripts are provided:

* `setup_local.bash`  
  Creates a local venv in the directory `.venv` and installs this package plus all dependencies there using pip.
* `setup_local_unisolated.bash`  
  Same as `create_local.bash` but access to system site packages is allowed.
  Use this if you want to use system packages to avoid building everything from source.

### Example on Debian-like distributions

Builing psycopg2 from source requires pg_config, a C toolchain and python as well as postgresql development headers.
To avoid this and use system versions:

```terminal
$ sudo apt install python3-all-venv python3-setuptools python3-psycopg2
$ ./setup_local_unisolated.bash
```

To use, you can either directly call the scripts from the .venv/bin/gb_* directory or:

```terminal
$ . .venv/bin/activate
$ gb_export_ips --help
```

## Status for the included tools

`moregvm` is a project mostly developed for in-house use by the maintainer(s).
The project only receives limited development time and resources.
Not all included tools are maintained equally well.
An overview:

| Name                     | Status |
| ------------------------ | ------ |
| gb_db_import             | 🟢     |
| gb_db_import_results     | 🟢     |
| gb_db_init               | 🟢     |
| gb_db_migrate            | 🟢     |
| gb_delete_old            | 🔴     |
| gb_delete_report         | 🟢     |
| gb_download_report       | 🟢     |
| gb_export_ips            | 🟡     |
| gb_get_report_format_ids | 🔴     |
| gb_make_all_visible_for  | 🟢     |
| gb_query_report          | 🟡     |
| gb_querytool             | 🟢     |
| gb_report_status         | 🟡     |
| gb_setup_and_start_scan  | 🟢     |
| gb_status_summary        | 🟡     |
| gb_task_status           | 🟡     |
| gb_web_filter            | 🟢     |

| Status | Details |
| :----: | ------- |
| 🟢     | In active use by the upstream maintainer(s). Any bugs arre likely to receive timely fixes. |
| 🟡     | Rarely used. Bugs are more likely. |
| 🔴     | Not in use by the upstream maintainer(s). Bugs likely. Bug reports unlikely to be processed unless accompanied by a pull request that includes a fix. |
