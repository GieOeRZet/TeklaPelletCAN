from pathlib import Path
import importlib.util
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("cg_rtc_vtable_scan",HERE/"cg_rtc_vtable_scan.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def test_constants():
    assert m.PROJECT_BASE==0x08000000
    assert m.RUNTIME_BASE==0x08010000
    assert m.VTABLE_PROJECT==0x0809446C
    assert m.AUTOSYNC_PROJECT==0x08062638

def test_scan_with_synthetic_image(tmp_path):
    import struct
    p=tmp_path/"x.bin"
    b=bytearray(0x95000)
    struct.pack_into("<I",b,m.CTOR_VPTR_LITERAL_PROJECT-m.PROJECT_BASE,0x080A446C)
    struct.pack_into("<I",b,m.VTABLE_PROJECT-m.PROJECT_BASE,0x08072639)
    p.write_bytes(b)
    r=m.scan(p)
    assert r["vptr_matches"] is True
    assert r["slot0_matches"] is True
