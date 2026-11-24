# MULTIPASS-14 — 6154 / 17-WRAPPER MATRIX ATTACK — 2026-11-20

## Objective
Continue the 6154 investigation from the already closed Level-3 gate proof. Do not re-prove the gate itself; attack the per-wrapper binding problem.

## Current hard facts carried forward
- 0x180A = 6154; resolver maps it to access level 3.
- 17 independent UI setup paths gate parent+0x23C on access>=3.
- FUN_0802FB04 proves +0x23C increment and +0x284 decrement.
- +0x60 is the current numeric value; +0x64 is its upper bound.
- 4A510 is concretely associated with TypedText 454, "Próg zmniejszania stopnia mocy [%]".
- FUN_08035786 remains geometry/value interpolation, not a proven CAN writer.
- +0x12B and +0x12C are separate context dimensions; +0x12C participates in instance-aware parameter lookup/read/write.
- record engine uses 0x2C stride; +0x08 CAN/index, +0x14/+0x1C value-related fields.
- Do not infer all 17 parameters from the 4A510 label.

## Matrix under investigation
1  4A510 / gate 4A566
2  4A9EC / gate 4AA42
3  4B1D4 / gate 4B22A
4  4C104 / gate 4C15A
5  4E9DC / gate 4EA32
6  4F400 / gate 4F456
7  4F744 / gate 4F79A
8  4FE9C / gate 4FEF2
9  5019C / gate 501F2
10 50458 / gate 504AE
11 50714 / gate 5076A
12 50A28 / gate 50A7E
13 50CE4 / gate 50D3A
14 50FA0 / gate 50FF6
15 5125C / gate 512B2
16 51518 / gate 5156E
17 5FAB4 / gate 5FB0A

## Multi-axis pass results
A. Address-pair revalidation: all 17 constructor/gate pairs remain consistent with the existing batch.
B. Semantic anchor revalidation: the only wrapper currently safely human-labeled is 4A510; do not propagate its label to siblings.
C. Resource/label search: repository text does not contain enough per-wrapper raw disassembly to safely manufacture a 17-row semantic table. This is an evidence boundary, not a failed hypothesis.
D. Reverse-binding strategy remains the highest-value next step: start from known parameter families/TypedText IDs and walk xrefs back into the wrapper constructors.
E. 6154 must remain modeled as a permission gate; parameter identity must be recovered independently.

## New methodological conclusion
The next useful work is not another broad search for the literal 17 addresses. The repository already records those addresses. The high-value attack is to recover the *constructor-local data flow* for each wrapper:
wrapper -> object allocation -> resource/title -> +0x60 initialization -> +0x64 initialization -> callback/object at +0x3D8 -> parameter ID.

Where direct constructor disassembly is absent from indexed repo text, use the raw firmware/decompiler source if available rather than guessing from summaries.

## Required output format for next run
Produce a 17-row table with columns:
wrapper | gate | title/resource | +0x60 source | +0x64 source | +0x3D8 object | parameter ID | instance dimension | CAN/record | confidence.

Use OPEN for every unproven cell.

## Important negative result
A failed repository text/xref search must NOT be converted into a false negative such as "no parameter exists". It only means the current indexed evidence is insufficient.

## User workflow requirement
After this major run, persist the continuity/checkpoint in Git. The user explicitly requested that conversations/continuity be appended after each major analysis run. This file is a technical checkpoint, not a fabricated full raw transcript.
