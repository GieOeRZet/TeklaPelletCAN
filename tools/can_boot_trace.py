#!/usr/bin/env python3
"""NewEstyma PASS 43: ruch CAN, ktory firmware panelu nadaje po starcie przy PUSTEJ magistrali (bez zadnych partnerow).
python3 -I tools/can_boot_trace.py FW2213TK_kopia.bin out.csv [--ticks 6000] [--inject id:hexdata@tick ...]
Pelny emulator systemowy (Board + DMA2D + CAN2). Tick = 100000 instrukcji (~1 ms). Pierwsze ramki pojawiaja sie ok. ticku 3300 (scheduler obiektow okresowych 0x080247C8: licznik poczatkowy 30 x ~100 ms).
--inject wstrzykuje ramke RX (np. 701:05@3500). Wyjscie: CSV tick,can_id,dlc,data_hex."""
import argparse, csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cortexm_rtos as C
LTDC = 0x40016800
def run(binpath, ticks=6000, injects=()):
    b = C.Board(binpath, tick=100000); b.enable_dma2d(); can = b.enable_can2()
    pend = sorted(injects)
    def hook(bd, *a):
        if bd.counters["svc"] == 0: return
        hook.n = getattr(hook, "n", 0) + 1
        if hook.n >= 100 and hook.n % 10 == 0: bd.wr(LTDC + 0x38, 1); bd.raise_irq(88)
        while pend and pend[0][0] <= hook.n: _, i, d = pend.pop(0); can.inject(i, d)
    b.run(slices=ticks, hook=hook)
    return b, can
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("bin"); ap.add_argument("out"); ap.add_argument("--ticks", type=int, default=6000); ap.add_argument("--inject", action="append", default=[])
    a = ap.parse_args(); inj = []
    for s in a.inject: left, t = s.split("@"); i, d = left.split(":"); inj.append((int(t), int(i, 16), bytes.fromhex(d)))
    b, can = run(a.bin, a.ticks, inj)
    with open(a.out, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["tick", "can_id", "dlc", "data_hex"])
        for fr in can.tx: w.writerow([fr["tick"], "0x%03X" % fr["id"], fr["dlc"], fr["data"].hex(" ")])
    print(len(can.tx), "ramek TX")
