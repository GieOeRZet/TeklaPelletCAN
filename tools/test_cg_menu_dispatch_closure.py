#!/usr/bin/env python3
import sys as _s,pathlib as _p; _s.path.insert(0,str(_p.Path(__file__).resolve().parent)); import paths as _paths
import csv, pathlib
p=_paths.DATA/"cg_menu_dispatch_closure.csv"
rows=list(csv.DictReader(p.open()))
assert len(rows)==10
expected={11:(11,"0x080384B0"),12:(13,"0x0803850C"),13:(17,"0x0803850C"),14:(15,"0x08042318"),15:(12,"0x080373BA/0x080373E6"),16:(14,"return"),17:(18,"0x08038574"),18:(16,"0x0803856C"),19:(19,"0x08038638"),20:(20,"0x080382EE")}
for r in rows:
    k=int(r["row"]); assert (int(r["class"]),r["first_level_handler"])==expected[k]
print("PASS 96 test: OK")
