# BATCH — FOURTH RAW PASS: 370A COMPOSITE CONSTRUCTOR + GEOMETRY CORRELATION — 2026-11-19

## 1. Direct caller proof for FUN_0803C33E

A full raw Thumb BL scan of FW2213TK_kopia.bin finds exactly three direct calls to FUN_0803C33E:

- 0x08039AD6
- 0x08039BBE
- 0x08039CA6

These are inside the three already identified sibling constructor functions:

- FUN_08039A48
- FUN_08039B30
- FUN_08039C18

Immediately after each FUN_0803C33E call, the returned composite pointer is saved and then passed to FUN_0803CB04 when the second child/component exists.

[FW] This is stronger than merely noticing similar code: the three sibling constructors really instantiate the same FUN_0803C33E visual composite and wire a FUN_0803CB04 updater around it.

## 2. FUN_0803C33E exact object layout

Raw disassembly shows:

- +0x330 -> FUN_0802DF08, initial resource 0xFFFF
- +0x35C -> FUN_0802DF08, initial resource 0xFFFF
- +0x388 -> separate object/helper initialized with constants
- +0x464 -> separate object/helper
- +0x498 -> separate object/helper
- +0x84C -> separate helper/container initialized by FUN_080424C4
- +0x85C -> FUN_0802DF08, initial resource 0xFFFF
- +0x888 -> FUN_0802DF08, initial resource 0xFFFF
- +0x8B4 -> FUN_0802DF08, initial resource 0xFFFF
- +0x8E0 -> FUN_0802DF08, initial resource 0xFFFF
- +0x90C/+0x948/+0x97C... -> additional UI objects.

[FW] The +0x84C helper sits immediately before the 370A Bitmap and is initialized with parent pointer + two literal parameters. This is likely the container/layout support object around the Bitmap cluster, but exact class semantics remain OPEN.

## 3. FUN_0803C5B4 is a layout/initialization method touching the same object offsets

Raw disassembly of FUN_0803C5B4 begins by initializing state and then reaches:

- child pointer = parent +0x85C
- X = 0x28
- Y = 0x46
- BL FUN_0804272C
- BL FUN_08030380(parent+0x04, child)

Therefore the +0x85C Bitmap is hard-positioned at (40,70) in this layout path and attached to the parent's child/container list.

The same method subsequently:
- configures +0x97C,
- configures +0x948,
- sets +0x8E0 to resource 0x7A,
- positions +0x8E0 at X=0x18E (398) and Y from runtime state,
- attaches +0x8E0 through parent+0x04.

[FW] This makes the multi-child layout interpretation considerably stronger.

## 4. Important correction to previous wording

The raw scan found no direct BL to FUN_0803C5B4 and no literal function-pointer occurrence of 0x0803C5B5 in the raw image.

Therefore do NOT claim:
- "FUN_0803C5B4 is directly called by FUN_0803C33E", or
- exact C++ virtual slot number for C5B4.

The correct statement is:
- C33E constructs the object layout;
- C5B4 is a separate raw method operating on the same object layout and assigning hard geometry;
- the dispatch mechanism connecting them is still OPEN.

## 5. FUN_0804272C proof

FUN_0804272C:

- loads object vtable-like field +0,
- calls slot +0x2C with r1,
- reloads +0,
- calls slot +0x30 with r2.

Thus it is definitively a two-coordinate setter.

## 6. 370A runtime path remains unchanged and closed

The visual updater is FUN_0803CB2C, not CB04:

0x370A
 -> internal 0x121
 -> FUN_08036FF2
 -> runtime record
 -> 0x20021FA6
 -> u8 1..3
 -> FUN_0803CB2C
 -> FUN_0803CACC
 -> parent +0x85C
 -> FUN_080307BC
 -> resource 11/12/13

## 7. New architectural picture

The strongest current model is:

SIBLING SCREEN CONSTRUCTOR
  -> FUN_0803C33E
      -> common visual composite
          -> Bitmap +0x85C  [370A-selected]
          -> Bitmap +0x888
          -> Bitmap +0x8B4
          -> Bitmap +0x8E0
          -> support objects around +0x84C etc.
  -> FUN_0803CB04
      -> FUN_0803CB2C update
          -> 0x121 / 370A
          -> FUN_0803CACC
          -> +0x85C

SEPARATE LAYOUT METHOD
  -> FUN_0803C5B4
      -> +0x85C at (40,70)
      -> +0x8E0 at (398,Yruntime)

## 8. Next attack

1. Resolve the dispatch mechanism for C5B4 (search all indirect-call/vtable tables, not BL only).
2. Identify the helper/container at +0x84C and its relation to +0x85C.
3. Recover W/H/visibility mutations of +0x85C from all methods.
4. Recover actual resource-registry records for IDs 11/12/13.
5. Compare the three sibling constructors beyond their common C33E call to identify the concrete Home/Main screen instance.
6. Keep 014/469E8 and 0x0801AB7E separate.
