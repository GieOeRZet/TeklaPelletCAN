# MULTIPASS-20 — 0x47/0x48 GRAPH FAMILY SEMANTIC CLOSURE — 2026-11-20

## Scope
Continuation from the 2026-11-20 checkpoint. This pass attacks the remaining OPEN item: semantic identity of registry keys 0x47 and 0x48.

## HARD — direct dispatcher proof

FUN_0803EC18 reads the matched 16-byte registry record and obtains its primary key from offset +0x00.

For records of type byte 5, the code explicitly branches:

- key == 0x47:
  - resolver 0x4A
  - resolver 0x4B
  - resolver 0x4C
  - resolver 0x4D
  - resolver 0x4E
  - then FUN_08048520(...)

- key == 0x48:
  - resolver 0x4F
  - resolver 0x50
  - resolver 0x51
  - resolver 0x52
  - resolver 0x53
  - then the same FUN_08048520(...)

The resolver mapping is independently closed:

0x4A..0x4E -> 0x2261..0x2265 = blower modulation curve points at 20/40/60/80/100% boiler power.

0x4F..0x53 -> 0x2268, 0x226E, 0x226F, 0x2275, 0x227A = exhaust/extra-fan characteristic points.

Therefore the following is now HARD at the dispatcher/data-family level:

0x47 = graph content selector for Family A (blower modulation characteristic).

0x48 = graph content selector for Family B (exhaust/extra-fan characteristic).

This does NOT yet prove that 0x47/0x48 are screen IDs, menu IDs, or titles. They are proven registry/dispatcher keys selecting the two graph data families.

## Important refinement

Earlier ledger entry:
"0x47/0x48 semantic identity is OPEN"

is now SUPERSEDED.

New state:
- semantic family selection: HARD
- exact page/screen identity: OPEN
- exact title TypedText: OPEN
- exact navigation/touch origin: OPEN
- exact configuration gate making 0x48 reachable: OPEN

## 0x47 vs 0x48 graph construction

Both branches use identical X coordinates:

20, 40, 60, 80, 100

and converge on FUN_08048520.

FUN_08048520 updates graph content at parent +0x963C and swaps it into dynamic host parent +0x84F4 via FUN_0802EADE.

Thus the firmware implements one reusable graph class with two data sources, not two unrelated graph implementations.

## Secondary record fields

The records are known to contain different secondary values:
- 0x47 -> 0x8E
- 0x48 -> 0x7E

The current decompiled path does not by itself establish the semantic namespace of these secondary values. Do NOT yet label them as TypedText IDs, bitmap IDs, page IDs, or titles.

The graph branch also prepares local metadata:
- Family A: local_4C = 0x8E
- Family B: local_4C = 0x7E

Because Ghidra's recovered FUN_08048520 prototype is incomplete, the exact ABI/use of these metadata values must be checked against raw Thumb before assigning meaning.

## External sanity check (not firmware proof)

The official Estyma/Tekla installer manual describes "Wentylator wspomagający" as having a characteristic configured analogously to section 4.2.1 "Moc dmuchawy modulacja". This is consistent with the firmware architecture of one reusable five-point graph for two characteristic families.

## 0x300B remains separate

0x68 -> 0x300B is still a separate hard fact. 0x300B selects:
- value 1 -> "Podajnik palnika"
- value !=1 -> "Wentylator wspomagający [%]"

It must not be reused as the Family B graph visibility gate.

## Remaining highest-value attack

P0:
1. Recover raw Thumb ABI at the 0x3EC18 -> 0x48520 call.
2. Determine whether local_4C 0x8E/0x7E is passed as a real argument and where it lands in FUN_08047604 / graph title/resource setup.
3. Trace all incoming references to 0x0807F5EC and identify its object/class/vtable role.
4. Identify the page/content constructor that registers keys 0x47 and 0x48.
5. Trace the navigation event that causes the 0x48 registry entry to refresh.
6. Trace all consumers of Family B parameters upstream to the actual equipment/configuration gate.
7. Separately complete 0x300B writer -> storage -> CAN persistence.

## Confidence ledger

HARD:
- 0x47 selects Family A graph data.
- 0x48 selects Family B graph data.
- both use the same graph construction/update path.
- Family A = 0x2261..0x2265.
- Family B = 0x2268/0x226E/0x226F/0x2275/0x227A.

OPEN:
- 0x8E/0x7E namespace/meaning.
- exact screen/page title for 0x47/0x48.
- exact navigation origin.
- actual Family B visibility/equipment gate.
- 0x0807F5EC object/vtable lifecycle.
