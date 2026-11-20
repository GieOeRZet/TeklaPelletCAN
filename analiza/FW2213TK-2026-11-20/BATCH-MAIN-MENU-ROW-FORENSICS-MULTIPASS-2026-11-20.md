# TeklaPelletCAN — MAIN MENU ROW FORENSICS / MULTIPASS
Date: 2026-11-20
Firmware: FW2213TK_kopia.bin
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

## PASS 01 — raw table parse

Table @ 0x42348, 21 records x 6 bytes:

index selector bitmap_A bitmap_B
0 0 60 83
1 10 61 85
2 1 62 86
3 2 63 86
4 3 64 86
5 4 65 86
6 5 66 88
7 6 71 87
8 7 67 84
9 8 70 82
10 9 69 99
11 11 72 78
12 13 74 89
13 17 77 159
14 15 76 96
15 0 12 73
16 90 14 75
17 97 18 78
18 100 16 79
19 98 19 80
20 95 20 81

[FW][CLOSED]

## PASS 02 — loop-consumption proof

Constructor @ 0x42160:
- r5=15 at 0x421da
- first loop tests r4 < 15
- first loop consumes records 0..14
- r9 starts at 0x42348 and advances +6
- second loop again uses count 15
- r10 starts at 0x42346 and is advanced +6
- therefore the same first 15 records are used by the two passes.

The six trailing records 15..20 are NOT consumed by these loops.

[FW][CLOSED]

## PASS 03 — second-pass pointer alignment

r9 = 0x42348.
r10 = 0x42346.

First pass:
- selector = [r9+0]
- bitmap_A = [r9+2]
- bitmap_B = [r9+4]

Second pass:
- selector = [r10+2]
- bitmap_A = [r10+4]
- r10[0] is an additional byte test.

Thus r10 is deliberately positioned two bytes before the first record so the second pass sees selector/bitmap_A from the same records while also testing a preceding byte.

This is strong evidence for a two-phase row construction/state overlay, not a second 6-record continuation.

[FW][STRONG]

## PASS 04 — row builder input

FUN_0804BC6C receives:
- r0 = row object
- r1 = bitmap_A
- r2 = bitmap_B

It:
- creates/updates child at +0x8C using r1,
- creates/updates child at +0x60 using r2 when r2 != 0xFFFF,
- performs resource/geometry recomputation through FUN_080313A4 / FUN_08030358 / related vtable calls.

Therefore the two bitmap IDs are two separate row layers/components, not a single bitmap choice.

[FW][CLOSED]

## PASS 05 — A/B visual role cross-check

Direct RGB565 extraction of the firmware assets shows:

selector 0:
- A60 = circular-arrow/state symbol
- B83 = boiler/cabinet-like menu symbol

selector 10:
- A61 = alternate circular-arrow/state symbol
- B85 = flame/burner symbol

selectors 1..4:
- A62..65 = distinct state/indicator graphics
- B86 = common radiator/heating symbol

selector 5:
- A66 = glowing heater/rod state graphic
- B88 = faucet/CWU symbol

selector 6:
- A71 = thin line/state element
- B87 = solar-panel symbol

selector 7:
- A67 = glowing bar/actuator state graphic
- B84 = buffer/tank symbol

selector 8:
- A70 = rotary/actuator graphic
- B82 = multi-module/cascade-like symbol

selector 9:
- A69 = rotary/actuator graphic
- B99 = additional-storage/room-like symbol

selector 11:
- A72 = small red tank/indicator
- B78 = alarm-history document + warning symbol

selector 13:
- A74 = tank/cabinet graphic
- B89 = information symbol

selector 17:
- A77 = menu-bars graphic
- B159 = gears/configuration symbol

selector 15:
- A76 = neutral background/plate
- B96 = user + lock symbol

This strongly separates A = state/selection/decoration layer from B = semantic menu icon.

[DATA][STRONG]

## PASS 06 — trailing six asset-family test

Trailing records:

0:(12,73)
90:(14,75)
97:(18,78)
100:(16,79)
98:(19,80)
95:(20,81)

Visual extraction:

12 = large red Tekla boiler image, 108x141
14 = tall grey cabinet/boiler image, 54x100
18 = small vertical white device/tank image, 30x30
16 = narrow vertical white element, 20x34
19 = neutral rounded-square plate, 30x31
20 = checkmark tile, 30x31

73 = 68x75 tank-like panel
75 = 68x75 neutral tank/cabinet panel
78 = 39x50 alarm-history icon
79 = 480x45 long horizontal bar
80 = 440x1 horizontal line
81 = 440x50 long horizontal bar

These are qualitatively different from the first 15 menu-row icon pairs. In particular, 79/80/81 are wide bars/lines rather than menu icons.

Therefore the six trailing records should NOT be treated as six more ordinary rows of the same main-menu widget family.

[DATA][STRONG]

## PASS 07 — duplicate selector 0

There are two selector=0 records:
- first: 0:(60,83)
- trailing: 0:(12,73)

Because they belong to different asset families and only the first is consumed by the 0x42160 loops, the duplicate selector is not evidence of two ordinary Kocioł rows.

The second selector=0 is currently an unresolved secondary context/resource configuration.

[FW][DATA][STRONG]

## PASS 08 — semantic mapping of first 15 selectors

The B-layer icons independently support:

0 = Kocioł / boiler
10 = Palnik / burner
1 = CO1
2 = CO2
3 = CO3
4 = CO4
5 = CWU
6 = Solar
7 = Buffer
8 = Cascade
9 = Additional fuel storage
11 = Alarm history
13 = Program information
17 = Configuration
15 = Menu level/PIN

The configuration resolver directly gates 1..9, so these are not merely labels:
1..4 -> 0x2105
5 -> 0x2106
6 -> 0x2108
7 -> 0x2107
8 -> 0x350C
9 -> 0x3525

[FW][DATA][STRONG]

## PASS 09 — menu ordering of the proven first group

The proven selector order for this constructor is:

Kocioł
Palnik
CO1
CO2
CO3
CO4
CWU
Solar
Buffer
Cascade
Additional fuel storage
Alarm history
Program information
Configuration
Menu level/PIN

This is a 15-entry first group.

Do NOT append Language, Sound alarm, Output test, Statistics, Network to this group until their consumer/context is independently closed.

[FW][DATA][CLOSED for first group]

## PASS 10 — access-level relation

The constructor copies model +0x158 at 0x421dc into an object byte at r6+r7. If nonzero, it performs a second pass over the same 15 records.

This proves that access level changes row construction/state processing, but the exact visual effect of that second pass is still OPEN.

Do not simplify this to "level > 0 simply shows/hides rows."

[FW][STRONG]

## PASS 11 — special second-pass marker

After the second-pass row builder call, code checks r10[0] against 0x0C and 0x0E and changes row fields at +0xE9 / +0x11D.

This suggests special row-state handling encoded outside the selector field, but the exact meaning of 0x0C/0x0E is OPEN.

[FW][OPEN]

## PASS 12 — string catalog sanity check

Firmware UTF-16 string extraction contains exact menu labels such as:
- Kocio
- OGRZEWANIE 1..4
- Historia alarmów
- Informacje o programie
- Poziom menu (PIN)
- KONFIGURACJA
- TEST WYJ
- STATYSTYKI
- Network

These corroborate the semantic mapping but are not used to override the raw selector/consumer evidence.

[DATA][STRONG]

## PASS 13 — configuration matrix

The resolver-level configuration space is:
Heating 0..4 x five binary capabilities (HW, Solar, Buffer, CascadeMaster, AdditionalStorage) = 160 synthetic installation states.

At resolver layer:
- minimum visible entries from the 21-record selector vector = 12
- maximum = 21

But this count is only a selector-level mathematical result. It is NOT a claim that one screen renders 21 rows. The 0x42160 constructor consumes 15 records only.

[FW][DATA]

## PASS 14 — contradiction search

Contradiction found and corrected:
Previous interpretation: all 21 records = one 21-row main menu.
Current evidence: constructor loops are exactly 15.

The previous claim is withdrawn.

No contradiction remains for the first 15 records.

[FW][CLOSED correction]

## PASS 15 — implementation consequence

The final ESP implementation must model the menu as at least:

A) proven 15-entry first group owned by constructor @0x42160,
B) separate unresolved resource group containing selectors 0/90/97/100/98/95.

Do not merge groups merely because they are contiguous in flash.

## PASS 16 — next reverse-engineering attack

1. Trace where the six trailing records are referenced at runtime, including indirect table-pointer construction.
2. Trace FUN_0804BC6C's exact child classes/vtables and geometry.
3. Trace the callback/navigation path for the 15 proven selectors.
4. Determine the exact second-pass effect of access level.
5. Map the six trailing selectors to their actual screen/context only after a consumer is found.
6. Map +0x158 thresholds to concrete screen families.

## Status

Closed:
- raw 21-record table
- first-15 consumption
- two-pass structure
- A/B resource roles
- first-15 semantic selector mapping
- configuration gates
- access code mapping from prior batch

Open:
- trailing six consumer
- exact row geometry/class tree
- touch/navigation callbacks
- second-pass access visual effect
