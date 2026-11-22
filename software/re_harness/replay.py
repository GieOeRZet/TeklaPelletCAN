"""Deterministic CAN/parameter replay cases for a future ARM backend."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class ReplayCase:
    name: str
    std_id: int
    data: bytes

def read_case(pid: int) -> ReplayCase:
    return ReplayCase(f"read_{pid:04X}", 0x0604,
                      bytes([0, 0, 0, 0x40, pid & 0xFF, (pid >> 8) & 0xFF, 1, 0]))

def write_case(pid: int, value: int, value_type: int = 3) -> ReplayCase:
    # Exact write payload encoding beyond the known command/PID/type fields
    # remains an adapter concern; keep this explicit rather than inventing it.
    return ReplayCase(f"write_{pid:04X}_t{value_type}", 0x0604,
                      bytes([0, 0, 0, 0x20, pid & 0xFF, (pid >> 8) & 0xFF, value_type & 0xFF, value & 0xFF]))

def baseline_cases(pids: Iterable[int]) -> list[ReplayCase]:
    return [read_case(pid) for pid in pids]
