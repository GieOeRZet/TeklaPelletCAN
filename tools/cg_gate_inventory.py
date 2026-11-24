#!/usr/bin/env python3
"""Static inventory of unresolved access-gate wrappers from repository CSV evidence."""
from __future__ import annotations
import argparse,csv
from pathlib import Path
UNRESOLVED = {'0x08054AB8':'level>=1 gate; screen/context unresolved','0x0805A9EC':'level>=3 gate; ctx12A=2 unresolved','0x0805B1D4':'level>=3 gate; ctx12A=4 unresolved','0x0805F400':'level>=3 gate; ctx12A=5 unresolved','0x0805FE9C':'level>=3 gate; context unresolved'}
KNOWN = {'0x0806125C':'level>=3 header gate; fuel store (ctx12A=2,12B=9)','0x08061518':'level>=3 header gate; cascade (ctx12A=2,12B=8)'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('csv');ap.add_argument('--out');a=ap.parse_args()
 rows=list(csv.DictReader(open(a.csv,encoding='utf-8',newline='')))
 lines=['# cg_gate_inventory','','| Gate | Evidence | Status |','|---|---|---|']
 for addr,meaning in {**UNRESOLVED,**KNOWN}.items():
  hits=[r for r in rows if addr.lower() in str(r).lower()]
  status='FACT' if addr in KNOWN else 'OPEN'
  lines.append('| '+addr+' | '+meaning+'; CSV hits='+str(len(hits))+' | '+status+' |')
 text='\n'.join(lines)+'\n'
 if a.out: Path(a.out).write_text(text,encoding='utf-8')
 else: print(text,end='')
if __name__=='__main__': main()
