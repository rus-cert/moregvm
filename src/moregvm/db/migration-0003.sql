BEGIN TRANSACTION;
DELETE FROM mg_meta WHERE schema_version = 2;
INSERT INTO mg_meta (schema_version) VALUES (3);

ALTER TABLE mg_raw_tasks
   ALTER COLUMN config_id DROP NOT NULL;

COMMIT TRANSACTION;
