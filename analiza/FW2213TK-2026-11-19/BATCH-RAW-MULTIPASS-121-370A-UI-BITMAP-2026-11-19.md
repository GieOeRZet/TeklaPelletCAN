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
## 11. SECOND PASS — +0x85C IS PROVEN TO BE A REAL BITMAP CHILD

The previous pass established that FUN_0803CACC writes the variable resource ID to parent +0x85C.

A further raw pass resolves the constructor of that same parent.

FUN_0803C33E builds the visual parent used by the 370A update component.

Critical constructor sequence:
- parent +0x84C is initialized by a visual helper;
- parent +0x85C -> FUN_0802DF08 with initial resource ID 0xFFFF;
- parent +0x888 -> FUN_0802DF08 with initial resource ID 0xFFFF;
- parent +0x8B4 -> FUN_0802DF08 with initial resource ID 0xFFFF;
- parent +0x8E0 -> FUN_0802DF08 with initial resource ID 0xFFFF.

FUN_0802DF08 is the concrete Bitmap constructor pattern: it calls the base visual constructor, installs Bitmap class data, writes the initial 16-bit resource ID into child +0x26, and calculates/stores dimensions from that resource.

[FW] parent +0x85C is a concrete Bitmap child object, not an arbitrary byte/field.

Closed path is now:
370A -> 0x121 -> 0x20021FA6 -> FUN_0803CACC -> parent+0x85C Bitmap -> resource 11..13

## 12. SECOND PASS — THE VISUAL PARENT IS A REPEATED COMPOSITE

FUN_0803C33E is called from three sibling constructors:
- FUN_08039A48
- FUN_08039B30
- FUN_08039C18

Each creates the same 0x85C/0x888/0x8B4/0x8E0 Bitmap family.
Each sibling also creates a FUN_0803CB04 update component, whose update routine reads model indices including 0x121.

[STRONG] The firmware has a repeated visual composite with four Bitmap children, and the Boiler image selector specifically controls the first Bitmap child at +0x85C.

Do not yet assign the three composites to specific screen names or cascade boilers; that requires additional model/parent/vtable evidence.

## 13. SECOND PASS — RESOURCE 14 IS A DIFFERENT CONSTRUCTION PATH

The variable 370A Bitmap path is structurally distinct from the investigated FUN_080469E8 path:
- 370A path: FUN_0803C33E -> Bitmap child +0x85C -> FUN_0803CACC -> resource 11..13.
- 469E8 path: FUN_080469E8 -> Bitmap child +0x13C -> fixed resource 14.

This is an architectural separation, not merely a naming difference.
Resource 14 therefore cannot be used as evidence against the 370A value+10 mapping.
## 14. THIRD PASS — CONSTRUCTOR STRUCTURE AND BITMAP WRITER REVALIDATED

Raw BIN was re-disassembled directly from FW2213TK_kopia.bin.

FUN_0803C33E exact constructor sequence:
- parent +0x330 -> FUN_0802DF08, initial resource 0xFFFF;
- parent +0x35C -> FUN_0802DF08, initial resource 0xFFFF;
- parent +0x85C -> FUN_0802DF08, initial resource 0xFFFF;
- parent +0x888 -> FUN_0802DF08, initial resource 0xFFFF;
- parent +0x8B4 -> FUN_0802DF08, initial resource 0xFFFF;
- parent +0x8E0 -> FUN_0802DF08, initial resource 0xFFFF.

This corrects an earlier simplification: the composite contains more than only the four +0x85C-family Bitmaps. The +0x330 and +0x35C Bitmap children are also explicitly constructed.

However the 370A update still targets only +0x85C.

FUN_080307BC exact behavior:
- reads uint16 resource ID from argument object;
- stores it at Bitmap child +0x26;
- derives width through FUN_0803439C;
- invokes Bitmap vtable slot +0x38 with the new width;
- derives height through FUN_080343EA;
- invokes Bitmap vtable slot +0x3C with the new height;
- recomputes clipping/visibility state and stores a flag at +0x29.

[FW] The selector update is therefore a real Bitmap resource replacement, followed by automatic dimension recalculation. It is not merely changing an ID field.

## 15. THIRD PASS — RESOURCE DIMENSIONS ARE CONSISTENT WITH EXTRACTED ASSETS

Repository extraction records the firmware bitmap dimensions:
- 011.png = 105x126
- 012.png = 108x141
- 013.png = 82x145
- 014.png = 54x100

The Bitmap constructor/writer derives dimensions from the resource itself rather than hardcoding these dimensions in FUN_0803CACC.

[STRONG] The three 370A-selected resources are therefore expected to drive three different Bitmap dimensions at runtime. This explains why the widget constructor uses resource 0xFFFF initially and later updates the actual resource.

Resource 14 remains independently constructed by FUN_080469E8 with fixed ID 14.

## 16. THIRD PASS — CLASS/VTABLE CLAIM MUST REMAIN CONSERVATIVE

Raw object construction writes pointer-like values at object +0, but several such values resolve into UTF-16/data regions rather than a conventional executable vtable.

Therefore we can safely say:
- FUN_0802DF08 is the firmware's Bitmap-construction routine;
- FUN_080307BC is the firmware's Bitmap resource setter/update routine;
- Bitmap methods are dispatched through object-relative slots +0x38/+0x3C;
- exact C++ vtable/class identity is still OPEN.

Do NOT label the literal at object +0 as a recovered C++ vtable until a separate executable method-table proof is found.

## 17. THIRD PASS — 370A PATH VS FIXED 14 PATH

Two resource-setting mechanisms now have independent raw proof:

Variable selector:
FUN_0803CB04 -> FUN_0803CACC -> parent+0x85C -> FUN_080307BC -> 11..13

Fixed visual:
FUN_080469E8 -> child+0x13C -> FUN_080307BC -> 14

They share the same low-level Bitmap resource writer but not the same Bitmap child or constructor.

[FW] This is the correct level of consolidation: shared Bitmap subsystem, separate higher-level UI components.