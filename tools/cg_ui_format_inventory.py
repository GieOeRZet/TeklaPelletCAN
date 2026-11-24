#!/usr/bin/env python3
import sys as _s,pathlib as _p; _s.path.insert(0,str(_p.Path(__file__).resolve().parent)); import paths as _paths
"""PASS 104: aggregate presenter format evidence by PID."""
import csv,pathlib
src=_paths.DATA/"presenter_map.csv"; out=_paths.DATA/"cg_ui_format_inventory.csv"; d={}
with src.open(encoding="utf-8-sig") as f:
 for r in csv.DictReader(f):
  if not r.get("pid"): continue
  k=(r["pid"],r.get("formats",""),r.get("div10","")); d.setdefault(k,{"n":0,"w":set()}); d[k]["n"]+=1; d[k]["w"].update(x for x in r.get("widget_offsets","").split("|") if x)
with out.open("w",newline="") as f:
 w=csv.writer(f); w.writerow(["pid","formats","div10","source_rows","widget_offsets"])
 for (pid,fmt,d10),v in sorted(d.items()): w.writerow([pid,fmt,d10,v["n"],"|".join(sorted(v["w"]))])
print(out,len(d))
