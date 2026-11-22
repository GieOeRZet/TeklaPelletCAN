#!/usr/bin/env python3
"""Deterministic Thumb vtable/object scanner.

Finds executable-looking function-pointer tables, vptr stores, and object-field
references. It is deliberately evidence-first: candidates are reported, not
silently promoted to proven vtables.
"""
from __future__ import annotations
import argparse, json, struct
from pathlib import Path

BASE = 0x08010000
FLASH_LO = 0x08010000
FLASH_HI = 0x08100000

def u32(data, off):
    if off < 0 or off + 4 > len(data):
        return None
    return struct.unpack_from("<I", data, off)[0]

def is_code_ptr(v):
    return FLASH_LO <= (v & ~1) < FLASH_HI

def scan(path, targets=(), min_slots=2, max_slots=32):
    data = Path(path).read_bytes()
    targets = set(targets)
    vtables = []
    for off in range(0, len(data) - 4 * min_slots + 1, 4):
        vals = [u32(data, off + 4*i) for i in range(min_slots)]
        if not all(is_code_ptr(v) for v in vals):
            continue
        # Extend while entries remain Thumb code pointers.
        n = min_slots
        while n < max_slots and is_code_ptr(u32(data, off + 4*n)):
            n += 1
        # Avoid reporting every interior window of a long table.
        prev = u32(data, off - 4) if off >= 4 else None
        if is_code_ptr(prev):
            continue
        entries = [u32(data, off + 4*i) for i in range(n)]
        vtables.append({
            "raw": off, "true": BASE + off, "slots": n,
            "entries": [{"slot": i, "target_true": v, "target_project": v - 0x10000}
                        for i, v in enumerate(entries)]
        })

    stores = []
    # Byte-level search for little-endian candidate vptr constants.
    for vt in vtables:
        needle = struct.pack("<I", vt["true"])
        pos = 0
        while True:
            pos = data.find(needle, pos)
            if pos < 0: break
            stores.append({
                "kind": "VTPTR_LITERAL_OCCURRENCE",
                "vtable_true": vt["true"], "at_raw": pos, "at_true": BASE + pos
            })
            pos += 1

    target_refs = []
    for t in targets:
        needle = struct.pack("<I", t)
        pos = 0
        while True:
            pos = data.find(needle, pos)
            if pos < 0: break
            target_refs.append({"target_true": t, "at_raw": pos, "at_true": BASE + pos})
            pos += 1

    return {"input": str(path), "size": len(data), "vtable_candidates": vtables,
            "vptr_literal_occurrences": stores, "target_refs": target_refs}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("bin")
    p.add_argument("--target", action="append", default=[])
    p.add_argument("--min-slots", type=int, default=2)
    p.add_argument("--max-slots", type=int, default=32)
    p.add_argument("--out", default="vtable_scan")
    a = p.parse_args()
    r = scan(a.bin, [int(x,0) for x in a.target], a.min_slots, a.max_slots)
    o = Path(a.out); o.parent.mkdir(parents=True, exist_ok=True)
    o.with_suffix(".json").write_text(json.dumps(r, indent=2), encoding="utf-8")
    lines = ["# Vtable / Object Scan", "", f"- input: {r['input']}", f"- vtable candidates: {len(r['vtable_candidates'])}", ""]
    lines += ["## Vtable candidates", "", "| TRUE | slots | first targets |", "|---:|---:|---|"]
    for v in r["vtable_candidates"]:
        first = ", ".join(f"0x{x['target_true']:08X}" for x in v["entries"][:6])
        lines.append(f"| 0x{v['true']:08X} | {v['slots']} | {first} |")
    lines += ["", "## Evidence rule", "", "A candidate becomes a proven vtable only when constructor/vptr-store or runtime indirect-call evidence independently connects it to an object."]
    o.with_suffix(".md").write_text("\n".join(lines), encoding="utf-8")

if __name__ == "__main__":
    main()
