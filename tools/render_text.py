#!/usr/bin/env python3
"""PASS 56: renderer tekstu z czcionek TouchGFX wyeksportowanych z firmware (tools/export_fonts.py): uklad poziomy wg advance/left/top (bez kerningu w tej wersji).
render(raw, font_index, text) -> (PIL 'L' alpha, baseline_y). Baseline = top glifu mierzony od gornej krawedzi linii: y_glifu = baseline - top, baseline = wysokosc_czcionki - pixBelowBase."""
import struct, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import export_fonts as E
from PIL import Image
def render(raw, fi, text):
    lst, n, hgt, pbb, data = E.FONTS[fi]; nodes = {g["unicode"]: g for g in E.load(raw, lst, n)}
    base = hgt - pbb; x = 0; items = []
    for ch in text:
        g = nodes.get(ord(ch)) or nodes.get(ord("?"))
        if g is None: continue
        items.append((x + g["left"], base - g["top"], g)); x += g["advance"]
    im = Image.new("L", (max(1, x + 2), hgt + 2), 0)
    for gx, gy, g in items:
        if g["width"] * g["height"]:
            gi = E.glyph_img(raw, data, g); im.paste(gi, (max(0, gx), max(0, gy)), gi)
    return im, base
