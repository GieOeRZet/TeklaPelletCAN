# TeklaPelletCAN — RESET SCOPE: ORIGINAL IGNEO TOUCH SOFTWARE SPECIFICATION
Data: 2026-11-20

## 0. CRITICAL SCOPE RESET

The target of this project is NOT the existing TeklaPelletCAN card/engine.
The existing card may be reused later only as a low-level browser/HA rendering or transport scaffold if useful. It is not a source of truth for configuration, screen availability, menu structure, dependencies, state logic, parameter relationships, write behavior, animations, module detection, buffer/solar/cascade behavior.
The source of truth is the original FW2213TK_kopia.bin, with external Estyma documentation used only as corroboration. Any behavior that exists only in the current TeklaPelletCAN software is provisional and must not be promoted to the reconstructed original.
The previous original-Touch Home layer is legacy/prototype, not the target implementation. In particular, a simple one-configuration Home renderer must not define the final architecture.

## 1. TARGET

Reconstruct the complete original Estyma/igneoTouch software behavior so that one card can render the correct installation dynamically:
- 0..4 CO circuits
- CWU present/absent
- buffer present/absent
- solar present/absent
- cascade master/slave state
- additional fuel storage present/absent
- external/room/outside/return/pressure/lambda/energy sensors
- hardware/module/profile differences
- menu access level
- alarm/service/statistics/configuration branches
- original touch/write semantics
- original animation/resource selection.
The user does not need to own every possible installation. The implementation must be derived from firmware so that it can be tested against synthetic configuration matrices and later real HA data.

## 2. SOURCE PRIORITY

1. [FW] direct evidence from FW2213TK_kopia.bin
2. [DATA] extracted binary tables/assets
3. [DOC] official Estyma/igneoTouch documentation
4. [STRONG] inference supported by multiple independent firmware paths
5. [OPEN] unresolved hypothesis
The existing TeklaPelletCAN JavaScript is not a source of truth.

## 3. MULTIPASS WORK COMPLETED IN THIS RESET

### PASS 01 — Current implementation audit
Confirmed that the current card/engine contains many hand-authored assumptions and a fixed screen model. It cannot be used as the behavioral specification.

### PASS 02 — Firmware size/integrity
Firmware: size 0x1F0000 = 2,031,616 bytes; SHA-256 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071.

### PASS 03 — TouchGFX architecture
Firmware contains direct TouchGFX source references: Bitmap.cpp, LCD16bpp.cpp, HAL.cpp, DMA.cpp, Container.cpp, Slider.cpp, Canvas.cpp, TypedText.hpp, WheelSelectorExtra.cpp. Panel geometry is 480x272 RGB565.

### PASS 04 — Bitmap database
188 bitmap resources are closed. Descriptor table file offset 0x54450; 20-byte TouchGFX BitmapData records; RGB565 + optional A8; payload mapping file_offset = runtime_pointer - 0x08010000. This asset database is original firmware data and must be reused by the new renderer.

### PASS 05 — Internal -> panel parameter mapping
The firmware contains a large explicit mapping table around 0x37580..0x37Bxx.
Important examples:
- 0x10E -> 0x2105 = Heating configuration
- 0x10F -> 0x2106 = Hot water configuration [STRONG]
- 0x110 -> 0x2108 = Solar configuration [STRONG]
- 0x111 -> 0x2107 = Buffer configuration [STRONG]
The 2105..2108 sequence is registered consecutively at 0x0800A5A2..0x0800A6D0 and matches the firmware configuration-string catalog order: Heating, Hot water, Buffer, Solar. The selector logic in FUN_0803C178 independently corroborates 0x10F as the hot-water gate, 0x110 as the solar gate and 0x111 as the buffer gate.
- 0x112 -> 0x3500 = Main module type
- 0x113 -> 0x3502 = CH expansion module type
- 0x114 -> 0x3501
- 0x115 -> 0x2123
- 0x116 -> 0x3606
- 0x117 -> 0x3506
- 0x118 -> 0x3508
- 0x119 -> 0x3509
- 0x11A -> 0x350A
- 0x11B -> 0x350B = Profile number
- 0x11C -> 0x350C
- 0x11D -> 0x350D
- 0x11E -> 0x3707
- 0x11F -> 0x3629
- 0x120 -> 0x362B
- 0x121 -> 0x370A = Boiler image selector
- 0x122 -> 0x3525
Fuel: 0x147 -> 0x3601, 0x148 -> 0x3600, 0x149 -> 0x3603, 0x14A -> 0x3602, 0x14B -> 0x3604, 0x14C -> 0x3607.

### PASS 06 — Configuration string catalog
Firmware strings explicitly contain: Autoconfig activation; Outside temperature sensor configuration; Heating configuration; Hot water configuration; Buffer configuration; Solar configuration; Lambda module presence; Is this device cascade master; Pressure sensor; Additional fuel storage; Energy meter type; Profile number; Main module type; CH expansion module type.
This proves that configuration is a first-class firmware domain, not an invention of the card.

### PASS 07 — Heating configuration dependency
Internal 0x10E is read repeatedly and compared against values 1..4.
Examples: 0x08031E6E compares against 1; 0x08031E92 compares against 2; 0x08031FAA and 0x08031FC2 compare against 1/2; 0x08032130 checks 0x10E >= 1; 0x08032150 checks 0x10E >= 2; 0x0803C1AC..0x0803C1EC uses 0x10E against 1,2,3,4.
Therefore the original UI/application has real installation-dependent branching for heating configuration.

### PASS 08 — Dynamic parameter selection
FUN_0803C178 reads a runtime table at RAM 0x20005EF0 and maps selector values to internal parameters: selector 6 -> 0x110; 7 -> 0x111; 5 -> 0x10F; 8 -> 0x11C; 1..4 -> 0x10E; 9 -> 0x122.
It then checks the selected configuration parameter and returns a boolean visibility/eligibility result. This is direct evidence that original UI rows are dynamically enabled/disabled from configuration. In particular, selector 5 is gated by 0x10F (CWU), selector 6 by 0x110 (solar), selector 7 by 0x111 (buffer), while selectors 1..4 are gated by 0x10E (heating configuration / CO count).

### PASS 09 — Profile normalization
The firmware contains explicit profile state: internal 0x11B, panel 0x350B. Profile is independent from boiler image, module type and heating configuration.

### PASS 10 — Hardware/module identity
Separate firmware inputs exist for main module type, CH expansion module type, profile, heating configuration, boiler image selector, device type, software version and short name. These must remain separate in the new software.

### PASS 11 — Official Estyma configuration corroboration
Official igneoTouch documentation describes configuration controls including automatic configuration, main I/O module, number of heating circuits, outside sensor, hot water, solar, buffer, lambda, fuel reserve sensor, fuel capacity/reserve, return sensor, profile number, boiler pump mode, cascade master, pressure sensor, additional fuel storage and energy measurement.
Firmware remains authoritative for exact behavior of this firmware revision.

### PASS 12 — Official profile corroboration
Estyma documentation describes Profile 1 = CO + CWU + Buffer; Profile 2 = CO1 + CO2 + CWU; Profile 3 = CO1 + CO2 + CWU + Buffer. The firmware separately stores profile number and other configuration values.

### PASS 13 — Menu structure corroboration
Original igneoTouch documentation lists Kocioł, Palnik, Ogrzewanie obwód 1..4, Ciepła woda użytkowa, Solary, Bufor, Historia alarmów, Informacje o programie, Poziom menu/PIN, Język, Alarm dźwiękowy, Konfiguracja, Test wyjść and Statystyki. Submenus include status/settings/schedules for applicable modules.
The final card must not hard-code all of these as always-present. Firmware configuration decides which are actually applicable.

### PASS 14 — Access levels
Official documentation confirms multiple menu access levels and that parameters are hidden depending on access level. Firmware also contains PIN/menu-level infrastructure. Visibility therefore has at least two independent gates: installation capability AND access level.

### PASS 15 — Burner animation/state
Closed firmware actuator map: index 0 / resources 40..42 = burner feeder; index 1 / 36..38 = storage/fuel feeder; index 2 / 65..67 = igniter; index 3 / 8..10 = blower; index 4 / 58..59 = grate movement; index 5 / +A38 unresolved.
Timing: 36..38 = 14; 40..42 = 14; 65..67 = 18; 8..10 = 6; 58..59 = 25.

### PASS 16 — Pump animation
Repeated firmware constructors instantiate resources 138..143 as a common six-frame pump animation across multiple component/screen families. This must become a reusable original animation component whose visibility depends on the relevant module.

### PASS 17 — Mixer animation
Firmware: base resource 105; state 1 -> 106; state 2 -> 107. Exact semantic direction of states 1/2 remains OPEN until the state-value chain is closed.

### PASS 18 — Hopper/fuel vertical slice
Closed: 0x147 -> 0x3601 fuel remaining; 0x148 -> 0x3600 capacity; 0x14A -> 0x3602 reserve flag. Percentage = 100 * remaining / capacity. FUN_0802DA54: reserve 0 -> bitmap 051; reserve nonzero -> bitmap 053; bitmap 052 is a second fixed layer.
The current card's percentage thresholds are therefore not the original firmware behavior and must not be treated as specification.

### PASS 19 — Whole-application domain
The parameter catalog covers boiler, burner, fuel storage, external fuel storage, CO1..CO4, CWU, buffer, solar, cascade, sensors, schedules, statistics, service, configuration, identity, alarms and persistence.

### PASS 20 — Architecture decision
The correct architecture is now fixed:
Original firmware parameter model -> Original installation/configuration resolver -> Original screen/menu visibility resolver -> Original screen state model -> Original widget/resource tree -> Original touch/callback/write mapping -> HA adapter -> rendering backend.
The existing TeklaPelletCAN engine may be reused only as a rendering/DOM/HA transport substrate where it does not impose behavior.

## 4. REQUIRED FINAL CONFIGURATION MODEL

### Installation
- heating configuration / number of CO circuits
- hot water configuration
- buffer configuration
- solar configuration
- outside sensor configuration
- lambda module presence
- return sensor
- pressure sensor
- fuel reserve sensor
- additional fuel storage
- energy meter type
- cascade master/slave state
- profile number
- main module type
- CH expansion module type
- boiler/device type
- boiler image selector

### Runtime
- boiler state/temperature/setpoint/program
- burner state and actuators
- fuel remaining/capacity/reserve
- CO1..CO4 measured/set temperatures and pump/mixer states
- CWU measured/set temperature/pump/priority/schedule
- buffer temperatures/energy/pump
- solar temperatures/power/flow/pump/status
- cascade state/power/slaves
- alarms
- service/maintenance
- statistics

### UI gates
Every screen/tile/row must be controlled by: installation capability, active instance, access level, runtime availability/validity and firmware state.

## 5. NO MORE ONE-CONFIGURATION ASSUMPTION

The final card must be able to render at least these synthetic installations without code changes:
A. CO1 only
B. CO1 + CWU
C. CO1 + CO2 + CWU
D. CO1 + CO2 + CWU + Buffer
E. CO1 + CO2 + CO3 + CO4 + CWU
F. CO1..CO4 + CWU + Buffer + Solar
G. same as F + additional fuel storage
H. same as F + cascade master
I. profile variants with different main/expansion modules
J. reduced-access user level
K. installer/service level
The user's personal installation is irrelevant to the software specification.

## 6. WHAT MUST NOT BE DONE AGAIN

Do NOT copy the current TeklaPelletCAN menu and call it original. Do NOT keep fixed CO/CWU tiles and merely gray them out. Do NOT assume CWU, buffer or solar always exist. Do NOT assume one or two CO circuits. Do NOT invent a config field in Lovelace YAML as the source of installation truth. Do NOT map arbitrary HA entities directly to screen positions. Do NOT use guessed parameter IDs. Do NOT use current engine labels as firmware semantics. Do NOT infer screen behavior from one screenshot. Do NOT use current _main() as the original Home implementation.

## 7. NEXT REVERSE-ENGINEERING PASSES

1. Close exact internal IDs for every configuration string: Hot water configuration, Buffer configuration, Solar configuration, Lambda module presence, Cascade master, Pressure sensor, Additional fuel storage, Energy meter type, etc.
2. Recover the original configuration-screen widget tree.
3. Recover the screen/menu dispatcher.
4. Recover Home/Main complete tree and all installation-dependent branches.
5. Recover CO1..CO4 family and instance selection.
6. Recover CWU family and presence/absence gate.
7. Recover Buffer family and presence/absence gate.
8. Recover Solar family and presence/absence gate.
9. Recover cascade family and master/slave branching.
10. Recover external/additional fuel-storage family.
11. Recover access-level visibility matrix.
12. Recover all touch -> parameter -> record -> CAN/storage write paths.
13. Build a machine-readable capability matrix from the firmware.
14. Build a synthetic configuration test harness covering all combinations.
15. Only after the behavioral model is closed, replace the current card renderer with the reconstructed screen system.

## 8. ACCEPTANCE CRITERION

Given firmware-equivalent configuration values, the card must produce the same available screens, widgets, values, animations and write actions as the original igneoTouch. The current TeklaPelletCAN software is never the authority for deciding what those values mean.