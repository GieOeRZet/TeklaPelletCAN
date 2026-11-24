#!/usr/bin/env python3
"""PASS 67: symulator ZRODEL LIVE: modul CAN IO wysyla ramki PDO (0x280/0x380/0x480 + node: 4 x u16 kanalow analogowych; 0x180 + node: PDO1), a panel przelicza surowy odczyt (12-bit ADC)
na temperature wg krzywej NTC. Mapowanie kanal->PID zmierzone przy domyslnej konfiguracji (data/ui_model/live_sources.json).
    sim = LiveSim(session); sim.set(0x2001, 65.0); sim.run(300)     # temperatury w stopniach C
Ramki musza isc POJEDYNCZO z odstepem (~12 tikow): odbiornik CAN przyjmuje jedna naraz. Wartosci uspredniane (filtr 8 probek), wiec potrzeba >= 8 rund."""
import json, os, bisect
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analiza", "FW2213TK-2026-11-22", "data", "ui_model")
class LiveSim:
    def __init__(self, session, src=None):
        self.s = session; self.src = json.load(open(src or os.path.join(D, "live_sources.json")))
        self.curve = sorted((int(k), (v - 65536 if v > 32767 else v)) for k, v in self.src["ntc_curve"]["points_raw_to_dC"].items())      # raw -> dC (malejaca)
        self.raw = {n: [1000] * 12 for n in (0x56, 0x45, 0x40, 0x46, 0x78, 0x50)}
        self.where = {}
        for node, m in self.src["modules"].items():
            for slot, info in m.get("slots", {}).items():
                for pid in info["pids_primary"]: self.where[int(pid, 16)] = (int(node, 16), int(slot))
    def temp_to_raw(self, dC):
        xs = [v for _, v in self.curve]; rs = [r for r, _ in self.curve]; best = min(range(len(xs)), key=lambda i: abs(xs[i] - dC))
        if best > 0 and best < len(xs) - 1:
            for a, b in ((best - 1, best), (best, best + 1)):
                if (xs[a] - dC) * (xs[b] - dC) <= 0 and xs[a] != xs[b]: return int(rs[a] + (rs[b] - rs[a]) * (xs[a] - dC) / (xs[a] - xs[b]))
        return rs[best]
    def set(self, pid, celsius):
        node, slot = self.where[pid]; self.raw[node][slot] = self.temp_to_raw(int(round(celsius * 10)))
    def round_(self, nodes=(0x56, 0x45)):
        for node in nodes:
            for j, base in enumerate((0x280, 0x380, 0x480)):
                self.s.can(base + node, b"".join(v.to_bytes(2, "little") for v in self.raw[node][4 * j:4 * j + 4])); self.s.wait(12)
            self.s.can(0x180 + node, bytes([1, 0, 0, 0, 0, 0, 0, 0])); self.s.wait(12)
    def run(self, ticks, nodes=(0x56, 0x45)):
        per = 12 * 4 * len(nodes); n = max(8, ticks // per)
        for _ in range(n): self.round_(nodes)
