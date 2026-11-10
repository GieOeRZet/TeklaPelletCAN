#!/usr/bin/env python3
"""Kopiuje wspolny interfejs aplikacji (android/ui/js, style.css) -> portal WWW urzadzenia
(web/js, web/style.css) - portal uzywa tego samego kodu co apka Android, oprocz
android/ui/js/native.js (most JNI, portal ma wlasny web/js/native.js).

Karty Lovelace (web/*-card.js) NIE sa czescia integracji HA (custom_components/teklapelletcan) -
instaluje sie je osobno z HACS, z dedykowanych repozytoriow (TeklaPelletClassic-card,
TeklaPelletModern-card), ktore maja wlasne kopie img/ i same synchronizuja sie z tym repo przy
wydaniu (patrz .github/workflows/ci.yml, joby publish-card-*).

Uzycie:  python3 tools/sync_web.py          # kopiuje
         python3 tools/sync_web.py --check  # CI: sprawdza, czy kopie sa aktualne
"""
import filecmp, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "web"
UI_SRC = ROOT / "android/ui"
UI_FILES = ["js/store.js", "js/ui.js", "js/views.js", "js/main.js", "js/updates.js", "js/theme.js", "style.css"]


def pairs():
    for f in UI_FILES:
        yield UI_SRC / f, SRC / f


if __name__ == "__main__":
    bad = []
    for s, d in pairs():
        if "--check" in sys.argv:
            if not d.exists() or not filecmp.cmp(s, d, shallow=False):
                bad.append(str(d.relative_to(ROOT)))
        else:
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(s, d)
    if "--check" in sys.argv:
        if bad:
            raise SystemExit("nieaktualne kopie: " + ", ".join(bad) + " – uruchom tools/sync_web.py")
        print("kopie plikow wspolnych aktualne")
    else:
        print(f"skopiowano wspolny interfejs do {SRC}")
