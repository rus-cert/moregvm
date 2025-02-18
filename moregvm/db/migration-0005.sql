BEGIN TRANSACTION;
DELETE FROM mg_meta WHERE schema_version = 4;
INSERT INTO mg_meta (schema_version) VALUES (5);

CREATE INDEX ON mg_raw_results (
    sync_vanished NULLS FIRST,
    sync_user,
    report_uuid,
    uuid
);
CREATE INDEX ON mg_raw_results (
    uuid,
    sync_vanished
);

COMMIT TRANSACTION;
