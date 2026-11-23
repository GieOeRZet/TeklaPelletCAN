#!/usr/bin/env python3
"""PASS 59: budowa UI-MODEL przez polaczenie widgetow z mapa prezenterow.

Wejscie:
  presenter_map.csv  - PASS 58, widget_offsets = offsets wzgledem aktywnego view
  widget JSON        - screen_inventory_menu.py / widget_inventory.py

Wyjscie:
  ui_model.json      - dane ekran -> widget -> presenter -> PID
  ui_model.csv       - plaska tabela do dalszej analizy
  ui_model_report.md - statystyka dopasowan i nierozwiazanych widgetow

Kluczowa zasada: view_off jest dowodem lokalizacji obiektu wzgledem widoku.
Nie zgadujemy PID po geometrii. Dokladne dopasowanie view_off jest zapisane jako
evidence=EXACT_VIEW_OFF; wiele kandydatow pozostaje wieloznacznych.
"""
import argparse
import csv
import json
import os
import re
from collections import Counter, defaultdict

def hx(v):
    if v is None or v == "":
        return None
    if isinstance(v, int):
        return v
    s = str(v).strip()
    try:
        return int(s, 16) if s.lower().startswith("0x") else int(s)
    except Exception:
        return None

def load_presenters(path):
    rows = []
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            offs = []
            for x in (r.get("widget_offsets") or "").split("|"):
                n = hx(x)
                if n is not None:
                    offs.append(n)
            r = dict(r)
            r["cluster_start_i"] = hx(r.get("cluster_start"))
            r["site_i"] = hx(r.get("site"))
            r["ui_key_i"] = hx(r.get("ui_key"))
            r["pid_i"] = hx(r.get("pid"))
            r["setter_i"] = hx(r.get("setter"))
            r["widget_offsets_i"] = offs
            rows.append(r)
    return rows

def load_widgets(path):
    with open(path, encoding="utf-8") as f:
        obj = json.load(f)
    if isinstance(obj, dict):
        for k in ("nodes", "screens", "widgets", "results"):
            if isinstance(obj.get(k), list):
                obj = obj[k]
                break
        else:
            obj = [obj]
    out = []
    for item in obj:
        if not isinstance(item, dict):
            continue
        if "widgets" in item and isinstance(item["widgets"], list):
            node = {k: v for k, v in item.items() if k != "widgets"}
            for w in item["widgets"]:
                d = dict(w)
                for k in ("node","parent","tap","title"):
                    if k in node and k not in d:
                        d[k] = node[k]
                out.append(d)
        else:
            out.append(dict(item))
    return out

def bind(widgets, presenters, active=None):
    """active (PASS 61, presenter_trace.py): {node: {sites: {site: [keys]}, setters: {setter: ["view"|r0]}}}.
    Gdy podane, kandydat jest AKTYWNY tylko jesli jego setter zostal wykonany na tym wezle z r0 == aktywny widok
    (dowod, ze setter nalezy do klasy widoku tego ekranu). Wiazanie statyczne zostaje w binding_static."""
    by_off = defaultdict(list)
    for pidx, p in enumerate(presenters):
        for off in set(p["widget_offsets_i"]):
            by_off[off].append((pidx, p))
    out = []
    for widx, w in enumerate(widgets):
        vo = hx(w.get("view_off"))
        matches = by_off.get(vo, []) if vo is not None else []
        candidates = []
        for pidx, p in matches:
            candidates.append({
                "presenter_row": pidx,
                "presenter_cluster": p.get("presenter_cluster"),
                "cluster_start": p.get("cluster_start"),
                "site": p.get("site"),
                "ui_key": p.get("ui_key"),
                "pid": p.get("pid"),
                "name": p.get("name"),
                "setter": p.get("setter"),
                "formats": p.get("formats"),
                "div10": int(p.get("div10") or 0),
                "evidence": "EXACT_VIEW_OFF",
            })
        d = dict(w)
        d["view_off_i"] = vo
        d["binding"] = "EXACT_VIEW_OFF" if len(candidates) == 1 else (
            "AMBIGUOUS_VIEW_OFF" if len(candidates) > 1 else "UNRESOLVED_VIEW_OFF"
        )
        if active is not None:
            act = active.get(str(w.get("node")))
            d["binding_static"] = d["binding"]
            if act is None:
                d["binding"] = "NO_ACTIVE_TRACE"
            else:
                on_view = {hx(k) for k, v in act.get("setters", {}).items() if "view" in v}
                sites = {hx(k) for k in act.get("sites", {})}
                for c in candidates:
                    c["setter_on_view"] = hx(c["setter"]) in on_view
                    c["site_executed"] = hx(c["site"]) in sites
                    if c["setter_on_view"]:
                        c["evidence"] = "EXACT_ACTIVE_VIEW_OFF"
                live = [c for c in candidates if c["setter_on_view"]]
                if candidates:
                    candidates = live
                d["binding"] = ("EXACT_ACTIVE_VIEW_OFF" if len(live) == 1 else "AMBIGUOUS_ACTIVE_VIEW_OFF" if len(live) > 1
                                else "INACTIVE_VIEW_OFF" if d["binding_static"] != "UNRESOLVED_VIEW_OFF" else "UNRESOLVED_VIEW_OFF")
        d["presenter_candidates"] = candidates
        out.append(d)
    return out

def flat_rows(model):
    rows = []
    for i, w in enumerate(model):
        cands = w.get("presenter_candidates") or [None]
        for c in cands:
            rows.append({
                "widget_index": i,
                "node": w.get("node"),
                "parent": w.get("parent"),
                "tap": w.get("tap"),
                "title": w.get("title"),
                "this": w.get("this", w.get("addr")),
                "view_off": w.get("view_off"),
                "role": w.get("role", w.get("type")),
                "x": w.get("x"),
                "y": w.get("y"),
                "w": w.get("w"),
                "h": w.get("h"),
                "touch": w.get("touch"),
                "vis": w.get("vis"),
                "text_id": w.get("text_id", w.get("id")),
                "bitmap_id": w.get("bitmap_id"),
                "wildcard": w.get("wildcard"),
                "binding": w.get("binding"),
                "presenter_row": None if c is None else c["presenter_row"],
                "presenter_cluster": None if c is None else c["presenter_cluster"],
                "site": None if c is None else c["site"],
                "ui_key": None if c is None else c["ui_key"],
                "pid": None if c is None else c["pid"],
                "name": None if c is None else c["name"],
                "setter": None if c is None else c["setter"],
                "formats": None if c is None else c["formats"],
                "div10": None if c is None else c["div10"],
            })
    return rows

def write_csv(path, rows):
    fields = list(rows[0]) if rows else ["widget_index","binding"]
    with open(path, "w", encoding="utf-8", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=fields)
        wr.writeheader()
        wr.writerows(rows)

def report(model, presenters, outpath, csv_path=None):
    cnt = Counter(w["binding"] for w in model)
    extra = [f"- {k}: **{v}**" for k, v in sorted(cnt.items()) if k not in ("EXACT_VIEW_OFF", "AMBIGUOUS_VIEW_OFF", "UNRESOLVED_VIEW_OFF")]
    exact = cnt["EXACT_VIEW_OFF"]
    amb = cnt["AMBIGUOUS_VIEW_OFF"]
    unresolved = cnt["UNRESOLVED_VIEW_OFF"]
    used = Counter()
    for w in model:
        for c in w["presenter_candidates"]:
            used[c["presenter_row"]] += 1
    unique_presenters = len(used)
    lines = [
        "# PASS 59 — UI-MODEL",
        "",
        "Metoda: dokladne laczenie widget.view_off z presenter_map.widget_offsets.",
        "Nie wybieramy PID przy wieloznacznym dopasowaniu; kandydaci sa zachowani.",
        "",
        "## Wynik",
        f"- widgety: **{len(model)}**",
        f"- EXACT_VIEW_OFF (1 kandydat): **{exact}**",
        f"- AMBIGUOUS_VIEW_OFF (>1 kandydat): **{amb}**",
        f"- UNRESOLVED_VIEW_OFF (brak): **{unresolved}**",
        f"- uzyte wiersze mapy prezenterow: **{unique_presenters}/{len(presenters)}**",
    ] + extra + [
        "",
        "## Status dowodu",
        "- EXACT_VIEW_OFF = silne powiazanie obiektu widgetu z lokalnym slotem prezentera.",
        "- PID/nazwa sa nadal danymi prezentera; nie sa dowodem, ze widget jest semantycznie wyswietlany bez dodatkowego sledzenia.",
        "- AMBIGUOUS_VIEW_OFF pozostaje OPEN do rozstrzygniecia przez konstruktor/ekran.",
        "- UNRESOLVED_VIEW_OFF wymaga kolejnego przebiegu trace lub uzupelnienia mapy.",
        "",
        "## Nastepny krok",
        "Przeniesc UI-MODEL do grafu akcji: widget touch -> handler -> zmiana PID/ekran/dialog/CAN.",
    ]
    if csv_path:
        lines.append(f"- tabela plaska: {csv_path}")
    with open(outpath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("presenter_csv")
    ap.add_argument("widget_json")
    ap.add_argument("out_json")
    ap.add_argument("--csv", dest="csv_out")
    ap.add_argument("--report")
    ap.add_argument("--active", help="presenter_trace.py JSON: zaweza kandydatow do setterow wykonanych na widoku wezla")
    args = ap.parse_args()
    p = load_presenters(args.presenter_csv)
    w = load_widgets(args.widget_json)
    active = json.load(open(args.active, encoding="utf-8")) if args.active else None
    model = bind(w, p, active)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump({
            "schema": "NewEstyma.UIModel/1",
            "evidence_rule": "EXACT_VIEW_OFF",
            "presenter_source": os.path.abspath(args.presenter_csv),
            "widget_source": os.path.abspath(args.widget_json),
            "presenters": len(p),
            "widgets": len(model),
            "items": model,
        }, f, ensure_ascii=False, indent=2)
    rows = flat_rows(model)
    if args.csv_out:
        write_csv(args.csv_out, rows)
    if args.report:
        report(model, p, args.report, args.csv_out)
    print(json.dumps({
        "presenters": len(p),
        "widgets": len(model),
        "exact": sum(x["binding"] == "EXACT_VIEW_OFF" for x in model),
        "ambiguous": sum(x["binding"] == "AMBIGUOUS_VIEW_OFF" for x in model),
        "unresolved": sum(x["binding"] == "UNRESOLVED_VIEW_OFF" for x in model),
        "all": dict(Counter(x["binding"] for x in model)),
    }))

if __name__ == "__main__":
    main()
