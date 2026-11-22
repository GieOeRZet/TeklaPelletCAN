# AUTONOMOUS PASS 34 — RUNTIME KEY 3 STORAGE / TYPE CLOSURE

Date: 2026-11-22

## Scope

Follow-up to PASS 33. Goal: determine what can be proven about runtime lookup key 3 storage at `0x20021FAA`, its physical type, relation to nearby startup configuration fields, and why class 12 uses type-5 temporaries when the startup runtime record has type 1.

Canonical firmware SHA-256:
`1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`

## HARD — key 3 is byte-backed

Startup at RAW `0x1D62` calls `FUN_0801143C` with:
- manager `0x20008D84`
- runtime lookup key `3`
- storage pointer `0x200208EC + 0x16BE = 0x20021FAA`
- type code `1`, obtained through `FUN_08010FC2`.

`FUN_08011812` locates the runtime record by key. Record +0x0C is the storage pointer and record +0x10 is the runtime type. Its final store for type 1 is an 8-bit load/store path:
`LDRB -> STRB [storage]`.

Therefore runtime key 3 is **physically byte-backed** at `0x20021FAA`. HARD.

## HARD — class 12 type-5 input is normalized to the record storage type

`FUN_080373BA`:
1. calls `FUN_080115F6(manager,key=3)`;
2. copies the returned value into a temporary;
3. creates that temporary with type 5;
4. reads it through `FUN_08014734`.

`FUN_080373E6`:
1. computes value modulo 8;
2. creates a type-5 temporary;
3. calls `FUN_08011812(manager,key=3,...)`.

The setter does not blindly store according to the incoming temporary type. It validates/converts the value and then writes according to the located runtime record type.

Thus the hard chain is:

`class 12 -> type-5 temporary/input -> runtime record key 3 (type 1) -> STRB -> 0x20021FAA`.

This resolves the apparent type mismatch.

## HARD — key 3 and key 4 share the same startup configuration base

Startup registers:
- key 3 -> `+0x16BE` -> `0x20021FAA` -> type 1
- key 4 -> `+0x16CE` -> `0x20021FBA` -> type 2

The same routine also registers nearby keys:
- `0x3500` -> `+0x16BF`
- `0x3502` -> `+0x16C0`
- `0x350B` -> `+0x16CC`

and later `0x3721/0x3724/0x3725/0x3726/0x3729/0x372B/0x372C` use nearby fields of the same base object.

This proves shared configuration/storage ownership, but not semantic names.

## HARD — nearby initialization does not prove catalog-PID identity

A separate initialization routine around PROJECT `0x080121C6` calls `FUN_08014700` for nearby storage locations:
- `+0x16A0`, default 50
- `+0x16AC`, default 30
- `+0x16B8`, default 1
- `+0x16C4`, default 5
- `+0x16D0`, default 5

`FUN_08014700` writes a 32-bit value and type tag 5 at storage +4. Key 3's `+0x16BE` and key 4's `+0x16CE` are distinct fields in the broader configuration region, not direct evidence of catalog row identity.

Do not equate runtime key 3 with catalog PID 3 or any catalog row from the numeric key alone.

## NEGATIVE EVIDENCE

Whole-BIN LE32 search for absolute SRAM address `0x20021FAA` found no literal occurrence.

The startup pointer is therefore formed arithmetically from `0x200208EC + 0x16BE`.

A whole-BIN immediate search for `0x16BE` found the startup construction as the relevant direct occurrence; no independent direct static semantic consumer was found.

This does not exclude indirect/runtime consumers.

## STRONG

Key 3 is a byte-domain runtime state. Combined with class 12's modulo-8 operation, this strengthens the cyclic-selector/state interpretation.

## OPEN

1. Exact semantic name of `0x20021FAA`.
2. Direct key-3 -> catalog PID mapping.
3. Other UI/resource consumers of key 3.
4. Why +0x16BE/+0x16CE are separately registered as runtime keys 3/4.
5. Full runtime-key startup matrix.
6. Provider/persistence/CAN publication behavior specifically for key 3.

## REJECTED / forbidden promotion

Without a direct bridge, do not claim:
- key 3 = catalog PID 3;
- key 3 = a specific user-facing parameter;
- key 3 = a specific menu selector;
- key 3 = a specific CAN parameter.

## Conclusion

PASS 34 closes the physical storage/type side:

`runtime key 3 -> manager 0x20008D84 -> record +0x0C = 0x20021FAA -> record type 1 -> byte-backed storage`.

Semantic/PID identity remains OPEN.
