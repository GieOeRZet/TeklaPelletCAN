#!/usr/bin/env python3
"""Aktualizuje manifest aktualizacji OTA (manifest.json) dla jednego kanalu.

  make_manifest.py --dir DIR --channel beta|stable --version 0.3.0 --build 17 --commit SHA --notes "tekst"
Wymaga w DIR/<kanal>/ plikow teklapelletcan.bin i teklapelletcan.bin.sig. Pozostale kanaly w manifescie zostaja bez zmian.
"""
import argparse, datetime, hashlib, json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--dir", required=True); p.add_argument("--channel", required=True, choices=["beta", "stable"])
p.add_argument("--version", required=True); p.add_argument("--build", type=int, required=True)
p.add_argument("--commit", default=""); p.add_argument("--notes", default="")
a = p.parse_args()

d = Path(a.dir)
binf, sigf = d / a.channel / "teklapelletcan.bin", d / a.channel / "teklapelletcan.bin.sig"
data = binf.read_bytes()
sig = sigf.read_text().strip()
if len(sig) != 128:
    raise SystemExit("podpis musi miec 128 znakow hex")
mf = d / "manifest.json"
m = json.loads(mf.read_text()) if mf.exists() else {"channels": {}}
m.setdefault("channels", {})[a.channel] = {
    "version": a.version, "build": a.build, "full": f"{a.version}+{a.build}",
    "file": f"{a.channel}/teklapelletcan.bin", "sig": f"{a.channel}/teklapelletcan.bin.sig",
    "sha256": hashlib.sha256(data).hexdigest(), "size": len(data), "commit": a.commit,
    "notes": a.notes.strip()[:400], "date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
}
mf.write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"manifest: kanal {a.channel} -> {a.version}+{a.build}, {len(data)} B")
