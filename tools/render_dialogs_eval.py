#!/usr/bin/env python3
"""Evaluate dialog renders. Never fabricate a score when data is missing."""
import argparse,csv,json,subprocess,sys
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"analiza"/"FW2213TK-2026-11-22"/"data"/"ui_model"
REFS={"paliwo":"dialog_shots/home_dlg_paliwo.png","zasilanie":"dialog_shots/home_dlg_zasilanie.png","auto":"dialog_shots/home_dlg_auto.png","czas":"dialog_shots/home_dlg_czas.png","data":"dialog_shots/home_dlg_data.png","number":"dialog_shots/edit_number_enum_sheet.png","enum":"dialog_shots/edit_number_enum_sheet.png","pin":"dialog_shots/pin_dialog_sheet.png","internet":"dialog_shots/home_control.png","program_day":"dialog_shots/program_day_dialog.png","program_copy":"dialog_shots/program_copy_sequence.png"}
def metric(a,b):
 x=np.asarray(a.convert("RGB")).astype(np.int16); y=np.asarray(b.convert("RGB")).astype(np.int16); d=np.abs(x-y).sum(axis=2)
 return float(d.mean()/3),float((d>40).mean()*100)
rows=[]
outdir=DATA/"render_dialogs_eval"; outdir.mkdir(parents=True,exist_ok=True)
for n,refname in REFS.items():
 out=outdir/(n+".png"); p=subprocess.run([sys.executable,str(ROOT/"tools"/"ui_render_dialogs.py"),n,str(out)],capture_output=True,text=True)
 try: missing=json.loads(p.stdout).get("missing",[])
 except Exception: missing=["renderer_failed:"+p.stderr[-300:]]
 ref=DATA/refname; status="OK"; mae=""; pct=""; reason=""
 if not ref.exists(): status="BRAK_DANYCH"; reason="brak zrzutu referencyjnego"
 elif missing: status="BRAK_DANYCH"; reason="; ".join(missing)
 else:
  try: mae,pct=metric(Image.open(out),Image.open(ref))
  except Exception as e: status="BRAK_DANYCH"; reason=str(e)
 rows.append({"dialog":n,"status":status,"mae":mae,"pct_diff":pct,"reference":refname,"missing":reason})
with (DATA/"render_dialogs_eval.csv").open("w",newline="",encoding="utf-8") as f:
 w=csv.DictWriter(f,fieldnames=rows[0]); w.writeheader(); w.writerows(rows)
md=["# Render dialogów — ocena","11 okien; BRAK_DANYCH oznacza brak danych potrzebnych do uczciwego pixel diff.","","| dialog | status | MAE | % diff >40 | brakujące dane |","|---|---|---:|---:|---|"]
md += ["| %s | %s | %s | %s | %s |"%(r["dialog"],r["status"],r["mae"],r["pct_diff"],r["missing"]) for r in rows]
(DATA/"render_dialogs_eval.md").write_text("\n".join(md)+"\n",encoding="utf-8")
print(json.dumps({"dialogs":len(rows),"ok":sum(r["status"]=="OK" for r in rows),"brak_danych":sum(r["status"]=="BRAK_DANYCH" for r in rows)},ensure_ascii=False))
