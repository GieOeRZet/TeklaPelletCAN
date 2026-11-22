#!/usr/bin/env python3
"""NewEstyma PASS 42: renderuje ekran panelu WYKONUJAC firmware (Board + LTDC + DMA2D) i zapisuje bufor ramki jako PNG.
python3 -I tools/render_screen.py FW2213TK_kopia.bin out.png [--ticks 3000] [--ltdc-start 100] [--ltdc-every 10] [--tick 100000]

Co jest symulowane: scheduler FreeRTOS (SysTick/PendSV/SVC), przerwanie LTDC (IRQ 88, co --ltdc-every tikow po --ltdc-start), DMA2D (M2M, M2M+PFC, blend, R2M),
SDRAM 16 MB (0xC0000000). Format i adres bufora czytane z rejestrow LTDC warstwy 1 (PFCR 0x40016894, CFBAR 0x400168AC, rozmiar z AWCR/BPCR).
NIE jest symulowane: dotyk, CAN (brak ramek od centrali -> ekran w stanie domyslnym), RTC, kontroler pamieci flash/EEPROM."""
import argparse, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cortexm_rtos as C
from PIL import Image
LTDC = 0x40016800

def framebuffer(b):
    awcr, bpcr = b.rd(LTDC + 0x10), b.rd(LTDC + 0x0C)
    w = (awcr >> 16 & 0xFFF) - (bpcr >> 16 & 0xFFF); h = (awcr & 0x7FF) - (bpcr & 0x7FF)
    pf, addr = b.rd(LTDC + 0x94) & 7, b.rd(LTDC + 0xAC)
    return w, h, pf, addr

def to_image(b, w, h, pf, addr):
    n = {0: 4, 1: 3, 2: 2}[pf]; raw = bytes(b.mu.mem_read(addr, w * h * n)); img = Image.new("RGB", (w, h)); px = img.load()
    for y in range(h):
        for x in range(w):
            o = (y * w + x) * n
            if pf == 2:
                v = raw[o] | raw[o + 1] << 8; r, g, bl = v >> 11 & 31, v >> 5 & 63, v & 31
                px[x, y] = (r << 3 | r >> 2, g << 2 | g >> 4, bl << 3 | bl >> 2)
            else: px[x, y] = (raw[o + 2], raw[o + 1], raw[o]) if pf == 0 else (raw[o], raw[o + 1], raw[o + 2])
    return img

def render(binpath, ticks=3000, ltdc_start=100, ltdc_every=10, tick=100000, hook=None):
    b = C.Board(binpath, tick=tick); b.enable_dma2d()
    def h(bd):
        if bd.counters["svc"] == 0: return
        h.n = getattr(h, "n", 0) + 1
        if h.n >= ltdc_start and h.n % ltdc_every == 0: bd.wr(LTDC + 0x38, 1); bd.raise_irq(88)
        if hook: hook(bd, h.n)
    b.run(slices=ticks, hook=h)
    return b

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("bin"); ap.add_argument("out")
    ap.add_argument("--ticks", type=int, default=3000); ap.add_argument("--ltdc-start", type=int, default=100)
    ap.add_argument("--ltdc-every", type=int, default=10); ap.add_argument("--tick", type=int, default=100000)
    a = ap.parse_args()
    b = render(a.bin, a.ticks, a.ltdc_start, a.ltdc_every, a.tick)
    w, h, pf, addr = framebuffer(b); img = to_image(b, w, h, pf, addr); img.save(a.out)
    d = b.dma2d
    print("ekran %dx%d, format LTDC=%d, bufor=0x%08X; DMA2D operacji %d (niewspierane %d); kolorow %d" % (w, h, pf, addr, len(d.log), len(d.unsupported), len(set(img.get_flattened_data() if hasattr(img, "get_flattened_data") else img.getdata()))))
