#!/usr/bin/env python3
"""NewEstyma PASS 46: automat eksploracji UI dla POZIOMU DOSTEPU (0..3), oparty na punktach kontrolnych.
  python3 -I tools/ui_explore.py FW2213TK_kopia.bin outdir --level N --prepare          # rozruch, konfiguracja, poziom dostepu, MENU na gorze -> menu.state + menu_tall.png + rows.txt
  python3 -I tools/ui_explore.py FW2213TK_kopia.bin outdir --level N --row IDX           # wczytuje menu.state, wchodzi w wiersz IDX, zrzuty (+strony ustawien z zebatki)
  python3 -I tools/ui_explore.py FW2213TK_kopia.bin outdir --level N --all [--workers 8] # prepare + wszystkie wiersze rownolegle
Konfiguracja pelna (0x2105=4, 0x2106..0x2108=1), poziom dostepu zapisany w MODEL+0x158 (FUN_08037E74: PIN 900/999/6154 -> 1/2/3).
Wiersze z kontrolkami wbudowanymi (PIN, Jezyk, Alarm dzwiekowy) sa pomijane (nie zmieniamy ustawien). Tylko ruchy przewijania W GORE (przeciagniecia w dol sa zawodne)."""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U
ROWS = ["kociol", "palnik", "co1", "co2", "co3", "co4", "cwu", "solar", "bufor", "alarmy", "info", "konfiguracja", "pin", "jezyk", "alarm_dzw", "test_wyjsc", "statystyki", "siec", "internet"]
SKIP = {"pin", "jezyk", "alarm_dzw"}
GEAR = {"kociol", "palnik", "co1", "co2", "co3", "co4", "cwu", "solar", "bufor"}
def name(i): return ROWS[i] if i < len(ROWS) else "row%d" % i
def prepare(binpath, out, level):
    os.makedirs(out, exist_ok=True)
    s = U.UiSession(binpath, out); s.boot(500)
    for pid, v in ((0x2105, 4), (0x2106, 1), (0x2107, 1), (0x2108, 1)): s.set_local(pid, v)
    s.set_access(level); s.wait(300); s.shot("home"); s.tap(34, 235, settle=700); s.go_top()
    s.checkpoint(os.path.join(out, "menu.state"))                      # MENU na gorze
    nav = U.ListNav(s); rows = nav.build(); nav.tall.save(os.path.join(out, "menu_tall.png"))
    with open(os.path.join(out, "rows.txt"), "w") as f:
        for r in rows: f.write("%d %s cy=%d chevron=%d\n" % (r["idx"], name(r["idx"]), r["cy"], r["chevron"]))
    import pickle; pickle.dump(rows, open(os.path.join(out, "rows.pkl"), "wb")); return rows
def do_row(binpath, out, level, idx, gear=True):
    import pickle
    rows = pickle.load(open(os.path.join(out, "rows.pkl"), "rb")); nm = name(idx)
    s = U.UiSession.from_checkpoint(binpath, os.path.join(out, "menu.state"), out); s.wait(120)
    nav = U.ListNav(s); nav.tall = __import__("PIL.Image", fromlist=["Image"]).open(os.path.join(out, "menu_tall.png")); nav.rows = rows
    if not nav.tap_row_from_top(idx): print("nie udalo sie wejsc: L%d %s" % (level, nm), flush=True); return False
    s.scroll_capture(nm, dy=120)
    if gear and nm in GEAR:
        s.tap(400, 245, settle=800); s.scroll_capture(nm + "_ust", dy=120)
    print("ok L%d %s" % (level, nm), flush=True); return True
def run_all(binpath, out, level, workers=8):
    from concurrent.futures import ProcessPoolExecutor
    rows = prepare(binpath, out, level); jobs = [r["idx"] for r in rows if name(r["idx"]) not in SKIP]
    with ProcessPoolExecutor(workers) as ex: res = list(ex.map(do_row_star, [(binpath, out, level, i) for i in jobs]))
    print("DONE", out, "ok=%d/%d" % (sum(res), len(res)))
def do_row_star(a): return do_row(*a)
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("bin"); ap.add_argument("out"); ap.add_argument("--level", type=int, default=0)
    ap.add_argument("--prepare", action="store_true"); ap.add_argument("--row", type=int, default=-1); ap.add_argument("--all", action="store_true"); ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    if a.prepare: prepare(a.bin, a.out, a.level); print("PREPARED")
    elif a.row >= 0: do_row(a.bin, a.out, a.level, a.row); print("ROW DONE")
    elif a.all: run_all(a.bin, a.out, a.level, a.workers)
