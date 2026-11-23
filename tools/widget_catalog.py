#!/usr/bin/env python3
"""PASS 55: z widgets_*.json (widget_inventory) generuje katalog 'ekran -> widgety' (markdown): tytul (TextArea y<46 wysrodkowany), liczba widgetow,
bitmapy (id, rozmiar), teksty PL, kontrolki dotykowe (pozycje), typy po vptr. Dedupe po tytule i zestawie bitmap/tekstow.
python3 -I tools/widget_catalog.py OUT.md IN.json [...]"""
import collections, json, sys
out = sys.argv[1]; screens = []
for f in sys.argv[2:]: screens += json.load(open(f))
def title(ws):
    c = [w for w in ws if w["type"] == "TextArea" and w["y"] < 46 and 190 < w["x"] + w["w"] // 2 < 290 and w.get("text_pl")]
    return c[0]["text_pl"].strip() if c else ""
groups = collections.OrderedDict()
for s in screens:
    t = title(s["widgets"]) or "(bez tytulu/ekran glowny lub okno)"; sig = (tuple(sorted(w.get("bitmap", 0) for w in s["widgets"] if w["type"] == "Image")), tuple(sorted(w.get("text_pl", "") for w in s["widgets"] if w["type"] == "TextArea")))
    groups.setdefault(t, {})
    groups[t].setdefault(sig, s)
md = ["# KATALOG WIDGETOW wg ekranow (emulacja, widgety aktywnego widoku TouchGFX)\n", "Typ: Image = bitmapa (id wg `data/bitmaps/manifest.csv`), TextArea = tekst (TypedText), inne = vptr klasy (kontenery/przyciski/pola). x,y = wspolrzedne ekranowe, t = dotykowy.\n"]
for t, vs in groups.items():
    md.append("\n## %s  (%d wariantow)\n" % (t, len(vs)))
    for k, (sig, s) in enumerate(vs.items()):
        if k >= 3: md.append("_... kolejne warianty pominiete (%d)_\n" % (len(vs) - 3)); break
        ws = s["widgets"]; md.append("**Wariant %d** (`%s`, %d widgetow)\n" % (k + 1, s["state"], len(ws)))
        imgs = [w for w in ws if w["type"] == "Image"]; txt = [w for w in ws if w["type"] == "TextArea"]; btn = [w for w in ws if w["touch"] and w["type"] not in ("Image", "TextArea")]
        if imgs: md.append("- bitmapy: " + ", ".join("%d(%s)@%d,%d" % (w["bitmap"], w["bmp_size"], w["x"], w["y"]) for w in imgs if "bitmap" in w))
        if txt: md.append("- teksty: " + "; ".join("%r@%d,%d" % (w["text_pl"], w["x"], w["y"]) for w in txt))
        if btn: md.append("- kontrolki dotykowe: " + ", ".join("%d,%d %dx%d" % (w["x"], w["y"], w["w"], w["h"]) for w in btn))
        md.append("")
open(out, "w", encoding="utf-8").write("\n".join(md)); print("ekranow-tytulow:", len(groups))
