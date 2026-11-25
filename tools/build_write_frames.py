#!/usr/bin/env python3
"""Etap B: laczy wyniki write_probe (/tmp/w/wp_*.json) w UI/write_frames.json.
Dla kazdego wiersza: PID, ramka zapisu panelu (id 0x584, 42 idx 01 u32LE), raw vs wyswietlana wartosc -> kodowanie (plain / x10 / inne)."""
import json, glob, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths
U = paths.UI_MODEL
src = sys.argv[1:] or sorted(glob.glob(str(paths.WORK / "wp_[abcd].json")))
sc = {}
for lst in json.load(open(U / "list_scales.json"))["lists"].values():
    for r in lst["rows"]:
        if r.get("pid"): sc[r["pid"]] = r
out = {}; stat = {}
def num(s):
    try: return float(str(s).replace(",", ".").strip())
    except Exception: return None
for f in src:
    for lk, rows in json.load(open(f)).items():
        for i, r in rows.items():
            pid = r.get("pid"); fr = r.get("frame")
            e = {"list": lk, "idx": int(i), "label_pl": r.get("label"), "dialog": r.get("dialog")}
            if not fr:
                e.update(status="brak_ramki", note=("OPEN: lista 0x11 to statystyki/liczniki - prawdopodobnie tylko odczyt (brak dialogu edycji)" if lk == "0x11" else "OPEN: brak ramki zapisu (przelacznik wymaga potwierdzenia/zagniezdzony wiersz); nie ustalono"))
                stat["brak_ramki"] = stat.get("brak_ramki", 0) + 1
            else:
                raw = fr["raw"]; b, a = num(r.get("shown_before")), num(r.get("shown_after"))
                s = sc.get(pid, {}); scale = s.get("scale")
                enc = "nieustalone"
                if a is not None and scale:
                    if abs(a / scale - raw) < 0.51: enc = "plain" if scale == 1.0 else "raw = wyswietlana / scale (scale=%s)" % scale
                    elif raw >= 256 and abs((raw - 256) - a / scale) < 0.51: enc = "flaga+256"
                elif r.get("dialog") == "radio": enc = "indeks opcji"
                elif r.get("dialog") == "nie_otwarto" and raw in (0, 1): enc = "przelacznik 0/1 (stuk w wartosc, bez dialogu)"
                e.update(status="ok", frame_hex=fr["hex"], raw=raw, shown_before=r.get("shown_before"), shown_after=r.get("shown_after"),
                         scale=scale, decimals=s.get("decimals"), encoding=enc, cmd=fr["cmd"],
                         evidence="MEASURED (emulator, ramka CAN id 0x584 z can2.tx po OK w dialogu)")
                stat[enc.split(" ")[0]] = stat.get(enc.split(" ")[0], 0) + 1
            out[pid or f"{lk}:{i}"] = e
doc = {"schema_version": "1.0", "evidence": "MEASURED (emulator: ramki CAN id 0x584 po OK w dialogu; zapis do prawdziwego kotla NIE testowany)", "description": "Kodowanie zapisu parametrow przez panel (PID->ramka). Tylko emulator; zapis do prawdziwego kotla NIE testowany.",
       "frame_format": "CAN id 0x584 DLC8: 42 idx_lo idx_hi 01 u32LE(raw)", "stats": stat, "pids": out}
(U / "write_frames.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(out), stat)
