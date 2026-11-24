#!/usr/bin/env python3
"""PASS 67: ocena renderera z danych na atlasie wszystkich ekranow -> data/ui_model/render_eval.csv/.md (MAE i % pikseli roznych >40 wzgledem zrzutu emulatora)."""
import csv, glob, json, os, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_compare as C
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analiza_archiwum", "FW2213TK-2026-11-22", "data") + os.sep
INV = {"L0": "widgets_inv_pass61_L0.json", "L1": "widgets_inv_pass65_L1_all.json", "LC": "widgets_inv_pass65_cascade_fuelstore_L0.json", "H": "widgets_inv_pass65_home_L0.json"}
rows = []
for pre, f in INV.items():
    inv = {n["node"]: n for n in json.load(open(A + f))}
    EXD = os.environ.get("ESTYMA_EXTRAS", A + "ui_model/extras"); OUTD = os.environ.get("ESTYMA_EVAL_OUT", A + "ui_model")      # katalog extras i wyjscia mozna nadpisac
    for ef in sorted(glob.glob(os.path.join(EXD, "%s_*.json" % pre))):
        node = os.path.basename(ef)[len(pre) + 1:-5]; at = A + "ui_model/atlas/%s_%s.png" % (pre, node)
        if not os.path.exists(at) or node not in inv: continue
        _, _, mae, fr, _ = C.compare(inv[node]["widgets"], at, json.load(open(ef))); rows.append(dict(screen="%s_%s" % (pre, node), mae=round(mae, 2), pct_diff=round(fr * 100, 1)))
w = csv.DictWriter(open(os.path.join(OUTD, "render_eval.csv"), "w", newline=""), fieldnames=["screen", "mae", "pct_diff"]); w.writeheader(); w.writerows(rows)
md = ["# Ocena renderera z danych vs atlas emulatora\n", "mediana: MAE %.2f, %% pikseli roznych %.1f; ekranow: %d\n" % (statistics.median(r["mae"] for r in rows), statistics.median(r["pct_diff"] for r in rows), len(rows)), "| ekran | MAE | % pikseli roznych |", "|---|---|---|"]
md += ["| %s | %s | %s |" % (r["screen"], r["mae"], r["pct_diff"]) for r in sorted(rows, key=lambda r: -r["pct_diff"])]
open(os.path.join(OUTD, "render_eval.md"), "w", encoding="utf-8").write("\n".join(md) + "\n"); print(md[1])
