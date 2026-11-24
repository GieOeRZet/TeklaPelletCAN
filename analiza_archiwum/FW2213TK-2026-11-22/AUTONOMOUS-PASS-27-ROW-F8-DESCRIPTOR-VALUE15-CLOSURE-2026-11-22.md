# AUTONOMOUS PASS 27 — ROW +0xF8 DESCRIPTOR / VALUE 0x15 CLOSURE — 2026-11-22

## Objective

Resolve the producer of the value consumed by PROJECT 0x08032F08 in the 0x0E access-table path.

## HARD — row constructor initializes +0xF8

The 21 row instances are initialized through PROJECT 0x0800DCFC with stride 0x274.

The constructor pointer supplied for the row type is runtime 0x08099571 -> PROJECT 0x08089571.

At PROJECT 0x08089570:

- [row+0x00] receives a runtime vptr;
- [row+0xF8] receives literal 0x0807C540;
- row+0x128 is passed to PROJECT 0x080355A0.

A second adjacent constructor at PROJECT 0x08089594 performs the same initialization pattern and also stores 0x0807C540 at +0xF8.

Therefore the initial value of row[i]+0xF8 is a shared static descriptor/table address, not an unknown per-row scalar.

## HARD — 0x08032F08 reads that descriptor

PROJECT 0x08032F08 is:

LDRB.W r0,[r0,#0x2C]
BX LR

The caller supplies r0 = row[i]+0xF8.

With the constructor-established value:

row[i]+0xF8 = 0x0807C540

therefore the initial read is:

0x0807C540 + 0x2C = 0x0807C56C

The canonical BIN at the corresponding RAW location contains:

LE32 0x080A5B15

so the byte returned by LDRB is:

0x15

Thus, under the constructor-established static value:

PROJECT 0x08032F08(row[i]+0xF8) = 0x15.

## HARD — revised 0x0E path

The static constructor path now gives:

0x20005F08[i] == 0x0E
-> row[i]+0xF8
-> 0x0807C540
-> read +0x2C
-> value 0x15
-> PROJECT 0x0803C270
-> logical key 0x0117
-> PROJECT 0x08037212
-> no static key match
-> no 0x08011812 call

So the path is not currently a row-specific value propagation path.

## Interpretation

The object at 0x0807C540 has a table-like layout: its first visible nonzero words include executable pointers beginning at +0x08, and +0x2C contains a pointer whose low byte is 0x15.

This is consistent with a static descriptor/vtable-like structure, but the exact class/ABI role is NOT promoted to HARD.

## HARD

- row constructors initialize +0xF8 with 0x0807C540;
- PROJECT 0x08032F08 reads byte +0x2C from that address;
- the canonical static byte is 0x15;
- therefore the constructor-established value returned by 0x08032F08 is 0x15.

## OPEN

1. Determine whether row[i]+0xF8 is ever mutated after construction.
2. Identify the object/table at 0x0807C540.
3. Resolve why logical key 0x0117 is sent into 0x08037212 despite having no static resolver-key match.
4. Continue 0x08037212 mapping and 260-slot catalog correlation.
5. Continue runtime-class 0..20 -> page/widget handlers.
6. Continue remaining SRAM-table writer search.

## REJECTED

- row[i]+0x124 as a directly initialized scalar value.
- Treating the 0x0E path's returned value as inherently row-specific.
