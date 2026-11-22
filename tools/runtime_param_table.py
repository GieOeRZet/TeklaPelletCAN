#!/usr/bin/env python3
"""NewEstyma: tabela runtime parametrow (manager 0x20008D84) odczytana z RAM po emulacji startupu.

python3 -I tools/runtime_param_table.py FW2213TK_kopia.bin [out.csv]

Rekord (stride 0x2C, baza = manager+0x08; wszystkie pola u32 LE) — ZWERYFIKOWANE na danych (PASS 35):
 +0x00 key            klucz wyszukiwania (0x080115F6)   +0x04 storage ptr (SRAM)
 +0x08 type           kod typu 1/2/3/4/5               +0x0C min
 +0x10 type(min)      +0x14 max      +0x18 type(max)   +0x1C default   +0x20 type(def)
 +0x24 klasa          (sidecar 0/1/2/3; rejestracja)    +0x28 wskaznik RUNTIME do nazwy ASCII
Pola wartosci (min/max/default) sa u32, ale znaczace tylko wg WLASNEGO kodu typu (+0x10/+0x18/+0x20): 1=u8, 2=u16, 4=s16, 3/5=u32; reszta bitow = smieci ze stosu.
"""
import csv, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import emu_startup as E

MGR, COUNT, STRIDE, BASE = 0x20008D84, 660, 0x2C, 0x08010000
CONFIG = 0x200208EC   # obiekt konfiguracji (storage klucza 3 = CONFIG+0x16BE)
TYPE = {1: "u8", 2: "u16", 3: "u32", 4: "s16", 5: "u32?"}

def cstr(raw, p):
    if not (BASE <= p < BASE + len(raw)): return None
    o = p - BASE; e = raw.index(b"\0", o)
    b = raw[o:e]
    return b.decode("ascii") if b and all(32 <= c < 127 for c in b) else None

def val(v, t):
    """pole wartosci zapisane jako u32, ale znaczace tylko tyle bajtow, ile mowi jego kod typu (reszta = smieci ze stosu)"""
    if t == 1: return v & 0xFF
    if t == 2: return v & 0xFFFF
    if t == 4:
        v &= 0xFFFF; return v - 0x10000 if v & 0x8000 else v
    return v

def table(path):
    mu, raw = E.boot(path)
    ram = E.read_ram(mu, 0x20000000, 0x40000)
    rows = []
    for i in range(COUNT):
        o = MGR - 0x20000000 + 8 + i * STRIDE
        w = struct.unpack_from("<11I", ram, o)
        if not any(w): continue
        key, st, ty, mn, tmn, mx, tmx, df, tdf, cls, nm = w
        rows.append(dict(slot=i, key=key, storage=st, cfg_off=(st - CONFIG) if CONFIG <= st < CONFIG + 0x4000 else "",
                         type=ty, type_name=TYPE.get(ty, "?"), min=val(mn, tmn), max=val(mx, tmx), default=val(df, tdf), min_t=tmn, max_t=tmx, def_t=tdf,
                         cls=cls, name_ptr=nm, name=cstr(raw, nm) or ""))
    return rows

if __name__ == "__main__":
    rows = table(sys.argv[1])
    out = sys.argv[2] if len(sys.argv) > 2 else None
    f = open(out, "w", newline="") if out else sys.stdout
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader()
    for r in rows:
        r = dict(r); r["key"] = "0x%04X" % r["key"]; r["storage"] = "0x%08X" % r["storage"]; r["name_ptr"] = "0x%08X" % r["name_ptr"]
        if r["cfg_off"] != "": r["cfg_off"] = "0x%X" % r["cfg_off"]
        w.writerow(r)
    print("rekordow:", len(rows), file=sys.stderr)
