#!/usr/bin/env python3
"""python3 -I tools/test_can_boot_trace.py FW2213TK_kopia.bin — asercje na ruchu CAN panelu po starcie (pusta magistrala)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import can_boot_trace as T
b, can = T.run(sys.argv[1], ticks=6000)
tx = [(f["id"], f["data"].hex(" ")) for f in can.tx]
assert (0x704, "05") in tx                                                    # heartbeat wezla 4 (operational)
for n in (0x605, 0x606, 0x607):
    assert (n, "20 04 30 01 00 00 00 00") in tx and (n, "40 01 20 01 00 00 00 00") in tx   # zapis 0x3004:01 i odczyt 0x2001:01 do wezlow 5..7
assert not any(i == 0x604 for i, _ in tx)                                     # poller 0x604 nie pracuje bez wlaczenia przez UI
assert min(f["tick"] for f in can.tx) > 3000 and len(can.tx) > 80
print("OK: can_boot_trace (%d ramek, ID: %s)" % (len(can.tx), sorted({hex(i) for i, _ in tx})[:6]))
