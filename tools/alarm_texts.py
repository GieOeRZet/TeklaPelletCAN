#!/usr/bin/env python3
"""Tekst alarmu wyswietlany przez panel dla danego KODU (z binarki, emulator): wpisuje kody do pierscienia historii alarmow (0x4010+i, znaczniki 0x4024/0x4038, 0x404C/0x404D),
wchodzi w ekran Historia alarmow (poziom 0) i dla kolejnych wpisow (strzalka w dol) czyta KOD i tekst (id typedtext + napis z widgetow). Tylko emulator.
Uzycie: ESTYMA_IDLE_FAST=1 python3 -I tools/alarm_texts.py OUT.json KOD [KOD ...]   (do 20 kodow na przebieg)"""
import json, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import ui_session as U, ctor_trace as C, ui_extras as X
out = sys.argv[1]; codes = [int(x) for x in sys.argv[2:]][:20]
res = json.load(open(out)) if os.path.exists(out) else {}
s = U.UiSession(str(paths.FIRMWARE), None); t = C.Tracer(s); s.boot(500)
for p, v in {0x2105: 4, 0x2106: 1, 0x2107: 1, 0x2108: 1}.items(): s.set_local(p, v)
s.set_access(0); s.wait(4500)
n = len(codes)
def put(pid, v):      # jak odpowiedz sterownika (0x584), przez prawdziwy RX handler; sprawdzenie stored
    for _ in range(3):
        if s.inject_param(pid, v, 2, 50) == v: return True
    return False
bad = []
for i, c in enumerate(codes):
    ok = put(0x4010 + i, c | (1 << 16) | (1 << 17)) and put(0x4024 + i, 1700000000 + i) and put(0x4038 + i, 0)
    if not ok: bad.append(c)
put(0x404C, n % 20); put(0x404D, n)
if bad: print("NIE WSZEDL:", bad, flush=True)
s.tap(34, 235, settle=700); s.wait(600)
# wejscie w Historia alarmow: wiersz menu (z RAM)
ws = C.widget_table(s, t); ex = X.extract(s, ws); rd = s.b.rd
cand = [w for w in ws if ex.get(w["this"], {}).get("cls") == "text" and ex[w["this"]].get("text", "").startswith("Historia") and 55 <= w["ax"] <= 90]
def aby(a):
    y = 0
    for _ in range(12):
        if not (0x20000000 <= a < 0x20030000): break
        v = rd(a + 6, 2); y += v - 65536 if v > 32767 else v; a = rd(a + 0x14)
    return y
la = int(cand[0]["this"], 16)
for _ in range(20):
    y = aby(la) + 14
    if 60 <= y <= 250: break
    s.drag_until_change(240, 235, 240, 175, attempts=4, ticks=240, pause_end=160)
s.wait(3000); s.tap(240, aby(la) + 14, settle=900); s.wait(900)
def read():
    ws = C.widget_table(s, t); ex = X.extract(s, ws); items = []
    for w in ws:
        e = ex.get(w["this"], {})
        if e.get("cls") == "text" and not e.get("hidden") and e.get("text") and 40 < w["ay"] < 215: items.append((w["ay"], w["ax"], e.get("tid"), e["text"]))
    return sorted(items)
for k in range(n + 1):
    it = read(); kod = [x[3] for x in it if x[3].startswith("KOD")]; nr = [x[3] for x in it if x[3].startswith("NR")]
    body = [x for x in it if not x[3].startswith(("KOD", "NR", "Powst", "Potw", "AKTYW", "NIEAKT", "POTW", "HISTORIA", "<", "9%"))]
    print(k, nr, kod, [(x[2], x[3]) for x in body][:4], flush=True)
    m = re.search(r"KOD:\s*(\d+)", kod[0]) if kod else None
    if m: res[m.group(1)] = dict(nr=nr[0] if nr else None, texts=[dict(tid=x[2], text=x[3]) for x in body])
    json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
    s.tap(430, 190, settle=700); s.wait(500)      # strzalka w dol
