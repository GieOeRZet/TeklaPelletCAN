from tools.pointer_flow_scan import scan

BIN="/mnt/data/FW2213TK_kopia.bin"

def test_menu_pointer_flows():
    r=scan(BIN,[0x20005EF0,0x20005F08])
    assert len(r["targets"])==3
    a=[x for x in r["targets"] if x["target_true"]==0x20005EF0]
    b=[x for x in r["targets"] if x["target_true"]==0x20005F08]
    assert {(x["literal_load_raw"],x["loaded_register"]) for x in a}=={(0x3C068,"r0"),(0x3C17A,"r2")}
    assert [(x["literal_load_raw"],x["loaded_register"]) for x in b]==[(0x422CE,"r5")]
    assert any(x["kind"]=="store" for x in a[0]["accesses"])
    assert any(x["kind"]=="store" for x in a[1]["accesses"])
    assert any(x["kind"]=="load" for x in b[0]["accesses"])

if __name__=="__main__":
    test_menu_pointer_flows()
