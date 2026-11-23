#!/usr/bin/env python3
"""PASS 51: katalog miejsc podnoszenia/zerowania alarmow. Menedzer alarmow (obiekt 0x20021E90, pierscien 20x12 B od +0xC):
raise(obj,code)=0x08025198, clear(obj,code)=0x08025104 (RUNTIME). Dla kazdego BL szuka stalej kodu ustawianej w r1 tuz przed wywolaniem.
python3 -I tools/alarm_sites.py FW.bin [out.csv]"""
import os, re, struct, sys, csv
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
B = 0x08010000; RAISE, CLEAR = 0x08025198, 0x08025104
def main(path, out=None):
    raw = open(path, "rb").read(); md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS); md.detail = False
    texts = {}
    tab = 0x0805098C
    for i in range(68):
        c, t = struct.unpack_from("<HH", raw, tab + 4 * i - B); texts[c] = t + 57
    def pl(i):
        p = struct.unpack_from("<I", raw, 0x5BD80 + 4 * i)[0]; o = p - B; s = []
        while True:
            ch = struct.unpack_from("<H", raw, o)[0]
            if ch == 0: break
            s.append(chr(ch)); o += 2
        return "".join(s)
    rows = []
    for tgt, kind in ((RAISE, "raise"), (CLEAR, "clear")):
        for i in range(0, len(raw) - 3, 2):
            h1, h2 = struct.unpack_from("<HH", raw, i)
            if (h1 & 0xF800) == 0xF000 and (h2 & 0xD000) in (0xD000, 0x9000):    # BL / B.W
                s = (h1 >> 10) & 1; j1 = (h2 >> 13) & 1; j2 = (h2 >> 11) & 1; i1 = ~(j1 ^ s) & 1; i2 = ~(j2 ^ s) & 1
                imm = (s << 24) | (i1 << 23) | (i2 << 22) | ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
                if s: imm -= 1 << 25
                if B + i + 4 + imm != tgt: continue
                code = None; ctx = list(md.disasm(raw[max(0, i - 24):i], B + max(0, i - 24)))
                for ins in reversed(ctx):
                    m = re.match(r"r1, #(0x[0-9a-f]+|\d+)$", ins.op_str)
                    if ins.mnemonic in ("movs", "mov", "movw", "mov.w") and m: code = int(m.group(1), 0); break
                rows.append((kind, hex(B + i), code if code is not None else "", pl(texts[code]) if code in texts else ""))
    rows.sort(key=lambda r: (r[2] == "", r[2] if r[2] != "" else 0, r[0]))
    if out:
        with open(out, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f); w.writerow(["kind", "site_runtime", "alarm_code", "text_pl"]); w.writerows(rows)
    return rows
if __name__ == "__main__":
    r = main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    for x in r: print(*x, sep="\t")
