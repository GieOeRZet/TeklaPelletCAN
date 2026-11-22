"""Platform-independent model of the recovered Estyma parameter record engine.

Only semantics closed by firmware evidence are implemented. Unknown sidecar semantics
remain explicit rather than guessed.
"""
from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, Optional, Sequence


class ValueType(IntEnum):
    U8 = 1
    U16 = 2
    U32 = 3
    S16 = 4
    S32 = 5


@dataclass(frozen=True)
class TypedValue:
    value: int
    type: ValueType


@dataclass
class ParameterRecord:
    # Canonical 0x2C-byte record:
    # +08 PID, +0C storage binding, +10 type,
    # +14 minimum, +1C maximum, +24 default/reset.
    pid: int
    value: int
    type: ValueType
    minimum: TypedValue
    maximum: TypedValue
    default: TypedValue
    # R+0x2C/R+0x30 are physically the next slot; kept explicit as sidecar
    # state only because registration code writes these adjacent addresses.
    sidecar_gate: Optional[int] = None
    sidecar_metadata: Optional[int] = None

    def validate_type(self, value: int) -> bool:
        if self.type == ValueType.U8:
            return 0 <= value <= 0xFF
        if self.type == ValueType.U16:
            return 0 <= value <= 0xFFFF
        if self.type == ValueType.U32:
            return 0 <= value <= 0xFFFFFFFF
        if self.type == ValueType.S16:
            return -0x8000 <= value <= 0x7FFF
        if self.type == ValueType.S32:
            return -0x80000000 <= value <= 0x7FFFFFFF
        return False

    def validate_range(self, value: int) -> int:
        if value > self.maximum.value:
            return 6
        if value < self.minimum.value:
            return 7
        return 0

    def write(self, value: int, validate_range: bool = True) -> int:
        if not self.validate_type(value):
            return 5
        if validate_range:
            status = self.validate_range(value)
            if status:
                return status
        self.value = value
        return 0

    def reset(self) -> int:
        self.value = self.default.value
        return self.value


class ParameterStore:
    STRIDE = 0x2C
    MAX_SCAN = 0x294  # scan bound, not a populated-record count

    def __init__(self, records: Sequence[ParameterRecord] = ()) -> None:
        self.records = list(records)
        self.by_pid: Dict[int, ParameterRecord] = {r.pid: r for r in self.records}

    def lookup(self, pid: int) -> ParameterRecord:
        return self.by_pid[pid]

    def read(self, pid: int) -> int:
        return self.lookup(pid).value

    def write(self, pid: int, value: int, validate_range: bool = True) -> int:
        return self.lookup(pid).write(value, validate_range)

    def repair_out_of_range(self, pid: int) -> int:
        r = self.lookup(pid)
        if r.validate_range(r.value) == 0:
            return r.value
        return r.reset()


@dataclass(frozen=True)
class FamilyMapping:
    base_pid: int
    instances: int = 4

    def resolve(self, instance: int) -> int:
        if not 1 <= instance <= self.instances:
            raise ValueError("instance must be 1..4")
        return self.base_pid + instance - 1


class ParameterMapper:
    FAMILY_COUNT = 49
    SINGLETON_COUNT = 372

    def __init__(self, families: Sequence[int], singletons: Sequence[int]) -> None:
        if len(families) != self.FAMILY_COUNT:
            raise ValueError("expected 49 family bases")
        if len(singletons) != self.SINGLETON_COUNT:
            raise ValueError("expected 372 singleton IDs")
        self.families = tuple(FamilyMapping(x) for x in families)
        self.singletons = tuple(singletons)

    def resolve_family(self, family_index: int, instance: int) -> int:
        return self.families[family_index].resolve(instance)

    def resolve_singleton(self, index: int) -> int:
        return self.singletons[index]

    @property
    def logical_position_count(self) -> int:
        return self.FAMILY_COUNT * 4 + self.SINGLETON_COUNT
