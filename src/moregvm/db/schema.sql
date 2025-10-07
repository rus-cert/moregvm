----- Meta table: Schema versioning -----
CREATE TABLE mg_meta (
    id INTEGER GENERATED ALWAYS AS (1) STORED PRIMARY KEY,
    schema_version INTEGER NOT NULL
);
INSERT INTO mg_meta (schema_version) VALUES (6);

----- mg_users: Every entry is associated with a user -----
CREATE TABLE mg_users (
	id SERIAL PRIMARY KEY,
	name TEXT UNIQUE NOT NULL
);

----- Syncdata tables: When was each entry synchronized? -----
CREATE TABLE mg_syncdata_notes (
	id BIGSERIAL PRIMARY KEY,
	date TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
	sync_user INTEGER NOT NULL REFERENCES mg_users(id)
);

CREATE TABLE mg_syncdata_overrides (
	id BIGSERIAL PRIMARY KEY,
	date TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
	sync_user INTEGER NOT NULL REFERENCES mg_users(id)
);

CREATE TABLE mg_syncdata_tasks (
	id BIGSERIAL PRIMARY KEY,
	date TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
	sync_user INTEGER NOT NULL REFERENCES mg_users(id)
);

CREATE TABLE mg_syncdata_reports (
	id BIGSERIAL PRIMARY KEY,
	date TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
	sync_user INTEGER NOT NULL REFERENCES mg_users(id)
);

CREATE TABLE mg_syncdata_results (
	id BIGSERIAL PRIMARY KEY,
	date TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
	sync_user INTEGER NOT NULL REFERENCES mg_users(id),
	report_uuid UUID NOT NULL,
	report_modified TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	report_status TEXT NOT NULL,
	report_progress INTEGER NOT NULL
);

----- Content tables -----
CREATE TABLE mg_raw_notes (
	id BIGSERIAL PRIMARY KEY,
	sync_found BIGINT NOT NULL REFERENCES mg_syncdata_notes(id),
	sync_vanished BIGINT DEFAULT NULL REFERENCES mg_syncdata_notes(id),
	sync_user INTEGER NOT NULL REFERENCES mg_users(id),
	uuid UUID NOT NULL,
	created TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	modified TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	owner TEXT NOT NULL,
	text TEXT NOT NULL,
	nvt_oid TEXT NOT NULL,
	nvt_name TEXT NOT NULL,
	hosts TEXT,
	location TEXT,
	active BOOLEAN NOT NULL,
	in_use BOOLEAN NOT NULL,
	orphan BOOLEAN NOT NULL,
	task_uuid UUID,
	result_uuid UUID
);

CREATE TABLE mg_raw_overrides (
	id BIGSERIAL PRIMARY KEY,
	sync_found BIGINT NOT NULL REFERENCES mg_syncdata_overrides(id),
	sync_vanished BIGINT DEFAULT NULL REFERENCES mg_syncdata_overrides(id),
	sync_user INTEGER NOT NULL REFERENCES mg_users(id),
	uuid UUID NOT NULL,
	created TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	modified TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	owner TEXT NOT NULL,
	text TEXT NOT NULL,
	nvt_oid TEXT NOT NULL,
	nvt_name TEXT NOT NULL,
	hosts TEXT,
	location TEXT,
	severity REAL,
	new_threat TEXT NOT NULL,
	new_severity REAL NOT NULL,
	end_time TIMESTAMP WITHOUT TIME ZONE,
	active BOOLEAN NOT NULL,
	in_use BOOLEAN NOT NULL,
	orphan BOOLEAN NOT NULL,
	task_uuid UUID,
	result_uuid UUID
);

CREATE TABLE mg_raw_tasks (
	id BIGSERIAL PRIMARY KEY,
	sync_found BIGINT NOT NULL REFERENCES mg_syncdata_tasks(id),
	sync_vanished BIGINT DEFAULT NULL REFERENCES mg_syncdata_tasks(id),
	sync_user INTEGER NOT NULL REFERENCES mg_users(id),
	uuid UUID NOT NULL,
	created TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	modified TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	owner TEXT NOT NULL,
	name TEXT NOT NULL,
	alterable BOOLEAN NOT NULL,
	comment TEXT,
	severity REAL,
	status TEXT NOT NULL,
	progress INTEGER NOT NULL,
	config_id UUID,
	report_count INTEGER NOT NULL,
	report_uuid UUID,
	findings_high INTEGER,
	findings_medium INTEGER,
	findings_low INTEGER,
	findings_log INTEGER,
	findings_false_positive INTEGER
);

CREATE TABLE mg_raw_reports (
	id BIGSERIAL PRIMARY KEY,
	sync_found BIGINT NOT NULL REFERENCES mg_syncdata_reports(id),
	sync_vanished BIGINT DEFAULT NULL REFERENCES mg_syncdata_reports(id),
	sync_user INTEGER NOT NULL REFERENCES mg_users(id),
	uuid UUID NOT NULL,
	created TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	modified TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	owner TEXT NOT NULL,
	name TEXT NOT NULL,
	comment TEXT,
	severity_full REAL NOT NULL,
	severity_filtered REAL NOT NULL,
	status TEXT NOT NULL,
	progress INTEGER NOT NULL,
	task_uuid UUID NOT NULL,
	task_name TEXT NOT NULL,
	scan_start TIMESTAMP WITHOUT TIME ZONE,
	scan_end TIMESTAMP WITHOUT TIME ZONE,
	timezone TEXT NOT NULL,
	findings_high INTEGER NOT NULL,
	findings_medium INTEGER NOT NULL,
	findings_low INTEGER NOT NULL,
	findings_log INTEGER NOT NULL,
	findings_false_positive INTEGER NOT NULL,
	findings_high_full INTEGER NOT NULL,
	findings_medium_full INTEGER NOT NULL,
	findings_low_full INTEGER NOT NULL,
	findings_log_full INTEGER NOT NULL,
	findings_false_positive_full INTEGER NOT NULL
);

-- The *_e_* tables hold a few columns (e)xternally for deduplication
-- This is because certain columns tend to correlate and/or be duplicated a lot, so storing them like this saves a lot of space
-- In essence it is a form of database normalization because the correlated columns would otherwise be a 3NF violation
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

CREATE TABLE mg_raw_results (
	id BIGSERIAL PRIMARY KEY,
	sync_found BIGINT NOT NULL REFERENCES mg_syncdata_results(id),
	sync_vanished BIGINT DEFAULT NULL REFERENCES mg_syncdata_results(id),
	sync_user INTEGER NOT NULL REFERENCES mg_users(id),
	uuid UUID NOT NULL,
	created TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	modified TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	owner TEXT NOT NULL,
	name TEXT NOT NULL,
	comment TEXT,
	host INET NOT NULL,
	hostname TEXT,
	port TEXT NOT NULL,
	threat TEXT NOT NULL,
	severity REAL NOT NULL,
	original_threat TEXT NOT NULL,
	original_severity REAL NOT NULL,
	qod_value SMALLINT NOT NULL,
	report_uuid UUID NOT NULL,
	e_description_id BIGINT REFERENCES mg_raw_results_e_description(id),
	e_nvt_id BIGINT NOT NULL REFERENCES mg_raw_results_e_nvt(id),
	detection_product TEXT,
	detection_method TEXT,
	detection_oid TEXT
);

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

----- Friendly views for each content table -----
CREATE VIEW mg_view_notes AS
SELECT * FROM mg_raw_notes WHERE sync_vanished IS NULL;

CREATE VIEW mg_view_overrides AS
SELECT * FROM mg_raw_overrides WHERE sync_vanished IS NULL;

CREATE VIEW mg_view_tasks AS
SELECT * FROM mg_raw_tasks WHERE sync_vanished IS NULL;

CREATE VIEW mg_view_reports AS
SELECT * FROM mg_raw_reports WHERE sync_vanished IS NULL;

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
    mg_raw_results.report_uuid,
    mg_raw_results.detection_product,
    mg_raw_results.detection_method,
    mg_raw_results.detection_oid
FROM mg_raw_results
    JOIN mg_raw_results_e_description
        ON mg_raw_results.e_description_id = mg_raw_results_e_description.id
    JOIN mg_raw_results_e_nvt
        ON mg_raw_results.e_nvt_id = mg_raw_results_e_nvt.id
WHERE mg_raw_results.sync_vanished IS NULL;
