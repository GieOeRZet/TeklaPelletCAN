"""Deterministic memory watchpoints used by the RE harness."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from .trace import EventKind, TraceEvent, TraceLog

@dataclass(frozen=True)
class Watchpoint:
    address: int
    size: int = 4
    name: str = ""
    def covers(self, address: int, size: int = 1) -> bool:
        return address < self.address + self.size and self.address < address + size

class WatchpointSet:
    def __init__(self, watchpoints: Iterable[Watchpoint] = ()) -> None:
        self._items = list(watchpoints)
    def add(self, watchpoint: Watchpoint) -> None:
        self._items.append(watchpoint)
    def matching(self, address: int, size: int = 1) -> list[Watchpoint]:
        return [w for w in self._items if w.covers(address, size)]
    def record_write(self, trace: TraceLog, seq: int, pc: int, address: int,
                     value: int, size: int = 4, caller: int | None = None) -> list[TraceEvent]:
        hits = self.matching(address, size)
        for watch in hits:
            trace.add(TraceEvent(seq=seq, kind=EventKind.WRITE, pc=pc,
                address=address, value=value, size=size, caller=caller,
                note=f"watchpoint:{watch.name or hex(watch.address)}"))
        return trace.events[-len(hits):] if hits else []
