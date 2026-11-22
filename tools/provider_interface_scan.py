#!/usr/bin/env python3
"""Evidence-first provider/interface scanner."""
from __future__ import annotations
import argparse, json, struct
from pathlib import Path
FLASH_LO=0x08010000
FLASH_HI=0x08100000
BASE=FLASH_LO
def u32(d,o):
    return struct.unpack_from("<I",d,o)[0] if 0<=o<=len(d)-4 else None
def codeptr(v):
    return v is not None and (v & 1) and FLASH_LO <= (v & ~1) < FLASH_HI
def scan(path,vtable,window=64):
    d=Path(path).read_bytes(); raw=vtable-BASE
    words=[]
    for i in range(window//4):
        v=u32(d,raw+i*4)
        words.append({"offset":i*4,"true":v,"code_pointer":codeptr(v)})
    needle=struct.pack("<I",vtable); refs=[]; p=0
    while True:
        p=d.find(needle,p)
        if p<0: break
        refs.append({"raw":p,"true":BASE+p}); p+=1
    return {"input":str(path),"vtable":hex(vtable),"words":words,"vtable_literal_refs":refs}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("bin"); ap.add_argument("--vtable",required=True,type=lambda x:int(x,0)); ap.add_argument("--window",type=int,default=64); ap.add_argument("--out",default="provider_interface_scan"); a=ap.parse_args()
    r=scan(a.bin,a.vtable,a.window); p=Path(a.out); p.parent.mkdir(parents=True,exist_ok=True)
    p.with_suffix(".json").write_text(json.dumps(r,indent=2))
    lines=[f"# Provider interface scan 0x{a.vtable:08X}","","| offset | value | Thumb code ptr |","|---:|---:|:---:|"]
    for x in r["words"]: lines.append(f"| 0x{x['offset']:02X} | {('0x%08X'%x['true']) if x['true'] is not None else 'None'} | {x['code_pointer']} |")
    p.with_suffix(".md").write_text("\n".join(lines))
if __name__=="__main__": main()
