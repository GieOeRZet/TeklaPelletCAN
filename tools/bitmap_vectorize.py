#!/usr/bin/env python3
"""Probuje odtworzyc bitmapy panelu wektorowo (CSS/SVG) i MIERZY roznice pikseli wobec oryginalu.
Modele: SOLID (jeden kolor), V (pionowy gradient: profil wierszy), H (poziomy gradient), S (rozdzielny: profil wierszy + profil kolumn, addytywnie),
kazdy opcjonalnie z maska zaokraglonych rogow (promien z kanalu alfa). Profile upraszczane do <=12 przystankow (Ramer-Douglas-Peucker), blad liczony po uproszczeniu.
Porownanie: kompozyt na szarym tle (#606060) i na bialym, blad sredni (0-255) i % pikseli z roznica > 24.
Klasy: WEKTOR (MAE<=2.5 i <=2% pikseli), PRZYBLIZONY (MAE<=6), RASTER (reszta).
Uzycie: python3 tools/bitmap_vectorize.py DIR_Z_PNG OUT.json [OUT_montaz.png]   (nazwy NNN_WxH.png)"""
import glob, json, os, re, sys
import numpy as np
from PIL import Image
src, out = sys.argv[1], sys.argv[2]; montage = sys.argv[3] if len(sys.argv) > 3 else None
def rdp(y, tol):                      # upraszczanie profilu 1D do punktow (indeks, wartosc)
    n = len(y); keep = {0, n - 1}; st = [(0, n - 1)]
    while st:
        a, b = st.pop()
        if b <= a + 1: continue
        xs = np.arange(a + 1, b); t_ = (xs - a) / (b - a); lin = y[a] + (y[b] - y[a]) * (t_[:, None] if y.ndim > 1 else t_)
        err = np.abs(y[a + 1:b] - lin).max(axis=-1) if y.ndim > 1 else np.abs(y[a + 1:b] - lin)
        k = int(err.argmax())
        if err[k] > tol: keep.add(a + 1 + k); st += [(a, a + 1 + k), (a + 1 + k, b)]
    return sorted(keep)
def interp(pts, y):                   # odtworzenie profilu z przystankow
    n = len(y); idx = np.arange(n); out = np.zeros_like(y, dtype=float)
    for c in range(y.shape[1]):
        out[:, c] = np.interp(idx, pts, y[pts, c])
    return out
def comp(rgb, a, bg):                 # kompozyt premult na tle
    return rgb + (1 - a[..., None]) * bg
def corner_radius(alpha):             # promien zaokraglenia z gornego lewego rogu
    h, w = alpha.shape
    if alpha[0, 0] > 0.5 or h < 4 or w < 4: return 0 if alpha[0, 0] > 0.5 else None
    row = alpha[0]; r = int(np.argmax(row > 0.5)) if (row > 0.5).any() else None
    return r
def rmask(h, w, r):
    if not r: return np.ones((h, w))
    yy, xx = np.mgrid[0:h, 0:w] + 0.5; m = np.ones((h, w))
    for cx, cy in ((r, r), (w - r, r), (r, h - r), (w - r, h - r)):
        sel = ((xx < r) if cx == r else (xx > w - r)) & ((yy < r) if cy == r else (yy > h - r))
        d = np.hypot(xx - cx, yy - cy); m = np.where(sel, np.clip(r + 0.5 - d, 0, 1), m)
    return m
res = {}; rows = []
files = sorted(glob.glob(os.path.join(src, "*.png")), key=lambda f: int(os.path.basename(f)[:3]))
for f in files:
    m = re.match(r"(\d+)_(\d+)x(\d+)\.png", os.path.basename(f))
    if not m: continue
    bid, w, h = int(m[1]), int(m[2]), int(m[3]); im = np.asarray(Image.open(f).convert("RGBA")).astype(float)
    a = im[..., 3] / 255; P = im[..., :3] * a[..., None]; A = a
    best = None
    cands = []
    # SOLID
    cands.append(("SOLID", np.broadcast_to(P.mean((0, 1)), P.shape), np.broadcast_to(A.mean(), A.shape), {"stops": None}))
    # V i H (profile premult + alfa jako 4 kanaly)
    Q = np.concatenate([P, A[..., None] * 255], axis=2)
    for name, axis in (("V", 1), ("H", 0)):
        prof = Q.mean(axis=axis)                                  # (h,4) lub (w,4)
        pts = rdp(prof, 1.2)
        rp = np.zeros_like(prof)
        for c in range(4): rp[:, c] = np.interp(np.arange(len(prof)), pts, prof[pts, c])
        R = np.broadcast_to(rp[:, None, :], (h, w, 4)) if name == "V" else np.broadcast_to(rp[None, :, :], (h, w, 4))
        cands.append((name, R[..., :3], R[..., 3] / 255, {"stops": [[int(i), [round(float(x), 1) for x in prof[i]]] for i in pts]}))
    # S: rozdzielny addytywnie (profil Y + profil X - srednia)
    py = Q.mean(1); px = Q.mean(0); mu = Q.mean((0, 1))
    ptsy, ptsx = rdp(py, 1.5), rdp(px, 1.5)
    ry = np.zeros_like(py); rx = np.zeros_like(px)
    for c in range(4): ry[:, c] = np.interp(np.arange(h), ptsy, py[ptsy, c]); rx[:, c] = np.interp(np.arange(w), ptsx, px[ptsx, c])
    R = ry[:, None, :] + rx[None, :, :] - mu
    cands.append(("S", R[..., :3], np.clip(R[..., 3] / 255, 0, 1), {"stops_y": len(ptsy), "stops_x": len(ptsx)}))
    for name, rgb, al, meta in cands:
        al = np.clip(al, 0, 1); rgbm = np.clip(rgb, 0, 255)
        r = corner_radius(A)
        for mask_r in ([None] if not r else [None, r]):
            mk = rmask(h, w, mask_r) if mask_r else np.ones((h, w))
            rgb2 = rgbm * (mk[..., None] if mask_r else 1); al2 = al * mk
            if mask_r:                                               # po masce: kolor premult skalowany
                rgb2 = rgbm * mk[..., None]
            err = 0; bad = 0
            for bg in (96, 255):
                d = np.abs(comp(P, A, bg) - comp(np.clip(rgb2, 0, 255), al2, bg)).max(axis=2); err += d.mean() / 2; bad += (d > 24).mean() / 2
            if best is None or err < best[0]: best = (err, bad, name + ("+R%d" % mask_r if mask_r else ""), meta, rgb2, al2)
    err, bad, name, meta, rgb2, al2 = best
    cls = "WEKTOR" if err <= 2.5 and bad <= 0.02 else "PRZYBLIZONY" if err <= 6 else "RASTER"
    res[str(bid)] = dict(id=bid, size=[w, h], model=name, mae=round(float(err), 2), pct_bad=round(float(bad) * 100, 1), klasa=cls, png_bytes=os.path.getsize(f), **meta)
    rows.append((bid, w, h, cls, err, P, A, rgb2, al2))
cnt = {}
for r in res.values(): cnt[r["klasa"]] = cnt.get(r["klasa"], 0) + 1
bytes_ = {k: sum(r["png_bytes"] for r in res.values() if r["klasa"] == k) for k in cnt}
doc = {"schema_version": "1.0", "evidence": "MEASURED (porownanie pikseli bitmapa vs odtworzenie wektorowe; kompozyt na tle #606060 i bialym)", "thresholds": {"WEKTOR": "MAE<=2.5 i <=2% pikseli roznych o >24", "PRZYBLIZONY": "MAE<=6"}, "summary": {"count": cnt, "png_bytes": bytes_}, "bitmaps": res}
json.dump(doc, open(out, "w"), ensure_ascii=False, indent=1); print(cnt, bytes_)
if montage:                                                           # montaz: dla klas WEKTOR/PRZYBLIZONY: oryg | odtworzenie | roznica x4
    sel = [r for r in rows if r[3] != "RASTER"]; cell_w = 3 * 120 + 30; rowsN = (len(sel) + 1) // 2
    im = Image.new("RGB", (2 * cell_w, max(1, rowsN) * 100), (40, 40, 40))
    for i, (bid, w, h, cls, err, P, A, rgb2, al2) in enumerate(sel):
        a = comp(P, A, 96); b = comp(np.clip(rgb2, 0, 255), al2, 96); d = np.clip(np.abs(a - b) * 4, 0, 255)
        x0 = (i % 2) * cell_w; y0 = (i // 2) * 100
        for k, arr in enumerate((a, b, d)):
            t = Image.fromarray(arr.astype("uint8")); sc = min(1, 110 / max(w, 1), 80 / max(h, 1)) if w > 110 or h > 80 else 1; t = t.resize((max(1, int(w * sc)), max(1, int(h * sc)))) if sc != 1 else t
            im.paste(t, (x0 + k * 120 + 4, y0 + 14))
        from PIL import ImageDraw; ImageDraw.Draw(im).text((x0 + 4, y0 + 2), "%d %s %.1f" % (bid, cls[:4], err), fill=(255, 255, 0))
    im.save(montage)
