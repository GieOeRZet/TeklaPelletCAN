import struct
from pathlib import Path
from re_scan import scan,true_to_project
def test_literal(tmp_path):
    p=tmp_path/"x.bin"; p.write_bytes(b"\x00\xbf"*8+struct.pack("<I",0x08010FCE))
    r=scan(p,[0x08010FCE])
    assert r["target_summary"][0]["literal_count"]==1
    assert r["target_summary"][0]["direct_call_count"]==0
def test_project():
    assert true_to_project(0x080A4544)==0x08094544