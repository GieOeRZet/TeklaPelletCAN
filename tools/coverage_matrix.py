#!/usr/bin/env python3
"""ETAP 3A: conservative UI appearance coverage matrix.

Important evidence rule:
- A screenshot is NOT reused across different gating configurations unless its
  filename/provenance explicitly identifies that configuration.
- Atlas filenames such as L1_17_screen prove level/row only; they do not prove
  0x350C/0x3525/etc. Therefore such a shot is assigned only to DEFAULT when
  DEFAULT is an explicit configuration, otherwise the cell remains OPEN.
- alarm/module_offline/dialog require dedicated captures.
- Renderer code and measured source data are never modified.

Usage:
  python3 -I tools/coverage_matrix.py
  python3 -I tools/coverage_matrix.py --threshold 5
"""
from __future__ import annotations
import argparse, csv, json, re
from pathlib import Path

STATES_SCREEN = ("default", "alarm", "module_offline")
STATES_DIALOG = ("dialog",)

def load_json(p):
    with p.open(encoding="utf-8") as f:
        return json.load(f)

def render_map(p):
    if not p.exists():
        return {}
    with p.open(encoding="utf-8", newline="") as f:
        return {r["screen"]: {"mae": float(r["mae"]), "pct_diff": float(r["pct_diff"])}
                for r in csv.DictReader(f)}

def filename_provenance(stem):
    """Return (level,row,kind,config,state) only when the filename encodes them."""
    # Supported explicit forms can be extended without changing acceptance logic.
    m = re.fullmatch(r"L(\d+)_(\d+)_(screen|settings)(?:__(.+))?", stem)
    if m:
        return int(m.group(1)), int(m.group(2)), m.group(3), (m.group(4) or "DEFAULT"), "default"
    m = re.fullmatch(r"L(\d+)_(\d+)_(screen|settings)_(alarm|module_offline|dialog)(?:__(.+))?", stem)
    if m:
        return int(m.group(1)), int(m.group(2)), m.group(3), (m.group(5) or "DEFAULT"), m.group(4)
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="analiza/FW2213TK-2026-11-22/data/ui_model")
    ap.add_argument("--threshold", type=float, default=5.0)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    root = Path(args.root)
    menu = load_json(root / "menu_tree.json")
    atlas_dir = root / "atlas"
    atlas = {p.stem: p for p in atlas_dir.glob("*.png")} if atlas_dir.exists() else {}
    renders = render_map(root / "render_eval.csv")

    rows_by_target = {}
    for row in menu.get("menu_rows", []):
        rows_by_target.setdefault(row.get("target"), []).append(row)

    # Build an exact screenshot index. No configuration is inferred from the
    # existence of a screen row in menu_tree.
    shot_index = {}
    for stem, p in atlas.items():
        prov = filename_provenance(stem)
        if prov:
            shot_index[prov] = p

    cells = []
    for node in menu.get("nodes", []):
        nid = node["id"]
        rows = rows_by_target.get(nid, [])
        states = STATES_DIALOG if node.get("kind") == "dialog" else STATES_SCREEN
        for level in range(4):
            cfgs = sorted({v.split("|", 1)[0]
                           for r in rows
                           for v in r.get("visible_in", [])
                           if v.endswith(f"|L{level}")})
            if not cfgs and level >= int(node.get("level_min", 0)):
                cfgs = ["DEFAULT"]
            for cfg in cfgs:
                for state in states:
                    shot = None
                    # HOME has an explicit H_home capture, but its provenance
                    # does not encode config/level; count it only for DEFAULT.
                    if state == "default":
                        if nid == "HOME" and cfg == "DEFAULT" and "H_home" in atlas:
                            shot = atlas["H_home"]
                        else:
                            # Find the menu row for this node and exact level.
                            for r in rows:
                                if not any(v.endswith(f"|L{level}") and v.split("|",1)[0] == cfg
                                           for v in r.get("visible_in", [])):
                                    continue
                                candidates = [
                                    (f"L{level}_{r['row']}_screen", "screen"),
                                    (f"L{level}_{r['row']}_settings", "settings"),
                                ]
                                for stem, kind in candidates:
                                    if stem in atlas:
                                        prov = filename_provenance(stem)
                                        if prov and prov[3] == cfg and prov[4] == state:
                                            shot = atlas[stem]
                                            break
                                if shot:
                                    break

                    ev = renders.get(shot.stem) if shot else None
                    cells.append({
                        "node": nid, "kind": node.get("kind"), "level": level,
                        "config": cfg, "state": state,
                        "screenshot": bool(shot),
                        "screenshot_ref": str(shot.relative_to(root)) if shot else None,
                        "render_eval": bool(ev),
                        "mae": ev["mae"] if ev else None,
                        "pct_diff": ev["pct_diff"] if ev else None,
                        "pass": bool(ev and ev["pct_diff"] < args.threshold),
                        "evidence": "STATIC-BASELINE-EXACT-CONFIG" if shot else "OPEN",
                    })

    covered = [c for c in cells if c["screenshot"]]
    evaluated = [c for c in cells if c["render_eval"]]
    passed = [c for c in cells if c["pass"]]
    result = {
        "schema_version": "1.1",
        "evidence": "STATIC-BASELINE",
        "firmware_sha256": menu.get("meta", {}).get("firmware_sha256"),
        "threshold_pct_diff": args.threshold,
        "method": {
            "nodes": "menu_tree.nodes",
            "levels": [0,1,2,3],
            "configurations": "menu_rows.visible_in exact signatures",
            "states": list(STATES_SCREEN) + ["dialog"],
            "visual_evidence": "atlas/*.png + render_eval.csv",
            "config_rule": "never infer gating config from row visibility; exact-config screenshot provenance required",
            "dynamic_backfill": "not performed automatically; missing cells remain OPEN"
        },
        "summary": {
            "cells": len(cells),
            "screenshots": len(covered),
            "render_eval": len(evaluated),
            "below_threshold": len(passed),
            "screenshot_coverage_pct": round(100*len(covered)/len(cells), 2) if cells else 0,
            "render_eval_coverage_pct": round(100*len(evaluated)/len(cells), 2) if cells else 0,
            "appearance_pass_pct_of_all_cells": round(100*len(passed)/len(cells), 2) if cells else 0,
            "appearance_pass_pct_of_evaluated": round(100*len(passed)/len(evaluated), 2) if evaluated else 0,
            "open_cells": len(cells)-len(covered)
        },
        "cells": cells,
    }
    out = Path(args.out) if args.out else root / "coverage_matrix.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    print(f"Wrote {out}")

if __name__ == "__main__":
    main()
