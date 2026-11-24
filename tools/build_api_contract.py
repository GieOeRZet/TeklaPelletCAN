#!/usr/bin/env python3
"""E6: buduje kontrakt API <-> ui_model: mapowanie PID panelu -> punkt urzadzenia/encja HA (rejestry/odczyty.csv, punkty.csv)
oraz raport pokrycia. Wyjscie: ui_model/pid_to_point.json + ui_model/API_KONTRAKT.md (czesc generowana miedzy znacznikami)."""
import csv, json, sys, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths
N = lambda s: "0x%04X" % int(str(s), 16)

odczyty = {N(r["indeks"]): r for r in csv.DictReader(open(paths.ROOT / "rejestry/odczyty.csv", encoding="utf-8"))}
punkty = {N(r["indeks"]): r for r in csv.DictReader(open(paths.ROOT / "rejestry/punkty.csv", encoding="utf-8"))}
lists = json.load(open(paths.UI_MODEL / "lists.json"))["lists"]
live = json.load(open(paths.UI_MODEL / "live_sources.json"))

by_pid = collections.OrderedDict()
for lk, rows in lists.items():
    for r in rows:
        if not r.get("pid"): continue
        p = N(r["pid"]); e = by_pid.setdefault(p, {"pid": p, "name_en": r.get("name_en"), "lists": [], "kind": r.get("kind"), "raw_min": r.get("raw_min"), "raw_max": r.get("raw_max")})
        e["lists"].append(lk)
for p, e in by_pid.items():
    o, k = odczyty.get(p), punkty.get(p)
    e["point_id"] = o["id"] if o else None
    e["write_key"] = (k["klucz"] if k else (o["klucz_zapisu"] if o and o["klucz_zapisu"] else None))
    e["read"] = ("odczyty:" + o["odczyt"]) if o else ("punkty (zapis)" if k else None)
    e["entity"] = ("%s.<node>_%s" % ({"sensor": "sensor", "binary_sensor": "binary_sensor", "enum": "select"}.get(o["rodzaj"], "sensor"), o["id"])) if o else None
    e["status"] = "MAPPED" if (o or k) else "NO_DEVICE_POINT"
out = {"schema_version": "1.0.0", "evidence": "STRONG (statyczny join, nie zmierzony): join ui_model/lists.json (PID panelu) z rejestry/odczyty.csv i punkty.csv po indeksie", "pids": list(by_pid.values())}
(paths.UI_MODEL / "pid_to_point.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
c = collections.Counter(e["status"] for e in by_pid.values())
miss = [e for e in by_pid.values() if e["status"] != "MAPPED"]
live_pids = set()
def walk(x):
    if isinstance(x, dict):
        for v in x.values(): walk(v)
    elif isinstance(x, list):
        for v in x: walk(v)
    elif isinstance(x, str) and len(x) == 6 and x.lower().startswith("0x"):
        try: live_pids.add(N(x))
        except ValueError: pass
walk(live)
gen = ["<!-- BEGIN GENERATED -->", "", "## Pokrycie PID listy panelu -> punkty urzadzenia (generowane: tools/build_api_contract.py)", "",
       f"PID w listach ui_model: **{len(by_pid)}**; zmapowane na punkt odczytu/zapisu: **{c['MAPPED']}**; bez punktu w urzadzeniu: **{c['NO_DEVICE_POINT']}**.", "",
       f"PID zrodel live (`live_sources.json`): {len(live_pids)}, z czego z punktem odczytu: {sum(1 for p in live_pids if p in odczyty)}.", "",
       "Brakujace (kandydaci do dodania w `rejestry/odczyty.csv`/`punkty.csv` - decyzja wlasciciela, to zmiana katalogu urzadzenia):", "",
       "| PID | nazwa (EN) | listy |", "|---|---|---|"]
gen += [f"| {e['pid']} | {e['name_en']} | {', '.join(sorted(set(e['lists']))).replace('|','/')[:60]} |" for e in miss]
gen += ["", "<!-- END GENERATED -->"]
doc = paths.UI_MODEL / "API_KONTRAKT.md"
txt = doc.read_text(encoding="utf-8") if doc.exists() else ""
if "<!-- BEGIN GENERATED -->" in txt:
    a = txt.index("<!-- BEGIN GENERATED -->"); b = txt.index("<!-- END GENERATED -->") + len("<!-- END GENERATED -->")
    txt = txt[:a] + "\n".join(gen) + txt[b:]
else:
    txt += "\n" + "\n".join(gen) + "\n"
doc.write_text(txt, encoding="utf-8")
print(dict(c), "live", len(live_pids))
