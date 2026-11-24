#!/usr/bin/env python3
import csv
p="analiza_archiwum/FW2213TK-2026-11-22/data/cg_presenter_setter_offsets_full.csv"; r=list(csv.DictReader(open(p,encoding="utf-8")))
assert len(r)==137
assert any(x["setter"]=="0x803d440" and "0x585c" in x["widget_offsets"].lower() for x in r)
print("PASS 102 test: OK",len(r))
