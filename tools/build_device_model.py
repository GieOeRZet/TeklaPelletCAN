#!/usr/bin/env python3
"""Buduje JEDEN pakiet 'model urzadzenia' dla ESP / integracji HA / karty / Androida / WWW z calej wiedzy ui_model (bez nowych pomiarow):
PID-y (655) z nazwami, typami, zakresami, trybem; menu i reguly widocznosci (konfiguracja, poziom PIN); listy nastaw (etykiety PL, rodzaj dialogu, krok, opcje enum);
rejestry KONFIGURACJI kotla (z nich ESP wykrywa, jakie widoki udostepnic); alarmy (kody, teksty z binarki w 8 jezykach, rejestry); statusy; moduly sieci; zrodla live; PROGRAM.
Kazda sekcja ma `evidence` ze zrodla. Wyjscie: ui_model/device_model.json. Uzycie: python3 tools/build_device_model.py"""
import csv, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
U = paths.UI_MODEL
J = lambda n: json.load(open(U / (n + ".json"), encoding="utf-8")) if (U / (n + ".json")).exists() else None
N = lambda v: "0x%04X" % int(str(v), 16)
mt, lists, scales, labels, enums, dialogs = J("menu_tree"), J("lists"), J("list_scales"), J("list_labels_pl"), J("enum_labels"), J("list_dialogs")
vendor, live, prog, outs, home, rules = J("vendor_sdo_scada"), J("live_sources"), J("program_screen"), J("outputs_test"), J("home_config"), J("menu_rules_check")
alv = J("alarm_codes_verified")
pm = {N(r["pid"]): r for r in csv.DictReader(open(paths.DATA / "pid_matrix_655.csv", encoding="utf-8-sig"))}
tt = {r["id_relative"]: r for r in csv.DictReader(open(paths.DATA / "texts_all_languages.csv", encoding="utf-8"))}
sc_by_pid = {}
for key, lst in scales["lists"].items():
    for r in lst["rows"]:
        if r.get("pid"): sc_by_pid[N(r["pid"])] = {k: r.get(k) for k in ("scale", "decimals", "display", "leading_space")}
pids = {}
for p, r in pm.items():
    pids[p] = dict(name_en=r["name"], type=r["type"], min=int(r["min"] or 0) if r["min"].lstrip("-").isdigit() else None, max=int(r["max"]) if r["max"].lstrip("-").isdigit() else None,
                   default=r["default"], mode=r["mode"], checked_write=r["checked_write"] == "1", synced=r["synced"] == "1", format=sc_by_pid.get(p))
cfg_regs = {}
for row in mt["menu_rows"]:
    for c in row.get("config_cond", []): cfg_regs.setdefault(N(c["pid"]), set()).add(row["title_pl"])
list_out = {}; rows_total = 0
for key, rows in lists["lists"].items():
    k = key.split("|")[0]; lab = labels["lists"].get(k, {}).get("rows", {}); dl = (dialogs["lists"].get(k) or {}); out = []
    for r in rows:
        i = str(r["idx"]); d = dl.get(i, {}); e = (enums["lists"].get(k) or {}).get(i)
        entry = dict(idx=r["idx"], pid=r.get("pid") and N(r["pid"]), label_pl=(lab.get(i) or {}).get("label_pl"), label_en=r.get("name_en"), level_min=r.get("level_min"), kind=r.get("kind"), min=r.get("raw_min"), max=r.get("raw_max"), default=r.get("raw_default"),
                     dialog=d.get("kind"), step=1 if d.get("kind") == "slider" else None, step_evidence=("MEASURED" if d.get("kind") == "slider" and "note" not in d else "INFERENCE" if d.get("kind") == "slider" else None))
        if e: entry["options"] = {v: o["text"] for v, o in e["options"].items()}
        if d.get("kind") == "radio" and "options" not in entry: entry["options_dialog"] = d.get("texts")
        out.append(entry); rows_total += 1
    list_out[key] = out
kon = [r for r in list_out.get("0x10|KONFIGURACJA|inst1", [])]
for r in kon:
    if r["pid"]: cfg_regs.setdefault(r["pid"], set()).add("Konfiguracja: " + str(r["label_pl"]))
model = {"schema_version": "1.0", "firmware_sha256": mt["meta"].get("firmware_sha256"), "evidence": "STRONG (zbior z ui_model; kazda sekcja ma wlasny evidence i zrodlo)",
         "pids": {"evidence": "FACT-STATIC (tablica parametrow panelu: runtime_param_table/pid_matrix_655)", "count": len(pids), "items": pids},
         "configuration": {"evidence": "MEASURED (menu_rules_check 36/36, home_config 40 kombinacji, screens_config 11)", "note": "Konfiguracje ESP wykrywa czytajac te rejestry ze sterownika; od nich zaleza widoki (wiersze menu, kafle HOME, schematy ekranow).",
                           "registers": {p: sorted(v) for p, v in sorted(cfg_regs.items())}, "home_rules": home["rules"], "menu_rows": [{k: r.get(k) for k in ("row", "title_pl", "target", "level_min", "config_cond", "embedded_control")} for r in mt["menu_rows"]], "menu_rules_check": rules["summary"]},
         "screens": {"evidence": mt["evidence"], "nodes": mt["nodes"], "edges": [{k: e.get(k) for k in ("from", "to", "level_min", "effect")} for e in mt["edges"]]},
         "lists": {"evidence": "MEASURED (etykiety PL z RAM, dialogi z emulatora; krok 1 raw zmierzony dla 76 suwakow, reszta INFERENCE)", "rows": rows_total, "items": list_out},
         "statuses": vendor and {"evidence": vendor["evidence"], "burner_state_codes": vendor["burner_state_codes"], "boiler_work_mode_codes": vendor["boiler_work_mode_codes"]},
         "alarms": {"evidence": (alv or {}).get("evidence", "STRONG (vendor_sdo_scada)"), "ring": vendor and vendor["alarms"]["registers"], "register_bits": vendor and vendor["alarms"]["alarm_register_bits"], "codes": (alv or {}).get("codes") or (vendor and vendor["alarms"]["codes"])},
         "modules": {"evidence": live["evidence"] if isinstance(live.get("evidence"), str) else "MEASURED", "transport": live["transport"], "items": live["modules"]},
         "program": {"evidence": prog["evidence"], "encoding": prog["encoding"]}, "outputs_test": {"evidence": outs["evidence"], "rows": outs["rows"]}}
out = paths.UI_MODEL / "device_model.json"; out.write_text(json.dumps(model, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"); print("OK", out.stat().st_size // 1024, "KB; PID:", len(pids), "wierszy list:", rows_total, "rejestry konfiguracji:", len(cfg_regs))
