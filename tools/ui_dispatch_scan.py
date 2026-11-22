#!/usr/bin/env python3
"""Extract the 21-entry runtime-class TBB dispatch graph.

Static/candidate only. Resolves the TBB byte table, follows the small
firmware trampolines, and records direct selector-byte stores. It does not
assign business semantics to class numbers.
"""
from __future__ import annotations
import argparse,json,struct
from pathlib import Path

TABLE_RAW=0x3C076
TBB_PC_RAW=0x3C072
PROJECT_BASE=0x08000000

def project(raw): return PROJECT_BASE+raw
def thumb32(h): return ((h>>11)&0x1F) in (0b11101,0b11110,0b11111)
def sign(v,b): return v-(1<<b) if v&(1<<(b-1)) else v

def b16(h,addr):
    if (h&0xF800)!=0xE000:return None
    return (addr+4+sign((h&0x7FF)<<1,12))&0xFFFFFFFF

def bw(h1,h2,addr):
    if (h1&0xF800)!=0xF000 or (h2&0xD000)!=0x9000:return None
    s=(h1>>10)&1; j1=(h2>>13)&1; j2=(h2>>11)&1
    i1=(~(j1^s))&1; i2=(~(j2^s))&1
    imm=(s<<24)|(i1<<23)|(i2<<22)|((h1&0x3FF)<<12)|((h2&0x7FF)<<1)
    return (addr+4+sign(imm,25))&0xFFFFFFFF

def resolve_trampoline(data,start,max_hops=3):
    cur=start
    movs=[]
    for _ in range(max_hops):
        for p in range(cur,min(cur+0x24,len(data)-3),2):
            h=struct.unpack_from("<H",data,p)[0]
            if (h&0xFF00)==0x2100: movs.append(h&0xFF)
            if thumb32(h):
                h2=struct.unpack_from("<H",data,p+2)[0]
                d=bw(h,h2,p)
                if d is not None:return d,movs
                continue
            d=b16(h,p)
            if d is not None and d>p and d<start+0x40:
                cur=d
                break
        else:
            break
    return None,movs

def scan(path):
    data=Path(path).read_bytes()
    if len(data)<TABLE_RAW+21: raise ValueError("BIN too small")
    out=[]
    for cls in range(21):
        table_byte=data[TABLE_RAW+cls]
        tbb_target=TABLE_RAW+2*table_byte
        row={"class":cls,"table_byte":table_byte,"tbb_target_raw":tbb_target}
        if struct.unpack_from("<H",data,tbb_target)[0]==0xBD10:
            row["kind"]="return"
            out.append(row); continue
        handler,movs=resolve_trampoline(data,tbb_target)
        if handler is None:
            row["kind"]="inline_or_unresolved"
            out.append(row); continue
        row.update(handler_raw=handler,handler_project=project(handler),
                  trampoline_movs_r1=movs)
        for p in range(handler,min(handler+0x30,len(data)-3),2):
            h=struct.unpack_from("<H",data,p)[0]
            if thumb32(h):
                h2=struct.unpack_from("<H",data,p+2)[0]
                if (h&0xFFF0)==0xF880:
                    row["selector_store_raw"]=p
                    row["selector_store_offset"]=h2&0xFFF
                    break
            elif (h&0xFFC0)==0x77C0:
                row["selector_store_raw"]=p
                row["selector_store_offset"]=(h>>6)&0x1F
                break
        out.append(row)
    return {"tbb_pc_raw":TBB_PC_RAW,"table_raw":TABLE_RAW,"classes":out}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("bin")
    ap.add_argument("--out",default="ui_dispatch_scan.json")
    a=ap.parse_args()
    r=scan(a.bin)
    Path(a.out).write_text(json.dumps(r,indent=2),encoding="utf-8")
    print(json.dumps(r,indent=2))

if __name__=="__main__":
    main()
