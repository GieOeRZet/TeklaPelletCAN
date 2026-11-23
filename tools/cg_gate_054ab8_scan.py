#!/usr/bin/env python3
"""PASS 80 anchors for the level!=0 CWU gate.

Usage: python3 tools/cg_gate_054ab8_scan.py FW2213TK_kopia.bin
"""
from pathlib import Path
import sys

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: cg_gate_054ab8_scan.py FW2213TK_kopia.bin")
    b=Path(sys.argv[1]).read_bytes()
    assert len(b)==0x1f0000
    # RAW 0x44CA6 = artifact runtime address 0x08054CA6 - 0x10000.
    # Gate sequence: ldrb.w r0,[r0,#0x158] ; cbz r0,...
    assert b[0x44ca6:0x44cae] == bytes.fromhex("f890 0158 b118 4629 1d20")
    # In the gated path: bitmap 0x84, presenter offset 0x1498.
    assert b[0x44cb4:0x44cc0] == bytes.fromhex("2084 f8ad 0000 4669 f241 4098")
    print("OK: RAW 0x44CA6 gate is level!=0 and gated path uses presenter offset 0x1498")
    print("artifact/runtime gate label: 0x08054AB8 / caller 0x08054CA6")
    print("presenter-map identity: 0x1498 -> PID 0x201A Hot water 1 result temperature")

if __name__=="__main__": main()
