#!/usr/bin/env python3
"""E7: sklada prototyp/estyma_prototype/model.json z ui_model (menu_tree, lists, list_scales) - maly pakiet dla prototypu karty."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths
U = paths.UI_MODEL
mt = json.load(open(U / "menu_tree.json")); ls = json.load(open(U / "lists.json"))["lists"]; sc = json.load(open(U / "list_scales.json"))["lists"]
PL = {}
for k, v in json.load(open(U / "list_labels_pl.json"))["lists"].items():
    for i, r in v["rows"].items(): PL[(k, int(i))] = r["label_pl"]      # etykiety PL (klucz listy "0x00" = poczatek klucza lists.json)
scale_by_pid = {}
for lst in sc.values():
    for r in lst["rows"]:
        if r.get("pid"): scale_by_pid[r["pid"]] = {k: r.get(k) for k in ("scale", "decimals", "display", "leading_space")}
lists = {}
for k, rows in ls.items():
    lists[k] = [{"idx": r["idx"], "pid": r.get("pid"), "name": PL.get((k.split("|")[0], r["idx"]), r.get("name_en")), "level_min": r.get("level_min", 0), "kind": r.get("kind"),
                 "min": r.get("raw_min"), "max": r.get("raw_max"), "def": r.get("raw_default"), "fmt": scale_by_pid.get(r.get("pid"))} for r in rows]
model = {"source": "ui_model (STRONG/MEASURED wg plikow zrodlowych); dane wartosci = domyslne z firmware, NIE z kotla",
         "nodes": {n["id"]: {"title": n["title_pl"], "kind": n["kind"], "level_min": n["level_min"]} for n in mt["nodes"]},
         "menu_rows": [{k: r.get(k) for k in ("row", "title_pl", "target", "level_min", "config_cond", "embedded_control")} for r in mt["menu_rows"]],
         "edges": [{k: e.get(k) for k in ("from", "to", "level_min", "effect")} for e in mt["edges"]], "lists": lists}
out = Path(__file__).resolve().parents[1] / "prototyp/estyma_prototype/model.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(model, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"); print(out, out.stat().st_size)
