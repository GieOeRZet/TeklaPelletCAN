from pathlib import Path
import importlib.util

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("cg_rtc_autosync_scan", HERE / "cg_rtc_autosync_scan.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_signature_constants():
    assert mod.PID_AUTOSYNC == 0x372F
    assert mod.FUNC_AUTOSYNC == 0x08062638
    assert mod.FUNC_RTC_SET == 0x08018E94
    assert mod.FUNC_RTC_GET == 0x08018F18
    assert mod.FUNC_RTC_BCD == 0x08018FF8
    assert mod.RUNTIME_BASE == 0x08010000
    assert mod.RUNTIME_PTR_AUTOSYNC == (0x08062638 + 0x10000 + 1).to_bytes(4, "little")


def test_project_to_file():
    assert mod.project_to_file(0x08000000) == 0
    assert mod.project_to_file(0x08062638) == 0x62638


def test_find_all():
    assert mod.find_all(b"abcabc", b"abc") == [0, 3]
