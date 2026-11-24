#!/usr/bin/env python3
"""PASS 70: lokalny inwentarz repo (uzupelnienie wynikow ChatGPT: numery linii i SHA-256). Tylko odczyt.
Wyjscie: NewEstyma/porzadek_lokalny/odwolania_lokalne.csv (plik, linia, tekst, rodzaj), sha256_pliki.csv (plik, rozmiar, sha256), duplikaty_sha256.csv (sha256, pliki).
Uzycie: python3 -I tools/inventory_repo.py"""
import csv, hashlib, os, re, subprocess, collections
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
files = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
os.makedirs("NewEstyma/porzadek_lokalny", exist_ok=True)
def kind(p):
    if p.startswith("tools/") and not p.split("/")[-1].startswith("test_"): return "kod-narzedzia"
    if p.startswith("tests/") or "/test_" in p or p.split("/")[-1].startswith("test_"): return "test"
    if p.startswith((".github/", "scripts/")) or p.endswith((".yml", ".yaml")): return "CI/konfiguracja"
    if p.endswith((".md", ".txt", ".rst")): return "dokumentacja"
    if p.startswith(("custom_components/", "firmware/", "android/", "web/", "software/", "rejestry/")): return "INTEGRACJA-uwaga"
    return "inne"
rx = re.compile(r"analiza_archiwum/[^\s\"'`)>,;]*")
sha = {}; refs = []; dup = collections.defaultdict(list)
for p in files:
    try:
        data = open(p, "rb").read()
    except Exception: continue
    h = hashlib.sha256(data).hexdigest(); sha[p] = (len(data), h); dup[h].append(p)
    if len(data) < 3_000_000 and not p.lower().endswith((".png", ".bin", ".jpg", ".zip", ".gz")):
        try: txt = data.decode("utf-8")
        except Exception: continue
        for i, line in enumerate(txt.splitlines(), 1):
            for m in rx.findall(line): refs.append((p, i, m, kind(p)))
with open("NewEstyma/porzadek_lokalny/odwolania_lokalne.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["plik", "linia", "sciezka", "rodzaj"]); w.writerows(refs)
with open("NewEstyma/porzadek_lokalny/sha256_pliki.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["plik", "rozmiar", "sha256"]); [w.writerow([p, s, h]) for p, (s, h) in sorted(sha.items())]
with open("NewEstyma/porzadek_lokalny/duplikaty_sha256.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["sha256", "liczba", "pliki"]); [w.writerow([h, len(v), " | ".join(v)]) for h, v in dup.items() if len(v) > 1 and any(x.startswith("analiza_archiwum/") for x in v)]
nd = sum(1 for v in dup.values() if len(v) > 1 and any(x.startswith("analiza_archiwum/") for x in v))
print("plikow", len(files), "odwolan", len(refs), "w plikach", len({r[0] for r in refs}), "grup duplikatow (analiza)", nd)
print(collections.Counter(r[3] for r in refs))
