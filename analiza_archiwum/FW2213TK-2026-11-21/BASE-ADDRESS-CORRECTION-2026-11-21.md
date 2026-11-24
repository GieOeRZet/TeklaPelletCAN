# RE Pack Base Address Correction — 2026-11-21

## Firmware
- File: `FW2213TK_kopia.bin`
- Size: `0x1F0000` = 2,031,616 B
- SHA-256: `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`

## Correct RE pack
The corrected pack is `FW2213TK_RE_PACK_08010000.zip`.

Its base address is:

`0x08010000`

The canonical addresses used by the project remain unchanged. For RE-pack indexed data:

`RE_PACK_ADDRESS = CANONICAL_PROJECT_ADDRESS + 0x10000`

Examples:
- `0x0800FF50 -> 0x0801FF50`
- `0x08063C3E -> 0x08073C3E`
- `0x0806E59C -> 0x0807E59C`

A direct byte comparison confirmed that the corrected pack window `0x08010000..0x08014000` matches the beginning of the authoritative BIN byte-for-byte.

## Rules
- BIN is the source of truth.
- RE pack is an index/accelerator.
- Critical disassembly must be verified against raw bytes.
- Do not silently change canonical firmware addresses.
- The corrected OpenAI RE Explorer internally accounts for the `+0x10000` pack offset.
