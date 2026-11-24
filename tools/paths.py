"""Jedno miejsce na sciezki repo. Po przeniesieniu `analiza/` -> `analiza_archiwum/` zmienia sie tylko ten plik.
Uzycie: from paths import ROOT, DATA, UI_MODEL, FIRMWARE   (tools/ jest na sys.path gdy skrypt uruchamiany z tools/)
Nadpisanie przez zmienna srodowiskowa ESTYMA_ANALIZA (np. katalog po zmianie nazwy)."""
from __future__ import annotations
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALIZA = ROOT / os.environ.get("ESTYMA_ANALIZA", "analiza")
RUN = ANALIZA / "FW2213TK-2026-11-22"
DATA = RUN / "data"
UI_MODEL = DATA / "ui_model"
SCHEMA = UI_MODEL / "schema"
FIRMWARE = ROOT / "FW2213TK_kopia.bin"   # poza gitem (.gitignore)
FIRMWARE_SHA256 = "1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071"
WORK = Path(os.environ.get("ESTYMA_WORK", "/tmp/w"))  # punkty kontrolne emulatora

def rel(p: Path) -> str:
    """Sciezka wzgledna wzgledem ROOT w zapisie POSIX (do zapisu w JSON/MD)."""
    return Path(p).resolve().relative_to(ROOT).as_posix()
