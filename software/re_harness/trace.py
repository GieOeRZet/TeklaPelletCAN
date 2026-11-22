"""Structured runtime evidence model."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Optional

class EventKind(str, Enum):
    CALL = "call"
    RETURN = "return"
    READ = "read"
    WRITE = "write"
    INDIRECT_CALL = "indirect_call"
    CAN_RX = "can_rx"
    CAN_TX = "can_tx"
    SNAPSHOT = "snapshot"

@dataclass(frozen=True)
class TraceEvent:
    seq: int
    kind: EventKind
    pc: int
    address: Optional[int] = None
    value: Optional[int] = None
    size: Optional[int] = None
    target: Optional[int] = None
    caller: Optional[int] = None
    object_address: Optional[int] = None
    offset: Optional[int] = None
    pid: Optional[int] = None
    note: str = ""

@dataclass
class TraceLog:
    events: list[TraceEvent] = field(default_factory=list)
    def add(self, event: TraceEvent) -> TraceEvent:
        self.events.append(event); return event
    def writes_to(self, address: int) -> list[TraceEvent]:
        return [e for e in self.events if e.kind == EventKind.WRITE and e.address == address]
    def indirect_calls_from(self, pc: int) -> list[TraceEvent]:
        return [e for e in self.events if e.kind == EventKind.INDIRECT_CALL and e.pc == pc]
    def changed_addresses(self) -> set[int]:
        return {e.address for e in self.events if e.kind == EventKind.WRITE and e.address is not None}
    def last(self, kind: Optional[EventKind] = None) -> Optional[TraceEvent]:
        for event in reversed(self.events):
            if kind is None or event.kind == kind: return event
        return None
    def extend(self, events: Iterable[TraceEvent]) -> None:
        self.events.extend(events)
