#!/usr/bin/env python3
import csv,pathlib
src=pathlib.Path(__file__).resolve().parents[1]/"analiza/FW2213TK-2026-11-22/data/resolver_t2.csv"; out=pathlib.Path(__file__).resolve().parents[1]/"analiza/FW2213TK-2026-11-22/data/cg_ui_key_pid_t2_full.csv"
with src.open(encoding="utf-8-sig") as f, out.open("w",newline="",encoding="utf-8") as g:
 r=csv.reader(f); w=csv.writer(g); next(r,None); w.writerow(["resolver_addr","index","ui_key","pid","kind","valid","name"])
 for row in r:
  if len(row)>=6 and row[2].startswith("0x") and row[3].startswith("0x"): w.writerow([row[0],row[1],row[2],row[3],row[4],row[5],",".join(row[6:])])
print(out)
