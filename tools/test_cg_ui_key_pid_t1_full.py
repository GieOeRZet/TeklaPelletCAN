#!/usr/bin/env python3
import csv,sys
p=sys.argv[1] if len(sys.argv)>1 else "analiza_archiwum/FW2213TK-2026-11-22/data/cg_ui_key_pid_t1_full.csv"
rows=list(csv.DictReader(open(p,encoding="utf-8")))
assert len(rows)==49, len(rows)
assert [int(r["idx"]) for r in rows]==list(range(49))
assert len({r["ui_key"] for r in rows})==49
m={r["ui_key"]:r["pid"] for r in rows}
assert m["0x00B0"]=="0x22A1"
assert m["0x00CB"]=="0x22F5"
assert m["0x00CD"]=="0x2301"
assert m["0x00D6"]=="0x2329"
print("PASS: T1 49 rows and representative mappings verified")
