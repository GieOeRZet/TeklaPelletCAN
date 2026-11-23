#!/usr/bin/env python3
"""Regression test for tools/ui_model.py using a tiny synthetic fixture."""
import csv, json, os, tempfile
from ui_model import load_presenters, load_widgets, bind, flat_rows

def main():
    with tempfile.TemporaryDirectory() as d:
        pc=os.path.join(d,"p.csv"); wc=os.path.join(d,"w.json")
        with open(pc,"w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=["presenter_cluster","cluster_start","site","ui_key","pid","name","setter","formats","div10","widget_offsets"])
            w.writeheader()
            w.writerow(dict(presenter_cluster="0",cluster_start="0x100",site="0x101",ui_key="0x10",pid="0x2001",name="Boiler temp",setter="0x300",formats="%d.%d",div10="1",widget_offsets="0x174|0x520"))
            w.writerow(dict(presenter_cluster="1",cluster_start="0x200",site="0x201",ui_key="0x11",pid="0x2005",name="Boiler on/off",setter="0x301",formats="",div10="0",widget_offsets="0x174"))
        json.dump([
            {"this":"0x20001000","view_off":0x520,"role":"text","text_id":12},
            {"this":"0x20001040","view_off":0x999,"role":"image","bitmap_id":7},
            {"this":"0x20001080","view_off":0x174,"role":"text","text_id":13},
        ],open(wc,"w",encoding="utf-8"))
        p=load_presenters(pc); w=load_widgets(wc); m=bind(w,p)
        assert m[0]["binding"]=="EXACT_VIEW_OFF" and m[0]["presenter_candidates"][0]["pid"]=="0x2001"
        assert m[1]["binding"]=="UNRESOLVED_VIEW_OFF"
        assert m[2]["binding"]=="AMBIGUOUS_VIEW_OFF" and len(m[2]["presenter_candidates"])==2
        assert len(flat_rows(m))==4
        # PASS 61: aktywny trace wezla rozstrzyga wieloznacznosc (setter 0x301 wykonany na widoku), 0x300 nie
        for x in w: x["node"]="n"
        act={"n":{"sites":{"0x201":[0x11]},"setters":{"0x301":["view"],"0x300":["0x20009999"]}}}
        m2=bind(w,p,act)
        assert m2[2]["binding"]=="EXACT_ACTIVE_VIEW_OFF" and m2[2]["presenter_candidates"][0]["pid"]=="0x2005"
        assert m2[0]["binding"]=="INACTIVE_VIEW_OFF" and m2[0]["binding_static"]=="EXACT_VIEW_OFF"
        assert m2[1]["binding"]=="UNRESOLVED_VIEW_OFF"
        assert bind(w,p,{})[0]["binding"]=="NO_ACTIVE_TRACE"
    print("PASS: ui_model synthetic exact/ambiguous/unresolved + active-trace cases")

if __name__=="__main__":
    main()
