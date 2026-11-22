#!/usr/bin/env python3
"""tools/disasm_thumb.py BIN ADDR [LEN] [--project]  — dezasemblacja Thumb-2; ADDR domyslnie RUNTIME (0x0801xxxx), z --project: PROJECT (0x0800xxxx)."""
import sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
b=sys.argv[1]; a=int(sys.argv[2],0); n=int(sys.argv[3],0) if len(sys.argv)>3 and not sys.argv[3].startswith('-') else 0x40
if '--project' in sys.argv: a+=0x10000
d=open(b,'rb').read(); o=a-0x08010000
for i in Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS).disasm(d[o:o+n],a): print("0x%08X  %-8s %s"%(i.address,i.mnemonic,i.op_str))
