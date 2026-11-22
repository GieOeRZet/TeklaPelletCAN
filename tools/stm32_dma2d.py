#!/usr/bin/env python3
"""NewEstyma: model peryferium DMA2D (Chrom-ART) STM32F4 dla tools/cortexm_rtos.py.
Rejestry sa zwyklą pamiecia (zapisuje je firmware); START w CR (0x4002B000 bit0) wykonuje operacje na pamieci, ustawia ISR.TCIF (bit1) i zgłasza IRQ 90.
Tryby (CR[17:16]): 0 M2M, 1 M2M+PFC, 2 M2M+blend, 3 R2M. Formaty (CM): 0 ARGB8888, 1 RGB888, 2 RGB565, 3 ARGB1555, 4 ARGB4444, 5 L8, 6 AL44, 7 AL88, 8 L4, 9 A8, 10 A4.
Operacje niewspierane sa LOGOWANE (dma.unsupported), nie ignorowane po cichu."""
import struct
DMA2D = 0x4002B000
CR, ISR, IFCR, FGMAR, FGOR, BGMAR, BGOR, FGPFCCR, FGCOLR, BGPFCCR, BGCOLR, FGCMAR, BGCMAR, OPFCCR, OCOLR, OMAR, OOR, NLR = (0x00, 0x04, 0x08, 0x0C, 0x10, 0x14, 0x18, 0x1C, 0x20, 0x24, 0x28, 0x2C, 0x30, 0x34, 0x38, 0x3C, 0x40, 0x44)
BPP = {0: 4, 1: 3, 2: 2, 3: 2, 4: 2, 5: 1, 6: 1, 7: 2, 8: 0.5, 9: 1, 10: 0.5}
MODES = {0: "M2M", 1: "M2M_PFC", 2: "M2M_BLEND", 3: "R2M"}

def to_argb(px, cm, clut=None, color=0):
    """pojedynczy piksel (int) w formacie cm -> (a,r,g,b) 0..255"""
    if cm == 0: return (px >> 24 & 255, px >> 16 & 255, px >> 8 & 255, px & 255)
    if cm == 1: return (255, px >> 16 & 255, px >> 8 & 255, px & 255)
    if cm == 2:
        r, g, b = px >> 11 & 31, px >> 5 & 63, px & 31
        return (255, r << 3 | r >> 2, g << 2 | g >> 4, b << 3 | b >> 2)
    if cm == 3: return ((px >> 15 & 1) * 255, (px >> 10 & 31) << 3, (px >> 5 & 31) << 3, (px & 31) << 3)
    if cm == 4: return ((px >> 12 & 15) * 17, (px >> 8 & 15) * 17, (px >> 4 & 15) * 17, (px & 15) * 17)
    if cm == 9: return (px & 255, color >> 16 & 255, color >> 8 & 255, color & 255)       # A8: alfa z piksela, kolor z COLR
    if cm == 5 and clut is not None: return clut(px)
    raise ValueError("format %d" % cm)

def from_argb(a, r, g, b, cm):
    if cm == 0: return a << 24 | r << 16 | g << 8 | b
    if cm == 1: return r << 16 | g << 8 | b
    if cm == 2: return (r >> 3) << 11 | (g >> 2) << 5 | (b >> 3)
    if cm == 3: return (1 if a >= 128 else 0) << 15 | (r >> 3) << 10 | (g >> 3) << 5 | (b >> 3)
    if cm == 4: return (a >> 4) << 12 | (r >> 4) << 8 | (g >> 4) << 4 | (b >> 4)
    raise ValueError("format wyjsciowy %d" % cm)

class Dma2D:
    def __init__(self, board, irq=90):
        self.b, self.irq = board, irq
        self.log, self.unsupported = [], []
        board.mu.hook_add(__import__("unicorn").UC_HOOK_MEM_WRITE, self._w, begin=DMA2D + CR, end=DMA2D + CR + 3)

    def _w(self, uc, access, addr, size, val, ud):
        if val & 1:                                         # START
            self.pending = True
            def once(u, a, sz, ud2, self=self):
                u.hook_del(self._h); self._run(); 
            nxt = uc.reg_read(__import__("unicorn").arm_const.UC_ARM_REG_PC) & ~1
            h = struct.unpack("<H", bytes(uc.mem_read(nxt, 2)))[0]
            nxt += 4 if (h >> 11) in (0x1D, 0x1E, 0x1F) else 2
            self._h = uc.hook_add(__import__("unicorn").UC_HOOK_CODE, once, begin=nxt, end=nxt)

    def r(self, off): return self.b.rd(DMA2D + off)
    def _run(self):
        b = self.b; cr = self.r(CR); mode = cr >> 16 & 3; nlr = self.r(NLR); pl, nl = nlr >> 16 & 0x3FFF, nlr & 0xFFFF
        opf = self.r(OPFCCR) & 7; omar = self.r(OMAR); oor = self.r(OOR) & 0x3FFF
        fgpf = self.r(FGPFCCR); bgpf = self.r(BGPFCCR); fgcm, bgcm = fgpf & 15, bgpf & 15
        rec = dict(mode=MODES[mode], pl=pl, nl=nl, out_cm=opf, omar=omar, oor=oor, fgcm=fgcm, bgcm=bgcm, fgmar=self.r(FGMAR), bgmar=self.r(BGMAR),
                   fgalpha=(fgpf >> 24, fgpf >> 16 & 3), ocolor=self.r(OCOLR))
        self.log.append(rec)
        try: self._exec(mode, pl, nl, opf, omar, oor, fgcm, bgcm, fgpf, bgpf)
        except Exception as e:
            self.unsupported.append((rec, repr(e)))
        b.wr(DMA2D + CR, cr & ~1)                           # START wyzerowany przez sprzet
        b.wr(DMA2D + ISR, self.r(ISR) | 2)                  # TCIF
        b.raise_irq(self.irq)

    def _px(self, addr, cm):
        n = BPP[cm]
        if n == 4: return self.b.rd(addr, 4)
        if n == 3: return self.b.rd(addr, 3)
        if n == 2: return self.b.rd(addr, 2)
        if n == 1: return self.b.rd(addr, 1)
        raise ValueError("bpp %s" % n)
    def _put(self, addr, val, cm):
        n = int(BPP[cm]); self.b.wr(addr, val, n)

    def _exec(self, mode, pl, nl, opf, omar, oor, fgcm, bgcm, fgpf, bgpf):
        b = self.b; ob = BPP[opf]
        if mode == 3:                                       # R2M: wypelnienie kolorem z OCOLR (w formacie wyjsciowym)
            col = self.r(OCOLR)
            for y in range(nl):
                row = omar + y * (pl + oor) * ob
                for x in range(pl): self._put(row + x * ob, col, opf)
            return
        fgmar, fgor = self.r(FGMAR), self.r(FGOR) & 0x3FFF; fb = BPP[fgcm]
        fgcol = self.r(FGCOLR); fam = fgpf >> 16 & 3; fa = fgpf >> 24
        if mode == 0:                                       # M2M: kopia bez konwersji (format = wyjsciowy)
            for y in range(nl):
                for x in range(pl):
                    self._put(omar + (y * (pl + oor) + x) * ob, self._px(fgmar + (y * (pl + fgor) + x) * int(fb), fgcm), opf)
            return
        bgmar, bgor = self.r(BGMAR), self.r(BGOR) & 0x3FFF; bb = BPP[bgcm]; bgcol = self.r(BGCOLR); bam = bgpf >> 16 & 3; ba = bgpf >> 24
        for y in range(nl):
            for x in range(pl):
                a, rr, g, bl = to_argb(self._px(fgmar + (y * (pl + fgor) + x) * int(fb), fgcm), fgcm, color=fgcol)
                if fam == 1: a = fa                          # AM=1: alfa zastapiona
                elif fam == 2: a = a * fa // 255             # AM=2: alfa mnozona
                if mode == 1:
                    self._put(omar + (y * (pl + oor) + x) * ob, from_argb(a, rr, g, bl, opf), opf); continue
                ba_, br, bg, bb_ = to_argb(self._px(bgmar + (y * (pl + bgor) + x) * int(bb), bgcm), bgcm, color=bgcol)
                if bam == 1: ba_ = ba
                elif bam == 2: ba_ = ba_ * ba // 255
                ao = a + ba_ * (255 - a) // 255
                if ao == 0: out = (0, 0, 0, 0)
                else:
                    mix = lambda f, bgc: (f * a + bgc * ba_ * (255 - a) // 255) // ao
                    out = (ao, mix(rr, br), mix(g, bg), mix(bl, bb_))
                self._put(omar + (y * (pl + oor) + x) * ob, from_argb(*out, opf), opf)
