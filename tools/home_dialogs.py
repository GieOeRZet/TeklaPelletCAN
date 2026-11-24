#!/usr/bin/env python3
"""PASS 69: wnetrza okien ekranu glownego (nakladki): widgety widoczne po otwarciu (efektywna widocznosc sceny z RAM) minus widoczne w stanie bazowym, klasy, prostokaty, teksty/bitmapy,
dotykowe elementy i ich skutki (stukniecie z punktu kontrolnego okna: PID, ramki CAN 0x584, zmiana obrazu). Uzycie: home_dialogs.py FW DIR INV.json OUT.json name ..."""
import json, os, sys, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, action_probe as AP, ui_extras as X
fw, d, invp, outp = sys.argv[1:5]; names = sys.argv[5:]
inv = json.load(open(invp))[0]["widgets"]; W = {w["this"]: w for w in inv}
s = U.UiSession.from_checkpoint(fw, os.path.join(d, "menu.state"), None)
st0 = os.path.join(d, "node_home.state"); s.b.load_state(st0); s.wait(1700); rd = s.b.rd; root = rd(0x20024818) + 4
base = {t for t in W if X.evis(rd, int(t, 16), root)}
recs = AP.pid_records(s); BG = (0x3726, 0x2311, 0x2312, 0x2313, 0x2314); res = {}
def pidsnap(): return AP.pid_snap(s, recs)
for n in names:
    st = os.path.join(d, "node_dlg_%s.state" % n); s.b.load_state(st); s.wait(300)
    ex = X.extract(s, inv); shown = [t for t in W if X.evis(rd, int(t, 16), root) and t not in base]
    items = []
    for t in shown:
        w = W[t]; e = ex.get(t, {}); a = int(t, 16)
        items.append(dict(this=t, cls=e.get("cls", "?"), role=w["role"], rect=[w["ax"], w["ay"], w["w"], w["h"]], touch=rd(a + 0x24, 1), text=e.get("text"), tid=e.get("tid"), bmp=w.get("bitmap_id") if w["role"] == "image" else e.get("bmp"), box=e.get("box")))
    touch = [i for i in items if i["touch"] == 1 and 0 < i["rect"][2] < 480 and i["rect"][0] >= 0 and i["rect"][1] >= 0]
    probes = []
    s.b.load_state(st); s.wait(200); hc = hashlib.md5(s.shot().tobytes()).hexdigest(); c0 = pidsnap(); s.can2.tx.clear(); s.wait(800); c1 = pidsnap(); ctl = dict(pid={k for k in c0 if c0[k] != c1[k]}, can={bytes(f["data"]).hex() for f in s.can2.tx}, img=hashlib.md5(s.shot().tobytes()).hexdigest())
    for i in touch:
        cx, cy = min(479, i["rect"][0] + i["rect"][2] // 2), min(271, i["rect"][1] + i["rect"][3] // 2)
        s.b.load_state(st); s.wait(200); h0 = hashlib.md5(s.shot().tobytes()).hexdigest(); p0 = pidsnap(); s.can2.tx.clear()
        s.tap(cx, cy, settle=500); s.wait(300); p1 = pidsnap(); im = s.shot()
        probes.append(dict(this=i["this"], tap=[cx, cy], rect=i["rect"], cls=i["cls"], pid=[(hex(k), p0[k], p1[k]) for k in p0 if p0[k] != p1[k] and k not in BG and k not in ctl["pid"]][:6],
                           can=[bytes(f["data"]).hex() for f in s.can2.tx if f["id"] == 0x584 and bytes(f["data"]).hex() not in ctl["can"]][:4], image_changed=hashlib.md5(im.tobytes()).hexdigest() != ctl["img"]))
    res[n] = dict(widgets=items, touch_probes=probes); print(n, len(items), "widgetow,", len(touch), "dotykowych", flush=True)
    json.dump(res, open(outp, "w"), ensure_ascii=False)
