from tools.pointer_flow_scan import scan
BIN="/mnt/data/FW2213TK_kopia.bin"
def test_menu_pointer_flows():
    r=scan(BIN,[0x20005EF0,0x20005F08])
    assert len(r["targets"])>=3
    ts={x["target_true"] for x in r["targets"]}
    assert 0x20005EF0 in ts and 0x20005F08 in ts
    assert any(x["loaded_register"]=="r5" for x in r["targets"] if x["target_true"]==0x20005F08)
if __name__=="__main__": test_menu_pointer_flows()
