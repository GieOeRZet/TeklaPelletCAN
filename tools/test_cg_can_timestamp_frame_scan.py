import hashlib, struct, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import cg_can_timestamp_frame_scan as s

def test_constants():
    assert s.PID == 0x2165
    assert s.STD_ID == 0x584
    assert s.OPCODE_SET == 1
    assert s.WIRE_U32 == 5
    assert s.TYPE_U32 == 3

def test_u32_layout():
    v=0x12345678
    assert struct.pack("<I",v) == bytes([0x78,0x56,0x34,0x12])

def test_firmware_sha():
    p=Path("/mnt/data/FW2213TK (1).bin")
    if p.exists():
        assert hashlib.sha256(p.read_bytes()).hexdigest() == "1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071"
