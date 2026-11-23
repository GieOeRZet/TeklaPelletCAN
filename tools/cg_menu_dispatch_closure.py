#!/usr/bin/env python3
"""PASS 96: deterministic menu-row -> runtime-class -> first-level handler audit.
Source-of-truth inputs are the recovered PASS 28/39/41 dispatch facts; this tool emits the closure CSV.
"""
import csv, pathlib
OUT=pathlib.Path(__file__).resolve().parents[1]/"analiza/FW2213TK-2026-11-22/data/cg_menu_dispatch_closure.csv"
ROWS=[
(11,11,"Historia alarmów","0x080384B0"),(12,13,"Informacje o programie","0x0803850C"),(13,17,"Konfiguracja","0x0803850C"),(14,15,"Poziom menu PIN","0x08042318"),(15,12,"Język","0x080373BA/0x080373E6"),(16,14,"no-op","return"),(17,18,"service/level-gated class","0x08038574"),(18,16,"service/level-gated class","0x0803856C"),(19,19,"service/level-gated class","0x08038638"),(20,20,"service/level-gated class","0x080382EE")]
with OUT.open("w",newline="") as f:
 w=csv.writer(f); w.writerow(["row","class","semantic","first_level_handler","confidence","source"])
 for row,cls,sem,h in ROWS: w.writerow([row,cls,sem,h,"HARD","PASS28+PASS39+PASS41"])
print(OUT)
