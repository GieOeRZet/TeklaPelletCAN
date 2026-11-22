# MULTIPASS-19-0x68-RESOLVER-CORRECTION-2026-11-20

## Scope

Deep firmware-only continuation of the extra-fan/blower branch. This pass specifically attacked resolver index 0x68, the direct UI branch FUN_08043A36, the parameter registry behind FUN_08036FF2, the writer path, and the graph dispatcher.

Firmware:
FW2213TK_kopia.bin
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

## Critical correction

The previous working note treated resolver index 0x68 as an unresolved generic configuration gate.

That is now CLOSED at the parameter-ID level:

FUN_08036FF2 maps internal resolver index:
0x68 -> parameter ID 0x300B

The mapping is in the resolver's second table at raw 0x37794:

0x68 -> 0x300B
0x97 -> 0x370C
0x98 -> 0x300E
0x99 -> 0x3713
0x9A -> 0x3714

[ERRATA PASS 35: baza tabeli 1 to RAW 0x37B48 (49 rekordów, PID = baza + instancja - 1); 0x37B36 było błędne]
The first resolver table at raw 0x37B36 is a separate mapping table and must not be confused with this second table.

## Parameter meaning

Repository register catalogue cross-check:
0x300B = Stop burning wood
type u8
range 0..1
current/recorded raw value 257 corresponds to value 1.

This is independently represented in:
rejestry/REJESTRY.md
rejestry/katalog-rejestrow.csv
rejestry/panel-fw-parametry-FW2213TK.csv
rejestry/snap-197-nazwy-FW2213TK.csv

Firmware itself defines/registers 0x300B in the parameter-definition code around raw 0x58DE:
MOVW r1,#0x300B
BL FUN_0801143C

## Direct UI consequence

FUN_08043A36 receives the resolved value from index 0x68 and performs:

if value == 1:
  TypedText 182 = "Podajnik palnika"

else:
  TypedText 183 = "Wentylator wspomagający [%]"

The direct code is:

08043A36:
  compare r1 with 1
  equal -> 0xB6 / TypedText 182
  non-equal -> 0xB7 / TypedText 183

Then it builds the label object at parent + 0xF74.

Thus the branch is NOT itself proof of "extra fan enabled/disabled".

It is a label variant controlled by parameter 0x300B, whose firmware/register meaning is Stop burning wood.

## Additional hard structure around +0xF74

A large constructor around raw 0x3CE... explicitly initializes parent+0xF74 via FUN_0802DD76.

Another constructor around raw 0x11ACC initializes parent+0xF74 as a typed value object.

FUN_08043A36 uses:
parent + 0xF74
and calls FUN_0802DDCA with text IDs 168/169 and 182/183.

The exact semantic parent/screen of this object is still OPEN.

## Writer-side evidence

A firmware function around raw 0x31CCC writes parameter index 0x68 through FUN_08037212:

[r4+0x8] context
r2 = 1
r1 = 0x68
BL FUN_08037212

Therefore the firmware has a real write path for the same internal resolver index.

Because 0x68 -> 0x300B, this is a firmware-native write path for Stop burning wood.

The surrounding function also handles many other configuration values, so do not label the entire function as an "extra fan setup" routine without further caller/context proof.

## Graph branch remains separate and valid

FUN_0803EC18 still hard-resolves the five-point graph families:

panel/index 0x4A..0x4E:
  0x4A -> 0x2261
  0x4B -> 0x2262
  0x4C -> 0x2263
  0x4D -> 0x2264
  0x4E -> 0x2265

panel/index 0x4F..0x53:
  0x4F -> 0x2268
  0x50 -> 0x226E
  0x51 -> 0x226F
  0x52 -> 0x2275
  0x53 -> 0x227A

The graph dispatcher is invoked from:
FUN_08048624 -> FUN_0803EC18
FUN_0807EB36 -> FUN_0803EC18

These callers iterate registered child/panel objects; FUN_0803EC18 is therefore a generic refresh/dispatcher, not proof that the graph is the same object as the 0x68 label branch.

## Panel registry evidence

FUN_0803EC18 searches a table beginning at raw 0x3F008 with 0x10-byte records.

Relevant records:

panel 0x47:
  secondary field 0x8E
  type byte 5
  pointer 0x0807F5EC
  final byte 1

panel 0x48:
  secondary field 0x7E
  type byte 5
  pointer 0x0807F5EC
  final byte 1

For panel 0x47 or 0x48, FUN_0803EC18 constructs five graph point values and calls FUN_08048520.

The exact semantic names of panel IDs 0x47/0x48 are still OPEN. Do not equate them to the TypedText titles of unrelated constructors merely because numeric IDs appear nearby.

## Important architectural conclusion

There are now three separate facts:

1. 0x300B / Stop burning wood controls a label variant:
   Podajnik palnika vs Wentylator wspomagający [%].

2. 0x2261..0x2265 are a five-point blower characteristic family.

3. 0x2268/0x226E/0x226F/0x2275/0x227A are a second five-point exhaust/extra-fan characteristic family.

The first does NOT yet prove the gate for the second.

The user's hypothesis that different boiler configurations may expose different fan-related screens remains valid as a hypothesis, but the specific 0x68 branch is now known to be 0x300B/Stop burning wood.

## Next attack

P0:
1. Resolve exact semantic identities of panel IDs 0x47 and 0x48.
2. Trace pointer 0x0807F5EC and its callers/constructor.
3. Determine whether panel 0x47 is blower graph and 0x48 exhaust graph, or another shared graph content.
4. Trace all references to parameter IDs 0x2261..0x2265 and 0x2268..0x227A through the model/update layer.
5. Find the actual configuration gate for the extra/boost fan screen.
6. Trace 0x300B from UI writer -> model -> CAN/record, independently from graph branch.
7. Recover parent/screen of +0xF74 and exact geometry.

## Confidence

HARD:
- 0x68 -> 0x300B
- 0x300B = Stop burning wood
- 0x68 is read by FUN_08043A36
- 0x68 is written through FUN_08037212
- 182/183 are selected directly by value 1/non-1
- graph families and their resolver indices
- panel 0x47/0x48 registry records

OPEN:
- exact semantic screen for 0x47/0x48
- exact gate for extra fan characteristic
- exact parent/geometry of +0xF74
- exact model/CAN path for 0x300B

REJECTED:
- "resolver 0x68 is the extra-fan enable gate" as a current claim.
