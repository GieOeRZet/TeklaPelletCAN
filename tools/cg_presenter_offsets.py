#!/usr/bin/env python3
"""PASS 86: rozszerzona statyczna mapa offsetow setterow prezenterow.
Nie wymaga capstone: korzysta z llvm-objdump Thumb-2 i sledzi this (r0)
oraz jego kopie przez r4/r5. Adresy raportowane jako PROJECT; firmware
ma baze RAW=PROJECT-0x08010000.
"""
import csv,re,subprocess,sys
BASE=0x08010000
def dis(fw,project):
    raw=project-BASE
    p=subprocess.run(["llvm-objdump","-D","--triple=thumbv7m-none-eabi",fw,
                      f"--start-address=0x{raw:x}",f"--stop-address=0x{raw+0x180:x}"],
                     text=True,capture_output=True,check=True)
    out=[]
    for line in p.stdout.splitlines():
        m=re.match(r"\s*([0-9a-f]+):\s+(?:[0-9a-f]{4}(?:\s+[0-9a-f]{4})*)\s+([a-z0-9.]+)\s*(.*)$",line)
        if m: out.append((BASE+int(m.group(1),16),m.group(2),m.group(3).strip()))
    return out
def scan(fw,a):
    alias={"r0":(0,"direct")}; const={}; rows=[]
    for ea,mn,op in dis(fw,a):
        s=op.replace(" ","")
        mm=re.search(r"\[(r\d+)(?:,#(0x[0-9a-f]+|\d+))?\]",s)
        if mm and mn.startswith(("ldr","str","ldrb","strb","ldrh","strh","ldrsb","ldrsh","ldrd","strd")):
            b=mm.group(1); v=int(mm.group(2),0) if mm.group(2) else 0
            if b in alias:
                base,_=alias[b]; rows.append((base+v,"direct" if b=="r0" and base==0 else "forwarded",ea,mn))
        mm=re.fullmatch(r"(r\d+),#(0x[0-9a-f]+|\d+)",s)
        if mm and mn.startswith(("movw","mov","movs","mov.w")):
            d,v=mm.groups(); const[d]=int(v,0); alias.pop(d,None); continue
        mm=re.fullmatch(r"(r\d+),(r\d+)",s)
        if mm and mn.startswith("add"):
            d,b=mm.groups()
            if b in alias and d in const:
                base,_=alias[b]; v=const[d]
                alias[d]=(base+v,"direct" if b=="r0" and base==0 else "forwarded")
                rows.append((base+v,"direct" if b=="r0" and base==0 else "forwarded",ea,"add-const"))
            elif not (d==b and b in alias): alias.pop(d,None)
            const.pop(d,None); continue
        mm=re.fullmatch(r"(r\d+),(r\d+),#(0x[0-9a-f]+|\d+)",s)
        if mm and mn.startswith("add"):
            d,b,v=mm.groups(); v=int(v,0)
            if b in alias:
                base,_=alias[b]; alias[d]=(base+v,"direct" if b=="r0" and base==0 else "forwarded")
                rows.append((base+v,"direct" if b=="r0" and base==0 else "forwarded",ea,"add"))
            else: alias.pop(d,None)
            const.pop(d,None); continue
        mm=re.fullmatch(r"(r\d+),(r\d+)",s)
        if mn.startswith("mov") and mm:
            d,b=mm.groups()
            if b in alias: alias[d]=alias[b]
            else: alias.pop(d,None)
            const.pop(d,None); continue
        if mn in ("bx","pop") and ("lr" in s or "pc" in s): break
    return rows
def main(fw,presenter,out):
    setters=[]
    with open(presenter,encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["setter"]: setters.append(int(r["setter"],16))
    setters=sorted(set(setters)); seen=set()
    with open(out,"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["setter_project","offset","confidence","evidence_project","evidence_kind"])
        for a in setters:
            for off,conf,ea,k in scan(fw,a):
                if not 0 <= off <= 0xffff: continue
                key=(a,off,conf)
                if key in seen: continue
                seen.add(key); w.writerow([f"0x{a:X}",f"0x{off:X}",conf,f"0x{ea:X}",k])
if __name__=="__main__": main(*sys.argv[1:4])
