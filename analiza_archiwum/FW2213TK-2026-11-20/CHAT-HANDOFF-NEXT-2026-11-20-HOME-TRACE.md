# CHAT HANDOFF — NEXT CHAT — HOME SCREEN TRACE — 2026-11-20

## User decision

Continue with P1 direction #2: HOME SCREEN RECONSTRUCTION.

## Immediate targets

1. Trace all indirect resource references for bitmap IDs 115, 144, 174.
2. Trace FUN_08031CCC caller/callee and object creation tree.
3. Reconstruct exact Home parent/child placement.
4. Identify visibility/configuration gates.
5. Connect Home widgets to the established animation/state-machine engine.
6. Trace model/CAN dependencies where firmware evidence exists.

## Firmware

File: FW2213TK_kopia.bin
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071
Runtime base: 0x08010000
file_offset = runtime_address - 0x08010000

## HARD baseline

IAR:
- __iar_program_start 0x94644
- __iar_init_vfp 0x8B4A8
- __cmain 0x8F74C
- __iar_low_level_init 0x8F766
- __iar_data_init3 0x89440
- __iar_lz77_init3 0x6E68C
- __iar_zero_init3 0x784F4
- main 0x62D82
- reconstructed SRAM 0x118B3 = 71859 bytes
- list block 0x20011534..0x20011669

Parameter/UI:
- 0x47 = case 10 / Palnik
- 0x48 = case 0 / Kocioł
- both have +0x158 gate
- graph 0x47 = 0x2261..0x2265
- graph 0x48 = 0x2268,0x226E,0x226F,0x2275,0x227A
- FUN_080480C0 does not individually filter 0x48 from presenter+0x20.

TypedText option tables:
- 0x0807F58C -> file 0x6F58C
- 0x0807F59C / key 0xB0 / 47290 -> six IDs 0xAF,0xB0,0xB1,0xB3,0xB4,0xB5
- 0x0807F5EC / keys 0x47,0x48 -> one ID 0x0037 (55)
- 0x0807F5EC is real uint16_t data, not a linker/vtable artifact.

PIN 6154 wrapper FUN_0804E9DC:
- fixed children at view+0x78,+0x11C,+0xD8,+0x17C,+0x1B0,+0xA4,+0x1E4
- access byte FUN_080314BA()+0x158
- if >=3 add view+0x23C
- always add view+0x210

Existing Home evidence:
- FUN_08031CCC is the key Home/widget-tree function.
- bitmap IDs 115/144/174 are open indirect-resource targets.
- FUN_080469E8 is Boiler widget, instantiated four times; known internal fields are recorded in the master handoff.
- hopper bitmaps 51/52/53 form a state machine.
- animation IDs already mapped: 138..143 pump; 105..107 mixer; 8..10 fan; 36..44 feeder/grate/heater group.

## Workflow

External deep-analysis agent = semantic analyst.
Execution assistant = exact BIN/Git extraction, disassembly, xrefs, raw windows and verification.

When asked for raw material:
- execute exactly;
- return one copyable block;
- no extra semantic interpretation unless explicitly requested.

After substantial closure:
- update GitHub report and continuity;
- distinguish HARD/HIGH/MEDIUM/OPEN/REJECTED.

## First attack

Start with exhaustive xrefs/resource resolution for 115, 144, 174. Do not stop at the first literal. Follow:
bitmap ID -> resource table/lookup -> widget constructor -> parent -> Home root -> visibility gate -> model/CAN dependency.

Then attack FUN_08031CCC and build the complete Home widget tree with unresolved edges explicitly marked.

Do not assume the old TeklaPelletCAN implementation or old screen layout is ground truth.
