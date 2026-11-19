# BATCH — RAW MULTIPASS: INTERNAL 0x121 → 0x370A → 0x20021FA6 → UI → BITMAP 11..13
Data: 2026-11-19

## 0. Wynik

[FW] Raw BIN closes the previously open Boiler image selector chain:

internal 0x121
 -> FUN_08036FF2
 -> mapping table around 0x08037934
 -> 0x121 -> 0x370A
 -> FUN_08037094
 -> FUN_080115F6
 -> runtime record for 0x370A
 -> record +0x0C backing-storage pointer
 -> 0x20021FA6
 -> current u8 value
 -> FUN_0803CB04
 -> FUN_0803CACC
 -> resource ID = value + 10
 -> FUN_080307BC(bitmap_child, resource_id)

## 1. 0x121 -> 0x370A

Raw table contains the exact pair:
0x08037984: 0x0121
0x08037986: 0x370A

[FW] internal model/index 0x121 is the runtime representation of external parameter 0x370A.

Same table independently proves:
- 0x158 -> 0x351A (Cascade slaves number)
- 0x11C -> 0x350C (Cascade master flag)

Therefore 0x158/0x11C must stay on the cascade branch.

## 2. FUN_08036FF2 is the generic index resolver

FUN_08036FF2(context, panel_index):
- reads object +0x12C;
- searches the mapping table;
- finds 0x121 -> 0x370A;
- combines mapped external ID with the instance component;
- passes the resolved external ID to FUN_08037094.

[STRONG] This is the hard bridge between the internal UI/model index namespace and the external parameter namespace.

## 3. FUN_08037094 -> FUN_080115F6

FUN_08037094 passes the resolved external ID to FUN_080115F6, then uses FUN_08014734 to extract the typed value.

FUN_080115F6 searches runtime records with stride 0x2C. The critical fields are:
- +0x08 = external/CAN index;
- +0x0C = backing storage pointer;
- +0x10 = type.

At the found record it loads [record+0x0C], dereferences that pointer, and returns the current value plus type information.

## 4. 370A registration -> exact RAM

Raw registration sequence for 370A:
movw r0,#0x16BA
adds r2,r4,r0
movw r1,#0x370A
...
BL FUN_0801143C

Inside FUN_0801143C:
- record +0x08 receives external ID;
- record +0x0C receives r2, the backing-storage pointer;
- record +0x10 receives the type.

Thus 370A record +0x0C = r4 + 0x16BA.

Raw BIN also contains the configuration base literal:
0x200208EC

Therefore:
0x200208EC + 0x16BA = 0x20021FA6

[FW] This closes the exact storage bridge without any direct MOVW/MOVT reference to 0x20021FA6.

## 5. 0x0801AB7E is withdrawn from the runtime path

Raw inspection of 0x0801AB7E shows pixel/table-like data, not executable Thumb code.

More importantly, the complete 370A runtime chain above reaches 0x20021FA6 through the record engine and never uses 0x0801AB7E.

[CORRECTION] Do not call 0x0801AB7E a 370A callback, do not put it into the 0x2C record layout, and do not use it as the 370A -> UI bridge.

Its separate data/resource provenance remains OPEN.

## 6. UI callsite proves internal 0x121 drives the visual component

At FUN_0803CB04 around 0x0803CBDA:

ldr r0,[r4,#0x8]
movw r1,#0x121
BL FUN_08036FF2
UXTB r1,r0
ldr r0,[r4,#0xC]
BL FUN_0803CACC

[FW] The visual component directly requests internal parameter 0x121.

## 7. FUN_0803CACC is the variable Bitmap/resource selector

Raw function:

0803CACC:
  adds r1,#0xA
  strh r1,[sp]
  addw r0,r0,#0x85C
  mov r1,sp
  BL FUN_080307BC

Therefore:
- resource_id = 370A_value + 10;
- bitmap object = UI parent + 0x85C;
- FUN_080307BC writes that resource ID.

This is direct raw proof, not inference from asset numbering.

## 8. Exact selector mapping is now CLOSED

370A is a u8 Boiler image selector with range 1..3.

Code adds 10 before calling the Bitmap/resource writer.

| 370A | resource ID |
|---:|---:|
| 1 | 11 |
| 2 | 12 |
| 3 | 13 |

[FW] The previously suspected 1->011, 2->012, 3->013 mapping is now proven by executable code.

Resource ID 14 remains separate: FUN_080469E8 independently constructs a Bitmap child with fixed ID 14. Do not merge that path with 370A.

## 9. Current architecture

Boiler image selector:

0x370A
  -> internal 0x121
  -> FUN_08036FF2
  -> mapping table
  -> FUN_08037094
  -> FUN_080115F6
  -> record +0x0C
  -> 0x20021FA6
  -> u8 1..3
  -> FUN_0803CB04
  -> FUN_0803CACC
  -> +10
  -> FUN_080307BC
  -> Bitmap object +0x85C
  -> resource 11..13

Separate cascade path:

0x351A / 0x350C
  -> FUN_0803E45C
  -> FUN_08047040
  -> four 469E8 composites
  -> fixed resource 14

## 10. Still open

1. Identify the exact C++ class/vtable behind FUN_0803CB04.
2. Identify the constructor/parent object containing Bitmap child +0x85C.
3. Recover direct BitmapData/resource-table proof for resource IDs 11, 12, 13 and match them to 011/012/013.
4. Recover geometry X/Y/W/H and visibility for the +0x85C Bitmap.
5. Determine the separate role of fixed resource 14.
6. Resolve the provenance of data at 0x0801AB7E separately.

## Evidence

[FW] 0x121 -> 0x370A; FUN_08036FF2; FUN_08037094; FUN_080115F6; 370A registration +0x16BA; base 0x200208EC; RAM 0x20021FA6; UI read of 0x121; FUN_0803CACC; value+10; FUN_080307BC.

[STRONG] The Boiler image selector path is now closed from parameter ID through storage to variable Bitmap resource ID.