#!/usr/bin/env python3
"""Regression checks for MENU_TREE_COMPLETE PASS 111.

This test validates the source-grounded 21-row matrix generated for PASS 111.
It deliberately does not invent semantic mappings for OPEN fields.
"""

from pathlib import Path
import csv

CSV = Path(__file__).resolve().parents[1] / "analiza_archiwum/FW2213TK-2026-11-22/data/cg_menu_tree_complete.csv"

EXPECTED_ROWS = 21
EXPECTED_HANDLERS = {
    0: "0x08038008", 1: "0x08038130", 2: "0x08038130",
    3: "0x08038130", 4: "0x08038130", 5: "0x080381E4",
    6: "0x0803809C", 7: "0x080383B0", 8: "0x08038278",
    9: "0x080382CA", 10: "0x080382A6", 11: "0x080384B0",
    12: "0x0803850C", 13: "0x08038568", 14: "0x08042318",
    15: "0x080373BA/0x080373E6", 16: "return",
    17: "0x08038574", 18: "0x0803856C", 19: "0x08038638",
    20: "0x080382EE",
}

def main():
    assert CSV.exists(), CSV
    rows = list(csv.DictReader(CSV.open(encoding="utf-8", newline="")))
    assert len(rows) == EXPECTED_ROWS, len(rows)
    assert [int(r["row"]) for r in rows] == list(range(EXPECTED_ROWS))
    assert len({r["row"] for r in rows}) == EXPECTED_ROWS

    for r in rows:
        idx = int(r["row"])
        assert r["first_level_handler"] == EXPECTED_HANDLERS[idx], (idx, r["first_level_handler"])
        assert r["selector"] != ""
        assert r["typed_text_id"] != ""
        assert r["bitmap_id"] != ""
        assert r["root_label"] != ""
        assert r["evidence"] != ""

    # Explicit evidence-discipline checks.
    assert rows[15]["observed_runtime_class"] == "12"
    assert rows[15]["pid_can_status"] == "hard"
    assert rows[16]["destination_status"] == "hard"
    assert rows[12]["pid_can_status"] == "open"

    print("PASS 111 MENU_TREE_COMPLETE regression: 21 rows / handlers / evidence discipline OK")

if __name__ == "__main__":
    main()
