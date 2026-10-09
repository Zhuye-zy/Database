#!/usr/bin/env python3
"""Enumerate reviewed logical source documents and explicitly retain pending records."""
from pathlib import Path
import sys,json,hashlib,xml.etree.ElementTree as ET
S=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(S/"02-数据导入"))
from import_support import logical_roots
rows=[]
def record(path,node,index,status,reason=""):
 rows.append({"source_file":str(path.relative_to(S)),"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
 "logical_document":index,"xml_root":node.tag.rsplit("}",1)[-1],"country":node.get("country"),
 "doc_number":node.get("doc-number"),"kind":node.get("kind"),"source_status":node.get("status"),
 "disposition":status,"reason":reason})
for p in sorted((S/"05-官方来源/01-四类基础样例").rglob("*")):
 if p.is_file() and p.suffix.lower()==".xml":
  for i,node in enumerate(logical_roots(p.read_bytes()),1):record(p,node,i,"基础样例已映射")
for p in (S/"05-官方来源/02-IPDPS补充样例/02-DOCDB原文").glob("*.xml"):
 for i,node in enumerate(logical_roots(p.read_bytes()),1):
  if "CreateDelete" in p.name:
   record(p,node,i,"撤回通知已分类","EPO ST36第36页：CV/DV为void/withdrawn通知；审计记录见stage2_meta.source_document")
  else:record(p,node,i,"重复归档","与基础DOCDB Amend同一来源内容，不重复入库")
for p in (S/"05-官方来源/02-IPDPS补充样例/03-法律状态原文").glob("*.xml"):
 raw=p.read_text()
 if not raw.rstrip().endswith("</legal-status-documents>"):raw+="\n</legal-status-documents>"
 for i,node in enumerate(ET.fromstring(raw),1):record(p,node,i,"法律样例已映射","外层缺失闭合标签仅在内存修复")
target=S/"07-验收结果/源文献处理清单.json"
target.write_text(json.dumps(rows,ensure_ascii=False,indent=2))
print('源文献处理统计:',dict(__import__('collections').Counter(r['disposition'] for r in rows)))
