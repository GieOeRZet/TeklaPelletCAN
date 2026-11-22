# NewEstyma — AGENT START HERE

READ THIS FILE FIRST.

## Mission
Reconstruct the Estyma controller firmware as completely and faithfully as possible (target: 1:1), then use the recovered model as the basis for a universal ESP32-C6 + CAN implementation and integrations.

## Canonical firmware
Filename: FW2213TK_kopia.bin
Size: 0x1F0000 = 2,031,616 bytes
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

Mapping:
PROJECT = 0x08000000 + RAW
RUNTIME/RE_PACK = PROJECT + 0x10000
RAW = RUNTIME - 0x08010000

Important: vtable/function pointers stored in the running image are runtime addresses; translate them to PROJECT before indexing the raw BIN.

RAW BIN is the source of truth.

## Rules
1. Continue autonomously. Do not stop after a fixed number of passes.
2. HARD means a fact is proven; HARD is not 100% project completion.
3. If a tool becomes insufficient, improve or create it and continue.
4. Every meaningful pass gets a report under analiza/FW2213TK-2026-11-22/.
5. Update the master state after important closures.
6. Separate FACT, STRONG, INFERENCE, OPEN and REJECTED.
7. Never promote an inference because it looks plausible.
8. Preserve negative results and rejected hypotheses.
9. Do not repeat closed work unless required to close a dependent boundary.
10. Continue until meaningful OPEN space is exhausted or explicitly bounded.

## Current anchors
- CAN2: 0x40006800
- parameter manager: 0x20008D84
- provider: 0x20008D64
- publication sink: 0x20008D60
- manager vtable: 0x080A44F0
- provider vtable runtime address: 0x080A31F0
- provider vtable PROJECT address: 0x080931F0
- provider vtable RAW offset: 0x931F0
- provider slot0 GET: runtime 0x0801DB31 / PROJECT 0x0800DB31
- provider slot1 SET: runtime 0x0801DB79 / PROJECT 0x0800DB79
- manager callback: FUN_08010FCE
- runtime parameter stride: 0x2C
- runtime scan bound: 660
- catalog: 260 entries
- READ: StdId 0x0604, command 0x40
- publication: StdId 0x0584, command 0x42

## Latest scheduler closure
startup -> 0x0800DDC0(0x20008D84,0x20008D64,0x20008D60) -> 0x08014824 -> scheduler registration -> 0x080147C8 -> vtable slot 0 -> FUN_08010FCE

## Latest provider closure
Provider vtable slots 0/1 are now HARD. Slot 0 is GET(PID, output) and slot 1 is SET(PID, value/type). This closure also corrected the runtime-vs-PROJECT address-base interpretation.

## Next targets
1. Recover remaining provider interface slots and persistence semantics.
2. Independently validate scheduler expiry -> FUN_08010FCE at runtime.
3. Build the complete 260-row cross-layer matrix.
4. Close sidecar class 1/2/3 semantics.
5. Continue UI/CAN object graphs.

## Tool workflow
re_scan -> vtable/interface -> object lifecycle -> runtime correlation -> PID matrix -> focused RAW proof -> pass report -> master update

Existing tools:
- tools/re_scan.py
- tools/vtable_scan.py
- tools/runtime_trace_analyzer.py
- tools/test_re_scan.py
- tools/test_re_tools.py

If a repeated manual operation appears, automate it.

## Reading order
1. this file
2. 01_PROJECT_STATE.md
3. 02_WORKFLOW.md
4. 03_TOOLING.md
5. 04_FIRMWARE_MANIFEST.md
6. DOKUMENTACJA/REVERSE_ENGINEERING_MASTER_2026-11-22.md
7. newest pass reports in analiza/

Important: 260 catalog != 660 runtime table. Mechanism closure != semantic closure. HARD != 100%.


## PASS 35 — emulator startupu
Do odczytu stanu RAM po inicjalizacji użyj `tools/emu_startup.py` / `boot()` (patrz 03_TOOLING.md). Tabela runtime 655 rekordów jest w `analiza/FW2213TK-2026-11-22/data/`. Klucz runtime = PID (z nazwą ASCII w rekordzie).
