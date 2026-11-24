#!/usr/bin/env python3
"""PASS 58: powiazanie pol tekstowych ekranu z PID-ami (B1 planu 1:1). Dla stanu ekranu: (1) wszystkie PID-y z tabeli runtime (lub BIND_PIDS=lista hex);
(2) dla kazdego PID-a (klasy live/ustawienie, bez blokowanych) wstrzykuje unikalna wartosc znacznikowa (inject_param) i obserwuje wywolania snprintf (0x08041134) -> bufor docelowy, format, wartosc;
(3) bufor -> widget (obiekt z polem +0x34 == bufor; rect i pozycja bezwzgledna). Wynik: tabela PID -> (widget, format, skala).
python3 -I tools/data_binding.py FW.bin STATE OUT.json"""
import json, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
fw, st, out = sys.argv[1:4]
raw = open(fw, "rb").read(); B = 0x08010000
s = U.UiSession.from_checkpoint(fw, st, None); s.enable_trace(); s.wait(500)
import csv
pids = sorted(int(r["key"], 16) for r in csv.DictReader(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analiza_archiwum", "FW2213TK-2026-11-22", "data", "runtime_param_table_655.csv"), encoding="utf-8")) if int(r["key"], 16) not in (0x3722, 0x3723))
if os.environ.get("BIND_PIDS"): pids = [int(x, 16) for x in os.environ["BIND_PIDS"].split(",")]
print("PID-y do wstrzykniecia:", len(pids), flush=True)
events = []
def sn(uc, a, sz, ud):
    r0, r2, r3, sp = (uc.reg_read(x) for x in (UC_ARM_REG_R0, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP))
    try: fmt = bytes(uc.mem_read(r2, 24)).split(b"\0")[0].decode("latin1") if r2 < 0x20000000 else "?"
    except Exception: fmt = "?"
    st1 = int.from_bytes(bytes(uc.mem_read(sp, 4)), "little")
    events.append(dict(dest=r0, fmt=fmt, a1=r3, a2=st1, lr=uc.reg_read(UC_ARM_REG_LR)))
s.b.mu.hook_add(UC_HOOK_CODE, sn, begin=0x08041134, end=0x08041134)
def widget_of(buf):
    mem = bytes(s.b.mu.mem_read(0x20000000, 0x30000))
    for o in range(0, 0x30000 - 0x40, 4):
        if int.from_bytes(mem[o + 0x34:o + 0x38], "little") == buf and 0x08070000 <= int.from_bytes(mem[o:o + 4], "little") < 0x08090000:
            a = 0x20000000 + o; x = y = 0; p = a
            for _ in range(12):
                if not (0x20000000 <= p < 0x20030000): break
                x += struct.unpack_from("<h", mem, p - 0x20000000 + 4)[0]; y += struct.unpack_from("<h", mem, p - 0x20000000 + 6)[0]; p = int.from_bytes(mem[p - 0x20000000 + 0x14:p - 0x20000000 + 0x18], "little")
            w, h = struct.unpack_from("<hh", mem, o + 8); return dict(widget=hex(a), ax=x, ay=y, w=w, h=h)
    return None
res = []
for k, pid in enumerate(pids):
    r = s._record(pid)
    if r is None: continue
    st_addr, ty = r; mx = {1: 200, 2: 900, 3: 90000, 4: 700, 5: 90000}[ty]; marker = 23 + 7 * (k % 31) + 100 * (k // 31)   # unikalny, mieszczacy sie w typach
    marker = min(marker, mx)
    events.clear(); got = s.inject_param(pid, marker, 2, 60); s.wait(250)
    ok = got == marker and marker >= 20
    hits = [e for e in events if ok and ((e["a1"] == marker) or (e["a1"] == marker // 10 and e["a2"] == marker % 10) or (e["a1"] == marker // 100 and e["a2"] == marker // 10 % 10))]
    row = dict(pid="0x%04X" % pid, type=ty, marker=marker, stored=got, formats=sorted({e["fmt"] for e in hits}))
    row["widgets"] = [dict(widget_of(e["dest"]) or {}, fmt=e["fmt"], dest=hex(e["dest"])) for e in {e["dest"]: e for e in hits}.values()]
    res.append(row); print(row["pid"], got, row["formats"], [(w.get("ax"), w.get("ay")) for w in row["widgets"]], flush=True)
    json.dump(res, open(out, "w"), indent=1)
