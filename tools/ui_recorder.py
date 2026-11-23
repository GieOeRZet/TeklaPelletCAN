#!/usr/bin/env python3
"""PASS 66: REKORDER UI — emulator panelu z interfejsem w przegladarce; klikasz jak w prawdziwym panelu, a narzedzie loguje (JSONL) kazde stukniecie:
ekran przed/po (vtable -> nazwa), widget pod palcem (adres, pozycja, tekst/bitmapa), zmiany PID, ramki CAN TX, zrzut. Mozna dopisywac notatki i zmieniac poziom/konfiguracje.
Uruchomienie (Windows/Linux/macOS, Python 3.10+):  pip install unicorn capstone pillow numpy
    python tools/ui_recorder.py --fw FW2213TK_kopia.bin            # potem otworz http://localhost:8765 (takze z telefonu w tej samej sieci: http://IP_PC:8765)
Firmware zostaje u Ciebie (nie jest czescia repo). Logi: sesja_*.jsonl + zrzuty w katalogu sesja_*/."""
import argparse, io, json, os, struct, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, ctor_trace as C, action_probe as AP

VIEW_NAMES = {"0x808f708": "HOME", "0x808f66c": "MENU", "0x808f910": "PROGRAM", "0x808f944": "LISTA", "0x808ed7c": "KOCIOL", "0x808ede4": "PALNIK", "0x808f5d0": "OGRZEWANIE", "0x808f604": "CWU",
              "0x808f978": "SOLARY", "0x808edb0": "BUFOR", "0x808ec10": "ALARMY", "0x808f638": "INFO", "0x808f80c": "TEST_WYJSC", "0x808f770": "SIEC", "0x808f9ac": "INTERNET", "0x808ee18": "KASKADA", "0x808eb74": "MAGAZYN"}
PAGE = """<!doctype html><meta charset=utf-8><title>UI rekorder</title><style>body{font:14px sans-serif;background:#222;color:#eee;margin:8px}canvas{border:1px solid #666;cursor:pointer;width:960px;max-width:100%}
#log{height:180px;overflow:auto;background:#111;padding:6px;font:12px monospace;white-space:pre-wrap}button,input,select{margin:2px}</style>
<div><b id=scr>-</b> <span id=st></span></div><canvas id=c width=480 height=272></canvas>
<div>poziom <select id=lvl><option>0<option>1<option>2<option>3</select> <button onclick=cfg()>ustaw poziom</button> | konfiguracja (np. 0x350C=1 0x2105=4): <input id=cf size=28><button onclick=cfg2()>ustaw</button> | notatka: <input id=nt size=30><button onclick=note()>zapisz</button></div>
<div id=log></div><script>
const c=document.getElementById('c'),x=c.getContext('2d');let busy=false;
async function frame(){if(busy)return;const r=await fetch('/frame.png?'+Date.now());const b=await r.blob();const i=await createImageBitmap(b);x.drawImage(i,0,0)}
setInterval(frame,600);
c.onclick=async e=>{const r=c.getBoundingClientRect();const px=Math.round((e.clientX-r.left)*480/r.width),py=Math.round((e.clientY-r.top)*272/r.height);busy=true;
 const j=await (await fetch('/tap',{method:'POST',body:JSON.stringify({x:px,y:py})})).json();busy=false;show(j);frame()};
function show(j){document.getElementById('scr').textContent=j.after_name||'';document.getElementById('st').textContent='ostatni: '+(j.widget?j.widget.label:'(brak widgetu)')+' -> '+j.effect;
 const l=document.getElementById('log');l.textContent=j.line+'\\n'+l.textContent}
async function cfg(){await fetch('/config',{method:'POST',body:JSON.stringify({level:+document.getElementById('lvl').value})})}
async function cfg2(){await fetch('/config',{method:'POST',body:JSON.stringify({set:document.getElementById('cf').value})})}
async function note(){await fetch('/note',{method:'POST',body:JSON.stringify({text:document.getElementById('nt').value})});document.getElementById('nt').value=''}
</script>"""
class Rec:
    def __init__(self, fw, level, cfg, outdir):
        self.lock = threading.Lock(); self.s = U.UiSession(fw, None); self.t = C.Tracer(self.s); self.raw = open(fw, "rb").read()
        self.out = outdir; os.makedirs(outdir, exist_ok=True); self.log = open(outdir + ".jsonl", "a", encoding="utf-8"); self.n = 0; self.running = True
        self.s.boot(500)
        for p, v in {0x2105: 4, 0x2106: 1, 0x2107: 1, 0x2108: 1, **cfg}.items(): self.s.set_local(p, v)
        self.s.set_access(level); self.s.wait(400); self.table = C.widget_table(self.s, self.t); self.recs = AP.pid_records(self.s)
        self.s.wait(3000); self.s.can2.tx.clear(); pa = AP.pid_snap(self.s, self.recs); self.s.wait(1500); pb = AP.pid_snap(self.s, self.recs)
        self.bg = {(f["id"], bytes(f["data"]).hex()) for f in self.s.can2.tx}; self.bgpid = {k for k in pa if pa[k] != pb[k]}      # tlo: ramki CAN (heartbeat, poller) i liczniki PID zmieniajace sie same
        self.frame = self.s.shot(); threading.Thread(target=self.tick, daemon=True).start()
    def tick(self):
        while self.running:
            with self.lock: self.s.wait(20)
            time.sleep(0.01)
    def pl(self, i):
        try:
            p = struct.unpack_from("<I", self.raw, 0x5BD80 + 4 * i)[0] - 0x08010000; r = []
            while True:
                c = struct.unpack_from("<H", self.raw, p)[0]
                if c == 0: break
                r.append(chr(c)); p += 2
            return "".join(r).replace("\x02", "#")
        except Exception: return "?"
    def vname(self): v = hex(self.s.b.rd(self.s.b.rd(AP.VIEW))); return VIEW_NAMES.get(v, v), v
    def under(self, x, y):
        best = None; rd = self.s.b.rd
        for w in self.table:
            try: a = int(w["this"], 16)
            except Exception: continue
            if not (w["ax"] <= x < w["ax"] + w["w"] and w["ay"] <= y < w["ay"] + w["h"]) or w["w"] <= 0 or w["h"] <= 0 or w["w"] > 480 or w["h"] > 272: continue
            if rd(a + 0x24, 1) != 1 or rd(a + 0x25, 1) != 1: continue
            if best is None or w["w"] * w["h"] < best["w"] * best["h"]: best = w
        if not best: return None
        lab = best["role"]
        if best.get("text_id") is not None and best["text_id"] < 496: lab = "tekst '%s'" % self.pl(best["text_id"] + 57)
        elif best.get("bitmap_id") is not None: lab = "bitmapa %s" % best["bitmap_id"]
        return dict(this=best["this"], rect=[best["ax"], best["ay"], best["w"], best["h"]], role=best["role"], text_id=best.get("text_id"), bitmap_id=best.get("bitmap_id"), label=lab)
    def tap(self, x, y):
        with self.lock:
            n0, v0 = self.vname(); p0 = AP.pid_snap(self.s, self.recs); wd = self.under(x, y)
            self.s.can2.tx.clear(); self.t.log.clear(); self.s.tap(x, y, hold=150, settle=500); self.s.wait(300)
            n1, v1 = self.vname(); p1 = AP.pid_snap(self.s, self.recs)
            if v1 != v0: self.table = C.widget_table(self.s, self.t)
            self.frame = self.s.shot(); self.n += 1; shot = "%04d_%s_to_%s.png" % (self.n, n0, n1); self.frame.save(os.path.join(self.out, shot))
            pid = [dict(pid="0x%04X" % k, old=p0[k], new=p1[k]) for k in p0 if p0[k] != p1.get(k) and k not in self.bgpid]
            can = [dict(id=hex(f["id"]), data=bytes(f["data"]).hex()) for f in self.s.can2.tx if (f["id"], bytes(f["data"]).hex()) not in self.bg]
            eff = "ekran %s -> %s" % (n0, n1) if v1 != v0 else ("PID %s" % [p["pid"] for p in pid][:4] if pid else "CAN %d" % len(can) if can else "wizualny/brak")
            rec = dict(t=time.time(), n=self.n, tap=[x, y], before=n0, after=n1, vtable_before=v0, vtable_after=v1, widget=wd, pid=pid[:20], can=can[:12], shot=shot)
            self.log.write(json.dumps(rec, ensure_ascii=False) + "\n"); self.log.flush()
            line = "#%d (%d,%d) %s | widget: %s | %s" % (self.n, x, y, n0, wd["label"] if wd else "-", eff)
            return dict(rec, effect=eff, after_name=n1, line=line)
    def png(self):
        with self.lock: im = self.s.shot()
        b = io.BytesIO(); im.save(b, "PNG"); return b.getvalue()
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--fw", required=True); ap.add_argument("--port", type=int, default=8765); ap.add_argument("--level", type=int, default=0)
    ap.add_argument("--config", nargs="*", default=[]); ap.add_argument("--out", default=time.strftime("sesja_%Y%m%d_%H%M%S")); a = ap.parse_args()
    cfg = {int(k, 16): int(v) for k, v in (c.split("=") for c in a.config)}
    R = Rec(a.fw, a.level, cfg, a.out); print("gotowe: http://localhost:%d  log: %s.jsonl" % (a.port, a.out), flush=True)
    class H(BaseHTTPRequestHandler):
        def log_message(self, *x): pass
        def _j(self, o, code=200): b = json.dumps(o, ensure_ascii=False).encode(); self.send_response(code); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
        def do_GET(self):
            if self.path.startswith("/frame.png"): b = R.png(); self.send_response(200); self.send_header("Content-Type", "image/png"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
            else: b = PAGE.encode(); self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
        def do_POST(self):
            d = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            if self.path == "/tap": self._j(R.tap(int(d["x"]), int(d["y"])))
            elif self.path == "/note":
                with R.lock: R.log.write(json.dumps(dict(t=time.time(), note=d.get("text", "")), ensure_ascii=False) + "\n"); R.log.flush()
                self._j({"ok": 1})
            elif self.path == "/config":
                with R.lock:
                    if "level" in d: R.s.set_access(int(d["level"]))
                    for tok in (d.get("set") or "").split():
                        k, v = tok.split("="); R.s.set_local(int(k, 16), int(v))
                    R.log.write(json.dumps(dict(t=time.time(), config=d), ensure_ascii=False) + "\n"); R.log.flush()
                self._j({"ok": 1})
            else: self._j({"err": "?"}, 404)
    ThreadingHTTPServer(("0.0.0.0", a.port), H).serve_forever()
if __name__ == "__main__": main()
