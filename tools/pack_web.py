#!/usr/bin/env python3
"""Pakuje pliki z web/ do tablicy C++ (gzip) osadzanej w firmware: pack_web.py <web_dir> <out.cpp>."""
import gzip, sys
from pathlib import Path

SKIP_DIRS = {"test"}
SKIP_FILES = {"bojler.png"}                     # duzy PNG; jest bojler.svg
MIME = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css",
        ".svg": "image/svg+xml", ".png": "image/png", ".webp": "image/webp", ".json": "application/json"}


def main():
    web, out = Path(sys.argv[1]), Path(sys.argv[2])
    files = sorted(p for p in web.rglob("*") if p.is_file() and not (set(p.relative_to(web).parts[:-1]) & SKIP_DIRS)
                   and p.name not in SKIP_FILES and p.suffix in MIME and not p.name.endswith(".md"))
    lines = ['// WYGENEROWANE przez tools/pack_web.py – nie edytuj.', '#include "web_assets.h"', "", "namespace {"]
    table = []
    for i, p in enumerate(files):
        raw = p.read_bytes()
        gz = gzip.compress(raw, 9, mtime=0)
        use_gz = len(gz) < len(raw) * 0.9
        data = gz if use_gz else raw
        lines.append(f"const unsigned char a{i}[] = {{{','.join(str(b) for b in data)}}};")
        table.append(f'    {{"/{p.relative_to(web).as_posix()}", "{MIME[p.suffix]}", a{i}, {len(data)}, {"true" if use_gz else "false"}}},')
    lines += ["}  // namespace", "", "const WebAsset kWebAssets[] = {"] + table + ["};", f"const unsigned kWebAssetCount = {len(files)};", ""]
    out.write_text("\n".join(lines), encoding="utf-8")
    total = sum(len(l) for l in lines)
    print(f"{len(files)} plikow -> {out}")


if __name__ == "__main__":
    main()
