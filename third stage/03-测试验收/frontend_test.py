#!/usr/bin/env python3
"""Verify every table/detail plus pagination, soft deletion and visible errors."""
import importlib.util, sys
from flask import template_rendered
from test_support import *

class BorrowedConnection:
    def __init__(self, conn): self.conn=conn
    def cursor(self, *args, **kwargs): return self.conn.cursor(*args, **kwargs)
    def close(self): pass

def main():
    report=Report('frontend_result');conn=None
    try:
        conn=connect()
        with conn.cursor() as cur:
            require_schema(cur);before=fingerprint(cur)
            path=ROOT/'01-前端应用/app.py'
            spec=importlib.util.spec_from_file_location('phase3_frontend',path);module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
            module.app.testing=True;module.get_conn=lambda:BorrowedConnection(conn)
            client=module.app.test_client();contexts=[]
            def capture(sender,template,context,**extra):contexts.append(context)
            template_rendered.connect(capture,module.app)
            def request(path,expected=200):
                contexts.clear();resp=client.get(path);require(resp.status_code==expected,f'{path}: expected={expected}, actual={resp.status_code}')
                return contexts[-1] if contexts else {}
            report.case('home_43_tables',lambda:require(request('/')['total']==43,'首页表数错误'))
            for table in sorted(BASELINE):report.case('table_'+table,lambda table=table:require(request('/table/'+table)['total']==BASELINE[table],'行数错误'))
            cur.execute('SELECT patent_id FROM patent ORDER BY 1');ids=[r[0] for r in cur.fetchall()]
            for pid in ids:report.case('patent_'+str(pid),lambda pid=pid:require(request('/patent/'+str(pid))['pid']==pid,'详情 ID 不符'))
            report.case('unknown_table_404',lambda:request('/table/no_such_table',404))
            report.case('unknown_patent_404',lambda:request('/patent/99999999',404))
            report.case('invalid_page',lambda:require(request('/table/patent?page=bad')['page']==1,'非法页码未回到第一页'))
            def pagination():
                a=request('/table/patent_citation?page=1')['rows'];b=request('/table/patent_citation?page=2')['rows']
                require(len(a)==module.PAGE_SIZE and len(b)==module.PAGE_SIZE,'分页大小错误')
                require(not {r['citation_id'] for r in a}&{r['citation_id'] for r in b},'相邻页数据重复')
                return {'first_page':len(a),'second_page':len(b)}
            report.case('pagination_distinct_rows',pagination)
            def soft_delete():
                cur.execute('SAVEPOINT front_soft')
                try:
                    cur.execute('SELECT p.publication_id,p.patent_id,p.publn_auth,p.publn_nr,p.publn_kind FROM publication p JOIN stage2_meta.publication_state s USING(publn_auth,publn_nr,publn_kind) ORDER BY p.publication_id LIMIT 1');pub,pid,*key=cur.fetchone()
                    cur.execute('UPDATE stage2_meta.publication_state SET is_deleted=true WHERE publn_auth=%s AND publn_nr=%s AND publn_kind=%s',key)
                    context=request('/patent/'+str(pid));require(pub not in [p['publication_id'] for p in context['pubs']],'详情暴露软删除文献')
                    require(all(c['publication_id']!=pub for c in context['claims']),'详情暴露软删除文献权利要求')
                    require(any(p['publication_id']==pub for p in request('/table/publication')['rows']),'物理追溯表错误过滤记录')
                    return {'deleted_publication_id':pub,'detail_filtered':True,'physical_table_preserved':True}
                finally:cur.execute('ROLLBACK TO SAVEPOINT front_soft');cur.execute('RELEASE SAVEPOINT front_soft')
            report.case('soft_deleted_publication_and_claims',soft_delete)
            def broken_query():
                cur.execute('SAVEPOINT front_error')
                try:
                    cur.execute('ALTER TABLE patent_applicant RENAME COLUMN person_id TO test_missing_person_id')
                    response=client.get('/patent/'+str(ids[0]));require(response.status_code==503,'数据库错误未返回 503')
                    require('数据加载失败' in response.get_data(as_text=True),'未显示加载失败')
                    return {'http_status':503}
                finally:cur.execute('ROLLBACK TO SAVEPOINT front_error');cur.execute('RELEASE SAVEPOINT front_error')
            report.case('query_error_is_not_empty_data',broken_query)
            def schema_error():
                original=module.SCHEMA
                try:module.SCHEMA='does_not_exist_phase3';request('/',503)
                finally:module.SCHEMA=original
                return {'http_status':503}
            report.case('missing_schema_503',schema_error)
            report.case('all_business_content_unchanged',lambda:require(fingerprint(cur)==before,'前端测试污染业务内容'))
            template_rendered.disconnect(capture,module.app)
        conn.rollback()
    except Exception as error:report.case('setup',lambda:require(False,str(error)))
    finally:
        if conn:conn.rollback();conn.close()
    return report.finish()
if __name__=='__main__':raise SystemExit(main())
