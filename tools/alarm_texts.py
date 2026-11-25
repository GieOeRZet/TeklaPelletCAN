#!/usr/bin/env python3
"""Tekst alarmu wyswietlany przez panel dla danego KODU (binarka, emulator): jeden kod na rozruch - wpisuje go do pierscienia historii (0x4010, znaczniki 0x4024/0x4038, 0x404C/0x404D)
przez inject_param (jak odpowiedz sterownika 0x584), wchodzi w Historia alarmow i czyta KOD + tekst (id typedtext + napis). Tylko emulator.
Uzycie: ESTYMA_IDLE_FAST=1 python3 -I tools/alarm_texts.py OUT.json KOD [KOD ...]"""
import json, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import ui_session as U, ctor_trace as C, ui_extras as X
out = sys.argv[1]; codes = [int(x) for x in sys.argv[2:]]
res = json.load(open(out)) if os.path.exists(out) else {}
for c in codes:
    if str(c) in res and res[str(c)].get("ok"): continue
    s = U.UiSession(str(paths.FIRMWARE), None); t = C.Tracer(s); s.boot(500)
    for p, v in {0x2105: 4, 0x2106: 1, 0x2107: 1, 0x2108: 1}.items(): s.set_local(p, v)
    s.set_access(0); s.wait(4500)
    def put(pid, v):
        for _ in range(3):
            if s.inject_param(pid, v, 2, 50) == v: return True
        return False
    s.wait(int(os.environ.get("AL_WAIT", "9000")))      # silnik sam dopisuje alarmy 100/105/110 (brak modulow) - poczekaj az skonczy, potem dopisz swoj wpis jako najnowszy
    nx = s.b.rd(s._record(0x404C)[0], 1); cn = s.b.rd(s._record(0x404D)[0], 1); SL = nx % 20
    ok = put(0x4010 + SL, c | (1 << 16) | (1 << 17)) and put(0x4024 + SL, 1700000000) and put(0x4038 + SL, 0) and put(0x404C, (SL + 1) % 20) and put(0x404D, min(20, cn + 1))
    s.tap(34, 235, settle=700); s.wait(600)
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
    s.wait(3000); s.tap(240, aby(la) + 14, settle=900); s.wait(1200)
    ws = C.widget_table(s, t); ex = X.extract(s, ws); items = []
    for w in ws:
        e = ex.get(w["this"], {})
        if e.get("cls") == "text" and not e.get("hidden") and e.get("text") and 40 < w["ay"] < 215: items.append((w["ay"], w["ax"], e.get("tid"), e["text"]))
    items.sort(); kod = [x[3] for x in items if x[3].startswith("KOD")]; m = re.search(r"KOD:\s*(\d+)", kod[0]) if kod else None
    body = [x for x in items if not x[3].startswith(("KOD", "NR", "Powst", "Potw", "AKTYW", "NIEAKT", "POTW", "HISTORIA", "<", "9%")) and x[1] < 300 and x[0] > 60]
    shown = int(m.group(1)) if m else None
    res[str(c)] = dict(ok=(shown == c), injected=ok, shown_code=shown, texts=[dict(tid=x[2], text=x[3], ay=x[0]) for x in body])
    json.dump(res, open(out, "w"), ensure_ascii=False, indent=1); print(c, "inj" if ok else "NOINJ", shown, [(x[2], x[3]) for x in body][:3], flush=True)
