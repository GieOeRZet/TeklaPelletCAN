#!/usr/bin/env python3
"""Generyczny ekstraktor semantyki ekranow z binarki: dla kazdego presentera (funkcja czytajaca model FUN_08036ff2) wyciaga
klucz UI -> PID -> setter widoku -> sterowane widgety (offset widoku = view_off z inwentarza widgetow) + stale setterow
(porownania, id bitmap, kolory, formaty tekstu, tabele DAT). Wynik: JSON per ekran + lista widgetow dynamicznych/statycznych.
Uzycie: python3 tools/presenter_widget_map.py OUT.json        (tylko pliki repo + FW2213TK_kopia.bin; bez emulatora)
Adresy: decompiled.c = runtime - 0x10000 (adres w pliku bin = adres decompiled - 0x08000000)."""
import csv, json, os, re, struct, sys, collections

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
D = os.path.join(ROOT, "analiza_archiwum", "FW2213TK-2026-11-22", "data")
out = sys.argv[1]
BIN = open(os.path.join(ROOT, "FW2213TK_kopia.bin"), "rb").read()
src = open(os.path.join(ROOT, "firmware", "FW2213TK-ghidra", "decompiled.c"), encoding="utf-8", errors="replace").read()
parts = re.split(r"\n// (0[0-9a-f]{7})\n", src)
F = {parts[i]: parts[i + 1] for i in range(1, len(parts), 2)}
T2 = {int(r["ui_key"], 16): r for r in csv.DictReader(open(os.path.join(D, "cg_ui_key_pid_t2_full.csv")))}
T1 = {int(r["ui_key"], 16): r for r in csv.DictReader(open(os.path.join(D, "cg_ui_key_pid_t1_full.csv")))}
PM = {r["pid"].lower() for r in csv.DictReader(open(os.path.join(D, "pid_matrix_655.csv"), encoding="utf-8-sig"))}
TT = {int(r["typedtext_id_relative"]): r["pl_text"] for r in csv.DictReader(open(os.path.join(D, "typedtext_database.csv"), encoding="utf-8"))}

# presenter -> (plik inwentarza, wezel)
SCREENS = {
    "08031ccc": ("widgets_inv_pass65_home_L0.json", "home", "HOME"),
    "0803cb2c": ("widgets_inv_pass65_L1_all.json", "0_screen", "KOCIOL"),
    "0803cf54": ("widgets_inv_pass65_L1_all.json", "1_screen", "PALNIK"),
    "0803d37c": ("widgets_inv_pass65_L1_all.json", "2_screen", "OGRZEWANIE"),
    "0803d744": ("widgets_inv_pass65_L1_all.json", "6_screen", "CWU"),
    "0803e45c": ("widgets_inv_pass65_cascade_fuelstore_L0.json", "9_screen", "KASKADA"),
    "0803e2e8": ("widgets_inv_pass65_cascade_fuelstore_L0.json", "10_screen", "MAGAZYN"),
    "0803e148": ("widgets_inv_pass71_solary_bufor.json", "7_screen", "SOLARY"),
    "0803df78": ("widgets_inv_pass71_solary_bufor.json", "8_screen", "BUFOR"),
}


def key_pid(k):
    r = T2.get(k) or T1.get(k)
    if not r: return (None, None)
    if r["pid"].lower() not in PM: return ("poza macierza 655: " + r["pid"][2:], r["name"])   # PID czytany przez UI, ale nieobecny w katalogu 655
    return (r["pid"], r["name"])


def cstr(addr):
    o = addr - 0x08000000
    if not (0 <= o < len(BIN)): return None
    e = BIN.find(b"\0", o, o + 80)
    return BIN[o:e].decode("latin-1") if e > o else None


def table(addr, n=12):
    o = addr - 0x08000000
    if not (0 <= o + 2 * n < len(BIN)): return None
    return list(struct.unpack("<%dH" % n, BIN[o:o + 2 * n]))


def setter_info(fn):
    b = F.get(fn)
    if b is None: return {}
    info = {}
    cmp_ = sorted({int(m, 0) for m in re.findall(r"(?:==|!=|<|>|<=|>=)\s*(0x[0-9a-fA-F]+|\d+)\b", b)})
    if cmp_: info["porownania"] = cmp_[:16]
    strs = {}
    for m in re.finditer(r"\bs_([A-Za-z0-9_]+)_(0[0-9a-f]{7})\b", b):
        s = cstr(int(m.group(2), 16))
        if s is not None: strs[m.group(2)] = s
    if strs: info["formaty"] = sorted(set(strs.values()))
    tabs = {}
    for m in re.finditer(r"\bDAT_(0[0-9a-f]{7})\b", b):
        a = int(m.group(1), 16)
        if 0x08020000 <= a < 0x08200000 and ("&DAT_" + m.group(1)) in b:
            t = table(a)
            if t: tabs[m.group(1)] = t
    if tabs: info["tabele_u16"] = tabs
    bm = sorted({int(m, 0) for m in re.findall(r"(?:local_\w+(?:\[0\])?|uVar\d+)\s*=\s*(0x[0-9a-fA-F]{1,2}|\d{1,3});", b) if 0 < int(m, 0) < 189})
    if bm and ("FUN_080307bc" in b or "FUN_0803079a" in b or "FUN_0802ddca" in b): info["bitmapy_w_kodzie"] = bm
    if "FUN_08030268" in b: info["kolor"] = "tak (FUN_08030268 rgb)"
    offs = sorted({int(m, 16) for m in re.findall(r"param_1 \+ (0x[0-9a-fA-F]+)", b)})
    info["offsety"] = offs
    return info


def widgets_for(offs, inv):
    res = []
    for o in offs:
        for delta, role in ((0, "widget"), (0x25, "widget.visible"), (0x26, "widget.id/alpha")):
            w = inv.get(o - delta)
            if w:
                res.append(dict(offset=hex(o), rola=role, view_off=hex(w["view_off"]), rect=[w["x"], w["y"], w["w"], w["h"]], bitmap=w.get("bitmap_id"), text=w.get("text_id"), vptr=w.get("vptr")))
                break
    return res


def analyse(fn, inv):
    b = F[fn]
    var2key = {}
    items = []
    for stmt in re.split(r";\s*\n", b):
        for m in re.finditer(r"(\w+)\s*=\s*FUN_08036ff2\([^,]+,\s*(0x[0-9a-fA-F]+|\d+)\)", stmt):
            var2key[m.group(1)] = int(m.group(2), 0)
        m = re.search(r"FUN_(0[0-9a-f]{7})\(\*\(undefined4 \*\)\(param_1 \+ 0xc\)(.*)\)", stmt, re.S)
        if m and "FUN_08036ff2" not in m.group(2):
            setter, args = m.group(1), m.group(2)
            ks = []
            for v in re.findall(r"\b(\w+)\b", args):
                if v in var2key: ks.append(var2key[v])
            for k in re.findall(r"FUN_08036ff2\([^,]+,\s*(0x[0-9a-fA-F]+|\d+)\)", stmt): ks.append(int(k, 0))
            info = setter_info(setter)
            pids = []
            for k in dict.fromkeys(ks):
                p, n = key_pid(k)
                if p and p.startswith("poza"): pids.append(dict(key=hex(k), pid_poza_macierza_655=p.split(": ")[1], name=n))
                else: pids.append(dict(key=hex(k), pid=p, name=n))
            ws = widgets_for(info.get("offsety", []), inv)
            items.append(dict(setter="0x" + setter, args=args.strip(", ")[:60], pids=pids, widgety=ws, **{k: v for k, v in info.items() if k != "offsety"}))
    return items


res = {"schema_version": "1.0", "evidence": "STRONG (statyczna analiza decompiled.c + inwentarze widgetow z emulatora; powiazanie setter->widget przez offset widoku)", "ekrany": {}}
for pres, (invf, node, name) in SCREENS.items():
    inv = {}
    total = 0
    for n in json.load(open(os.path.join(D, invf))):
        if str(n.get("node")) == node:
            for w in n["widgets"]:
                if "view_off" in w: inv[w["view_off"]] = w
            total = len(n["widgets"])
    items = analyse(pres, inv)
    ctrl = {w["view_off"] for it in items for w in it["widgety"]}
    res["ekrany"][name] = dict(presenter="0x" + pres, widgetow_na_ekranie=total, sterowane_przez_presenter=len(ctrl), settery=items)
json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
for k, v in res["ekrany"].items(): print(k, v["presenter"], "settery:", len(v["settery"]), "widgety sterowane:", v["sterowane_przez_presenter"], "/", v["widgetow_na_ekranie"])
