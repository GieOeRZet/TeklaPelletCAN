# NewEstyma — TOOLING

## Current tools

### tools/re_scan.py
Broad static RE scan: BL edges, literals, object-relative operations, parameter/PID references.

### tools/vtable_scan.py
Finds executable pointer-table candidates and vptr literal occurrences. Candidate detector only; RAW proof remains authoritative.

### tools/runtime_trace_analyzer.py
Aggregates CALL/RETURN/READ/WRITE/INDIRECT_CALL and correlates runtime object addresses/offsets. Main improvement target: stronger object/vtable identity and scheduler correlation.

### tests
tools/test_re_scan.py
tools/test_re_tools.py

## Planned automatic extensions
When needed, add:
- tools/object_lifecycle_scan.py
- tools/vtable_interface_scan.py
- tools/pid_matrix_builder.py

The target graph is:
constructor -> this -> argument objects -> field stores -> vptr -> methods

and:
vptr -> slot -> implementation -> callers -> callees -> object offsets

and:
catalog -> PID -> runtime record -> storage -> type -> min/max/default -> provider -> CAN -> UI

## Tool rules
- deterministic output
- RAW and PROJECT addresses together
- never silently apply address offsets
- candidate/proven status explicit
- JSON output where useful
- tests for new parsers/decoders
- preserve failed/rejected matches


## PASS 18 additions

- `tools/provider_interface_scan.py` — evidence-first inspection of a known provider/interface address; deliberately does not assume a contiguous vtable.
- `tools/test_provider_interface_scan.py` — scanner self-tests.
- Provider interface workflow now distinguishes code-pointer entries from mixed data in interface-adjacent regions.
