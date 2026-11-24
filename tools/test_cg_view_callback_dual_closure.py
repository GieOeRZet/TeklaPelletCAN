import csv,sys
p=sys.argv[1] if len(sys.argv)>1 else "analiza_archiwum/FW2213TK-2026-11-22/data/cg_view_callback_dual_closure.csv"
r=list(csv.DictReader(open(p,encoding="utf-8")))
assert len(r)==2
m={x["handler"]:x for x in r}
assert m["0x0807EB00"]["target"]=="0x0803C064"
assert m["0x0807EB36"]["target"]=="0x0803EC18"
assert all(x["base_offset"]=="0x3B4" and x["stride"]=="0x274" and x["count_offset"]=="0x3B8" for x in r)
print("PASS: dual callback closure verified")
