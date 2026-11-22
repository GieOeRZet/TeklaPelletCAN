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


## PASS 21 additions

- `tools/menu_matrix_scan.py` — deterministic extraction of the canonical 21×6 B MenuTree table plus whole-BIN literal-anchor audit for the runtime class table, access/update table, row constructor and row-selection resolvers.
- `tools/test_menu_matrix_scan.py` — regression test against the canonical BIN SHA-256 and known anchor offsets.


## PASS 22 additions

- `tools/iar_data_extract.py` — deterministic reproduction of the IAR LZ77 `.data` decoder and extraction of the two 21-byte MenuTree runtime tables.
- `tools/test_iar_data_extract.py` — regression test for decompressed size, exact table bytes and equality with root selectors.


## PASS 24 additions

- `tools/pointer_flow_scan.py` was upgraded to be Thumb-2 instruction-width aware. The previous scanner could interpret the second halfword of a 32-bit instruction as a false Thumb-1 memory operation.
- The scanner now recognizes common Thumb-2 immediate load/store forms, MOVW/MOVT candidates, and Thumb-2 PUSH.W function starts.
- SRAM targets are kept in SRAM address space; PROJECT/RUNTIME translation is applied only to firmware code addresses.
- `tools/test_pointer_flow_scan.py` now contains a regression proving that RAW 0x3C1FE is not a STRB and that the 0x080422C8 function start is recovered through PUSH.W.
- Canonical BIN regression passed.


## PASS 25 analysis note

No new scanner was required. The Thumb-2-safe pointer-flow output was combined with whole-BIN runtime-pointer/vtable searches and direct Thumb disassembly to close the ownership of PROJECT 0x080422C8 and the 21-row object geometry around constructor PROJECT 0x08074508.

Reusable rule:
- when a recovered consumer is a vtable method, resolve the runtime function pointer in the vtable before assigning ownership;
- when a loop uses a fixed stride/count, derive the object-relative field mathematically and carry the relation into the next call boundary.


## PASS 26 analysis note

Negative-result workflow was extended:
- when a resolver table is reached, enumerate its complete static key domain before promoting a call edge;
- distinguish resolver input keys from resolved output/PID values;
- preserve "no static match -> no downstream call" as a first-class closure.
