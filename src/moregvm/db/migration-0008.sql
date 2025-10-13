BEGIN TRANSACTION;
DELETE FROM mg_meta WHERE schema_version = 7;
INSERT INTO mg_meta (schema_version) VALUES (8);

DROP VIEW mg_view_results;

CREATE VIEW mg_view_results AS
SELECT
    mg_users.name AS user,
    mg_raw_reports.task_uuid,
    mg_raw_reports.task_name,
    mg_raw_reports.name AS report_name,
    mg_raw_results.id,
    mg_raw_results.sync_found,
    mg_raw_results.sync_vanished,
    mg_raw_results.sync_user,
    mg_syncdata_results.date AS sync_time,
    mg_raw_results.uuid,
    mg_raw_results.created,
    mg_raw_results.modified,
    mg_raw_results.owner,
    mg_raw_results.name,
    mg_raw_results.comment,
    mg_raw_results.host,
    mg_raw_results.hostname,
    mg_raw_results.port,
    mg_raw_results_e_nvt.nvt_oid,
    mg_raw_results_e_nvt.nvt_name,
    mg_raw_results_e_nvt.nvt_family,
    mg_raw_results_e_nvt.nvt_tags,
    mg_raw_results_e_nvt.nvt_solution,
    mg_raw_results_e_nvt.nvt_cvss_base_vector,
    mg_raw_results_e_nvt.nvt_summary,
    mg_raw_results_e_nvt.nvt_insight,
    mg_raw_results_e_nvt.nvt_affected,
    mg_raw_results_e_nvt.nvt_impact,
    mg_raw_results_e_nvt.nvt_vuldetect,
    mg_raw_results_e_nvt.nvt_solution_type,
    mg_raw_results.threat,
    mg_raw_results.severity,
    mg_raw_results.original_threat,
    mg_raw_results.original_severity,
    mg_raw_results.qod_value,
    mg_raw_results_e_description.description,
    mg_raw_results.report_uuid,
    mg_raw_results.detection_product,
    mg_raw_results.detection_method,
    mg_raw_results.detection_oid
FROM mg_raw_results
    JOIN mg_raw_results_e_description
        ON mg_raw_results.e_description_id = mg_raw_results_e_description.id
    JOIN mg_raw_results_e_nvt
        ON mg_raw_results.e_nvt_id = mg_raw_results_e_nvt.id
    JOIN mg_users
        ON mg_raw_results.sync_user = mg_users.id
    JOIN mg_syncdata_results
        ON mg_raw_results.sync_found = mg_syncdata_results.id
    JOIN mg_raw_reports
        ON mg_raw_reports.sync_vanished IS NULL
        AND mg_raw_results.report_uuid = mg_raw_reports.uuid
WHERE mg_raw_results.sync_vanished IS NULL;

COMMIT TRANSACTION;
