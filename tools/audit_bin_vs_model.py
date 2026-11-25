#!/usr/bin/env python3
"""Audyt: binarka (decompiled.c + tabele) kontra dane w ui_model. Pokazuje, co jest w sofcie, a nie jest jeszcze opisane/przypisane.
Przekroje: (1) PID-y czytane przez UI vs wzmianki w danych, (2) presentery (funkcje czytajace model) vs znane ekrany, (3) teksty TypedText: statycznie w kodzie vs widziane w emulatorze,
(4) bitmapy: statycznie w kodzie vs widziane, (5) klasy widgetow (vtable) i gdzie wystepuja.
Uzycie: python3 tools/audit_bin_vs_model.py OUT.json   (tylko odczyt plikow repo; bez emulatora)"""
import csv, glob, json, os, re, sys, collections

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
D = os.path.join(ROOT, "analiza_archiwum", "FW2213TK-2026-11-22", "data")
UI = os.path.join(D, "ui_model")
out = sys.argv[1]

src = open(os.path.join(ROOT, "firmware", "FW2213TK-ghidra", "decompiled.c"), encoding="utf-8", errors="replace").read()
parts = re.split(r"\n// (0[0-9a-f]{7})\n", src)
F = {parts[i]: parts[i + 1] for i in range(1, len(parts), 2)}

# ---------- dane modelu (tekst do wyszukiwania wzmianek)
SKIP = ("device_model.json", "INDEX.json", "coverage_matrix", "schema")
docs = {}
for f in glob.glob(os.path.join(UI, "**", "*.json"), recursive=True):
    if any(s in f for s in SKIP) or "/bind_raw/" in f or "/atlas/" in f or "/extras/" in f or "/dialog_shots/" in f or "/dialog_render/" in f:
        continue
    docs[f] = open(f, encoding="utf-8", errors="replace").read().lower()
doc_all = "\n".join(docs.values())
catalog = open(os.path.join(ROOT, "rejestry", "katalog-rejestrow.csv"), encoding="utf-8", errors="replace").read().lower()

# ---------- (1) PID-y
pm = list(csv.DictReader(open(os.path.join(D, "pid_matrix_655.csv"), encoding="utf-8-sig")))
t2 = {int(r["ui_key"], 16): r for r in csv.DictReader(open(os.path.join(D, "cg_ui_key_pid_t2_full.csv")))}
t1 = {int(r["ui_key"], 16): r for r in csv.DictReader(open(os.path.join(D, "cg_ui_key_pid_t1_full.csv")))}
getter = re.compile(r"FUN_08036ff2\([^,;]+,\s*(?:\(?\w+\)?\s*\+\s*)?(0x[0-9a-fA-F]+|\d+)\)")
keys_static = collections.defaultdict(set)         # ui_key -> presentery
for a, b in F.items():
    for m in getter.finditer(b):
        keys_static[int(m.group(1), 0)].add(a)
pid_rows = {}
for r in pm:
    p = r["pid"].lower()
    n = len(re.findall(re.escape(p), doc_all))
    pid_rows[p] = dict(pid=r["pid"], name=r["name"], mode=r["mode"], ui_keys=r["ui_keys"], mentions=n, in_catalog=p in catalog)
read_by_code = {}
for k, pres in keys_static.items():
    row = t2.get(k) or t1.get(k)
    if row:
        read_by_code.setdefault(row["pid"].lower(), set()).update(pres)
gaps = []
for p, pres in sorted(read_by_code.items()):
    row = pid_rows.get(p)
    if row and row["mentions"] == 0:
        gaps.append(dict(pid=p, name=row["name"], mode=row["mode"], presenters=sorted(pres), in_catalog=row["in_catalog"]))
unmentioned_all = [dict(pid=p, name=r["name"], mode=r["mode"], ui_keys=r["ui_keys"], in_catalog=r["in_catalog"]) for p, r in pid_rows.items() if r["mentions"] == 0]

# ---------- (2) presentery
presenters = []
for a, b in F.items():
    c = len(getter.findall(b))
    if c >= 3:
        ks = sorted({int(x, 0) for x in getter.findall(b)})
        pids = sorted({(t2.get(k) or t1.get(k) or {}).get("pid", "?") for k in ks})
        presenters.append(dict(func="0x" + a[1:], getter_calls=c, keys=len(ks), pids=pids[:40], pids_total=len(pids),
                               mentioned=sum(1 for p in pids if p != "?" and pid_rows.get(p.lower(), {}).get("mentions", 0) > 0)))
presenters.sort(key=lambda x: -x["getter_calls"])

# ---------- (3) teksty
TT = {int(r["typedtext_id_relative"]): r["pl_text"] for r in csv.DictReader(open(os.path.join(D, "typedtext_database.csv"), encoding="utf-8"))}
txt_static = set()
for b in F.values():
    for m in re.finditer(r"FUN_080313a4\([^;]*?,\s*(0x[0-9a-fA-F]+|\d+)\)", b):
        v = int(m.group(1), 0)
        if v in TT: txt_static.add(v)
    for m in re.finditer(r"FUN_080413a4\([^;]*?,\s*(0x[0-9a-fA-F]+|\d+)\)", b):
        v = int(m.group(1), 0)
        if v in TT: txt_static.add(v)
txt_seen, bmp_seen, classes = set(), set(), collections.defaultdict(set)
for f in glob.glob(os.path.join(UI, "extras", "*.json")):
    for w in json.load(open(f)).values():
        if w.get("tid") is not None: txt_seen.add(w["tid"])
for f in glob.glob(os.path.join(D, "widgets_inv*.json")):
    try: dd = json.load(open(f))
    except Exception: continue
    for n in dd:
        for w in n.get("widgets", []):
            if w.get("text_id") is not None: txt_seen.add(w["text_id"])
            if w.get("bitmap_id") is not None and w["bitmap_id"] < 189: bmp_seen.add(w["bitmap_id"])
            if w.get("vptr"): classes[w["vptr"]].add(str(n.get("node")))
for f in glob.glob(os.path.join(UI, "bind_raw", "*.json")) + glob.glob(os.path.join(UI, "atlas", "*.json")):
    t = open(f, errors="replace").read()
    for m in re.finditer(r'"(?:bitmap_id|bmp)"\s*:\s*(\d+)', t):
        if int(m.group(1)) < 189: bmp_seen.add(int(m.group(1)))
# bitmapy z kodu: lokalne stale u16 przed FUN_080307bc / 08040 7bc
bmp_static = set()
for b in F.values():
    if "FUN_080307bc" in b or "FUN_080407bc" in b:
        for m in re.finditer(r"=\s*(0x[0-9a-fA-F]{1,2}|\d{1,3});", b):
            v = int(m.group(1), 0)
            if 0 < v < 189: bmp_static.add(v)
man = {int(r["id"]): (r["width"], r["height"]) for r in csv.DictReader(open(os.path.join(D, "bitmaps", "manifest.csv")))}
bmp_doc = {i for i in man if re.search(r"(bitmap|bmp|klatk|frames|ikona|ikon)[^\n]{0,80}\b%d\b" % i, doc_all)}
txt_doc = {i for i, t in TT.items() if len(t.strip()) > 3 and t.strip().lower() in doc_all}

res = dict(
    schema_version="1.0",
    evidence="MEASURED (statyczna analiza decompiled.c + pliki modelu; porownanie liczbowe)",
    method="PID 'wzmianki' = liczba wystapien heksa w ui_model/*.json (bez device_model/bind_raw/atlas/extras); presentery = funkcje wolajace FUN_08036ff2 >=3 razy",
    totals=dict(pids=len(pm), pids_unmentioned=len(unmentioned_all), pids_read_by_code=len(read_by_code), pids_read_by_code_unmentioned=len(gaps),
                presenters=len(presenters), text_ids=len(TT), text_static=len(txt_static), text_seen_emulator=len(txt_seen),
                text_static_not_seen=len(txt_static - txt_seen), text_unseen_total=len(set(TT) - txt_seen), texts_unseen_and_undocumented=len(set(TT) - txt_seen - txt_doc),
                bitmaps=len(man), bitmaps_seen=len(bmp_seen), bitmaps_documented=len(bmp_doc), bitmaps_static_not_seen=len(bmp_static - bmp_seen), bitmaps_unseen_and_undocumented=len(set(man) - bmp_seen - bmp_doc)),
    pids_read_by_code_but_unmentioned=gaps,
    pids_unmentioned_all=unmentioned_all,
    presenters=presenters,
    texts_static_not_seen=[dict(id=i, pl=TT[i]) for i in sorted(txt_static - txt_seen)],
    texts_never_seen=[dict(id=i, pl=TT[i]) for i in sorted(set(TT) - txt_seen)],
    texts_unseen_and_undocumented=[dict(id=i, pl=TT[i]) for i in sorted(set(TT) - txt_seen - txt_doc)],
    bitmaps_never_seen_undocumented=[dict(id=i, size="%sx%s" % man[i]) for i in sorted(set(man) - bmp_seen - bmp_doc)],
    bitmaps_never_seen=[dict(id=i, size="%sx%s" % man[i], static_ref=i in bmp_static, documented=i in bmp_doc) for i in sorted(set(man) - bmp_seen)],
    widget_classes={k: sorted(v) for k, v in classes.items()},
)
json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
print(json.dumps(res["totals"], ensure_ascii=False, indent=1))
