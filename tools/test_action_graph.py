#!/usr/bin/env python3
from ui_model import bind
from action_graph import build

def main():
    presenters=[{"presenter_cluster":"0","cluster_start":"0x100","site":"0x101","ui_key":"0x10","pid":"0x2001","name":"T","setter":"0x300","formats":"","div10":"0","widget_offsets_i":[0x20]}]
    model={"items":bind([{"this":"0x20001000","view_off":0x20,"node":"1_screen","tap":"screen","role":"text"}],presenters)}
    actions=[
      {"widget":"0x20001000","handler":"0x0808EB00","effects":{"pid":"0x2001"}},
      {"node":"1_screen","tap":"screen","handler":"0x0808EB00","effects":{}},
      {"widget":"0x20009999","handler":"x","effects":{}},
    ]
    g=build(model,actions)
    assert g[0]["evidence"]=="EXACT_WIDGET" and g[0]["presenter_candidates"][0]["pid"]=="0x2001"
    assert g[1]["evidence"]=="EXACT_NODE_TAP"
    assert g[2]["evidence"]=="UNRESOLVED_ACTION_TARGET"
    print("PASS: action graph exact/node/unresolved")
if __name__=="__main__": main()
