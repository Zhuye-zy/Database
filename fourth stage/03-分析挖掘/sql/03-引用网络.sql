-- 分析三 · 引用网络结构（自引用 M:N + 库外引用）
-- 数据源：patentdb.patent_citation（citing_patent_id → patent，cited_patent_id → patent，可空自引用）
--         + patentdb.non_patent_citation（非专利文献 1:1 扩展）
-- 口径说明（沿用 C 角色交接要求，避免把"发出引用"说成"被引用热度"）：
--   1) citation_type：P = 专利文献引用，N = 非专利文献引用；两类必须分开统计；
--   2) 被引专列可能不在本地库：cited_patent_id 为空但保留 cited_country/doc_number/doc_kind/date_raw；
--      因此"库内被引用热度"在本样例中为 0，本文件给出的是**引用方（出度）**结构与**被引文献的来源分布**；
--   3) 日期列 cited_doc_date_raw 为原文（YYYYMMDD 或 YYYYMM00 月精度），年代统计用前 4 位字符。

-- @query: type_split | 引用类型分布（P 专利 / N 非专利）
SELECT pc.citation_type                                AS "类型码",
       CASE pc.citation_type WHEN 'P' THEN '专利文献引用'
                             WHEN 'N' THEN '非专利文献引用'
                             ELSE '其他' END            AS "类型",
       count(*)                                        AS "引用条数",
       count(DISTINCT pc.citing_patent_id)             AS "引用方专利数"
FROM patentdb.patent_citation pc
GROUP BY pc.citation_type
ORDER BY pc.citation_type;

-- @query: out_degree | 出度 TOP10：每个引用方专利引用了他人的多少件文献
SELECT pc.citing_patent_id                             AS "引用方专利ID",
       pa.appln_auth || pa.appln_nr                    AS "申请号",
       count(*) FILTER (WHERE pc.citation_type = 'P')  AS "专利引用",
       count(*) FILTER (WHERE pc.citation_type = 'N')  AS "非专利引用",
       count(*)                                        AS "合计",
       count(*) FILTER (WHERE pc.cited_patent_id IS NOT NULL) AS "库内可解析"
FROM patentdb.patent_citation pc
JOIN patentdb.patent pa ON pa.patent_id = pc.citing_patent_id
GROUP BY pc.citing_patent_id, pa.appln_auth, pa.appln_nr
ORDER BY count(*) DESC, pc.citing_patent_id
LIMIT 10;

-- @query: cited_country | 被引专利文献的来源国别 TOP10
SELECT pc.cited_country                                AS "被引国别",
       count(*)                                        AS "被引次数"
FROM patentdb.patent_citation pc
WHERE pc.citation_type = 'P' AND pc.cited_country IS NOT NULL
GROUP BY pc.cited_country
ORDER BY count(*) DESC, pc.cited_country
LIMIT 10;

-- @query: cited_decade | 被引专利文献的年代分布（原文日期前 4 位 → 年代段）
SELECT (left(pc.cited_doc_date_raw, 4)::int / 10 * 10) AS "年代段",
       count(*)                                        AS "被引次数"
FROM patentdb.patent_citation pc
WHERE pc.citation_type = 'P'
  AND left(pc.cited_doc_date_raw, 4) BETWEEN '1900' AND '2100'
GROUP BY 1
ORDER BY 1;

-- @query: resolution | 库内解析率：被引目标有多少能连回本地 patent
SELECT count(*)                                                       AS "引用总条数",
       count(*) FILTER (WHERE pseudo.is_patent)                       AS "专利文献引用",
       count(*) FILTER (WHERE pseudo.cited_patent_id IS NOT NULL)     AS "库内已解析",
       count(*) FILTER (WHERE pseudo.is_patent
                          AND pseudo.cited_patent_id IS NULL)         AS "库外专利引用",
       count(*) FILTER (WHERE pseudo.npl_id IS NOT NULL)              AS "非专利引用明细"
FROM (
  SELECT pc.citation_id, pc.cited_patent_id, (pc.citation_type = 'P') AS is_patent,
         (SELECT npl.npl_id FROM patentdb.non_patent_citation npl
           WHERE npl.citation_id = pc.citation_id) AS npl_id
  FROM patentdb.patent_citation pc
) pseudo;
