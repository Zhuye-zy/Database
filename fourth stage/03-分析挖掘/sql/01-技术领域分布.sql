-- 分析一 · 技术领域分布（D 角色，第五项：专利数据分析与挖掘）
-- 数据源：patentdb.patent_classification（专利×分类号 M:N）⋈ patentdb.classification（符号自身属性）
-- 口径说明：
--   1) 分类号来自官方样例 XML 的 (51)(52)(58) 字段，IPC 与 CPC 两套体系分开统计，不混算；
--   2) 顶层统计按"专利"去重（count(DISTINCT patent_id)），因为同一专利可有多条分类号；
--   3) classification.section 为部（A–H/Y），class_no 为大类号，subclass 为小类字母；
--   4) 部的名称取自 WIPO IPC 标准（非本库数据），见报告中的对照表。

-- @query: ipc_section | 分类体系的部级分布（专利去重 + 分类号条数）
SELECT c.scheme_code                                   AS "分类体系",
       c.section                                       AS "部",
       count(DISTINCT pc.patent_id)                    AS "专利数",
       count(*)                                        AS "分类号条数"
FROM patentdb.patent_classification pc
JOIN patentdb.classification c USING (scheme_code, symbol)
WHERE c.section IS NOT NULL
GROUP BY c.scheme_code, c.section
ORDER BY c.scheme_code, count(DISTINCT pc.patent_id) DESC, c.section;

-- @query: ipc_class | 大类 TOP12（如 H01、A01）
SELECT pc.scheme_code                                  AS "分类体系",
       (c.section || c.class_no)                       AS "大类",
       count(DISTINCT pc.patent_id)                    AS "专利数",
       count(*)                                        AS "分类号条数"
FROM patentdb.patent_classification pc
JOIN patentdb.classification c USING (scheme_code, symbol)
WHERE c.section IS NOT NULL AND c.class_no IS NOT NULL
GROUP BY pc.scheme_code, (c.section || c.class_no)
ORDER BY count(DISTINCT pc.patent_id) DESC, "大类"
LIMIT 12;

-- @query: coverage | 分类覆盖度（有分类号的专利占比）
SELECT count(DISTINCT pc.patent_id)                                       AS "有分类号的专利",
       (SELECT count(*) FROM patentdb.patent)                             AS "专利总数",
       round(100.0 * count(DISTINCT pc.patent_id)
             / (SELECT count(*) FROM patentdb.patent), 1)                 AS "覆盖率百分比"
FROM patentdb.patent_classification pc;
