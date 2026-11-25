#!/usr/bin/env python3
"""ETAP B: kodowanie zapisu z panelu. Dla kazdego wiersza listy: otwiera dialog (lub przelacznik), zmienia wartosc o jeden krok i zatwierdza OK, po czym czyta ramke, ktora PANEL wysyla na CAN (id 0x584, `42 <idx> 01 <u32>`):
surowa wartosc na magistrali vs wyswietlana (kodowanie: zwykla / flaga +256 / x10). Tylko emulator.
Uzycie: ESTYMA_IDLE_FAST=1 python3 -I tools/write_probe.py L3DIR LC3DIR OUT.json KLUCZ... [WP_ONLY=plik.json]"""
import json, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import ui_session as U, ctor_trace as C, ui_extras as X
from PIL import Image
l3, lc3, out = sys.argv[1:4]; keys = sys.argv[4:]
lab = json.load(open(paths.UI_MODEL / "list_labels_pl.json"))["lists"]; sc = json.load(open(paths.UI_MODEL / "list_scales.json"))["lists"]
res = json.load(open(out)) if os.path.exists(out) else {}
def vis_texts(s, ws):
    ex = X.extract(s, ws)
    return {w["this"]: (w["ay"], w["ax"], ex[w["this"]]["font"], ex[w["this"]]["text"]) for w in ws if ex.get(w["this"], {}).get("cls") == "text" and not ex[w["this"]].get("hidden") and ex[w["this"]].get("text")}
def texts(s, ws, base):
    """teksty dialogu = widoczne teksty, ktorych nie bylo (lub mialy inny napis) przed stukniecieciem"""
    now = vis_texts(s, ws); return sorted(v for k, v in now.items() if base.get(k) != v and v[3].strip())
def open_node(d, idx, kind):
    """swiezy rozruch z menu.state + wejscie w wezel (BEZ wczytywania punktu kontrolnego w srodku sesji - po load_state przewiniecie+stukniecie nie otwiera dialogu)"""
    s = U.UiSession.from_checkpoint(str(paths.FIRMWARE), os.path.join(d, "menu.state"), None); s.wait(120)
    nav = U.ListNav(s); nav.tall = Image.open(os.path.join(d, "menu_tall.png")); nav.rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb")); t = C.Tracer(s); t.log.clear()
    ok = ui_nav.tap_incremental(s, nav, idx) and hex(s.b.rd(s.b.rd(0x20024818))) != "0x808f66c"
    if not ok and idx >= 13:
        s = U.UiSession.from_checkpoint(str(paths.FIRMWARE), os.path.join(d, "menu.state"), None); s.wait(120)
        nav = U.ListNav(s); nav.tall = Image.open(os.path.join(d, "menu_tall.png")); nav.rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb")); t = C.Tracer(s); t.log.clear()
        ok = ui_nav.tap_tail(s, nav, idx, 19)
    if not ok: return None, None, None
    s.wait(700)
    if kind == "settings": s.tap(400, 245, settle=800); s.wait(500)
    return s, nav, t
import ui_nav

import struct, re
DONE = json.load(open(out)) if os.path.exists(out) else {}
dlg = json.load(open(paths.UI_MODEL / "list_dialogs.json"))["lists"]
def frames_since(s, n0):
    r = []
    for f in s.can2.tx[n0:]:
        d = bytes(f["data"])
        if f["id"] == 0x584 and len(d) == 8 and d[0] in (0x42, 0x43, 0x4B, 0x4F, 0x40) and d[3] == 1: r.append(dict(index="0x%04X" % (d[1] | d[2] << 8), cmd=hex(d[0]), raw=struct.unpack("<I", d[4:])[0], hex=d.hex()))
    return r
for key in keys:
    node = sc[key]["node"]; idx, kind = node.split("_", 1); idx = int(idx); d = lc3 if idx in (9, 10) else l3
    DONE.setdefault(key, {})
    for i, r in lab[key]["rows"].items():
        info = (dlg.get(key) or {}).get(i) or {}
        if info.get("kind") not in ("slider", "radio", "nie_otwarto") or "note" in info: continue
        if i in DONE[key] and DONE[key][i].get("done"): continue
        if os.environ.get("WP_ONLY") and i not in json.load(open(os.environ["WP_ONLY"])).get(key, []): continue
        s, nav, t = open_node(d, idx, kind)
        if s is None: DONE[key][i] = dict(status="NIE_WESZLO_W_WEZEL", done=True); json.dump(DONE, open(out, "w"), ensure_ascii=False, indent=1); continue
        rd = s.b.rd
        def abs_y(a):
            y = 0
            for _ in range(12):
                if not (0x20000000 <= a < 0x20030000): break
                v = rd(a + 6, 2); y += v - 65536 if v > 32767 else v; a = rd(a + 0x14)
            return y
        ws0 = C.widget_table(s, t); ex0 = X.extract(s, ws0)
        cand = [w for w in ws0 if ex0.get(w["this"], {}).get("cls") == "text" and ex0[w["this"]].get("text") == r["label_pl"] and w["ax"] < 100]
        if not cand: DONE[key][i] = dict(status="BRAK_WIDGETU", done=True); json.dump(DONE, open(out, "w"), ensure_ascii=False, indent=1); continue
        la = int(cand[0]["this"], 16); ok = False
        for _ in range(40):
            y = abs_y(la) + 12
            if 55 <= y <= 255: ok = True; break
            if y > 255:
                if not s.drag_until_change(240, 235, 240, 175, attempts=4, ticks=240, pause_end=160): break
            elif not s.drag_until_change(240, 100, 240, 160, attempts=4, ticks=240, pause_end=160): break
        if not ok: DONE[key][i] = dict(status="NIE_DOSZEDL", done=True); json.dump(DONE, open(out, "w"), ensure_ascii=False, indent=1); continue
        s.wait(3000); pid = r["pid"]; pidn = int(pid, 16); n0 = len(s.can2.tx); rec = dict(label=r["label_pl"], pid=pid, dialog=info.get("kind"), done=True)
        before = vis_texts(s, C.widget_table(s, t))
        if info["kind"] == "slider":
            for _try in range(2):
                s.tap(400, abs_y(la) + 12, settle=900); s.wait(400)
                tx = texts(s, C.widget_table(s, t), before)
                if any(x[3] == r["label_pl"] for x in tx): break
            big = [x for x in tx if x[2] >= 4]; v0 = big[0][3] if big else None
            s.tap(297, 205, settle=500); s.wait(300); b2 = [x for x in texts(s, C.widget_table(s, t), before) if x[2] >= 4]; v1 = b2[0][3] if b2 else None
            if v1 == v0: s.tap(142, 205, settle=500); s.wait(300); b2 = [x for x in texts(s, C.widget_table(s, t), before) if x[2] >= 4]; v1 = b2[0][3] if b2 else None
            s.tap(415, 228, settle=900); s.wait(1500); rec.update(shown_before=v0, shown_after=v1)
        elif info["kind"] == "radio":
            s.tap(400, abs_y(la) + 12, settle=900); s.wait(500); s.tap(120, 125, settle=500); s.wait(300); s.tap(415, 228, settle=900); s.wait(1500)
        else:      # przelacznik / licznik: jedno stukniecie w wartosc
            s.tap(430, abs_y(la) + 12, settle=900); s.wait(1500)
        fr = frames_since(s, n0); mine = [f for f in fr if int(f["index"], 16) == pidn]
        rec["frames_all"] = fr[:6]; rec["frame"] = mine[0] if mine else None; rec["frame_raw"] = mine[0]["raw"] if mine else None
        DONE[key][i] = rec; json.dump(DONE, open(out, "w"), ensure_ascii=False, indent=1)
        print(key, i, r["label_pl"][:28], rec.get("shown_before"), rec.get("shown_after"), "->", rec["frame_raw"], flush=True)
