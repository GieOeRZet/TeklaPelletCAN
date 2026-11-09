#!/usr/bin/env python3
"""Kopiuje karte (web/) do integracji HA: custom_components/teklapelletcan/www (HACS dostarcza tylko ten katalog).

Uzycie:  python3 tools/sync_web.py          # kopiuje
         python3 tools/sync_web.py --check  # CI: sprawdza, czy kopia jest aktualna
"""
import filecmp, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, DST = ROOT / "web", ROOT / "custom_components/teklapelletcan/www"
FILES = ["pelletcan-card.js", "teklapelletcan-card.js", "tekla-panel-card.js", "pelletcan-lang.js"]
DIRS = ["img"]


def pairs():
    for f in FILES:
        yield SRC / f, DST / f
    for d in DIRS:
        for p in (SRC / d).rglob("*"):
            if p.is_file():
                yield p, DST / p.relative_to(SRC)


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
            raise SystemExit("nieaktualne kopie karty: " + ", ".join(bad) + " – uruchom tools/sync_web.py")
        print("karta w integracji aktualna")
    else:
        print(f"skopiowano karte do {DST}")
