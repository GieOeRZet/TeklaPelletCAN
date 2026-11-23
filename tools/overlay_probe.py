#!/usr/bin/env python3
"""PASS 65: okna/nakladki (dialogi) otwierane stukniegciem w wyzwalacz. Okna sa budowane dynamicznie przy otwarciu, wiec widgety rejestrujemy sledzeniem
konstrukcji (ctor_trace.Tracer) tylko w trakcie stuknięcia. Dla kazdego wyzwalacza zapisuje: punkt kontrolny otwartego okna (DIR/node_dlg_<name>.state),
inwentarz okna (wezel 'dlg_<name>' w OUT.json, format jak widgets_inv), zrzut. Uzycie: overlay_probe.py FW DIR NODE OUT.json SHOTDIR name=x,y ..."""
import json, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, action_probe as AP, ctor_trace as C
fw, d, node, outp, shots = sys.argv[1:6]; trig = [a.split("=") for a in sys.argv[6:]]
s = U.UiSession.from_checkpoint(fw, os.path.join(d, "menu.state"), None); st = AP.enter_node(s, d, pickle.load(open(os.path.join(d, "rows.pkl"), "rb")), node)
t = C.Tracer(s); os.makedirs(shots, exist_ok=True); out = []
for name, xy in trig:
    x, y = [int(v) for v in xy.split(",")]
    s.b.load_state(st); s.wait(300); t.log.clear(); s.tap(x, y, hold=150, settle=700); s.wait(300)
    ws = C.widget_table(s, t); s.shot("x").save(os.path.join(shots, name + ".png"))
    s.checkpoint(os.path.join(d, "node_dlg_%s.state" % name))
    out.append(dict(node="dlg_" + name, trigger=dict(node=node, tap=[x, y]), view_vptr=hex(s.b.rd(s.b.rd(AP.VIEW))), widgets=ws))
    print(name, len(ws), "widgetow zbudowanych przy otwarciu, vptr", out[-1]["view_vptr"], flush=True)
    json.dump(out, open(outp, "w"), ensure_ascii=False)
