"""Self-checks for the platform-independent RE harness."""
from software.re_harness.trace import EventKind, TraceEvent, TraceLog
from software.re_harness.watchpoints import Watchpoint, WatchpointSet

def test_watchpoint():
    trace = TraceLog()
    targets = WatchpointSet([Watchpoint(0x20008D60, 4, "D60")])
    hits = targets.record_write(trace, 1, 0x08012345, 0x20008D60, 0x080A4544)
    assert len(hits) == 1
    assert hits[0].address == 0x20008D60
    assert hits[0].value == 0x080A4544

def test_trace_queries():
    trace = TraceLog([
        TraceEvent(1, EventKind.INDIRECT_CALL, 0x08062AE4, target=0x080629FC),
        TraceEvent(2, EventKind.WRITE, 0x080103EC, address=0x2002466C, value=0x080A4568),
    ])
    assert trace.indirect_calls_from(0x08062AE4)[0].target == 0x080629FC
    assert 0x2002466C in trace.changed_addresses()
