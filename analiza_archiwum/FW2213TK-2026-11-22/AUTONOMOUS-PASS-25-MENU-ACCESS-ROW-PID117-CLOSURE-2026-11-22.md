# AUTONOMOUS PASS 25 — MENU ACCESS TABLE → ROW OBJECT → PID 0x0117 CLOSURE — 2026-11-22

## Objective

Continue immediately from PASS 24 and resolve the highest-value remaining UI boundary around PROJECT 0x080422C8:

- identify the owning object;
- prove the 21-row object geometry;
- connect access-table value 0x0E to a concrete row field;
- follow the resulting value into the parameter write path.

## HARD — vtable ownership of PROJECT 0x080422C8

A whole-BIN runtime-pointer search found:

- runtime function pointer 0x080522C9 occurs at RAW 0x7F680;
- its PROJECT function is 0x080422C8;
- the pointer is part of a runtime vtable beginning at RAW 0x7F66C;
- the vtable runtime address is 0x0808F66C.

The vtable slot geometry is:

- slot 0: RAW 0x7F66C -> runtime 0x08043C73
- slot 1: RAW 0x7F670 -> runtime 0x080A60ED
- slot 2: RAW 0x7F674 -> runtime 0x08043A33
- slot 3: RAW 0x7F678 -> runtime 0x08052161
- slot 4: RAW 0x7F680 -> runtime 0x080522C9 -> PROJECT 0x080422C9

Therefore PROJECT 0x080422C8 is HARD-confirmed as the Thumb implementation of vtable slot 4 for the class whose vptr is runtime 0x0808F66C.

This removes the previous ambiguity around whether 0x080422C8 is an isolated helper.

## HARD — concrete constructor and 21-row allocation geometry

Constructor at RAW 0x74508 / PROJECT 0x08074508:

- receives object in r0;
- stores runtime vptr 0x0808F66C at [r4+0].

The constructor then calls:

- RAW 0x74516 -> PROJECT 0x08074516
- r0 = r4 + 0x422C
- BL PROJECT 0x0807454C

It also initializes a 21-element region through PROJECT 0x0800DCFC:

- r0 = r4 + 0x42C
- r2 = 0x274
- r3 = 0x15
- r1 = literal-backed helper/class pointer
- BL 0x0800DCFC

Thus the object contains a 21-element repeated region beginning at:

- object +0x42C
- stride 0x274
- count 0x15 = 21

This matches the 21-entry MenuTree/access-table model independently of the SRAM table itself.

## HARD — access-table index maps to row instance field

PROJECT 0x080422C8 starts with:

- r4 = this
- r5 = 0x20005F08
- r8 = r4 + 0x524
- r7 = 0x15

Each loop:

- reads [r5]
- r5 += 1
- r8 += 0x274

Therefore for index i:

- access byte = 0x20005F08[i]
- r8 = object + 0x524 + i*0x274

Since the row-instance region begins at object +0x42C, this is exactly:

- row[i] + 0xF8

because:

0x524 - 0x42C = 0xF8.

This is a HARD structural mapping.

## HARD — 0x0E gate reads row[i] + 0x124

When the current access-table byte equals 0x0E:

PROJECT 0x080422C8:

- r0 = r8
- BL PROJECT 0x08032F08

PROJECT 0x08032F08 is:

- LDRB.W r0, [r0,#0x2C]
- BX LR

Therefore the value forwarded from row i is:

row[i] + 0xF8 + 0x2C = row[i] + 0x124

So:

0x20005F08[i] == 0x0E
-> read row[i]+0x124

This is a new exact field-level UI closure.

## HARD — row value reaches PID 0x0117 write path

After 0x08032F08:

PROJECT 0x080422C8:

- r1 = returned row[i]+0x124 value
- r0 = [this+0x3C]
- BL PROJECT 0x0803C270

PROJECT 0x0803C270:

- reads [r0+0x10]
- requires it to equal 1
- moves incoming value to r2
- r0 = [r0+8]
- r1 = 0x0117
- branches to PROJECT 0x08037212

Therefore:

0x20005F08[i] == 0x0E
-> row[i]+0x124
-> object+0x3C state object
-> [state+0x10] == 1
-> PROJECT 0x08037212
-> logical parameter key 0x0117
-> value = row[i]+0x124

## HARD — 0x08037212 is tied to the parameter manager

PROJECT 0x08037212 loads:

- manager pointer 0x20008D84 from literal RAW 0x3754C.

It then searches a static mapping table and calls:

- PROJECT 0x08011812

with the resolved PID/value/type tuple.

Thus the chain is not merely a UI-local setter. It reaches the already closed parameter-manager update engine.

The exact mapping from logical key 0x0117 to the final PID selected by 0x08037212 is a separate OPEN because 0x08037212 performs a lookup before calling 0x08011812.

## HARD — 0x08037212 mapping table geometry

At entry:

- r8 = incoming logical key 0x0117
- r5 = incoming value

The first search loop iterates 0x31 entries.

It compares r8 against entries addressed through an ADR-derived table and, on a match, computes the PID from the matched entry plus another byte value before calling 0x08011812.

A second loop scans 0x174 entries through another ADR-derived table.

Therefore logical key 0x0117 is a resolver key, not automatically the final CAN PID.

Do not yet label 0x0117 as a final Estyma PID.

## NEW ARCHITECTURAL MODEL

The recovered chain is now:

Menu access table
-> access class byte
-> row instance
-> row field +0x124
-> state/access gate
-> logical UI parameter key 0x0117
-> parameter-key resolver 0x08037212
-> concrete parameter manager 0x20008D84
-> FUN_08011812
-> existing local write/publication/CAN machinery

This is the first direct machine-level bridge from the MenuTree runtime access table into the generic parameter engine.

## STRONG

- The 21 row objects are the concrete runtime instances behind the 21 MenuTree entries.
- The +0x274 stride is the runtime row-instance stride.
- The field at row[i]+0x124 is likely a per-row parameter/value binding because it is fed into the generic parameter write path.
- 0x0117 is likely a UI/logical parameter selector rather than a final CAN PID because 0x08037212 resolves it through a separate mapping table.

These semantic labels remain STRONG, not HARD.

## OPEN

1. Resolve the 0x08037212 mapping entry for logical key 0x0117.
2. Identify the concrete final PID/value/type tuple passed to 0x08011812 for the 0x0E path.
3. Identify the object at this+0x3C and its +0x10 state field.
4. Map each of the 21 row instances to the 21 root MenuTree selectors.
5. Trace row[i]+0x124 backward to its producer/initializer.
6. Trace runtime classes 0..20 from 0x0803C064 to page/widget constructors.
7. Continue resource/text/bitmap/PID/CAN cross-linking.
8. Continue arithmetic/alias writer search for 0x20005EF0 and 0x20005F08.

## REJECTED

- 0x080422C8 as an unrelated standalone helper.
- The earlier assumption that 0x080422C8 could not be tied to a concrete class.
- 0x0117 as the final CAN PID without resolving 0x08037212's mapping.

## Next attack

Highest-value target is now PROJECT 0x08037212:

- recover the exact mapping-table entries around logical key 0x0117;
- derive the final PID/storage/type tuple;
- connect it to the 260-row catalog.

In parallel, use constructor 0x08074508 and row initializer 0x0800DCFC to recover the producer of row[i]+0x124.
