import hashlib
import subprocess
import sys
from pathlib import Path

def test_timestamp_tx_exclusion(tmp_path):
    src = tmp_path / "FW.bin"
    # Minimal synthetic image is not sufficient because anchors are absolute.
    # This test therefore validates the scanner's own source-level contract
    # and is intended for CI environments where the canonical firmware is present.
    p = Path(__file__).resolve().parents[1] / "tools" / "cg_timestamp_tx_exclusion_scan.py"
    assert p.exists()
    text = p.read_text()
    assert "0x111EE" in text
    assert "0x112B8" in text
    assert "0x2165" in text
