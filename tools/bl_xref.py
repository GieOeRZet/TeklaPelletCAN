#!/usr/bin/env python3
"""tools/bl_xref.py BIN TARGET...  — wszystkie BL/B.W do TARGET (adres RUNTIME 0x0801xxxx). Dekoduje Thumb-2 BL (T1 imm24)."""
import sys,struct
d=open(sys.argv[1],'rb').read(); B=0x08010000
tg={int(x,0)&~1 for x in sys.argv[2:]}
out={t:[] for t in tg}
for o in range(0,len(d)-3,2):
    h1,h2=struct.unpack_from('<HH',d,o)
    if (h1&0xF800)==0xF000 and (h2&0xD000) in (0xD000,0x9000):     # BL (D000) / B.W (9000)
        s=(h1>>10)&1; i1=(h2>>13)&1; i2=(h2>>11)&1
        j1=(~(i1^s))&1 if (h2&0xD000)==0xD000 else (~(i1^s))&1
        j1=(~((h2>>13)&1 ^ s))&1; j2=(~((h2>>11)&1 ^ s))&1
        imm=(s<<24)|(j1<<23)|(j2<<22)|((h1&0x3FF)<<12)|((h2&0x7FF)<<1)
        if s: imm-=1<<25
        t=B+o+4+imm
        if t in tg: out[t].append((B+o,'BL' if (h2&0x5000)==0x5000 else 'B.W'))
for t in sorted(out):
    print("target 0x%08X: %d refs"%(t,len(out[t])))
    for a,k in out[t]: print("  0x%08X %s  (PROJECT 0x%08X, RAW 0x%X)"%(a,k,a-0x10000,a-B))
