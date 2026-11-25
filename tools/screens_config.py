#!/usr/bin/env python3
"""Co pojawia sie w EKRANACH i LISTACH NASTAW przy jakiej konfiguracji: dla kombinacji (0x2105,0x2106,0x2107,0x2108) jeden rozruch, poziom 3, dla kazdego wiersza MENU
(Kociol, Palnik, Ogrzewanie 1, CWU, Solary, Bufor) wejscie w ekran i w nastawy, odczyt podpisu widocznych widgetow z RAM (rect, klasa, bitmapa, id tekstu - bez wartosci).
Wiersz w MENU znajdowany po napisie etykiety (polozenie z RAM), przewijanie bez wczytywania punktow kontrolnych. Wynik: JSON {kombinacja: {cel: {screen:[...], settings:[...]}}}.
Uzycie: ESTYMA_IDLE_FAST=1 python3 -I tools/screens_config.py OUT.json COMBO ...   (COMBO = 2105,2106,2107,2108)"""
import json, os, sys, unicodedata, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import ui_session as U, ctor_trace as C, ui_extras as X
out = sys.argv[1]; res = json.load(open(out)) if os.path.exists(out) else {}
TARGETS = [("kociol", "Kocioł"), ("palnik", "Palnik"), ("co1", "Ogrzewanie obwód 1"), ("cwu", "Ciepła woda użytkowa"), ("solary", "Solary"), ("bufor", "Bufor")]
def sig(s, ws):
    ex = X.extract(s, ws); r = set()
    for w in ws:
        e = ex.get(w["this"], {})
        if e.get("hidden") or w["w"] <= 0 or w["h"] <= 0 or w["w"] > 479 or w["ay"] > 900: continue
        r.add((tuple([w["ax"], w["ay"] % 10000, w["w"], w["h"]]), e.get("cls"), e.get("bmp") if e.get("bmp") is not None else w.get("bitmap_id"), e.get("tid")))
    return sorted(r, key=str)
for cb in sys.argv[2:]:
    if cb in res: continue
    a, b, c, d = [int(x) for x in cb.split(",")]; cfg = dict(zip((0x2105, 0x2106, 0x2107, 0x2108), (a, b, c, d)))
    s = U.UiSession(str(paths.FIRMWARE), None); t = C.Tracer(s); s.boot(500)
    for p, x in cfg.items(): s.set_local(p, x)
    s.set_access(3); s.wait(300); s.tap(34, 235, settle=700); s.wait(600); rd = s.b.rd; res[cb] = {}
    def abs_y(ad):
        y = 0
        for _ in range(12):
            if not (0x20000000 <= ad < 0x20030000): break
            v = rd(ad + 6, 2); y += v - 65536 if v > 32767 else v; ad = rd(ad + 0x14)
        return y
    for key, title in TARGETS:
        ws = C.widget_table(s, t); ex = X.extract(s, ws)
        cand = [w for w in ws if ex.get(w["this"], {}).get("cls") == "text" and not ex[w["this"]].get("hidden") and ex[w["this"]].get("text", "").startswith(title) and 55 <= w["ax"] <= 90 and w["ay"] >= 46]
        if not cand: res[cb][key] = None; continue
        la = int(cand[0]["this"], 16); ok = False
        for _ in range(30):
            y = abs_y(la) + 14
            if 60 <= y <= 250: ok = True; break
            if y > 250: s.drag_until_change(240, 235, 240, 175, attempts=4, ticks=240, pause_end=160)
            else: s.drag_until_change(240, 100, 240, 200, attempts=4, ticks=240, pause_end=160)
        if not ok: res[cb][key] = "NIE_DOSZEDL"; continue
        s.wait(3000); s.tap(240, abs_y(la) + 14, settle=800); s.wait(700)
        ws1 = C.widget_table(s, t); sc = sig(s, ws1); s.tap(400, 245, settle=800); s.wait(600); ws2 = C.widget_table(s, t); st = sig(s, ws2)
        res[cb][key] = dict(screen=sc, settings=st, view_screen=hex(rd(rd(0x20024818))))
        s.tap(65, 22, settle=800); s.wait(500); s.tap(65, 22, settle=800); s.wait(500)      # wstecz: nastawy -> ekran -> MENU
        s.wait(1500)
        json.dump(res, open(out, "w"), ensure_ascii=False); print(cb, key, len(sc), len(st), flush=True)
