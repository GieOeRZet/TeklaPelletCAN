#!/usr/bin/env python3
"""NewEstyma PASS 44: emulator systemowy + dotyk FT5x06 (I2C1 @0x38) -> zrzuty ekranu.
python3 -I tools/touch_screen.py FW2213TK_kopia.bin outdir  --tap X,Y@TICK [--tap ...] [--shot TICK ...] [--ticks N] [--hold 200]
Wspolrzedne X,Y = wspolrzedne ekranu 480x272 (zakladamy mapowanie 1:1 z rejestrow FT5x06; do weryfikacji kalibracja).
Tap = nacisniecie na --hold tikow (domyslnie 200 ms; kontroler odpytywany ok. co 40 tikow), potem zwolnienie. Zrzut PNG w tikach --shot (domyslnie: 400 tikow po kazdym tapnieciu)."""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cortexm_rtos as C, stm32_i2c as I, render_screen as R
LTDC = 0x40016800
def session(binpath, taps, shots, ticks, hold=200, out=None, ltdc_every=10, setup=None):
    b = C.Board(binpath, tick=100000); b.enable_dma2d(); can = b.enable_can2(); ft = I.FT5x06(); b.enable_i2c(slaves={0x38: ft})
    if setup: setup(b, can)
    taps = sorted(taps); shots = sorted(shots); done = []
    def hook(bd, *a):
        if bd.counters["svc"] == 0: return
        hook.n = getattr(hook, "n", 0) + 1; n = hook.n
        if n >= 100 and n % ltdc_every == 0: bd.wr(LTDC + 0x38, 1); bd.raise_irq(88)
        for (x, y, t) in taps:
            if n == t: ft.touch(x, y)
            if n == t + hold: ft.release()
        while shots and shots[0] <= n:
            t = shots.pop(0); w, h, pf, addr = R.framebuffer(bd); img = R.to_image(bd, w, h, pf, addr)
            if out: img.save(os.path.join(out, "shot_%05d.png" % t))
            done.append((t, img))
    b.run(slices=ticks, hook=hook)
    return b, ft, done
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("bin"); ap.add_argument("out")
    ap.add_argument("--tap", action="append", default=[]); ap.add_argument("--shot", type=int, action="append", default=[])
    ap.add_argument("--ticks", type=int, default=2500); ap.add_argument("--hold", type=int, default=200)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); taps = []
    for s in a.tap: xy, t = s.split("@"); x, y = xy.split(","); taps.append((int(x), int(y), int(t)))
    shots = a.shot or [t + a.hold + 400 for _, _, t in taps]
    b, ft, done = session(a.bin, taps, shots, a.ticks, a.hold, a.out)
    print("zrzutow:", len(done), "odczytow FT5x06:", len(ft.reads))
