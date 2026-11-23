#!/usr/bin/env python3
"""NewEstyma PASS 46: automat eksploracji UI dla zadanego POZIOMU DOSTEPU (0..3).
python3 -I tools/ui_explore.py FW2213TK_kopia.bin outdir --level N [--only nazwa,nazwa] [--no-gear]
Ustawia konfiguracje pelna (0x2105=4, 0x2106..0x2108=1) i poziom dostepu (MODEL+0x158), skleja liste MENU (ListNav -> menu_tall.png),
wchodzi w kazdy wiersz ze strzalka i robi zrzuty z przewijaniem (`<nazwa>_<n>.png`), a dla ekranow urzadzen takze strony USTAWIEN (zebatka w prawym dolnym rogu: `<nazwa>_ust_<n>.png`).
Wiersze z kontrolkami wbudowanymi (PIN, Jezyk, Alarm dzwiekowy) sa POMIJANE, zeby nie zmieniac ustawien. Nazwy wierszy wg kolejnosci przy pelnej konfiguracji (PASS 45/46)."""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U
ROWS = ["kociol", "palnik", "co1", "co2", "co3", "co4", "cwu", "solar", "bufor", "alarmy", "info", "konfiguracja", "pin", "jezyk", "alarm_dzw", "test_wyjsc", "statystyki", "siec", "internet"]
SKIP = {"pin", "jezyk", "alarm_dzw"}
GEAR = {"kociol", "palnik", "co1", "co2", "co3", "co4", "cwu", "solar", "bufor"}
def explore(binpath, out, level, only=None, gear=True):
    s = U.UiSession(binpath, out); s.boot(500)
    for pid, v in ((0x2105, 4), (0x2106, 1), (0x2107, 1), (0x2108, 1)): s.set_local(pid, v)
    s.set_access(level); s.wait(300); s.shot("home"); s.tap(34, 235, settle=700)
    nav = U.ListNav(s); rows = nav.build(); nav.tall.save(os.path.join(out, "menu_tall.png"))
    with open(os.path.join(out, "rows.txt"), "w") as f:
        for r in rows: f.write("%d %s chevron=%d\n" % (r["idx"], ROWS[r["idx"]] if r["idx"] < len(ROWS) else "?", r["chevron"]))
    for r in rows:
        nm = ROWS[r["idx"]] if r["idx"] < len(ROWS) else "row%d" % r["idx"]
        if nm in SKIP or (only and nm not in only): continue
        if not nav.tap_row(r["idx"]): print("nie udalo sie wejsc:", nm, flush=True); continue
        s.scroll_capture(nm, dy=120)
        if gear and nm in GEAR:
            s.tap(400, 245, settle=800); s.scroll_capture(nm + "_ust", dy=120); s.tap(50, 22, settle=700)
        s.tap(50, 22, settle=700); print("ok", nm, flush=True)
    return s
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("bin"); ap.add_argument("out"); ap.add_argument("--level", type=int, default=0)
    ap.add_argument("--only", default=""); ap.add_argument("--no-gear", action="store_true"); a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    explore(a.bin, a.out, a.level, set(a.only.split(",")) if a.only else None, not a.no_gear); print("DONE", a.out)
