#!/usr/bin/env python3
"""PASS 102: aggregate all presenter_map widget offsets by setter."""
import csv,pathlib
src=pathlib.Path(__file__).resolve().parents[1]/"analiza/FW2213TK-2026-11-22/data/presenter_map.csv"; out=pathlib.Path(__file__).resolve().parents[1]/"analiza/FW2213TK-2026-11-22/data/cg_presenter_setter_offsets_full.csv"
d={}
with src.open(encoding="utf-8-sig") as f:
 for r in csv.DictReader(f):
  s=r.get("setter","").strip()
  if not s: continue
  d.setdefault(s,{"offs":set(),"rows":0}); d[s]["rows"]+=1; d[s]["offs"].update(x for x in r.get("widget_offsets","").split("|") if x)
with out.open("w",newline="") as f:
 w=csv.writer(f); w.writerow(["setter","widget_offsets","source_rows","confidence"])
 for s,v in sorted(d.items()): w.writerow([s,"|".join(sorted(v["offs"])),v["rows"],"PRESENTER_MAP_HARD"])
print(out,len(d))
