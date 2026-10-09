#!/usr/bin/env python3
"""Build, import, test, dump and restore in a unique disposable container."""
from pathlib import Path
import subprocess,sys,os,uuid,time,json,hashlib,datetime,secrets
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent;B=REPO/'second stage'
sys.path.insert(0,str(ROOT/'03-测试验收'))
from test_support import connect,fingerprint
OUT=ROOT/'07-验收结果';OUT.mkdir(exist_ok=True)
C='patentdb-phase3-check-'+uuid.uuid4().hex[:10]
IMAGE=os.environ.get('POSTGRES_IMAGE','docker.m.daocloud.io/library/postgres:16')
ENV={**os.environ,'PATENT_CONTAINER':C,'PGHOST':'127.0.0.1','PGDATABASE':'patentdb','PGUSER':'postgres','PGPASSWORD':secrets.token_hex(16),'DB_SCHEMA':'patentdb','PHASE3_DISPOSABLE':'1','PYTHONDONTWRITEBYTECODE':'1'}
checks=[]
def command(args,input=None):
    p=subprocess.run(args,input=input,capture_output=True,text=True,env=ENV)
    if p.returncode:raise RuntimeError(f'{Path(args[0]).name}: '+p.stderr+'\n'+p.stdout)
    return p.stdout

def psql(query,db='patentdb'):
    return command(['docker','exec','-i',C,'psql','-X','-U','postgres','-d',db,'-v','ON_ERROR_STOP=1'],query)

def content(db):
    result={}
    for schema in ['patentdb','stage2_meta']:
        # Use unaligned output directly for table names.
        p=subprocess.run(['docker','exec',C,'psql','-X','-At','-U','postgres','-d',db,'-c',"SELECT tablename FROM pg_tables WHERE schemaname='"+schema+"' ORDER BY 1"],capture_output=True,text=True,check=True)
        for table in p.stdout.splitlines():
            query="SELECT count(*),md5(coalesce(string_agg(row_to_json(t)::text,E'\\n' ORDER BY row_to_json(t)::text),'')) FROM "+schema+'.'+table+' t;'
            result[schema+'.'+table]=psql(query,db)
    return result

try:
    command(['docker','run','-d','--name',C,'-e','POSTGRES_PASSWORD='+ENV['PGPASSWORD'],'-e','POSTGRES_DB=patentdb','-p','127.0.0.1::5432',IMAGE])
    for _ in range(45):
        p=subprocess.run(['docker','exec',C,'pg_isready','-U','postgres'],capture_output=True)
        if p.returncode==0:break
        time.sleep(1)
    else:raise RuntimeError('PostgreSQL readiness timeout')
    binding=json.loads(command(['docker','inspect',C]))[0]['NetworkSettings']['Ports']['5432/tcp'][0]
    ENV['PGPORT']=binding['HostPort'];os.environ.update({k:v for k,v in ENV.items() if k.startswith('PG') or k=='DB_SCHEMA'})
    # Checks exact original XML bytes, before any database writes.
    command([sys.executable,'-B',str(B/'02-数据导入/import_samples.py'),'--dry-run']);checks.append('fresh_source_SHA256')
    for path in sorted((B/'01-数据库结构').glob('*.sql')):psql(path.read_text())
    for name in ['import_samples.py','import_enrichment.py']:command([sys.executable,'-B',str(B/'02-数据导入'/name),'--refresh-reviewed'])
    command([sys.executable,'-B',str(B/'02-数据导入/import_batch.py'),'--operations-file',str(B/'05-官方来源/02-IPDPS补充样例/02-DOCDB原文/DOCDB-201724-CreateDelete-PubDate20170609AndBefore-EP-0001.xml')])
    checks.append('fresh_schema_and_source_import')
    original=content('patentdb')
    for name in ['acceptance_failure_test.py','smoke_test.py','fk_violation_test.py','complex_boundary_test.py','frontend_test.py']:
        print('Running',name,flush=True)
        output=command([sys.executable,str(ROOT/'03-测试验收'/name)])
        (OUT/(name+'.txt')).write_text(output)
        checks.append(name)
    output=psql((ROOT/'03-测试验收/performance_test.sql').read_text());(OUT/'performance_current.txt').write_text(output);checks.append('performance_queries')
    if content('patentdb')!=original:raise AssertionError('Tests changed business or audit contents')
    checks.append('all_46_table_contents_unchanged')
    dump=ROOT/'08-数据库交付/patentdb-phase3.dump';dump.parent.mkdir(exist_ok=True)
    with dump.open('wb') as stream:subprocess.run(['docker','exec',C,'pg_dump','-U','postgres','-d','patentdb','-Fc','--no-owner','--no-acl'],stdout=stream,check=True)
    command(['docker','exec',C,'createdb','-U','postgres','patentdb_restore'])
    with dump.open('rb') as stream:subprocess.run(['docker','exec','-i',C,'pg_restore','-U','postgres','-d','patentdb_restore','--no-owner','--no-acl','--exit-on-error'],stdin=stream,check=True,capture_output=True)
    if content('patentdb_restore')!=original:raise AssertionError('Restored 46 table contents differ')
    checks.append('dump_restore_46_table_contents_identical')
    result={'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS','checks':checks,'postgres_version':psql('SELECT version();'),'dump':str(dump.relative_to(ROOT)),'dump_sha256':hashlib.sha256(dump.read_bytes()).hexdigest(),'table_count':46}
    (OUT/'fresh_acceptance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
except Exception as error:
    result={'status':'FAIL','checks_completed':checks,'error':str(error)};(OUT/'fresh_acceptance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(str(error),file=sys.stderr);raise SystemExit(1)
finally:
    subprocess.run(['docker','rm','-f',C],capture_output=True)
