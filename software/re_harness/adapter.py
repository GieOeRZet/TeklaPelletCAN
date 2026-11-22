"""Backend-neutral interface for an ARM emulator.

A concrete backend (Unicorn/QEMU/etc.) must implement this interface. Keeping
the interface here prevents the RE model from depending on a specific emulator.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from .trace import TraceLog
from .watchpoints import WatchpointSet

class ArmBackend(ABC):
    def __init__(self, trace: TraceLog, watchpoints: WatchpointSet) -> None:
        self.trace = trace
        self.watchpoints = watchpoints

    @abstractmethod
    def reset(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def load_firmware(self, image: bytes, base: int = 0x08000000) -> None:
        raise NotImplementedError

    @abstractmethod
    def write_memory(self, address: int, data: bytes) -> None:
        raise NotImplementedError

    @abstractmethod
    def read_memory(self, address: int, size: int) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def run_until(self, address: int, max_steps: int = 1_000_000) -> None:
        raise NotImplementedError

    def feed_can(self, std_id: int, data: bytes) -> None:
        raise NotImplementedError("Backend must expose CAN injection")
