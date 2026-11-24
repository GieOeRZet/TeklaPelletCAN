# BATCH — PARAMETER CONFIG TABLE vs RUNTIME RECORD ENGINE — 2026-11-19

## Result

A deeper pass through the parameter/record engine confirms that the runtime record structure is separate from the 370A configuration/code table.

### Runtime record registration

FUN_0801143C registers a record with stride 0x2C:

- +0x08 = panel/CAN index
- +0x0C = source/storage pointer
- +0x10 = type
- +0x14 = value/descriptor
- +0x1C = alternate value/limit
- +0x24 = third descriptor
- +0x2C = access/flag
- +0x30 = metadata

FUN_080115F6 / 0801167A / 080116E6 locate these records by index and return their stored fields.

FUN_08011812 performs type/range checking and writes the accepted value into the storage pointer from record +0x0C.

### Architectural consequence

The 370A entry:

    0x370A
    RAM 0x20021FA6
    handler/code boundary 0x0801AB7E

must not be modeled as a field inside the 0x2C runtime record.

The architecture is:

    parameter configuration table
        |
        +-- parameter ID
        +-- RAM address
        +-- code/handler boundary
        |
        +-- parameter engine
               |
               +-- runtime record 0x2C
                      |
                      +-- storage/value/CAN

This is important because searching for 0x0801AB7E inside the 0x2C record engine is the wrong level.

## Next attack

Recover the separate parameter configuration table/dispatcher around the data region containing the 370A entry, and determine how its code/handler field is consumed.

Do not infer the handler semantics from FUN_0801143C.
