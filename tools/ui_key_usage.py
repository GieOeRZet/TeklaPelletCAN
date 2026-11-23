#!/usr/bin/env python3
"""PASS 52: mapa uzycia kluczy UI (model_get 0x08046FF2) w kodzie: dla kazdego BL 0x08046FF2 szuka stalej r1 (klucz) tuz przed wywolaniem.
Laczy z resolver_t1/t2 (klucz -> PID -> nazwa). python3 -I tools/ui_key_usage.py FW.bin DATA_DIR OUT.csv"""
import csv, os, re, struct, sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
B = 0x08010000; GET = 0x08046FF2
def main(fw, data, out):
    raw = open(fw, "rb").read(); md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
    res = {}
    for fn in ("resolver_t1.csv", "resolver_t2.csv"):
        for r in csv.DictReader(open(os.path.join(data, fn), encoding="utf-8")):
            res.setdefault(int(r["ui_key"], 16), (fn[9:11], r["value"], r["name"]))
    sites = {}
    for i in range(0, len(raw) - 3, 2):
        h1, h2 = struct.unpack_from("<HH", raw, i)
        if (h1 & 0xF800) != 0xF000 or (h2 & 0xD000) != 0xD000: continue
        s = (h1 >> 10) & 1; j1 = (h2 >> 13) & 1; j2 = (h2 >> 11) & 1; i1 = ~(j1 ^ s) & 1; i2 = ~(j2 ^ s) & 1
        imm = (s << 24) | (i1 << 23) | (i2 << 22) | ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
        if s: imm -= 1 << 25
        if B + i + 4 + imm != GET: continue
        key = None
        for ins in reversed(list(md.disasm(raw[max(0, i - 16):i], B + max(0, i - 16)))):
            m = re.match(r"r1, #(0x[0-9a-f]+|\d+)$", ins.op_str)
            if ins.mnemonic in ("movs", "mov", "movw", "mov.w") and m: key = int(m.group(1), 0); break
        sites.setdefault(key, []).append(B + i)
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(["ui_key", "table", "pid", "name", "sites", "first_site"])
        for k in sorted(sites, key=lambda x: (x is None, x)):
            r = res.get(k, ("", "", "")) if k is not None else ("", "", "(klucz nie-stala)")
            w.writerow(["" if k is None else "0x%04X" % k, r[0], r[1], r[2], len(sites[k]), hex(sites[k][0])])
    print("klucze:", len(sites), "wywolan:", sum(len(v) for v in sites.values()))
if __name__ == "__main__": main(*sys.argv[1:4])
