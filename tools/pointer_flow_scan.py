#!/usr/bin/env python3
"""Deterministic Thumb literal-pointer flow scanner."""
from __future__ import annotations
import argparse, json, struct
from pathlib import Path
BASE = 0x08010000
def project(a): return a - 0x10000
def raw_to_true(off): return BASE + off
def true_to_raw(a): return a - BASE
def decode_ldr_literal(hw, off):
    if (hw & 0xF800) != 0x4800: return None
    rt=(hw>>8)&7
    pc=(raw_to_true(off+4)) & ~3
    return rt, pc + ((hw&0xFF)*4)
def decode_mem(hw):
    op=(hw>>9)&7; rn=(hw>>3)&7; rt=hw&7; imm5=(hw>>6)&0x1F
    reg={0:("STR",4,"store"),1:("STRH",2,"store"),2:("STRB",1,"store"),
         4:("LDR",4,"load"),5:("LDRH",2,"load"),6:("LDRB",1,"load")}
    if op in reg:
        m,w,k=reg[op]; return {"mnemonic":m,"kind":k,"base_reg":rn,"index_reg":(hw>>6)&7,"offset":None,"width":w}
    top=hw&0xF800
    imm={0x6000:("STR",4,"store",4),0x6800:("LDR",4,"load",4),
         0x7000:("STRB",1,"store",1),0x7800:("LDRB",1,"load",1),
         0x8000:("STRH",2,"store",2),0x8800:("LDRH",2,"load",2)}
    if top in imm:
        m,w,k,mul=imm[top]; return {"mnemonic":m,"kind":k,"base_reg":rn,"index_reg":None,"offset":imm5*mul,"width":w}
    return None
def find_start(data, off, limit=0x100):
    for p in range(off & ~1, max(-1,off-limit), -2):
        hw=struct.unpack_from("<H",data,p)[0]
        if (hw & 0xFE00)==0xB400: return p
    return max(0,off-limit)
def scan(path, targets, window=0x180):
    data=Path(path).read_bytes(); wanted=set(targets); out=[]
    for off in range(0,len(data)-1,2):
        d=decode_ldr_literal(struct.unpack_from("<H",data,off)[0],off)
        if not d or d[1] not in wanted: continue
        rt,addr=d; fstart=find_start(data,off); ops=[]
        for p in range(off+2,min(len(data)-1,off+window),2):
            hw=struct.unpack_from("<H",data,p)[0]; m=decode_mem(hw)
            if m and m["base_reg"]==rt:
                ops.append({"at_raw":p,"at_true":raw_to_true(p),**m})
            if hw in (0x4770,0xBD00): break
        out.append({"target_true":addr,"target_project":project(addr),"target_raw":true_to_raw(addr),
                    "literal_load_raw":off,"literal_load_true":raw_to_true(off),"loaded_register":f"r{rt}",
                    "function_start_raw":fstart,"function_start_true":raw_to_true(fstart),
                    "function_start_project":project(raw_to_true(fstart)),"accesses":ops})
    return {"input":str(path),"size":len(data),"base_true":BASE,"targets":out}
def render(r):
    s=["# Pointer Flow Scan","","Evidence: candidate/static only.","Decoder: Thumb 16-bit PC-relative LDR literals and common 16-bit memory forms.",""]
    for x in r["targets"]:
        s += [f"## Target 0x{x['target_true']:08X}",f"- PROJECT: 0x{x['target_project']:08X}",
              f"- RAW literal: 0x{x['target_raw']:X}",f"- LDR literal: RAW 0x{x['literal_load_raw']:X} -> {x['loaded_register']}",
              f"- Function candidate: PROJECT 0x{x['function_start_project']:08X}",""]
        if x["accesses"]:
            s += ["| RAW | TRUE | Kind | Mnemonic | Base | Offset/Index |","|---:|---:|---|---|---:|---|"]
            for a in x["accesses"]:
                oi=a["index_reg"] if a["index_reg"] is not None else a["offset"]
                s.append(f"| 0x{a['at_raw']:X} | 0x{a['at_true']:08X} | {a['kind']} | {a['mnemonic']} | r{a['base_reg']} | {oi} |")
        else: s.append("- No decoded same-register accesses.")
        s.append("")
    return "\n".join(s)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("bin"); ap.add_argument("--target",action="append",required=True)
    ap.add_argument("--window",type=lambda x:int(x,0),default=0x180); ap.add_argument("--out",default="pointer_flow_scan")
    a=ap.parse_args(); r=scan(a.bin,[int(x,0) for x in a.target],a.window); p=Path(a.out); p.parent.mkdir(parents=True,exist_ok=True)
    p.with_suffix(".json").write_text(json.dumps(r,indent=2),encoding="utf-8"); p.with_suffix(".md").write_text(render(r),encoding="utf-8")
if __name__=="__main__": main()
