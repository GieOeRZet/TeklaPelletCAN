#!/usr/bin/env python3
"""python3 -I tools/test_render_screen.py FW2213TK_kopia.bin  — render + asercje (480x272 RGB565 w jednym z dwoch buforow 0xC0000000 lub 0xC003FC00, niepusty obraz, brak niewspieranych operacji DMA2D)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_screen as R
b = R.render(sys.argv[1], ticks=3000); w, h, pf, addr = R.framebuffer(b); img = R.to_image(b, w, h, pf, addr)
assert (w, h, pf) == (480, 272, 2) and addr in (0xC0000000, 0xC003FC00), (w, h, pf, addr)   # podwojne buforowanie: dwa bufory 480*272*2 B
assert len(b.dma2d.unsupported) == 0 and len(b.dma2d.log) > 500
cols = len(set(img.getdata())); assert cols > 300, cols
black = sum(1 for p in img.getdata() if p == (0, 0, 0)); assert 0.3 < black / (w * h) < 0.95
print("OK: render_screen (kolorow %d)" % cols)
