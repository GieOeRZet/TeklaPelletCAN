import csv,sys
r=list(csv.DictReader(open(sys.argv[1] if len(sys.argv)>1 else "analiza_archiwum/FW2213TK-2026-11-22/data/cg_alarm_asymmetry_audit.csv",encoding="utf-8"))
m={int(x["alarm_code"]):x for x in r}
assert m[7]["status"]=="clear-only"
assert m[131]["status"]=="raise-only"
assert m[140]["raise_sites"]=="3"
assert m[250]["status"]=="clear-only"
print("PASS: alarm asymmetry audit")
