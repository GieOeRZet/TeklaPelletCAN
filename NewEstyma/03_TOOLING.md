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
- RAW, PROJECT and RUNTIME addresses together
- runtime base is 0x08010000; PROJECT base is 0x08000000
- never silently apply address offsets
- vtable/function-pointer values are runtime addresses and must be translated before RAW indexing
- candidate/proven status explicit
- JSON output where useful
- tests for new parsers/decoders
- preserve failed/rejected matches


## PASS 18 additions

- `tools/provider_interface_scan.py` — evidence-first inspection of a known provider/interface address; deliberately does not assume a contiguous vtable.
- `tools/test_provider_interface_scan.py` — scanner self-tests.
- Provider interface workflow now distinguishes code-pointer entries from mixed data in interface-adjacent regions.


## PASS 19 address-base correction

The firmware image has a runtime/repacked base of 0x08010000 while static PROJECT addresses use 0x08000000 + RAW. Vtable analysis must inspect RAW at RUNTIME - 0x08010000. Provider vtable 0x080A31F0 therefore lives at RAW 0x931F0, not RAW 0xA31F0.
