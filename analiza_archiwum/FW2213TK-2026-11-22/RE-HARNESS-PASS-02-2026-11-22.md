# RE Harness Progress — 2026-11-22 — pass 2

## Now added

- `software/re_harness/adapter.py`: backend-neutral ARM emulator contract.
- `software/re_harness/replay.py`: deterministic READ/WRITE replay cases.
- `software/re_harness/evidence.py`: converts runtime trace events into evidence records/Markdown.

## Important evidence boundary

WRITE replay currently encodes only positions already supported by evidence:
command, PID and type. It deliberately does **not** invent the remaining value-byte
layout. The concrete backend must inject the exact firmware frame representation.

## Next closure pass

1. connect a real ARM backend if the existing emulator package/source is available,
2. instrument every memory store,
3. capture first writer of 0x20008D60,
4. resolve [0x2002466C+0x14] -> vptr -> slot0,
5. capture CAN replay traces and RAM deltas.

No percentage increase is claimed from scaffolding alone.
