-- 分析五 · 数据来源分布、时间分布与专利族规模
-- 数据源：patentdb.dataset / patent / publication / patent_family / patent_family_member
--         + patentdb.legal_status_event / legal_event_code + patentdb.patent_keyword
-- 口径说明：
--   1) 数据来源按官方样例的 5 类目录统计：US 申请公布、US 授权公告、EP 全文、EP DOCDB 摘要、
--      EP 法律状态（第 5 类是补充法律事件用的官方样例，不是题面四类之外的必选数据源）；
--   2) 年份来自 publn_date / appln_filing_date；月精度或哨兵值在导入时已转 NULL 并保留 *_raw，
--      所以年份分布只统计可确定到日的记录，不代表全部数据；
--   3) 专利族按 DOCDB/INPADOC 两种族口径分组，成员数含库外成员；库内成员为能连回本地 patent 的成员。

-- @query: dataset_split | 数据来源分布
SELECT d.dataset_code                                  AS "数据集",
       d.dataset_name_cn                               AS "中文名",
       (SELECT count(*) FROM patentdb.publication p WHERE p.dataset_id = d.dataset_id) AS "文献数",
       (SELECT count(*) FROM patentdb.patent pa WHERE pa.dataset_id = d.dataset_id)    AS "申请数"
FROM patentdb.dataset d
ORDER BY "文献数" DESC, d.dataset_code;

-- @query: publn_year | 公布年份分布
SELECT extract(year FROM p.publn_date)::int            AS "公布年份",
       count(*)                                        AS "文献数"
FROM patentdb.publication p
WHERE p.publn_date IS NOT NULL
GROUP BY 1
ORDER BY 1;

-- @query: filing_year | 申请年份分布
SELECT extract(year FROM pa.appln_filing_date)::int    AS "申请年份",
       count(*)                                        AS "申请数"
FROM patentdb.patent pa
WHERE pa.appln_filing_date IS NOT NULL
GROUP BY 1
ORDER BY 1;

-- @query: family_size | 专利族规模
SELECT pf.family_id                                    AS "族ID",
       pf.family_type                                  AS "族类型",
       count(pfm.member_id)                            AS "成员总数",
       count(pfm.member_patent_id)                     AS "库内成员",
       count(*) FILTER (WHERE pfm.is_representative = 'Y') AS "代表文献数"
FROM patentdb.patent_family pf
LEFT JOIN patentdb.patent_family_member pfm ON pfm.family_id = pf.family_id
GROUP BY pf.family_id, pf.family_type
ORDER BY count(pfm.member_id) DESC, pf.family_id;

-- @query: legal_event | 法律状态事件码分布
SELECT lse.event_code                                  AS "事件码",
       lec.event_descr                                 AS "事件说明",
       count(*)                                        AS "事件条数"
FROM patentdb.legal_status_event lse
LEFT JOIN patentdb.legal_event_code lec
       ON lec.event_auth = lse.event_auth AND lec.event_code = lse.event_code
GROUP BY lse.event_code, lec.event_descr
ORDER BY count(*) DESC, lse.event_code;

-- @query: keyword_source | 关键词来源（必须标注为本地派生）
SELECT 'patent_keyword 关联条数' AS "指标", count(*)::text AS "数值" FROM patentdb.patent_keyword
UNION ALL
SELECT 'keyword 词条数', count(*)::text FROM patentdb.keyword
UNION ALL
SELECT 'source=' || kw.source, count(*)::text FROM patentdb.keyword kw GROUP BY kw.source
ORDER BY 1;
