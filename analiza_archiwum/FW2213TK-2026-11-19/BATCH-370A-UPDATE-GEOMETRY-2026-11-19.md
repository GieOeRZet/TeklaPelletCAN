# BATCH — 370A VISUAL COMPOSITE: UPDATE METHOD + GEOMETRY — 2026-11-19

## 1. Major correction: FUN_0803CB04 is constructor, not the update body

Raw disassembly proves:

`FUN_0803CB04`
- calls `FUN_080427FC`,
- writes object fields +0 and +4,
- stores the visual composite pointer in +0x0C,
- returns the object.

The actual recurring update body begins at:

`FUN_0803CB2C`

and is a straight sequence of model reads followed by UI mutations.

[FW] Therefore the 370A visual read should be represented as:

```
update object
  -> FUN_0803CB2C
      -> FUN_08036FF2(..., 0x121)
      -> FUN_0803CACC(parent, value)
      -> parent +0x85C Bitmap
```

The previous shorthand calling `FUN_0803CB04` the update function is corrected. `CB04` = constructor/wiring; `CB2C` = update routine.

## 2. FUN_0803CB2C is a multi-parameter visual refresh

The update body reads, in order, several internal indices including:

- 0x01F
- 0x023
- 0x00C
- 0x00D
- 0x11D
- 0x00E
- 0x017
- 0x11F
- 0x02A
- 0x11A
- 0x029
- **0x121**
- 0x00B
- 0x010

The important point is that 0x121 is not an isolated callback. It is one member of a larger refresh transaction for the same visual composite.

[FW] The 0x121 operation is exact:

```
ldr r0,[r4,#0x8]
movw r1,#0x121
BL  FUN_08036FF2
UXTB r1,r0
ldr r0,[r4,#0xC]
BL  FUN_0803CACC
```

So +0x08 is the model/context provider and +0x0C is the visual composite target.

## 3. FUN_0803CACC remains the closed 370A Bitmap bridge

`FUN_0803CACC`:
- receives the u8 value returned by the 0x121 resolver,
- adds 0x0A,
- targets parent +0x85C,
- calls `FUN_080307BC`.

Thus the already closed chain remains:

```
external 370A
 -> internal 0x121
 -> FUN_08036FF2
 -> runtime record
 -> 0x20021FA6
 -> u8 1..3
 -> FUN_0803CB2C
 -> FUN_0803CACC
 -> Bitmap +0x85C
 -> resource 11..13
```

## 4. New geometry proof: FUN_0804272C is an X/Y setter

Raw `FUN_0804272C` is now identified by behavior.

It:
1. reads object slot +0x2C and calls it with argument r1;
2. reads object slot +0x30 and calls it with argument r2;
3. therefore forwards the two coordinates independently.

[FW] In the call sites used here, this is a two-coordinate setter:

```
FUN_0804272C(object, X, Y)
```

Do not claim a full C++ class name yet; only the X/Y behavior is proven.

## 5. New geometry hit on the 370A target Bitmap

A nearby raw method at `FUN_0803C5B4` operates on the same composite offsets and explicitly prepares the 370A target child:

```
addw r8,r4,#0x85C
...
movs r1,#0x28
movs r2,#0x46
mov r0,r8
BL FUN_0804272C
```

Therefore:

```
Bitmap child +0x85C
X = 0x28 = 40
Y = 0x46 = 70
```

[STRONG] This is the first hard X/Y coordinate recovered for the 370A-selected Bitmap.

The same routine then adds that child to the parent/container through:

```
r0 = parent + 0x04
r1 = parent + 0x85C
BL FUN_08030380
```

So the 85C child is not only positioned; it is explicitly attached to the parent's child/container structure in this layout path.

### Association caveat

The raw routine `FUN_0803C5B4` has no direct BL callsite in the current flat-code scan; it is therefore safest to call it a **layout/update method using the same composite layout**, not yet a proven direct constructor call from `FUN_0803C33E`.

What is hard:
- the code targets +0x85C;
- the coordinate setter semantics are hard;
- X=40, Y=70 are hard values;
- it attaches +0x85C through parent +4.

What remains open:
- exact dispatch mechanism that invokes `FUN_0803C5B4`;
- exact C++ class/vtable identity.

## 6. Constructor structure revalidated

`FUN_0803C33E` explicitly creates:

- +0x330 Bitmap, resource 0xFFFF
- +0x35C Bitmap, resource 0xFFFF
- +0x85C Bitmap, resource 0xFFFF
- +0x888 Bitmap, resource 0xFFFF
- +0x8B4 Bitmap, resource 0xFFFF
- +0x8E0 Bitmap, resource 0xFFFF

The 370A update targets only +0x85C.

This gives the current structural picture:

```
Composite
├── Bitmap +0x330
├── Bitmap +0x35C
├── Bitmap +0x85C  <-- 370A selector, X=40 Y=70 in layout method
├── Bitmap +0x888
├── Bitmap +0x8B4
└── Bitmap +0x8E0
```

## 7. Additional nearby geometry clue

The same `FUN_0803C5B4` layout/update code later targets +0x8E0:

```
resource ID = 0x7A
X = 0x18E = 398
Y = value read from a runtime halfword
```

This is not yet merged into the 370A semantics, but it strongly indicates that the routine is laying out multiple children of the same large composite rather than merely manipulating one bitmap.

## 8. Resource-table subsystem

`FUN_0803439C` and `FUN_080343EA` are now behaviorally understood as Bitmap resource width/height lookups.

They:
- use a resource registry at runtime base around `0x2002454C`,
- select entries by resource ID,
- return width from entry +0x08,
- return height from entry +0x0A.

This independently confirms that `FUN_080307BC` recalculates the Bitmap dimensions from the selected resource.

Direct runtime BitmapData pointer initialization for IDs 11/12/13 is still open.

## 9. Updated main graph

```
370A
 -> internal 0x121
 -> FUN_08036FF2
 -> mapping table @ 08037984
 -> FUN_08037094
 -> FUN_080115F6
 -> record +0x0C
 -> 0x20021FA6
 -> u8 1..3
 -> FUN_0803CB2C       [actual update body]
 -> FUN_0803CACC
 -> +0x85C
 -> FUN_080307BC
 -> resource 11/12/13
 -> Bitmap dimensions from resource registry
 -> layout path: X=40, Y=70 [FUN_0803C5B4]
```

## 10. Next attack

Do not repeat the closed selector chain.

Next vertical attack:
1. resolve the dispatch/call mechanism for FUN_0803C5B4;
2. trace every geometry mutation of +0x85C and siblings;
3. recover W/H and visibility state for +0x85C;
4. identify the actual parent/container path from the three callers 08039A48 / 08039B30 / 08039C18 into Home/Main;
5. resolve resource registry entries 11/12/13 to the real BitmapData records;
6. only then merge the visual geometry into the Home/Main screen map.
