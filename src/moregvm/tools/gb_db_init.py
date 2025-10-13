#!/usr/bin/env python3

import os

import moregvm


class GbDbInit(moregvm.LazyTool):
    """
    This script imports the database schema, creating all tables,
    indices and constraints

    Example:
        $ gb_db_init
    """

    def tool_main(self) -> None:
        # commit is implicit, the connection is the context manager
        with moregvm.db_cursor() as curs:
            schema = os.path.dirname(moregvm.__file__) + "/db/schema.sql"
            SQL_SCHEMA = open(schema, "r").read()
            curs.execute(SQL_SCHEMA)


if __name__ == "__main__":
    GbDbInit.run_from_sysargs()
