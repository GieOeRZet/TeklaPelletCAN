"""Evidence extraction: observations only, no semantic guessing."""
from __future__ import annotations
from dataclasses import dataclass
from .trace import EventKind, TraceLog

@dataclass(frozen=True)
class Evidence:
    category: str
    statement: str
    seq: int

def extract(trace: TraceLog) -> list[Evidence]:
    out: list[Evidence] = []
    for e in trace.events:
        if e.kind == EventKind.WRITE and e.address is not None:
            out.append(Evidence("memory-write",
                                f"PC 0x{e.pc:08X} wrote 0x{e.value or 0:08X} to 0x{e.address:08X}",
                                e.seq))
        elif e.kind == EventKind.INDIRECT_CALL:
            target = "unknown" if e.target is None else f"0x{e.target:08X}"
            out.append(Evidence("indirect-call",
                                f"PC 0x{e.pc:08X} indirect-called {target}",
                                e.seq))
        elif e.kind == EventKind.CAN_RX:
            out.append(Evidence("can-rx", f"CAN RX at PC 0x{e.pc:08X}", e.seq))
        elif e.kind == EventKind.CAN_TX:
            out.append(Evidence("can-tx", f"CAN TX at PC 0x{e.pc:08X}", e.seq))
    return out

def markdown(trace: TraceLog) -> str:
    lines = ["# Runtime Evidence", "", "| Seq | Category | Observation |", "|---:|---|---|"]
    for item in extract(trace):
        lines.append(f"| {item.seq} | {item.category} | {item.statement} |")
    return "\n".join(lines) + "\n"
