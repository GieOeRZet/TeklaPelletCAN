# TeklaPelletCAN — WHOLE-SOFTWARE MULTIPASS ANALYSIS
Data: 2026-11-20
Firmware: FW2213TK_kopia.bin
Size: 0x1F0000 = 2,031,616 B
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071
Branch: ccr-be8a1bcb-5t76j0

## 0. SCOPE CORRECTION

This pass is explicitly **not a Home-screen-only investigation**.

The Home/hopper path was used as a vertical slice because it exposed the architecture cleanly. The actual target is the **entire firmware software stack**:

BOOT → display/HAL → application/root → configuration/profile → parameter/record engine → CAN → application state → screen dispatch → TouchGFX object tree → bitmap/text/font → touch/callback → read/write → CAN/storage/side effects.

No bitmap re-extraction was repeated; the 188-resource baseline remains closed.

---

# 1. MULTIPASS PASSES EXECUTED

1. Vector table / reset / exception map.
2. Display/HAL/TouchGFX source-string scan.
3. Parameter mapper and family-of-4 analysis.
4. Record-engine structure and read/write path.
5. Full internal-ID → CAN mapping-table extraction.
6. Parameter semantic string-catalog extraction.
7. UI constructor / Bitmap-constructor cluster scan.
8. add-child / widget-tree constructor scan.
9. Bitmap descriptor table verification.
10. Common animation-engine trace.
11. Actuator index → internal parameter → panel parameter → asset range.
12. Hopper/fuel vertical trace.
13. Pump animation family 138..143 trace.
14. Mixer state family 105..107 trace.
15. Hardware/profile/device identity parameter scan.
16. Cross-check of known hypotheses against raw BIN and triage of remaining OPEN threads.

---

# 2. BOOT / MCU / DISPLAY

[FW] Vector table starts at raw 0x000000:
- initial SP = 0x20013F28
- reset vector = 0x080A3209
- handlers populate the following vector region.

[FW] Runtime addresses are based on 0x08000000 for code.

[FW] TouchGFX/display stack is directly evidenced by source strings including:
- Bitmap.cpp
- LCD16bpp.cpp
- HAL.cpp
- DMA.cpp
- Container.cpp
- Slider.cpp
- Canvas.cpp
- TypedText.hpp
- RadioButtonGroup.hpp
- WheelSelectorExtra.cpp

[FW] Panel geometry is 480×272 RGB565.

This is therefore a real STM32 TouchGFX application, not a generic bitmap UI.

---

# 3. PARAMETER / RECORD ENGINE = CENTRAL SOFTWARE BUS

[FW] The key lookup function is FUN_08036FF2(context, panel_index).

The model is:

panel index
→ current object +0x12C (instance 1..4)
→ family-of-4 resolution
→ singleton/family table
→ record lookup
→ value/descriptor

[FW] Record engine:
- registration: FUN_0801143C
- lookup: FUN_080115F6
- value access: FUN_0801167A / FUN_080116E6
- write path: FUN_08011812 via FUN_08037212
- record stride: 0x2C

[FW] Object fields:
- +0x12B = class/type
- +0x12C = active instance 1..4

This is one of the central architectural facts of the whole software.

---

# 4. INTERNAL-ID → PANEL PARAMETER TABLE

The raw table around 0x37590..0x37Cxx contains many direct internal→panel mappings.

Important closed examples:

- 0x23 → 0x216A = Burner state
- 0x24 → 0x216B = Burner storage feeder
- 0x26 → 0x216C = Burner burner feeder
- 0x27 → 0x216D = Burner igniter
- 0x28 → 0x216E = Burner blower
- 0x29 → 0x216F = Burner storage feeding time [dS]

Actuator controls:
- 0x41 → 0x2251 = Burner storage feeder
- 0x45 → 0x2252 = Burner burner feeder
- 0x46 → 0x2253 = Burner igniter
- 0x47 → 0x2254 = Burner blower
- 0x75 → 0x2276 = Grate move indicator

Fuel:
- 0x147 → 0x3601 = fuel remaining [kg]
- 0x148 → 0x3600 = tank capacity [kg]
- 0x149 → 0x3603 = fuel reserve [kg]
- 0x14A → 0x3602 = is fuel reserve
- 0x14B → 0x3604 = IN17 config
- 0x14C → 0x3607 = reserve sensor state
- 0x116 → 0x3606

Hardware/config:
- 0x112 → 0x3500 = Main module type
- 0x113 → 0x3502 = CH expansion module type
- 0x10D → 0x3505
- 0x114 → 0x3501
- 0x117 → 0x3506
- 0x121 → 0x370A = Boiler image selector
- 0x11B → 0x350B = Profile number
- 0x11C → 0x350C

CO/other runtime families:
- 0x130 → 0x3739
- 0x131 → 0x373A
- 0x132 → 0x373B
- 0x133 → 0x3722
- 0x134 → 0x3723
- 0x135 → 0x3728
- 0x136 → 0x373C
- 0x137 → 0x373D

Another direct block:
- 0x14D → 0x3511
- 0x14E → 0x3512
- 0x14F → 0x3513
- 0x150 → 0x3514
- 0x151 → 0x3515
- 0x152 → 0x3516
- 0x153 → 0x3517
- 0x154 → 0x3518
- 0x155 → 0x351B
- 0x156 → 0x351C
- 0x157 → 0x3519
- 0x158 → 0x351A

And:
- 0x159 → 0x351E
- 0x15A → 0x351F
- 0x15B → 0x3522
- 0x15C → 0x3523
- 0x15D → 0x3524
- 0x15E → 0x3520
- 0x15F → 0x3526
- 0x160 → 0x3521
- 0x161 → 0x3529
- 0x162 → 0x352A
- 0x163 → 0x3527
- 0x164 → 0x3528
- 0x165 → 0x352B

The firmware therefore contains a large, explicit protocol abstraction layer rather than scattering raw CAN IDs through UI code.

---

# 5. PARAMETER SEMANTIC CATALOG = WHOLE APPLICATION DOMAIN

The firmware string catalog around 0x24C00..0x276xx exposes the software's functional domain.

### Boiler / heating
Examples:
- Outside temperature
- Outside temperature averaged
- Boiler minimal pump temperature
- Boiler on/off hysteresis
- Boiler pressure
- Boiler temperature
- Boiler program
- Boiler on/off
- Boiler pump state
- Boiler schedule Monday..Sunday
- Boiler return temperature
- Boiler return mixer test
- Boiler mixer opening time
- CH mixer state

### Burner
- Burner external permission
- Burner state
- Burner storage feeder
- Burner burner feeder
- Burner igniter
- Burner blower
- Burner power
- Burner blower correction
- Fuel consumption
- Time to grate cleaning
- Grate full move time
- Is grate cleaning on
- Grate move indicator
- Grate cleaning number
- Storage feeder period
- Feeder rate
- Burner storage feeder test
- Burner grate test
- Igniter test
- Burner feeder test
- Burner inertia
- Grate silence mode
- Burner blower minimal/max RPM
- Burner brightness
- Burner feeder temperature
- Burner blower RPM
- Incandenscing fuel
- Grate modulation parameters
- Current burner power
- Burner feeder/storage-feeder timing
- Igniter preheat time
- Burning-off feeder work time
- Burner pause time/power/blower power

### Hot water / CWU
- Hot water 1 measured temperature
- comfort temperature
- economical temperature
- result temperature
- program
- max temperature
- heat now
- hysteresis
- source
- source delta
- min delta
- pump state
- circular pump state
- schedules Monday..Sunday
- priority
- required temperature

### External fuel storage
- motor 1/2 test
- motor 1/2 state
- level sensor state
- transport time
- overrun time
- hose empty time
- feeder work/pause
- reserve sensor
- reserve sensor state
- max cycles

### Central heating / room
- CH comfort/eco setpoints
- room measured temperature
- CH pump state/test
- room sensor type/use
- CH schedule Monday..Sunday
- manual setpoint
- room hysteresis/calibration
- correction factor
- minimum CH pump temperature
- permanent pump
- energy-saving lowering
- thermostat state
- room setpoint adjustment
- radio sensor diagnostics
- automatic summer recognition

### Buffer
- burner power depending on buffer energy
- top/bottom measured temperature
- top/bottom set temperature
- minimal pump temperature
- automatic top temperature
- T1/T2/T3
- pump delta parameters

### Solar
- solar temperatures 1..4
- water max
- alarm max/min
- solar pump state/test
- configuration
- flow and related parameters

### Configuration / maintenance / identity
- Autoconfig activation
- sensor configurations
- heating / hot-water / buffer / solar configuration
- sound alarm activation
- return sensor
- pressure sensor
- additional fuel storage
- EGT sensor type
- boiler image selector
- next/confirmed service date
- automatic time synchronization
- settings recovery
- recovery count
- PIN
- fuel counters
- statistics
- VideRoom versions

This is the evidence that the firmware contains a complete boiler-control application, not a single UI screen.

---

# 6. UI CONSTRUCTOR / WIDGET-TREE LANDSCAPE

A broad raw call scan found:
- ~180 calls to the standard Bitmap constructor FUN_0802DF08
- ~542 calls to add-child helper FUN_08030380
- ~210 direct calls to Bitmap resource setter FUN_080307BC

These counts are architectural evidence: the UI is a large object graph.

Major constructor clusters include:

- 0x02BDF0 — large root/component constructor
- 0x02C294 — major setup / hopper and other children
- 0x03242C / 0x03279C / 0x032F20 — repeated UI constructors
- 0x03C33E / 0x03C5B4 — major custom component cluster
- 0x03D19C
- 0x03E1BC
- 0x03E5AC — large Home/Main candidate root
- 0x042EEC — six-channel actuator animation aggregate
- 0x043DDC
- 0x045070
- 0x045A8C
- many 0x04Cxxx..0x04DBxx constructors forming repeated module families

This is the correct direction for reconstructing the whole UI: recover constructor → child → resource → geometry → callback rather than trying to redraw screens from screenshots.

---

# 7. HOME / MAIN IS ONLY ONE SLICE

[STRONG] FUN_0803E5AC is a large Home/Main root candidate with many subobjects:
- +0x041C
- +0x042C
- +0x84F4
- +0x8F70
- +0x92DC
- +0x963C
- +0xA26C
- +0xA5FC
- +0xA628
- +0xA654
- +0xA680
- +0xA6AC..+0xA6DC

[FW] Hopper:
- fuel remaining / capacity / reserve state are read from the parameter engine
- percentage = 100*remaining/capacity
- reserve selects bitmap 051 vs 053 on +0x5A8
- bitmap 052 is a second fixed layer on +0x5D4
- +0x960 is an intermediate parent/container-like object, exact class still OPEN.

This does NOT mean the whole software is Home. It is one vertical slice that is already unusually well traced.

---

# 8. COMMON ANIMATION ENGINE

[FW]
- FUN_0803079A: first resource +0x30, last resource +0x32
- FUN_080307AE: ticks +0x34, frame counter +0x35
- FUN_08030708: direction +0x36, enable +0x37
- FUN_08030640: advances resource +0x26 through the configured range and calls FUN_080307BC

Direction:
- 0 = first → last
- nonzero = last → first

Closed actuator channels:
- 36..38 = Burner storage feeder / fuel feeder
- 40..42 = Burner burner feeder
- 65..67 = Burner igniter
- 8..10 = Burner blower
- 58..59 = Grate move

Timing configured by 0x08042EEC:
- 36..38: 14
- 40..42: 14
- 65..67: 18
- 8..10: 6
- 58..59: 25

Index map:
- index 0 → +0x948 → 40..42
- index 1 → +0x90C → 36..38
- index 2 → +0x984 → 65..67
- index 3 → +0x9C0 → 8..10
- index 4 → +0x9FC → 58..59
- index 5 → +0xA38 → OPEN

Important correction:
The enable argument to FUN_08043954 is not uniformly the animation object's +0x37. For several channels it is stored in parent state fields first.

---

# 9. PUMP FAMILY 138..143

[FW] Repeated constructors call:
FUN_0803079A(object, 0x8A, 0x8F)

That is decimal:
138..143.

Observed in multiple constructor families:
- 0x0424EC
- 0x044AB8
- 0x045070
- 0x04C410
- 0x04C78C
- 0x04CA94
- 0x04CD9C
- 0x04D00C
- 0x04D320
- 0x04D634
- 0x04D948

[STRONG] This is a shared six-frame pump animation family instantiated in multiple screens/components. Exact CO/CWU/Home membership is still OPEN.

---

# 10. MIXER FAMILY 105..107

[FW]
- 105 is base resource.
- FUN_0803C550(state) selects:
  - state 1 → 106
  - state 2 → 107
  - otherwise → 105.
- upstream caller uses panel parameter/internal ID 0x29.

[OPEN] Which of states 1/2 corresponds exactly to OPEN/CLOSE still requires the semantic value table/runtime branch.

---

# 11. HOPPER / FUEL

[FW] Exact path:

internal 0x147 → CAN 0x3601 = remaining
internal 0x148 → CAN 0x3600 = capacity
internal 0x14A → CAN 0x3602 = reserve flag

percentage = 100*remaining/capacity

→ FUN_0802DA54(context, percentage, reserve_flag)

FUN_0802DA54:
- reserve=0 → resource 0x33 / bitmap 051
- reserve!=0 → resource 0x35 / bitmap 053
- bitmap 052 is fixed second layer on +0x5D4
- refreshes the relevant child objects.

[CORRECTION]
+0x5DA/+0x5DE must not be called crop/progress fields yet. They are part of the extended object region and interact with the common animation/object methods, but exact semantics remain OPEN.

---

# 12. DEVICE / HARDWARE VARIANTS

[FW]
The application has explicit identity/configuration inputs:
- 0x3500 Main module type
- 0x3502 CH expansion module type
- 0x350B Profile number
- 0x370A Boiler image selector
- 0x3664 software version
- 0x3665 igneTouch boiler short name
- 0x2125 Device type
- 0x2105 Heating configuration

The code contains branching based on hardware/profile state.

[STRONG]
Hardware profile, heating configuration, boiler image selection, and CO instance count are separate concepts. Do not collapse them into one selector.

---

# 13. THE SOFTWARE IS LARGER THAN THE CURRENT UI TRACE

The recovered parameter catalog alone shows these major software domains:

1. Boot / MCU / display
2. TouchGFX framework
3. Application/root
4. Parameter mapper
5. Record database
6. CAN mapping
7. Boiler core
8. Burner state machine
9. Fuel storage / hopper
10. Burner feeder
11. Grate
12. Igniter
13. Burner blower
14. CH / CO1..CO4
15. CWU / hot water
16. External fuel storage
17. Buffer
18. Solar
19. Sensors
20. Schedules
21. Statistics
22. Service/maintenance
23. Hardware configuration
24. Device identity / variant
25. Alarm/configuration infrastructure
26. Touch/UI navigation
27. Bitmap/TypedText/font resources
28. Animation engine
29. Touch/callback/write path
30. persistence/settings recovery

This is now the scope of the project.

---

# 14. OPEN THREADS — PRIORITY FOR WHOLE-SOFTWARE RECONSTRUCTION

## P1 — Screen dispatch / application navigation
Recover:
screen selector → constructor/object → active widget tree → touch callback → next screen.

## P2 — Home/Main complete tree
Close:
3E5AC → children → exact resources → geometry → visibility → callbacks.

## P3 — CO1..CO4 screen family
Close:
3E714 → parameter IDs → widget records → exact instance-specific geometry/state.

## P4 — CWU family
Use repeated 138..143 pump constructors to identify the complete CWU screen/component chain.

## P5 — Burner/service family
Trace 216A..216F and 2251..2254/2276 from parameter read → UI state → animation.

## P6 — 130..137
User semantics say four ON/OFF icons; firmware trace must close exact positions and state resources.

## P7 — 160/161
Close configuration/settings button and callback path.

## P8 — 39 + 168/169
Identify the exact UI component and screen.

## P9 — 60/61, 43/44, +A38/index 5
Find resource writers and upstream parameter/state.

## P10 — 370A
Close:
370A → selector/branch → resource ID → BitmapData → widget → geometry.

## P11 — WheelSelectorExtra
Close:
38CF4 → vptr → vtable → methods → extraText → real widget instances.

## P12 — touch/write side
For each major screen:
touch → callback → parameter ID → instance → FUN_08037212 → record → CAN/storage.

---

# 15. RULE FOR THE NEXT PASSES

Do not produce isolated discoveries.

For every module, seek the vertical chain:

source/constructor
→ vptr/class
→ object instance
→ child/widget
→ resource
→ X/Y/W/H
→ visibility/state
→ callback/touch
→ panel parameter
→ instance mapping
→ record
→ CAN/storage
→ side effect.

The target is the **whole original software**, reconstructed from the binary, not one pretty screen.

