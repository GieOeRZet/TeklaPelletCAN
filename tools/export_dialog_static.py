#!/usr/bin/env python3
"""E7: tlo statyczne dialogu liczbowego dla karty (bez emulatora): render z dialog_render/number_dialog_data.json z pominieciem tekstow, wypelnionego toru i galki (rysowane dynamicznie w karcie).
Wyjscie: web/estyma_prototype/dialogs/number_bg.png + img/knob.png, track_fill.png, track.png."""
import json, os, sys, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths, ui_render as R
d = json.load(open(paths.UI_MODEL / "dialog_render" / "number_dialog_data.json")); ws = d["widgets"]; ex = d["extras"]
omit = {w["this"] for w in ws if (ex.get(w["this"], {}).get("cls") == "text" and w["ay"] > 20) or w.get("bitmap_id") in (165, 69)}
keep = [w for w in ws if w["this"] not in omit]
vis = sorted([(ex[w["this"]]["z"], w) for w in ws if w["this"] in ex and not ex[w["this"]].get("hidden") and "z" in ex[w["this"]]], key=lambda x: x[0]); dim = None
for i, (z, w) in enumerate(vis[:-1]):
    nx = vis[i + 1][1]
    if z > 10 and (w["w"], w["h"]) == (480, 272) and ex[w["this"]]["cls"] == "other" and 380 <= nx["w"] <= 470 and nx["h"] >= 200: dim = (180, z); break
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "estyma_prototype"); os.makedirs(os.path.join(out, "img"), exist_ok=True)
R.render(keep, ex, dim=dim).save(os.path.join(out, "dialogs", "number_bg.png"))
for name, bid in (("track", 163), ("track_fill", 165), ("knob", 69)): shutil.copy(os.path.join(paths.DATA, "bitmaps", "png", "%03d.png" % bid), os.path.join(out, "img", name + ".png"))
print("OK", len(keep), "widgetow, dim", dim)
