from pathlib import Path
import importlib.util, struct, tempfile
spec=importlib.util.spec_from_file_location("pis","tools/provider_interface_scan.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
def test_codeptr():
    assert m.codeptr(0x0801DB31)
    assert not m.codeptr(0x0801DB30)
def test_scan():
    d=bytearray(0x200); struct.pack_into("<I",d,0x40,0x0801DB31); struct.pack_into("<I",d,0x44,0x0801DB79)
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/"x.bin"; p.write_bytes(d); r=m.scan(p,0x08010040,8)
        assert r["words"][0]["code_pointer"] and r["words"][1]["code_pointer"]
