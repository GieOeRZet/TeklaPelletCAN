#!/usr/bin/env python3
"""NewEstyma PASS 44: sesja UI sterowana krok po kroku na emulatorze systemowym (FreeRTOS + LTDC + DMA2D + CAN2 + I2C/FT5x06).
    s = UiSession("FW2213TK_kopia.bin"); s.boot(); s.tap(34,235); s.wait(600); img = s.shot("menu")
Wspolrzedne = EKRANOWE 480x272 (przeliczane na surowe kontrolera: x/0.375, y/0.354 — z FUN sampleTouch 0x080759DC).
Metody: wait(ticks), tap(x,y,hold=150), swipe(x0,y0,x1,y1,ticks=200), shot(name)->PIL.Image (zapis do outdir/name.png), can(id,data), set_param(pid,value) (przez CAN 0x584/0x42),
state() (przydatne liczniki). Tick ~ 1 ms (100000 instrukcji). Jedna sesja ~ kilka sekund rozruchu + ~3 s na 1000 tikow."""
import os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cortexm_rtos as C, stm32_i2c as I, render_screen as R
LTDC = 0x40016800
def screen_to_raw(sx, sy): return max(0, round((sx - 0.5) / 0.375)), max(0, round((sy - 0.5) / 0.354))

class UiSession:
    def __init__(self, binpath, outdir=None, tick=100000):
        self.b = C.Board(binpath, tick=tick); self.b.enable_dma2d(); self.can2 = self.b.enable_can2()
        self.ft = I.FT5x06(); self.b.enable_i2c(slaves={0x38: self.ft}); self.out = outdir; self.n = 0; self.shots = {}
        if outdir: os.makedirs(outdir, exist_ok=True)
        self._hook_extra = None
    def _hook(self, bd, *a):
        if bd.counters["svc"] == 0: return
        self.n += 1
        if self.n >= 100 and self.n % 10 == 0: bd.wr(LTDC + 0x38, 1); bd.raise_irq(88)
        if self._hook_extra: self._hook_extra(self.n)
    def wait(self, ticks):
        self.b.run(slices=ticks, hook=self._hook)
    def boot(self, ticks=700): self.wait(ticks)
    def tap(self, x, y, hold=150, settle=0):
        self.ft.touch(*screen_to_raw(x, y)); self.wait(hold); self.ft.release(); self.wait(max(60, settle))
    def swipe(self, x0, y0, x1, y1, ticks=240, steps=12):
        self.ft.touch(*screen_to_raw(x0, y0)); self.wait(60)
        for i in range(1, steps + 1):
            x, y = x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps; self.ft._set(2, *screen_to_raw(x, y), 1); self.ft.last = screen_to_raw(x, y); self.wait(ticks // steps)
        self.ft.release(); self.wait(80)
    def shot(self, name=None):
        w, h, pf, addr = R.framebuffer(self.b); img = R.to_image(self.b, w, h, pf, addr)
        if name and self.out: img.save(os.path.join(self.out, name + ".png"))
        if name: self.shots[name] = img
        return img
    def can(self, can_id, data): self.can2.inject(can_id, data)
    def set_param(self, pid, value, size=4):
        self.can2.inject(0x584, bytes([0x42, pid & 255, pid >> 8, 1]) + (value & 0xFFFFFFFF).to_bytes(4, "little"))
    def _record(self, pid):
        """rekord tabeli runtime managera 0x20008D84 (stride 0x2C, baza +8): (storage, typ) albo None"""
        base = 0x20008D84 + 8
        for i in range(660):
            a = base + i * 0x2C
            if self.b.rd(a) == pid: return self.b.rd(a + 4), self.b.rd(a + 8)
        return None
    def set_local(self, pid, value):
        """zapis wprost do storage'u parametru (jak ustawienie wczytane z pamieci nieulotnej); szerokosc wg typu rekordu (1=u8, 2=u16, 3/5=u32, 4=s16).
        UWAGA: omija walidacje i publikacje; to stan poczatkowy, nie zapis uzytkownika."""
        r = self._record(pid)
        if r is None: raise KeyError("brak rekordu dla PID 0x%X" % pid)
        st, ty = r; n = {1: 1, 2: 2, 3: 4, 4: 2, 5: 4}[ty]; self.b.wr(st, value & ((1 << 8 * n) - 1), n); return st
    def state(self): return dict(self.b.counters, tick=self.n, task=self.b.task_name())
