#!/usr/bin/env python3
"""Build/validate the MenuTree 21-node closure from existing project CSVs.

The script is intentionally conservative: it only joins evidence already
present in menu_rows_21.csv, menu_click_effects_21.csv and
cg_menu_dispatch_closure.csv. It never guesses missing semantic fields.
"""

from __future__ import annotations
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "analiza/FW2213TK-2026-11-22/data"

def read_csv(name):
    with (DATA / name).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def main():
    menu = read_csv("menu_rows_21.csv")
    clicks = {int(r["row"]): r for r in read_csv("menu_click_effects_21.csv")}
    dispatch = {int(r["row"]): r for r in read_csv("cg_menu_dispatch_closure.csv")}

    assert len(menu) == 21
    assert set(map(int, [r["row"] for r in menu])) == set(range(21))

    for r in menu:
        i = int(r["row"])
        if i in clicks:
            r["click_effect"] = clicks[i]["changed"] or clicks[i]["error"]
        if i in dispatch:
            r["semantic_dispatch"] = dispatch[i]["semantic"]
            r["handler"] = dispatch[i]["first_level_handler"]

    out = DATA / "cg_menu_tree_complete.csv"
    fields = list(menu[0].keys()) + ["click_effect", "semantic_dispatch", "handler"]
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(menu)

    print(f"wrote {out} ({len(menu)} rows)")

if __name__ == "__main__":
    main()
