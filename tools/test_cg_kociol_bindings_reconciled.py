#!/usr/bin/env python3
import csv
p='analiza_archiwum/FW2213TK-2026-11-22/data/cg_kociol_bindings_reconciled.csv'; r=list(csv.DictReader(open(p)))
by={x['pid']:x for x in r}
assert by['0x22A1']['widget_addr']=='0x200162F8'
assert 'frames 138' in by['0x2277']['bitmap_or_effect']
assert by['0x370A']['widget_addr']=='0x20016894'
print('PASS 98 corrected test: OK')
