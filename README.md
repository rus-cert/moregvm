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
  Same as `create_local.bash` but system site packages will be used where possible rather than installing all dependencies from PyPI.
  Use this if you want to use system packages to avoid building everything from source (see next section).

### Example: Getting started quickly

It may be undesirable to install everything from pip beacuse building psycopg2 from source requires a C toolchain, pg_config as well as python and postgresql development headers.
To avoid this and use system versions instead (package names in this example are from Debian):

```terminal
$ sudo apt install python3-all-venv python3-setuptools python3-psycopg2
$ ./setup_local_unisolated.bash
```

To use, you can either directly call the scripts from the .venv/bin/gb_* directory or let the venv activate script set your PATH:

```terminal
$ . .venv/bin/activate
$ gb_export_ips --help
```

## Greenbone credentials configuration

To configure access to your greenbone instance/appliance, place credentials in the file `$HOME/.config/moregvm-credentials.json`:

```json
{
  "hostname": "gb.example.com",
  "default_user": "user1",
  "users": {
    "user1": "password1",
    "user2": "password2"
  }
}
```

You can omit `default_user`, it will default to `dev`.

## Database configuration

If you wish to use the `gb_db_*` tools, you may need to configure access to a Postgres database under `$HOME/.config/moregvm-database.json`:

```json
{
  "dsn": "dbname=test user=postgres password=secret"
}
```

Psycopg2 expects the connection information as a _data source name_, `dsn`.
Its value needs to be specified as a [libpq connection string].

You can _skip_ the database config entirely if connections with an empty dsn work in your setup.
Typically an empty dsn works if:
* database name, database username and unix username are identical
* Postgres runs locally
* the unix user can access the postgres socket file and unix credential authentication is enabled

[libpq connection string]: https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING

## Usage notes

Some code in this project assumes that names of some OpenVAS resources (e.g. tasks, targets, filters) are unique among all resources of that type which can be seen by the current user.
Please note that OpenVAS does not enforce uniqueness of all names and conflicts may lead to unexpected behavior.

`moregvm` is a project mostly developed for in-house use by the maintainer(s).
The project only receives limited development time and resources and the included tools receive different levels of testing and maintenance.
Refer to the following section for details:

### Status of included tools

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
| gb_merge_reports         | 🟡     |
| gb_query_report          | 🟡     |
| gb_querytool             | 🟢     |
| gb_report_status         | 🟡     |
| gb_setup_and_start_scan  | 🟢     |
| gb_status_summary        | 🟡     |
| gb_task_status           | 🟡     |
| gb_upload_report         | 🟡     |
| gb_web_filter            | 🟢     |

| Status | Details |
| :----: | ------- |
| 🟢     | In active use by the upstream maintainer(s). Any bugs are likely to receive timely fixes. |
| 🟡     | Rarely used. Bugs are more likely. |
| 🔴     | Not in use by the upstream maintainer(s). Bugs likely. Bug reports unlikely to be processed unless accompanied by a pull request that includes a fix. |
