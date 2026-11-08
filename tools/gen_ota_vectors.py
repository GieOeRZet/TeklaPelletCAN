#!/usr/bin/env python3
"""Generuje firmware/test/ota_vectors.h: maly 'obraz' ESP (naglowek 0xE9, chip_id 13) i jego podpisy kluczem testowym."""
import hashlib, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import ota_sign as O

key = O.load(Path(__file__).parent / "dev-keys/ota-dev-private.pem")

def image(chip):
    h = bytearray(24)
    h[0] = 0xE9; h[12] = chip & 0xFF; h[13] = chip >> 8
    return bytes(h) + bytes((i * 7 + 3) & 0xFF for i in range(1000))

good = image(13)
wrong_chip = image(5)
tampered = bytearray(good); tampered[500] ^= 1
def arr(name, data):
    return f"static const unsigned char {name}[] = {{{','.join(str(b) for b in data)}}};\n"
TR = O.TRAILER_MAGIC
sig_good = bytes.fromhex(O.sign_image(key, good))
pkg = good + TR + sig_good
pkg_tampered = bytes(tampered) + TR + sig_good
pkg_nosig = good + bytes(72)
out = "// WYGENEROWANE przez tools/gen_ota_vectors.py (klucz testowy)\n#pragma once\n"
out += arr("kOtaPackage", pkg) + arr("kOtaPackageTampered", pkg_tampered) + arr("kOtaPackageNoSig", pkg_nosig)
out += arr("kOtaGood", good) + arr("kOtaWrongChip", wrong_chip) + arr("kOtaTampered", bytes(tampered))
out += f'static const char* kOtaGoodSig = "{O.sign_image(key, good)}";\n'
out += f'static const char* kOtaWrongChipSig = "{O.sign_image(key, wrong_chip)}";\n'
Path(__file__).parent.parent.joinpath("firmware/test/ota_vectors.h").write_text(out)
print("zapisano ota_vectors.h")
