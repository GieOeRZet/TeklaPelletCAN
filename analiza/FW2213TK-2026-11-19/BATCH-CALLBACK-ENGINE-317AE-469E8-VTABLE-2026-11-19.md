# BATCH — MULTIPASS CALLBACK ENGINE + 469E8 TIMER DISPATCH — 2026-11-19

## Executive result

This pass went below the previous documentation layer and recovered the complete exported `decompiled.c` blob from its GitHub blob SHA. The raw BIN itself is still not stored in the repository, so no raw Thumb bytes are invented.

The main result is a sharper architecture:

1. `FUN_080317AE` is not merely a vague "update dispatcher". Its first registry loop is an explicit per-tick/per-update traversal of registered objects, and for every active entry it calls **vtable slot +0x50**.
2. `FUN_080318B4` is exactly the registration/reference-count side of that same mechanism.
3. `FUN_080469E8` registers the complete 469E8 object, not its Bitmap child separately. Therefore the unresolved 469E8 runtime method is exactly the object's `DAT_08046CC4 + 0x50` entry.
4. `FUN_08030762` is a separate, already recoverable dynamic Bitmap-child update helper used by many larger components. It unregisters a Bitmap object, selects its resource ID from object state, writes it with `FUN_080307BC`, calls the Bitmap object's vtable +0x14, and leaves the object unregistered. This proves the firmware has an established dynamic Bitmap-update pattern, but it is **not yet proven** to be the 469E8 path.
5. The callback addresses for 3709..370D are demonstrably heterogeneous internal code boundaries:
   - 3709 -> 0x0801425C = inside FUN_0801417C, offset +0xE0.
   - 370A -> 0x0801AB7E = no named function.
   - 370B -> 0x08015CCC = no named function.
   - 370C -> 0x0801659E = inside FUN_080164F4, offset +0xAA.
   - 370D -> 0x08016614 = inside FUN_080164F4, offset +0x120.
6. Therefore the table field previously called "callback" must now be treated as a **code/handler boundary field**, not as a conventional C++-style function pointer.

## Pass 1 — exact 317AE semantics

Recovered body of `FUN_080317AE`:

- obtains global state from `DAT_08031A8C`;
- handles the active module/window state before the registry walk;
- registry count is at object offset `+0x64` (Ghidra expression `*(ushort *)(param_1 + 0x19)`);
- registered object pointers are at `+0x04 + index*4`;
- active/reference bytes are at `+0x68 + index`.

The decisive loop is conceptually:

    for each registered object:
        if active/reference byte != 0:
            call registered_object->vtable[0x50]()

The decompiler represents this as an indirect call through:

    (**(code **)(*(int *)registered_object + 0x50))()

No parameter ID, CAN index, Bitmap ID or 370A is read in this dispatcher itself.

### Important ordering

The update loop occurs BEFORE the cleanup loop that removes entries whose active/reference byte is zero.

Therefore +0x50 is a genuine runtime update/tick boundary, not a registration helper.

## Pass 2 — exact 318B4 semantics

`FUN_080318B4`:

- scans the registered object pointer array;
- if the object already exists, increments its reference byte at `+0x68 + index`;
- otherwise marks a new entry active and stores the object pointer;
- count is at `+0x64`;
- capacity is 0x18 entries.

`FUN_0803193A` is the matching decrement/unregistration operation.

So the pair is:

    FUN_080318B4 = register / retain
    FUN_0803193A = release / unretain
    FUN_080317AE = periodic traversal + vtable +0x50 dispatch

This is now a closed registry architecture.

## Pass 3 — 469E8 exact registration boundary

`FUN_080469E8`:

1. calls base initializer `FUN_0802DD4C`;
2. temporarily installs `DAT_08046CC0`;
3. finally installs `DAT_08046CC4` as the 469E8 class vptr;
4. constructs Bitmap child at `+0x4F`;
5. calls `FUN_080307BC(child, 0x0E)`;
6. positions the Bitmap using child vtable +0x2C/+0x30;
7. attaches it with `FUN_08030380`;
8. creates four TypedText-related children;
9. obtains the active module through `FUN_080314BA()`;
10. registers **the parent 469E8 object itself** through `FUN_080318B4(active_module, param_1)`.

Therefore:

    469E8 object
       |
       +-- registered in timer/update registry
       |
       +-- FUN_080317AE
       |
       +-- DAT_08046CC4 + 0x50
       |
       +-- UNKNOWN 469E8 runtime method

The Bitmap child has its own vptr `DAT_0802DF7C`; that is a different class boundary.

## Pass 4 — dynamic Bitmap mechanism already present elsewhere

`FUN_08030762(int *param_1)` is a separate recoverable mechanism:

    active module
       |
       +-- FUN_0803193A(module, bitmap_object)   // unregister
       |
       +-- choose resource ID from bitmap_object state
       |
       +-- FUN_080307BC(bitmap_object, resource_id)
       |
       +-- bitmap_object vtable +0x14
       |
       +-- return

Its resource selection is based on object fields:

    if byte(object + 0x36) == 0:
        id = object[0x30]
    else:
        id = object[0x32]

Then:

    FUN_080307BC(bitmap_object, id)

This is important because it proves that the firmware already uses a **state-driven dynamic Bitmap resource update idiom** rather than requiring every resource ID to be hard-coded in a constructor.

However, current evidence does NOT prove that 469E8 invokes 30762 or that 370A feeds these fields.

## Pass 5 — callback neighborhood revalidation

From the parameter table:

    3709 -> 0x0801425C
    370A -> 0x0801AB7E
    370B -> 0x08015CCC
    370C -> 0x0801659E
    370D -> 0x08016614

Function-range containment from `functions.txt`:

### 3709

    0x0801425C
       inside FUN_0801417C
       function size 610 bytes
       offset +0xE0
       end 0x080143DD

`FUN_0801417C` is a large model-name/table builder containing entries such as Bio Compact, Draco Bio, Tytan Bio, etc.

This is strong evidence against the idea that the table field is simply "the setter function for parameter 3709".

### 370B

    0x08015CCC
       not the start of a named function
       lies in the unrecognized gap between the named function blocks around 0x08015A4E and 0x0801625C

### 370C / 370D

Both lie inside:

    FUN_080164F4
    size 452 bytes
    0x080164F4..0x080166B7

Offsets:

    370C -> 0x0801659E = +0xAA
    370D -> 0x08016614 = +0x120

`FUN_080164F4` is a real state/logic routine: it calls `FUN_080166B8`, reads/writes multiple state fields, calculates thresholds/timers and drives related state helpers.

### 370A

    0x0801AB7E
       no named function
       no function-range containment in functions.txt

It remains the critical missing code/data boundary.

## Pass 6 — architectural correction

The parameter table's code field should now be named conservatively:

**handler/code boundary**

rather than:

**callback function**

until the raw dispatch mechanism is recovered.

The architecture is:

    PARAMETER TABLE
        |
        +-- parameter ID 0x370A
        +-- RAM 0x20021FA6
        +-- handler/code boundary 0x0801AB7E
                    |
                    +-- UNKNOWN dispatcher / internal entry

This is consistent with neighboring entries pointing inside larger routines.

## Pass 7 — relationship to 469E8

The two branches remain independent:

    370A
      |
      +-- RAM 0x20021FA6
      |
      +-- 0x0801AB7E
      |
      +-- UNKNOWN parameter engine path


    active module
      |
      +-- 469E8 registration
      |
      +-- 317AE
      |
      +-- DAT_08046CC4 + 0x50
      |
      +-- UNKNOWN 469E8 update
      |
      +-- child +0x4F
      |
      +-- Bitmap resource state

The first real merge point to search for is now not "another bitmap constructor", but a concrete read/use of the 370A state inside one of the runtime update methods.

## Pass 8 — what is now ruled out

1. 318B4 is NOT the parameter binding function.
2. 317AE is NOT a parameter reader; it is the timer/update dispatcher.
3. 469E8 constructor is NOT the dynamic selector; its Bitmap ID 14 is fixed at construction.
4. 370A's code field is NOT safe to label as a normal named function.
5. Bitmap IDs 11/12/13/14 still cannot be mapped to 370A values 1/2/3 by numbering alone.

## Pass 9 — highest-value next attack

Priority order:

### A — recover 469E8 +0x50

Need to resolve:

    DAT_08046CC4 + 0x50
       |
       +-- concrete code address
       |
       +-- method body
       |
       +-- model/state reads
       |
       +-- child +0x4F or other child state
       |
       +-- visibility/resource change

### B — recover 370A handler boundary

Need raw Thumb2 around:

    0x0801AB7E

and, ideally, the code that invokes the parameter-table handler/code field.

### C — use known dynamic Bitmap idiom as a pattern

Compare the 469E8 object against classes that use:

    unregister -> FUN_080307BC(variable_id) -> child vtable update

and determine whether the 469E8 update is structurally analogous.

### D — only then merge

    0x20021FA6
       |
       +-- model notification/read
       |
       +-- 469E8 update
       |
       +-- resource ID
       |
       +-- 011/012/013/014

## Evidence status

[FW] 317AE registry traversal and +0x50 indirect dispatch — CLOSED.

[FW] 318B4 registration/reference counting — CLOSED.

[FW] 3193A release/unregistration — CLOSED.

[FW] 469E8 final vptr DAT_08046CC4 — CLOSED.

[FW] 469E8 Bitmap child +0x4F — CLOSED.

[FW] 469E8 constructor Bitmap ID 14 — CLOSED.

[FW] 30762 dynamic Bitmap update idiom — CLOSED as a generic mechanism.

[STRONG] 3709..370D code fields are internal code boundaries / handler entries, not necessarily function starts.

[OPEN] 0x0801AB7E actual semantics.

[OPEN] DAT_08046CC4 + 0x50 concrete target.

[OPEN] 370A -> 469E8.

[OPEN] 370A -> 011/012/013/014 mapping.

## Rule for the next pass

Do not stop after resolving one address. Once either 0x0801AB7E or DAT_08046CC4+0x50 is resolved, immediately continue down that path until it reaches a state read/write, child/resource, or a hard dead-end caused by missing raw bytes. Then start the other path.

