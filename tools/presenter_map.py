#!/usr/bin/env python3
"""PASS 58: statyczna mapa prezenterow: wszystkie wywolania model_get (0x08046FF2) z kluczem UI -> PID/nazwa oraz nastepujacy BL (setter widoku). Dla settera: ciagi formatow (adr/ldr pc),
dzielenie przez 10 (magiczna stala 0x66666667), stale przesuniec widgetow (movw rX,#0x....). Klastry = funkcje-prezentery (odleglosc miedzy wywolaniami < 0x300).
python3 -I tools/presenter_map.py FW.bin DATA_DIR OUT.csv"""
import csv, os, re, struct, sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
B = 0x08010000; GET = 0x08046FF2
def main(fw, data, out):
    raw = open(fw, "rb").read(); md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
    res = {}
    for fn in ("resolver_t1.csv", "resolver_t2.csv"):
        for r in csv.DictReader(open(os.path.join(data, fn), encoding="utf-8")): res.setdefault(int(r["ui_key"], 16), (r["value"], r["name"]))
    def bl_target(i):
        h1, h2 = struct.unpack_from("<HH", raw, i)
        if (h1 & 0xF800) != 0xF000 or (h2 & 0xD000) != 0xD000: return None
        s = (h1 >> 10) & 1; j1 = (h2 >> 13) & 1; j2 = (h2 >> 11) & 1; i1 = ~(j1 ^ s) & 1; i2 = ~(j2 ^ s) & 1
        imm = (s << 24) | (i1 << 23) | (i2 << 22) | ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
        if s: imm -= 1 << 25
        return B + i + 4 + imm
    sites = [B + i for i in range(0, len(raw) - 3, 2) if bl_target(i) == GET]
    cl = []; cur = []
    for a in sites:
        if cur and a - cur[-1] > 0x300: cl.append(cur); cur = []
        cur.append(a)
    if cur: cl.append(cur)
    def cstr(a):
        try:
            o = a - B; e = raw.index(b"\0", o); s = raw[o:e]
            return s.decode("ascii") if 1 <= len(s) < 40 and all(32 <= c < 127 for c in s) else None
        except Exception: return None
    def analyze_setter(t):
        info = dict(fmts=set(), div10=False, offs=set()); code = list(md.disasm(raw[t - B:t - B + 0x180], t))
        for i in code:
            if i.mnemonic in ("pop", "pop.w") and "pc" in i.op_str: break
            m = re.match(r"r\d, #(0x[0-9a-f]+)$", i.op_str)
            if i.mnemonic in ("movw", "mov.w") and m and 0x100 < int(m.group(1), 16) < 0x8000: info["offs"].add(m.group(1))
            if "0x66666667" in i.op_str: info["div10"] = True
            if i.mnemonic.startswith("addw") and "pc" in i.op_str:
                v = ((i.address + 4) & ~3) + int(i.op_str.split("#")[1], 16); s = cstr(v)
                if s and "%" in s: info["fmts"].add(s)
            m2 = re.match(r"r\d, \[pc, #(0x[0-9a-f]+)\]", i.op_str)
            if i.mnemonic.startswith("ldr") and m2:
                v = struct.unpack_from("<I", raw, ((i.address + 4) & ~3) + int(m2.group(1), 16) - B)[0]
                if v == 0x66666667: info["div10"] = True
        return info
    rows = []
    for k, c in enumerate(cl):
        for a in c:
            code = list(md.disasm(raw[a - 16 - B:a - B], a - 16)); key = None
            for ins in reversed(code):
                m = re.match(r"r1, #(0x[0-9a-f]+|\d+)$", ins.op_str)
                if ins.mnemonic in ("movs", "mov", "movw", "mov.w") and m: key = int(m.group(1), 0); break
            nxt = list(md.disasm(raw[a + 4 - B:a + 40 - B], a + 4)); setter = None
            for ins in nxt:
                if ins.mnemonic in ("bl", "b.w") and ins.op_str.startswith("#"):
                    t = int(ins.op_str[1:], 16)
                    if t != GET: setter = t; break
            info = analyze_setter(setter) if setter else dict(fmts=set(), div10=False, offs=set())
            r = res.get(key, ("", "")) if key is not None else ("", "")
            rows.append((k, hex(c[0]), hex(a), "" if key is None else "0x%04X" % key, r[0], r[1], hex(setter) if setter else "", "|".join(sorted(info["fmts"])), int(info["div10"]), "|".join(sorted(info["offs"]))))
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(["presenter_cluster", "cluster_start", "site", "ui_key", "pid", "name", "setter", "formats", "div10", "widget_offsets"]); w.writerows(rows)
    print("klastry prezenterow:", len(cl), "wywolan get:", len(sites))
if __name__ == "__main__": main(*sys.argv[1:4])
