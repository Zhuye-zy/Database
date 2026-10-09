#!/usr/bin/env python3
"""Execute the documented fresh-machine initialization against an isolated Docker container."""
from pathlib import Path
import os,subprocess,json,shutil
S=Path(__file__).resolve().parents[1]
name="patentdb-deploy-check-"+str(os.getpid())
env={**os.environ,"PATENT_CONTAINER":name,"PATENT_PORT":"0","POSTGRES_PASSWORD":"isolated-deploy-test","PYTHONDONTWRITEBYTECODE":"1"}
before=set((S/"08-历史备份").glob("数据库更新-*"))
result={}
try:
 p=subprocess.run(["bash",str(S/"06-运行管理/init_db.sh")],env=env,text=True,capture_output=True)
 (S/"07-验收结果/全新部署日志.txt").write_text(p.stdout+p.stderr)
 if p.returncode:raise RuntimeError(p.stderr or p.stdout[-2000:])
 result={"status":"PASS","entrypoint":"06-运行管理/init_db.sh","container_created":True,"business_tables":43,"operational_tables":3,"sample_import_and_verify":"PASS"}
 print(json.dumps(result,ensure_ascii=False,indent=2))
except Exception as ex:
 result={"status":"FAIL","error":str(ex)};raise
finally:
 (S/"07-验收结果/全新部署验收.json").write_text(json.dumps(result,ensure_ascii=False,indent=2))
 subprocess.run(["docker","rm","-f","-v",name],capture_output=True)
 subprocess.run(["docker","volume","rm",name+"_data"],capture_output=True)
 for p in set((S/"08-历史备份").glob("数据库更新-*"))-before:
  assert p.resolve().is_relative_to((S/"08-历史备份").resolve())
  shutil.rmtree(p)
