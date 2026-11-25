#!/usr/bin/env python3
"""Etap D: PID-y harmonogramu (PROGRAM) dla kazdego ekranu i dnia - ramka zapisu panelu po zmianie godziny w dialogu dnia (komfort/eco + OK).
Uzycie: ESTYMA_IDLE_FAST=1 python3 -I tools/program_write_probe.py L3DIR OUT.json ROW [ROW ...]   (ROW = wiersz menu: 0 Kociol, 2-5 Ogrzewanie1-4, 6 CWU). Tylko emulator."""
import json, os, pickle, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths, ui_session as U, ctor_trace as C, ui_nav, ui_extras as X
from PIL import Image
d, out = sys.argv[1:3]; rows = [int(x) for x in sys.argv[3:]]
DAYS = ["Pn", "Wt", "Sr", "Cz", "Pt", "Sb", "Nd"]; Y = [65, 120, 175, 230]
FULL = ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"]
def title(s):
    ws = C.widget_table(s, s.tr); ex = X.extract(s, ws)
    return [ex[w["this"]]["text"] for w in ws if w["this"] in ex and ex[w["this"]].get("cls") == "text" and not ex[w["this"]].get("hidden") and ex[w["this"]].get("text") in FULL]
res = json.load(open(out)) if os.path.exists(out) else {}
def frames(s, n0):
    r = []
    for f in s.can2.tx[n0:]:
        b = bytes(f["data"])
        if f["id"] == 0x584 and len(b) == 8 and b[0] in (0x42, 0x43, 0x4B, 0x4F, 0x40) and b[3] == 1: r.append(dict(index="0x%04X" % (b[1] | b[2] << 8), raw=struct.unpack("<I", b[4:])[0], hex=b.hex()))
    return r
def boot(row):
    s = U.UiSession.from_checkpoint(str(paths.FIRMWARE), os.path.join(d, "menu.state"), None); s.wait(120)
    nav = U.ListNav(s); nav.tall = Image.open(os.path.join(d, "menu_tall.png")); nav.rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb")); t = C.Tracer(s); t.log.clear()
    ok = ui_nav.tap_incremental(s, nav, row); s.wait(900); s.tr = t; return s, ok
for row in rows:
    for k, day in enumerate(DAYS):
        key = "row%d_%s" % (row, day)
        if res.get(key, {}).get("done"): continue
        rec = dict(row=row, day=day, frames=[], done=True)
        for attempt in ("comfort", "eco"):
            s, ok = boot(row)
            if not ok: rec.update(status="NIE_WESZLO_W_EKRAN"); break
            s.tap(414, 130, settle=900); s.wait(2500)
            if k >= 3: s.drag_until_change(240, 230, 240, 80, attempts=4, ticks=240, pause_end=160); s.wait(300)
            if k == 6: s.drag_until_change(240, 230, 240, 80, attempts=4, ticks=240, pause_end=160); s.wait(300)
            ys = [Y[k]] if k < 3 else [Y[3], Y[2], Y[1], Y[0]] if k == 6 else [Y[(k - 3 + o) % 4] for o in (0, 1, 2, 3)]
            got = None
            for y in ys:
                s.tap(235, y, settle=900); s.wait(400); tt = title(s)
                if tt and tt[0] == FULL[k]: got = tt[0]; break
                if tt: s.close_ok = True; s, ok = boot(row); s.tap(414, 130, settle=900); s.wait(2500); s.drag_until_change(240, 230, 240, 80, attempts=4, ticks=240, pause_end=160); s.wait(300)
            rec["dialog_title"] = got
            if got is None: rec["status"] = "NIE_TEN_DZIEN"; break
            n0 = len(s.can2.tx)
            s.tap(275 if attempt == "comfort" else 195, 154, settle=500); s.wait(200); s.tap(415, 228, settle=900); s.wait(600)
            fr = frames(s, n0); rec["attempt_" + attempt] = fr
            if fr: rec["frames"] = fr; rec["status"] = "ok"; break
        else: rec["status"] = "BRAK_RAMKI"
        res[key] = rec; json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
        print(key, rec.get("status"), [(f["index"], f["raw"]) for f in rec["frames"]], flush=True)
