#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from datetime import datetime,timezone
from pathlib import Path
def count(d):
 if isinstance(d,list): return len(d)
 if isinstance(d,dict):
  for k in ("rows","codes","lists","nodes","edges","dialogs","modules","items","records"):
   if isinstance(d.get(k),list): return len(d[k])
  return len(d)
 return 1
def evidence_paths(d):
 out=set()
 def w(x):
  if isinstance(x,str) and (".png" in x.lower() or "RUN_SUMMARY" in x.upper()): out.add(x)
  elif isinstance(x,dict):
   for v in x.values(): w(v)
  elif isinstance(x,list):
   for v in x: w(v)
 w(d); return sorted(out)
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("root",nargs="?",default="analiza/FW2213TK-2026-11-22/data/ui_model"); ap.add_argument("--output"); a=ap.parse_args(); root=Path(a.root); out=Path(a.output) if a.output else root/"INDEX.json"; rows=[]
 for p in sorted(root.rglob("*.json")):
  if p.name=="INDEX.json": continue
  rel=p.relative_to(root).as_posix()
  try:d=json.loads(p.read_text(encoding="utf-8"))
  except Exception as e: rows.append({"file":rel,"error":str(e)}); continue
  sp=root/"schema"/(p.stem+".schema.json")
  rows.append({"file":rel,"schema":sp.relative_to(root).as_posix() if sp.exists() else None,"schema_version":d.get("schema_version") if isinstance(d,dict) else None,"records":count(d),"date":datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),"evidence_paths":evidence_paths(d)})
 idx={"schema_version":"1.0.0","generated_at":datetime.now(timezone.utc).isoformat(),"root":"analiza/FW2213TK-2026-11-22/data/ui_model","files":rows}; out.write_text(json.dumps(idx,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print("wrote",out,len(rows))
if __name__=="__main__": main()
