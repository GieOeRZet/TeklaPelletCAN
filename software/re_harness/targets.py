"""High-value runtime targets derived from current RE evidence."""
from .watchpoints import Watchpoint, WatchpointSet

DEFAULT_TARGETS = WatchpointSet([
    Watchpoint(0x20008D60, 4, "parameter-table-object"),
    Watchpoint(0x20008D84, 4, "parameter-record-table"),
    Watchpoint(0x200114C0, 12, "node4-object-record"),
    Watchpoint(0x2002466C, 0x24, "CAN-poller-object"),
    Watchpoint(0x200244EC, 4, "CAN-TX-queue"),
    Watchpoint(0x200244DC, 4, "CAN-RX-queue"),
])

# Static instruction anchors for an emulator adapter:
# 0x080629FC = CAN poller
# 0x08062AE4 = READ 0x0604/0x40 construction
# 0x08063B80 = CAN dispatcher
# 0x08062A90 = parameter parser
# 0x08011812 = parameter commit/update
# 0x0806E59C = CAN TX adapter
