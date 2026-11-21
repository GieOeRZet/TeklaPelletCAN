# FULL HANDOFF — corrected RE pack

This document points the next chat to the complete handoff state.

## Authority model
Gemini is lead RE/proof authority. OpenAI executes requested extraction tasks, preserves RAW evidence, performs independent checks when appropriate, packages artifacts and maintains documentation.

## Firmware
`FW2213TK_kopia.bin`
SHA-256: `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`

## Corrected indexing
The current RE pack uses base `0x08010000`. Canonical project addresses are unchanged; translate to pack addresses by adding `0x10000`.

The corrected OpenAI RE Explorer is based on this mapping.

## Current OPEN-1
Prove:
`[0x20008D60]` initialization/value -> vtable/interface -> slot 0 exact target -> TX path.

Known hard chain after the unresolved slot target:
`0x200244EC -> CanTxTask -> FUN_08061734 -> CAN2`.

Known hard facts and all earlier evidence are in:
`MASTER-CONTEXT-ETAP1-52-FINAL.md` and `OPENAI_FULL_SUMMARY_ETAP1-52.md`.

Do not promote `FUN_0806E59C` to slot 0 without direct firmware proof.
