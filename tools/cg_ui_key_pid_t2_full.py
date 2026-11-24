#!/usr/bin/env python3
import sys as _s,pathlib as _p; _s.path.insert(0,str(_p.Path(__file__).resolve().parent)); import paths as _paths
import csv,pathlib
src=_paths.DATA/"resolver_t2.csv"; out=_paths.DATA/"cg_ui_key_pid_t2_full.csv"
with src.open(encoding="utf-8-sig") as f, out.open("w",newline="",encoding="utf-8") as g:
 r=csv.reader(f); w=csv.writer(g); next(r,None); w.writerow(["resolver_addr","index","ui_key","pid","kind","valid","name"])
 for row in r:
  if len(row)>=6 and row[2].startswith("0x") and row[3].startswith("0x"): w.writerow([row[0],row[1],row[2],row[3],row[4],row[5],",".join(row[6:])])
print(out)
