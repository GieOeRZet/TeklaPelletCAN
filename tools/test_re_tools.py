import struct, json
from pathlib import Path
from vtable_scan import scan
from runtime_trace_analyzer import analyze

def test_vtable_candidate(tmp_path):
    p=tmp_path/"x.bin"
    p.write_bytes(struct.pack("<IIII",0x08020001,0x08020011,0x08020021,0))
    r=scan(p,min_slots=2,max_slots=8)
    assert r["vtable_candidates"][0]["slots"] == 3

def test_runtime_indirect_edge():
    r=analyze([
        {"kind":"indirect_call","pc":0x08010FCE,"target":0x08011368,"object_address":0x20010000,"offset":0x7178},
        {"kind":"return","pc":0x08011368},
    ], focus=[0x08010FCE,0x08011368])
    assert r["indirect_edges"][0]["count"] == 1
    assert r["object_paths"][0]["offset"] == 0x7178
