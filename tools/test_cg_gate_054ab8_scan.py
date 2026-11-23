from pathlib import Path

def test_gate_054ab8_scanner_exists():
    p=Path(__file__).resolve().parents[1]/"tools/cg_gate_054ab8_scan.py"
    assert p.exists()
    s=p.read_text()
    assert "0x44ca6" in s
    assert "0x1498" in s
    assert "0x201A" in s
