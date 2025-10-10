#!/usr/bin/env python3

import argparse
import collections
import os
import sys
from typing import cast

import gvm.errors
import psycopg2
from psycopg2 import sql

import moregvm

# Globals
debug = False
quiet = False
status = False

DEFAULT_FILTERSTRING = "apply_overrides=1 sort=created rows=-1 notes=0"
NVT_COLUMNS = [
    "nvt_oid", "nvt_name", "nvt_family", "nvt_tags", "nvt_solution", "nvt_cvss_base_vector", "nvt_summary",
    "nvt_insight", "nvt_affected", "nvt_impact", "nvt_vuldetect", "nvt_solution_type"
]


class GbDbImportResults(moregvm.Tool):
    """
    This script imports a result from greenbone into the database.

    Examples:
        $ gb_db_import_results 32302393-115e-42e4-ba28-14d3899e1db0
    """

    @classmethod
    def custom_args(cls, parser: argparse.ArgumentParser):
        # Our arguments are too complex for the other methods
        parser.add_argument("report", help="report UUID")
        parser.add_argument("-q", "--quiet", help="Suppress progress indication", action="store_true")
        parser.add_argument("-d", "--debug", help="Print debugging messages", action="store_true")

    def tool_main(self) -> None:
        global debug, quiet, status
        (debug, quiet) = (self.args["debug"], self.args["quiet"])
        status = not quiet and not debug and sys.stderr.isatty()

        dsn = None
        if "RUSCERTGB_DSN" in os.environ:
            dsn = os.environ["RUSCERTGB_DSN"]

        name = self.user

        # columns
        available_cols = collections.ChainMap(moregvm.COLUMNS["result"], moregvm.GLOBAL_COLUMNS)
        columns = list(available_cols.keys())

        options = dict(moregvm.OPTIONS["result"])

        if status: moregvm.progress_indicator(0, "get_reports")
        try:
            report_UUID = self.args["report"]
            filterstr = DEFAULT_FILTERSTRING
            get_report_response = self.gmp.get_report(
                report_id=report_UUID, filter_string=filterstr
            )
        except gvm.errors.GvmResponseError as ex:
            if ex.status == "404":
                raise moregvm.PermanentError("Report not found")
            raise
        report = get_report_response.find('./report')
        results = report.findall('./report/results/result')

        if debug:
            self.errprint(f"greenbone returned report with {len(results)} results")

        # commit is implicit, the connection is the context manager
        with psycopg2.connect(dsn) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT id FROM mg_users WHERE name = (%s)", (name,))
                match curs.rowcount:
                    case 0: curs.execute("INSERT INTO mg_users (name) VALUES (%s) RETURNING id", (name,))
                    case 1: pass
                    case _: raise moregvm.InternalError(
                            f"SELECT on mg_users returned {curs.rowcount} rows. Expected 0 or 1.")
                # we checked that there's a result in the 'match' so the cast() is safe
                username_id = cast(tuple[int], curs.fetchone())[0]
                conn.commit()

                sync_data_query = """ INSERT INTO mg_syncdata_results (
                                          sync_user,
                                          report_uuid,
                                          report_modified,
                                          report_status,
                                          report_progress
                                      ) VALUES (%s, %s, %s, %s, %s) RETURNING id
                                  """
                curs.execute(sync_data_query, (username_id,
                                               report_UUID,
                                               moregvm.GLOBAL_COLUMNS["modified"].extract(report),
                                               moregvm.COLUMNS["report"]["status"].extract(report),
                                               moregvm.COLUMNS["report"]["progress"].extract(report)))

                # if the INSERT above didn't raise an exception, there will be a value, so the cast() is safe
                syncdata_id = cast(tuple[int], curs.fetchone())[0]

                temp_query =""" CREATE TEMPORARY TABLE incoming_mg_results (
                                    uuid UUID NOT NULL,
                                    created TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                                    modified TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                                    owner TEXT NOT NULL,
                                    name TEXT NOT NULL,
                                    comment TEXT,
                                    host INET NOT NULL,
                                    hostname TEXT,
                                    port TEXT NOT NULL,
                                    nvt_oid TEXT NOT NULL,
                                    nvt_name TEXT NOT NULL,
                                    nvt_family TEXT NOT NULL,
                                    nvt_tags TEXT NOT NULL,
                                    nvt_solution TEXT,
                                    nvt_cvss_base_vector TEXT NOT NULL,
                                    nvt_summary TEXT NOT NULL,
                                    nvt_insight TEXT,
                                    nvt_affected TEXT,
                                    nvt_impact TEXT,
                                    nvt_vuldetect TEXT,
                                    nvt_solution_type TEXT,
                                    threat TEXT NOT NULL,
                                    severity REAL NOT NULL,
                                    original_threat TEXT NOT NULL,
                                    original_severity REAL NOT NULL,
                                    qod_value SMALLINT NOT NULL,
                                    description TEXT,
                                    report_uuid UUID NOT NULL,
                                    detection_product TEXT,
                                    detection_method TEXT,
                                    detection_oid TEXT
                            ) ON COMMIT DROP;
                            """
                curs.execute(temp_query)

                sql_identifiers = [sql.Identifier(cn) for cn in columns]
                sql_identifiers.append(sql.Identifier("report_uuid"))
                for idr, result in enumerate(results):
                    if status and idr % 50 == 0: moregvm.progress_indicator(idr, len(results), name="copy to db")
                    temp_values = []

                    for cn in columns:
                        col_obj = available_cols[cn]
                        col_value = col_obj.extract(result)
                        temp_values.append(col_value if col_value != '' else None)
                    temp_values.append(report_UUID)
                    values = tuple(temp_values)

                    incoming_query = sql.SQL("INSERT INTO incoming_mg_results ({fields}) VALUES ({parameter})").format(
                                fields = sql.SQL(',').join(sql_identifiers),
                                parameter = sql.SQL(',').join(sql.Placeholder() * (len(sql_identifiers)))
                                )
                    if debug:
                        self.errprint("queryformat:", incoming_query.as_string(conn))

                    curs.execute(incoming_query, values)

                transform_incoming = sql.SQL(
                        """ INSERT INTO mg_raw_results_e_description (description)
                            SELECT description
                            FROM (
                                SELECT description FROM incoming_mg_results
                                EXCEPT
                                SELECT description FROM mg_raw_results_e_description
                            ) new_descriptions;
                            INSERT INTO mg_raw_results_e_nvt (nvt_oid, nvt_name, nvt_family, nvt_tags, nvt_solution, nvt_cvss_base_vector, nvt_summary, nvt_insight, nvt_affected, nvt_impact, nvt_vuldetect, nvt_solution_type)
                            SELECT nvt_oid, nvt_name, nvt_family, nvt_tags, nvt_solution, nvt_cvss_base_vector, nvt_summary, nvt_insight, nvt_affected, nvt_impact, nvt_vuldetect, nvt_solution_type
                            FROM (
                                SELECT nvt_oid, nvt_name, nvt_family, nvt_tags, nvt_solution, nvt_cvss_base_vector, nvt_summary, nvt_insight, nvt_affected, nvt_impact, nvt_vuldetect, nvt_solution_type
                                FROM incoming_mg_results
                                EXCEPT
                                SELECT nvt_oid, nvt_name, nvt_family, nvt_tags, nvt_solution, nvt_cvss_base_vector, nvt_summary, nvt_insight, nvt_affected, nvt_impact, nvt_vuldetect, nvt_solution_type
                                FROM mg_raw_results_e_nvt
                            ) new_nvts;
                            ALTER TABLE incoming_mg_results
                                ADD COLUMN e_description_id BIGINT,
                                ADD COLUMN e_nvt_id BIGINT;
                            UPDATE incoming_mg_results
                            SET e_description_id = (
                                SELECT mg_raw_results_e_description.id
                                FROM mg_raw_results_e_description
                                WHERE mg_raw_results_e_description.description = incoming_mg_results.description
                                OR (mg_raw_results_e_description.description IS NULL AND incoming_mg_results.description IS NULL)
                            );
                            UPDATE incoming_mg_results
                            SET e_nvt_id = (
                                SELECT mg_raw_results_e_nvt.id
                                FROM mg_raw_results_e_nvt
                                WHERE mg_raw_results_e_nvt.nvt_oid = incoming_mg_results.nvt_oid
                                AND mg_raw_results_e_nvt.nvt_name = incoming_mg_results.nvt_name
                                AND mg_raw_results_e_nvt.nvt_family = incoming_mg_results.nvt_family
                                AND mg_raw_results_e_nvt.nvt_tags = incoming_mg_results.nvt_tags
                                AND mg_raw_results_e_nvt.nvt_solution IS NOT DISTINCT FROM incoming_mg_results.nvt_solution
                                AND mg_raw_results_e_nvt.nvt_cvss_base_vector = incoming_mg_results.nvt_cvss_base_vector
                                AND mg_raw_results_e_nvt.nvt_summary = incoming_mg_results.nvt_summary
                                AND mg_raw_results_e_nvt.nvt_insight IS NOT DISTINCT FROM incoming_mg_results.nvt_insight
                                AND mg_raw_results_e_nvt.nvt_affected IS NOT DISTINCT FROM incoming_mg_results.nvt_affected
                                AND mg_raw_results_e_nvt.nvt_impact IS NOT DISTINCT FROM incoming_mg_results.nvt_impact
                                AND mg_raw_results_e_nvt.nvt_vuldetect IS NOT DISTINCT FROM incoming_mg_results.nvt_vuldetect
                                AND mg_raw_results_e_nvt.nvt_solution_type IS NOT DISTINCT FROM incoming_mg_results.nvt_solution_type
                            );
                        """
                )

                columns_transformed = [c for c in columns if c not in {"description", *NVT_COLUMNS}]
                columns_transformed += ["e_description_id", "e_nvt_id"]

                sql_identifiers_transformed = [sql.Identifier(cn) for cn in columns_transformed]
                sql_identifiers_transformed.append(sql.Identifier("report_uuid"))

                vanished_conditions_sql = sql.SQL(' AND ').join(
                       sql.SQL("mg_raw_results.{column} IS NOT DISTINCT FROM vanished_entries.{column}\n").format(
                                    column = sql.Identifier(cn))
                              for cn in columns_transformed
                       )

                updating_query = sql.SQL(
                        """ UPDATE mg_raw_results
                            SET sync_vanished = {syncdata_id}
                            FROM (
                                SELECT {fields} FROM mg_raw_results
                                    WHERE sync_vanished IS NULL
                                    AND sync_user = {username_id}
                                    AND report_uuid = {report_uuid}
                                EXCEPT
                                SELECT {fields} FROM incoming_mg_results
                            ) vanished_entries
                            WHERE sync_vanished IS NULL
                                AND sync_user = {username_id}
                                AND mg_raw_results.report_uuid = {report_uuid}
                                AND {conditions}
                        """).format(
                                fields = sql.SQL(',').join(sql_identifiers_transformed),
                                syncdata_id = sql.Literal(syncdata_id),
                                username_id = sql.Literal(username_id),
                                report_uuid = sql.Literal(report_UUID),
                                conditions = vanished_conditions_sql
                                )
                if debug:
                    self.errprint("updating_q:\n",updating_query.as_string(conn))

                inserting_query = sql.SQL(
                        """ INSERT INTO mg_raw_results (sync_found, sync_user, {fields})
                            SELECT {syncdata_id}, {username_id}, {fields}
                            FROM (
                                SELECT {fields} FROM incoming_mg_results
                                EXCEPT
                                SELECT {fields} FROM mg_raw_results
                                    WHERE sync_vanished IS NULL
                                    AND sync_user = {username_id}
                                    AND report_uuid = {report_uuid}
                            ) nested_query
                        """).format(
                                fields = sql.SQL(',').join(sql_identifiers_transformed),
                                syncdata_id = sql.Literal(syncdata_id),
                                username_id = sql.Literal(username_id),
                                report_uuid = sql.Literal(report_UUID)
                            )
                if debug:
                    self.errprint("inserting_q:\n",inserting_query.as_string(conn))
                if status: moregvm.progress_indicator(len(results), len(results), name="deduplicate")
                curs.execute(transform_incoming)
                if status: moregvm.progress_indicator(len(results), len(results), name="set sync_vanished")
                curs.execute(updating_query)
                if status: moregvm.progress_indicator(len(results), len(results), name="insert")
                curs.execute(inserting_query)
                if status: moregvm.progress_indicator_erase()

if __name__ == '__main__':
    GbDbImportResults.run_from_sysargs()
