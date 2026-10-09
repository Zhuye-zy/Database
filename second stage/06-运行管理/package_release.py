#!/usr/bin/env python3
"""Build a reviewable GitHub handover archive. Does not commit or push."""
from pathlib import Path
import subprocess,json,hashlib,zipfile,datetime,argparse,sys
S=Path(__file__).resolve().parents[1];out=S/"09-GitHub交付";out.mkdir(exist_ok=True)
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument("--reuse-backup",action="store_true",help="Package the already restored and verified snapshot")
args=ap.parse_args()
if not args.reuse_backup:
 subprocess.run(["bash",str(S/"06-运行管理/backup_db.sh")],check=True)
 subprocess.run([sys.executable,"-B",str(S/"03-测试验收/verify_restore.py")],check=True)
else:
 dump=out/"数据库备份/patentdb-sample.dump"
 evidence=json.loads((S/"07-验收结果/备份恢复验收.json").read_text())
 if evidence.get("status")!="PASS" or evidence.get("dump_sha256")!=hashlib.sha256(dump.read_bytes()).hexdigest():
  raise RuntimeError("Backup must first pass verify_restore.py")
include=["README.md",".gitignore",".gitattributes","01-数据库结构","02-数据导入","03-测试验收","04-报告与基线","05-官方来源","06-运行管理","07-验收结果","09-GitHub交付/数据库备份","09-GitHub交付/README.md"]
files=[]
for name in include:
 p=S/name
 for f in ([p] if p.is_file() else sorted(p.rglob("*"))):
  if not f.is_file() or f.is_symlink():continue
  rel=f.relative_to(S)
  if any(x in rel.parts for x in ("__pycache__","导入日志","批次测试输入")):continue
  if f.suffix in (".pyc",".part") or f.name.startswith(".env"):continue
  if f.stat().st_size>100*1024*1024:raise RuntimeError("Single file exceeds GitHub 100MiB limit: "+str(rel))
  files.append(f)
manifest=[{"path":str(p.relative_to(S)),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
manifest_path=out/"上传文件清单.json";manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
target=out/"patentdb-stage2-github.zip"
with zipfile.ZipFile(target,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,"second-stage/"+str(p.relative_to(S)))
 z.write(manifest_path,"second-stage/09-GitHub交付/上传文件清单.json")
with zipfile.ZipFile(target) as z:
 if z.testzip():raise RuntimeError("ZIP checksum verification failed")
summary={"created_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"archive":target.name,"files":len(files)+1,
 "bytes":target.stat().st_size,"largest_input_file_bytes":max(x["bytes"] for x in manifest),
 "sha256":hashlib.sha256(target.read_bytes()).hexdigest(),"zip_crc_check":"PASS","uploaded_to_GitHub":False}
(out/"打包结果.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2))
print(json.dumps(summary,ensure_ascii=False,indent=2))
