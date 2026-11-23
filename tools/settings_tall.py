#!/usr/bin/env python3
"""NewEstyma PASS 47: PELNE listy ustawien (zszyte w jeden wysoki obraz) dla ekranu i poziomu dostepu, na podstawie punktow kontrolnych z ui_explore.
python3 -I tools/settings_tall.py FW2213TK_kopia.bin EXPLORE_DIR NAZWA OUT.png     # EXPLORE_DIR = katalog z menu.state/rows.pkl/menu_tall.png (ui_explore --prepare), NAZWA np. palnik|kociol|co1|cwu|solar|bufor|konfiguracja
Wchodzi w wiersz MENU, dla ekranow urzadzen dodatkowo w NASTAWY (zebatka), po czym sklada cala liste (ui_session.stitch_body)."""
import os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, ui_explore as X
from PIL import Image
def run(binpath, d, name, out):
    rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb")); idx = X.ROWS.index(name)
    s = U.UiSession.from_checkpoint(binpath, os.path.join(d, "menu.state")); s.wait(120)
    nav = U.ListNav(s); nav.tall = Image.open(os.path.join(d, "menu_tall.png")); nav.rows = rows
    if not nav.tap_row_from_top(idx): print("nie weszlo", name); return False
    if name in X.GEAR: s.tap(400, 245, settle=800)
    t = U.stitch_body(s); t.save(out); print("ok", name, t.size, flush=True); return True
if __name__ == "__main__": run(*sys.argv[1:5])
