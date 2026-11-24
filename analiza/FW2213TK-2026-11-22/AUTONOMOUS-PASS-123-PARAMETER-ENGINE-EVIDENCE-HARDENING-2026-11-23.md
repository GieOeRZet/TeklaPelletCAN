# AUTONOMOUS PASS 123 — PARAMETER ENGINE EVIDENCE-HARDENING — 2026-11-23

## Findings

### 1. Runtime record geometry
- Canonical stride remains 0x2C.
- +0x08 = external parameter/CAN index.
- +0x0C = local storage pointer.
- +0x10 = type tag.
- +0x2C = next record; +0x30 = +0x04 of next record.

### 2. Descriptor-derived values
The platform model previously described +0x14/+0x1C/+0x24 directly as minimum/maximum/default raw fields. That wording exceeded the available proof.

Current evidence only proves that these offsets feed descriptor/getter/validation/reset paths. The decoded values may be represented as minimum/maximum/default in the platform model, but this is a semantic decode, not proof that the raw record stores three scalar fields with those names.

Model comments were hardened accordingly in `software/model/parameter_engine.py`.

### 3. Sidecar boundary
Sidecar class/access behavior is partially closed:
- record class values 0..3 correlate with catalog access classes.
- class 1 and class 3 are accepted by the write/operation gate.
- synchronization includes class 2 and class 3.
- exact full semantic distinction of classes 1/2/3 remains OPEN.

### 4. 260/568/660 separation
- 260 = catalog cardinality.
- 568 = logical UI/model mapper positions.
- 660 = runtime lookup scan bound.
These are separate namespaces and must not be collapsed into one parameter count.

## Code change
`software/model/parameter_engine.py`` comments were corrected so the implementation no longer claims unproven raw field semantics for +0x14/+0x1C/+0x24 or treats +0x2C/+0x30 as fields of the same record.

## Remaining highest-value static targets
1. Exact descriptor layout behind 0x08014728/0x08014734/0x0801155A.
2. Remaining provider vtable interface slots.
3. Complete 260 catalog -> runtime record -> CAN/UI matrix.
4. Local-write publication timing/shadow semantics.
5. Callback entry CFG for 0x08048493 and 0x080485A1.

## Dynamic boundary
Scheduler expiry and the 6666 CAN/poller tests remain dynamic-only and are not marked CLOSED without actual emulator evidence.