BEGIN TRANSACTION;
DELETE FROM schema_meta WHERE schema_version = 0;
INSERT INTO schema_meta (schema_version) VALUES (1);

ALTER TABLE gvm_notes_syncdata RENAME CONSTRAINT gvm_notes_syncdata_sync_user_fkey TO mg_syncdata_notes_sync_user_fkey;
ALTER TABLE gvm_overrides_syncdata RENAME CONSTRAINT gvm_overrides_syncdata_sync_user_fkey TO mg_syncdata_overrides_sync_user_fkey;
ALTER TABLE gvm_tasks_syncdata RENAME CONSTRAINT gvm_tasks_syncdata_sync_user_fkey TO mg_syncdata_tasks_sync_user_fkey;
ALTER TABLE gvm_reports_syncdata RENAME CONSTRAINT gvm_reports_syncdata_sync_user_fkey TO mg_syncdata_reports_sync_user_fkey;
ALTER TABLE gvm_results_syncdata RENAME CONSTRAINT gvm_results_syncdata_sync_user_fkey TO mg_syncdata_results_sync_user_fkey;
ALTER TABLE gvm_notes RENAME CONSTRAINT gvm_notes_sync_found_fkey TO mg_raw_notes_sync_found_fkey;
ALTER TABLE gvm_notes RENAME CONSTRAINT gvm_notes_sync_vanished_fkey TO mg_raw_notes_sync_vanished_fkey;
ALTER TABLE gvm_notes RENAME CONSTRAINT gvm_notes_sync_user_fkey TO mg_raw_notes_sync_user_fkey;
ALTER TABLE gvm_overrides RENAME CONSTRAINT gvm_overrides_sync_found_fkey TO mg_raw_overrides_sync_found_fkey;
ALTER TABLE gvm_overrides RENAME CONSTRAINT gvm_overrides_sync_vanished_fkey TO mg_raw_overrides_sync_vanished_fkey;
ALTER TABLE gvm_overrides RENAME CONSTRAINT gvm_overrides_sync_user_fkey TO mg_raw_overrides_sync_user_fkey;
ALTER TABLE gvm_tasks RENAME CONSTRAINT gvm_tasks_sync_found_fkey TO mg_raw_tasks_sync_found_fkey;
ALTER TABLE gvm_tasks RENAME CONSTRAINT gvm_tasks_sync_vanished_fkey TO mg_raw_tasks_sync_vanished_fkey;
ALTER TABLE gvm_tasks RENAME CONSTRAINT gvm_tasks_sync_user_fkey TO mg_raw_tasks_sync_user_fkey;
ALTER TABLE gvm_reports RENAME CONSTRAINT gvm_reports_sync_found_fkey TO mg_raw_reports_sync_found_fkey;
ALTER TABLE gvm_reports RENAME CONSTRAINT gvm_reports_sync_vanished_fkey TO mg_raw_reports_sync_vanished_fkey;
ALTER TABLE gvm_reports RENAME CONSTRAINT gvm_reports_sync_user_fkey TO mg_raw_reports_sync_user_fkey;
ALTER TABLE gvm_results RENAME CONSTRAINT gvm_results_sync_found_fkey TO mg_raw_results_sync_found_fkey;
ALTER TABLE gvm_results RENAME CONSTRAINT gvm_results_sync_vanished_fkey TO mg_raw_results_sync_vanished_fkey;
ALTER TABLE gvm_results RENAME CONSTRAINT gvm_results_sync_user_fkey TO mg_raw_results_sync_user_fkey;

ALTER TABLE    gvm_notes                 RENAME TO mg_raw_notes;
ALTER INDEX    gvm_notes_pkey            RENAME TO mg_raw_notes_pkey;
ALTER SEQUENCE gvm_notes_id_seq          RENAME TO mg_raw_notes_id_seq;
ALTER TABLE    gvm_notes_syncdata        RENAME TO mg_syncdata_notes;
ALTER INDEX    gvm_notes_syncdata_pkey   RENAME TO mg_syncdata_notes_pkey;
ALTER SEQUENCE gvm_notes_syncdata_id_seq RENAME TO mg_syncdata_notes_id_seq;

ALTER TABLE    gvm_overrides                 RENAME TO mg_raw_overrides;
ALTER INDEX    gvm_overrides_pkey            RENAME TO mg_raw_overrides_pkey;
ALTER SEQUENCE gvm_overrides_id_seq          RENAME TO mg_raw_overrides_id_seq;
ALTER TABLE    gvm_overrides_syncdata        RENAME TO mg_syncdata_overrides;
ALTER INDEX    gvm_overrides_syncdata_pkey   RENAME TO mg_syncdata_overrides_pkey;
ALTER SEQUENCE gvm_overrides_syncdata_id_seq RENAME TO mg_syncdata_overrides_id_seq;

ALTER TABLE    gvm_reports                 RENAME TO mg_raw_reports;
ALTER INDEX    gvm_reports_pkey            RENAME TO mg_raw_reports_pkey;
ALTER SEQUENCE gvm_reports_id_seq          RENAME TO mg_raw_reports_id_seq;
ALTER TABLE    gvm_reports_syncdata        RENAME TO mg_syncdata_reports;
ALTER INDEX    gvm_reports_syncdata_pkey   RENAME TO mg_syncdata_reports_pkey;
ALTER SEQUENCE gvm_reports_syncdata_id_seq RENAME TO mg_syncdata_reports_id_seq;

ALTER TABLE    gvm_results                 RENAME TO mg_raw_results;
ALTER INDEX    gvm_results_pkey            RENAME TO mg_raw_results_pkey;
ALTER SEQUENCE gvm_results_id_seq          RENAME TO mg_raw_results_id_seq;
ALTER TABLE    gvm_results_syncdata        RENAME TO mg_syncdata_results;
ALTER INDEX    gvm_results_syncdata_pkey   RENAME TO mg_syncdata_results_pkey;
ALTER SEQUENCE gvm_results_syncdata_id_seq RENAME TO mg_syncdata_results_id_seq;

ALTER TABLE    gvm_tasks                 RENAME TO mg_raw_tasks;
ALTER INDEX    gvm_tasks_pkey            RENAME TO mg_raw_tasks_pkey;
ALTER SEQUENCE gvm_tasks_id_seq          RENAME TO mg_raw_tasks_id_seq;
ALTER TABLE    gvm_tasks_syncdata        RENAME TO mg_syncdata_tasks;
ALTER INDEX    gvm_tasks_syncdata_pkey   RENAME TO mg_syncdata_tasks_pkey;
ALTER SEQUENCE gvm_tasks_syncdata_id_seq RENAME TO mg_syncdata_tasks_id_seq;

ALTER TABLE    schema_meta                   RENAME TO mg_meta;
ALTER INDEX    schema_meta_pkey              RENAME TO mg_meta_pkey;
ALTER TABLE    sync_users                    RENAME TO mg_users;
ALTER INDEX    sync_users_pkey               RENAME TO mg_users_pkey;
ALTER INDEX    sync_users_name_key           RENAME TO mg_users_name_key;
ALTER SEQUENCE sync_users_id_seq             RENAME TO mg_users_id_seq;

COMMIT TRANSACTION;
