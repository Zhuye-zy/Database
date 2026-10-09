#!/usr/bin/env python3
"""Reproduce public official sample downloads; no login credentials or browser cookies."""
from pathlib import Path
import argparse,json,hashlib,subprocess,datetime
S=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument("--download",action="store_true",help="Download missing archived packages")
 ap.add_argument("--verify-remote",action="store_true",help="Fetch temporary copies and verify against pinned hashes")
 args=ap.parse_args()
 manifest=json.loads((S/"05-官方来源/download_manifest.json").read_text())
 results=[]
 for item in manifest:
  dest=(S/item["path"]).resolve()
  if not dest.is_relative_to(S.resolve()):raise ValueError("Manifest path escaped stage directory")
  exists=dest.exists()
  if exists:
   actual=hashlib.sha256(dest.read_bytes()).hexdigest()
   if actual!=item["sha256"]:raise RuntimeError("Local hash mismatch: "+item["code"])
  if args.verify_remote or (args.download and not exists):
   dest.parent.mkdir(parents=True,exist_ok=True);part=dest.with_name(dest.name+".part")
   cmd=["curl","--fail","--location","--silent","--show-error","--retry","2","--connect-timeout","20","--max-time","180","-A","Mozilla/5.0","-o",str(part)]
   if item.get("url"):cmd.append(item["url"])
   else:cmd+=["-G","https://ipdps.cnipa.gov.cn/public/download","--data-urlencode","rcId="+item["rcId"],"--data-urlencode","fileType="+str(item["fileType"])]
   try:
    subprocess.run(cmd,check=True)
    body=part.read_bytes()
    if not (body.startswith(b"PK") if dest.suffix==".zip" else body.startswith(b"%PDF")):
     raise RuntimeError("Server returned an unexpected file type: "+item["code"])
    if hashlib.sha256(body).hexdigest()!=item["sha256"]:
     raise RuntimeError("Official file differs from reviewed snapshot. Review it separately; existing file was not overwritten: "+item["code"])
    if not exists:part.replace(dest)
   finally:
    if part.exists():part.unlink()
  if not dest.exists():raise FileNotFoundError(str(dest)+" (run with --download)")
  results.append({"code":item["code"],"file":item["path"],"sha256":item["sha256"],"status":"REMOTE_VERIFIED" if args.verify_remote else "LOCAL_VERIFIED","bytes":dest.stat().st_size})
  print(results[-1]["status"],item["code"],dest.stat().st_size)
 out=S/"07-验收结果/官方下载校验.json"
 out.write_text(json.dumps({"time_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"results":results},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
