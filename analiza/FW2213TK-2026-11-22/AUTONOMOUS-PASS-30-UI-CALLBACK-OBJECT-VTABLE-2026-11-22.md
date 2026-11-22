# AUTONOMOUS PASS 30 — UI CALLBACK OBJECT VTABLE 0x0809F848 — 2026-11-22

## Objective

Resolve the runtime vtable installed by the common UI constructor at PROJECT 0x08039494 and determine the machine-level interface of the object stored at parent+0x110.

## HARD — vtable identity and storage

PROJECT 0x08039494 loads literal:

- 0x0809F848

and stores it at [object].

This vtable pointer is also present in the constructor at PROJECT 0x08039394.

Static vtable location:

- runtime address: 0x0809F848
- PROJECT address: 0x0808F848
- RAW offset: 0x8F848

The vtable contains non-zero entries at slots:

| slot | runtime pointer | PROJECT | RAW |
|---:|---:|---:|---:|
| 2 | 0x080A0399 | 0x08090399 | 0x90399 |
| 3 | 0x0809BAF5 | 0x0808BAF5 | 0x8BAF5 |
| 8 | 0x0809DE25 | 0x0808DE25 | 0x8DE25 |
| 9 | 0x0809B675 | 0x0808B675 | 0x8B675 |
| 14 | 0x080A0069 | 0x08090069 | 0x90069 |
| 15 | 0x0809B735 | 0x0808B735 | 0x8B735 |

Slots 0,1,4..7,10..13 are zero in the recovered table region.

This is direct static evidence.

## HARD — constructor variants

PROJECT 0x08039394:

1. stores vtable 0x0809F848;
2. stores 0 at +0x4;
3. copies a static 8-byte pair from the literal target around RAW 0x793A0 into +0x8.

PROJECT 0x08039494:

1. stores the same vtable;
2. stores incoming parent object at +0x4;
3. stores incoming r2/r3 at +0x8/+0xC.

PROJECT 0x080394A8 copies the +0x4/+0x8/+0xC fields into an existing object.

Therefore the object at parent+0x110 is a four-field runtime object:

- +0x00: vtable 0x0809F848
- +0x04: context/owner pointer
- +0x08: callback/table pointer or related context
- +0x0C: signed/index/offset field

The semantic names are deliberately not promoted beyond these machine-level facts.

## HARD — vtable slots 2 and 8 share the same dispatch algorithm

PROJECT 0x08090398 (vtable slot 2) performs:

1. r2 = [object+0x0C]
2. r1 = [object+0x04]
3. r1 += arithmetic shift-right(r2,1)
4. if r2 is non-negative:
   - callback base = [object+0x08]
5. otherwise:
   - callback base = [r1]
   - index = [object+0x08]
   - callback = [callback base + index]
6. r0 = r1
7. BX callback

This is a genuine indirect dispatch through the three data fields.

PROJECT 0x0808DE24 (vtable slot 8) implements the same structural algorithm with r3/r4 temporaries.

Therefore slots 2 and 8 are two interface entries implementing the same family of indirect callback dispatch.

## HARD — vtable slots 3 and 9 are the corresponding sibling operations

PROJECT 0x0808BAF4 (slot 3) and PROJECT 0x0808B674 (slot 9) implement the same boolean/state-check pattern:

- test object+0x04;
- if present, test object+0x08;
- otherwise inspect the sign bit of object+0x0C;
- return 0/1.

The repeated implementation occurs in a large generated method family.

This is a second, independent interface operation associated with the same object layout.

## HARD — callback object is not merely a data descriptor

The vtable methods perform actual indirect calls.

The generic UI construction path therefore creates an executable polymorphic object:

runtime class
-> static callback/config pointer
-> temporary object
-> vtable 0x0809F848
-> parent+0x110
-> indirect callback dispatch

This closes another layer of the UI runtime architecture.

## STRONG

The object resembles a callback/delegate/indirect-dispatch abstraction because:

- it has a vtable;
- it stores an owner/context pointer;
- it stores another pointer/index field;
- vtable methods perform indirect calls;
- multiple vtable slots implement related dispatch/check operations.

The exact C++ class/type name is unknown and must remain OPEN.

## OPEN

1. Identify the call sites of vtable slots 2/3/8/9 from UI handlers and determine their actual arguments.
2. Map each static callback pointer (0x08048037 etc.) to the vtable operation that consumes it.
3. Trace those callbacks into text/bitmap/resource and PID access.
4. Resolve vtable slots 14/15.
5. Resolve the static pair used by constructor 0x08039394.
6. Continue class 12 and class 15 special paths.
7. Continue runtime table mutation and 260-row matrix.

## REJECTED

- Treating 0x0809F848 as a passive resource table.
- Treating parent+0x110 as merely a pointer field without runtime behavior.
- Assigning a business name such as "widget", "screen", or "event handler" as HARD.
