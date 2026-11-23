#!/usr/bin/env python3
from pathlib import Path
import sys

PID=0x2165
STORAGE=0x20008D28
BASE=0x08000000

def hits(b,p):
    out=[]; s=0
    while True:
        i=b.find(p,s)
        if i<0: return out
        out.append(BASE+i); s=i+1

def scan(path):
    b=Path(path).read_bytes()
    return {
        'pid_2165_le16_project_hits':[hex(x) for x in hits(b,PID.to_bytes(2,'little'))],
        'storage_literal_project_hits':[hex(x) for x in hits(b,STORAGE.to_bytes(4,'little'))],
        'binary_size':len(b),
    }

if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('usage: cg_timestamp_producer_scan.py FW.bin')
    print(scan(sys.argv[1]))