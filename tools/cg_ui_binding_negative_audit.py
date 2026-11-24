#!/usr/bin/env python3
"""PASS 114: conservative static UI binding audit.

Builds two reverse indexes from source-grounded presenter_map.csv:
1) view/widget offset -> presenter rows/PIDs
2) setter -> offsets

It also checks whether specific target UI keys/PIDs are absent from the
presenter map. Absence is a negative result, not an inferred mapping.

No firmware execution and no semantic assignment from geometry.
"""

from __future__ import annotations
import sys as _s,pathlib as _p; _s.path.insert(0,str(_p.Path(__file__).resolve().parent)); import paths as _paths
import csv
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
SRC = _paths.DATA / "presenter_map.csv"
OUT = _paths.DATA / "cg_ui_binding_negative_audit.csv"

TARGETS = [
    ("0x00F3", "0x2114", "Buffer top set temperature"),
    ("0x00F4", "0x2115", "Buffer bottom set temperature"),
    ("0x00F5", "0x2280", "Buffer top set temperature (separate PID)"),
    ("0x00B0", "0x22A1", "Room temp sensor type"),
    ("0x00CD", "0x2301", "CH thermostat state"),
]

def norm(s):
    return (s or "").strip().upper()

def main():
    with SRC.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    out = []
    for key, pid, name in TARGETS:
        matches = [
            r for r in rows
            if norm(r.get("ui_key")) == key or norm(r.get("pid")) == pid
        ]
        exact = [
            r for r in matches
            if norm(r.get("ui_key")) == key and norm(r.get("pid")) == pid
        ]
        out.append({
            "ui_key": key,
            "pid": pid,
            "name": name,
            "source_rows": len(matches),
            "exact_pair_rows": len(exact),
            "setters": "|".join(sorted({norm(r.get("setter")) for r in exact if r.get("setter")})),
            "widget_offsets": "|".join(sorted({
                x for r in exact for x in (r.get("widget_offsets") or "").split("|") if x
            })),
            "status": "PRESENTER_PAIR_PRESENT" if exact else "PRESENTER_PAIR_ABSENT",
        })

    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)

    print(f"wrote {OUT} ({len(out)} target pairs)")

if __name__ == "__main__":
    main()
