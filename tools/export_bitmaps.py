#!/usr/bin/env python3
"""NewEstyma PASS 47: eksport WSZYSTKICH 188 bitmap zapisanych w firmware FW2213TK do PNG + manifest + plansze + ZIP.
python3 -I tools/export_bitmaps.py FW2213TK_kopia.bin OUTDIR
Tablica deskryptorow: RAW 0x54450, 188 wpisow po 0x14 B: {u32 data_ptr, u32 extra_ptr (alfa A8 lub 0), u16 width, u16 height, u16 solid_x, solid_y, solid_w, solid_h};
wskazniki w adresach RUNTIME (obraz pod 0x08010000). Dane: RGB565 little-endian (w*h*2 B) + opcjonalnie A8 (w*h B). Wyjscie:
 OUTDIR/png/NNN.png, OUTDIR/manifest.csv (id, rozmiar, alfa, wskazniki, solid rect, sha256 PNG), OUTDIR/sheet_*.png (plansze poglądowe), OUTDIR.zip"""
import csv, hashlib, os, struct, sys, zipfile
from PIL import Image, ImageDraw
BASE, TABLE, STRIDE, COUNT = 0x08010000, 0x54450, 0x14, 188
def decode(b, i):
    dp, ep, w, h, sx, sy, sw, sh = struct.unpack_from("<IIHHHHHH", b, TABLE + i * STRIDE)
    n = w * h; o = dp - BASE; raw = b[o:o + 2 * n]; assert len(raw) == 2 * n, "bitmapa %d: uciete dane" % i
    px = bytearray(3 * n)
    for k in range(n):
        v = raw[2 * k] | raw[2 * k + 1] << 8; r, g, bl = v >> 11 & 31, v >> 5 & 63, v & 31
        px[3 * k] = r << 3 | r >> 2; px[3 * k + 1] = g << 2 | g >> 4; px[3 * k + 2] = bl << 3 | bl >> 2
    im = Image.frombytes("RGB", (w, h), bytes(px))
    if ep:
        a = b[ep - BASE:ep - BASE + n]; assert len(a) == n, "bitmapa %d: uciete A8" % i
        im.putalpha(Image.frombytes("L", (w, h), a))
    return im, dict(id=i, width=w, height=h, alpha=int(bool(ep)), data_ptr="0x%08X" % dp, extra_ptr="0x%08X" % ep, solid="%d,%d,%d,%d" % (sx, sy, sw, sh))
def sheet(png_dir, ids, out, cols=8, cw=118, ch=96):
    rows = (len(ids) + cols - 1) // cols; W = Image.new("RGB", (cols * cw, rows * ch), (60, 60, 70)); d = ImageDraw.Draw(W)
    for n, i in enumerate(ids):
        im = Image.open(os.path.join(png_dir, "%03d.png" % i)).convert("RGBA"); sc = min((cw - 8) / im.width, (ch - 22) / im.height, 3.0)
        im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc)))); x, y = (n % cols) * cw, (n // cols) * ch
        W.paste(im, (x + 4, y + 16), im); d.text((x + 4, y + 2), str(i), fill=(255, 255, 0))
    W.save(out)
if __name__ == "__main__":
    raw = open(sys.argv[1], "rb").read(); out = sys.argv[2]; png = os.path.join(out, "png"); os.makedirs(png, exist_ok=True)
    assert hashlib.sha256(raw).hexdigest() == "1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071", "to nie kanoniczny FW2213TK_kopia.bin"
    rows = []
    for i in range(COUNT):
        im, d = decode(raw, i); p = os.path.join(png, "%03d.png" % i); im.save(p); d["mode"] = im.mode; d["sha256"] = hashlib.sha256(open(p, "rb").read()).hexdigest(); rows.append(d)
    with open(os.path.join(out, "manifest.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    for a, b_ in ((0, 64), (64, 128), (128, 188)): sheet(png, list(range(a, b_)), os.path.join(out, "sheet_%03d_%03d.png" % (a, b_ - 1)))
    with zipfile.ZipFile(out.rstrip("/") + ".zip", "w", zipfile.ZIP_DEFLATED) as z:
        for dp, _, fs in os.walk(out):
            for fn in sorted(fs): z.write(os.path.join(dp, fn), os.path.join(os.path.basename(out.rstrip("/")), os.path.relpath(os.path.join(dp, fn), out)))
    print("OK: %d bitmap, alfa: %d, RGB: %d, ZIP: %s" % (len(rows), sum(r["alpha"] for r in rows), sum(1 - r["alpha"] for r in rows), out.rstrip("/") + ".zip"))
