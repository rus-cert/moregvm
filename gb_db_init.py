#!/usr/bin/env python3

import os

import moregvm
import psycopg2

class GbDbInit(moregvm.LazyTool):
    """
    This script imports the database schema, creating all tables,
    indices and constraints

    Example:
        $ gb_db_init
    """
    def tool_main(self) -> None:
        dsn = None
        if "RUSCERTGB_DSN" in os.environ:
            dsn = os.environ["RUSCERTGB_DSN"]

        # commit is implicit, the connection is the context manager
        with psycopg2.connect(dsn) as conn:
            with conn.cursor() as curs:
                schema = os.path.dirname(moregvm.__file__) + "/db/schema.sql"
                SQL_SCHEMA = open(schema, "r").read()
                curs.execute(SQL_SCHEMA)

if __name__ == '__main__':
    GbDbInit.run_from_sysargs()
