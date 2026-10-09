-- 分析四 · 权利要求结构与说明书/附图规模
-- 数据源：patentdb.claim（弱实体，部分键 (lang_code, claim_number)）
--         + patentdb.claim_dependency（一元递归依赖）
--         + patentdb.description_section / patentdb.drawing（弱实体）
-- 口径说明：
--   1) claim_type：I = 独立权利要求，D = 从属权利要求（官方 XML 显式给出）；
--   2) 多语言：EP 文献的 title/claim 按语言分套，语言需分开统计，不能相加后当作"权利要求总数"；
--   3) 右表用 LEFT JOIN 聚合，避免把"没有权利要求全文的文献"（如部分外观设计/摘要级数据）直接丢弃。

-- @query: claim_type | 权利要求类型分布（全部语言合计）
SELECT cl.claim_type                                   AS "类型码",
       CASE cl.claim_type WHEN 'I' THEN '独立权利要求'
                          WHEN 'D' THEN '从属权利要求'
                          ELSE '未标注' END             AS "类型",
       count(*)                                        AS "条数",
       count(DISTINCT cl.publication_id)               AS "涉及文献"
FROM patentdb.claim cl
GROUP BY cl.claim_type
ORDER BY cl.claim_type;

-- @query: lang_split | 权利要求与标题的语言分布（EP 多语言口径）
SELECT lang.lang_code                                  AS "语言",
       (SELECT count(*) FROM patentdb.claim c  WHERE c.lang_code  = lang.lang_code) AS "权利要求",
       (SELECT count(*) FROM patentdb.title t  WHERE t.lang_code  = lang.lang_code) AS "标题"
FROM (SELECT DISTINCT lang_code FROM patentdb.claim
      UNION SELECT DISTINCT lang_code FROM patentdb.title) lang
ORDER BY "权利要求" DESC, "语言";

-- @query: doc_structure | 文献结构 TOP8（权利要求/说明书章节/附图）
SELECT p.publication_id                                 AS "文献ID",
       p.publn_auth || p.publn_nr || p.publn_kind       AS "文献号",
       p.publn_kind                                     AS "种类码",
       count(DISTINCT cl.claim_id) FILTER (WHERE cl.claim_type = 'I') AS "独立权项",
       count(DISTINCT cl.claim_id) FILTER (WHERE cl.claim_type = 'D') AS "从属权项",
       count(DISTINCT ds.section_id)                    AS "说明书章节",
       count(DISTINCT dr.drawing_id)                    AS "附图",
       p.number_of_claims                               AS "源文件声明权项数"
FROM patentdb.publication p
LEFT JOIN patentdb.claim cl              ON cl.publication_id = p.publication_id
LEFT JOIN patentdb.description_section ds ON ds.publication_id = p.publication_id
LEFT JOIN patentdb.drawing dr            ON dr.publication_id = p.publication_id
GROUP BY p.publication_id, p.publn_auth, p.publn_nr, p.publn_kind, p.number_of_claims
ORDER BY count(DISTINCT cl.claim_id) DESC, p.publication_id
LIMIT 8;

-- @query: dependency | 权利要求依赖（claim_dependency）依赖类型统计
SELECT cd.dependency_type                              AS "依赖类型",
       count(*)                                        AS "依赖条数",
       count(DISTINCT cd.dependent_claim_id)           AS "从属权项数"
FROM patentdb.claim_dependency cd
GROUP BY cd.dependency_type
ORDER BY count(*) DESC;
