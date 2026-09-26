\pset pager off
\echo === Publications and titles ===
SELECT p.publication_id,p.publn_auth,p.publn_nr,p.publn_kind,t.lang_code,t.title_text
FROM patentdb.publication p LEFT JOIN patentdb.title t USING(publication_id)
ORDER BY p.publication_id,t.lang_code LIMIT 20;
\echo === Claims in all languages ===
SELECT p.publn_nr,c.lang_code,count(*) AS claims
FROM patentdb.publication p JOIN patentdb.claim c USING(publication_id)
GROUP BY p.publn_nr,c.lang_code ORDER BY p.publn_nr,c.lang_code;
\echo === Raw external citations ===
SELECT citation_id,cited_country,cited_doc_number,cited_doc_kind,cited_doc_date,cited_doc_date_raw
FROM patentdb.patent_citation WHERE citation_type='P' AND cited_publn_id IS NULL LIMIT 10;
\echo === Applicants ===
SELECT p.appln_auth,p.appln_nr,r.sequence_nr,n.person_name
FROM patentdb.patent p JOIN patentdb.patent_applicant r USING(patent_id)
JOIN patentdb.person n USING(person_id) ORDER BY p.patent_id,r.sequence_nr LIMIT 10;
\echo === Legal events ===
SELECT p.appln_nr,e.event_code,e.event_publn_date,e.event_text
FROM patentdb.patent p JOIN patentdb.legal_status_event e USING(patent_id) ORDER BY e.event_seq_nr;
\echo === Query execution plan: small samples may correctly use sequential scans ===
EXPLAIN (ANALYZE,BUFFERS)
SELECT p.publn_nr,t.title_text,c.claim_number
FROM patentdb.publication p JOIN patentdb.title t USING(publication_id)
JOIN patentdb.claim c USING(publication_id)
WHERE p.publn_auth='EP' AND t.lang_code='EN' AND c.lang_code='EN';
