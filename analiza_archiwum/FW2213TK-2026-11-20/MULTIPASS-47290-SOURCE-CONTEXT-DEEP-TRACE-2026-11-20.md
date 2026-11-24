# MULTIPASS — 47290 SOURCE/CONTEXT DEEP TRACE — 2026-11-20

## Scope

This batch deliberately continues from the previous checkpoint and does NOT restart the already closed geometry/resource work.

Primary target:
`0803EC18 -> 0803EE30 -> 080484B0 -> 08047334 -> param_7`

Secondary targets:
- identity of the object called `record`,
- origin/role of `record+0x08`,
- caller context,
- relation to `DAT_0803EEC0`,
- relation to parameter IDs,
- relation to Language selector 90,
- relation to the 0803E5AC runtime tree.

Source binary:
`FW2213TK_kopia.bin`
SHA-256:
`1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`
size 2,031,616 B.

---

# 1. MULTIPASS PROTOCOL

Performed independent passes over:
1. raw BIN bytes at 0803EC18,
2. raw BIN bytes at 0803EE30,
3. raw BIN bytes at 08048468/4B0/4F0/520,
4. raw BIN bytes at 08047334,
5. BL target decoding,
6. all raw BL xrefs to 0803EC18,
7. all raw BL xrefs to 0803EE30,
8. all raw BL xrefs to 080484B0,
9. caller 08048624,
10. caller 0807EB36,
11. register provenance for r4,
12. stack argument provenance,
13. exact offsets +0x07/+0x08/+0x0C,
14. immediate panel-ID extraction from 0803EC18,
15. parameter-table correlation for those IDs,
16. DAT_0803EEC0 raw bytes,
17. raw-pointer occurrence scan for 0x20011534/0x20011650/0x20011594,
18. 0803E714 comparison,
19. selector 90 / Language cross-check,
20. eight TypedText-language table cross-check,
21. Home-root direct-tree cross-check,
22. 47290 151/152 cross-check,
23. old-project geometry exclusion,
24. contradiction test against "47290 = language selector",
25. contradiction test against "record = 0x2C parameter-engine record",
26. framework/vtable possibility check,
27. 08048468/4B0/4F0 role separation,
28. caller-context structure hypothesis,
29. parameter IDs 74..83 semantic correlation,
30. final evidence classification.

---

# 2. NEW HARD CORRECTION: "record" IS NOT THE 0x2C PARAMETER-ENGINE RECORD

This is the most important result of this batch.

Earlier notes used the word `record` for the object whose fields are read by `0803EE30`.

Raw binary now proves that this object is supplied through **r4**, and r4 is callee-saved across `FUN_0803EC18`.

At both direct call sites of `FUN_0803EC18`:

### Caller A
`FUN_08048624`:
- function prologue contains `mov r4,r0`.

### Caller B
`FUN_0807EB36`:
- function prologue also contains `mov r4,r0`.

Therefore inside `FUN_0803EC18`, the structure later called "record" is the caller's original object/context in r4.

This is **not** enough to say what class it is, but it means:

`record+0x08`

should currently be described as:

> field +0x08 of the caller/model/context object passed through r4

and NOT automatically as the generic CAN parameter record.

This removes an important possible category error.

---

# 3. ALL DIRECT CALLERS OF 0803EC18

Raw Thumb BL scan of the entire BIN found exactly two direct BL targets:

| call site | caller |
|---|---|
| 0x0804864A | FUN_08048624 |
| 0x0807EB5C | FUN_0807EB36 |

No other direct BL was found.

This does not rule out indirect/vtable entry into 0803EC18, but it makes the two direct caller contexts very important.

---

# 4. 0803EE30 IS INTERNAL, NOT A PUBLIC GLOBAL DISPATCH ENTRY

Raw BL scan found:

- exactly one direct caller of `FUN_080484B0`: `0x0803EE30`
- exactly one direct caller of `FUN_08047334`: `0x080484D4`
- no direct BL to `0803EE30` from elsewhere.

Thus the chain is:

`FUN_0803EC18`
→ `FUN_0803EE30`
→ `FUN_080484B0`
→ `FUN_08047334`

The only known route into 47290's update renderer is therefore through this internal model/update path.

---

# 5. EXACT STACK ARGUMENT PROVENANCE — REVALIDATED FROM RAW BYTES

At `0803EE18`:

`LDR r1,[r4,#0x08]`

immediately followed by:

`STR r1,[sp,#0x08]`

Therefore:

`stack_arg2 = *(r4 + 0x08)`

At `0803EE1E`:

`LDRB r1,[r4,#0x07]`

then:

`STR r1,[sp,#0x04]`

Therefore:

`stack_arg1 = *(u8*)(r4 + 0x07)`

At `0803EE22`:

`LDRH r1,[r4,#0x0C]`

then:

`SUBS r1,#1`

then:

`STR r1,[sp,#0x00]`

Therefore:

`stack_arg0 = *(u16*)(r4 + 0x0C) - 1`

This is direct BIN proof.

So the bridge is:

`r4+0x0C -> slot/index`
`r4+0x07 -> variant/state byte`
`r4+0x08 -> pointer to six-label TypedText array`

---

# 6. HARD LABEL-ARRAY BRIDGE

At `080484B0`, the stack argument at +0x08 is copied into the seventh argument of `FUN_08047334`.

Therefore:

`param_7 = *(r4 + 0x08)`

and `FUN_08047334` consumes:

`TypedTextID = param_7[slot]`

This is now a clean four-step hard chain:

`caller object r4`
→ `r4+0x08`
→ `six-element u16 TypedText array`
→ `FUN_08047334`
→ `slot label`

The exact six values remain unresolved.

---

# 7. WHAT 0803EC18 ACTUALLY DOES

The raw function is not a trivial language-list constructor.

It contains a repeated sequence:

`panel index`
→ `FUN_08036FF2(context,index)`
→ store resolved value into an object field.

Immediately visible hardcoded panel IDs include:

- `0x4A`
- `0x4B`
- `0x4C`
- `0x4D`
- `0x4E`
- `0x4F`
- `0x50`
- `0x51`
- `0x52`
- `0x53`

Decimal:

- 74..83.

The values are fetched through `FUN_08036FF2`, not hardcoded as runtime values.

This is strong evidence that 0803EC18 belongs to a parameter/configuration/model update path.

---

# 8. SEMANTIC CORRELATION OF 0x4A..0x53

The panel parameter map correlates the first IDs with:

- panel 74 / CAN-side `0x2252`: Burner burner feeder
- panel 75 / `0x2261`: blower characteristic 20%
- panel 76 / `0x2262`: blower characteristic 40%
- panel 77 / `0x2263`: blower characteristic 60%
- panel 78 / `0x2264`: blower characteristic 80%
- panel 79 / `0x2265`: blower characteristic 100%
- panel 80 / `0x2268`: currently catalogued as value 20 / candidate
- panel 81 / `0x226E`: unresolved
- panel 82 / `0x226F` or adjacent panel mapping remains to be independently closed
- panel 83 / next parameter remains to be independently closed.

Important:
this correlation is from the project parameter map, not from a semantic guess about 47290 itself.

The first six IDs therefore point strongly toward a **burner / blower characteristic configuration family**, not language selection.

But this does NOT yet prove that 47290 displays these six parameters. They are values fetched in the larger 0803EC18 model/update path.

---

# 9. IMPORTANT CONSEQUENCE FOR LANGUAGE HYPOTHESIS

The language selector hypothesis must now be split into two separate questions:

### Q1
Does firmware have a Language setting?

**YES — HARD.**

- menu selector 90 = Language,
- parameter ID 3 = Language,
- RAM 0x20021FAA,
- range 0..30,
- eight TypedText language tables.

### Q2
Is 47290 the UI component used by selector 90?

**NOT PROVEN.**

The newly traced 0803EC18 path is clearly parameter/model heavy and directly resolves panel IDs 74..83.

Therefore the current evidence does **not** support:

`47290 = Language selector`

and actually makes that interpretation weaker.

---

# 10. 47290 ITSELF REMAINS A GENERIC SIX-SLOT SELECTOR

Hard properties remain:

- parent/root candidate: `0803E5AC + 0x92DC`,
- six slots,
- X=100,
- Y=50,84,118,152,186,220,
- bitmap pair 151/152,
- labels supplied dynamically,
- update path through 484B0 → 47334.

The renderer does not encode "Language".

This is exactly what we would expect from a reusable component whose semantic labels are supplied by an external object.

---

# 11. 08048468 / 080484B0 / 080484F0 ARE THREE PARALLEL UPDATE PATHS

The same 0803EC18 dispatcher can call three sibling update bridges:

- `08048468`
- `080484B0`
- `080484F0`

The existing tree analysis places these against different child/content regions.

Known relationships:

- `48468` updates content host around root +0x84F4,
- `484B0` updates the 47290 component at root +0x92DC,
- `484F0` is a sibling update path for another root child,
- `48520` handles another content/large-component path.

This strongly suggests 0803EC18 is a **multi-widget screen/model refresh dispatcher**, not a dedicated language routine.

---

# 12. DAT_0803EEC0 — RAW BINARY CONFIRMATION

At raw offset `0x3EEC0`, BIN bytes are:

`34 15 01 20`
`50 16 01 20`
`94 15 01 20`

These are:

- 0x20011534
- 0x20011650
- 0x20011594

So the previous identification of `DAT_0803EEC0` as a pointer table is directly confirmed from the uploaded BIN.

The three RAM objects are runtime structures.

A raw BIN occurrence scan found each of these RAM addresses exactly once, at this pointer table.

Therefore their contents are runtime-initialized; they are not static arrays embedded directly at those RAM addresses in flash.

---

# 13. WHY THE SIX LABEL IDs ARE STILL NOT RECOVERED

The pointer at `r4+0x08` is a runtime field.

The raw BIN does not contain a second literal occurrence of that RAM address.

Therefore the next trace cannot simply be:

"search BIN for 0x2001153C".

The pointer is likely assigned through:
- object construction,
- model registration,
- copied descriptor,
- vtable/factory path,
- runtime table initialization.

This is an important methodological boundary.

---

# 14. 08048624 — DIRECT CALLER A

Raw bytes show:

- `push {r3,r4,r5,lr}`
- `mov r4,r0`
- reads `r4+0x3B8`
- uses a table/indirect addressing path,
- calls `0803EC18`.

Thus 48624 is itself an object-method-like function operating on the same object whose r4 becomes the 0803EC18 context.

No direct BL to 48624 exists in the raw scan.

This strongly suggests vtable/indirect dispatch.

Do NOT invent its semantic name yet.

---

# 15. 0807EB36 — DIRECT CALLER B

Raw bytes show:

- `push`
- `mov r4,r0`
- loops over object-derived data,
- calls `0803EC18`.

Again, r4 is the original object.

The function lies in the later firmware/framework address region and should not automatically be labelled as TouchGFX framework code. It needs a vtable/class trace.

---

# 16. CONTRADICTION TEST — LANGUAGE SCREEN

If 47290 were a fixed six-language selector, we would expect at least one of:

A. six fixed TypedText IDs corresponding to language names;

B. a direct read of Language parameter ID 3;

C. a direct navigation edge from selector 90 to 47290;

D. a constructor that fills r4+0x08 with language-name IDs;

E. six values that decode as language names in the eight language tables.

None is closed yet.

Instead, the only newly closed upstream path feeds a parameter-heavy dispatcher.

Status:

**47290 = language selector: WEAK / OPEN, leaning negative.**

---

# 17. CONTRADICTION TEST — AUTOMATIC UPDATER

No hard chain was found:

`boot/update start`
→ `language choice`
→ `47290`.

No hard update-screen text family has been linked to 47290.

Therefore the updater-language hypothesis remains weak.

The user-provided manual's automatic-update procedure remains consistent with that conclusion.

---

# 18. WHAT WE SHOULD NOT DO

Do NOT:

- map 47290 labels to language names just because selector 90 exists;
- assume six slots means six languages;
- call r4 a generic CAN record;
- use the 0x2C record-engine layout here without a direct type/data-flow proof;
- infer the six IDs from nearby flash constants;
- infer them from the old web/card implementation;
- infer them from the six-slot geometry.

---

# 19. NEXT HIGH-VALUE ATTACK

The next target is no longer "search more strings".

It is:

## A — recover the class/descriptor behind r4

Trace:

`08048624 / 0807EB36`
→ vtable/factory
→ object constructor
→ initialization of:
- +0x07
- +0x08
- +0x0C
- +0x3B8
→ source of +0x08 pointer.

## B — recover pointer contents

Once the writer to `r4+0x08` is identified:

`pointer`
→ six u16 IDs
→ each ID
→ eight language tables
→ actual strings.

## C — trace selector 90 independently

`menu row selector 90`
→ touch/callback
→ navigation/content host
→ constructor
→ check whether it reaches 47290.

## D — trace parameter 3 independently

`Language ID 3`
→ read/write function at 0x08011D6C
→ RAM 0x20021FAA
→ mapper 0..30
→ language table selection.

If D reaches the same object as A, language hypothesis becomes strong.
If D reaches another UI class, 47290 language hypothesis is effectively rejected.

---

# 20. CURRENT EVIDENCE MATRIX

| Item | Status |
|---|---|
| 47290 six-slot component | HARD |
| 47290 vertical geometry | HARD |
| 151/152 normal/selected | HARD |
| 47290 labels are external | HARD |
| label pointer = r4+0x08 | HARD |
| r4 is caller context/object | HARD |
| r4 is generic 0x2C CAN record | REJECTED / unsupported |
| 0803EC18 direct callers | HARD: 48624, 7EB36 |
| 0803EC18 resolves IDs 0x4A..0x53 | HARD |
| 0x4A..0x53 are parameter indices | HARD |
| first six correlate to burner/blower family | STRONG |
| selector 90 = Language | HARD |
| parameter 3 = Language | HARD |
| eight language tables | HARD |
| 47290 = Language selector | OPEN / leaning negative |
| 47290 = updater language selector | WEAK / OPEN |
| selector 90 -> 47290 | OPEN |
| Language parameter -> 47290 | OPEN |
| exact six TypedText IDs | OPEN |
| exact writer of r4+0x08 | OPEN |
| exact class/vtable of r4 | OPEN |

---

# 21. CONTINUITY FOR NEXT AGENT

Start from these exact facts.

Do not restart 47290 geometry.

Do not restart 151/152.

Do not restart eight language tables.

Do not restart selector 90 = Language.

Do not restart parameter 3 = Language.

Continue with:

`08048624`
and
`0807EB36`

then identify the object type and the writer of:

`object + 0x08`.

The decisive question is:

> What six u16 values are stored behind r4+0x08 at the moment 0803EE30 calls 080484B0?

That is the shortest route to either proving or killing the language-selector hypothesis.

Evidence discipline:
HARD / STRONG / CORRELATION / OPEN.
No semantic closure without a data-flow or navigation proof.
