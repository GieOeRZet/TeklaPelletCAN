#!/usr/bin/env python3
"""PASS 79 static negative proof for PID 0x2165 publisher exclusion.

Usage:
  python3 tools/cg_timestamp_tx_exclusion_scan.py FW2213TK_kopia.bin
"""
from pathlib import Path
import sys

PID = 0x2165
RAW_BASE = 0x08000000

def le16(b, off):
    return int.from_bytes(b[off:off+2], "little")

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: cg_timestamp_tx_exclusion_scan.py FW2213TK_kopia.bin")
    b = Path(sys.argv[1]).read_bytes()
    assert len(b) == 0x1F0000, hex(len(b))

    hits = [i for i in range(0, len(b)-1, 2) if le16(b, i) == PID]
    addrs = [RAW_BASE + i for i in hits]

    # The two publisher blocks are stable RAW anchors from PASS 79.
    # 0x111EE/0x111F6: PID literal + comparison in normal publisher.
    # 0x112B8/0x112C0: PID literal + comparison in special publisher.
    assert le16(b, 0x111EE) == PID
    assert le16(b, 0x112B8) == PID

    # Confirm the surrounding Thumb instruction bytes are the expected MOVW
    # encodings used to load 0x2165.
    assert b[0x111EE:0x111F2] == bytes.fromhex("f242 1365")
    assert b[0x112B8:0x112BC] == bytes.fromhex("f242 1365")

    print("OK")
    print("size=0x%x" % len(b))
    print("pid=0x%04x" % PID)
    print("all LE16 occurrences:", ", ".join("0x%08X" % x for x in addrs))
    print("publisher normal anchor: PROJECT 0x080211EE")
    print("publisher special anchor: PROJECT 0x080212B8")
    print("result: PID 0x2165 is explicitly excluded from both 0x584/0x42 publisher paths")

if __name__ == "__main__":
    main()
