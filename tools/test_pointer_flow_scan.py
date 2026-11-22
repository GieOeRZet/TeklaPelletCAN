from tools.pointer_flow_scan import scan

BIN="/mnt/data/FW2213TK_kopia.bin"

def test_menu_pointer_flows():
    r=scan(BIN,[0x20005EF0,0x20005F08])
    assert len(r["targets"])==3
    a=[x for x in r["targets"] if x["target_true"]==0x20005EF0]
    b=[x for x in r["targets"] if x["target_true"]==0x20005F08]
    assert {(x["literal_load_raw"],x["loaded_register"]) for x in a}=={(0x3C068,"r0"),(0x3C17A,"r2")}
    assert [(x["literal_load_raw"],x["loaded_register"]) for x in b]==[(0x422CE,"r5")]
    # PASS 23 false positive: 0x3C1FC is a 32-bit MOV.W, so 0x3C1FE
    # is its second halfword and must never be decoded as STRB.
    assert not any(x["at_raw"]==0x3C1FE and x["kind"]=="store" for y in a for x in y["accesses"])
    # Real Thumb-2 MOVW instructions in the same function are recognized.
    assert any(x["at_raw"]==0x3C18C and x["mnemonic"]=="MOVW" and x["imm16"]==0x111 for y in a for x in y["wide_instructions"])
    assert any(x["kind"]=="load" and x["at_raw"]==0x422DE for x in b[0]["accesses"])

if __name__=="__main__":
    test_menu_pointer_flows()
