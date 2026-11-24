#!/usr/bin/env python3
import csv
p="analiza_archiwum/FW2213TK-2026-11-22/data/cg_kociol_visual_binding_matrix.csv"; r=list(csv.DictReader(open(p)))
assert len(r)==9
by={x["pid"]:x for x in r}
assert by["0x370A"]["widget"]=="0x20016894"
assert by["0x22A1"]["widget"].startswith("0x20016274")
assert "animation" in by["0x2277"]["effect"]
print("PASS 103 test: OK")
