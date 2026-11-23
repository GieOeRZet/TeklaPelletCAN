#!/usr/bin/env python3
"""NewEstyma PASS 47: porownanie zrzutow ekranow miedzy poziomami dostepu (katalogi z ui_explore).
python3 -I tools/compare_levels.py DIR_A DIR_B [out_dir]
Dla kazdej nazwy ekranu (np. kociol, palnik_ust, konfiguracja) porownuje kolejne strony (<nazwa>_<n>.png) po obrazie BEZ naglowka (y<46: licznik % i ikona poziomu sie zmieniaja).
Wypisuje: ekran, liczbe stron A/B, ktore strony sa rozne i ile pikseli sie rozni; zapisuje plansze A|B|roznica dla roznych stron."""
import glob, os, re, sys
import numpy as np
from PIL import Image
def pages(d):
    out = {}
    for f in glob.glob(os.path.join(d, "*_[0-9]*.png")):
        m = re.match(r"(.+)_(\d+)\.png$", os.path.basename(f))
        if m: out.setdefault(m.group(1), {})[int(m.group(2))] = f
    return out
def body(im): return np.asarray(im.convert("RGB"), dtype=int)[46:, :, :]
def compare(da, db, out=None):
    A, B = pages(da), pages(db); rep = []
    for nm in sorted(set(A) | set(B)):
        pa, pb = A.get(nm, {}), B.get(nm, {}); n = max(len(pa), len(pb)); diffs = []
        for i in range(n):
            if i in pa and i in pb:
                x, y = body(Image.open(pa[i])), body(Image.open(pb[i])); d = int((np.abs(x - y).sum(axis=2) > 40).sum())
                if d: diffs.append((i, d))
                if d and out:
                    os.makedirs(out, exist_ok=True); ia, ib = Image.open(pa[i]), Image.open(pb[i])
                    dm = Image.fromarray(((np.abs(np.asarray(ia.convert("RGB"), dtype=int) - np.asarray(ib.convert("RGB"), dtype=int)).sum(axis=2) > 40) * 255).astype("uint8")).convert("RGB")
                    W = Image.new("RGB", (480 * 3 + 12, 272), (80, 80, 80)); W.paste(ia, (0, 0)); W.paste(ib, (486, 0)); W.paste(dm, (972, 0)); W.save(os.path.join(out, "%s_%d.png" % (nm, i)))
            else: diffs.append((i, -1))
        rep.append((nm, len(pa), len(pb), diffs))
    return rep
if __name__ == "__main__":
    rep = compare(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    for nm, na, nb, d in rep: print("%-16s stron A=%d B=%d  %s" % (nm, na, nb, ("ROZNE: " + ", ".join("p%d(%s)" % (i, "brak" if x < 0 else x) for i, x in d)) if d else "identyczne"))
