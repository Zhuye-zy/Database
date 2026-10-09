-- 分析二 · 申请人排名与人员角色分布
-- 数据源：patentdb.person（ISA 超类，person_type: L=机构 / N=自然人）
--         + 五张角色关联表（M:N，均含联系属性 sequence_nr）
-- 口径说明：
--   1) 排名按"专利数"（count DISTINCT patent_id）降序，避免同一专利多申请人重复计数；
--   2) 一件专利可以有多个申请人（样例 18 条申请人关联覆盖 16 件专利），因此排名不等于专利数总和；
--   3) 姓名未做消歧（同名不同人 / 同一人不同写法无法自动区分），结果仅作样例内观察。

-- @query: applicant_rank | 申请人 TOP15（机构/自然人标注）
SELECT p.person_name                                   AS "申请人",
       CASE p.person_type WHEN 'L' THEN '机构' WHEN 'N' THEN '自然人' ELSE '未标注' END AS "类型",
       count(DISTINCT pa.patent_id)                    AS "专利数",
       count(*)                                        AS "关联条数",
       min(pa.sequence_nr)                             AS "最小顺序号"
FROM patentdb.patent_applicant pa
JOIN patentdb.person p USING (person_id)
GROUP BY p.person_name, p.person_type
ORDER BY count(DISTINCT pa.patent_id) DESC, p.person_name
LIMIT 15;

-- @query: applicant_type | 申请主体类型分布
SELECT CASE p.person_type WHEN 'L' THEN '机构' WHEN 'N' THEN '自然人' ELSE '未标注' END AS "类型",
       count(DISTINCT p.person_id)                     AS "人数",
       count(DISTINCT pa.patent_id)                    AS "涉及专利",
       count(*)                                        AS "关联条数"
FROM patentdb.patent_applicant pa
JOIN patentdb.person p USING (person_id)
GROUP BY 1
ORDER BY "关联条数" DESC;

-- @query: role_summary | 五类人员角色（申请人/发明人/权利人/代理人/审查员）对比
SELECT '申请人' AS "角色", count(*) AS "关联条数", count(DISTINCT patent_id) AS "专利数" FROM patentdb.patent_applicant
UNION ALL
SELECT '发明人', count(*), count(DISTINCT patent_id) FROM patentdb.patent_inventor
UNION ALL
SELECT '权利人（受让人）', count(*), count(DISTINCT patent_id) FROM patentdb.patent_assignee
UNION ALL
SELECT '代理人', count(*), count(DISTINCT patent_id) FROM patentdb.patent_agent
UNION ALL
SELECT '审查员', count(*), count(DISTINCT patent_id) FROM patentdb.patent_examiner
ORDER BY "关联条数" DESC;
