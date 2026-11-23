#!/usr/bin/env python3
"""PASS 56: eksport czcionek TouchGFX (GeneratedFont) z obrazu firmware.
Fabryki czcionek: 6 wywolan konstruktora 0x0805B75C (0x080517E8.. 0x0805190E) z argumentami: lista glifow (r1), liczba glifow (r2), wysokosc (r3), pixBelowBase ([sp]), bpp ([sp+4]),
wskaznik na dane glifow ([sp+0x10]), wskaznik na tablice kerningu/gsub ([sp+0x14]).
GlyphNode (14 B): +0 u32 dataOffset (w tablicy danych), +4 u16 unicode, +6 u8 width, +7 u8 height, +8 u8 top, +9 i8 left, +10 u8 advance, +11 u8 (0xFF), +12 u16 (kerning).
Dane glifu: 4 bpp (wartosc 0..15 = alfa), wiersze upakowane BEZ wyrownania, nibble NISKI pierwszy (potwierdzone wizualnie).
python3 -I tools/export_fonts.py FW.bin OUTDIR"""
import csv, json, os, struct, sys
from PIL import Image
B = 0x08010000
FONTS = [  # (lista, liczba, wysokosc, pixBelowBase, dane)  — z analizy fabryk
    (0x0806F030, 76, 12, 3, 0x0806D598), (0x08068218, 152, 20, 5, 0x08037978), (0x0806DCD0, 127, 26, 6, 0x080319B4),
    (0x0806EAFC, 95, 36, 8, 0x08029490), (0x08074730, 19, 64, 9, 0x08039E20), (0x0807483C, 19, 92, 12, 0x0802D90C)]
def load(raw, lst, n):
    nodes = []
    for k in range(n):
        o = lst - B + 14 * k
        off, uni, w, h, top, left, adv = struct.unpack_from("<IHBBBbB", raw, o)
        nodes.append(dict(offset=off, unicode=uni, width=w, height=h, top=top, left=left, advance=adv))
    return nodes
def glyph_img(raw, data, g, hi_first=False):
    w, h = g["width"], g["height"]; o = data - B + g["offset"]; px = []
    for i in range(w * h):
        b = raw[o + i // 2]; v = (b >> 4) if ((i % 2 == 0) == hi_first) else (b & 15); px.append(v * 17)
    im = Image.new("L", (max(1, w), max(1, h)));
    if w * h: im.putdata(px)
    return im
def main(fw, out):
    raw = open(fw, "rb").read(); os.makedirs(out, exist_ok=True); meta = []
    for fi, (lst, n, hgt, pbb, data) in enumerate(FONTS):
        nodes = load(raw, lst, n); d = os.path.join(out, "font%d_h%d" % (fi, hgt)); os.makedirs(d, exist_ok=True)
        cols = 24; cell = hgt + 6; rows = (n + cols - 1) // cols; atlas = Image.new("L", (cols * (hgt + 4), rows * cell), 40)
        with open(os.path.join(d, "glyphs.csv"), "w", newline="") as f:
            w = csv.writer(f); w.writerow(["unicode", "char", "width", "height", "top", "left", "advance", "data_offset"])
            for k, g in enumerate(nodes):
                try: ch = chr(g["unicode"]) if g["unicode"] >= 0x20 else ""
                except Exception: ch = ""
                w.writerow(["0x%04X" % g["unicode"], ch, g["width"], g["height"], g["top"], g["left"], g["advance"], g["offset"]])
                im = glyph_img(raw, data, g); im.save(os.path.join(d, "u%04X.png" % g["unicode"]))
                atlas.paste(im, ((k % cols) * (hgt + 4) + 1, (k // cols) * cell + 2))
        mx = max(g["offset"] + (g["width"] * g["height"] * 4 + 7) // 8 for g in nodes)
        open(os.path.join(d, "glyph_data_4bpp.bin"), "wb").write(raw[data - B:data - B + mx])        # surowe dane glifow (4 bpp, nibble niski pierwszy, upakowane ciagle)
        atlas.save(os.path.join(d, "atlas.png")); meta.append(dict(font=fi, height=hgt, glyphs=n, pixBelowBase=pbb, list="0x%08X" % lst, data="0x%08X" % data, bpp=4))
    json.dump(meta, open(os.path.join(out, "fonts.json"), "w"), indent=1); print("OK", len(FONTS), "czcionek")
if __name__ == "__main__": main(sys.argv[1], sys.argv[2])
