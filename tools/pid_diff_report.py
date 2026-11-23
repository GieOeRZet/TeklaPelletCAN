#!/usr/bin/env python3
"""PASS 63: tabela widget -> PID -> regula z wynikow pid_diff.py.  Uzycie: pid_diff_report.py OUT.md OUT.csv FW.bin res1.json [res2.json ...]"""
import csv, json, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pid_diff as P
B = 0x08010000
def main():
    out_md, out_csv, fw = sys.argv[1:4]; files = sys.argv[4:]
    raw = open(fw, "rb").read(); meta = P.pid_meta()
    def pl(i):
        try:
            o = struct.unpack_from("<I", raw, 0x5BD80 + 4 * i)[0] - B; r = []
            while True:
                c = struct.unpack_from("<H", raw, o)[0]
                if c == 0: break
                r.append(chr(c)); o += 2
            return "".join(r).replace("\x02", "#")
        except Exception: return "?"
    rows = []; md = ["# Wiazania widget -> PID (PID-diff, poziom dostepu 0)\n"]
    for f in files:
        R = json.load(open(f)); W = {w["this"]: w for w in R["widgets"]}; node = R["node"]
        md.append("\n## wezel %s — %d widgetow w inwentarzu, %d PID-ow ekranu\n" % (node, len(W), len(R["pids"])))
        md.append("| PID | nazwa | klasa | widget | pozycja | zasob statyczny | regula (wartosc -> stan) |\n|---|---|---|---|---|---|---|")
        live_noeffect = []
        for pid, d in R["pids"].items():
            if "runs" not in d: continue
            cls = meta[int(pid, 16)]["mode"]; dep = 0
            for t, w in W.items():
                if (w["ax"], w["ay"]) == (9, 239) and w["role"] == "image": continue          # animacja pompy (klatki 138-142 zmieniaja sie same)
                sts = [json.dumps(r["state"][t], sort_keys=True) for r in d["runs"]]
                if len(set(sts)) < 2: continue
                dep += 1
                rule = "; ".join("%s -> %s" % (r["value"], ("vis=%d" % r["state"][t]["vis"]) + (" bmp=%s" % r["state"][t]["bmp"] if "bmp" in r["state"][t] else "") + (" '%s'" % r["state"][t]["text"] if r["state"][t].get("text") is not None else "")
                                              + (" rect=%s" % r["state"][t]["rect"] if r["state"][t]["rect"] != d["runs"][0]["state"][t]["rect"] else "")) for r in d["runs"])
                stat = ("bitmapa %s" % w["bitmap_id"] if w.get("bitmap_id") is not None else "") + ("tekst '%s'" % (pl(w["text_id"] + 57) if w.get("text_id") is not None and w["text_id"] < 496 else "") if w["role"] == "text" else "")
                pos = "%d,%d %dx%d" % (w["ax"], w["ay"], w["w"], w["h"])
                md.append("| %s | %s | %s | %s | %s | %s | %s |" % (pid, d["name"], cls, t, pos, stat, rule))
                rows.append(dict(node=node, pid=pid, name=d["name"], cls=cls, widget=t, role=w["role"], pos=pos, static=stat, rule=rule))
            if dep == 0: live_noeffect.append("%s %s (%s)" % (pid, d["name"], cls))
        md.append("\nPID-y czytane na ekranie bez zmiany widgetow w tescie (live/zablokowane/zaleznosc warunkowa): " + ("; ".join(live_noeffect) or "brak") + "\n")
    open(out_md, "w", encoding="utf-8").write("\n".join(md))
    w = csv.DictWriter(open(out_csv, "w", newline="", encoding="utf-8"), fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(len(rows), "wiazan")
if __name__ == "__main__": main()
