#!/usr/bin/env python3
"""Generuje firmware/test/license_vectors.h (kody testowe podpisane kluczem testowym)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import license as L

key = L.load_key(Path(__file__).parent / "dev-keys/license-dev-private.pem")
dev = bytes.fromhex("A1B2C3D4E5F6")
any_code = L.make_code(key, "full", bytes(6), 1)
bound = L.make_code(key, "full", dev, 7)
tampered = bound[:20] + ("A" if bound[20] != "A" else "B") + bound[21:]
out = Path(__file__).parent.parent / "firmware/test/license_vectors.h"
out.write_text("// WYGENEROWANE przez tools/gen_license_vectors.py (klucz testowy)\n#pragma once\n"
               f'static const char* kCodeAny = "{any_code}";\n'
               f'static const char* kCodeBound = "{bound}";\n'
               f'static const char* kCodeTampered = "{tampered}";\n', encoding="utf-8")
print("zapisano", out)
