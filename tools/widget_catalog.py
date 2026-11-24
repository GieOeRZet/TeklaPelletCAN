#!/usr/bin/env python3
"""PASS 57: katalog 'ekran -> widgety' z inv_*.json (tools/screen_inventory.py): tytul, dla kazdego widgetu: rola, pozycja bezwzgledna (ax,ay), rozmiar, bitmapa (id/rozmiar), tekst PL (id wzgledny+57), czcionka/wyrownanie, wildcard (zawartosc bufora), dotykowosc.
python3 -I tools/widget_catalog.py OUT.md IN.json [...]"""
import collections, csv, json, os, sys
out = sys.argv[1]; screens = []
for f in sys.argv[2:]: screens += json.load(open(f))
man = {}
mp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analiza_archiwum", "FW2213TK-2026-11-22", "data", "bitmaps", "manifest.csv")
if os.path.exists(mp): man = {int(r["id"]): "%sx%s" % (r["width"], r["height"]) for r in csv.DictReader(open(mp))}
FN = {0: "12px", 1: "20px", 2: "26px", 3: "36px", 4: "64px", 5: "92px"}; AL = {0: "L", 1: "C", 2: "R"}
groups = collections.OrderedDict()
for s in screens:
    t = s["title"] or "(bez tytulu: ekran glowny / okno)"
    vis = [w for w in s["widgets"] if w["vis"] and (w["role"] != "other" or w["touch"])]
    sig = (tuple(sorted(w["bitmap_id"] for w in vis if w["role"] == "image" and w["bitmap_id"] is not None)), tuple(sorted((w.get("text_id") or 0) for w in vis if w["role"] == "text")))
    groups.setdefault(t, {}).setdefault(sig, s)
md = ["# KATALOG WIDGETOW wg ekranow (z sledzenia konstrukcji TouchGFX w emulatorze)\n",
      "Wspolrzedne (ax,ay) bezwzgledne na ekranie 480x272. Tekst = TypedText (id wzgledny, tekst PL = pl(id+57)); wildcard = zawartosc bufora tekstu dynamicznego w chwili zrzutu. Widgety `other` dotykowe = przyciski/kontrolki.\n"]
for t, vs in groups.items():
    md.append("\n## %s  (%d wariantow)\n" % (t, len(vs)))
    for k, (sig, s) in enumerate(vs.items()):
        if k >= 2: md.append("_... kolejne warianty (%d) pominiete_\n" % (len(vs) - 2)); break
        ws = [w for w in s["widgets"] if w["vis"]]; md.append("**Wariant %d** (wezel %s, tap %s, %d widgetow)\n" % (k + 1, s["node"], s["tap"], len(ws)))
        md.append("| rola | ax,ay | w×h | zasob | szczegoly |\n|---|---|---|---|---|")
        for w in sorted(ws, key=lambda w: (w["ay"], w["ax"])):
            if w["role"] == "other" and not w["touch"]: continue
            if w["ax"] + w["w"] <= 0 or w["ay"] + w["h"] <= 0 or w["ax"] >= 480 or w["ay"] >= 272: continue
            if w["role"] == "image": res = "bitmapa %s (%s)" % (w["bitmap_id"], man.get(w["bitmap_id"], "?")); det = ""
            elif w["role"] == "text": res = "tekst %s" % w.get("text_id"); det = "%r font %s %s%s" % (w.get("text_pl", ""), FN.get(w.get("font"), "?"), AL.get(w.get("align"), "?"), (" wildcard=%r" % w["wildcard"]) if w.get("wildcard") else "")
            else: res = ""; det = "kontrolka dotykowa"
            md.append("| %s | %d,%d | %d×%d | %s | %s |" % (w["role"], w["ax"], w["ay"], w["w"], w["h"], res, det.replace("|", "/")))
        md.append("")
open(out, "w", encoding="utf-8").write("\n".join(md)); print("ekrany (tytuly):", len(groups))
