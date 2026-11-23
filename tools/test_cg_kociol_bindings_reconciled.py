#!/usr/bin/env python3
import csv
p='analiza/FW2213TK-2026-11-22/data/cg_kociol_bindings_reconciled.csv'
r=list(csv.DictReader(open(p))); assert len(r)==5
assert r[0]['pid']=='0x370A' and r[0]['widget_addr']=='0x20016894'
assert r[1]['pid']=='0x350D' and r[1]['widget_addr']=='0x20016A94'
assert r[2]['pid']=='0x350A' and r[2]['widget_addr']=='0x20016A24'
assert r[3]['pid']=='0x2005' and r[3]['widget_addr']=='0x20016918'
print('PASS 98 test: OK')
