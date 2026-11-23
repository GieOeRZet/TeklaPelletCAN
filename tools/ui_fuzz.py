#!/usr/bin/env python3
"""PASS 53: eksploracja UI sterowana pokryciem (BFS po ekranach). Z punktu startowego (checkpoint lub swiezy rozruch) dla kazdego wezla stukamy siatke
punktow + sterowania (wstecz, kafel ustawien); jesli obraz (z maska wskaznika CPU) jest nowy -> zapis nowego wezla (save_state) i dalsza eksploracja do glebokosci DEPTH.
Zbiera pokrycie blokow (UC_HOOK_BLOCK) -> OUT/cov_fuzz_<tag>.json oraz zrzuty nowych ekranow OUT/<tag>_<n>.png.
python3 -I tools/ui_fuzz.py FW.bin OUT TAG SECONDS [--state menu.state] [--access N] [--cfg H,D,B,S[,CASC,FUEL2]] [--depth 3]"""
import os, sys, time, json, hashlib, datetime, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U
from unicorn import UC_HOOK_BLOCK
ap = argparse.ArgumentParser(); ap.add_argument("fw"); ap.add_argument("out"); ap.add_argument("tag"); ap.add_argument("seconds", type=int)
ap.add_argument("--state"); ap.add_argument("--access", type=int, default=3); ap.add_argument("--cfg", default="4,1,1,1"); ap.add_argument("--depth", type=int, default=3)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
GRID = [(x, y) for y in (60, 95, 130, 165, 200, 235) for x in (40, 110, 180, 250, 320, 390, 450)] + [(40, 22), (400, 245), (445, 118), (445, 187), (232, 187), (448, 240), (34, 235), (100, 240), (380, 75), (240, 250), (415, 230), (295, 205), (125, 205)]
def sig(im):
    im = im.copy(); im.paste((0, 0, 0), (400, 0, 480, 46)); return hashlib.md5(im.tobytes()).hexdigest()
if a.state: s = U.UiSession.from_checkpoint(a.fw, a.state, a.out)
else:
    s = U.UiSession(a.fw, a.out, rtc_start=datetime.datetime(2026, 11, 23, 14, 35, 0)); s.boot(800)
    c = [int(x) for x in a.cfg.split(",")]
    for pid, v in zip((0x2105, 0x2106, 0x2107, 0x2108, 0x350C, 0x3525), c): s.set_local(pid, v)
    s.wait(300)
s.set_access(a.access); s.wait(200)
cov = set(); s.b.mu.hook_add(UC_HOOK_BLOCK, lambda uc, ad, sz, ud: cov.add(ad), begin=0x08010000, end=0x080A0000)
seen = {}; t0 = time.time(); nodes = []; n = 0
def add(img, depth, parent):
    global n
    h = sig(img)
    if h in seen: return None
    path = os.path.join(a.out, "%s_%03d.state" % (a.tag, n)); s.checkpoint(path); img.save(os.path.join(a.out, "%s_%03d.png" % (a.tag, n)))
    seen[h] = n; nodes.append((path, depth, h, parent)); n += 1; return n - 1
add(s.shot(), 0, -1); qi = 0; taps = 0
while qi < len(nodes) and time.time() - t0 < a.seconds:
    path, depth, h0, parent = nodes[qi]; qi += 1
    if depth >= a.depth: continue
    for (x, y) in GRID:
        if time.time() - t0 > a.seconds: break
        s.b.load_state(path); s.wait(30); s.tap(x, y, hold=140, settle=280); taps += 1
        if taps % 40 == 0: s.wait(20)
        im = s.shot(); k = add(im, depth + 1, qi - 1)
        if k is not None: print("nowy ekran #%d (z #%d tap %d,%d) t=%ds pokrycie=%d" % (k, qi - 1, x, y, time.time() - t0, len(cov)), flush=True)
    json.dump(sorted(cov), open(os.path.join(a.out, "cov_fuzz_%s.json" % a.tag), "w"))
json.dump(sorted(cov), open(os.path.join(a.out, "cov_fuzz_%s.json" % a.tag), "w")); print("KONIEC wezlow", n, "tapow", taps, "pokrycie", len(cov))
