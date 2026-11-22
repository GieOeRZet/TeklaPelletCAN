#!/usr/bin/env python3
"""Deterministic Thumb pointer-flow scanner.

Tracks Thumb-1 PC-relative literal pointers and avoids interpreting the
second halfword of Thumb-2 instructions as an independent Thumb-1 instruction.
It also records MOVW/MOVT materialization candidates and common Thumb-2
immediate memory operations. Candidate/static only; semantic meaning is not
promoted.
"""
from __future__ import annotations
import argparse,json,struct
from pathlib import Path

BASE=0x08010000

def project(a): return a-0x10000
def raw_to_true(off): return BASE+off
def true_to_raw(a): return a-BASE

def is_thumb32_prefix(h):
    return ((h>>11)&0x1f) in (0b11101,0b11110,0b11111)

def ldr_literal(hw,off):
    if (hw&0xF800)!=0x4800:return None
    return (hw>>8)&7, ((raw_to_true(off+4))&~3)+((hw&0xff)*4)

def movw_movt(h1,h2):
    if (h1 & 0xFBF0) not in (0xF240,0xF2C0): return None
    i=(h1>>10)&1
    imm4=h1&0xF
    imm3=(h2>>12)&7
    rd=(h2>>8)&0xF
    imm8=h2&0xFF
    imm=(i<<11)|(imm4<<12)|(imm3<<8)|imm8
    return {"mnemonic":"MOVT" if (h1&0x80) else "MOVW","rd":rd,"imm16":imm}

def mem16(hw):
    if (hw & 0xF000)==0x5000:
        op=(hw>>9)&7
        rn=(hw>>3)&7
        rm=(hw>>6)&7
        rt=hw&7
        reg={
            0:("STR",4,"store"),1:("STRH",2,"store"),2:("STRB",1,"store"),
            4:("LDR",4,"load"),5:("LDRH",2,"load"),6:("LDRB",1,"load")
        }
        if op in reg:
            m,w,k=reg[op]
            return {"mnemonic":m,"kind":k,"base_reg":rn,"index_reg":rm,
                    "offset":None,"width":w,"rt":rt}
    top=hw&0xF800
    imm={
        0x6000:("STR",4,"store",4),0x6800:("LDR",4,"load",4),
        0x7000:("STRB",1,"store",1),0x7800:("LDRB",1,"load",1),
        0x8000:("STRH",2,"store",2),0x8800:("LDRH",2,"load",2)
    }
    if top in imm:
        m,w,k,mul=imm[top]
        rn=(hw>>3)&7
        rt=hw&7
        imm5=(hw>>6)&0x1f
        return {"mnemonic":m,"kind":k,"base_reg":rn,"index_reg":None,
                "offset":imm5*mul,"width":w,"rt":rt}
    return None

def mem32(h1,h2):
    key=h1&0xFFF0
    forms={
        0xF880:("STRB",1,"store"),0xF890:("LDRB",1,"load"),
        0xF8A0:("STRH",2,"store"),0xF8B0:("LDRH",2,"load"),
        0xF8C0:("STR",4,"store"),0xF8D0:("LDR",4,"load")
    }
    if key in forms:
        m,w,k=forms[key]
        return {"mnemonic":m,"kind":k,"base_reg":h1&0xF,"index_reg":None,
                "offset":h2&0xFFF,"width":w,"rt":(h2>>12)&0xF}
    return None

def find_start(data,off,limit=0x100):
    for p in range(off&~1,max(-1,off-limit),-2):
        h=struct.unpack_from("<H",data,p)[0]
        if (h&0xFE00)==0xB400:  # Thumb-1 PUSH
            return p
        if h==0xE92D:            # Thumb-2 PUSH.W
            return p
    return max(0,off-limit)

def scan(path,targets,window=0x180):
    data=Path(path).read_bytes()
    wanted=set(targets)
    out=[]
    for off in range(0,len(data)-1,2):
        d=ldr_literal(struct.unpack_from("<H",data,off)[0],off)
        if not d:
            continue
        rt,pool_true=d
        pool_raw=true_to_raw(pool_true)
        if pool_raw<0 or pool_raw+4>len(data):
            continue
        value=struct.unpack_from("<I",data,pool_raw)[0]
        if value not in wanted:
            continue
        fstart=find_start(data,off)
        accesses=[]
        wide=[]
        alive=True
        p=off+2
        end=min(len(data)-1,off+window)
        while p<end:
            h1=struct.unpack_from("<H",data,p)[0]
            if is_thumb32_prefix(h1) and p+4<=len(data):
                h2=struct.unpack_from("<H",data,p+2)[0]
                mm=mem32(h1,h2)
                mv=movw_movt(h1,h2)
                if mv:
                    wide.append({
                        "at_raw":p,
                        "at_project":project(raw_to_true(p)),
                        **mv
                    })
                if mm and alive and mm["base_reg"]==rt:
                    accesses.append({
                        "at_raw":p,
                        "at_project":project(raw_to_true(p)),
                        **mm,
                        "thumb32":True
                    })
                    if mm["kind"]=="load" and mm["rt"]==rt:
                        alive=False
                p+=4
                continue
            mm=mem16(h1)
            if mm and alive and mm["base_reg"]==rt:
                accesses.append({
                    "at_raw":p,
                    "at_project":project(raw_to_true(p)),
                    **mm,
                    "thumb32":False
                })
                if mm["kind"]=="load" and mm["rt"]==rt:
                    alive=False
            p+=2
        out.append({
            "target_true":value,
            "target_address_space":"SRAM",
            "pool_raw":pool_raw,
            "pool_true":pool_true,
            "literal_load_raw":off,
            "literal_load_true":raw_to_true(off),
            "loaded_register":f"r{rt}",
            "function_start_raw":fstart,
            "function_start_true":raw_to_true(fstart),
            "function_start_project":project(raw_to_true(fstart)),
            "accesses":accesses,
            "wide_instructions":wide
        })
    return {"input":str(path),"size":len(data),"base_true":BASE,"targets":out}

def render(r):
    s=[
        "# Pointer Flow Scan","",
        "Evidence: candidate/static only.",
        "Decoder: Thumb-1 PC-relative LDR literals, Thumb-2 instruction-width separation, "
        "MOVW/MOVT candidates, and common Thumb-1/Thumb-2 memory forms.",""
    ]
    for x in r["targets"]:
        s += [
            f"## Target 0x{x['target_true']:08X}",
            f"- address space: {x['target_address_space']}",
            f"- literal pool RAW: 0x{x['pool_raw']:X}",
            f"- LDR literal RAW: 0x{x['literal_load_raw']:X} -> {x['loaded_register']}",
            f"- function candidate PROJECT: 0x{x['function_start_project']:08X}",""
        ]
        if x["accesses"]:
            s += [
                "| RAW | PROJECT | Kind | Mnemonic | Base | Offset/Index | Thumb-2 |",
                "|---:|---:|---|---|---:|---:|---|"
            ]
            for a in x["accesses"]:
                oi=a["index_reg"] if a["index_reg"] is not None else a["offset"]
                s.append(
                    f"| 0x{a['at_raw']:X} | 0x{a['at_project']:08X} | {a['kind']} | "
                    f"{a['mnemonic']} | r{a['base_reg']} | {oi} | {a['thumb32']} |"
                )
        else:
            s.append("- No same-register memory access after provenance-preserving decode.")
        if x["wide_instructions"]:
            s += ["","### MOVW/MOVT candidates"]
            for a in x["wide_instructions"]:
                s.append(
                    f"- RAW 0x{a['at_raw']:X}: {a['mnemonic']} r{a['rd']}, #0x{a['imm16']:X}"
                )
        s.append("")
    return "\n".join(s)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("bin")
    ap.add_argument("--target",action="append",required=True)
    ap.add_argument("--window",type=lambda x:int(x,0),default=0x180)
    ap.add_argument("--out",default="pointer_flow_scan")
    a=ap.parse_args()
    r=scan(a.bin,[int(x,0) for x in a.target],a.window)
    p=Path(a.out)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.with_suffix(".json").write_text(json.dumps(r,indent=2),encoding="utf-8")
    p.with_suffix(".md").write_text(render(r),encoding="utf-8")

if __name__=="__main__":
    main()
