# MULTIPASS-22 — DEEP CROSS-CHECK / HOME-CWU-174 / 2105-CONFIGURATION / MANUFACTURER-CORRELATION
Data: 2026-11-20

## Executive result

This pass was deliberately split into independent axes rather than repeating bitmap extraction:

1. firmware resource architecture,
2. 174/175/176/179 asset family,
3. Home user anchors,
4. generic Bitmap writer/animation machinery,
5. Heating configuration 0x2105,
6. CO1..CO4 capability fan-out,
7. official Estyma/Tekla installer documentation,
8. current web-card implementation as a secondary artifact only,
9. contradiction / stale-hypothesis audit.

No claim is promoted to HARD merely because a number or geometry happens to look plausible.

---

# PASS 01 — 174 is a RESOURCE, not a widget

Known hard resource table facts:

- 174 = 38x40
- 175 = 37x40
- 176 = 38x40
- 179 = 67x151
- bitmap descriptor table = runtime 0x08064450
- descriptor stride = 0x14
- 188 firmware resources 000..187
- runtime bitmap base = 0x08010000

The correct abstraction remains:

Bitmap ID -> BitmapData/resource table -> Bitmap/child instance(s) -> parent/component -> screen.

This is reinforced by the generic writer:

FUN_080307BC writes the resource ID into child +0x26 and then obtains resource dimensions through virtual methods +0x38/+0x3C.

Therefore a resource ID cannot be treated as a unique widget identity.

---

# PASS 02 — USER ANCHOR 174

User observation closes three facts independently of firmware call-site:

- 174 = CWU/DHW icon
- Home slot 6 from left / 2nd from right
- the same visual appears inside a composed hot-water-tank graphic on another screen

The third observation is especially important.

It rejects:

174 == Home-only widget identity

and strongly supports:

174 == reusable semantic water/CWU bitmap.

The correct next trace is therefore not:

174 -> Home constructor

but:

174
 -> all resource-resolution paths
 -> every Bitmap child receiving it
 -> parent class/context
 -> geometry
 -> state
 -> screen/factory
 -> touch/callback

---

# PASS 03 — 174/175/176 family does NOT prove three states

Dimensions:

174 = 38x40
175 = 37x40
176 = 38x40

The atlas groups them as tap/water family.

This is useful family evidence, but dimensions alone do NOT establish:

- 174 = ON
- 175 = OFF
- 176 = alarm

Those assignments remain OPEN until the resource-selection call-sites are recovered.

---

# PASS 04 — 179 is a high-value composite target

179 = 67x151.

Because the user sees 174 as part of a larger hot-water-tank composition, 179 must be treated as a candidate anchor for that screen.

However:

179 + 174 visual association != firmware proof of parent/child relation.

Two possibilities remain:

A. 179 is a background/base graphic and 174 is an independently attached Bitmap child.

B. 179 is unrelated to the observed composite and the screen assembles another water graphic from multiple assets.

The only decisive test is call-site/constructor tracing.

---

# PASS 05 — generic Bitmap writer closes the mechanism

FUN_080307BC is already independently established as the concrete resource setter.

The important field is:

child +0x26 = resource ID

The function then resolves dimensions and feeds geometry through virtual methods.

This means a direct call such as:

FUN_080307BC(child, 0xAE)

would be decisive proof for 174, but absence of a literal call is NOT proof of absence because the firmware uses table-driven and virtual machinery.

Therefore the correct search set is:

- literal 0xAE / decimal 174
- table values
- indirect setters
- constructor data
- virtual dispatch
- neighboring 0xAF/0xB0
- parent constructors around water/CWU UI

---

# PASS 06 — animation engine is another reusable-resource mechanism

The firmware contains a generic animation engine:

FUN_0803079A:
  +0x30 = first resource
  +0x32 = last resource

FUN_080307AE:
  +0x34 = tick count

FUN_08030708:
  +0x36 = direction
  +0x37 = enable

FUN_08030640:
  advances current resource and eventually calls the common resource setter.

This is critical architectural evidence:

resource IDs are first-class runtime state.

Therefore a resource such as 174 can be selected by:
- constructor,
- state dispatcher,
- animation/state machine,
- table lookup,
- virtual callback,

without appearing as a simple hard-coded Home assignment.

---

# PASS 07 — manufacturer documentation independently confirms multi-screen reuse architecture

The official Tekla/Estyma installer manual describes the system as modular:

- heating circuits,
- DHW/CWU,
- solar,
- buffer,
- cascade,
- additional fuel store,
- configurable modules.

It explicitly shows different installation profiles.

Profile 1:
CO + CWU + Buffer.

Profile 2:
CO1 + CO2 + CWU.

Profile 3:
CO1 + CO2 + CWU + Buffer.

Official documentation therefore independently supports the idea that the same semantic UI concepts are reused under different installation configurations.

Source:
official Estyma/Tekla installer manual.

---

# PASS 08 — official documentation closes the meaning of "number of CO circuits"

The manual states that the configuration contains "Ilość obwodów grzewczych" and that profiles expose CO / CO1 / CO2 depending on installation.

The wiring profiles show:

Profile 1 -> CO + CWU + Buffer
Profile 2 -> CO1 + CO2 + CWU
Profile 3 -> CO1 + CO2 + CWU + Buffer

This is independent evidence that CO1/CO2 are capability-dependent objects rather than arbitrary screen decoration.

---

# PASS 09 — firmware 0x2105 is consistent with this capability model

Current source-of-truth mapping:

internal 0x10E -> CAN 0x2105 = Heating configuration.

The parameter itself is:

- u8
- range 0..4
- default 1
- local storage 0x20021FAF

This is NOT merely a guessed label: it is supported by the raw firmware mapping and parameter record.

---

# PASS 10 — direct firmware capability fan-out

FUN_0803C178 resolves the active model and applies these exact gates:

selector 1:
  internal 0x10E / CAN 0x2105
  visible iff value >= 1

selector 2:
  0x2105
  visible iff value >= 2

selector 3:
  0x2105
  visible iff value >= 3

selector 4:
  0x2105
  visible iff value >= 4

This is the strongest current firmware proof that Heating configuration controls the availability of four separate CO selectors.

It is still NOT proof of the exact C064 construction bridge.

---

# PASS 11 — important distinction: capability vs object construction

We now have two separate facts:

A. capability/visibility:
0x2105 -> selectors 1..4 -> thresholds 1..4

B. object architecture:
+0x12B = class/type
+0x12C = instance
FUN_08036FF2 resolves family-of-4 records using instance-1.

The missing edge is:

0x2105
 -> selector
 -> concrete CO object/class
 -> C064 / +0x12B/+0x12C
 -> concrete widget/parameter family

That edge remains OPEN.

This separation prevents a common reverse-engineering error: treating a visibility gate as if it were the constructor itself.

---

# PASS 12 — 0x2105 and 0x10E must not be swapped

Current authoritative mapping:

0x10D -> 0x3505 = outside-temperature sensor configuration
0x10E -> 0x2105 = heating configuration
0x10F -> 0x2106 = hot-water configuration
0x110 -> 0x2108 = solar configuration
0x111 -> 0x2107 = buffer configuration

Older notes using:

0x10E -> 0x3505
0x10F -> 0x2105

are stale and rejected.

---

# PASS 13 — manufacturer access levels corroborate the firmware access model

Official manual:

- level 0 = user
- level 1 = installer, code 0900
- menu hides parameters according to access level.

Firmware independently resolves:

0 -> level 0
900 -> level 1
999 -> level 2
6154 -> level 3

Therefore the access-level mechanism is not an invented reverse-engineering construct; the manufacturer documentation independently confirms the architectural concept.

---

# PASS 14 — 6154 is therefore a real firmware capability boundary

The firmware has at least 17 independent UI setup paths using:

access_level >= 3
 -> add child at parent +0x23C

Common editor path:
FUN_0802FB04

- +0x23C = increment
- +0x284 = decrement
- value = +0x60
- upper bound = +0x64

This proves that 6154 changes actual widget construction/availability in at least these paths.

It is not just a hidden menu password.

---

# PASS 15 — official manual and firmware agree on configuration persistence

Manual says after configuration changes, especially module/source changes:

- power cycle,
- wait at least 10 seconds so changes are stored.

This matters for reverse engineering because configuration values are expected to be persistent model state, not transient screen-only flags.

That is consistent with the firmware architecture where configuration is read through the generic parameter/model accessor.

---

# PASS 16 — firmware update mechanism is separate from 47290

Official manual says firmware update is:

- FAT32 microSD
- file starts with FW
- extension .bin
- root directory
- automatic update on boot
- red LED at start, green at completion
- remove card after main screen appears

This does NOT identify FUN_08047290.

The six-slot vertical geometry:

(100,50), (100,84), (100,118), (100,152), (100,186), (100,220)

therefore remains an unidentified component/screen until its factory/event path is recovered.

The "six slots = language/update" hypothesis remains OPEN, not CLOSED.

---

# PASS 17 — current web implementation is evidence of our reconstruction, not firmware proof

Current card layer explicitly uses:

- 051/052/053 for hopper
- 77 MENU
- 115 quick/power
- 144 CO1
- 174 CWU

This is useful as an implementation record, but it must never be fed backwards as proof of firmware call-sites.

The source-of-truth direction remains:

BIN -> analysis -> reconstruction

not:

web reconstruction -> supposed BIN behavior.

---

# PASS 18 — hopper trace demonstrates why indirect resource searches matter

The hopper is now a complete example:

CAN 0x3601 remaining kg
+
CAN 0x3600 capacity
-> percentage
+
CAN 0x3602 reserve flag
-> FUN_0802DA54

Then:

reserve=0 -> resource 051 on +0x5A8
reserve!=0 -> resource 053 on +0x5A8
fixed resource 052 on +0x5D4

This proves that a semantic Home tile can be a composition of multiple Bitmap children and runtime state.

That is precisely the model we should now apply to CWU/174.

---

# PASS 19 — Home seven-zone model now has three hard visual anchors

1. slot 4 = CO1 = 144
2. slot 6 = CWU = 174
3. slot 7 = lower-right = 115

This is user-verified UI evidence.

Current seven-zone model:

1 MENU candidate 77
2 fuel/hopper 051/052/053
3 burner unresolved
4 CO1 144
5 conditional/unresolved
6 CWU 174
7 lower-right 115

Slot 5 should NOT be forced to CO2 until the configuration gate and Home constructor converge.

---

# PASS 20 — CO2 has independent firmware support

Asset atlas:

144/145 = CO1 family
146/147 = CO2 family

Firmware configuration resolver independently exposes selectors 1..4 under 0x2105.

Official profiles independently show CO1 + CO2.

Therefore three independent evidence classes converge:

USER/UI:
CO1 visibly occupies slot 4.

FIRMWARE:
selectors 1..4 are capability-gated by 0x2105.

MANUFACTURER:
profiles explicitly contain CO1/CO2.

This makes CO2 in the conditional fifth Home zone a strong hypothesis, but the exact Home constructor still remains OPEN.

---

# PASS 21 — CO3/CO4 are not merely theoretical labels

The firmware has:

- TypedText 119..122 = CO1..CO4
- four selector gates
- family-of-4 parameter resolution
- +0x12C instance numbering 1..4
- resource families for CO1/CO2 already visible in the asset atlas.

Thus the four-circuit architecture is present in the software model even where the physical Home screen may only expose the currently configured subset.

---

# PASS 22 — official hardware architecture explains why 4 software instances can exist

The manufacturer documentation describes CAN I/O expansion and installation profiles, while the firmware supports up to four CO instances.

The exact hardware-to-instance allocation is still variant/profile dependent and must not be reduced to one profile.

The correct model is:

hardware/profile capability
 -> configuration state
 -> firmware capability gates
 -> instance-specific UI/model objects.

---

# PASS 23 — resource 174 likely participates in both generic and screen-specific composition

Because 174 is user-observed in Home and inside a CWU/tank composition, the most economical architecture is:

shared Bitmap resource
+
different parent/container contexts.

This is a STRONG architectural inference.

It is NOT yet a literal firmware call-chain proof.

---

# PASS 24 — high-value next disassembly target

The most valuable next raw-BIN search is:

resource 0xAE / decimal 174
AND neighboring:
0xAF / 175
0xB0 / 176
AND:
0xB3 / 179

Then cluster every hit by:

- function address
- object base/parent offset
- call to FUN_080307BC
- vtable method
- X/Y setters
- attach-to-parent call
- state dispatcher
- parameter read
- screen/factory caller.

The winning cluster should expose whether Home and CWU detail screens share a Bitmap child class.

---

# PASS 25 — second high-value target: water parameter fan-out

Current mapping gives:

0x10F -> 0x2106 = Hot water configuration.

This should now be traced in parallel with 174.

Target:

0x2106
 -> all callers
 -> visibility/configuration gates
 -> CWU selector/object
 -> parent/container
 -> resource selection
 -> 174/175/176
 -> tank composite / Home.

This is likely a much stronger bridge than searching for bitmap 174 in isolation.

---

# PASS 26 — third high-value target: 179 parent/child relationship

Search all references to 179 and inspect whether the same constructor family also creates a child whose resource is 174/175/176.

If yes:

179 + 174/175/176

becomes a firmware-proven water-screen composition.

If no:

the user-observed composite must be reconstructed from a different parent path.

Either outcome is valuable because it removes a major ambiguity.

---

# PASS 27 — fourth target: Home factory convergence

Do not derive Home from the web card.

Instead:

Find the root constructor candidate FUN_0803E5AC
 -> identify children/resources
 -> map children to 115/144/174
 -> recover parent geometry
 -> identify click callbacks
 -> compare configuration-dependent child insertion.

The three user anchors are ideal search constraints.

---

# PASS 28 — fifth target: slot-5 state machine

Once Home root is found, test:

Heating configuration = 1:
slot 4 CO1
slot 5 absent/empty

Heating configuration = 2:
slot 4 CO1
slot 5 CO2

Heating configuration = 3/4:
slot 5 may no longer simply mean CO2 if the UI reflows.

This must be determined from the actual constructor, not assumed.

---

# PASS 29 — manufacturer cross-check changes the probability landscape

Before this pass, "2105 controls CO count" was only a firmware/UI inference.

After cross-checking the official manual:

- manufacturer explicitly models number of heating circuits,
- profiles explicitly enumerate CO1/CO2,
- firmware explicitly gates selectors 1..4 from 2105,
- asset families explicitly include CO1/CO2,
- TypedText contains CO1..CO4.

Therefore the combined hypothesis:

2105 = capability count/configuration for heating circuits

is now STRONG, bordering on CLOSED semantically.

What remains OPEN is only the exact object-construction bridge.

---

# PASS 30 — contradiction audit

Rejected/stale:

- 0x10E -> 0x3505 as current mapping
- 0x10F -> 0x2105 as current mapping
- 47290 = Home bottom bar
- 056/057 = 151/152
- bitmap number == widget ID
- 174 is Home-only
- percentage chooses hopper 051 vs 052
- 6154 is merely a password/menu flag
- 370A numeric coincidence -> bitmap 011/012/013
- old generated boiler image as original firmware asset

Preserved as OPEN:

- exact 174 writer call-sites
- 174/175/176 state selection
- 179 relation to water screen
- exact Home factory
- slot-5 reflow
- 2105 -> C064/+0x12C bridge
- exact semantics of 47290
- exact 115 writer
- exact 144/145 state selection.

---

# FINAL STATE AFTER THIS PASS

## CLOSED / HARD
- 188 bitmap resources
- RGB565 + A8 renderer model
- generic Bitmap resource setter
- resource ID is runtime data
- 174/175/176 dimensions
- 179 dimensions
- Home 144=CO1 visual anchor
- Home 174=CWU visual anchor
- Home 115=lower-right visual anchor
- 0x10E -> 0x2105
- 0x2105 -> selector gates 1..4 with >=1..4
- CO1..CO4 instance architecture
- official access-level architecture
- official multi-profile CO/CWU/Buffer architecture.

## STRONG
- 2105 is the heating-circuit capability/configuration axis
- 174 is a reusable CWU semantic resource
- slot 5 is likely conditional CO2 in the one/two-circuit Home layout
- water screen likely reuses the same resource family.

## OPEN
- direct 174/175/176 consumer graph
- 179 -> 174 relationship
- exact Home factory
- Home child geometry
- touch/callback mapping for 144/174/115
- 2105 -> concrete C064/+0x12C object bridge
- exact per-state roles 174/175/176.

## NEXT ATTACK ORDER

1. 0x2106/CWU configuration fan-out.
2. 174/175/176/179 raw resource consumer graph.
3. Home root/factory and children.
4. CO1/CO2/CO3/CO4 construction bridge.
5. 115 direct writer.
6. 144/145 state selector.
7. 47290 factory/event path.

This ordering is now better than repeatedly searching the same bitmap IDs in isolation.
