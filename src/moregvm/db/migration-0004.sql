BEGIN TRANSACTION;
DELETE FROM mg_meta WHERE schema_version = 3;
INSERT INTO mg_meta (schema_version) VALUES (4);

-- deduplicate description column:

CREATE TABLE mg_raw_results_e_description (
    id BIGSERIAL PRIMARY KEY,
    description TEXT
);

CREATE UNIQUE INDEX ON mg_raw_results_e_description (
    -- using MD5() because using the entire content could be too long for the index
    -- MD5 is ok because this doesn't need to be a cryptographically secure hash
    MD5(description)
);

-- The above index cannot be used for fast lookups, so optimize lookups using:
CREATE INDEX ON mg_raw_results_e_description USING HASH (description);
CREATE INDEX ON mg_raw_results_e_description (id) WHERE description IS NULL;

INSERT INTO mg_raw_results_e_description (description) (
    SELECT DISTINCT description
    FROM mg_raw_results
);

ALTER TABLE mg_raw_results
    ADD COLUMN e_description_id BIGINT REFERENCES mg_raw_results_e_description(id);

UPDATE mg_raw_results
SET e_description_id = (
    SELECT mg_raw_results_e_description.id
    FROM mg_raw_results_e_description
    -- IS [NOT] DISTINCT FROM is slow in postgres -> use: a=b OR (a IS NULL AND b IS NULL)
    WHERE mg_raw_results_e_description.description = mg_raw_results.description
       OR (mg_raw_results_e_description.description IS NULL AND mg_raw_results.description IS NULL)
);

ALTER TABLE mg_raw_results
    ALTER COLUMN e_description_id SET NOT NULL,
    DROP COLUMN description;

-- deduplicate nvt_* columns:

CREATE TABLE mg_raw_results_e_nvt (
    id BIGSERIAL PRIMARY KEY,
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
    nvt_solution_type TEXT
);

CREATE UNIQUE INDEX ON mg_raw_results_e_nvt (
    nvt_oid, nvt_name, nvt_family, nvt_cvss_base_vector, nvt_summary, nvt_solution_type,
    -- using MD5() because using the entire content would be too long for the index
    -- MD5 is ok because this doesn't need to be a cryptographically secure hash
    MD5(nvt_tags),
    MD5(nvt_solution),
    MD5(nvt_insight),
    MD5(nvt_affected),
    MD5(nvt_impact),
    MD5(nvt_vuldetect)
);

INSERT INTO mg_raw_results_e_nvt (nvt_oid, nvt_name, nvt_family, nvt_tags, nvt_solution, nvt_cvss_base_vector, nvt_summary, nvt_insight, nvt_affected, nvt_impact, nvt_vuldetect, nvt_solution_type) (
    SELECT DISTINCT nvt_oid, nvt_name, nvt_family, nvt_tags, nvt_solution, nvt_cvss_base_vector, nvt_summary, nvt_insight, nvt_affected, nvt_impact, nvt_vuldetect, nvt_solution_type
    FROM mg_raw_results
);

ALTER TABLE mg_raw_results
    ADD COLUMN e_nvt_id BIGINT REFERENCES mg_raw_results_e_nvt(id);

UPDATE mg_raw_results
SET e_nvt_id = (
    SELECT mg_raw_results_e_nvt.id
    FROM mg_raw_results_e_nvt
    -- IS [NOT] DISTINCT FROM is slow in postgres (operation does not use index) -> use eqality for non-null fields
    WHERE mg_raw_results_e_nvt.nvt_oid = mg_raw_results.nvt_oid
      AND mg_raw_results_e_nvt.nvt_name = mg_raw_results.nvt_name
      AND mg_raw_results_e_nvt.nvt_family = mg_raw_results.nvt_family
      AND mg_raw_results_e_nvt.nvt_tags = mg_raw_results.nvt_tags
      AND mg_raw_results_e_nvt.nvt_solution IS NOT DISTINCT FROM mg_raw_results.nvt_solution
      AND mg_raw_results_e_nvt.nvt_cvss_base_vector = mg_raw_results.nvt_cvss_base_vector
      AND mg_raw_results_e_nvt.nvt_summary = mg_raw_results.nvt_summary
      AND mg_raw_results_e_nvt.nvt_insight IS NOT DISTINCT FROM mg_raw_results.nvt_insight
      AND mg_raw_results_e_nvt.nvt_affected IS NOT DISTINCT FROM mg_raw_results.nvt_affected
      AND mg_raw_results_e_nvt.nvt_impact IS NOT DISTINCT FROM mg_raw_results.nvt_impact
      AND mg_raw_results_e_nvt.nvt_vuldetect IS NOT DISTINCT FROM mg_raw_results.nvt_vuldetect
      AND mg_raw_results_e_nvt.nvt_solution_type IS NOT DISTINCT FROM mg_raw_results.nvt_solution_type
);

ALTER TABLE mg_raw_results
    ALTER COLUMN e_nvt_id SET NOT NULL,
    DROP COLUMN nvt_oid,
    DROP COLUMN nvt_name,
    DROP COLUMN nvt_family,
    DROP COLUMN nvt_tags,
    DROP COLUMN nvt_solution,
    DROP COLUMN nvt_cvss_base_vector,
    DROP COLUMN nvt_summary,
    DROP COLUMN nvt_insight,
    DROP COLUMN nvt_affected,
    DROP COLUMN nvt_impact,
    DROP COLUMN nvt_vuldetect,
    DROP COLUMN nvt_solution_type;

CREATE VIEW mg_view_results AS
SELECT
    mg_raw_results.id,
    mg_raw_results.sync_found,
    mg_raw_results.sync_vanished,
    mg_raw_results.sync_user,
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
    mg_raw_results.report_uuid
FROM mg_raw_results
    JOIN mg_raw_results_e_description
        ON mg_raw_results.e_description_id = mg_raw_results_e_description.id
    JOIN mg_raw_results_e_nvt
        ON mg_raw_results.e_nvt_id = mg_raw_results_e_nvt.id;


COMMIT TRANSACTION;
