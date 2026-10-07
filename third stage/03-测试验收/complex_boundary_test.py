#!/usr/bin/env python3
"""Result-set assertions and transactional boundary cases, never commit fixtures."""
from test_support import *
from psycopg2.errors import NotNullViolation, StringDataRightTruncation

def main():
    report=Report("complex_boundary_result");conn=None
    try:
        conn=connect()
        with conn.cursor() as cur:
            require_schema(cur);before=fingerprint(cur)
            def applicants():
                cur.execute("SELECT person_id FROM patent_applicant GROUP BY person_id ORDER BY count(*) DESC,person_id LIMIT 1");person=cur.fetchone()[0]
                cur.execute("SELECT patent_id FROM patent_applicant WHERE person_id=%s ORDER BY patent_id",(person,));expected=cur.fetchall()
                cur.execute("SELECT p.patent_id FROM person n JOIN patent_applicant a USING(person_id) JOIN patent p USING(patent_id) WHERE n.person_id=%s ORDER BY p.patent_id",(person,));actual=cur.fetchall()
                require(bool(expected) and actual==expected,"申请人专利集合不匹配")
                return {"person_id":person,"patent_ids":[r[0] for r in actual]}
            report.case("specific_applicant_patents",applicants)
            def citations():
                cur.execute("SELECT citing_patent_id FROM patent_citation WHERE citation_type='P' GROUP BY 1 ORDER BY count(*) DESC,1 LIMIT 1");pid=cur.fetchone()[0]
                cur.execute("SELECT citation_id FROM patent_citation WHERE citing_patent_id=%s AND citation_type='P' ORDER BY citation_id",(pid,));expected=cur.fetchall()
                cur.execute("SELECT c.citation_id,c.cited_patent_id,p.patent_id,c.cited_country,c.cited_doc_number,c.cited_doc_kind FROM patent src JOIN patent_citation c ON c.citing_patent_id=src.patent_id LEFT JOIN patent p ON p.patent_id=c.cited_patent_id WHERE src.patent_id=%s AND c.citation_type='P' ORDER BY c.citation_id",(pid,));rows=cur.fetchall()
                require([(r[0],) for r in rows]==expected and bool(rows),"引用集合不匹配")
                require(all((r[1] is None and r[4]) or r[1]==r[2] for r in rows),"引用目标既无法连接也无来源号码")
                return {"patent_id":pid,"patent_citations":len(rows),"internal_targets":sum(r[1] is not None for r in rows),"external_examples":[list(r[3:]) for r in rows[:3]]}
            report.case("specific_patent_citations",citations)
            def families():
                cur.execute("SELECT family_id FROM patent_family ORDER BY family_id");ids=[r[0] for r in cur.fetchall()];require(bool(ids),"无可验收专利族")
                details=[]
                for fid in ids:
                    cur.execute("SELECT member_id FROM patent_family_member WHERE family_id=%s ORDER BY member_id",(fid,));expected=cur.fetchall()
                    cur.execute("SELECT m.member_id,m.member_patent_id,p.patent_id FROM patent_family f JOIN patent_family_member m USING(family_id) LEFT JOIN patent p ON p.patent_id=m.member_patent_id WHERE f.family_id=%s ORDER BY m.member_id",(fid,));actual=cur.fetchall()
                    require(bool(expected) and [(r[0],) for r in actual]==expected,"族成员集合不匹配")
                    require(all(r[1] is None or r[1]==r[2] for r in actual),"族成员库内连接失效")
                    refs={}
                    for table in ["family_member_application_ref","family_member_publication_ref"]:
                        cur.execute(sql.SQL("SELECT count(*) FROM {} WHERE member_id IN (SELECT member_id FROM patent_family_member WHERE family_id=%s)").format(sql.Identifier(table)),(fid,));expected_count=cur.fetchone()[0]
                        cur.execute(sql.SQL("SELECT count(*) FROM patent_family f JOIN patent_family_member m USING(family_id) JOIN {} r USING(member_id) WHERE f.family_id=%s").format(sql.Identifier(table)),(fid,));require(cur.fetchone()[0]==expected_count,"原始族成员引用遗漏")
                        refs[table]=expected_count
                    details.append({"family_id":fid,"member_ids":[r[0] for r in actual],"source_refs":refs})
                return details
            report.case("all_family_members_and_source_refs",families)
            def transaction_case(name,fn):
                def run():
                    cur.execute("SAVEPOINT boundary")
                    try:return fn()
                    finally:cur.execute("ROLLBACK TO SAVEPOINT boundary");cur.execute("RELEASE SAVEPOINT boundary")
                report.case(name,run)
            def null_optional():
                cur.execute("SELECT section_id FROM description_section LIMIT 1");sid=cur.fetchone()[0]
                cur.execute("UPDATE description_section SET section_text=NULL,heading=NULL WHERE section_id=%s RETURNING section_text,heading",(sid,));require(cur.fetchone()==(None,None),"可空字段无法保留 NULL")
                return {"NULL_fields":["section_text","heading"]}
            transaction_case("nullable_fields",null_optional)
            def not_null():
                try:cur.execute("UPDATE claim SET claim_text=NULL WHERE claim_id=(SELECT min(claim_id) FROM claim)")
                except NotNullViolation as e:return {"sqlstate":e.pgcode,"column":e.diag.column_name}
                raise AssertionError("必填文本 NULL 未被拒绝")
            transaction_case("required_text_rejects_null",not_null)
            def empty():
                cur.execute("UPDATE abstract SET abstract_text='' WHERE abstract_id=(SELECT min(abstract_id) FROM abstract) RETURNING abstract_text");require(cur.fetchone()==('',),"空字符串往返不一致")
                return "TEXT 空字符串与 NULL 区分；schema 未要求非空字符串"
            transaction_case("empty_string_round_trip",empty)
            special="中文 日本語 한국어 café 🧪 O'Reilly \\ & <tag> \"双引号\"\n第二行"
            for table,id_col,col in [("abstract","abstract_id","abstract_text"),("claim","claim_id","claim_text"),("description_section","section_id","section_text")]:
                def text_roundtrip(table=table,id_col=id_col,col=col):
                    value=special*12000
                    cur.execute(sql.SQL("UPDATE {} SET {}=%s WHERE {}=(SELECT min({}) FROM {}) RETURNING {},length({}),octet_length({})").format(*map(sql.Identifier,[table,col,id_col,id_col,table,col,col,col])),(value,));stored,chars,bytes_=cur.fetchone()
                    require(stored==value and chars==len(value),"超长/特殊字符文本被截断或编码改变")
                    return {"characters":chars,"utf8_bytes":bytes_,"sha256":hashlib.sha256(stored.encode()).hexdigest()}
                transaction_case(table+"_long_unicode_text",text_roundtrip)
            def too_long():
                try:cur.execute("UPDATE person SET person_name=%s WHERE person_id=(SELECT min(person_id) FROM person)",('x'*501,))
                except StringDataRightTruncation as e:return {"sqlstate":e.pgcode,"limit":500}
                raise AssertionError("VARCHAR(500) 越界未被拒绝")
            transaction_case("varchar_limit_rejection",too_long)
            def internal_citation():
                cur.execute("SELECT patent_id FROM patent ORDER BY patent_id LIMIT 2");a,b=[r[0] for r in cur.fetchall()]
                cur.execute("UPDATE patent_citation SET citing_patent_id=%s,cited_patent_id=%s WHERE citation_id=(SELECT min(citation_id) FROM patent_citation WHERE citation_type='P') RETURNING citation_id",(a,b));cid=cur.fetchone()[0]
                cur.execute("SELECT x.patent_id,y.patent_id FROM patent_citation c JOIN patent x ON x.patent_id=c.citing_patent_id JOIN patent y ON y.patent_id=c.cited_patent_id WHERE citation_id=%s",(cid,));require(cur.fetchone()==(a,b),"库内双端正例连接失效")
                return "事务内测试正例，回滚；不将测试引用作为官方数据"
            transaction_case("internal_patent_citation_positive",internal_citation)
            report.case("all_business_content_unchanged",lambda:require(fingerprint(cur)==before,"测试污染业务表"))
        conn.rollback()
    except Exception as error:report.case("setup",lambda:require(False,str(error)))
    finally:
        if conn:conn.rollback();conn.close()
    return report.finish()
if __name__=="__main__":raise SystemExit(main())
