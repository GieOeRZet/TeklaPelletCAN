#!/usr/bin/env python3
"""1:1: dla kazdego wiersza listy nastaw (z list_labels_pl.json: slot -> pozycja) otwiera dialog edycji (stukniecie w wartosc po przewinieciu listy z sumowaniem przesuniec),
odczytuje z RAM: rodzaj (suwak liczbowy / radio z opcjami), tytul PL, min/max/wartosc, krok (+ raz, - raz). Wynik: ui_model/list_dialogs.json {klucz: {idx: {...}}}.
Uzycie: ESTYMA_IDLE_FAST=1 python3 -I tools/list_dialogs.py L3DIR LC3DIR OUT.json KLUCZ [KLUCZ...]    (klucz np. 0x00)
Tylko w emulatorze; zadnych zapisow do kotla."""
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
for key in keys:
    node = sc[key]["node"]; idx, kind = node.split("_", 1); idx = int(idx); d = lc3 if idx in (9, 10) else l3
    res.setdefault(key, {})
    lists_rows = {str(r["idx"]): r for k2, v2 in json.load(open(paths.UI_MODEL / "lists.json"))["lists"].items() if k2.split("|")[0] == key for r in v2}
    for i, r in lab[key]["rows"].items():
        if i in res[key] and res[key][i].get("kind") in ("slider", "radio"): continue
        if os.environ.get("LD_ONLY") and i not in json.load(open(os.environ["LD_ONLY"])).get(key, []): continue
        if os.environ.get("LD_KIND") and lists_rows.get(i, {}).get("kind") != os.environ["LD_KIND"]: continue
        s, nav, t = open_node(d, idx, kind)
        if s is None: res[key][i] = dict(status="NIE_WESZLO_W_WEZEL"); json.dump(res, open(out, "w"), ensure_ascii=False, indent=1); print(key, i, "NIE_WESZLO_W_WEZEL", flush=True); continue
        rd = s.b.rd
        def abs_y(a):
            y = 0
            for _ in range(12):
                if not (0x20000000 <= a < 0x20030000): break
                v = rd(a + 6, 2); y += v - 65536 if v > 32767 else v; a = rd(a + 0x14)
            return y
        ws0 = C.widget_table(s, t); ex0 = X.extract(s, ws0)
        cand = [w for w in ws0 if ex0.get(w["this"], {}).get("cls") == "text" and ex0[w["this"]].get("text") == r["label_pl"] and w["ax"] < 100]
        if not cand: res[key][i] = dict(status="BRAK_WIDGETU_ETYKIETY"); json.dump(res, open(out, "w"), ensure_ascii=False, indent=1); print(key, i, "BRAK_WIDGETU_ETYKIETY", flush=True); continue
        la = int(cand[0]["this"], 16); ok = False
        for _ in range(40):
            y = abs_y(la) + 12
            if 55 <= y <= 255: ok = True; break
            if y > 200:
                if not s.drag_until_change(240, 235, 240, 175, attempts=4, ticks=240, pause_end=160): break
            elif not s.drag_until_change(240, 100, 240, 160, attempts=4, ticks=240, pause_end=160): break
        if not ok: res[key][i] = dict(status="NIE_DOSZEDL"); json.dump(res, open(out, "w"), ensure_ascii=False, indent=1); print(key, i, "NIE_DOSZEDL", flush=True); continue
        s.wait(3000)
        before = vis_texts(s, C.widget_table(s, t))
        for _try in range(2):
            s.tap(400, abs_y(la) + 12, settle=900); s.wait(400); ws = C.widget_table(s, t); tx = texts(s, ws, before)
            if any(x[3] == r["label_pl"] for x in tx): break
        rec = dict(label=r["label_pl"], pid=r["pid"], texts=[x[3] for x in tx], fonts=[x[2] for x in tx])
        big = [x for x in tx if x[2] >= 4 and x[3].strip().lstrip("-").replace(".", "").replace(" ", "").isdigit()]
        if big:
            rec["kind"] = "slider"; v0 = big[0][3]
            for nm, (px, py) in (("plus", (297, 205)), ("minus", (142, 205))):
                s.tap(px, py, settle=500); s.wait(250); w2 = C.widget_table(s, t); t2 = sorted(v for v in vis_texts(s, w2).values()); b2 = [x for x in t2 if x[2] >= 4]
                rec[nm] = b2[0][3] if b2 else None
            rec["value0"] = v0
        elif tx: rec["kind"] = "radio"
        else: rec["kind"] = "nie_otwarto"
        res[key][i] = rec; json.dump(res, open(out, "w"), ensure_ascii=False, indent=1); print(key, i, rec["kind"], rec["texts"][:8], rec.get("value0"), rec.get("plus"), rec.get("minus"), flush=True)
