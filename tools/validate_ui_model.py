#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; UI=ROOT/"analiza/FW2213TK-2026-11-22/data/ui_model"; SCHEMA=UI/"schema"; PIDCSV=ROOT/"analiza/FW2213TK-2026-11-22/data/pid_matrix_655.csv"
PID=re.compile(r"^0x[0-9A-Fa-f]{4}$"); ANY=re.compile(r"(?i)\bPID\b[^0-9A-Fa-f]{0,12}(0x[0-9A-Fa-f]{4})")
def walk(x,p=""):
 yield p,x
 if isinstance(x,dict):
  for k,v in x.items(): yield from walk(v,f"{p}.{k}" if p else k)
 elif isinstance(x,list):
  for i,v in enumerate(x): yield from walk(v,f"{p}[{i}]")
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("root",nargs="?",default=str(UI)); ap.add_argument("--json",action="store_true"); a=ap.parse_args(); root=Path(a.root)
 known=set()
 if PIDCSV.exists():
  with PIDCSV.open(encoding="utf-8-sig",newline="") as f:
   for r in csv.reader(f):
    if r and PID.match(r[0].strip()): known.add(r[0].strip().upper())
 errors=[]; warnings=[]; records=[]
 for p in sorted(root.rglob("*.json")):
  if p.name=="INDEX.json": continue
  rel=p.relative_to(root).as_posix(); sch=SCHEMA/(p.stem+".schema.json")
  if not sch.exists(): warnings.append({"file":rel,"problem":"missing schema"})
  try:d=json.loads(p.read_text(encoding="utf-8"))
  except Exception as e: errors.append({"file":rel,"problem":"invalid JSON: "+str(e)}); continue
  if not isinstance(d,dict): errors.append({"file":rel,"problem":"root must be object"}); continue
  if not isinstance(d.get("schema_version"),str) or not d["schema_version"]: errors.append({"file":rel,"field":"schema_version","problem":"missing/empty"})
  ev=d.get("evidence")
  if not isinstance(ev,str) or not ev.strip(): errors.append({"file":rel,"field":"evidence","problem":"missing/empty"})
  elif not re.match(r"^(MEASURED|STRONG|INFERENCE|OPEN|REJECTED)\b",ev): errors.append({"file":rel,"field":"evidence","problem":"invalid label"})
  refs=set()
  for path,v in walk(d):
   if isinstance(v,str): refs.update(x.upper() for x in ANY.findall(v))
   if isinstance(v,dict):
    for k,x in v.items():
     if k.lower() in {"pid","pid_ref","pid_reference"} and isinstance(x,str):
      if not PID.match(x): errors.append({"file":rel,"field":path+"."+k,"problem":"invalid PID format"})
      else: refs.add(x.upper())
  for x in sorted(refs):
   if x not in known: errors.append({"file":rel,"problem":"PID not found in pid_matrix_655.csv","value":x})
  records.append({"file":rel,"schema":str(sch.relative_to(root)) if sch.exists() else None,"pid_refs":sorted(refs)})
 out={"ok":not errors,"errors":errors,"warnings":warnings,"summary":{"files":len(records),"errors":len(errors),"warnings":len(warnings),"pid_matrix_entries":len(known)},"files":records}
 if a.json: print(json.dumps(out,ensure_ascii=False,indent=2))
 else:
  print("ui_model validation: "+("PASS" if not errors else "FAIL")); print("files=%d errors=%d warnings=%d pid_matrix=%d"%(len(records),len(errors),len(warnings),len(known)))
  for x in errors: print("ERROR",x)
  for x in warnings: print("WARN",x)
 return 0 if not errors else 1
if __name__=="__main__": raise SystemExit(main())
