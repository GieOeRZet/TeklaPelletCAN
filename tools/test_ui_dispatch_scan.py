from ui_dispatch_scan import scan

BIN="/mnt/data/FW2213TK_kopia.bin"

def test_tbb_graph():
    r=scan(BIN)
    rows=r["classes"]
    assert len(rows)==21
    assert [x["table_byte"] for x in rows]==[
        0x0B,0x11,0x15,0x19,0x1D,0x24,0x30,0x36,0x3C,0x42,
        0x2A,0x48,0x5A,0x7A,0x80,0x63,0x74,0x6E,0x68,0x4E,0x54
    ]
    by={x["class"]:x for x in rows}
    assert by[0]["handler_raw"]==0x38008
    assert by[1]["handler_raw"]==0x38130 and by[1]["trampoline_movs_r1"]==[1]
    assert by[2]["handler_raw"]==0x38130 and by[2]["trampoline_movs_r1"]==[2]
    assert by[3]["handler_raw"]==0x38130 and by[3]["trampoline_movs_r1"]==[3]
    assert by[4]["handler_raw"]==0x38130 and by[4]["trampoline_movs_r1"]==[4]
    assert by[5]["handler_raw"]==0x381E4
    assert by[6]["handler_raw"]==0x383B0
    assert by[7]["handler_raw"]==0x38278
    assert by[8]["handler_raw"]==0x382CA
    assert by[9]["handler_raw"]==0x382A6
    assert by[10]["handler_raw"]==0x3809C
    assert by[11]["handler_raw"]==0x384B0
    assert by[12]["kind"]=="inline_or_unresolved"
    assert by[13]["handler_raw"]==0x3850C
    assert by[14]["kind"]=="return"
    assert by[15]["handler_raw"]==0x42318
    assert by[16]["handler_raw"]==0x3856C
    assert by[17]["handler_raw"]==0x38568
    assert by[18]["handler_raw"]==0x38574
    assert by[19]["handler_raw"]==0x38638
    assert by[20]["handler_raw"]==0x382EE

if __name__=="__main__":
    test_tbb_graph()
