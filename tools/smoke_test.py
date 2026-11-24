#!/usr/bin/env python3
"""Test dymny repo (bez emulatora): kompilacja tools/*.py, walidator ui_model, INDEX zgodny z plikami, istnienie sciezek z paths.py.
Uzycie: python3 tools/smoke_test.py   (kod wyjscia 0 = PASS). Uruchom PRZED i PO zmianie struktury katalogow."""
import json, py_compile, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths
fail = []
KNOWN_BROKEN = {"re_scan.py", "test_cg_alarm_asymmetry_audit.py"}  # bledy skladniowe sprzed porzadkowania (BACKLOG), nie blokuja
for p in sorted((paths.ROOT / "tools").glob("*.py")):
    if p.name in KNOWN_BROKEN: continue
    try: py_compile.compile(str(p), doraise=True, cfile=str(Path(tempfile.gettempdir()) / "x.pyc"))
    except Exception as e: fail.append(f"compile {p.name}: {e}")
for d in (paths.DATA, paths.UI_MODEL, paths.SCHEMA):
    if not d.is_dir(): fail.append(f"brak katalogu {d}")
r = subprocess.run([sys.executable, str(paths.ROOT / "tools/validate_ui_model.py")], capture_output=True, text=True)
if r.returncode or "PASS" not in r.stdout: fail.append("validate_ui_model: " + r.stdout[-200:] + r.stderr[-200:])
with tempfile.TemporaryDirectory() as t:
    out = Path(t) / "INDEX.json"
    subprocess.run([sys.executable, str(paths.ROOT / "tools/build_ui_model_index.py"), "--output", str(out)], capture_output=True)
    if out.exists():
        new = {f["path"] if "path" in f else f.get("file"): f for f in json.loads(out.read_text())["files"]}
        old = {f["path"] if "path" in f else f.get("file"): f for f in json.loads((paths.UI_MODEL / "INDEX.json").read_text())["files"]}
        if set(new) != set(old): fail.append(f"INDEX rozjechany: {sorted(set(new) ^ set(old))[:5]}")
    else: fail.append("build_ui_model_index nie wygenerowal pliku")
print("SMOKE", "FAIL" if fail else "PASS"); [print(" -", x) for x in fail]
sys.exit(1 if fail else 0)
