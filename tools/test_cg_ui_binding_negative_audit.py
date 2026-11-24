#!/usr/bin/env python3
"""Regression test for PASS 114 negative UI binding audit."""
from pathlib import Path
import csv

P = Path(__file__).resolve().parents[1] / "analiza_archiwum/FW2213TK-2026-11-22/data/cg_ui_binding_negative_audit.csv"

def main():
    rows = list(csv.DictReader(P.open(encoding="utf-8", newline="")))
    assert len(rows) == 5
    by = {(r["ui_key"], r["pid"]): r for r in rows}
    assert by[("0x00F3","0x2114")]["status"] == "PRESENTER_PAIR_ABSENT"
    assert by[("0x00F4","0x2115")]["status"] == "PRESENTER_PAIR_PRESENT"
    assert by[("0x00F5","0x2280")]["status"] == "PRESENTER_PAIR_PRESENT"
    assert by[("0x00B0","0x22A1")]["status"] == "PRESENTER_PAIR_PRESENT"
    assert by[("0x00CD","0x2301")]["status"] == "PRESENTER_PAIR_PRESENT"
    print("PASS 114 regression: target pair presence/absence is stable")
if __name__ == "__main__":
    main()
