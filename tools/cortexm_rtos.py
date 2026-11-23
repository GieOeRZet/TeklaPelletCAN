#!/usr/bin/env python3
"""NewEstyma: emulator systemowy FW2213TK (STM32F4 / Cortex-M4 + FreeRTOS) na Unicornie.

Wzgledem tools/emu_startup.py dodaje PELNY model wyjatkow Cortex-M, wiec dziala kompletny scheduler FreeRTOS:
  * SVC (np. vPortStartFirstTask), SysTick, PendSV, dowolne IRQ z tablicy wektorow (np. CAN2 RX0) — wejscie/wyjscie z wyjatku
    robione recznie na natywnych rejestrach Unicorna (MSP/PSP/BASEPRI/PRIMASK): ramka r0-r3,r12,lr,pc,xpsr na stosie watku;
  * powrot z wyjatku wykrywany z UC_HOOK_INTR (intno 8, PC=0xFFFFFFFC) — Unicorn nie wektoryzuje wyjatkow sam;
  * PendSV zadany zapisem ICSR (0xE000ED04 bit 28) jest wstrzykiwany zaraz po instrukcji zapisu (taskYIELD);
  * SysTick wstrzykiwany co `tick` instrukcji (maskowany gdy BASEPRI/PRIMASK != 0 lub trwa inny wyjatek).
Model NIE zawiera: prawdziwego NVIC (priorytety poza maskowaniem BASEPRI), DMA, timerow, LCD/FSMC, CAN HW (patrz raise_irq / hooki uzytkownika).
Adresy w API sa RUNTIME (obraz pod 0x08010000), jak w emu_startup.py.

Uzycie:  b = Board("FW2213TK_kopia.bin"); b.run(slices=200); print(b.task_name())
"""
import os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import emu_startup as E
from unicorn import UcError, UC_HOOK_INTR, UC_HOOK_MEM_WRITE, UC_HOOK_CODE
from unicorn.arm_const import *

ICSR, EXC_RET_STOP = 0xE000ED04, 0xFFFFFFF0
MSP_TOP = 0x20013F28           # poczatkowy SP z tablicy wektorow (stos wyjatkow po starcie schedulera)
PXCURRENTTCB_LIT = 0x08068174 + 4 + 0x30   # literal w vPortSVCHandler: adres zmiennej pxCurrentTCB (wg PASS 34)

class Board:
    def __init__(self, binpath, tick=20000, patch_rcc=True):
        self.mu, self.raw, self.unm = E.build(binpath, E.DEFAULT_NOP)
        mu = self.mu
        mu.mem_map(0xC0000000, 0x1000000)   # SDRAM (FMC Bank 5/6): bufor ramki LTDC 0xC0000000, 16 MB
        if patch_rcc: E.install_stub(mu, E.RCC_GETFLAG, 1)
        self.vt = struct.unpack_from("<%dI" % 128, self.raw, 0)
        self.tick = tick; self.boot_budget = 200_000_000
        self.switches = []         # nazwy zadan po kazdym PendSV (przelaczenie kontekstu)
        self.pend = set()          # oczekujace wyjatki (numery: 11 SVC, 14 PendSV, 15 SysTick, 16+ IRQ)
        self.stack = []            # aktywne wyjatki: (excno, lr_ret)
        self._why = "count"
        self.fault = None; self.log = []              # dziennik zdarzen (excno, task)
        self.counters = {"svc": 0, "systick": 0, "pendsv": 0, "irq": 0, "ret": 0}
        self.on_exc = None         # callback(excno) przy wejsciu w wyjatek
        self.tcb_ptr = struct.unpack_from("<I", self.raw, (PXCURRENTTCB_LIT & ~3) - E.BASE)[0]
        mu.hook_add(UC_HOOK_INTR, self._intr)
        mu.hook_add(UC_HOOK_MEM_WRITE, self._memw, begin=ICSR, end=ICSR + 3)
        mu.reg_write(UC_ARM_REG_SP, self.vt[0])
        self.pc = self.vt[1] & ~1
        self.thumb_sp_msp = MSP_TOP

    # ---- pamiec / rejestry ----
    def rd(self, a, n=4): return int.from_bytes(self.mu.mem_read(a, n), "little")
    def wr(self, a, v, n=4): self.mu.mem_write(a, (v & ((1 << 8 * n) - 1)).to_bytes(n, "little"))
    def reg(self, r): return self.mu.reg_read(r)

    # ---- wyjatki ----
    def _memw(self, uc, access, addr, size, val, ud):
        if addr == ICSR and val & (1 << 28):                 # PENDSVSET (taskYIELD / koniec SysTick)
            self.pend.add(14)
            # zatrzymaj PO tej instrukcji zapisu (wzorzec: portYIELD wywoluje PendSV natychmiast): jednorazowy hook na nastepnej instrukcji
            pc = uc.reg_read(UC_ARM_REG_PC) & ~1
            h = struct.unpack("<H", bytes(uc.mem_read(pc, 2)))[0]
            nxt = pc + (4 if (h >> 11) in (0x1D, 0x1E, 0x1F) else 2)
            def once(u, a, sz, ud, self=self):
                self._why = "icsr"; u.emu_stop()
                try: u.hook_del(self._oh)
                except Exception: pass
            self._oh = uc.hook_add(UC_HOOK_CODE, once, begin=nxt, end=nxt)
    def _intr(self, uc, intno, ud):
        pc = uc.reg_read(UC_ARM_REG_PC)
        if intno == 2:                                        # SVC
            self.counters["svc"] += 1; self._why = "svc"; uc.emu_stop()
        elif intno == 8 and pc >= EXC_RET_STOP:               # powrot z wyjatku (EXC_RETURN w PC)
            self._exc_return(pc | 1); self._why = "ret"; uc.emu_stop()
        else:
            self.fault = dict(intno=intno, pc=pc, lr=uc.reg_read(UC_ARM_REG_LR), sp=uc.reg_read(UC_ARM_REG_SP), task=self.task_name(), counters=dict(self.counters), stack=list(self.stack),
                              regs={n: uc.reg_read(r) for n, r in zip(("r0","r1","r2","r3","r4","r5","r6","r7"), (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7))})
            self._why = "fault"; uc.emu_stop()

    def masked(self):
        return bool(self.stack) or self.reg(UC_ARM_REG_BASEPRI) != 0 or self.reg(UC_ARM_REG_PRIMASK) != 0
    def _enter(self, excno, resume_pc):
        mu = self.mu; handler = self.vt[excno] & ~1
        in_thread = not self.stack
        sp = self.reg(UC_ARM_REG_SP) if in_thread else self.reg(UC_ARM_REG_SP)
        xpsr = self.reg(UC_ARM_REG_XPSR) | (1 << 24)
        sp0 = sp; sp = (sp - 32) & ~7
        if (sp0 - 32) & 4: xpsr |= (1 << 9)                  # STKALIGN: bit 9 = ramka dopelniona o 4 B (zapamietane do powrotu)
        frame = [self.reg(r) for r in (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_R12, UC_ARM_REG_LR)] + [resume_pc | 1, xpsr]
        mu.mem_write(sp, struct.pack("<8I", *frame))
        if in_thread:
            self.reg_psp = sp; mu.reg_write(UC_ARM_REG_PSP, sp)
            mu.reg_write(UC_ARM_REG_SP, self.thumb_sp_msp)
            lr = 0xFFFFFFFD
        else:
            mu.reg_write(UC_ARM_REG_SP, sp); lr = 0xFFFFFFF1
        mu.reg_write(UC_ARM_REG_LR, lr)
        self.stack.append((excno, lr)); self.pc = handler
        if excno == 15: self.counters["systick"] += 1
        elif excno == 14: self.counters["pendsv"] += 1
        elif excno >= 16: self.counters["irq"] += 1
        if self.on_exc: self.on_exc(excno)
    def _exc_return(self, retpc):
        mu = self.mu; excno, lr_ent = self.stack.pop(); self.counters["ret"] += 1
        if (retpc & ~1) == 0xFFFFFFFC:                        # EXC_RETURN 0xFFFFFFFD (thread, PSP)
            sp = self.reg(UC_ARM_REG_PSP)
        elif (retpc & ~1) == 0xFFFFFFF8:                      # 0xFFFFFFF9 (thread, MSP)
            sp = self.reg(UC_ARM_REG_SP)
        else:                                                 # 0xFFFFFFF1 (handler)
            sp = self.reg(UC_ARM_REG_SP)
        w = struct.unpack("<8I", bytes(mu.mem_read(sp, 32)))
        for r, v in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_R12, UC_ARM_REG_LR), w[:6]): mu.reg_write(r, v)
        mu.reg_write(UC_ARM_REG_XPSR, w[7] & ~(1 << 9))
        mu.reg_write(UC_ARM_REG_SP, sp + 32 + (4 if w[7] & (1 << 9) else 0))
        self.pc = w[6] & ~1
        if excno == 14: self.switches.append(self.task_name())

    def raise_irq(self, irqn): self.pend.add(16 + irqn)


    # ---- punkty kontrolne (checkpoint/restore) ----
    _REGS = ("R0","R1","R2","R3","R4","R5","R6","R7","R8","R9","R10","R11","R12","SP","LR","XPSR","MSP","PSP","BASEPRI","PRIMASK","FAULTMASK","CONTROL","FPSCR","FPEXC")
    def save_state(self, path, extra=None):
        """zapis pelnego stanu: rejestry, wszystkie zmapowane regiony poza flashem (SRAM, SDRAM, peryferia, CCM...), stan schedulera i modeli.
        extra: dowolny obiekt do zapisania (np. stan sesji UI). Plik jest skompresowany (zlib)."""
        import pickle, zlib
        from unicorn import arm_const as A
        regs = {n: self.mu.reg_read(getattr(A, "UC_ARM_REG_" + n)) for n in self._REGS if hasattr(A, "UC_ARM_REG_" + n)}
        mem = []
        for lo, hi, perm in self.mu.mem_regions():
            if 0x08000000 <= lo < 0x08300000 or lo < 0x1000 or lo >= 0xE0000000: continue          # flash i tablica wektorow nie sa zapisywane
            mem.append((lo, bytes(self.mu.mem_read(lo, hi - lo + 1))))
        models = {}
        if hasattr(self, "i2c"):
            models["i2c"] = {base: {k: v for k, v in i.__dict__.items() if k in ("log", "state", "addr", "rw", "rd_buf")} for base, i in self.i2c.items()}
            models["i2c_slaves"] = {base: {a: sl.__dict__.copy() for a, sl in i.slaves.items()} for base, i in self.i2c.items()}
        if hasattr(self, "can2"): models["can2"] = dict(tx=list(self.can2.tx), rx_log=list(self.can2.rx_log))
        if hasattr(self, "dma2d"): models["dma2d"] = dict(log=len(self.dma2d.log))
        st = dict(regs=regs, mem=mem, pc=self.pc, pend=set(self.pend), stack=list(self.stack), counters=dict(self.counters), switches=list(self.switches), models=models, extra=extra)
        with open(path, "wb") as f: f.write(zlib.compress(pickle.dumps(st), 3))
    def load_state(self, path):
        """wczytanie stanu zapisanego save_state; wymaga Board z tymi samymi wlaczonymi modelami (enable_*). Zwraca 'extra'."""
        import pickle, zlib
        from unicorn import arm_const as A
        st = pickle.loads(zlib.decompress(open(path, "rb").read()))
        have = [(lo, hi) for lo, hi, _ in self.mu.mem_regions()]
        for lo, data in st["mem"]:
            if not any(l <= lo and lo + len(data) - 1 <= h for l, h in have):
                try: self.mu.mem_map(lo & ~0xFFF, ((len(data) + (lo & 0xFFF) + 0xFFF) & ~0xFFF))
                except Exception: pass
            self.mu.mem_write(lo, data)
        for n, v in st["regs"].items(): self.mu.reg_write(getattr(A, "UC_ARM_REG_" + n), v)
        self.pc, self.pend, self.stack = st["pc"], set(st["pend"]), list(st["stack"]); self.counters.update(st["counters"]); self.switches = list(st["switches"])
        m = st["models"]
        if "i2c" in m and hasattr(self, "i2c"):
            for base, d in m["i2c"].items(): self.i2c[base].__dict__.update(d)
            for base, sl in m.get("i2c_slaves", {}).items():
                for a, d in sl.items(): self.i2c[base].slaves[a].__dict__.update(d)
        if "can2" in m and hasattr(self, "can2"): self.can2.tx[:] = m["can2"]["tx"]; self.can2.rx_log[:] = m["can2"]["rx_log"]
        return st["extra"]

    def enable_i2c(self, base=0x40005400, slaves=None):
        import stm32_i2c; i = stm32_i2c.I2C(self, base, slaves); self.i2c = getattr(self, 'i2c', {}); self.i2c[base] = i; return i

    def enable_rtc(self, start=None, ticks_per_s=1000):
        import stm32_rtc; self.rtc = stm32_rtc.Rtc(self, start=start, ticks_per_s=ticks_per_s); return self.rtc

    def enable_can2(self):
        import stm32_can; self.can2 = stm32_can.Can2(self); return self.can2

    def enable_dma2d(self):
        import stm32_dma2d; self.dma2d = stm32_dma2d.Dma2D(self); return self.dma2d

    # ---- informacje o schedulerze ----
    def current_tcb(self): return self.rd(self.rd(self.tcb_ptr)) if False else self.rd(self.tcb_ptr)
    def task_name(self):
        t = self.current_tcb()
        if not (0x20000000 <= t < 0x20040000): return "?"
        try: s = bytes(self.mu.mem_read(t + 0x34, 16)).split(b"\0")[0].decode("ascii", "replace")
        except Exception: return "?"
        return s

    def diag(self, why=""):
        """stan w chwili awarii: zadanie, rejestry, slad wywolan (adresy powrotu Thumb ze stosu)"""
        sp = self.reg(UC_ARM_REG_SP)
        try: ws = struct.unpack("<64I", bytes(self.mu.mem_read(sp, 256)))
        except Exception: ws = ()
        names = ("r0","r1","r2","r3","r4","r5","r6","r7","r8")
        regs = {n: self.reg(r) for n, r in zip(names, (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8))}
        return dict(why=why, task=self.task_name(), pc=self.reg(UC_ARM_REG_PC), lr=self.reg(UC_ARM_REG_LR), sp=sp, regs=regs,
                    trace=[w for w in ws if 0x08010000 <= w < 0x08200000 and w & 1][:14], counters=dict(self.counters), stack=list(self.stack))

    # ---- petla wykonania ----
    def _burst(self, budget):
        """jedna porcja wykonania; zwraca przyczyne zatrzymania: 'svc' | 'ret' | 'icsr' | 'count'"""
        self._why = "count"
        try: self.mu.emu_start(self.pc | 1, 0, count=budget)
        except UcError as e:
            self.fault = self.diag(str(e)); raise RuntimeError("blad emulacji: %s pc=0x%X" % (e, self.reg(UC_ARM_REG_PC)))
        if self._why == "fault": raise RuntimeError("FAULT %r" % self.fault)
        if self._why == "count": self.pc = self.reg(UC_ARM_REG_PC) & ~1
        elif self._why in ("svc", "icsr"): self.pc = self.reg(UC_ARM_REG_PC) & ~1
        return self._why

    def _deliver(self):
        """wstrzykuje oczekujace wyjatki; zwraca True gdy cos weszlo"""
        if 11 in self.pend: self.pend.discard(11); self._enter(11, self.pc); return True
        if self.masked(): return False
        for e in sorted(self.pend):
            if e == 14 or e >= 16 or e == 15:
                self.pend.discard(e); self._enter(e, self.pc); return True
        return False

    def run(self, slices=100, until=None, hook=None):
        """slices * tick instrukcji, po kazdym slice SysTick; until(board)->bool przerywa; hook(board) po kazdym slice"""
        for sl in range(slices):
            budget = self.tick if self.counters["svc"] > 0 else self.boot_budget   # przed startem schedulera: duze porcje (petle opoznien)
            while budget > 0:
                why = self._burst(budget)
                budget = max(0, budget - 1) if why != "count" else 0
                if why == "svc": self.pend.add(11); budget = min(budget, self.tick)
                while self._deliver(): pass
                if why == "count": break
            if self.counters["svc"] > 0: self.pend.add(15)  # SysTick wlaczany dopiero przez start schedulera (svc)
            while self._deliver(): pass
            if hook: hook(self)
            if until and until(self): return True
        return True

if __name__ == "__main__":
    import collections
    b = Board(sys.argv[1], tick=int(sys.argv[3]) if len(sys.argv) > 3 else 2000)
    ok = b.run(slices=int(sys.argv[2]) if len(sys.argv) > 2 else 2000)
    print("ok" if ok else "BLAD", "licznik:", b.counters, "pc=0x%X" % b.pc)
    print("przelaczenia kontekstu:", len(b.switches), dict(collections.Counter(b.switches)))
    print("poczatek kolejnosci:", b.switches[:25])
