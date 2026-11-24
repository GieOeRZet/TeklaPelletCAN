#!/usr/bin/env python3
"""PASS 67: renderer UI Z DANYCH (bez emulatora): rysuje ekran z inwentarza widgetow (pozycje, bitmapy, teksty, czcionki, kolory pudelek), bitmap PNG i glifow 4 bpp.
Uzycie: ui_render.py INV.json WEZEL OUT.png [--extras EXTRAS.json]   (INV.json = lista wezlow {node, widgets})
Model: tlo = kolor Box 0x2945 (41,40,41); widget 'image' -> bitmapa id (data/bitmaps/png/NNN.png); 'text' -> tekst (text_pl, \\x02 = wildcard) czcionka font 0..5, wyrownanie 0=L 1=C 2=R;
'other' z kolorem w extras (vptr Box + kolor RGB565 +0x28, alfa +0x26) -> prostokat. Kolejnosc rysowania = kolejnosc w inwentarzu (po adresie)."""
import csv, json, os, sys
from PIL import Image
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analiza_archiwum", "FW2213TK-2026-11-22", "data")
FONTS = [("font0_h12", 12, 3), ("font1_h20", 20, 5), ("font2_h26", 26, 6), ("font3_h36", 36, 8), ("font4_h64", 64, 9), ("font5_h92", 92, 12)]
BG = (41, 40, 41); DY = 0
_fc = {}; _bc = {}
def font(i):
    if i not in _fc:
        name, h, pbb = FONTS[i]; d = os.path.join(D, "fonts", name); g = {}
        for r in csv.DictReader(open(os.path.join(d, "glyphs.csv"))): g[int(r["unicode"], 16)] = dict(w=int(r["width"]), h=int(r["height"]), top=int(r["top"]), left=int(r["left"]), adv=int(r["advance"]), off=int(r["data_offset"]))
        _fc[i] = (g, open(os.path.join(d, "glyph_data_4bpp.bin"), "rb").read(), h, pbb)
    return _fc[i]
def glyph_alpha(i, ch):
    g, data, h, pbb = font(i); gl = g.get(ord(ch))
    if gl is None: return None, None
    w, hh = gl["w"], gl["h"]; px = []
    for k in range(w * hh):
        b = data[gl["off"] + k // 2]; px.append(((b >> 4) if k % 2 else (b & 15)) * 17)          # nibble niski pierwszy
    return (Image.frombytes("L", (w, hh), bytes(px)) if w * hh else None), gl
def text_width(i, s): g = font(i)[0]; return sum(g.get(ord(c), dict(adv=0))["adv"] for c in s)
def draw_text(img, i, s, x, y, w, align, color=(255, 255, 255)):
    g, data, h, pbb = font(i); tw = text_width(i, s)
    cx = x + (0 if align == 0 else (w - tw) // 2 if align == 1 else w - tw); base = y + h                      # linia bazowa glifow = gorna krawedz + wysokosc czcionki (skalibrowane na atlasie: dy = pixBelowBase wzgledem y+h-pbb)
    for c in s:
        a, gl = glyph_alpha(i, c)
        if gl is None: continue
        if a is not None:
            gx, gy = cx + gl["left"], base - gl["top"]
            layer = Image.new("RGB", a.size, color); img.paste(layer, (gx, gy), a)
        cx += gl["adv"]
def bitmap(i):
    if i not in _bc:
        f = os.path.join(D, "bitmaps", "png", "%03d.png" % i); _bc[i] = Image.open(f).convert("RGBA") if os.path.exists(f) else None
    return _bc[i]
def rgb565(v): r, g, b = v >> 11 & 31, v >> 5 & 63, v & 31; return (r << 3 | r >> 2, g << 2 | g >> 4, b << 3 | b >> 2)
def clip_rect(w, W):                          # przeciecie prostokatow wszystkich przodkow (kontenery TouchGFX/ScrollableContainer przycinaja potomkow)
    x0, y0, x1, y1 = w["ax"], w["ay"], w["ax"] + w["w"], w["ay"] + w["h"]; a = W.get(w["parent"]); n = 0; cx0, cy0, cx1, cy1 = 0, 0, 480, 272
    while a is not None and n < 20:
        if a["w"] > 0 and a["h"] > 0 and a["w"] < 2000:
            cx0, cy0, cx1, cy1 = max(cx0, a["ax"]), max(cy0, a["ay"]), min(cx1, a["ax"] + a["w"]), min(cy1, a["ay"] + a["h"])
        a = W.get(a["parent"]); n += 1
    return (cx0, cy0, cx1, cy1), (x0 < cx0 or y0 < cy0 or x1 > cx1 or y1 > cy1)
def draw_text_ml(img, i, s, x, y, w, align, color):          # wiele linii: krok = wysokosc czcionki + piksele pod linia bazowa
    s = s.replace("\\n", "\n"); step = font(i)[2] + font(i)[3]      # typedtext zawiera tez literalne \\n
    for k, ln in enumerate(s.split("\n")):
        if ln: draw_text(img, i, ln, x, y + k * step, w, align, color)
def render(widgets, extras=None, size=(480, 272), dim=None):          # dim=(alfa, z_progu): przed pierwszym widgetem o z>=z_progu rysowana jest czarna nakladka o danej alfie (okno modalne)
    img = Image.new("RGB", size, BG); W = {w["this"]: w for w in widgets}
    def visible(w):
        a = w; n = 0
        while a is not None and n < 20:
            if a["vis"] != 1: return False
            a = W.get(a["parent"]); n += 1
        return True
    if extras and any("z" in e for e in extras.values()): widgets = sorted(widgets, key=lambda w: (extras.get(w["this"]) or {}).get("z", 10**6))
    dimmed = dim is None
    for w in widgets:
        if not dimmed and ((extras or {}).get(w["this"]) or {}).get("z", -1) >= dim[1]:
            img = Image.composite(Image.new("RGB", size, (0, 0, 0)), img, Image.new("L", size, dim[0])); dimmed = True
        if w["w"] <= 0 or w["h"] <= 0 or w["w"] > 2000 or (extras is None and not visible(w)) or w["ax"] > 480 or w["ay"] > 272 or w["ax"] + w["w"] < 0 or w["ay"] + w["h"] < 0: continue
        ex = (extras or {}).get(w["this"])
        if ex and ex.get("hidden"): continue                       # efektywna niewidocznosc wg RAM biezacego punktu kontrolnego
        crect, needclip = clip_rect(w, W); base = img.copy() if needclip else None
        if ex and ex.get("cls") == "box":
            col = rgb565(ex["box"]); al = ex.get("alpha", 255)
            if (w["w"], w["h"]) == (480, 272) and col == BG and al >= 255: continue          # pelnoekranowe tlo; polprzezroczysta nakladka (dialog) rysowana
            layer = Image.new("RGB", (w["w"], w["h"]), col); img.paste(layer, (w["ax"], w["ay"]), Image.new("L", (w["w"], w["h"]), al))
        elif w["role"] == "image" and w.get("bitmap_id") is not None:
            b = bitmap(w["bitmap_id"])
            if b is not None: img.paste(b.convert("RGB"), (w["ax"], w["ay"]), b.getchannel("A"))
        elif ex and ex.get("cls") == "btn":
            b = bitmap(ex["bmp"])
            if b is not None: img.paste(b.convert("RGB"), (w["ax"], w["ay"]), b.getchannel("A"))
            if ex.get("icon"):
                ib = bitmap(ex["icon"])
                if ib is not None: img.paste(ib.convert("RGB"), (w["ax"] + ex["icon_xy"][0], w["ay"] + ex["icon_xy"][1]), ib.getchannel("A"))
        elif ex and ex.get("cls") == "text":
            if ex.get("bg") is not None:
                bb = bitmap(ex["bg"])
                if bb is not None: img.paste(bb.convert("RGB"), (w["ax"], w["ay"]), bb.getchannel("A"))
            ty = w["ay"] + DY + ((w["h"] - font(ex["font"])[2] - font(ex["font"])[3]) // 2 if ex.get("bg") is not None else 0)       # etykieta przycisku: pionowo wysrodkowana
            if ex["text"]: draw_text_ml(img, ex["font"], ex["text"], w["ax"], ty, w["w"], ex["align"], rgb565(ex["color"]))
        elif w["role"] == "text" and (w.get("text_pl") or w.get("wildcard")):
            s = (w.get("text_pl") or "\x02").replace("\x02", w.get("wildcard") or "")
            draw_text(img, w.get("font") or 0, s, w["ax"], w["ay"] + DY, w["w"], w.get("align") or 0)
        if base is not None:
            m = Image.new("L", size, 0); m.paste(255, crect); img = Image.composite(img, base, m)
    return img
if __name__ == "__main__":
    inv = {n["node"]: n for n in json.load(open(sys.argv[1]))}; ex = json.load(open(sys.argv[sys.argv.index("--extras") + 1])) if "--extras" in sys.argv else None
    render(inv[sys.argv[2]]["widgets"], ex).save(sys.argv[3]); print("OK", sys.argv[3])
