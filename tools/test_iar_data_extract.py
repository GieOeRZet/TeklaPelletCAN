import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BIN=Path("/mnt/data/FW2213TK_kopia.bin")
def test_iar_data_extract():
    if not BIN.exists(): return
    p=subprocess.run([sys.executable,str(ROOT/"tools/iar_data_extract.py"),str(BIN)],check=True,capture_output=True,text=True)
    d=json.loads(p.stdout)
    assert d["decompressed"]["size"]==0x118B3
    assert d["runtime_tables"]["class_0x20005EF0"]["bytes"]==[0,10,1,2,3,4,5,6,7,8,9,11,13,17,15,0,90,97,100,98,95]
    assert d["runtime_tables"]["access_0x20005F08"]["bytes"]==d["runtime_tables"]["class_0x20005EF0"]["bytes"]
    assert d["runtime_tables"]["class_0x20005EF0"]["matches_root_selector"] is True
if __name__=="__main__": test_iar_data_extract(); print("ok")
