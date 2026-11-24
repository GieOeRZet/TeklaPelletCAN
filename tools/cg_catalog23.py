#!/usr/bin/env python3
"""PASS 94: decode the 23-entry Parameters-set catalog from a RAM image."""
import struct
BASE=0x20008C50
COUNT=23
STEP=0x10

def decode(ram: bytes, ram_base=0x20000000):
    out=[]
    off=BASE-ram_base
    for i in range(COUNT):
        ptr=struct.unpack_from("<I",ram,off+i*4)[0]
        value=struct.unpack_from("<I",ram,ptr+8-ram_base)[0]
        out.append((i,ptr,value))
    return out
