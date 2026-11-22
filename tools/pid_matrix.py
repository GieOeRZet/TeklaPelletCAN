#!/usr/bin/env python3
"""NewEstyma: macierz PID (klucz runtime) -> storage/typ/zakres/dostep/sync/UI.  Wejscie: runtime_param_table_655.csv + resolver_t1/t2.csv.
python3 -I tools/pid_matrix.py DATA_DIR out.csv
Klasa (+0x24) = tryb dostepu (HARD: 448/448 zgodna z kolumna access katalogu panelu; PASS 5: 08011812 z kontrola pozwala tylko 1,3; sync 08011368 tylko 2,3):
 0 live (odczyt, bez sync)   1 komenda (zapis z kontrola, bez sync)   2 lustro z centrali (sync, bez zapisu z kontrola)   3 nastawa (zapis z kontrola + sync)."""
import csv, os, sys
d = sys.argv[1]
rt = list(csv.DictReader(open(os.path.join(d, "runtime_param_table_655.csv"))))
t1 = list(csv.DictReader(open(os.path.join(d, "resolver_t1.csv")))); t2 = list(csv.DictReader(open(os.path.join(d, "resolver_t2.csv"))))
MODE = {"0": "live", "1": "command", "2": "mirror", "3": "setting"}
ui = {}
for r in t2: ui.setdefault(int(r["value"], 16), []).append(("T2", r["ui_key"], 0))
for r in t1:
    b = int(r["value"], 16)
    for inst in (1, 2, 3, 4): ui.setdefault(b + inst - 1, []).append(("T1", r["ui_key"], inst))
rows = []
for r in rt:
    k = int(r["key"], 16); u = ui.get(k, [])
    rows.append(dict(pid=r["key"], name=r["name"], type=r["type_name"], min=r["min"], max=r["max"], default=r["default"],
                     storage=r["storage"], cfg_off=r["cfg_off"], cls=r["cls"], mode=MODE.get(r["cls"], "?"),
                     checked_write=int(r["cls"] in ("1", "3")), synced=int(r["cls"] in ("2", "3")),
                     ui_keys=";".join("%s:%s%s" % (t, kk, ("/inst%d" % i) if i else "") for t, kk, i in u)))
rows.sort(key=lambda x: int(x["pid"], 16))
with open(sys.argv[2], "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
import collections
print("PID:", len(rows), "tryby:", dict(collections.Counter(x["mode"] for x in rows)), "z kluczem UI:", sum(1 for x in rows if x["ui_keys"]))
