#!/usr/bin/env python3
"""PASS 97: alarm manager closure audit."""
import csv,pathlib
OUT=pathlib.Path(__file__).resolve().parents[1]/'analiza/FW2213TK-2026-11-22/data/cg_alarm_closure.csv'
rows=[('raise','manager raises code with active+unack bits','0x08025198 -> ring 0x20021E90 + index +0xFC','HARD'),('is_unacknowledged','bit17 test','0x08025134','HARD'),('is_active','bit16 test','0x0802516C','HARD'),('clear','clear-by-code helper','0x08025104','HARD'),('acknowledge','CAN write clears bit17 and writes confirmation timestamp','0x4010+i bit17 + 0x4038+i timestamp','HARD'),('reset_memory','local command register','0x404E / 0x20021F94','STRONG')]
with OUT.open('w',newline='') as f:
 w=csv.writer(f); w.writerow(['alarm_action','evidence','exact_path_or_register','confidence']); w.writerows(rows)
print(OUT)
