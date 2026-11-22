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


## PASS 27 analysis note

Pointer-flow correlation was extended from a row-relative field to its constructor-established pointer target. This preserves the distinction between:
- row[i]+offset as a field;
- the pointer stored in that field;
- the memory read performed through that pointer.

This distinction is now required for UI/object graph work.


## PASS 28 analysis note

The runtime-class TBB table is now treated as a first-class graph node:
runtime class -> handler -> common/special tail -> UI construction state.

For UI graph work, preserve the distinction:
- root MenuTree selector;
- runtime class byte;
- handler-internal selector bytes at object+0x12B/object+0x12C;
- widget/page constructor inputs.


## PASS 29 tooling

Added `tools/ui_dispatch_scan.py` and `tools/test_ui_dispatch_scan.py`.

The scanner:
- reads the exact 21-byte TBB table at RAW 0x3C076;
- resolves 16-bit and 32-bit trampoline branches;
- follows only bounded local trampolines;
- stops at an unconditional branch leaving the local case, preserving inline/special cases;
- records resolved PROJECT handler addresses;
- records direct selector-byte stores where statically recognizable.

Regression coverage includes all 21 class entries, classes 1..4 shared handler parameters, class 12 special path, class 14 return, class 15 direct 0x42318 path, and classes 16..20.


## PASS 30 analysis note

The UI graph now treats vtable-backed callback objects as explicit graph nodes:
constructor -> vtable -> object fields -> indirect dispatch -> callback.

Future UI tracing must follow both:
- static callback/config pointers;
- vtable calls through object+0x110.


## PASS 35 additions — EMULACJA STARTUPU (nowa klasa dowodu: stan RAM po inicjalizacji)

- `tools/emu_startup.py` — emulacja startupu FW2213TK w Unicornie (Cortex-M4). Obraz pod RUNTIME 0x08010000. Opcje: `--max`, `--ram`, `--watch LO:HI`, `--trace-calls ADDR`, `--stub ADDR=VAL`, `--first-task`, `--patch-nop`.
  API: `boot(bin)` zwraca `(mu, raw)` po startupie + pierwsze zadanie FreeRTOS. Pomijane: pętle RCC (3 NOP-y tylko w kopii w pamięci), `RCC_GetFlagStatus` 0x08028AE4 -> 1, svc #0 odtwarzane ręcznie.
  NIE modeluje przerwań, PendSV/kolejnych zadań ani peryferiów. Nie dodawaj hooków UC_HOOK_BLOCK ani zapisu pamięci w hookach odczytu (zakłóca emulację).
  Hook na każdą instrukcję jest ~100x wolniejszy; używaj hooków jednoadresowych.
- `tools/runtime_param_table.py` — tabela runtime 655 rekordów (CSV).  `tools/test_runtime_param_table.py` — regresja.
- `tools/resolver_tables.py` — tabele rezolwera 08036FF2 (49 + 372 rekordy).  `tools/test_resolver_tables.py` — regresja.
- `tools/bl_xref.py` — wszystkie BL/B.W do adresów (UWAGA: adresy RUNTIME = PROJECT + 0x10000).
- `tools/disasm_thumb.py` — dezasemblacja Thumb-2 z adresu RUNTIME (`--project` dla PROJECT).

Reguła adresowa (częsty błąd): argumenty narzędzi to adresy RUNTIME; adresy w raportach to PROJECT. 0x0801143C (PROJECT) = 0x0802143C (RUNTIME).
Reguła odczytu tabel: rekordy 4-bajtowe są wyrównane do bazy tabeli; odczyt z przesunięciem 2 B daje fałszywe pary (błąd PASS 26).

- `tools/pid_matrix.py` (PASS 36) — macierz PID: storage/typ/zakres/tryb dostępu/sync/klucze UI z danych PASS 35 -> data/pid_matrix_655.csv.
