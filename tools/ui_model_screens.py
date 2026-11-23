#!/usr/bin/env python3
"""PASS 61: czytelny katalog "ekran -> widget -> dane" z wyniku tools/ui_model.py (jeden lub wiecej plikow ui_model.json).
Dla kazdego wezla: widgety z wiazaniem dynamicznym (DYNAMIC_WRITE*, EXACT_ACTIVE_VIEW_OFF) z pozycja, rola, tekstem/bitmapa,
kluczem UI, PID, nazwa, formatem i polami zapisanymi przez setter. Uzycie:
  python3 -I tools/ui_model_screens.py OUT.md L0=ui_model_L0.json L2=ui_model_L2.json"""
import json, sys
from collections import Counter

GOOD = ("DYNAMIC_WRITE", "DYNAMIC_WRITE_MULTI", "EXACT_ACTIVE_VIEW_OFF")

def main(out, *specs):
    lines = ["# UI-MODEL — ekran -> widget -> dane (PASS 61)", "",
             "Wiazania: DYNAMIC_WRITE = zaobserwowany zapis settera prezentera w obiekt widgetu / jego bufor tekstu (emulator); "
             "EXACT_ACTIVE_VIEW_OFF = statyczny offset settera wykonanego na tym widoku. Pozycja = ax,ay (ekran), w x h.", ""]
    tot = Counter()
    for spec in specs:
        tag, path = spec.split("=", 1)
        items = json.load(open(path, encoding="utf-8"))["items"]
        nodes = {}
        for w in items: nodes.setdefault(w.get("node"), []).append(w)
        lines.append("## Poziom %s" % tag); lines.append("")
        for node, ws in nodes.items():
            c = Counter(w["binding"] for w in ws); tot.update(c)
            good = [w for w in ws if w["binding"] in GOOD]
            title = ws[0].get("title") or ""
            lines.append("### %s %s — widgetow %d, powiazanych %d" % (node, title, len(ws), len(good)))
            if not good: lines.append(""); continue
            lines.append(""); lines.append("| ax,ay | w x h | rola | tekst/bitmapa | klucz | PID | nazwa | format | pola | dowod |")
            lines.append("|---|---|---|---|---|---|---|---|---|---|")
            for w in sorted(good, key=lambda w: (w.get("ay", 0), w.get("ax", 0))):
                for cnd in w["presenter_candidates"]:
                    tb = (w.get("text_pl") or w.get("wildcard") or "") if w.get("role") == "text" else ("bmp %s" % w.get("bitmap_id") if w.get("bitmap_id") is not None else "")
                    tb = str(tb).replace("|", "/").replace("\n", " ")[:30]
                    f = ",".join(str(x) for x in (cnd.get("fields") or [])[:6])
                    lines.append("| %s,%s | %sx%s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                        w.get("ax"), w.get("ay"), w.get("w"), w.get("h"), w.get("role"), tb, cnd.get("ui_key") or "",
                        cnd.get("pid") or "", (cnd.get("name") or "")[:40], (cnd.get("formats") or "").replace("|", "/"), f, w["binding"]))
            lines.append("")
    lines.insert(3, "Suma wiazan: " + ", ".join("%s=%d" % kv for kv in sorted(tot.items())) + "\n")
    open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(dict(tot))

if __name__ == "__main__":
    main(*sys.argv[1:])
