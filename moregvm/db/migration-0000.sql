BEGIN TRANSACTION;

CREATE TABLE schema_meta (
    id INTEGER GENERATED ALWAYS AS (1) STORED PRIMARY KEY,
    schema_version INTEGER NOT NULL
);
INSERT INTO schema_meta (schema_version) VALUES (0);

ALTER TABLE sync_users
    ALTER COLUMN name SET NOT NULL;
ALTER TABLE gvm_notes_syncdata
    ALTER COLUMN date SET NOT NULL;
ALTER TABLE gvm_overrides_syncdata
    ALTER COLUMN date SET NOT NULL;
ALTER TABLE gvm_tasks_syncdata
    ALTER COLUMN date SET NOT NULL;
ALTER TABLE gvm_reports_syncdata
    ALTER COLUMN date SET NOT NULL;
ALTER TABLE gvm_results_syncdata
    ALTER COLUMN date SET NOT NULL;
ALTER TABLE gvm_notes
    ALTER COLUMN created SET NOT NULL;
ALTER TABLE gvm_overrides
    ALTER COLUMN created SET NOT NULL;
ALTER TABLE gvm_tasks
    ALTER COLUMN created SET NOT NULL;
ALTER TABLE gvm_reports
    ALTER COLUMN created SET NOT NULL;
ALTER TABLE gvm_results
    ALTER COLUMN created SET NOT NULL;

COMMIT TRANSACTION;
