#!/usr/bin/env python3
"""NewEstyma PASS 44: emulator systemowy + dotyk FT5x06 (I2C1 @0x38) -> zrzuty ekranu.
python3 -I tools/touch_screen.py FW2213TK_kopia.bin outdir  --tap X,Y@TICK [--tap ...] [--shot TICK ...] [--ticks N] [--hold 200]
Wspolrzedne X,Y = wspolrzedne EKRANU 480x272, przeliczane na surowe kontrolera (x/0.375, y/0.354; ustalone z firmware, PASS 44); --raw wylacza przeliczanie.
Tap = nacisniecie na --hold tikow (domyslnie 200 ms; kontroler odpytywany ok. co 40 tikow), potem zwolnienie. Zrzut PNG w tikach --shot (domyslnie: 400 tikow po kazdym tapnieciu)."""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cortexm_rtos as C, stm32_i2c as I, render_screen as R
LTDC = 0x40016800
# Przeliczenie z FUN 0x080759DC (sampleTouch, PASS 44): x_ekran = (x_raw*3750+5000)/10000 (~0.375*x), y_ekran = (y_raw*354+500)/1000 (~0.354*y)
# => panel dotykowy FT5x06 raportuje ~1280x768; wspolrzedne ekranu 480x272 trzeba przeliczyc na surowe.
def screen_to_raw(sx, sy):
    rx = round((sx - 0.5) / 0.375); ry = round((sy - 0.5) / 0.354)
    return max(0, rx), max(0, ry)
def session(binpath, taps, shots, ticks, hold=200, out=None, ltdc_every=10, setup=None, raw=False):
    b = C.Board(binpath, tick=100000); b.enable_dma2d(); can = b.enable_can2(); ft = I.FT5x06(); b.enable_i2c(slaves={0x38: ft})
    if setup: setup(b, can)
    taps = sorted(taps); shots = sorted(shots); done = []
    def hook(bd, *a):
        if bd.counters["svc"] == 0: return
        hook.n = getattr(hook, "n", 0) + 1; n = hook.n
        if n >= 100 and n % ltdc_every == 0: bd.wr(LTDC + 0x38, 1); bd.raise_irq(88)
        for (x, y, t) in taps:
            if n == t: ft.touch(*(screen_to_raw(x, y) if not raw else (x, y)))
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
    ap.add_argument("--ticks", type=int, default=2500); ap.add_argument("--hold", type=int, default=200); ap.add_argument("--raw", action="store_true", help="X,Y to wspolrzedne surowe kontrolera (domyslnie: ekranowe 480x272)")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); taps = []
    for s in a.tap: xy, t = s.split("@"); x, y = xy.split(","); taps.append((int(x), int(y), int(t)))
    shots = a.shot or [t + a.hold + 400 for _, _, t in taps]
    b, ft, done = session(a.bin, taps, shots, a.ticks, a.hold, a.out, raw=a.raw)
    print("zrzutow:", len(done), "odczytow FT5x06:", len(ft.reads))
