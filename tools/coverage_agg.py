#!/usr/bin/env python3
"""E3: agregacja wynikow coverage_gen.py (OUTROOT/L*_*/result.json) -> ui_model/coverage_matrix_agent.json + .md (tabela pokrycia i %).
Uzycie: python3 tools/coverage_agg.py OUTROOT"""
import glob, json, os, sys, collections, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
root = sys.argv[1] if len(sys.argv) > 1 else "/tmp/w/cov"
cells = []; jobs = []
for f in sorted(glob.glob(os.path.join(root, "L*_*", "result.json"))):
    r = json.load(open(f)); jobs.append(dict(level=r["level"], config=r["config"], pids=r["pids"], rows_expected=r["rows_expected"], rows_actual=r["rows_actual"], rows_match=r["rows_match"]))
    for c in r["cells"]: cells.append(dict(level=r["level"], config=r["config"], **c))
for c in cells:
    if c["node"] == "ALARMY" and c["level"] == 0: c["artifact"] = "artefakt emulatora (zawiniecie ramki); real = normalny uklad wg zdjecia wlasciciela"
meas = [c for c in cells if "pct_diff" in c and not c.get("artifact")]; notvis = [c for c in cells if str(c.get("status", "")).startswith("NOT_VISIBLE")]; bad = [c for c in cells if "error" in c or c.get("status") == "TAP_FAILED"]; bad = [c for c in cells if "error" in c or c.get("status") == "TAP_FAILED"]
def share(th): return round(100 * sum(c["pct_diff"] < th for c in meas) / max(1, len(meas)), 1)
summ = dict(jobs=len(jobs), cells_measured=len(meas), not_visible_in_emulator=len(notvis), errors=len(bad), median_pct=statistics.median(c["pct_diff"] for c in meas) if meas else None,
            share_lt3=share(3), share_lt8=share(8), jobs_rows_mismatch=[(j["level"], j["config"], j["rows_expected"], j["rows_actual"]) for j in jobs if not j["rows_match"]])
out = dict(schema_version="1.0", evidence="MEASURED (emulator, render z danych vs zrzut; mapowanie konfiguracja->PID = INFERENCE, patrz tools/coverage_gen.py)", method="tools/coverage_gen.py + run_coverage_par.sh (poziomy 0,1,3; L2 pominiety - zalozenie L1=L2, do weryfikacji)", summary=summ, jobs=jobs, cells=cells)
json.dump(out, open(paths.UI_MODEL / "coverage_matrix_agent.json", "w"), ensure_ascii=False, indent=1)
by = collections.defaultdict(list)
for c in meas: by[(c["node"], c["kind"])].append(c["pct_diff"])
md = ["# Pokrycie wizualne (agent UI, E3)", "", "Zmierzone komorki: %d, niewidoczne w emulatorze mimo visible_in: %d, bledy: %d; mediana %.1f%%; <3%%: %s%%; <8%%: %s%%." % (len(meas), len(notvis), len(bad), summ["median_pct"] or 0, summ["share_lt3"], summ["share_lt8"]), "", "| wezel | rodzaj | n | min | mediana | max |", "|---|---|---|---|---|---|"]
for (n, k), v in sorted(by.items(), key=lambda x: -max(x[1])): md.append("| %s | %s | %d | %.1f | %.1f | %.1f |" % (n, k, len(v), min(v), statistics.median(v), max(v)))
(paths.UI_MODEL / "coverage_matrix_agent.md").write_text("\n".join(md) + "\n", encoding="utf-8"); print(json.dumps({k: v for k, v in summ.items() if k != "jobs_rows_mismatch"}), "\n".join(md[4:20]))
