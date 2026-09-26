-- Idempotent stage-B audit corrections. Apply after 01-create-schema.sql.
BEGIN;
ALTER TABLE patentdb.country_office
 ALTER COLUMN organisation_flag DROP NOT NULL,
 ALTER COLUMN is_epo_member DROP NOT NULL,
 ALTER COLUMN is_eu_member DROP NOT NULL,
 ALTER COLUMN discontinued DROP NOT NULL;
UPDATE patentdb.country_office SET organisation_flag=NULL,is_epo_member=NULL,is_eu_member=NULL,discontinued=NULL
WHERE st3_name=ctry_code AND iso_alpha3 IS NULL;
ALTER TABLE patentdb.patent ALTER COLUMN appln_filing_date DROP NOT NULL;
ALTER TABLE patentdb.ipc_techn_field ALTER COLUMN ipc_maingroup_symbol TYPE VARCHAR(30);
DELETE FROM patentdb.patent_family
 WHERE family_id=9000001 AND family_type='LOCAL' AND source_family_id=-3048794
 AND note LIKE 'LOCAL_PLACEHOLDER for cited US3048794%';
CREATE OR REPLACE FUNCTION patentdb.check_person_isa() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE ids bigint[]; pid bigint; typ char(1); nat boolean; org boolean;
BEGIN
 IF TG_OP='INSERT' THEN ids:=ARRAY[NEW.person_id];
 ELSIF TG_OP='DELETE' THEN ids:=ARRAY[OLD.person_id];
 ELSE ids:=ARRAY[OLD.person_id,NEW.person_id]; END IF;
 FOREACH pid IN ARRAY ids LOOP
  SELECT person_type INTO typ FROM patentdb.person WHERE person_id=pid;
  IF NOT FOUND THEN CONTINUE; END IF;
  SELECT EXISTS(SELECT 1 FROM patentdb.natural_person WHERE person_id=pid),
         EXISTS(SELECT 1 FROM patentdb.organization WHERE person_id=pid) INTO nat,org;
  IF NOT ((typ='N' AND nat AND NOT org) OR (typ='L' AND org AND NOT nat)) THEN
   RAISE EXCEPTION 'person % must have exactly one subtype matching person_type %',pid,typ;
  END IF;
 END LOOP;
 RETURN NULL;
END; $$;
DO $$
BEGIN
 IF NOT EXISTS(SELECT 1 FROM pg_constraint WHERE conname='ck_claim_positive' AND connamespace='patentdb'::regnamespace) THEN
 ALTER TABLE patentdb.claim ADD CONSTRAINT ck_claim_positive CHECK(claim_number>0 AND claim_seq>0);
 ALTER TABLE patentdb.claim_dependency ADD CONSTRAINT ck_claim_not_self CHECK(dependent_claim_id<>parent_claim_id);
 ALTER TABLE patentdb.publication ADD CONSTRAINT ck_publication_nonnegative_counts
 CHECK ((number_of_claims IS NULL OR number_of_claims>=0) AND (number_of_figures IS NULL OR number_of_figures>=0));
 END IF;
END; $$;
COMMENT ON COLUMN patentdb.country_office.st3_name IS '样例仅含代码时暂存代码；未核实的正式名称不得视为已完整导入';
COMMENT ON COLUMN patentdb.country_office.is_epo_member IS 'NULL=官方样例未提供/未核实，不能推断为N';
COMMENT ON COLUMN patentdb.patent_citation_category.relevant_claim IS '0表示来源未给出对应权利要求，不代表第0项权利要求';
COMMENT ON TABLE patentdb.family_citation IS '仅允许两端均可由真实来源确认的专利族；不得为非空而虚构族号';

-- Preserve the application kind explicitly supplied by the reviewed DOCDB/legal XML.
UPDATE patentdb.patent SET appln_kind='A' WHERE appln_auth='EP' AND appln_nr='79100245' AND appln_kind='NA' AND dataset_id IN (4,5);
UPDATE patentdb.patent SET appln_kind='A' WHERE appln_auth='EP' AND appln_nr='79100654' AND appln_kind='NA' AND dataset_id IN (4,5);
UPDATE patentdb.patent SET appln_kind='A' WHERE appln_auth='EP' AND appln_nr='19778361' AND appln_kind='NA' AND dataset_id IN (4,5);
COMMIT;
