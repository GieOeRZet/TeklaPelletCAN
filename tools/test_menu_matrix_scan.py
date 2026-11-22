import json, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIN = Path("/mnt/data/FW2213TK_kopia.bin")

def test_menu_matrix_scan():
    if not BIN.exists():
        return
    p = subprocess.run(
        [sys.executable, str(ROOT / "tools/menu_matrix_scan.py"), str(BIN)],
        check=True, capture_output=True, text=True,
    )
    d = json.loads(p.stdout)
    assert d["sha256"] == "1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071"
    assert d["size"] == 0x1F0000
    rows = d["table"]["rows"]
    assert len(rows) == 21
    assert rows[0]["selector"] == 0 and rows[0]["typed_text"] == 60 and rows[0]["bitmap"] == 83
    assert rows[14]["selector"] == 15 and rows[14]["typed_text"] == 76 and rows[14]["bitmap"] == 96
    assert rows[15]["selector"] == 0 and rows[15]["typed_text"] == 12 and rows[15]["bitmap"] == 73
    assert rows[20]["selector"] == 95 and rows[20]["typed_text"] == 20 and rows[20]["bitmap"] == 81
    assert d["anchors"]["runtime_class_table"]["raw_hits"] == ["0x3c218"]
    assert d["anchors"]["access_update_table"]["raw_hits"] == ["0x42314"]
    assert d["anchors"]["row_ctor_thumb"]["raw_hits"] == ["0x3c030"]
    assert d["anchors"]["row_select_thumb"]["raw_hits"] == ["0x63ab8"]
    assert d["anchors"]["row_select_sibling_thumb"]["raw_hits"] == ["0x63ac0"]

if __name__ == "__main__":
    test_menu_matrix_scan()
    print("ok")
