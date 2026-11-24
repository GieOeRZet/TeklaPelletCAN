#!/usr/bin/env python3
"""PASS 107: export and validate resolver_t1 as a complete source-grounded table."""
import csv,sys
src=sys.argv[1]; out=sys.argv[2]
rows=list(csv.DictReader(open(src,encoding="utf-8")))
assert len(rows)==49
with open(out,"w",newline="",encoding="utf-8") as f:
 w=csv.writer(f); w.writerow(["resolver_addr","idx","ui_key","pid","rule","in_runtime","name"])
 for r in rows:
  addr=hex(0x08010000+int(r["raw_off"],16))
  w.writerow([addr,int(r["idx"]),r["ui_key"],r["value"],r["rule"],r["in_runtime"],r["name"]])
