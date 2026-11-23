from pathlib import Path
import importlib.util, struct
spec=importlib.util.spec_from_file_location('m',Path(__file__).with_name('cg_timestamp_producer_scan.py'))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def test_constants():
    assert m.PID==0x2165
    assert m.STORAGE==0x20008D28
    assert m.BASE==0x08000000

def test_synthetic(tmp_path):
    p=tmp_path/'x.bin'; b=bytearray(32)
    b[4:6]=struct.pack('<H',0x2165)
    b[12:16]=struct.pack('<I',0x20008D28)
    p.write_bytes(b); r=m.scan(p)
    assert r['pid_2165_le16_project_hits']==['0x8000004']
    assert r['storage_literal_project_hits']==['0x8000000c']