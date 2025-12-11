# List of moregvm tools

A list of all tools with their --help output follows:

## gb_db_import
```
usage: gb_db_import [-h] [--user USER] [-q] [-d] [--pagesize PAGESIZE]
                    resource_type

This script imports a resource_type from greenbone into the database

positional arguments:
  resource_type        Type of resource (e.g. 'report')

options:
  -h, --help           show this help message and exit
  --user USER          Greenbone username
  -q, --quiet          Suppress progress indication
  -d, --debug          Print debugging messages
  --pagesize PAGESIZE  pagination size

Examples:
    $ gb_db_import report
```

## gb_db_import_results
```
usage: gb_db_import_results [-h] [--user USER] [-q] [-d] report

This script imports a result from greenbone into the database.

positional arguments:
  report       report UUID

options:
  -h, --help   show this help message and exit
  --user USER  Greenbone username
  -q, --quiet  Suppress progress indication
  -d, --debug  Print debugging messages

Examples:
    $ gb_db_import_results 32302393-115e-42e4-ba28-14d3899e1db0
```

## gb_db_init
```
usage: gb_db_init [-h] [--user USER]

This script imports the database schema, creating all tables,
indices and constraints

options:
  -h, --help   show this help message and exit
  --user USER  Greenbone username

Example:
    $ gb_db_init
```

## gb_db_migrate
```
usage: gb_db_migrate [-h] [--user USER] version

This script migrates the db from VERSION-1 to VERSION
using migration-VERSION.sql

positional arguments:
  version      Version to migrate to

options:
  -h, --help   show this help message and exit
  --user USER  Greenbone username

Example:
    $ gb_db_migrate 42
```

## gb_delete_old
```
usage: gb_delete_old [-h] [--user USER] prefix days

Find all specified reports and deletes them along with their corresponding
tasks and targets, selected by a prefix and an age threshold.

positional arguments:
  prefix       Delete reports whose task name starts with this string
  days         Age threshold in days

options:
  -h, --help   show this help message and exit
  --user USER  Greenbone username

Example:
    $ gb_delete_old "uni-240305-" 4
```

## gb_delete_report
```
usage: gb_delete_report [-h] [--user USER] report_id

Delete a report, its task and its target.

positional arguments:
  report_id    UUID of report

options:
  -h, --help   show this help message and exit
  --user USER  Greenbone username

Example:
    $ gb_delete_report f94ff9ad-6911-477f-a0ab-189c6a81da8c
```

## gb_download_report
```
usage: gb_download_report [-h] [--user USER] [--force] [--format FORMAT]
                          [--output OUTPUT] [--replace-filter REPLACE_FILTER]
                          [--add-filter ADD_FILTER]
                          report_id

This script requests a report and exports locally.

positional arguments:
  report_id             UUID of report

options:
  -h, --help            show this help message and exit
  --user USER           Greenbone username
  --force               Use --force to overwrite a file.
  --format FORMAT       UUID or name of report format. Defaults to TXT if outputting to stdout, otherwise Vulernability Report PDF.
  --output OUTPUT       Filename for downloaded report. Default is '<uuid>.<ext>'. '-' means output to stdout instead.
  --replace-filter REPLACE_FILTER
                        The filter to pass to Greenbone, in Greenbone filter syntax.
  --add-filter ADD_FILTER
                        Additional filter in Greenbone filter syntax. Use if you want to add to the default filter.

Example:
    $ gb_download_report 123e4567-e89b-12d3-a456-426614174000 --format=1fb9036c-1439-11eb-9d5d-b05cda5b0faa --output=./example_path
```

## gb_export_ips
```
usage: gb_export_ips [-h] [--user USER] [--pagesize PAGESIZE] [--sort]
                     filterstring

Request results by filter string and return all matching IPs

positional arguments:
  filterstring         Filter string for greenbone

options:
  -h, --help           show this help message and exit
  --user USER          Greenbone username
  --pagesize PAGESIZE  pagination size
  --sort               Sorted output (doesn't output in real-time)

Example:
    $ gb_export_ips "name~uni-230601-UST"
```

## gb_get_report_format_ids
```
usage: gb_get_report_format_ids [-h] [--user USER]

This script requests report format IDs and writes them to /home/tools/.config/gb-tools-report-format-ids_v2.json

options:
  -h, --help   show this help message and exit
  --user USER  Greenbone username

Example:
    $ gb_get_report_format_ids
```

## gb_make_all_visible_for
```
usage: gb_make_all_visible_for [-h] [--user USER] [--debug] [--really-change]
                               resource_type principal_type principal_id

Make ALL resources of a given type that the current user owns visible to a principal.

positional arguments:
  resource_type    Type of resource (override or note)
  principal_type   Type of subject principal (user, group, role)
  principal_id     UUID of the subject user, group or role

options:
  -h, --help       show this help message and exit
  --user USER      Greenbone username
  --debug          Print debugging messages
  --really-change  Actually change state instead of a dry run

Example:
    $ gb_make_all_visible_for override group 72dbb441-8c96-41b4-939d-7bfc28dd6e6d
```

## gb_merge_reports
```
usage: gb_merge_reports [-h] [--user USER] [--force] [-f] [-t] [-o OUTPUT]
                        reports [reports ...]

Merge several reports into one

positional arguments:
  reports              Reports to merge

options:
  -h, --help           show this help message and exit
  --user USER          Greenbone username
  --force              Combine --output with --force to overwrite a file
  -f, --file           Read the reports locally from files
  -t, --task           Use task names instead of report UUIDs
  -o, --output OUTPUT  Destination for merged report. Defaults to '-' for stdout

The 'reports' argument is to be specified as:
    * report UUIDs
    * task name (with -t/--task)
    * paths to files (with -f/--file)
    * '-' for standard input (with -f/--file)

This tool outputs XML to standard output unless --output is given. It pairs well
with the gb_upload_report tool.

Examples:
    $ gb_merge_reports 12345678-1234-1234-1234-1234567890ab 12345678-1234-1234-1234-1234567890ab
    $ gb_merge_reports -f ./first.xml ./second.xml
    $ gb_merge_reports -t uni-2510-SAMPLE uni-2510-SAMPLE2
    $ gb_merge_reports --user=u1 -t TASK1 TASK2 | gb_upload_report --user=u2 -n NEWTASK
```

## gb_query_report
```
usage: gb_query_report [-h] [--user USER] [-q] [-d] [-f] [-t] [--fenced]
                       [--all] [--format {csv,csvnohead,json,jsonl,raw}]
                       report [columns]

Get results from a report

positional arguments:
  report                Report to query
  columns               What columns to include

options:
  -h, --help            show this help message and exit
  --user USER           Greenbone username
  -q, --quiet           Suppress progress indication
  -d, --debug           Print debugging messages
  -f, --file            Read the report locally from a file
  -t, --task            Use task name instead of a report UUID
  --fenced              Fence in the output with a type line and a 'LAST' line
  --all                 Output ALL available columns
  --format {csv,csvnohead,json,jsonl,raw}
                        Output format

The 'report' argument is to be specified as:
    * a report UUID
    * a task name (with -t/--task)
    * a path (with -f/--file)
    * '-' for standard input (with -f/--file)

Refer to the results columns listed in "gb_querytool --help" for a list
of possible columns.

Examples:
    $ gb_query_report 5e4554ea-df35-45f4-8637-d14f1634466d name,severity
    $ gb_query_report -f ./export.xml name,severity
    $ gb_query_report -t uni-240305-UST-TS-EXAMPLE name,severity
```

## gb_querytool
```
usage: gb_querytool [-h] [--user USER] [-q] [-d] [--fenced] [--all]
                    [--format {csv,csvnohead,json,jsonl,raw}]
                    [--pagesize PAGESIZE]
                    resource_type filter [columns]

Run a search in greenbone

positional arguments:
  resource_type         Type of resource (e.g. 'report')
  filter                Filter string for greenbone
  columns               What columns to include

options:
  -h, --help            show this help message and exit
  --user USER           Greenbone username
  -q, --quiet           Suppress progress indication
  -d, --debug           Print debugging messages
  --fenced              Fence in the output with a type line and a 'LAST' line
  --all                 Output ALL available columns
  --format {csv,csvnohead,json,jsonl,raw}
                        Output format
  --pagesize PAGESIZE   pagination size

Available columns per type:
  task: uuid created modified owner name alterable comment severity status progress config_id
    report_count report_uuid findings_high findings_medium findings_low findings_log
    findings_false_positive
  report: uuid created modified owner name comment severity_full severity_filtered status progress
    task_uuid task_name scan_start scan_end timezone findings_high findings_medium findings_low
    findings_log findings_false_positive findings_high_full findings_medium_full findings_low_full
    findings_log_full findings_false_positive_full
  result: uuid created modified owner name comment detection_product detection_method detection_oid
    host hostname port nvt_oid nvt_name nvt_family nvt_tags nvt_solution nvt_cvss_base_vector
    nvt_summary nvt_insight nvt_affected nvt_impact nvt_vuldetect nvt_solution_type threat severity
    original_threat original_severity qod_value description
  note: uuid created modified owner text nvt_oid nvt_name hosts location active in_use orphan
    task_uuid result_uuid
  override: uuid created modified owner text nvt_oid nvt_name hosts location severity new_threat
    new_severity end_time active in_use orphan task_uuid result_uuid
  target: uuid created modified owner name comment hosts exclude_hosts writable
    allow_simultaneous_ips alive_tests
  config: uuid created modified owner name comment writable in_use family_count family_count_growing
    nvt_count nvt_count_growing
  report_format: uuid created modified owner name summary description extension content_type
  filter: uuid created modified owner name comment term type
  tag: uuid created modified owner name comment resource_type resource_count active
  user: uuid created modified owner name comment
  group: uuid created modified owner name comment
  role: uuid created modified owner name comment
  permission: uuid created modified owner name comment resource_uuid resource_type resource_name
    subject_uuid subject_type subject_name

Examples:
    $ gb_querytool --user=autoscan report "task~RUS-CERT" uuid,task_name,severity_filtered
    $ gb_querytool results 'severity=10' host,port,name
```

## gb_report_status
```
usage: gb_report_status [-h] [--user USER] report_id

This script requests the given report and returns it status.

positional arguments:
  report_id    UUID of report

options:
  -h, --help   show this help message and exit
  --user USER  Greenbone username

Example:
    $ gb_report_status 0bdeb40a-b2a2-4e3a-ab9f-0809d89a3489
```

## gb_setup_and_start_scan
```
usage: gb_setup_and_start_scan [-h] [--user USER] [--portlist PORTLIST]
                               [--scanner SCANNER] [--scanconfig SCANCONFIG]
                               [--alivetest ALIVETEST]
                               target_name hosts_ip

This script requests a target name and a list of IPs to create a
target and task and starts it automatically.

positional arguments:
  target_name           Name of the target
  hosts_ip              List of hosts IP addresses

options:
  -h, --help            show this help message and exit
  --user USER           Greenbone username
  --portlist PORTLIST   UUID of greenbone port list
  --scanner SCANNER     UUID of greenbone scanner
  --scanconfig SCANCONFIG
                        UUID of greenbone scan config
  --alivetest ALIVETEST
                        Name of alive test (e.g. 'ICMP Ping')

Example:
    $ gb_setup_and_start_scan "uni-240305-UST-TS-EXAMPLE" 127.0.0.1
```

## gb_status_summary
```
usage: gb_status_summary [-h] [--user USER] [--all] [--list]

Shows the status of reports (Running, Done, etc.)

options:
  -h, --help   show this help message and exit
  --user USER  Greenbone username
  --all        Shows all reports including those that are Done
  --list       Print a list rather than a count

Examples:
    $ gb_status_summary
    $ gb_status_summary --all
    $ gb_status_summary --all --list
```

## gb_task_status
```
usage: gb_task_status [-h] [--user USER] task_id

This script requests the given task and returns it status.

positional arguments:
  task_id      UUID of task

options:
  -h, --help   show this help message and exit
  --user USER  Greenbone username

Example:
    $ gb_task_status d34a201e-cf36-4a38-bcfe-811c43c65622
```

## gb_upload_report
```
usage: gb_upload_report [-h] [--user USER] [-n] [-i INPUT] task_name

Upload a report to a container task

positional arguments:
  task_name          Name of the container task to upload the report into

options:
  -h, --help         show this help message and exit
  --user USER        Greenbone username
  -n, --new          Create a new container task by that name
  -i, --input INPUT  Input file. Defaults to '-' for stdin.

This tool reads XML from standard output unless --input is given. It pairs well
with the gb_merge_reports and gb_download_report tools.

Examples:
    $ zcat archived_report.xml.gz | gb_upload_report "target task"
    $ gb_upload_report -i ./file.xml "target task"
    $ gb_merge_reports --user=u1 -t TASK1 TASK2 | gb_upload_report --user=u2 -n NEWTASK
```

## gb_web_filter
```
usage: gb_web_filter [-h] [--user USER] [--verbose]
                     {list,show,create,update,create-or-update,delete,get-default-filter,set-default-filter,unset-default-filter} ...

This script interacts with the stored filters in the greenbone web
interface.

positional arguments:
  {list,show,create,update,create-or-update,delete,get-default-filter,set-default-filter,unset-default-filter}
    list                list all filters of a given type
    show                shows a stored filter string
    create              create a new filter
    update              update a filter
    create-or-update    update a filter
    delete              delete a filter
    get-default-filter  show the name of the default filter for a given type
    set-default-filter  set the default filter for a given type
    unset-default-filter
                        remove a default filter assignment for a given type

options:
  -h, --help            show this help message and exit
  --user USER           Greenbone username
  --verbose             Show an indication of the changes that have been made.

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
```
