#!/usr/bin/env python3
import csv,sys
t1=list(csv.DictReader(open(sys.argv[1],encoding="utf-8")))
t2=list(csv.DictReader(open(sys.argv[2],encoding="utf-8")))
o=set(r["ui_key"] for r in t1)&set(r["ui_key"] for r in t2)
assert len(t1)==49 and len(t2)==372
assert not o, sorted(o)
assert all(r["rule"]=="PID=value+inst-1" for r in t1)
assert all(r["rule"]=="PID=value" for r in t2)
print("PASS: T1/T2 49+372, zero UI-key overlap")
