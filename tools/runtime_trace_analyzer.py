#!/usr/bin/env python3
"""Analyze RE-Harness JSON/JSONL traces and close indirect-call/object-flow gaps."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from collections import defaultdict

def load(path):
    text = Path(path).read_text(encoding="utf-8")
    try:
        obj = json.loads(text)
        events = obj.get("events", obj if isinstance(obj, list) else [])
    except json.JSONDecodeError:
        events = [json.loads(x) for x in text.splitlines() if x.strip()]
    return events

def hx(v):
    return f"0x{v:08X}" if isinstance(v, int) else str(v)

def analyze(events, focus=None):
    focus = set(focus or [])
    by_pc = defaultdict(list)
    edges = defaultdict(int)
    object_paths = defaultdict(list)
    for e in events:
        kind = str(e.get("kind","")).lower()
        pc = e.get("pc")
        target = e.get("target")
        if pc is not None:
            by_pc[pc].append(e)
        if kind in ("indirect_call","indirect-call") and pc is not None and target is not None:
            edges[(pc,target)] += 1
            obj = e.get("object_address")
            off = e.get("offset")
            if obj is not None:
                object_paths[(obj,off)].append(e)
    focus_hits = []
    for e in events:
        vals = [e.get("pc"), e.get("target"), e.get("address"), e.get("object_address")]
        if any(v in focus for v in vals):
            focus_hits.append(e)
    return {
        "event_count": len(events),
        "indirect_edges": [
            {"pc": pc, "target": target, "count": n}
            for (pc,target), n in sorted(edges.items())
        ],
        "object_paths": [
            {"object_address": obj, "offset": off, "events": len(es)}
            for (obj,off), es in sorted(object_paths.items())
        ],
        "focus_hits": focus_hits,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("trace")
    p.add_argument("--focus", action="append", default=[])
    p.add_argument("--out", default="runtime_trace_analysis")
    a=p.parse_args()
    r=analyze(load(a.trace), [int(x,0) for x in a.focus])
    o=Path(a.out); o.parent.mkdir(parents=True,exist_ok=True)
    o.with_suffix(".json").write_text(json.dumps(r,indent=2),encoding="utf-8")
    lines=["# Runtime Trace Analysis","",f"- events: {r['event_count']}","",
           "## Indirect edges","",
           "| PC | target | count |","|---:|---:|---:|"]
    for x in r["indirect_edges"]:
        lines.append(f"| {hx(x['pc'])} | {hx(x['target'])} | {x['count']} |")
    lines += ["","## Object paths","","| object | offset | events |","|---:|---:|---:|"]
    for x in r["object_paths"]:
        lines.append(f"| {hx(x['object_address'])} | {hx(x['offset']) if x['offset'] is not None else '-'} | {x['events']} |")
    o.with_suffix(".md").write_text("\n".join(lines),encoding="utf-8")

if __name__=="__main__":
    main()
