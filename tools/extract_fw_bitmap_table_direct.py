#!/usr/bin/env python3
from pathlib import Path
import struct
from PIL import Image

# FW2213TK.bin direct bitmap extractor
# Critical: firmware load base is 0x08010000, not 0x08000000.

BIN = Path("FW2213TK_kopia.bin")
OUT = Path("bitmap-direct")
LOAD_BASE = 0x08010000
TABLE = 0x54450
COUNT = 188
STRIDE = 0x14

b = BIN.read_bytes()
(OUT / "png").mkdir(parents=True, exist_ok=True)

for bitmap_id in range(COUNT):
    off = TABLE + bitmap_id * STRIDE
    data_ptr, extra_ptr = struct.unpack_from("<II", b, off)
    width, height, solid_x, solid_y, solid_w, solid_h = struct.unpack_from("<6H", b, off + 8)
    n = width * height

    data_off = data_ptr - LOAD_BASE
    rgb = b[data_off:data_off + n * 2]
    if len(rgb) != n * 2:
        raise ValueError(f"bitmap {bitmap_id}: truncated RGB565")

    im = Image.frombytes("RGB", (width, height), rgb, "raw", "RGB;16")

    if extra_ptr:
        extra_off = extra_ptr - LOAD_BASE
        alpha = b[extra_off:extra_off + n]
        if len(alpha) != n:
            raise ValueError(f"bitmap {bitmap_id}: truncated A8")
        im.putalpha(Image.frombytes("L", (width, height), alpha))

    im.save(OUT / "png" / f"{bitmap_id:03d}.png", optimize=False)
