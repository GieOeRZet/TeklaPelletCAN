#!/usr/bin/env python3
"""NewEstyma: sekwencja zadan odczytu 0x0604 generowana przez poller FUN_080629FC (PROJECT; RUNTIME 0x080729FC) po emulacji startupu.
python3 -I tools/poller_trace.py FW2213TK_kopia.bin runtime_param_table_655.csv out.csv

Wywoluje poller jako funkcje (obiekt 0x2002466C) i przechwytuje 20-bajtowy rekord w wywolaniu prymitywu kolejki TX
(PROJECT 0x08057224 = RUNTIME 0x08067224), czyli dokladnie to, co trafia do CanTxTask.
UWAGA: pola obiektu +0x08 (start) i +0x10 (aktywny) sa USTAWIANE przez harness; ich producent w prawdziwym runtime jest OPEN."""
import csv, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import emu_startup as E
from unicorn import UcError, UC_HOOK_CODE
from unicorn.arm_const import *
OBJ, POLLER, QSEND, SENT = 0x2002466C, 0x080729FC, 0x08067224, 0x08010002
mu, raw = E.boot(sys.argv[1])
recs = []
def q(uc, a, s, ud):
    recs.append(bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1), 20)))
    uc.reg_write(UC_ARM_REG_R0, 1); uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
mu.hook_add(UC_HOOK_CODE, q, begin=QSEND, end=QSEND)
mu.hook_add(UC_HOOK_CODE, lambda uc, a, s, u: uc.emu_stop(), begin=SENT & ~1, end=SENT & ~1)
mu.mem_write(OBJ + 8, b"\x01"); mu.mem_write(OBJ + 0x10, b"\x01")
for i in range(2000):
    n = len(recs)
    mu.reg_write(UC_ARM_REG_R0, OBJ); mu.reg_write(UC_ARM_REG_LR, SENT | 1); mu.reg_write(UC_ARM_REG_SP, 0x20012000)
    try: mu.emu_start(POLLER | 1, 0, count=200000)
    except UcError as e: print("blad:", e); break
    if bytes(mu.mem_read(OBJ + 8, 1))[0] == 0 and len(recs) > 0: break
rt = {int(r["key"], 16): r["name"] for r in csv.DictReader(open(sys.argv[2]))}
with open(sys.argv[3], "w", newline="") as f:
    w = csv.writer(f); w.writerow(["order", "pid", "name", "can_id", "dlc", "data_hex"])
    for i, r in enumerate(recs):
        sid, dlc, data = struct.unpack_from("<I", r, 0)[0], r[10], r[11:19]
        pid = data[1] | data[2] << 8
        w.writerow([i, "0x%04X" % pid, rt.get(pid, ""), "0x%03X" % sid, dlc, data.hex(" ")])
print("zadan odczytu:", len(recs))
