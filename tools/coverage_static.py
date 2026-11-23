#!/usr/bin/env python3
"""PASS 55: pokrycie funkcji z ROZPOZNAWANIEM KODU: rekurencyjny disasm od korzeni (wektory, odczytane z flash wskazniki-funkcje w tablicach vtable, cele BL z kodu osiagalnego, poczatki wykonanych blokow).
Odsiewa falszywe 'funkcje' = cele BL zdekodowane z danych. Wykonane = poczatek funkcji w zbiorze blokow z cov_*.json.
python3 -I tools/coverage_static.py FW.bin OUT.csv COV_DIR_OR_JSON [...]"""
import glob, json, os, struct, sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS, CS_OP_IMM, CS_GRP_JUMP, CS_GRP_RET, CS_GRP_CALL
B = 0x08010000; CODE_END = 0x08076000
def main(fw, out, srcs):
    raw = open(fw, "rb").read(); N = min(len(raw), CODE_END - B)
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS); md.detail = True
    seen = set(); 
    for s in srcs:
        for f in (glob.glob(os.path.join(s, "cov_*.json")) if os.path.isdir(s) else [s]): seen.update(a & ~1 for a in json.load(open(f)))
    roots = {}                       # addr -> zrodlo
    reach_only = set(seen)            # wykonane bloki: tylko do odkrywania celow BL w kodzie osiagalnym, NIE liczone jako funkcje
    # wektory
    for i in range(0, 0x200, 4):
        v = struct.unpack_from("<I", raw, i)[0]
        if v & 1 and B <= v < CODE_END: roots.setdefault(v & ~1, "vector")
    # wskazniki-funkcje w tablicach: >=3 kolejne odd-adresy w zakresie kodu (vtable)
    run = []
    for i in range(0, len(raw) - 3, 4):
        v = struct.unpack_from("<I", raw, i)[0]
        if v & 1 and B <= v < CODE_END: run.append((i, v & ~1))
        else:
            if len(run) >= 3:
                for _, a in run: roots.setdefault(a, "vtable")
            run = []
    called = set(); visited = {}; funcs = {}         # funcs: entry -> (n_instr, has_ret)
    work = sorted(set(roots) | reach_only)
    def cov_ok(a): return B <= a < B + N and a % 2 == 0
    while work:
        e = work.pop()
        if e in funcs or -e in funcs or not cov_ok(e): continue
        stack = [e]; n = 0; ret = False; local = set(); bad = False
        while stack:
            a = stack.pop()
            while cov_ok(a) and a not in local:
                ins = list(md.disasm(raw[a - B:a - B + 4], a, 1))
                if not ins: bad = (n == 0) or bad; break
                i = ins[0]; local.add(a); n += 1
                if CS_GRP_RET in i.groups or (i.mnemonic.startswith("pop") and "pc" in i.op_str) or i.mnemonic in ("bx",) or (i.mnemonic.startswith("ldr") and "pc" in i.op_str.split(",")[0]): ret = True; break
                if CS_GRP_JUMP in i.groups or CS_GRP_CALL in i.groups:
                    if i.operands and i.operands[0].type == CS_OP_IMM:
                        t = i.operands[0].imm & ~1
                        if CS_GRP_CALL in i.groups or i.mnemonic in ("b.w", "b") and not i.cc:
                            if CS_GRP_CALL in i.groups: work.append(t); called.add(t)
                            else: stack.append(t)
                        else: stack.append(t)                      # warunkowy skok: obie galezie
                    if i.mnemonic in ("b", "b.w") and CS_GRP_CALL not in i.groups and i.cc in (0, 15): ret = True; break      # bezwarunkowy skok konczy sciezke
                    if i.mnemonic in ("cbz", "cbnz"): pass
                a += i.size
        if n >= 3 and not bad and (e not in reach_only or e in roots or e in called): funcs[e] = (n, ret)
        elif e in reach_only: funcs.setdefault(-e, (n, ret))   # zapamietaj (ujemny klucz) zeby nie przetwarzac ponownie
    rows = [(a, n, ret, a in seen) for a, (n, ret) in sorted(funcs.items()) if a > 0]
    with open(out, "w") as f:
        f.write("func,instr,has_ret,executed,source\n")
        for a, n, ret, ex in rows: f.write("0x%08X,%d,%d,%d,%s\n" % (a, n, ret, ex, roots.get(a, "bl")))
    ex = sum(1 for r in rows if r[3]); print("funkcje (rozpoznany kod):", len(rows), "| wykonane:", ex, "(%.1f%%)" % (100 * ex / max(1, len(rows))), "| niewykonane:", len(rows) - ex)
if __name__ == "__main__": main(sys.argv[1], sys.argv[2], sys.argv[3:])
