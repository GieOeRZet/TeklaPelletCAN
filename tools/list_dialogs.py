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
for key in keys:
    node = sc[key]["node"]; idx, kind = node.split("_", 1); idx = int(idx); d = lc3 if idx in (9, 10) else l3
    s = U.UiSession.from_checkpoint(str(paths.FIRMWARE), os.path.join(d, "menu.state"), None); s.wait(120)
    nav = U.ListNav(s); nav.tall = Image.open(os.path.join(d, "menu_tall.png")); nav.rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb")); t = C.Tracer(s); t.log.clear()
    import ui_nav
    if not ui_nav.tap_incremental(s, nav, idx): print(key, "TAP_FAILED", flush=True); continue
    s.wait(700)
    if kind == "settings": s.tap(400, 245, settle=800); s.wait(500)
    tmp = "/tmp/ld_%s.state" % key.replace("0x", ""); s.checkpoint(tmp); base = lab[key]["base_ay"]; res.setdefault(key, {})
    lists_rows = {str(r["idx"]): r for k2, v2 in json.load(open(paths.UI_MODEL / "lists.json"))["lists"].items() if k2.split("|")[0] == key for r in v2}
    rd = s.b.rd
    def abs_y(a):
        y = 0
        for _ in range(12):
            if not (0x20000000 <= a < 0x20030000): break
            v = rd(a + 6, 2); y += v - 65536 if v > 32767 else v; a = rd(a + 0x14)
        return y
    for i, r in lab[key]["rows"].items():
        if i in res[key]: continue
        if os.environ.get("LD_KIND") and lists_rows.get(i, {}).get("kind") != os.environ["LD_KIND"]: continue
        s.b.load_state(tmp); s.wait(150); ok = False; y = None
        ws0 = C.widget_table(s, t); ex0 = X.extract(s, ws0)
        cand = [w for w in ws0 if ex0.get(w["this"], {}).get("cls") == "text" and ex0[w["this"]].get("text") == r["label_pl"] and w["ax"] < 100]
        if not cand: res[key][i] = dict(status="BRAK_WIDGETU_ETYKIETY"); continue
        la = int(cand[0]["this"], 16)
        for _ in range(40):
            y = abs_y(la) + 12      # polozenie srodka wiersza z RAM (uwzglednia przesuniecie przewijania)
            if 100 <= y <= 200: ok = True; break
            if not s.drag_until_change(240, 235, 240, 175, attempts=4, ticks=240, pause_end=160) if y > 200 else not s.drag_until_change(240, 100, 240, 160, attempts=4, ticks=240, pause_end=160): break
        s.wait(900)      # wygaszenie przewijania (listy recyklingowane)
        before = vis_texts(s, C.widget_table(s, t))
        for _try in range(3):      # pierwsze stukniecie po przewinieciu bywa polykane (zatrzymanie inercji) - powtorz do 3 razy
            s.tap(400, y, settle=900); s.wait(400); ws = C.widget_table(s, t); tx = texts(s, ws, before)
            if any(x[3] == r["label_pl"] for x in tx): break
        rec = dict(label=r["label_pl"], pid=r["pid"], texts=[x[3] for x in tx], fonts=[x[2] for x in tx])
        big = [x for x in tx if x[2] >= 4 and x[3].strip().lstrip("-").replace(".", "").replace(" ", "").isdigit()]
        if big:                                         # dialog z suwakiem: duza wartosc
            rec["kind"] = "slider"; v0 = big[0][3]
            for nm, (px, py) in (("plus", (297, 205)), ("minus", (142, 205))):
                s.tap(px, py, settle=500); s.wait(250); w2 = C.widget_table(s, t); t2 = sorted(v for v in vis_texts(s, w2).values()); b2 = [x for x in t2 if x[2] >= 4]
                rec[nm] = b2[0][3] if b2 else None
            rec["value0"] = v0
        else:
            rec["kind"] = "radio_or_other"
            if os.environ.get("LD_SHOTS"): s.shot().save(os.path.join(os.environ["LD_SHOTS"], "ld_%s_%s.png" % (key, i)))
        res[key][i] = rec; json.dump(res, open(out, "w"), ensure_ascii=False, indent=1); print(key, i, rec.get("kind"), rec["texts"][:6], rec.get("value0"), rec.get("plus"), rec.get("minus"), flush=True)
