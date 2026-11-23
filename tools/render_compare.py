#!/usr/bin/env python3
"""PASS 67: zgodnosc renderera z atlasem emulatora: render_compare.py INV.json WEZEL ATLAS.png [--extras E.json] [--out DIFF.png] -> MAE, procent pikseli roznych (>40), obraz roznic"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_render as R
from PIL import Image, ImageChops
import numpy as np
def compare(widgets, atlas, extras=None):
    a = R.render(widgets, extras); b = Image.open(atlas).convert("RGB"); d = np.abs(np.asarray(a).astype(int) - np.asarray(b).astype(int)).sum(axis=2)
    return a, b, float(d.mean() / 3), float((d > 40).mean()), d
if __name__ == "__main__":
    inv = {n["node"]: n for n in json.load(open(sys.argv[1]))}; ex = json.load(open(sys.argv[sys.argv.index("--extras") + 1])) if "--extras" in sys.argv else None
    a, b, mae, frac, d = compare(inv[sys.argv[2]]["widgets"], sys.argv[3], ex); print("MAE %.2f  pikseli roznych %.1f%%" % (mae, frac * 100))
    if "--out" in sys.argv:
        o = sys.argv[sys.argv.index("--out") + 1]; sh = Image.new("RGB", (480 * 3, 272)); sh.paste(a, (0, 0)); sh.paste(b, (480, 0)); sh.paste(Image.fromarray(np.clip(d, 0, 255).astype("uint8")).convert("RGB"), (960, 0)); sh.save(o)
