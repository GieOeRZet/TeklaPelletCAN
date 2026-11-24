#!/usr/bin/env python3
import csv
r=list(csv.DictReader(open("analiza_archiwum/FW2213TK-2026-11-22/data/cg_ui_format_inventory.csv")))
assert len(r)>20
assert any(x["pid"]=="0x2001" and "%d.%d" in x["formats"] and x["div10"]=="1" for x in r)
print("PASS 104 test: OK",len(r))
