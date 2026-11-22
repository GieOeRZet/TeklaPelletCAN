#!/usr/bin/env python3
"""Deterministic ARM/Thumb static RE scanner. Requires capstone."""
from __future__ import annotations
import argparse,json,re,struct
from pathlib import Path
from collections import defaultdict
BASE=0x08010000
def true_to_project(a): return a-0x10000
def parse_imm(s):
    m=re.search(r"#(0x[0-9a-f]+|[0-9]+)",s,re.I)
    return int(m.group(1),0) if m else None
def scan(path,targets):
    from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
    data=Path(path).read_bytes()
    md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS); md.detail=True
    calls=[]; indirect=[]; literals=[]; memrefs=[]
    for ins in md.disasm(data,BASE):
        m=ins.mnemonic.lower(); op=ins.op_str; raw=ins.address-BASE
        if m in ("bl","blx","b","b.w","bl.w"):
            t=parse_imm(op)
            if t is not None: calls.append({"kind":"DIRECT_CALL" if m.startswith("bl") else "BRANCH","at_raw":raw,"at_true":ins.address,"target_true":t,"target_project":true_to_project(t),"text":ins.mnemonic+" "+op})
        if m in ("blx","bx") and not op.startswith("#"): indirect.append({"at_raw":raw,"at_true":ins.address,"text":ins.mnemonic+" "+op,"target_expr":op})
        if m.startswith("ldr") and "pc" in op.lower(): literals.append({"kind":"LITERAL_LOAD","at_raw":raw,"at_true":ins.address,"text":ins.mnemonic+" "+op})
        if "[" in op and "]" in op: memrefs.append({"at_raw":raw,"at_true":ins.address,"text":ins.mnemonic+" "+op})
        if m in ("movw","movt"):
            v=parse_imm(op)
            if v is not None: literals.append({"kind":m.upper(),"at_raw":raw,"at_true":ins.address,"immediate":v,"text":ins.mnemonic+" "+op})
    for t in targets:
        needle=struct.pack("<I",t); start=0
        while True:
            off=data.find(needle,start)
            if off<0: break
            literals.append({"kind":"LE32_LITERAL","at_raw":off,"at_true":BASE+off,"target":t,"text":"LE32 0x%08X"%t}); start=off+1
    by=defaultdict(list)
    for c in calls:
        if c["target_true"] in targets: by[c["target_true"]].append(c)
    return {"input":str(path),"size":len(data),"base_true":BASE,"calls":calls,"indirect_calls":indirect,"literal_candidates":literals,"memory_refs":memrefs,"target_summary":[{"target_true":t,"target_project":true_to_project(t),"direct_call_count":len(by.get(t,[])),"literal_count":sum(1 for x in literals if x.get("target")==t)} for t in targets]}
def md(r):
    z=["# Static RE Scan","","- input: "+r["input"],"- size: "+str(r["size"])+" B","","## Target summary","","| TRUE | PROJECT | Direct BL/BLX | LE32 literals |","|---:|---:|---:|---:|"]
    for x in r["target_summary"]: z.append("| 0x%08X | 0x%08X | %d | %d |"%(x["target_true"],x["target_project"],x["direct_call_count"],x["literal_count"]))
    z+=["","## Indirect dispatch candidates","","| TRUE | Instruction | Expression |","|---:|---|---|"]
    for x in r["indirect_calls"]: z.append("| 0x%08X | %s | %s |"%(x["at_true"],x["text"],x["target_expr"]))
    z+=["","## Evidence rule","Direct calls and exact LE32 literals are mechanical observations. Indirect edges require independent runtime/object/vtable evidence."]
    return "\n".join(z)
def main():
    p=argparse.ArgumentParser(); p.add_argument("bin"); p.add_argument("--target",action="append",default=[]); p.add_argument("--out",default="re_scan")
    a=p.parse_args(); r=scan(a.bin,[int(x,0) for x in a.target]); o=Path(a.out); o.parent.mkdir(parents=True,exist_ok=True)
    o.with_suffix(".json").write_text(json.dumps(r,indent=2),encoding="utf-8"); o.with_suffix(".md").write_text(md(r),encoding="utf-8")
if __name__=="__main__": main()