#!/usr/bin/env python3

import argparse
import sys
import os
import psycopg2
from psycopg2 import sql

import moregvm

from collections import ChainMap
from typing import Any, cast
# Constants
allowed_types = ["note", "override", "task", "report"]

# Globals
debug=False
quiet=False
status=False

class GbDbImport(moregvm.Tool):
    """
    This script imports a resource_type from greenbone into the database

    Examples:
        $ gb_db_import report
    """

    @classmethod
    def custom_args(cls, parser: argparse.ArgumentParser):
        # Our arguments are too complex for the other methods
        parser.add_argument("resource_type", help="Type of resource (e.g. 'report')")
        parser.add_argument("-q", "--quiet", help="Suppress progress indication", action="store_true")
        parser.add_argument("-d", "--debug", help="Print debugging messages", action="store_true")
        parser.add_argument("--pagesize", default=None, help="pagination size")

    def tool_main(self) -> None:
        global debug, quiet, status
        (debug, quiet) = (self.args["debug"], self.args["quiet"])
        status = not quiet and sys.stderr.isatty()
        resource_type = self.args["resource_type"]

        # resource_type
        if resource_type not in allowed_types:
            if resource_type[-1] == 's' and resource_type[:-1] in allowed_types:
                resource_type = resource_type[:-1] # strip off plural 's'
            else:
                raise moregvm.PermanentError(f'Currently only the types {allowed_types} are supported')

        dsn = None
        if "RUSCERTGB_DSN" in os.environ:
            dsn = os.environ["RUSCERTGB_DSN"]

        name = self.user

        # columns

        available_cols = ChainMap(moregvm.COLUMNS[resource_type], moregvm.GLOBAL_COLUMNS)

        columns = list(available_cols.keys())

        options = dict(moregvm.OPTIONS[resource_type])

        # actually run the query
        resource_iter = moregvm.resources_gen(self,
                                                resource_type,
                                                "", options,
                                                self.args["pagesize"], debug, status)
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
              
                sync_data_query = sql.SQL(
                        "INSERT INTO mg_syncdata_{resource_type}s (sync_user) VALUES (%s) RETURNING id").format(
                                resource_type = sql.SQL(resource_type),
                        )
                curs.execute(sync_data_query, (username_id,))
                # if the INSERT above didn't raise an exception, there will be a value, so the cast() is safe
                syncdata_id = cast(tuple[int], curs.fetchone())[0] 

                temp_query = sql.SQL(
                            """ CREATE TEMPORARY TABLE incoming_mg_{resource_type}s
                            (LIKE mg_raw_{resource_type}s INCLUDING ALL EXCLUDING DEFAULTS) ON COMMIT DROP;
                                    ALTER TABLE incoming_mg_{resource_type}s
                                    DROP COLUMN id,
                                    DROP COLUMN sync_found,
                                    DROP COLUMN sync_vanished,
                                    DROP COLUMN sync_user
                            """).format(
                                resource_type = sql.SQL(resource_type),
                                )
                curs.execute(temp_query, (username_id,))

                vanished_conditions_sql = sql.SQL(' AND ').join(
                       sql.SQL("mg_raw_{resource_type}s.{column} IS NOT DISTINCT FROM vanished_entries.{column}\n").format(
                                    resource_type = sql.SQL(resource_type),
                                    column = sql.Identifier(cn))
                              for cn in columns
                       )
                sql_identifiers = [sql.Identifier(cn) for cn in columns]

                for resource in resource_iter:
                    temp_values = []

                    for cn in columns:
                        col_obj = available_cols[cn]
                        col_value = col_obj.extract(resource)
                        temp_values.append(col_value if col_value != '' else None)
                    values = tuple(temp_values)

                    incoming_query = sql.SQL("INSERT INTO incoming_mg_{resource_type}s ({fields}) VALUES ({parameter})").format(
                                resource_type = sql.SQL(resource_type),
                                fields = sql.SQL(',').join(sql_identifiers),
                                parameter = sql.SQL(',').join(sql.Placeholder() * len(sql_identifiers))
                                )
                    if debug:
                        self.errprint(incoming_query.as_string(conn))
                    curs.execute(incoming_query, values)

                updating_query = sql.SQL(
                        """ UPDATE mg_raw_{resource_type}s
                            SET sync_vanished = {syncdata_id}
                            FROM (
                                SELECT {fields} FROM mg_raw_{resource_type}s
                                    WHERE sync_vanished IS NULL AND sync_user = {username_id}
                                EXCEPT
                                SELECT {fields} FROM incoming_mg_{resource_type}s
                            ) vanished_entries
                            WHERE sync_vanished IS NULL
                                AND sync_user = {username_id}
                                AND {conditions}
                        """).format(
                                resource_type = sql.SQL(resource_type),
                                fields = sql.SQL(',').join(sql_identifiers),
                                syncdata_id = sql.Literal(syncdata_id),
                                username_id = sql.Literal(username_id),
                                conditions = vanished_conditions_sql
                                )
                if debug:
                    self.errprint(updating_query.as_string(conn))

                inserting_query = sql.SQL(
                        """ INSERT INTO mg_raw_{resource_type}s (sync_found, sync_user, {fields})
                            SELECT {syncdata_id}, {username_id}, {fields}
                            FROM (
                                SELECT {fields} FROM incoming_mg_{resource_type}s
                                EXCEPT
                                SELECT {fields} FROM mg_raw_{resource_type}s
                                    WHERE sync_vanished IS NULL AND sync_user = {username_id}
                            ) nested_query
                        """).format(
                                resource_type = sql.SQL(resource_type),
                                fields = sql.SQL(',').join(sql_identifiers),
                                syncdata_id = sql.Literal(syncdata_id),
                                username_id = sql.Literal(username_id)
                            )
                if debug:
                    self.errprint(inserting_query.as_string(conn))
                curs.execute(updating_query)
                curs.execute(inserting_query)

if __name__ == '__main__':
    GbDbImport.run_from_sysargs()

