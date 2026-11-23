#!/usr/bin/env python3
"""Surowy listing Thumb z binarki (capstone). Adresy PROJECT (0x08000000+RAW). Uzycie: dump_listing.py FW.bin OUTDIR ADDR[:LEN] ...  (LEN domyslnie 0x120)"""
import os, sys, capstone
fw, out = sys.argv[1], sys.argv[2]; d = open(fw, "rb").read(); os.makedirs(out, exist_ok=True)
md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB); md.detail = False
for a in sys.argv[3:]:
    addr, _, ln = a.partition(":"); addr = int(addr, 16) & ~1; ln = int(ln, 16) if ln else 0x120; raw = addr - 0x08000000
    lines = ["; PROJECT %#x  RAW %#x  RUNTIME %#x  dlugosc %#x" % (addr, raw, addr + 0x10000, ln)]
    for i in md.disasm(d[raw:raw + ln], addr): lines.append("%08x  %-8s %s" % (i.address, i.mnemonic, i.op_str))
    open(os.path.join(out, "listing_%08x.txt" % addr), "w").write("\n".join(lines) + "\n"); print(addr, len(lines) - 1)
