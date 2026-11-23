#!/usr/bin/env python3
"""PASS 52: raport pokrycia funkcji firmware. Funkcje = cele BL/B.W w obrazie (RUNTIME 0x08010000..0x08080000).
Wykonane = poczatki blokow podstawowych zebrane przez UC_HOOK_BLOCK (tools/gate_trace.py -> cov_*.json, tools/coverage_boot.py).
python3 -I tools/coverage_report.py FW.bin out.csv DIR_OR_JSON [...]"""
import glob, json, os, struct, sys
B = 0x08010000; END = 0x08080000
def targets(raw):
    t = {}
    for i in range(0, min(len(raw), END - B) - 3, 2):
        h1, h2 = struct.unpack_from("<HH", raw, i)
        if (h1 & 0xF800) == 0xF000 and (h2 & 0xC000) == 0xC000 and (h2 & 0x1000 or True) and (h2 & 0xD000) in (0xD000, 0x9000):
            s = (h1 >> 10) & 1; j1 = (h2 >> 13) & 1; j2 = (h2 >> 11) & 1; i1 = ~(j1 ^ s) & 1; i2 = ~(j2 ^ s) & 1
            imm = (s << 24) | (i1 << 23) | (i2 << 22) | ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
            if s: imm -= 1 << 25
            a = B + i + 4 + imm
            if B <= a < END and (h2 & 0xD000) == 0xD000: t.setdefault(a & ~1, []).append(B + i)
    return t
def main(fw, out, srcs):
    raw = open(fw, "rb").read(); T = targets(raw); seen = set(); files = []
    for s in srcs:
        for f in (glob.glob(os.path.join(s, "cov_*.json")) if os.path.isdir(s) else [s]):
            files.append(f); seen.update(a & ~1 for a in json.load(open(f)))
    hit = sorted(a for a in T if a in seen); miss = sorted(a for a in T if a not in seen)
    print("pliki pokrycia:", len(files), "| funkcje (cele BL):", len(T), "| wykonane:", len(hit), "(%.1f%%)" % (100 * len(hit) / max(1, len(T))), "| niewykonane:", len(miss))
    with open(out, "w") as f:
        f.write("func_runtime,executed,callers\n")
        for a in sorted(T): f.write("0x%08X,%d,%d\n" % (a, a in seen, len(T[a])))
    return T, seen
if __name__ == "__main__": main(sys.argv[1], sys.argv[2], sys.argv[3:])
