#!/usr/bin/env python3
"""PASS 61: rzeczywisty przebieg stukniec (zrodlo zdarzen dla tools/action_graph.py).

Dla wezla inwentarza (screen_inventory_menu.py: node "IDX_screen" / "IDX_settings") odtwarza wejscie z menu.state
(ten sam deterministyczny przebieg => te same adresy widgetow), zapisuje punkt kontrolny ekranu i dla kazdego
dotykalnego, widocznego widgetu (Drawable +0x24 touch, +0x25 vis) stuka w srodek prostokata. Kazde stukniecie
startuje z tego samego punktu kontrolnego. Rejestrowane skutki (wylacznie zaobserwowane, nic nie jest zgadywane):
  view      - zmiana klasy aktywnego widoku: vptr obiektu [0x20024818] (TouchGFX trzyma wszystkie widoki w jednym
              buforze, wiec sam wskaznik widoku sie nie zmienia - porownujemy jego vtable)
  body/head - zmiana obrazu ciala (y>=46) / naglowka (y<46) wzgledem przebiegu kontrolnego bez dotyku
  pid       - zmiany wartosci w storage'ach 655 parametrow (stara -> nowa)
  can       - ramki TX, ktorych NIE ma w przebiegu kontrolnym tej samej dlugosci (tlo: heartbeat, SDO, poller)
  texts     - TypedText ustawione na nowo (setTypedText) po stuknieciu, z tekstem PL; tytul = najwyzszy szeroki tekst
Uzycie:
  python3 -I tools/action_probe.py FW.bin DIR INV.json OUT.json --nodes 0_screen 0_settings [--max N] [--settle 700]
DIR = katalog z ui_explore.py --prepare (menu.state, rows.pkl, menu_tall.png). Wynik: lista akcji
{node, tap, widget(this), x, y, effects{...}} gotowa dla action_graph.py.
"""
import argparse, hashlib, json, os, pickle, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, ctor_trace as C
from PIL import Image

VIEW = 0x20024818
B = 0x08010000

def pid_records(s):
    base = 0x20008D84 + 8; out = []
    for i in range(660):
        a = base + i * 0x2C; pid = s.b.rd(a)
        if pid == 0 or pid > 0xFFFF: continue
        st, ty = s.b.rd(a + 4), s.b.rd(a + 8)
        if ty in (1, 2, 3, 4, 5) and 0x20000000 <= st < 0x20030000: out.append((pid, st, {1: 1, 2: 2, 3: 4, 4: 2, 5: 4}[ty]))
    return out

def pid_snap(s, recs): return {p: s.b.rd(st, n) for p, st, n in recs}

def hsh(im, box): return hashlib.sha1(im.crop(box).tobytes()).hexdigest()[:12]

def can_key(f): return (f["id"], bytes(f["data"]).hex())

def enter_node(s, d, rows, node, settle=700):
    """punkt kontrolny wezla inwentarza (IDX_screen / IDX_settings), ta sama sekwencja co screen_inventory_menu.grab"""
    idx, kind = node.split("_", 1); idx = int(idx)
    st_path = os.path.join(d, "node_%s.state" % node)
    if not os.path.exists(st_path):
        s.b.load_state(os.path.join(d, "menu.state")); s.wait(60)
        nav = U.ListNav(s); nav.tall = Image.open(os.path.join(d, "menu_tall.png")); nav.rows = rows
        nav.tap_row_from_top(idx); s.wait(settle)
        if kind == "settings": s.tap(400, 245, settle=800); s.wait(settle)
        s.checkpoint(st_path)
    return st_path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bin"); ap.add_argument("dir"); ap.add_argument("inv"); ap.add_argument("out")
    ap.add_argument("--nodes", nargs="+", required=True); ap.add_argument("--max", type=int, default=0)
    ap.add_argument("--settle", type=int, default=700); ap.add_argument("--shots", default="")
    a = ap.parse_args()
    raw = open(a.bin, "rb").read()
    def pl(i):
        try:
            p = struct.unpack_from("<I", raw, 0x5BD80 + 4 * i)[0]; o = p - B; r = []
            while True:
                c = struct.unpack_from("<H", raw, o)[0]
                if c == 0: break
                r.append(chr(c)); o += 2
            return "".join(r)
        except Exception: return "?"
    inv = {n["node"]: n for n in json.load(open(a.inv, encoding="utf-8"))}
    rows = pickle.load(open(os.path.join(a.dir, "rows.pkl"), "rb"))
    s = U.UiSession.from_checkpoint(a.bin, os.path.join(a.dir, "menu.state"), None)
    t = C.Tracer(s); recs = None; res = []
    if os.path.exists(a.out): res = json.load(open(a.out, encoding="utf-8"))
    done = {(r["node"], r["widget"]) for r in res}
    if a.shots: os.makedirs(a.shots, exist_ok=True)
    for node in a.nodes:
        if node not in inv: print("brak wezla w inwentarzu:", node, flush=True); continue
        st_path = enter_node(s, a.dir, rows, node, a.settle)
        if recs is None:
            s.b.load_state(st_path); recs = pid_records(s)
        # przebieg kontrolny: ta sama dlugosc bez dotyku
        s.b.load_state(st_path); s.can2.tx.clear(); v0 = s.b.rd(s.b.rd(VIEW)); p0 = pid_snap(s, recs)
        s.wait(150 + max(60, a.settle)); im0 = s.shot(); bg = {can_key(f) for f in s.can2.tx}; pc = pid_snap(s, recs)
        body0, head0 = hsh(im0, (0, 46, 480, 272)), hsh(im0, (0, 0, 480, 46))
        cands = [w for w in inv[node]["widgets"] if w.get("touch") and w.get("vis") and w["w"] > 0 and w["h"] > 0
                 and w["w"] * w["h"] < 480 * 272 * 0.6]
        seen_xy = set(); n = 0
        for w in sorted(cands, key=lambda w: (w["ay"], w["ax"])):
            cx = min(479, max(0, w["ax"] + w["w"] // 2)); cy = min(271, max(0, w["ay"] + w["h"] // 2))
            if (cx, cy) in seen_xy or (node, w["this"]) in done: continue
            seen_xy.add((cx, cy))
            if a.max and n >= a.max: break
            n += 1
            s.b.load_state(st_path); s.can2.tx.clear(); t.log.clear()
            s.tap(cx, cy, hold=150, settle=a.settle); im = s.shot(); v1 = s.b.rd(s.b.rd(VIEW)); p1 = pid_snap(s, recs)
            if a.shots: im.save(os.path.join(a.shots, "%s_%s.png" % (node, w["this"])))
            texts = {}
            for r in t.log:
                if r["op"] == "text": texts[hex(r["this"])] = r["id"]
            new_texts = sorted({pl(i + 57) for i in texts.values() if i < 496})
            title = ""
            if v1 != v0:
                ws = C.widget_table(s, t)
                for x in sorted(ws, key=lambda x: x["ay"]):
                    if x["role"] == "text" and 0 <= x["ay"] < 46 and x["w"] >= 300:
                        title = x["wildcard"] or (pl(x["text_id"] + 57) if x["text_id"] is not None and x["text_id"] < 496 else ""); break
            can = [dict(id=hex(f["id"]), data=bytes(f["data"]).hex()) for f in s.can2.tx if can_key(f) not in bg]
            pid = [dict(pid="0x%04X" % k, old=pc[k], new=p1[k]) for k in pc if pc[k] != p1.get(k)]   # wzgledem przebiegu kontrolnego (liczniki tla odpadaja)
            eff = dict(view_changed=v1 != v0, from_vptr=hex(v0), view_vptr=hex(v1), title=title,
                       body_changed=hsh(im, (0, 46, 480, 272)) != body0, head_changed=hsh(im, (0, 0, 480, 46)) != head0,
                       pid=pid, can=can, texts=new_texts[:40])
            kindc = ("SCREEN" if v1 != v0 else "PID" if pid else "CAN" if can else "VISUAL" if eff["body_changed"] or eff["head_changed"] else "NONE")
            res.append(dict(node=node, tap="tap", widget=w["this"], x=cx, y=cy, w=w["w"], h=w["h"], role=w.get("role"),
                            text_pl=w.get("text_pl") or w.get("wildcard") or "", bitmap_id=w.get("bitmap_id"), effect=kindc, effects=eff,
                            handler=None))
            print(node, w["this"], (cx, cy), kindc, title or "", pid[:3], can[:2], flush=True)
            json.dump(res, open(a.out, "w"), ensure_ascii=False, indent=1)
    print("DONE", len(res))

if __name__ == "__main__":
    main()
