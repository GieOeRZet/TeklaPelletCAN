#!/usr/bin/env python3
"""python3 -I tools/test_resolver_tables.py FW2213TK_kopia.bin  — sprawdza tabele rezolwera 08036FF2 (PASS 34)."""
import struct, sys
raw = open(sys.argv[1], "rb").read()
t2 = {k: v for k, v in (struct.unpack_from("<hH", raw, 0x37578 + 4 * i) for i in range(0x174))}
t1 = [struct.unpack_from("<hH", raw, 0x37B48 + 4 * i) for i in range(0x31)]
assert t2[0x117] == 0x3506 and t2[0x68] == 0x300B and t2[0x115] == 0x2123
assert t1[0] == (0xA8 - 0x10000 if False else 0xA8, 0x22FD) and t1[1] == (0xA9, 0x2032) and t1[-1] == (0xD6, 0x2329)
assert struct.unpack_from("<HH", raw, 0x3797C) == (0x117, 0x3506)        # korekta PASS 26: rekord wyrownany do 4 B
print("OK: resolver_tables")
