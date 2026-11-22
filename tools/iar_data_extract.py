#!/usr/bin/env python3
"""Extract the IAR LZ77 .data image and inspect MenuTree runtime tables."""
from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path

SRC_OFF=0x96114
SRC_END=0x9694E
SRAM_BASE=0x20000000
CLASS_ADDR=0x20005EF0
ACCESS_ADDR=0x20005F08
ROOT_PROJECT=0x08042348
PROJECT_BASE=0x08000000

def iar_lz77(src: bytes) -> bytes:
    out=bytearray(); i=0
    while i<len(src):
        r5=src[i]; i+=1
        r6=r5 & 3
        if r6==0:
            r6=src[i]+3; i+=1
        r4=r5>>4
        if r4==0xF:
            r4=src[i]+0xF; i+=1
        lit=r6-1
        out.extend(src[i:i+lit]); i+=lit
        if r4==0: continue
        dist_hi=(r5>>2)&3
        dist_lo=src[i]; i+=1
        if dist_hi==3:
            dist_hi=src[i]; i+=1
        dist=dist_lo+(dist_hi<<8)
        if dist==0: continue
        for _ in range(r4+2):
            out.append(out[-dist])
    return bytes(out)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("bin")
    args=ap.parse_args()
    b=Path(args.bin).read_bytes()
    s=b[SRC_OFF:SRC_END]
    mem=iar_lz77(s)
    if len(mem)!=0x118B3: raise SystemExit(f"unexpected decompressed size {len(mem):#x}")
    def read(addr,n):
        off=addr-SRAM_BASE
        return mem[off:off+n]
    cls=read(CLASS_ADDR,21)
    acc=read(ACCESS_ADDR,21)
    root_raw=ROOT_PROJECT-PROJECT_BASE
    root=[]
    for i in range(21):
        root.append(struct.unpack_from("<H",b,root_raw+i*6)[0])
    print(json.dumps({
      "sha256":hashlib.sha256(b).hexdigest(),
      "compressed":{"raw_start":hex(SRC_OFF),"raw_end_exclusive":hex(SRC_END),"size":len(s)},
      "decompressed":{"base":hex(SRAM_BASE),"size":len(mem),"end_exclusive":hex(SRAM_BASE+len(mem))},
      "runtime_tables":{
        "class_0x20005EF0":{"bytes":list(cls),"hex":cls.hex(" "),"matches_root_selector":list(cls)==root},
        "access_0x20005F08":{"bytes":list(acc),"hex":acc.hex(" "),"matches_class":acc==cls},
      },
      "root_selectors":root
    },indent=2))
if __name__=="__main__": main()
