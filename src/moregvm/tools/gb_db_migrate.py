#!/usr/bin/env python3

import os
from typing import cast

import moregvm


class GbDbMigrate(moregvm.LazyTool):
    """
    This script migrates the db from VERSION-1 to VERSION
    using migration-VERSION.sql

    Example:
        $ gb_db_migrate 42
    """

    @classmethod
    def required_args(cls):
        return {
            "version": "Version to migrate to",
        }

    def tool_main(self) -> None:
        migration_version = self.args["version"]

        # commit is implicit, the connection is the context manager
        with moregvm.db_cursor() as curs:
            curs.execute("SELECT schema_version FROM mg_meta")
            db_version_before = cast(tuple[int], curs.fetchone())[0]

            if db_version_before != int(migration_version)-1:
                raise moregvm.PermanentError(f"Error: You specified to update from version {int(migration_version)-1} to version {migration_version}, but the current schema version is {db_version_before}")

            # padding
            version_number_str = migration_version.zfill(4)

            migration = os.path.dirname(moregvm.__file__) + f"/db/migration-{version_number_str}.sql"
            SQL_MIGRATION = open(migration, "r").read()
            curs.execute(SQL_MIGRATION)
            self.output(f"Running schema migration from version {db_version_before} to version {migration_version}")

            curs.execute("SELECT schema_version FROM mg_meta")
            db_version_after = cast(tuple[int], curs.fetchone())[0]

            if db_version_after != int(migration_version):
                raise moregvm.PermanentError(f"Error: Schema migration applied but the stored schema version did not change")


if __name__ == "__main__":
    GbDbMigrate.run_from_sysargs()
