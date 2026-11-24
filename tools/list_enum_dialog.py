#!/usr/bin/env python3
"""PASS 70: etykiety opcji wyliczen listy: stukniecie wiersza typu enum -> dialog radio; odczyt ID tekstow czytanych przez firmware przy rysowaniu dialogu (hak na tablice tekstow
dodany PRZED uruchomieniem, enable_trace) minus ID czytane bez stukniecia (linia bazowa). Wynik: id tekstow (PL) i napisy PL/EN.
Uzycie: ESTYMA_IDLE_FAST=1 python3 -I tools/list_enum_dialog.py FW DIR INV NODE LISTKEY OUT.json ROW_IDX [ROW_IDX ...]"""
import json, os, pickle, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, action_probe as AP
fw, d, inv_path, node, key, out = sys.argv[1:7]; idxs = [int(x) for x in sys.argv[7:]]
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analiza_archiwum", "FW2213TK-2026-11-22", "data", "ui_model")
meta = {r["idx"]: r for r in [v for k, v in json.load(open(os.path.join(D, "lists.json")))["lists"].items() if k.startswith(key + "|")][0]}
sc = json.load(open(os.path.join(D, "list_scales.json")))["lists"][key]["rows"]; sc = {r["idx"]: r for r in sc}
RAW = open(fw, "rb").read()
def txt(lang, i):
    tb = U.UiSession.TEXT_LANG_PTRS[lang] - 57 * 4 - 0x08010000
    try:
        p = struct.unpack_from("<I", RAW, tb + 4 * i)[0] - 0x08010000; r = []
        while len(r) < 80:
            c = struct.unpack_from("<H", RAW, p)[0]
            if c == 0: break
            r.append(chr(c)); p += 2
        return "".join(ch for ch in r if ch.isprintable())
    except Exception: return "?"
rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb"))
s = U.UiSession.from_checkpoint(fw, os.path.join(d, "menu.state"), None); st = AP.enter_node(s, d, rows, node)
s.enable_trace(); s.b.load_state(st); s.wait(600)
rd = s.b.rd; S16 = lambda a: rd(a, 2) - 65536 if rd(a, 2) > 32767 else rd(a, 2)
def abs_y(a):
    y = 0
    for _ in range(12):
        if not (0x20000000 <= a < 0x20030000): break
        y += S16(a + 6); a = rd(a + 0x14)
    return y
inv = {n["node"]: n for n in json.load(open(inv_path))}[node]; W = {w["this"]: w for w in inv["widgets"]}
res = json.load(open(out)) if os.path.exists(out) else {}
for idx in idxs:
    r = sc.get(idx); vw = [w for w in (r or {}).get("control", {}).get("widgets", []) if w["role"] == "text"]
    if not vw: print(idx, "brak widgetu wartosci"); continue
    ay = vw[0]["ay"]
    base_ids = set()
    s.b.load_state(st); s.wait(300); s.trace["text"].clear(); s.wait(300); base_ids = {i for (l, i) in s.trace["text"] if l == 0}
    s.b.load_state(st); s.wait(300)
    # przewin do wiersza: znajdz widget po polozeniu absolutnym (tekst w slocie)
    tw = [w for w in inv["widgets"] if w["role"] == "text" and w["ax"] == vw[0]["ax"] and w["ay"] == ay]
    a = int(tw[0]["this"], 16) if tw else None
    for _ in range(14):
        y = abs_y(a) if a else 0
        if 70 <= y <= 225: break
        s.drag_until_change(240, 230, 240, 80, attempts=4, ticks=240, pause_end=160) if y > 225 else s.drag_until_change(240, 80, 240, 230, attempts=4, ticks=240, pause_end=160)
    y = abs_y(a); s.trace["text"].clear(); s.tap(vw[0]["ax"] + 15, y + 20, settle=900); s.wait(400)
    ids = sorted({i for (l, i) in s.trace["text"] if l == 0} - base_ids)
    res[str(idx)] = dict(name_en=meta[idx]["name_en"], pid=meta[idx]["pid"], row_y=y, new_text_ids=ids, pl={i: txt(0, i) for i in ids}, en={i: txt(1, i) for i in ids}); json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
    s.shot("enum_%s" % idx) if s.out else None
    print(idx, meta[idx]["name_en"], [(i, res[str(idx)]["pl"][i]) for i in ids][:12], flush=True)
