#!/usr/bin/env python3
"""Verify the RTC auto-sync object's runtime vtable linkage in the canonical BIN."""
from pathlib import Path
import struct, sys

PROJECT_BASE=0x08000000
RUNTIME_BASE=0x08010000
CTOR_VPTR_LITERAL_PROJECT=0x08010464
VTABLE_PROJECT=0x0809446C
AUTOSYNC_PROJECT=0x08062638

def u32(b,o): return struct.unpack_from("<I",b,o)[0]

def scan(path):
    b=Path(path).read_bytes()
    literal=u32(b,CTOR_VPTR_LITERAL_PROJECT-PROJECT_BASE)
    slot0=u32(b,VTABLE_PROJECT-PROJECT_BASE)
    return {
        "vptr_literal_project":hex(CTOR_VPTR_LITERAL_PROJECT),
        "vptr_literal_value_runtime":hex(literal),
        "vtable_project":hex(VTABLE_PROJECT),
        "vtable_slot0_runtime":hex(slot0),
        "expected_slot0_runtime":hex(AUTOSYNC_PROJECT+(RUNTIME_BASE-PROJECT_BASE)+1),
        "slot0_matches":slot0==AUTOSYNC_PROJECT+(RUNTIME_BASE-PROJECT_BASE)+1,
        "vptr_matches":literal==VTABLE_PROJECT+(RUNTIME_BASE-PROJECT_BASE),
    }

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit(f"usage: {sys.argv[0]} FW.bin")
    for k,v in scan(sys.argv[1]).items():
        print(f"{k}: {v}")
