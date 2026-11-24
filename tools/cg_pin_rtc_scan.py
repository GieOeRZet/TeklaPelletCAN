#!/usr/bin/env python3
"""Static-only scan for the FW2213TK PIN special path and RTC hardware anchors."""
from __future__ import annotations
import argparse, hashlib, struct
from pathlib import Path
EXPECTED_SHA256="1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071"
EXPECTED_SIZE=0x1F0000
PROJECT_BASE=0x08000000
RUNTIME_DELTA=0x10000
def project(raw:int)->int: return PROJECT_BASE+raw
def hits(data:bytes,needle:bytes):
    out=[]; p=0
    while True:
        i=data.find(needle,p)
        if i<0:return out
        out.append(i); p=i+1
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("bin"); ap.add_argument("--out",default=None)
    a=ap.parse_args(); data=Path(a.bin).read_bytes()
    sha=hashlib.sha256(data).hexdigest()
    if len(data)!=EXPECTED_SIZE: raise SystemExit(f"SIZE_MISMATCH {len(data)} != {EXPECTED_SIZE}")
    if sha!=EXPECTED_SHA256: raise SystemExit(f"SHA256_MISMATCH {sha}")
    rows=[]
    def add(label,raw,detail): rows.append((label,raw,project(raw),detail))
    for val,label in [(0x7c8,"1992"),(0x1a0a,"6666")]:
        hs=hits(data,struct.pack("<H",val))
        add(f"PIN literal {label}",hs[0] if hs else -1,f"LE16 occurrences={len(hs)}; all={[(hex(x),hex(project(x))) for x in hs[:20]]}")
    for val,label in [(0x20008c50,"RAM registry pointer 0x20008C50"),(0x40002800,"RTC base"),(0x40002804,"RTC register literal"),(0x40002808,"RTC register literal"),(0x4000280c,"RTC register literal")]:
        hs=hits(data,struct.pack("<I",val))
        add(label,hs[0] if hs else -1,f"LE32 occurrences={len(hs)}; all={[(hex(x),hex(project(x))) for x in hs[:20]]}")
    for pa,name in [(0x08018E94,"FUN_08018E94 (RTC write path)"),(0x08018F18,"FUN_08018F18 (RTC read path)"),(0x08018F78,"FUN_08018F78 (RTC conversion/write helper)"),(0x08018FF8,"FUN_08018FF8 (RTC conversion/read helper)"),(0x0801906E,"FUN_0801906E (RTC field conversion)")]:
        add(name,pa-PROJECT_BASE,"function entry; runtime=0x%08X"%(pa+RUNTIME_DELTA))
    rows.append(("23-entry registry",-1,-1,"OPEN: 0x20008C50 is SRAM/IAR-LZ77 state; raw BIN cannot be indexed directly."))
    lines=["# cg_pin_rtc_scan result","",f"- SHA-256: {sha}",f"- size: {len(data):#x} bytes","",'| Anchor | RAW | PROJECT | Detail |','|---|---:|---:|---|']
    for lab,raw,pa,det in rows:
        lines.append(f'| {lab} | {("OPEN" if raw<0 else hex(raw))} | {("OPEN" if pa<0 else hex(pa))} | {det} |')
    text="\n".join(lines)+"\n"
    if a.out: Path(a.out).write_text(text,encoding="utf-8")
    else: print(text,end="")
if __name__=="__main__": main()
