# NewEstyma — CONTINUATION WORKFLOW

## First action in a new chat
Read:
1. NewEstyma/00_AGENT_START_HERE.md
2. NewEstyma/01_PROJECT_STATE.md
3. NewEstyma/03_TOOLING.md
4. NewEstyma/04_FIRMWARE_MANIFEST.md
5. latest DOKUMENTACJA master
6. newest analiza pass

Then inspect repository state and continue from the highest-value OPEN.

## Standard autonomous pass
A. Establish
- verify firmware SHA when BIN is available
- read latest master
- identify newest pass and unresolved OPENs
- inspect tools before creating new ones

B. Scan
- re_scan first
- vtable/interface scan
- object lifecycle scan
- runtime trace correlation
- focused RAW disassembly

C. Prove
For every candidate:
- locate literal/XREF
- inspect RAW bytes
- decode Thumb
- follow caller/callee edges
- establish object/register provenance
- correlate runtime where useful
- classify evidence

D. Automate
If the same manual operation is needed repeatedly:
- extend or create a tool
- add a self-test
- document invocation/output
- use it in the same pass

E. Report
Create:
analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-XX-<NAME>-2026-11-22.md

Include:
- objective
- sources/evidence
- exact addresses
- RAW/PROJECT mapping
- findings
- closures
- rejected interpretations
- remaining OPENs
- next attack
- tool changes

F. Update state
Update NewEstyma/01_PROJECT_STATE.md and the DOKUMENTACJA master, then commit coherently.

## Priority
1. unresolved architectural boundary
2. concrete object/interface mapping
3. cross-layer matrix
4. runtime validation
5. UI semantic completion
6. cleanup

## Evidence levels
FACT/HARD = directly proven.
STRONG = multiple independent clues, final direct proof missing.
INFERENCE = plausible but unproven.
OPEN = unknown.
REJECTED = disproven.

Never upgrade evidence by wording alone.

## 100% policy
There is no arbitrary pass limit. Continue until meaningful OPEN space is closed or exhaustively bounded and the next agent can continue without oral context.
