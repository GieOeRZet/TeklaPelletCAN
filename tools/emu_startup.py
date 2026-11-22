#!/usr/bin/env python3
"""NewEstyma: emulacja kodu startowego FW2213TK w Unicornie (Cortex-M4).

Uzycie:
  python3 -I tools/emu_startup.py FW2213TK_kopia.bin [--max N] [--ram out.bin]
         [--watch 0xLO:0xHI ...] [--trace-calls 0xADDR ...] [--patch-nop 0xADDR ...]

Adresy: obraz jest mapowany pod RUNTIME 0x08010000 (= PROJECT + 0x10000 = RAW + 0x08010000).
Argumenty --watch/--trace-calls/--patch-nop przyjmuja adresy RUNTIME (true).
Wyjscie jest deterministyczne. NIE modeluje: przerwan, schedulera FreeRTOS, peryferiow (zwracaja 0).
Pętle czekania na sprzet wykrywane sa heurystycznie (PC powtarzany) i raportowane - dodaj --patch-nop.
"""
import argparse, hashlib, struct, sys
from unicorn import (Uc, UcError, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS,
                     UC_HOOK_MEM_WRITE, UC_HOOK_CODE, UC_HOOK_BLOCK, UC_HOOK_MEM_READ_UNMAPPED,
                     UC_HOOK_MEM_WRITE_UNMAPPED, UC_HOOK_MEM_FETCH_UNMAPPED)
from unicorn.arm_const import *

BASE = 0x08010000
SHA = "1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071"
DEFAULT_NOP = (0x080745D2, 0x080745F4, 0x0801DC36)   # petle RCC (SystemInit) - tylko kopia w pamieci

def hx(s): return int(s, 0)

def build(path, nops, extra_regions=()):
    raw = open(path, "rb").read()
    assert hashlib.sha256(raw).hexdigest() == SHA, "to nie kanoniczny FW2213TK_kopia.bin"
    img = bytearray(raw)
    for a in nops:
        o = a - BASE; img[o:o+2] = b"\x00\xbf"
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    mu.mem_map(0x08000000, 0x210000); mu.mem_write(BASE, bytes(img))
    mu.mem_map(0x20000000, 0x40000)
    for b, s in ((0x40000000,0x100000),(0x42000000,0x100000),(0xE0000000,0x100000),(0x10000000,0x10000)):
        mu.mem_map(b, s)
    mu.reg_write(UC_ARM_REG_SP, struct.unpack_from("<I", raw, 0)[0])
    mu.reg_write(UC_ARM_REG_C1_C0_2, mu.reg_read(UC_ARM_REG_C1_C0_2) | (0xF << 20))
    mu.reg_write(UC_ARM_REG_FPEXC, 0x40000000)
    def unm(uc, access, addr, size, val, ud):
        page = addr & ~0xFFF
        try: uc.mem_map(page, 0x1000)
        except UcError: return False
        unm.pages.append(page); return True
    unm.pages = []
    for h in (UC_HOOK_MEM_READ_UNMAPPED, UC_HOOK_MEM_WRITE_UNMAPPED):
        mu.hook_add(h, unm)
    return mu, raw, unm


SVC_PC, TCB_LIT = 0x08068198, 0x08068174 + 4 + 0x30   # svc #0 (vPortStartFirstTask); literal = adres pxCurrentTCB
RCC_GETFLAG = 0x08028AE4                              # RCC_GetFlagStatus (SPL) - firmware czeka na gotowosc zegarow

def install_stub(mu, ad, val):
    """funkcja pod RUNTIME-adresem ad zwraca val (r0) bez wykonywania"""
    def st(uc, addr, size, ud):
        uc.reg_write(UC_ARM_REG_R0, val); uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
    ad &= ~1; mu.hook_add(UC_HOOK_CODE, st, begin=ad, end=ad)

def install_first_task(mu, raw):
    """odtwarza svc #0: wczytuje kontekst pierwszego zadania FreeRTOS z pxCurrentTCB i wchodzi w jego kod"""
    def first_task(uc, addr, size, ud):
        rd = lambda ad: struct.unpack("<I", bytes(uc.mem_read(ad, 4)))[0]
        tcb_ptr = struct.unpack_from("<I", raw, (TCB_LIT & ~3) - BASE)[0]
        sp = rd(rd(tcb_ptr))
        regs = [rd(sp + 4*i) for i in range(9)]
        for r, v in zip((UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11), regs[:8]):
            uc.reg_write(r, v)
        psp = sp + 36
        fr = [rd(psp + 4*i) for i in range(8)]
        for r, v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R12,UC_ARM_REG_LR), fr[:6]):
            uc.reg_write(r, v)
        uc.reg_write(UC_ARM_REG_SP, psp + 32); uc.reg_write(UC_ARM_REG_PC, fr[6] | 1)
        print("first-task: TCB=0x%08X task_pc=0x%08X sp=0x%08X" % (rd(tcb_ptr), fr[6], psp + 32))
    mu.hook_add(UC_HOOK_CODE, first_task, begin=SVC_PC, end=SVC_PC)

def boot(path, max_insns=1_500_000_000):
    """standardowy bieg: startup + RCC stub + pierwsze zadanie FreeRTOS; zwraca (mu, raw)"""
    mu, raw, unm = build(path, DEFAULT_NOP)
    install_stub(mu, RCC_GETFLAG, 1); install_first_task(mu, raw)
    try: mu.emu_start(struct.unpack_from("<I", raw, 4)[0], 0, count=max_insns)
    except UcError as e: print("zatrzymano:", e)
    return mu, raw

def read_ram(mu, addr, n): return bytes(mu.mem_read(addr, n))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bin"); ap.add_argument("--max", type=int, default=5_000_000)
    ap.add_argument("--ram"); ap.add_argument("--watch", action="append", default=[])
    ap.add_argument("--trace-calls", action="append", default=[])
    ap.add_argument("--patch-nop", action="append", default=[])
    ap.add_argument("--start", default=None)
    ap.add_argument("--first-task", action="store_true", help="odtworz svc #0 (vPortStartFirstTask) i wejdz w kod pierwszego zadania FreeRTOS")
    ap.add_argument("--stub", action="append", default=[], help="ADDR=VAL: funkcja o adresie RUNTIME zwraca VAL (r0) bez wykonywania")
    a = ap.parse_args()
    nops = list(DEFAULT_NOP) + [hx(x) for x in a.patch_nop]
    mu, raw, unm = build(a.bin, nops)
    watch = [tuple(hx(p) for p in w.split(":")) for w in a.watch]
    wlog = []
    def onw(uc, acc, addr, size, val, ud):
        if any(lo <= addr < hi for lo, hi in watch):
            wlog.append((uc.reg_read(UC_ARM_REG_PC), addr, size, val & 0xFFFFFFFF))
    if watch: mu.hook_add(UC_HOOK_MEM_WRITE, onw)
    tc = {hx(x) & ~1 for x in a.trace_calls}; clog = []
    pcs = {}
    def oncall(uc, addr, size, ud):
        clog.append((addr, [uc.reg_read(r) for r in (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3)],
                     bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP), 32)), uc.reg_read(UC_ARM_REG_LR)))
    for t in tc: mu.hook_add(UC_HOOK_CODE, oncall, begin=t, end=t)   # tylko wskazane adresy (szybko)
    for sp_ in a.stub:
        ad, v = sp_.split("="); install_stub(mu, hx(ad), hx(v))
    if a.first_task: install_first_task(mu, raw)
    start = hx(a.start) if a.start else struct.unpack_from("<I", raw, 4)[0]
    try:
        mu.emu_start(start, 0, count=a.max)
    except UcError as e:
        print("zatrzymano:", e)
    pc = mu.reg_read(UC_ARM_REG_PC)
    print("pc koncowy: 0x%08X" % pc)
    if unm.pages: print("auto-zmapowane strony:", ", ".join(hex(p) for p in unm.pages[:12]))
    for pc_, ad, sz, v in wlog: print("W pc=0x%08X [0x%08X] <- 0x%X (%dB)" % (pc_, ad, v, sz))
    for ad, regs, stk, lr in clog:
        print("CALL 0x%08X lr=0x%08X r0-3=%s stack=%s" % (ad, lr, [hex(r) for r in regs], stk.hex()))
    if a.ram:
        open(a.ram, "wb").write(bytes(mu.mem_read(0x20000000, 0x40000)))
        print("SRAM ->", a.ram)

if __name__ == "__main__":
    main()
