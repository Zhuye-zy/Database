"""Shared source parsing and structured audit output. Python standard library only."""
from pathlib import Path
import os, json, hashlib, datetime, re
import xml.etree.ElementTree as ET
STAGE=Path(__file__).resolve().parents[1]
def logical_roots(data):
    """Handle single XML, concatenated XML declarations and DOCDB wrappers."""
    parts=re.split(br"(?=<\?xml\s)", data)
    roots=[]
    for part in parts:
        if not part.strip(): continue
        root=ET.fromstring(part)
        if root.tag.rsplit("}",1)[-1]=="exchange-documents":
            roots.extend(n for n in root if n.tag.rsplit("}",1)[-1]=="exchange-document")
        else: roots.append(root)
    return roots
def write_log(name, payload):
    folder=Path(os.environ.get("PATENT_LOG_DIR",str(STAGE/"07-验收结果/导入日志")))
    if not folder.resolve().is_relative_to(STAGE.resolve()):
        raise ValueError("All logs must remain under second stage")
    folder.mkdir(parents=True,exist_ok=True)
    now=datetime.datetime.now(datetime.timezone.utc)
    payload={"timestamp_utc":now.isoformat(),"event":name,**payload}
    target=folder/(now.strftime("%Y%m%dT%H%M%S.%fZ")+"-"+name+".json")
    target.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
def assert_source_snapshot(folder):
    expected=json.loads((Path(__file__).parent/"source_snapshot.json").read_text())
    actual={str(p.relative_to(folder)):hashlib.sha256(p.read_bytes()).hexdigest()
      for p in folder.rglob("*") if p.is_file() and p.suffix.lower()==".xml"}
    if actual!=expected:
        err={"dataset":"sample-snapshot","source_file":str(folder),"logical_document":None,
             "xml_path":"/","error_type":"SourceSnapshotChanged",
             "message":"This importer uses fixed sample IDs. Review mappings and IDs before adding/replacing sources."}
        write_log("source-validation",{"errors":[err]})
        raise RuntimeError(err["message"])
