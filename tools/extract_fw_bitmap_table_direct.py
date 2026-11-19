#!/usr/bin/env python3
from pathlib import Path
import struct
from PIL import Image

# FW2213TK direct TouchGFX BitmapData extractor.
# Runtime pointers in this image use load base 0x08010000.
#
# Important:
# Do NOT use Pillow raw mode "RGB;16" here. For little-endian RGB565
# bytes from the firmware that mode swaps the red/blue interpretation.
# Decode the 16-bit RGB565 word explicitly instead.

BIN = Path("FW2213TK_kopia.bin")
OUT = Path("bitmap-direct")
LOAD_BASE = 0x08010000
TABLE = 0x54450
COUNT = 188
STRIDE = 0x14


def rgb565_to_rgb(raw: bytes, width: int, height: int) -> Image.Image:
    expected = width * height * 2
    if len(raw) != expected:
        raise ValueError(f"truncated RGB565: {len(raw)} != {expected}")

    # Firmware stores each RGB565 pixel as a little-endian uint16.
    pixels = bytearray(width * height * 3)
    for i in range(width * height):
        v = raw[2 * i] | (raw[2 * i + 1] << 8)
        r = (v >> 11) & 0x1F
        g = (v >> 5) & 0x3F
        b = v & 0x1F

        # Expand 5/6/5 bits to 8-bit channels using bit replication,
        # matching normal RGB565 -> RGB conversion semantics.
        pixels[3 * i + 0] = (r << 3) | (r >> 2)
        pixels[3 * i + 1] = (g << 2) | (g >> 4)
        pixels[3 * i + 2] = (b << 3) | (b >> 2)

    return Image.frombytes("RGB", (width, height), bytes(pixels))


b = BIN.read_bytes()
(OUT / "png").mkdir(parents=True, exist_ok=True)

for bitmap_id in range(COUNT):
    off = TABLE + bitmap_id * STRIDE
    data_ptr, extra_ptr = struct.unpack_from("<II", b, off)
    width, height, solid_x, solid_y, solid_w, solid_h = struct.unpack_from(
        "<6H", b, off + 8
    )
    n = width * height

    data_off = data_ptr - LOAD_BASE
    rgb = b[data_off:data_off + n * 2]
    im = rgb565_to_rgb(rgb, width, height)

    if extra_ptr:
        extra_off = extra_ptr - LOAD_BASE
        alpha = b[extra_off:extra_off + n]
        if len(alpha) != n:
            raise ValueError(f"bitmap {bitmap_id}: truncated A8")
        im.putalpha(Image.frombytes("L", (width, height), alpha))

    im.save(OUT / "png" / f"{bitmap_id:03d}.png", optimize=False)
