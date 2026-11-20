# TeklaPelletCAN V0.1 — BASELINE / EARLY DEVELOPMENT

Firmware: FW2213TK_kopia.bin
Size: 2,031,616 B (0x1F0000)
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071
Runtime/file base: 0x08010000

## Purpose
This is the closed V0.1 baseline for the reverse-engineering phase. It consolidates what is proven, what is partial, and what is still required before a 1:1 behavioural reproduction can be built on ESP32+CAN, a dynamic Home Assistant UI, and a PC emulator.

## Proven / closed
- Cortex-M/IAR startup and Reset_Handler chain.
- IAR LZ77 initialization and SRAM decompression.
- 188-record parameter dictionary at raw 0x2F008 / runtime 0x0803F008.
- PIN/access hierarchy 0900 / 0999 / 6154.
- Parameter read/write core 0x36FF2..0x37540.
- Main/special parameter mapping tables 0x37578 / 0x37B48.
- Buffer/register/time functions 0x17DC4..0x1908E and 0x39250..0x3933E.
- HomeView + FUN_08031CCC structure and parameter dependencies.
- Range-check context 0x185B0..0x18630 using 0x18F18.
- Context 0x14840..0x14870.
- TouchGFX presence and framework strings.
- Real CAN peripheral configuration code around 0x60B80..0x61940.

## HomeView
Confirmed: seven bottom tiles, five activity overlays, pellet hopper/fill, boiler/set temperatures, burner state, operating mode, summer/winter, WiFi, CO1/CO2/CWU widgets, clock/date, alarm/manual/external-temperature related widgets and their configuration gates.

Important gates:
- CO1: 0x10E >= 1
- CO2: 0x10E >= 2
- CWU: 0x10F != 0
- burner activity: 0x39 not in {0,9,10}
- CO1 activity: 0x0B != 0 && 0xAC != 0
- CO2 activity: 0x0B != 0 && 0xD7 != 0
- CWU activity: 0x0B != 0 && 0xDC != 0

## Global scan
The whole 0x000000..0x1EFFFF image was linearly disassembled and globally scanned for:
- vectors,
- BL/BLX targets,
- strings,
- TouchGFX evidence,
- TypedText pointer tables,
- hardware literals,
- CAN code,
- UI/application regions.

Important warning: linear objdump also decodes data/literal pools as instructions. It is not a finished CFG.

## Major remaining gaps
1. All screens/views except HomeView are not yet fully reconstructed.
2. Full TouchGFX navigation graph (View/Presenter/Transition/FrontendHeap) is missing.
3. Parameter semantics need a machine-readable final database: min/max/step/scale/enums/visibility/editability/dependencies/read/write.
4. CAN protocol is not yet 1:1: bitrate/bit timing, all IDs, DLCs, payload layouts, cycles, timeouts, handshake, alarms/status and special frames remain.
5. NVM/flash/CRC/default/recovery and alarm-history persistence are not closed.
6. Scheduler/programs/services/statistics state machines are not closed.
7. Complete bitmap/font/glyph/TypedText asset manifest is not closed.
8. Full runtime RAM/object layout and state model are not closed.
9. PC emulator and HA dynamic UI are not implemented.

## Target architecture
Build one canonical model:

Parameter DB + CAN DB + UI schema + configuration/access gates + assets + navigation

and generate three consumers:
- ESP32 + TWAI
- Home Assistant dynamic UI
- PC emulator

Do not implement the ESP as a collection of hard-coded screens. The canonical model must drive all three targets.

## Evidence policy
FACT = direct binary/disassembly/xref.
LIKELY = strong but not complete inference.
HYPOTHESIS = semantic guess.
UNKNOWN = not established.

## Next P0
Construct a recursive-disassembly/CFG index seeded by vectors, confirmed BLs, vtables/function pointers and IRQ vectors; classify every byte as confirmed code / likely code / pointer table / string / asset / compressed / unknown. Then reconstruct every View/Presenter/Transition before writing the emulator.