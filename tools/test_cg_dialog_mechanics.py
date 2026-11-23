#!/usr/bin/env python3
import csv
r=list(csv.DictReader(open("analiza/FW2213TK-2026-11-22/data/cg_dialog_mechanics.csv"))); assert len(r)==4
assert {x["dialog"] for x in r}=={"PIN","Fuel","Time","Value edit"}
print("PASS 105 test: OK")
