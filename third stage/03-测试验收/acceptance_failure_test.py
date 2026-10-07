#!/usr/bin/env python3
"""Only for fresh disposable acceptance DB: ensure bad databases fail gates."""
import subprocess,sys
from test_support import *

def main():
    report=Report('acceptance_failure_result');conn=None
    try:
        require(os.environ.get('PHASE3_DISPOSABLE')=='1','此故障注入测试仅允许在 verify_fresh.py 的一次性数据库运行')
        conn=connect();conn.autocommit=True
        with conn.cursor() as cur:
            require_schema(cur);before=fingerprint(cur)
            cur.execute('CREATE SCHEMA phase3_empty_test')
            def run(name,schema=SCHEMA):
                proc=subprocess.run([sys.executable,str(ROOT/'03-测试验收'/name)],env={**os.environ,'DB_SCHEMA':schema},capture_output=True,text=True)
                require(proc.returncode!=0,'错误环境却返回成功退出码: '+name)
                return {'exit_code':proc.returncode}
            for name in ['smoke_test.py','fk_violation_test.py']:
                report.case(name+'_missing_schema',lambda name=name:run(name,'phase3_no_such_schema'))
                report.case(name+'_empty_schema',lambda name=name:run(name,'phase3_empty_test'))
            cur.execute("SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname='fk_patent_citation_cited_patent_id' AND connamespace=(SELECT oid FROM pg_namespace WHERE nspname=%s)",(SCHEMA,));definition=cur.fetchone()[0]
            try:
                cur.execute('ALTER TABLE patent_citation DROP CONSTRAINT fk_patent_citation_cited_patent_id')
                report.case('missing_cited_patent_fk_nonzero',lambda:run('fk_violation_test.py'))
            finally:cur.execute('ALTER TABLE patent_citation ADD CONSTRAINT fk_patent_citation_cited_patent_id '+definition)
            report.case('all_business_content_unchanged',lambda:require(fingerprint(cur)==before,'故障模拟污染数据'))
            cur.execute('DROP SCHEMA phase3_empty_test')
    except Exception as error:report.case('setup',lambda:require(False,str(error)))
    finally:
        if conn:conn.close()
    return report.finish()
if __name__=='__main__':raise SystemExit(main())
