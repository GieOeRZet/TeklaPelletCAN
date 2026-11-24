#!/usr/bin/env python3
import csv, pathlib
p=pathlib.Path(__file__).resolve().parents[1]/"analiza/FW2213TK-2026-11-22/data/cg_menu_dispatch_closure.csv"
rows=list(csv.DictReader(p.open()))
assert len(rows)==10
expected={11:(11,"0x080384B0"),12:(13,"0x0803850C"),13:(17,"0x0803850C"),14:(15,"0x08042318"),15:(12,"0x080373BA/0x080373E6"),16:(14,"return"),17:(18,"0x08038574"),18:(16,"0x0803856C"),19:(19,"0x08038638"),20:(20,"0x080382EE")}
for r in rows:
    k=int(r["row"]); assert (int(r["class"]),r["first_level_handler"])==expected[k]
print("PASS 96 test: OK")
