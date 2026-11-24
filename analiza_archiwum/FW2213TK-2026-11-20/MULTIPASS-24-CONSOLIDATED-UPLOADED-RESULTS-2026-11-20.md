# MULTIPASS-24 — Consolidation of uploaded FW2213TK analysis package — 2026-11-20

Firmware: FW2213TK_kopia.bin
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

## 1. Input package inspected

User supplied:
FW2213TK_wyniki_analizy_2026-11-20.zip

Contents:
- RAPORT-FW2213TK-LZ77-I-PARAMETRY-2026-11-20.md
- FUN_0803E714_parametry_wg_PIN.json
- FUN_0803E714_parametry_wg_PIN.csv

The package was opened and read directly. It is a previous analysis result package, not a new firmware image.

## 2. Consolidated HARD evidence from the package

### IAR startup and data initialization

- 0x94644 = __iar_program_start
- 0x8B4A8 = __iar_init_vfp
- 0x8F74C = __cmain
- 0x89440 = __iar_data_init3
- 0x6E68C = __iar_lz77_init3
- 0x784F4 = __iar_zero_init3

IAR record 2:
- record: 0x8B4E0
- compressed/input source: 0x96114..0x9694E
- destination: 0x20000000
- reconstructed output: 0x118B3 = 71859 bytes
- target parameter-list block: 0x20011534..0x20011669, 310 bytes

### 0x47 / 0x48 closure

0x0047:
- graph family A
- parameters 0x2261..0x2265
- FUN_0803E714 case 10 = Palnik
- access gate: context + 0x158 != 0
- first list element at 0x200115D0

0x0048:
- graph family B
- parameters 0x2268, 0x226E, 0x226F, 0x2275, 0x227A
- FUN_0803E714 case 0 = Kocioł
- access gate: context + 0x158 != 0
- first list element at 0x200115B0
- explicitly NOT case 10

### Complete parameter-list map

case 0 Kocioł
- level 0: 0x0F, 0x14, 0x15
- level 1: 0x48, 0x11, 0x16, 0x118, 0x119, 0x26, 0x28, 0x14B, 0x2E, 0x2F

case 1..4 CO1..CO4
- level 0: 0xA9, 0xAA, 0xBE, 0xB1, 0xAF, 0xBC, 0xB4, 0xB5, 0xB6, 0xB7, 0xD3, 0xD4
- level 1: 0xAD, 0xAE, 0xB0, 0xB3, 0xB2, 0xB8, 0xBA, 0xB9, 0xBB, 0xBD, 0xCC

case 5 CWU
- level 0: 0xD9, 0xDA, 0xDD, 0xDE, 0xE3, 0xE7, 0xE5, 0xE6
- level 1: 0xDF, 0xE0, 0xE2, 0xE1

case 6 Solar
- level 0: 0x103, 0x104, 0x105
- level 1: 0x106, 0x107, 0x108, 0x109

case 7 Bufor
- level 0: 0xF3, 0xF4
- level 1: 0xF6, 0xF7, 0x9C, 0x9D, 0xFC

case 8 Kaskada
- level 0: 0x158, 0x14D, 0x14E, 0x14F, 0x150, 0x151, 0x152, 0x153, 0x154

case 9 Zasobnik
- level 0: 0x15E, 0x160, 0x163, 0x164
- level 1: 0x161, 0x165, 0x15F

case 10 Palnik
- level 0: 0x54, 0x59, 0x5A, 0x5D, 0x5C
- level 1: 0x47, 0x55, 0x57, 0x89, 0x76, 0x63, 0x65, 0x77, 0x78, 0x8A, 0x69, 0x6F, 0x70, 0x73, 0x8D, 0xA5, 0xA6, 0xA7, 0x5B
- level 2: 0x87, 0x79, 0x91, 0xA1

case 0x10 Konfiguracja
- level 0: 0x125, 0x08, 0x02, 0x149, 0x126
- level 1: 0x114, 0x112, 0x113, 0x10E, 0x10D, 0x10F, 0x110, 0x111, 0x115, 0x116, 0x148, 0x11A, 0x11B, 0x12, 0x11C, 0x11D, 0x122, 0x11F, 0x133
- level 2: 0x90, 0x16A

case 0x11 Statystyki / Info
- level 0: 0x19A, 0x19B, 0x19C, 0x19D, 0x19E, 0x19F, 0x1A0, 0x1A1, 0x1A2, 0x1A3, 0x1A5, 0x1A6, 0x1A7

6154:
- firmware constant 0x180A
- level 3 is not represented by a separate >=3 branch in FUN_0803E714;
- level 3 UI exposure is handled by separate gates.

## 3. Raw reconstructed list block

The package contains the complete 310-byte dump:
0x20011534..0x20011669.

This remains the authoritative reconstructed runtime data for the list-selection branch. The byte-level dump is preserved in the supplied package and earlier project reports.

## 4. Previous UI findings carried forward

The package also confirms:
- FUN_0802DDCA = ButtonWithIcon::setBitmaps
- bitmap IDs 0xB6/0xB7 are the manual wood-burning button icon pair
- this is separate from TypedText ID 182/183
- FUN_0802EADE is the dynamic host/content switcher
- 0x0807F5EC is DATA/vtable region, not executable code

## 5. Current execution state after package inspection

The latest execution payload already sent to Gemini contains:
- complete Thumb disassembly of FUN_080480C0, 0x480C0..0x48422
- raw 96-byte span 0x7F58C..0x7F5EB

Gemini is currently performing semantic analysis of that payload.

Execution layer must not invent semantic conclusions while this branch is under Gemini analysis.

Next action:
- wait for Gemini request;
- execute requested BIN/Git extraction exactly;
- return raw results as one copyable block;
- persist substantial results to Git;
- then continue with the next requested branch.

## 6. OPEN queue

Highest priority:
1. resolver/index 0x68 source and gate;
2. exact relation of extra/boost/exhaust fan UI branch to 0x2268..0x227A;
3. parent/vtable origin of FUN_0804752C / FUN_080475A4;
4. exact equipment/configuration condition exposing extra fan;
5. complete graph/resource reuse matrix.

Then:
6. 17-row level-3 parameter binding matrix;
7. +0x3D8 callback/model binding;
8. 47290 six TypedText ID source;
9. Home indirect resource traces for bitmap IDs 115/144/174;
10. module/source/room-controller/CAN dependency graph.

## 7. Provenance

This report is a consolidation of an uploaded previous-result package. It does not replace the firmware-derived evidence. The package agrees with the current handoff on the closed IAR/LZ77 and 0x47/0x48 branches.

No contradiction was found during direct inspection of the supplied package.
