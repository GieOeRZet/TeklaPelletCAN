#!/usr/bin/env python3
"""Static scan for the exact CAN RX write gate that can target PID 0x2165."""
from pathlib import Path
import struct
import hashlib

PID = 0x2165
STD_ID = 0x584
OPCODE_SET = 1
WIRE_U32 = 5
TYPE_U32 = 3

def find_all(blob, needle):
    out=[]; p=0
    while True:
        p=blob.find(needle,p)
        if p<0: return out
        out.append(p); p+=1

def main():
    import sys
    fw=Path(sys.argv[1] if len(sys.argv)>1 else "/mnt/data/FW2213TK (1).bin").read_bytes()
    print("size", len(fw))
    print("sha256", hashlib.sha256(fw).hexdigest())
    for name,val in [("PID_LE16", struct.pack("<H",PID)),("STDID_LE16", struct.pack("<H",STD_ID))]:
        print(name, [hex(x) for x in find_all(fw,val)[:20]])
    for off, desc in [
        (0x62ab2, "cmp StdId against 0x584"),
        (0x62ad8, "BL FUN_08062B22"),
        (0x62b2c, "load PID bytes frame+4/+5"),
        (0x62b7a, "opcode frame+6 == 1 gate"),
        (0x62c18, "wire-u32 decode branch"),
        (0x62c28, "load frame+7"),
    ]:
        print(hex(0x08000000+off), desc)
    print("Expected logical write: StdId 0x584, PID 0x2165, opcode 1, u32 LE at frame+7..+10")

if __name__ == "__main__":
    main()
