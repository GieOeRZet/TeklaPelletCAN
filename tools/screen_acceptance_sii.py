#!/usr/bin/env python3
"""Acceptance harness for the original firmware screens SIEC/INFO/INTERNET.

This uses the real UiSession/Board firmware emulator, not a mock UI.
It is intentionally conservative: results are emitted as evidence, never
labelled FACT-DYNAMIC by this script unless the firmware actually produced
the observed change.

Usage:
  python3 -I tools/screen_acceptance_sii.py FW2213TK_kopia.bin OUTDIR

The firmware binary is deliberately not part of the repository.
"""

import hashlib, json, os, sys
from PIL import Image, ImageChops
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U

FW_SHA = "1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071"
SCREENS = {
    "INFO": 0x808f638,
    "SIEC": 0x808f770,
    "INTERNET": 0x808f9ac,
}

def diff(a, b, path):
    d = ImageChops.difference(a, b)
    box = d.getbbox()
    d.save(path)
    return box

def save_meta(out, name, meta):
    with open(os.path.join(out, name + ".json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

def boot(out, level=1):
    s = U.UiSession(sys.argv[1], out)
    s.boot(700)
    # Same full configuration/access preparation used by the established UI
    # explorer. This is a state setup, not a user write.
    for pid, val in ((0x2105,4),(0x2106,1),(0x2107,1),(0x2108,1)):
        s.set_local(pid, val)
    s.set_access(level)
    s.wait(300)
    return s

def menu_to_row(s, row):
    s.tap(34,235,settle=700)
    s.go_top()
    nav = U.ListNav(s)
    nav.build()
    ok = nav.tap_row_from_top(row, settle=800)
    if not ok:
        raise RuntimeError("cannot enter menu row %d" % row)
    s.wait(300)

def snapshot(s, out, label):
    return s.shot(label)

def info_suite(out):
    s = boot(out)
    menu_to_row(s, 12)
    base = snapshot(s,out,"info_baseline")
    tests = []
    for label,pid,val in (
        ("software_2_214",0x3664,0x0214),
        ("software_2_215",0x3664,0x0215),
        ("boiler_1",0x3665,0x00000001),
        ("pin_1",0x2170,1),
        ("pin_5678",0x2170,5678),
        ("pin_max",0x2170,65535),
    ):
        before = s.shot()
        s.inject_param(pid,val)
        s.wait(250)
        after = s.shot(label)
        tests.append({
            "label":label, "pid":hex(pid), "value":val,
            "body_changed": bool(diff(before,after,os.path.join(out,label+"_diff.png"))),
            "state":s.state(),
        })
    save_meta(out,"INFO_acceptance",{"screen":hex(SCREENS["INFO"]),"tests":tests})
    return tests

def internet_suite(out):
    s = boot(out)
    menu_to_row(s,20)
    base = snapshot(s,out,"internet_baseline")
    tests=[]
    # Direct PID/state tests first. Editor tests are intentionally separate:
    # they require observing the real dialog/vtable before any assumptions
    # about its keyboard implementation are made.
    for label,pid,val in (
        ("wifi_on",0x373E,1),
        ("wifi_off",0x373E,0),
        ("remote_on",0x3741,1),
        ("remote_off",0x3741,0),
        ("status_373d_2",0x373D,2),
        ("status_373d_0",0x373D,0),
    ):
        before=s.shot()
        s.inject_param(pid,val)
        s.wait(250)
        after=s.shot(label)
        tx_before=len(s.can2.tx)
        tests.append({
            "label":label,"pid":hex(pid),"value":val,
            "body_changed":bool(diff(before,after,os.path.join(out,label+"_diff.png"))),
            "state":s.state(),
            "tx_total":tx_before,
        })
    # SSID serialization probes: use 6 u32 chunks. "Home" is the known
    # big-endian-per-u32 representation 0x486f6d65.
    ssid=[0x486f6d65,0,0,0,0,0]
    for i,v in enumerate(ssid):
        s.inject_param(0x3730+i,v)
    s.wait(250)
    s.shot("internet_ssid_home")
    # Touch SSID once. The resulting vtable/body/bitmap/text trace is the
    # evidence used to identify the editor, rather than assuming DLG_TEKST.
    s.enable_trace()
    before=s.shot()
    s.tap(180,62,settle=1000)
    after=s.shot("internet_ssid_tap")
    tests.append({
        "label":"ssid_tap",
        "body_changed":bool(diff(before,after,os.path.join(out,"ssid_tap_diff.png"))),
        "trace":s.trace,
        "state":s.state(),
    })
    save_meta(out,"INTERNET_acceptance",{"screen":hex(SCREENS["INTERNET"]),"tests":tests})
    return tests

def siec_suite(out):
    s = boot(out)
    menu_to_row(s,19)
    base=s.shot("siec_empty")
    tests=[]
    # The harness first captures the empty state. Node-module injection is
    # deliberately done through the same CAN2 RX model as all other tests.
    # Heartbeat + 0x1018:02 identity are sent repeatedly to tolerate the
    # panel's polling phase.
    def node_tick(node, identity=(0x00000000,0x00000000)):
        # CANopen heartbeat: operational (0x05).
        s.can(0x700+node,[0x05])
        # SDO response to identity sub-index 2: 43 18 10 02 + vendor value.
        s.can(0x580+node,[0x43,0x18,0x10,0x02,
                          identity[0]&255,(identity[0]>>8)&255,
                          (identity[0]>>16)&255,(identity[0]>>24)&255])
    cases=[("node_56",0x56),("node_57",0x57),("node_40",0x40),("node_5b",0x5B),("unknown_0x22",0x22)]
    for label,node in cases:
        before=s.shot()
        for _ in range(4):
            node_tick(node)
            s.wait(120)
        after=s.shot(label)
        tests.append({
            "label":label,"node":hex(node),
            "body_changed":bool(diff(before,after,os.path.join(out,label+"_diff.png"))),
            "state":s.state(),
            "rx_count":len(s.can2.rx_log),
            "tx_tail":s.can2.tx[-30:],
        })
    save_meta(out,"SIEC_acceptance",{"screen":hex(SCREENS["SIEC"]),"tests":tests})
    return tests

def main():
    fw=sys.argv[1]
    out=sys.argv[2]
    os.makedirs(out,exist_ok=True)
    raw=open(fw,"rb").read()
    got=hashlib.sha256(raw).hexdigest()
    assert got==FW_SHA,(got,FW_SHA)
    results={}
    results["INFO"]=info_suite(os.path.join(out,"INFO"))
    results["INTERNET"]=internet_suite(os.path.join(out,"INTERNET"))
    results["SIEC"]=siec_suite(os.path.join(out,"SIEC"))
    save_meta(out,"RUN_SUMMARY",{"firmware_sha256":got,"screens":SCREENS,"results":results})
    print("ACCEPTANCE HARNESS COMPLETE")
    print("Dynamic evidence is in",out)
    print("No test result is inferred from this script itself.")

if __name__=="__main__":
    main()
