#!/usr/bin/env python3
"""PASS 52: lista wywolan model_get (klucze UI -> PID/nazwa) i innych BL w zakresie funkcji. python3 -I tools/fn_keys.py FW.bin START LEN  (np. ekran glowny: 0x08041CB8 0x400)"""
import re,struct,sys,csv
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
raw=open(sys.argv[1],"rb").read(); B=0x08010000
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS)
res={}
for fn in ("resolver_t1.csv","resolver_t2.csv"):
    for r in csv.DictReader(open("/home/user/teklapelletcan/analiza_archiwum/FW2213TK-2026-11-22/data/"+fn,encoding="utf-8")): res.setdefault(int(r["ui_key"],16),(r["value"],r["name"]))
a=int(sys.argv[2],16); n=int(sys.argv[3],16); code=list(md.disasm(raw[a-B:a-B+n],a))
key=None
for i in code:
    m=re.match(r"r1, #(0x[0-9a-f]+|\d+)$",i.op_str)
    if i.mnemonic in("movs","mov","movw","mov.w") and m: key=int(m.group(1),0)
    if i.mnemonic=="bl":
        t=int(i.op_str.lstrip("#"),16)
        if t==0x8046ff2: print("%08x GET key=%s %s"%(i.address,hex(key) if key is not None else None,res.get(key,("","?"))))
        else: print("%08x   -> %x"%(i.address,t))
    if i.mnemonic in("pop","pop.w") and "pc" in i.op_str: print("%08x RET"%i.address)
