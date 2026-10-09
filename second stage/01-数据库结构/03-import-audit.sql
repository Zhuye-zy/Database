-- Operational metadata is separate from the 43-table business model.
BEGIN;
CREATE SCHEMA IF NOT EXISTS stage2_meta;
CREATE TABLE IF NOT EXISTS stage2_meta.import_batch(
 batch_id uuid PRIMARY KEY, started_at timestamptz NOT NULL DEFAULT now(),
 finished_at timestamptz, source_root text NOT NULL,
 status text NOT NULL CHECK(status IN ('RUNNING','SUCCEEDED','FAILED')),
 summary jsonb NOT NULL DEFAULT '{}'::jsonb);
CREATE TABLE IF NOT EXISTS stage2_meta.source_document(
 batch_id uuid NOT NULL REFERENCES stage2_meta.import_batch,
 source_file text NOT NULL, document_index integer NOT NULL,
 dataset text NOT NULL, logical_identifier text,
 xml_path text NOT NULL, sha256 char(64), raw_operation text,
 disposition text NOT NULL, raw_xml text,
 error_type text, error_message text,
 PRIMARY KEY(batch_id,source_file,document_index));
CREATE TABLE IF NOT EXISTS stage2_meta.publication_state(
 publn_auth char(2) NOT NULL, publn_nr varchar(30) NOT NULL, publn_kind varchar(2) NOT NULL,
 source_doc_id text, last_exchange_date date, is_deleted boolean NOT NULL DEFAULT false,
 last_operation text NOT NULL, last_batch_id uuid NOT NULL REFERENCES stage2_meta.import_batch,
 PRIMARY KEY(publn_auth,publn_nr,publn_kind));
CREATE INDEX IF NOT EXISTS ix_source_document_identifier ON stage2_meta.source_document(logical_identifier);
CREATE OR REPLACE VIEW stage2_meta.active_publication AS
 SELECT p.* FROM patentdb.publication p
 LEFT JOIN stage2_meta.publication_state s USING(publn_auth,publn_nr,publn_kind)
 WHERE NOT coalesce(s.is_deleted,false);
COMMENT ON SCHEMA stage2_meta IS 'B阶段批次、来源、错误及软删除元数据；不计入A的43张业务表';
COMMENT ON VIEW stage2_meta.active_publication IS '展示端优先从此视图读取文献；D只软删除，CV/DV仅记撤回通知';
COMMIT;
