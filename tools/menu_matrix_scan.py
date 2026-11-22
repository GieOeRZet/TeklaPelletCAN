#!/usr/bin/env python3
"""Deterministic raw-BIN MenuTree matrix/anchor scanner.

Purpose:
- parse the 21 x 6-byte MenuTree table at PROJECT 0x08042348;
- emit RAW/PROJECT/RUNTIME address forms;
- verify direct literal anchors for the runtime class/access tables and
  known row-selection/constructor pointers.

This is an evidence scanner, not a semantic classifier.
"""
from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path

PROJECT_BASE = 0x08000000
RUNTIME_BASE = 0x08010000
TABLE_PROJECT = 0x08042348

ANCHORS = {
    "runtime_class_table": 0x20005EF0,
    "access_update_table": 0x20005F08,
    "row_ctor_thumb": 0x0805BB43,
    "row_select_thumb": 0x0808EB01,
    "row_select_sibling_thumb": 0x0808EB37,
}

def find_le32(data: bytes, value: int) -> list[int]:
    needle = struct.pack("<I", value & 0xFFFFFFFF)
    out, pos = [], 0
    while True:
        pos = data.find(needle, pos)
        if pos < 0:
            return out
        out.append(pos)
        pos += 1

def raw_to_project(raw: int) -> int:
    return raw + PROJECT_BASE

def project_to_runtime(project: int) -> int:
    return project + (RUNTIME_BASE - PROJECT_BASE)

def parse_table(data: bytes, raw: int, count: int = 21) -> list[dict]:
    rows = []
    for i in range(count):
        off = raw + i * 6
        selector, typed_text, bitmap = struct.unpack_from("<HHH", data, off)
        rows.append({
            "index": i,
            "raw": hex(off),
            "project": hex(raw_to_project(off)),
            "selector": selector,
            "typed_text": typed_text,
            "bitmap": bitmap,
        })
    return rows

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("bin")
    ap.add_argument("--table-project", type=lambda x: int(x, 0), default=TABLE_PROJECT)
    ap.add_argument("--count", type=int, default=21)
    args = ap.parse_args()

    data = Path(args.bin).read_bytes()
    table_raw = args.table_project - PROJECT_BASE
    result = {
        "sha256": hashlib.sha256(data).hexdigest(),
        "size": len(data),
        "address_model": {
            "project": "RAW + 0x08000000",
            "runtime": "PROJECT + 0x10000",
        },
        "table": {
            "raw": hex(table_raw),
            "project": hex(args.table_project),
            "count": args.count,
            "stride": 6,
            "rows": parse_table(data, table_raw, args.count),
        },
        "anchors": {},
    }

    for name, value in ANCHORS.items():
        hits = find_le32(data, value)
        result["anchors"][name] = {
            "value": hex(value),
            "raw_hits": [hex(x) for x in hits],
            "count": len(hits),
        }

    print(json.dumps(result, indent=2, sort_keys=False))

if __name__ == "__main__":
    main()
