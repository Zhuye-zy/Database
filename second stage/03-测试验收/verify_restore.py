#!/usr/bin/env python3
"""Restore the distributable pg_dump into an isolated container and compare business contents."""
from pathlib import Path
import os,subprocess,time,json,hashlib
S=Path(__file__).resolve().parents[1]
dump=S/"09-GitHub交付/数据库备份/patentdb-sample.dump"
target="patentdb-restore-check-"+str(os.getpid())
source=os.environ.get("PATENT_CONTAINER","patentdb")
image=os.environ.get("POSTGRES_IMAGE","docker.m.daocloud.io/library/postgres:16")
def cmd(args,input=None,check=True):
 p=subprocess.run(args,input=input,capture_output=True)
 if check and p.returncode:raise RuntimeError(p.stderr.decode(errors="replace"))
 return p
def sql(c,text):
 return cmd(["docker","exec","-i",c,"psql","-X","-U","postgres","-d","patentdb","-At","-v","ON_ERROR_STOP=1"],text.encode()).stdout.decode().strip()
def fingerprints(c):
 names=sql(c,"SELECT tablename FROM pg_tables WHERE schemaname IN ('patentdb','stage2_meta') ORDER BY schemaname,tablename;")
 objects=sql(c,"SELECT schemaname||'.'||tablename FROM pg_tables WHERE schemaname IN ('patentdb','stage2_meta') ORDER BY 1;").splitlines()
 return dict(line.split("|") for line in sql(c," UNION ALL ".join("SELECT '"+n+"',md5(coalesce(string_agg(row_to_json(t)::text,E'\\n' ORDER BY row_to_json(t)::text),'')) FROM "+n+" t" for n in objects)+";").splitlines())
result={}
try:
 cmd(["docker","run","-d","--name",target,"-e","POSTGRES_PASSWORD=restore-disposable","-e","POSTGRES_DB=patentdb",image])
 for _ in range(45):
  if cmd(["docker","exec",target,"pg_isready","-U","postgres"],check=False).returncode==0:break
  time.sleep(1)
 else:raise RuntimeError("Readiness timeout")
 cmd(["docker","exec","-i",target,"pg_restore","-U","postgres","-d","patentdb","--no-owner","--no-acl","--exit-on-error"],dump.read_bytes())
 a,b=fingerprints(source),fingerprints(target)
 if a!=b:raise RuntimeError("Restored table contents differ: "+str([k for k in a if a[k]!=b.get(k)]))
 result={"status":"PASS","business_tables":43,"operational_tables":3,"identical_table_contents":len(a),"source":source,"dump":str(dump.relative_to(S)),"dump_sha256":hashlib.sha256(dump.read_bytes()).hexdigest()}
 print(json.dumps(result,ensure_ascii=False,indent=2))
except Exception as ex:
 result={"status":"FAIL","error":str(ex)};raise
finally:
 (S/"07-验收结果/备份恢复验收.json").write_text(json.dumps(result,ensure_ascii=False,indent=2))
 cmd(["docker","rm","-f","-v",target],check=False)
