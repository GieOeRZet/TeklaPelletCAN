#!/usr/bin/env python3
"""Static evidence scanner for the panel RTC auto-sync path.

Scope: FW2213TK static RE only. The scanner is intentionally conservative:
it checks byte signatures at the already-established project addresses and
reports the exact evidence needed to reproduce the PASS without inventing
semantics from unrelated literals.

Firmware load address for this canonical image: 0x08000000.
"""

from __future__ import annotations

from pathlib import Path
import sys

BASE = 0x08000000
RUNTIME_BASE = 0x08010000
FUNC_AUTOSYNC = 0x08062638
FUNC_RTC_SET = 0x08018E94
FUNC_RTC_GET = 0x08018F18
FUNC_RTC_BCD = 0x08018FF8
PID_AUTOSYNC = 0x372F

# Thumb-2 bytes as they occur in the canonical binary.
SIG_PID = bytes.fromhex("43 f2 2f 72")
SIG_BL_RTC_SET = bytes.fromhex("b6 f7 d5 fa")
SIG_BL_RTC_GET = bytes.fromhex("b6 f7 99 fb")
SIG_BL_RTC_BCD = bytes.fromhex("b6 f7 f6 fb")
RUNTIME_PTR_AUTOSYNC = (FUNC_AUTOSYNC + 0x10000 + 1).to_bytes(4, "little")


def project_to_file(addr: int) -> int:
    return addr - BASE


def read_region(blob: bytes, start: int, size: int) -> bytes:
    off = project_to_file(start)
    if off < 0 or off + size > len(blob):
        raise ValueError(f"region outside image: {start:#x}+{size:#x}")
    return blob[off : off + size]


def find_all(data: bytes, sig: bytes) -> list[int]:
    out = []
    pos = 0
    while True:
        pos = data.find(sig, pos)
        if pos < 0:
            return out
        out.append(pos)
        pos += 1


def scan(path: Path) -> dict:
    blob = path.read_bytes()
    # FUN_08062638 is 718 bytes per the recovered Ghidra function table.
    auto = read_region(blob, FUNC_AUTOSYNC, 718)
    runtime_ptr_hits = [
        hex(BASE + x) for x in find_all(blob, RUNTIME_PTR_AUTOSYNC)
    ]
    return {
        "file": str(path),
        "size": len(blob),
        "base": hex(BASE),
        "autosync_function": hex(FUNC_AUTOSYNC),
        "autosync_size": len(auto),
        "pid_372f_offsets": [hex(FUNC_AUTOSYNC + x) for x in find_all(auto, SIG_PID)],
        "rtc_set_signature": [hex(FUNC_AUTOSYNC + x) for x in find_all(auto, SIG_BL_RTC_SET)],
        "rtc_get_signature": [hex(FUNC_AUTOSYNC + x) for x in find_all(auto, SIG_BL_RTC_GET)],
        "rtc_bcd_signature": [hex(FUNC_AUTOSYNC + x) for x in find_all(auto, SIG_BL_RTC_BCD)],
        "runtime_ptr_autosync": hex(FUNC_AUTOSYNC + 0x10000 + 1),
        "runtime_ptr_hits_project": runtime_ptr_hits,
        "known_targets": {
            "rtc_set": hex(FUNC_RTC_SET),
            "rtc_get": hex(FUNC_RTC_GET),
            "rtc_bcd": hex(FUNC_RTC_BCD),
            "pid": hex(PID_AUTOSYNC),
            "runtime_base": hex(RUNTIME_BASE),
        },
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} FW.bin", file=sys.stderr)
        return 2
    result = scan(Path(argv[1]))
    for k, v in result.items():
        print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
