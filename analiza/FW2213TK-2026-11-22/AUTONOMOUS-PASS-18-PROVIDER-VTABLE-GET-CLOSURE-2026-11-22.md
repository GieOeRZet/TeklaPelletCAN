# PASS 18 CORRECTION — provider vtable evidence retraction — 2026-11-22

This correction supersedes the earlier PASS 18 claim about provider vtable slots.

## HARD that remains valid
- 0x20008D64 is the concrete provider object.
- Constructor 0x0800DB08 assigns vptr 0x080A31F0.
- FUN_0801143C performs the indirect provider call through the vptr stored at manager+0x7178.

## RETRACTED
The earlier claims that vtable[0] = 0x0801DB31 and vtable[1] = 0x0801DB79, and that these are proven GET/SET implementations, are NOT proven.

Canonical RAW verification under PROJECT = 0x08000000 + RAW shows:
- PROJECT 0x080A31F0 -> RAW 0x0A31F0, whose bytes are 0xFF in the canonical BIN.
- PROJECT 0x0801DB31 -> RAW 0x01DB31, not an executable function entry.
- PROJECT 0x0801DB79 -> RAW 0x01DB79, also not a valid function entry.

Those targets may be runtime-materialized/decompressed, but that requires runtime write/materialization or actual indirect-call evidence.

## Tooling correction
The provider scanner remains a candidate scanner only. It must not promote a slot from a Thumb-looking pointer alone. Runtime materialization and/or an actual indirect-call observation is required.

## Current status
Provider object/vptr: HARD.
Provider interface slots: OPEN.
Provider GET/SET concrete implementations: OPEN.

This is an evidence downgrade of the slot claims, not a loss of the provider object closure.
