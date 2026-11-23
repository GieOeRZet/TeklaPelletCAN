#!/usr/bin/env python3
import csv
p='analiza/FW2213TK-2026-11-22/data/cg_dual_menu_callbacks.csv'; r=list(csv.DictReader(open(p))); assert len(r)==2
assert r[0]['dispatch_target'].startswith('FUN_0803C064')
assert r[1]['dispatch_target'].startswith('FUN_0803EC18')
print('PASS 99 test: OK')
