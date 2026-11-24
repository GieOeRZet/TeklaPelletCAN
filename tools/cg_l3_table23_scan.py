#!/usr/bin/env python3
"""Static PASS 81 checks for L>=3 wrappers and Parameters-set source array."""
from pathlib import Path
import struct

RAW_BASE = 0x08000000
ARTIFACT_DELTA = 0x10000
WRAPPERS = {
    0x0805A9EC: 0x4A9EC,
    0x0805B1D4: 0x4B1D4,
    0x0805F400: 0x4F400,
    0x0805FE9C: 0x4FE9C,
}
CALLERS = {0x4A9EC: 0x40DD2, 0x4B1D4: 0x41318, 0x4F400: 0x4B4CC, 0x4FE9C: 0x4BEAA}
TABLE_PTR = 0x20008C50
SOURCE_BASE = 0x20008D84
RECORD_SIZE = 0x14
RECORD23 = SOURCE_BASE + 22 * RECORD_SIZE

def artifact_to_raw(a): return a - 0x08000000 - ARTIFACT_DELTA
def u32(p, off): return struct.unpack_from("<I", p, off)[0]

def analyze(data: bytes):
    return {
        "size": len(data),
        "wrappers_raw": WRAPPERS,
        "callers_raw": CALLERS,
        "source_base": hex(SOURCE_BASE),
        "record_size": hex(RECORD_SIZE),
        "record23": hex(RECORD23),
        "record23_end": hex(RECORD23 + RECORD_SIZE - 1),
        "table_entries": 23,
    }

if __name__ == "__main__":
    import argparse, json
    ap = argparse.ArgumentParser()
    ap.add_argument("firmware", type=Path)
    args = ap.parse_args()
    print(json.dumps(analyze(args.firmware.read_bytes()), indent=2))
