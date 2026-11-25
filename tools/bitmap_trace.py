#!/usr/bin/env python3
"""Grafiki panelu: trasowanie WSZYSTKICH bitmap do SVG (vtracer, kilka presetow) i pomiar bledu pikseli wobec oryginalu
(render Chromium 1x przez tools/render_svgs.js, kompozyt na tle #606060 i bialym).
Wynik: JSON (per bitmapa: najlepszy preset, MAE, % pikseli roznych o >24, rozmiar SVG/PNG, klasa) + katalog SVG.
Klasy: WEKTOR (MAE<=2.5, <=2% pikseli), DOBRY (MAE<=6, <=6%), SLABY (MAE<=12), RASTER (gorzej).
Uzycie: python3 tools/bitmap_trace.py DIR_PNG OUT_DIR OUT.json   (nazwy plikow NNN_WxH.png)"""
import glob, json, os, re, subprocess, sys
import numpy as np
from PIL import Image
import vtracer

HERE = os.path.dirname(os.path.abspath(__file__))
src, outd, outj = sys.argv[1:4]
os.makedirs(outd, exist_ok=True)
PRESETS = {
    "s1_p6": dict(scale=1, color_precision=6, layer_difference=16, filter_speckle=1, corner_threshold=60, length_threshold=3.5, splice_threshold=45, path_precision=2),
    "s4_p6": dict(scale=4, color_precision=6, layer_difference=12, filter_speckle=4, corner_threshold=60, length_threshold=4.0, splice_threshold=45, path_precision=1),
    "s4_p8": dict(scale=4, color_precision=8, layer_difference=8, filter_speckle=2, corner_threshold=45, length_threshold=3.0, splice_threshold=45, path_precision=1),
}
jobs, info = [], {}
for f in sorted(glob.glob(os.path.join(src, "*.png")), key=lambda f: int(os.path.basename(f)[:3])):
    m = re.match(r"(\d+)_(\d+)x(\d+)\.png", os.path.basename(f))
    if not m:
        continue
    bid, w, h = int(m[1]), int(m[2]), int(m[3])
    info[bid] = dict(w=w, h=h, png=f)
    im = Image.open(f).convert("RGBA")
    for pn, p in PRESETS.items():
        sc = p["scale"]
        tmp = os.path.join(outd, "%03d_in_%s.png" % (bid, pn))
        (im.resize((w * sc, h * sc), Image.LANCZOS) if sc != 1 else im).save(tmp)
        svgf = os.path.join(outd, "%03d_%s.svg" % (bid, pn))
        try:
            vtracer.convert_image_to_svg_py(tmp, svgf, colormode="color", hierarchical="stacked", mode="spline", filter_speckle=p["filter_speckle"],
                                             color_precision=p["color_precision"], layer_difference=p["layer_difference"], corner_threshold=p["corner_threshold"],
                                             length_threshold=p["length_threshold"], max_iterations=10, splice_threshold=p["splice_threshold"], path_precision=p["path_precision"])
            txt = open(svgf).read()   # viewBox = rozmiar powiekszony, width/height = rozmiar oryginalu
            txt = re.sub(r'<svg([^>]*?)width="\d+" height="\d+"', r'<svg\1width="%d" height="%d" viewBox="0 0 %d %d"' % (w, h, w * sc, h * sc), txt, count=1)
            open(svgf, "w").write(txt)
            os.remove(tmp)
            jobs.append(dict(svg=os.path.abspath(svgf), w=w, h=h, out=os.path.abspath(svgf[:-4] + "_r.png"), id=bid, preset=pn))
        except Exception as e:
            print("ERR", bid, pn, e)
jf = os.path.abspath(os.path.join(outd, "jobs.json"))
json.dump(jobs, open(jf, "w"))
subprocess.run(["node", os.path.join(HERE, "render_svgs.js"), jf], check=True, cwd="/tmp")


def comp(a4, bg):
    a = a4[..., 3:4] / 255
    return a4[..., :3] * a + bg * (1 - a)


res = {}
for bid, d in info.items():
    o = np.asarray(Image.open(d["png"]).convert("RGBA")).astype(float)
    best, tried = None, {}
    for pn in PRESETS:
        rf = os.path.join(outd, "%03d_%s_r.png" % (bid, pn))
        if not os.path.exists(rf):
            continue
        r = np.asarray(Image.open(rf).convert("RGBA").resize((d["w"], d["h"]))).astype(float)
        err = bad = 0
        for bg in (96, 255):
            x = np.abs(comp(o, bg) - comp(r, bg)).max(axis=2)
            err += x.mean() / 2
            bad += (x > 24).mean() / 2
        svgb = os.path.getsize(os.path.join(outd, "%03d_%s.svg" % (bid, pn)))
        tried[pn] = dict(mae=round(float(err), 2), pct_bad=round(float(bad) * 100, 1), svg_bytes=svgb)
        if best is None or err < best[0]:
            best = (err, bad, pn, svgb)
    err, bad, pn, svgb = best
    pngb = os.path.getsize(d["png"])
    cls = "WEKTOR" if err <= 2.5 and bad <= .02 else "DOBRY" if err <= 6 and bad <= .06 else "SLABY" if err <= 12 else "RASTER"
    res[str(bid)] = dict(id=bid, size=[d["w"], d["h"]], best=pn, mae=round(float(err), 2), pct_bad=round(float(bad) * 100, 1), klasa=cls, png_bytes=pngb, svg_bytes=svgb, presets=tried)
cnt = {}
for r in res.values():
    cnt[r["klasa"]] = cnt.get(r["klasa"], 0) + 1
byt = {k: [sum(r["png_bytes"] for r in res.values() if r["klasa"] == k), sum(r["svg_bytes"] for r in res.values() if r["klasa"] == k)] for k in cnt}
json.dump(dict(schema_version="1.0", evidence="MEASURED (trasowanie vtracer, render Chromium 1x, porownanie pikseli na tle #606060 i bialym)",
               summary=dict(count=cnt, bytes_png_svg=byt), bitmaps=res), open(outj, "w"), ensure_ascii=False, indent=1)
print(cnt, byt)
