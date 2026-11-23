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
    def swipe(self, x0, y0, x1, y1, ticks=240, steps=12, pause_end=0):
        self.ft.touch(*screen_to_raw(x0, y0)); self.wait(60)
        for i in range(1, steps + 1):
            x, y = x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps; self.ft._set(2, *screen_to_raw(x, y), 1); self.ft.last = screen_to_raw(x, y); self.wait(ticks // steps)
        if pause_end: self.wait(pause_end)          # zatrzymanie palca przed puszczeniem: brak predkosci => brak bezwladnosci (flick)
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
    MODEL = 0x20020784   # singleton modelu (FUN 0x080414BA); poziom dostepu = bajt MODEL+0x158 (FUN_08037E74: PIN 900->1, 999->2, 6154->3)
    def set_access(self, level): self.b.wr(self.MODEL + 0x158, level, 1)
    def access(self): return self.b.rd(self.MODEL + 0x158, 1)
    @staticmethod
    def body_hash(im, y0=46):
        """skrot obrazu BEZ naglowka (y<y0): w naglowku zmienia sie licznik procentowy"""
        import hashlib
        return hashlib.md5(im.crop((0, y0, im.width, im.height)).tobytes()).hexdigest()
    def drag_until_change(self, x0, y0, x1, y1, attempts=5, ticks=240, steps=12, pause_end=160):
        """przeciagniecie powtarzane z przesunieciem fazy wzgledem odpytywania kontrolera (~40 tikow), az obraz (bez naglowka) sie zmieni.
        Pojedyncze przeciagniecia (zwlaszcza w dol od dolu listy) bywaja gubione zaleznie od fazy; zwraca True, gdy sie zmienilo."""
        for k in range(attempts):
            h0 = self.body_hash(self.shot()); self.swipe(x0, y0, x1, y1, ticks=ticks, steps=steps, pause_end=pause_end); self.wait(250)
            if self.body_hash(self.shot()) != h0: return True
            self.wait(7 + 9 * k)
        return False
    def go_top(self, tries=8):
        last = None
        for _ in range(tries):
            moved = self.drag_until_change(240, 70, 240, 240)
            if not moved: return True          # nie przewija sie juz => gora
        return False
    def scroll_capture(self, name, maxpages=8, dy=150, x=240, ytop=230):
        """robi zrzut, przewija w gore o dy i powtarza, az obraz przestanie sie zmieniac; zwraca liste obrazow"""
        import hashlib
        imgs, last = [], None
        for i in range(maxpages):
            im = self.shot("%s_%d" % (name, i)); h = self.body_hash(im)
            if h == last: break
            imgs.append(im); last = h; self.drag_until_change(x, ytop, x, ytop - dy, attempts=3)
        return imgs
    def checkpoint(self, path):
        """zapisuje stan emulatora i licznik tikow sesji (patrz Board.save_state)"""
        self.b.save_state(path, extra=dict(n=self.n))
    @classmethod
    def from_checkpoint(cls, binpath, path, outdir=None):
        s = cls(binpath, outdir); ex = s.b.load_state(path); s.n = ex["n"]; return s
    BITMAP_TABLE = (0x08064450, 188, 0x14)          # RUNTIME: tablica deskryptorow bitmap (RAW 0x54450, 188 wpisow po 0x14 B)
    TEXT_LANG_PTRS = (0x0806BE64, 0x0806AEEC, 0x0806B6A8, 0x0806CDDC, 0x080697B8, 0x08069F74, 0x0806C620, 0x0806A730)   # wskazniki tabel TypedText (PL EN LT SK CZ ES RO EST) = adres wpisu ID 57
    def enable_trace(self):
        """sledzi, ktore bitmapy i teksty (ID) firmware CZYTA przy rysowaniu: odczyty deskryptorow bitmap i wskaznikow TypedText (flash). Wynik: self.trace = {'bitmaps': set, 'text': set((jezyk, id))}"""
        from unicorn import UC_HOOK_MEM_READ
        self.trace = {"bitmaps": set(), "text": set(), "pids": set()}; base, n, stride = self.BITMAP_TABLE
        # PID-y odczytywane przez GUITask: wejscie w wyszukiwanie rekordu runtime (RUNTIME 0x080215F6; r2 = klucz). Tylko gdy biezace zadanie = GUITask (TCB 0x20001198)
        from unicorn import UC_HOOK_CODE
        from unicorn.arm_const import UC_ARM_REG_R2
        def look(uc, a, sz, ud):
            try:
                if self.b.rd(self.b.tcb_ptr) == 0x20001198: self.trace["pids"].add(uc.reg_read(UC_ARM_REG_R2) & 0xFFFF)
            except Exception: pass
        self.b.mu.hook_add(UC_HOOK_CODE, look, begin=0x080215F6, end=0x080215F6)
        def rb(uc, a, ad, sz, v, ud): self.trace["bitmaps"].add((ad - base) // stride)
        self.b.mu.hook_add(UC_HOOK_MEM_READ, rb, begin=base, end=base + n * stride - 1)
        for li, ptr in enumerate(self.TEXT_LANG_PTRS):
            tb = ptr - 57 * 4
            def rt(uc, a, ad, sz, v, ud, li=li, tb=tb): self.trace["text"].add((li, (ad - tb) // 4))
            self.b.mu.hook_add(UC_HOOK_MEM_READ, rt, begin=tb, end=tb + 495 * 4 - 1)
    def dump_trace(self, path):
        import json
        json.dump(dict(bitmaps=sorted(self.trace["bitmaps"]), text=sorted(self.trace["text"]), pids=sorted(self.trace["pids"])), open(path, "w"))
    def state(self): return dict(self.b.counters, tick=self.n, task=self.b.task_name())


def stitch_body(s, drag=60, maxsteps=60, maxerr=3):
    """sklada CALE przewijalne cialo ekranu (pod naglowkiem, y>=46) w jeden wysoki obraz: przeciagniecia w gore + dopasowanie przesuniecia; zwraca PIL.Image"""
    from PIL import Image
    B0 = ListNav.BODY0; frames = [s.shot()]; offs = [0]
    for _ in range(maxsteps):
        prev = frames[-1]
        if not s.drag_until_change(240, 235, 240, 235 - drag, attempts=4): break
        cur = s.shot()
        if s.body_hash(cur) == s.body_hash(prev): break
        err, d = ListNav._shift(prev, cur)
        if d == 0 or err > maxerr: break
        frames.append(cur); offs.append(offs[-1] + d)
    h = offs[-1] + frames[-1].height - B0; tall = Image.new("RGB", (480, h))
    for f, o in zip(frames, offs): tall.paste(f.crop((0, B0, 480, f.height)), (0, o))
    return tall


class ListNav:
    """Nawigator przewijanej listy (np. glowne MENU): skleja cala liste w jeden obraz (przesuniecie miedzy zrzutami wykrywane korelacja),
    potem dla dowolnego wiersza przewija tak, by byl widoczny, i zwraca wspolrzedna ekranowa do stuniecia. Wiersze maja stale rozstaw ~50 px.
    Uzycie: nav = ListNav(session); nav.build(); nav.rows (lista dict: idx, chevron); nav.tap_row(idx)."""
    BODY0 = 46      # poczatek obszaru listy (pod naglowkiem)
    PITCH = 50
    def __init__(self, s): self.s = s; self.tall = None; self.rows = []
    @staticmethod
    def _shift(a, b):
        """o ile pikseli lista przesunela sie miedzy a i b (b jest przewiniete w gore): minimalny blad dopasowania"""
        import numpy as np
        A = np.asarray(a.convert("L"), dtype=int)[ListNav.BODY0:, :460]; B = np.asarray(b.convert("L"), dtype=int)[ListNav.BODY0:, :460]
        best = None
        for d in range(0, A.shape[0] - 30):
            e = np.abs(A[d:] - B[:A.shape[0] - d]).mean()
            if best is None or e < best[0]: best = (e, d)
        return best
    def build(self, drag=60, maxsteps=30):
        from PIL import Image
        s = self.s; assert s.go_top(); frames = [s.shot()]; offs = [0]
        for _ in range(maxsteps):
            prev = frames[-1]; s.drag_until_change(240, 235, 240, 235 - drag, attempts=3); cur = s.shot()
            if s.body_hash(cur) == s.body_hash(prev): break
            err, d = self._shift(prev, cur)
            if d == 0 or err > 3: break
            frames.append(cur); offs.append(offs[-1] + d)
        h = offs[-1] + frames[-1].height - self.BODY0
        tall = Image.new("RGB", (480, h)); 
        for f, o in zip(frames, offs): tall.paste(f.crop((0, self.BODY0, 480, f.height)), (0, o))
        self.tall = tall; self.offs = offs; n = max(1, round((h - 4) / self.PITCH)); self.rows = []
        for i in range(n):
            cy = 29 + self.PITCH * i; self.rows.append(dict(idx=i, cy=cy, chevron=self._chevron(tall, cy)))
        return self.rows
    @staticmethod
    def _chevron(img, cy):
        px = img.convert("L").load(); h = img.height
        c = sum(1 for yy in range(max(0, cy - 9), min(h, cy + 9)) for xx in range(432, 452) if px[xx, yy] > 150)
        return c > 6
    def offset(self, img):
        """aktualny offset przewiniecia ekranu wzgledem sklejonej listy"""
        import numpy as np
        T = np.asarray(self.tall.convert("L"), dtype=int); B = np.asarray(img.convert("L"), dtype=int)[self.BODY0:, :460]
        best = None
        for o in range(0, T.shape[0] - B.shape[0] + 1):
            e = np.abs(T[o:o + B.shape[0], :460] - B).mean()
            if best is None or e < best[0]: best = (e, o)
        return best
    def tap_row_from_top(self, idx, settle=800):
        """jak tap_row, ale TYLKO ruchy w gore (niezawodne); zaklada, ze lista jest na gorze (np. po wczytaniu punktu kontrolnego)"""
        s = self.s; cy = self.rows[idx]["cy"]
        for _ in range(14):
            err, o = self.offset(s.shot()); y = self.BODY0 + cy - o
            if 70 <= y <= 250: s.tap(240, y, settle=settle); return True
            if y < 70: return False
            if not s.drag_until_change(240, 235, 240, 175, attempts=4): return False
        return False
    def tap_row(self, idx, settle=800):
        s = self.s; cy = self.rows[idx]["cy"]
        for _ in range(6):
            err, o = self.offset(s.shot())
            y = self.BODY0 + cy - o
            if 56 <= y <= 262: s.tap(240, y, settle=settle); return True
            if y > 262: s.drag_until_change(240, 235, 240, 135)
            else: s.drag_until_change(240, 80, 240, 180)
        return False
