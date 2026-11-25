#!/usr/bin/env python3
"""Etap D: sklada UI/program_pids.json z wynikow tools/program_write_probe.py (/tmp/w/pp/pp_*.json): PID harmonogramu dla ekranu x dnia (ramka zapisu panelu)."""
import glob, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths
D = ["Pn", "Wt", "Sr", "Cz", "Pt", "Sb", "Nd"]; NAMES = {0: "KOCIOL", 2: "OGRZEWANIE1", 3: "OGRZEWANIE2", 4: "OGRZEWANIE3", 5: "OGRZEWANIE4", 6: "CWU"}
src = {}
for f in sorted(glob.glob(str(paths.WORK / "pp" / "pp_*.json"))):
    for k, v in json.load(open(f)).items():
        if v.get("status") == "ok": src[k] = v
out = {}
for row, name in NAMES.items():
    out[name] = {d: (src.get("row%d_%s" % (row, d), {}).get("frames") or [{}])[0].get("index") for d in D}
miss = [(n, d) for n, m in out.items() for d, v in m.items() if v is None]
doc = {"schema_version": "1.0", "evidence": "MEASURED (emulator: ramka CAN 0x584 po zmianie godziny w dialogu dnia + OK; dzien potwierdzony tytulem dialogu)",
       "pids": out, "missing": miss, "formulas": {"KOCIOL": "0x2209 + dzien (Pn=0..Nd=6)", "OGRZEWANIE_k": "0x2126 + 4*dzien + (k-1), k=1..4", "CWU": "0x2154 + dzien (Pn..Sb), niedziela = 0x2160"},
       "encoding": "u32 maska 24 bitow, bit h = godzina h (1 = komfort); zapis wartosci zmienionej przy OK; ramka 42 idx 01 u32LE"}
(paths.UI_MODEL / "program_pids.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8"); print(json.dumps(out), "brak:", miss)
