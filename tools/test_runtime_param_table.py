#!/usr/bin/env python3
"""Test regresyjny (wymaga kanonicznego BIN): python3 -I tools/test_runtime_param_table.py FW2213TK_kopia.bin"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import runtime_param_table as T
rows = T.table(sys.argv[1]); by = {r["key"]: r for r in rows}
assert len(rows) == 655 and len({r["key"] for r in rows}) == 655
r3 = by[3]; assert (r3["name"], r3["storage"], r3["type_name"], r3["min"], r3["max"], r3["default"]) == ("Language", 0x20021FAA, "u8", 0, 30, 0)
assert r3["cfg_off"] == 0x16BE and by[4]["cfg_off"] == 0x16CE and by[0x2105]["cfg_off"] == 0x16C3
assert by[0x2016]["min"] == -100 and by[0x2016]["max"] == 1500           # s16 + maskowanie typem
assert by[0x200D]["max"] == 255                                          # max 0x5FF z typem 1 -> u8
assert by[0x3506]["name"] == "Sound alarm activation" and by[0x300B]["name"] == "Stop burning wood"
assert sum(1 for r in rows if r["storage"] >= 0x40000000) == 15          # BKPSRAM
print("OK: runtime_param_table")
