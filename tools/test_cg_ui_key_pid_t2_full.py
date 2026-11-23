#!/usr/bin/env python3
import csv
r=list(csv.DictReader(open("analiza/FW2213TK-2026-11-22/data/cg_ui_key_pid_t2_full.csv",encoding="utf-8")))
assert len(r)==372
assert any(x["ui_key"]=="0x000E" and x["pid"]=="0x2004" for x in r)
assert any(x["ui_key"]=="0x0121" and x["pid"]=="0x370A" for x in r)
print("PASS 101 test: OK",len(r))
