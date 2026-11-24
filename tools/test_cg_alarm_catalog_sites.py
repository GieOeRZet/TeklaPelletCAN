#!/usr/bin/env python3
import csv
p='analiza_archiwum/FW2213TK-2026-11-22/data/cg_alarm_catalog_sites.csv'; r=list(csv.DictReader(open(p))); assert len(r)==31
codes=[int(x['code']) for x in r]; assert codes==[1,2,3,4,5,6,7,30,31,32,36,40,41,42,43,50,51,52,53,110,115,123,131,139,140,150,151,160,161,201,203,250]
print('PASS 100 test: OK')
