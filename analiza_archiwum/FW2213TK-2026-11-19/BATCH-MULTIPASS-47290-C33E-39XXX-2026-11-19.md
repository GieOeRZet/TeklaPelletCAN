# BATCH — 2026-11-19 — multi-pass binary deepening: Home/47290/C33E/39A48

## 0. Source and method

Analyzed the uploaded `FW2213TK_kopia.bin` directly with ARM Thumb disassembly and cross-reference scanning. This batch is based on hard binary evidence, not prior semantic assumptions.

Important correction retained: `FUN_08047290` is a **vertical six-slot component**, not the bottom bar.

---

## 1. Home-root direct-call map is confirmed at runtime address 0x0803E5AC

`FUN_0803E5AC` directly constructs/attaches these children:

- `+0x380` -> `FUN_08038ED0`
- `+0x3BC` -> `FUN_08041E1C`
- `+0x3EC` -> `FUN_08041E1C`
- `+0x41C` -> `FUN_08047230`
- `+0x42C` -> repeated constructor via `FUN_0800DCD4`
- `+0x84F4` -> `FUN_0802E716`
- `+0x8F70` -> `FUN_08047244`
- `+0x92DC` -> `FUN_08047290`
- `+0x963C` -> `FUN_08047604`
- `+0xA26C` -> `FUN_08047E54`
- `+0xA5FC`, `+0xA628` -> `FUN_08038ED0`
- `+0xA654`, `+0xA680` -> bitmap/resource objects via `FUN_0802DF08`
- `+0xA6AC` -> `FUN_08047FD4`
- `+0xA6BC` -> `FUN_08047FE8`
- `+0xA6CC` -> `FUN_08047FFC`
- `+0xA6DC` -> `FUN_08047FE8`

The direct parent/add helper is `FUN_08030380`; it writes child.parent at +0x14 and links the child into the parent's +0x28 child chain.

Therefore these are genuine object-tree edges from `0803E5AC`, not inferred proximity.

---

## 2. 47290 is a real six-slot vertical selector/list

`FUN_08047290`:

- object base in the Home root: `root + 0x92DC`
- creates six records with stride `0x40`
- first record at `+0xA8`
- each record is positioned vertically
- X = 100 (via vtable setter)
- Y = 50 + 34*slot
- therefore Y positions are:
  - slot 0: 50
  - slot 1: 84
  - slot 2: 118
  - slot 3: 152
  - slot 4: 186
  - slot 5: 220

This is hard geometry and rules out the bottom-bar interpretation.

The constructor calls `FUN_0800DCD4(dest, init_fn, stride, count)`. `DCD4` is a generic repeated-function dispatcher:

- r0 = current destination
- r1 = initializer callback
- r2 = stride
- r3 = count
- calls callback for each slot and advances by stride.

Thus the values at `DAT_0804732C` and `DAT_08047330` are **function pointers/callbacks**, not arrays of raw records.

---

## 3. 47290 slot rendering is decoded much further

`FUN_08047334` is the slot update/render function.

For the selected/clamped slot:

1. Selects record:
   `object + 0xA8 + slot*0x40`
2. Sets the visual geometry.
3. Creates/updates a child via `FUN_0804C392`.
4. Attaches that child through the object's +0x60 component.
5. Reads a TypedText ID from an external array:
   `param_7[slot]`
6. Builds/updates a text object around `object + 0x25C + ...`.
7. Sets text geometry based on the per-slot record.
8. Attaches the text.
9. Calls `FUN_0804C320` with four halfwords:
   - 0x97 = 151
   - 0x98 = 152
   - 0x97 = 151
   - 0x98 = 152

This establishes that the six slots have a **normal/selected bitmap pair using resources 151/152**.

The component therefore is not merely six text rows. It is a six-item composite selector with:
- per-slot geometry,
- bitmap state,
- TypedText label,
- touch/update state.

---

## 4. 484B0 is the public/update bridge into 47334

`FUN_080484B0`:

- operates on `root + 0x92DC`
- marks `root + 0x9301 = 1`
- converts the slot/index argument to u16
- forwards the runtime arguments to `FUN_08047334`.

The important caller is `FUN_0803EE30`.

At that call site:

- r0 = component pointer
- r1 = signed halfword from caller record +0x2
- r2/r3 = runtime values
- stack arguments include:
  - `[record+0x0C] - 1`
  - byte `[record+0x07]`
  - pointer `[record+0x08]`

Because 47334 consumes its seventh argument as `param_7`, the final pointer is concretely:

`param_7 = *(record + 0x08)`

and then:

`TypedTextID = param_7[slot]`

This is the next target for resolving the six actual labels.

---

## 5. 3EE30 belongs to a larger configuration/parameter builder

`FUN_0803E714` and the surrounding 3E7xx–3EBxx code build arrays of TypedText/configuration IDs into a runtime object.

A global descriptor pointer at literal `0x0803EEC0` resolves to RAM address:

- `0x20011534`
- `0x20011650`
- `0x20011594`

The descriptor at `0x20011534` is repeatedly used with offsets such as:
- +0x74
- +0x7C
- +0x90
- +0x9C
- +0xC4
- +0xDC
- +0xF4
- +0x104
- +0x10C
- +0x110

through `FUN_0803EFDA`, which copies a source array of u16 IDs into the object's runtime list at +0x20.

Therefore the six-label list is not hardcoded directly inside 47290. It is supplied by the active configuration/model descriptor.

This is an important architectural point: **47290 is a reusable renderer; the actual six labels come from the active configuration path.**

---

## 6. First semantic warning: 0803E5AC may be broader than a literal "Home screen"

The direct tree is confirmed, but several child components carry large parameter/error language tables.

Examples from their resource pointers:

### 47244
String pool starts around:
- "Interruptor Delta OFF [°C]"
- "Sekundární modulace MIN [%]"
- "Sekundární modulace MAX [%]"

### 47290
String pool starts around:
- "... roštu [kg]"
- "Poškození venkovního čidla"
- "Ventilátor zapálení (dřevo)"
- "Čas modulace..."

### 47604
String pool includes:
- "MIN [%]"
- "Sekundární modulace MAX [%]"
- "Průměrná doba zapálení [s]"
- "Power supply fai..."

### 47E54
String pool includes:
- "Komunikace s modulem Mini 7"
- "Komunikace s modulem Mini 4"
- related communication/error messages.

These are strong evidence that the 0803E5AC object is a **large runtime screen/model host containing many parameter/configuration subcomponents**, not a simple static home-card constructor.

Do not discard the previous Home-root hypothesis, but do not treat every child as a visual Home widget. The tree is real; its semantic layer still needs separation.

---

## 7. C33E → 424C4 chain is now structurally closed one level deeper

`FUN_0803C33E`:

- initializes object
- creates helper at `+0x84C`
- calls:
  `FUN_080424C4(r0 = object+0x84C, r1 = object, r2, r3)`

`FUN_080424C4` is now proven to be a tiny object initializer:

- writes its own class/static pointer at +0
- writes parent at +0x04
- writes two 32-bit parameters at +0x08/+0x0C.

Thus:

`C33E + 0x84C` is a **real child/helper object whose parent pointer is C33E**.

It is NOT the parent of +0x85C.

Then C33E initializes:
- +0x330
- +0x35C
- +0x85C
- +0x888
- +0x8B4
- +0x8E0
etc.

The +0x85C child remains the bitmap slot for the closed 370A → 11/12/13 chain.

---

## 8. C33E/C5B4 bitmap subtree

`FUN_0803CACC` is now concrete:

- adds 0x0A to its input
- writes the resulting u16 as Typed/bitmap resource ID
- destination is `object + 0x85C`
- calls `FUN_080307BC`.

Therefore if the input is 1/2/3, CACC writes 11/12/13.

This is the lower-level implementation of:

`370A selector 1..3 → C33E +0x85C → resource 11/12/13`

`FUN_0803C5B4` is NOT directly called by BL anywhere; it is a method likely reached indirectly through a class/vtable. Do not treat it as the direct bitmap writer.

---

## 9. Three sibling composite constructors remain a key unresolved variant layer

The binary has:

- `FUN_08039A48`
- `FUN_08039B30`
- `FUN_08039C18`

Each is called by a dedicated wrapper:

- `08038036 → 08039A48`
- `08038058 → 08039B30`
- `0803807A → 08039C18`

All three converge on `FUN_0803C33E`.

Each wrapper reads:
- caller object +0x108
- caller object +0x120 / +0x124

and supplies those model pointers into the sibling constructor.

The sibling constructors differ in model thresholds and helper selection, e.g.:

- 39A48 checks first model value against 0x0B64
- 39B30 checks against 0x14C4
- 39C18 checks against 0x14C4

and use different helper constructors for the secondary objects.

This is strong evidence of a **family of concrete UI/model variants**, not one widget with only a changed string.

However, there is still no hard static edge proving that 39A48/39B30/39C18 are direct children of 0803E5AC. Their immediate wrappers are the correct next point for variant/factory tracing.

---

## 10. Next mandatory passes

Do NOT restart from 370A.

### Pass A — resolve 47290 labels
Trace the RAM structure at 0x20011534 and especially:
- +0x08
- +0x74/+0x7C/+0x90/+0x9C/+0xC4/+0xDC/+0xF4/+0x104/+0x10C/+0x110

Goal: obtain the actual six TypedText IDs used by 47290 in every configuration branch.

### Pass B — resolve 47244
Decode:
- constructor
- +0x60 child
- 34A90 child creation
- text IDs
- bitmap IDs
- parent chain
- runtime update path.

### Pass C — resolve 2E716
Continue:
- 34A90
- 34D74
- all TypedText/resource IDs
- parent/child links
- callbacks.

### Pass D — reverse the three 39xxx siblings backwards
Trace:
`39A48/39B30/39C18 → wrappers 38036/58/7A → caller/factory/indirect dispatch`

Do not assume Home until a hard edge is found.

### Pass E — resolve C33E helper object
Trace the object created by 424C4:
- static pointer 0x0809F7D0
- all methods/uses
- where its parent C33E is later used
- whether it controls visibility/configuration.

### Pass F — identify actual bitmap display parent
Starting from:
`C33E +0x85C`
walk:
`+0x84C → 424C4 → C33E → 39xxx → wrapper → factory`

The goal is the first hard edge back into the main screen tree.

---

## 11. Hard conclusions from this batch

1. 47290 is vertical six-slot selector/list, Y=50/84/118/152/186/220.
2. 47290 uses bitmap resources 151/152 for its slot state.
3. 47290 gets its labels dynamically from a runtime u16 array.
4. 484B0 is the update bridge into 47334.
5. 47334's label array comes from caller record +0x08.
6. 3E714 builds configuration-dependent TypedText arrays into runtime memory.
7. C33E +0x84C is a real helper child; its parent is C33E.
8. C33E +0x85C is the actual runtime bitmap child for 11/12/13.
9. 39A48/39B30/39C18 are three concrete sibling implementations converging on C33E.
10. There is still no proof that those three are direct Home children.
11. 0803E5AC has a genuine object tree, but several children are clearly parameter/error/configuration-heavy; semantic labeling must be separated from tree topology.

## Evidence rule

Everything above is based on the uploaded firmware disassembly. Where semantic labels remain unresolved, they are explicitly marked unresolved rather than guessed.
