#!/usr/bin/env python3
"""PASS 108: source-grounded dual callback closure."""
import csv,sys
src=sys.argv[1]; out=sys.argv[2]
with open(src,encoding="utf-8") as f: rows=list(csv.DictReader(f))
with open(out,"w",newline="",encoding="utf-8") as f:
 w=csv.writer(f); w.writerow(["handler","base_offset","stride","count_offset","dispatch","target","confidence","source"])
 for x in rows: w.writerow([x["handler"],x["base_offset"],x["stride"],x["count_offset"],x["dispatch"],x["target"],x["confidence"],x["source"]])
