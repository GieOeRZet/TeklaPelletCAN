#!/usr/bin/env python3
import csv
r=list(csv.DictReader(open("analiza_archiwum/FW2213TK-2026-11-22/data/cg_level3_wrappers_closed.csv"))); assert len(r)==4
assert all(x["gate"]=="model+0x158>=3" for x in r)
assert all(x["child_offset"]=="0x23C" and x["init_offset"]=="0x210" for x in r)
print("PASS 106 test: OK")
