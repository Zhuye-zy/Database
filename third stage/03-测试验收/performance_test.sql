-- C 角色性能测试与调优
-- 用法：sudo docker exec -i patentdb psql -X -U postgres -d patentdb -v ON_ERROR_STOP=1 < performance_test.sql

\timing on

\echo '===== P1: 申请人 -> 专利 三表 JOIN ====='
EXPLAIN (ANALYZE, BUFFERS)
SELECT p.patent_id, pe.person_name
FROM patentdb.patent p
JOIN patentdb.patent_applicant pa ON pa.patent_id = p.patent_id
JOIN patentdb.person pe ON pe.person_id = pa.person_id
LIMIT 1000;

\echo '===== P2: 专利 -> 发出专利引用数量 ====='
EXPLAIN (ANALYZE, BUFFERS)
SELECT citing_patent_id, count(*) AS n
FROM patentdb.patent_citation
WHERE citation_type = 'P'
GROUP BY citing_patent_id
ORDER BY n DESC
LIMIT 20;

\echo '===== P3: 分类体系分布（IPC/CPC，非技术领域） ====='
EXPLAIN (ANALYZE, BUFFERS)
SELECT scheme_code, count(*)
FROM patentdb.patent_classification
GROUP BY scheme_code
ORDER BY 2 DESC;

\echo '===== P4: 申请时间趋势 ====='
EXPLAIN (ANALYZE, BUFFERS)
SELECT date_trunc('year', appln_filing_date) AS y, count(*)
FROM patentdb.patent
WHERE appln_filing_date IS NOT NULL
GROUP BY y
ORDER BY y;

-- 索引优化建议（按 EXPLAIN 结果决定是否取消注释）
-- CREATE INDEX IF NOT EXISTS idx_patent_applicant_patent
--   ON patentdb.patent_applicant (patent_id);
-- CREATE INDEX IF NOT EXISTS idx_patent_applicant_person
--   ON patentdb.patent_applicant (person_id);
-- CREATE INDEX IF NOT EXISTS idx_patent_inventor_patent
--   ON patentdb.patent_inventor (patent_id);
-- CREATE INDEX IF NOT EXISTS idx_patent_citation_citing_patent
--   ON patentdb.patent_citation (citing_patent_id);
-- CREATE INDEX IF NOT EXISTS idx_patent_classification_patent
--   ON patentdb.patent_classification (patent_id);
