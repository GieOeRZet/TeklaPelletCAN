#!/usr/bin/env python3
"""PASS 55: triaz niewykonanych funkcji. Dla kazdej niewykonanej funkcji (cel BL, patrz coverage_report.py): rozmiar (do nastepnego celu BL), liczba wolajacych,
ilu wolajacych lezy w WYKONANEJ funkcji (=> galaz nieodwiedzona w zywym kodzie) a ilu w niewykonanej (martwy lancuch), literaly peryferiow w zakresie funkcji,
wyroznik: 'HAL/niewolane' (wszyscy wolajacy w niewykonanym kodzie).
python3 -I tools/coverage_triage.py FW.bin function_coverage.csv OUT.csv"""
import bisect, csv, struct, sys
B = 0x08010000
PER = {0x40011000: "USART1", 0x40004400: "USART2", 0x40004800: "USART3", 0x40004C00: "UART4", 0x40005000: "UART5", 0x40011400: "USART6", 0x40007800: "UART7", 0x40007C00: "UART8",
       0x40013000: "SPI1", 0x40003800: "SPI2", 0x40003C00: "SPI3", 0x40015000: "SPI5", 0x40012C00: "SDIO", 0x40012000: "ADC1", 0x40005400: "I2C1", 0x40005800: "I2C2", 0x40005C00: "I2C3",
       0x40006400: "CAN1", 0x40006800: "CAN2", 0x40002800: "RTC", 0x40016800: "LTDC", 0x40023800: "RCC", 0x40023C00: "FLASH", 0x40007000: "PWR", 0x40001000: "TIM6", 0x40001400: "TIM7",
       0x40000000: "TIM2", 0x40000400: "TIM3", 0x40000800: "TIM4", 0x40000C00: "TIM5", 0x40010000: "TIM1", 0x40026000: "DMA1", 0x40026400: "DMA2", 0x4002B000: "DMA2D", 0x40012C00: "ADC", 0x40020000: "GPIO",
       0xA0000000: "FMC", 0x50000000: "USB_OTG_FS", 0x40040000: "USB_OTG_HS", 0x40028000: "ETH", 0x40013800: "SYSCFG", 0x40003000: "IWDG", 0x40002C00: "WWDG", 0x40007400: "DAC"}
def main(fw, cov, out):
    raw = open(fw, "rb").read(); rows = list(csv.DictReader(open(cov)))
    funcs = sorted(int(r["func_runtime"], 16) for r in rows); ex = {int(r["func_runtime"], 16): r["executed"] == "1" for r in rows}
    def enclosing(a):
        i = bisect.bisect_right(funcs, a) - 1; return funcs[i] if i >= 0 else None
    # wolajacy: skan BL
    callers = {}
    for i in range(0, len(raw) - 3, 2):
        h1, h2 = struct.unpack_from("<HH", raw, i)
        if (h1 & 0xF800) != 0xF000 or (h2 & 0xD000) != 0xD000: continue
        s = (h1 >> 10) & 1; j1 = (h2 >> 13) & 1; j2 = (h2 >> 11) & 1; i1 = ~(j1 ^ s) & 1; i2 = ~(j2 ^ s) & 1
        imm = (s << 24) | (i1 << 23) | (i2 << 22) | ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
        if s: imm -= 1 << 25
        t = (B + i + 4 + imm) & ~1
        if t in ex: callers.setdefault(t, []).append(B + i)
    res = []
    for k, a in enumerate(funcs):
        if ex[a]: continue
        end = funcs[k + 1] if k + 1 < len(funcs) else a + 64; size = end - a
        cs = callers.get(a, []); ce = [enclosing(c) for c in cs]
        live = sum(1 for e in ce if e is not None and ex.get(e)); dead = len(ce) - live
        per = set()
        for off in range(a - B, min(end - B, len(raw)) - 3, 4):
            v = struct.unpack_from("<I", raw, off)[0]
            for base, n in PER.items():
                if base <= v < base + 0x400: per.add(n)
        res.append((a, size, len(cs), live, dead, ",".join(sorted(per))))
    with open(out, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["func", "size", "callers", "callers_in_executed_fn", "callers_in_unexecuted_fn", "peripherals"])
        for r in res: w.writerow(["0x%08X" % r[0]] + list(r[1:]))
    live = [r for r in res if r[3] > 0]; dead = [r for r in res if r[3] == 0]
    print("niewykonane:", len(res), "| z wolajacym w wykonanym kodzie (nieodwiedzona galaz):", len(live), "| tylko martwy lancuch:", len(dead))
    return res
if __name__ == "__main__": main(*sys.argv[1:4])
