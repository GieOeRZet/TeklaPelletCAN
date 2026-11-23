#!/usr/bin/env python3
"""PASS 63: warunki widocznosci i tresci widgetow jako dane (eksperyment w emulatorze).

Wejscie: UI-MODEL (tools/ui_model.py z --active presenter_trace v3), w ktorym wiazanie DYNAMIC_WRITE mowi, ktory setter
(i klucz UI -> PID) zapisuje ktore pola widgetu. Pole 0x25 (37) = widocznosc Drawable, 0x24 (36) = dotykalnosc,
"buf" = tekst (bufor wildcard), 0x26..0x29 obrazka = bitmapa. Dla kazdej pary (wezel, PID) narzedzie wczytuje punkt
kontrolny ekranu, wstrzykuje wartosc PID jak sterownik (UiSession.inject_param: ramka 0x584/0x42 przez prawdziwy RX,
walidacja min/max jak w firmware) i po odswiezeniu odczytuje z RAM: vis, touch, bitmape i tekst kazdego widgetu
powiazanego z tym PID. Wynik: tabela (wezel, widget, PID, wartosc) -> stan. Nic nie jest wnioskowane z kodu.
Uzycie: python3 -I tools/condition_probe.py FW.bin DIR UI_MODEL.json OUT.json [--values 0 1 2 3 5678] [--nodes ...]"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U

def widget_state(s, this, role):
    rd = s.b.rd; st = dict(vis=rd(this + 0x25, 1), touch=rd(this + 0x24, 1))
    if role == "image": st["bmp"] = rd(this + 0x26, 2)
    if role == "text":
        bp = rd(this + 0x34); t = []
        if 0x20000000 <= bp < 0x2002FFC0:
            for i in range(48):
                c = rd(bp + 2 * i, 2)
                if c == 0: break
                t.append(chr(c))
        st["text"] = "".join(t)
    return st

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bin"); ap.add_argument("dir"); ap.add_argument("model"); ap.add_argument("out")
    ap.add_argument("--values", nargs="+", type=int, default=[0, 1, 2, 3, 5678]); ap.add_argument("--nodes", nargs="*")
    ap.add_argument("--settle", type=int, default=250)
    a = ap.parse_args()
    items = json.load(open(a.model, encoding="utf-8"))["items"]
    groups = {}
    for w in items:
        if not str(w.get("binding", "")).startswith("DYNAMIC_WRITE"): continue
        if a.nodes and w.get("node") not in a.nodes: continue
        for c in w["presenter_candidates"]:
            pid = c.get("pid")
            if not pid or "inst" in str(c.get("pid_rule", "")) and not pid: continue
            groups.setdefault((w["node"], pid), []).append(dict(this=w["this"], role=w.get("role"), ax=w.get("ax"), ay=w.get("ay"),
                                                               w=w.get("w"), h=w.get("h"), fields=c.get("fields"), name=c.get("name"),
                                                               static=w.get("text_pl") or w.get("wildcard") or w.get("bitmap_id")))
    res = json.load(open(a.out)) if os.path.exists(a.out) else []
    done = {(r["node"], r["pid"]) for r in res}
    s = None
    for (node, pid), ws in sorted(groups.items()):
        if (node, pid) in done: continue
        st = os.path.join(a.dir, "node_%s.state" % node)
        if not os.path.exists(st): continue
        if s is None: s = U.UiSession.from_checkpoint(a.bin, st, None)
        rows = []
        for v in a.values:
            s.b.load_state(st)
            try: got = s.inject_param(int(pid, 16), v)
            except Exception as e: got = "ERR %s" % e
            s.wait(a.settle)
            rows.append(dict(value=v, stored=got, widgets={w["this"]: widget_state(s, int(w["this"], 16), w["role"]) for w in ws}))
        # widgety, ktorych stan zalezy od wartosci
        dep = [w["this"] for w in ws if len({json.dumps(r["widgets"][w["this"]], sort_keys=True) for r in rows}) > 1]
        res.append(dict(node=node, pid=pid, name=ws[0]["name"], widgets=ws, samples=rows, depends=dep))
        print(node, pid, ws[0]["name"], "zalezne: %d/%d" % (len(dep), len(ws)), flush=True)
        json.dump(res, open(a.out, "w"), ensure_ascii=False, indent=1)
    print("DONE", len(res))

if __name__ == "__main__":
    main()
