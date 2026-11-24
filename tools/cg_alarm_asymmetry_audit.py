#!/usr/bin/env python3
import csv,sys,collections
src=sys.argv[1]; out=sys.argv[2]
rows=list(csv.DictReader(open(src,encoding="utf-8")))
d=collections.defaultdict(lambda:{"raise":0,"clear":0,"text":""})
for r in rows:
 if not r["alarm_code"]: continue
 c=int(r["alarm_code"]); d[c][r["kind"]]+=1; d[c]["text"]=r["text_pl"]
with open(out,"w",newline="",encoding="utf-8") as f:
 w=csv.writer(f);w.writerow(["alarm_code","raise_sites","clear_sites","status","text_pl"])
 for c in sorted(d):
  x=d[c]; status="paired" if x["raise"] and x["clear"] else ("raise-only" if x["raise"] else "clear-only")
  if c==0: status="unlabeled-generic"
  w.writerow([c,x["raise"],x["clear"],status,x["text"]])
