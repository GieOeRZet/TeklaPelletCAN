#!/usr/bin/env python3
"""PASS 63: PID-diff - wiazania widget -> PID przez roznicowanie stanu widgetow po wstrzyknieciu wartosci PID.

Pilot na jednym wezle (np. 0_screen = Kociol, poziom 0). Bez hakow MEM_WRITE i bez hakow na settery.
Jedyny hak (tylko w fazie "cands", przed przebiegami pomiarowymi): odczyt PID przez GUITask (UiSession.enable_trace()["pids"]).

Fazy:
  cands : punkt kontrolny wezla -> 400 tikow z hakiem -> lista PID czytanych przez GUITask  -> OUT.cands.json
  diff  : dla kazdego PID z listy i kilku wartosci: load_state(punkt kontrolny) -> inject_param -> wait(settle) -> stan widgetow
          (vis +0x25, touch +0x24, rect +4, bitmapa +0x26, tekst bufora +0x34) + zrzut. Przebieg kontrolny (bez wstrzykniecia)
          o tej samej dlugosci. Widget zalezny od wartosci = stan rozny dla >=2 roznych wartosci (po odjeciu tego,
          co zmienia sie samo - kontrola). Wynik zapisywany przyrostowo po kazdym PID (wznawialny).
Uzycie: python3 -I tools/pid_diff.py FW.bin DIR INV.json NODE OUT_PREFIX [--phase cands|diff|all] [--settle 200] [--pids 0x2001 ...]
"""
import argparse, csv, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, action_probe as AP
import pickle

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analiza", "FW2213TK-2026-11-22", "data")
VIEW = 0x20024818
S16 = lambda lo, hi: (lo | hi << 8) - (1 << 16) if (lo | hi << 8) & 0x8000 else (lo | hi << 8)


def pid_meta():
    m = {}
    for r in csv.DictReader(open(os.path.join(DATA, "pid_matrix_655.csv"), encoding="utf-8")):
        m[int(r["pid"], 16)] = r
    return m


def read_text(s, this):
    bp = s.b.rd(this + 0x34)
    if not (0x20000000 <= bp < 0x2002FFC0): return None
    t = []
    for i in range(48):
        c = s.b.rd(bp + 2 * i, 2)
        if c == 0: break
        t.append(chr(c))
    return "".join(t)


def read_state(s, widgets):
    rd = s.b.rd; out = {}
    for w in widgets:
        a = int(w["this"], 16)
        st = dict(vis=rd(a + 0x25, 1), touch=rd(a + 0x24, 1),
                  rect=[S16(rd(a + 4 + 2 * i, 1), rd(a + 5 + 2 * i, 1)) for i in range(4)])
        if w["role"] == "image": st["bmp"] = rd(a + 0x26, 2)
        if w["role"] == "text": st["text"] = read_text(s, a)
        out[w["this"]] = st
    return out


def sample_values(meta):
    """3-5 wartosci: min, max, 0/1 (jesli w zakresie), typowa (srodek), 5678 ('brak danych', jesli w zakresie) - bez duplikatow"""
    lo, hi = int(meta["min"]), int(meta["max"])
    if hi - lo <= 8: return list(range(lo, hi + 1))      # male zakresy (typy, wyliczenia): wszystkie wartosci (np. 0x22A1 =4 steruje „Ochrona kotla”)
    cand = [lo, hi, (lo + hi) // 2, 1, 0, 5678]
    vals = []
    for v in cand:
        if lo <= v <= hi and v not in vals: vals.append(v)
    return vals[:5] if len(vals) > 5 else vals


def good_widgets(inv_node):
    """odrzuca wpisy-smieci inwentarza (rect poza ekranem: pola nie-Drawable)"""
    out = []
    for w in inv_node["widgets"]:
        if w["role"] == "other" and (w["w"] < 0 or abs(w["ax"]) > 2000 or w["w"] > 2000 or w["vis"] > 1 or w["touch"] > 1): continue
        out.append(w)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bin"); ap.add_argument("dir"); ap.add_argument("inv"); ap.add_argument("node"); ap.add_argument("out")
    ap.add_argument("--phase", default="all"); ap.add_argument("--settle", type=int, default=200)
    ap.add_argument("--pids", nargs="*"); ap.add_argument("--shots", default="")
    a = ap.parse_args()
    inv = {n["node"]: n for n in json.load(open(a.inv, encoding="utf-8"))}[a.node]
    rows = pickle.load(open(os.path.join(a.dir, "rows.pkl"), "rb"))
    meta = pid_meta(); t0 = time.time()
    s = U.UiSession.from_checkpoint(a.bin, os.path.join(a.dir, "menu.state"), None)
    st_path = AP.enter_node(s, a.dir, rows, a.node)
    cands_path = a.out + ".cands.json"
    if a.phase in ("cands", "all") and not os.path.exists(cands_path):
        s.enable_trace(); s.b.load_state(st_path); s.trace["pids"].clear(); s.wait(400)
        json.dump(sorted(s.trace["pids"]), open(cands_path, "w")); print("cands", len(s.trace["pids"]), "%.0fs" % (time.time() - t0), flush=True)
        if a.phase == "cands": return
        s = U.UiSession.from_checkpoint(a.bin, os.path.join(a.dir, "menu.state"), None)   # swiat bez haka dla pomiarow
    if a.phase == "cands": return
    cands = json.load(open(cands_path))
    if a.pids: cands = [int(p, 16) for p in a.pids]
    ws = good_widgets(inv)
    res_path = a.out + ".json"
    res = json.load(open(res_path)) if os.path.exists(res_path) else dict(node=a.node, widgets=ws, control=None, pids={})
    if res["control"] is None:
        s.b.load_state(st_path); v0 = s.b.rd(s.b.rd(VIEW)); res["view_vptr"] = hex(v0)
        s.wait(a.settle + 240); res["control"] = read_state(s, ws); s.shot("x")
        res["control_dump"] = None
    if a.shots: os.makedirs(a.shots, exist_ok=True)
    for pid in cands:
        key = "0x%04X" % pid
        if key in res["pids"]: continue
        m = meta.get(pid)
        if not m: res["pids"][key] = dict(skipped="brak w pid_matrix"); continue
        runs = []
        for v in sample_values(m):
            s.b.load_state(st_path)
            try: got = s.inject_param(pid, v)
            except Exception as e: got = "ERR %s" % e
            s.wait(a.settle); im = s.shot()
            shot = None
            if a.shots:
                shot = "%s_%s_%s.png" % (a.node, key, v); im.save(os.path.join(a.shots, shot))
            runs.append(dict(value=v, stored=got, view_vptr=hex(s.b.rd(s.b.rd(VIEW))), state=read_state(s, ws), shot=shot))
        res["pids"][key] = dict(name=m["name"], type=m["type"], min=m["min"], max=m["max"], runs=runs)
        json.dump(res, open(res_path, "w"), ensure_ascii=False)
        print(key, m["name"], [r["stored"] for r in runs], "%.0fs" % (time.time() - t0), flush=True)
    print("DONE %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
