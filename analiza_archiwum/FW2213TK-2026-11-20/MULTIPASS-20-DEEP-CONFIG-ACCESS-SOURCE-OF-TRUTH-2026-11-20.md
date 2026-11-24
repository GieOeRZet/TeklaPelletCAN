# MULTIPASS-20 — DEEP CONFIGURATION / ACCESS / MENU / SOURCE-OF-TRUTH CORRECTION
Data: 2026-11-20

## Cel
Wykonać wielowarstwowy cross-check całego obecnie dostępnego modelu konfiguracji panela:
- internal index -> CAN ID,
- konfiguracja 2105..2108,
- resolver FUN_0803C178,
- 21-slot row family,
- access levels 0..3,
- menu selectors,
- official Estyma documentation,
- instance engine +0x12B/+0x12C,
- 6154 numeric editor gates,
- stale hypotheses from 2026-11-19.

Źródło prawdy:
1. bezpośredni FW / raw-derived traces,
2. extracted DATA,
3. official Estyma/Tekla docs,
4. STRONG correlations,
5. OPEN hypotheses.

---

## PASS 01 — CURRENT INTERNAL -> CAN MAPPING

Aktualny, skorygowany mapping jest:

| internal | CAN/panel | znaczenie |
|---|---:|---|
| 0x10D | 0x3505 | Outside temperature sensor configuration |
| 0x10E | 0x2105 | Heating configuration |
| 0x10F | 0x2106 | Hot water configuration |
| 0x110 | 0x2108 | Solar configuration |
| 0x111 | 0x2107 | Buffer configuration |
| 0x112 | 0x3500 | Main module type |
| 0x113 | 0x3502 | CH expansion module type |
| 0x114 | 0x3501 | Autoconfig activation |

[FW/DATA][CLOSED]

This mapping is independently present in the 2026-11-20 architecture-reset/whole-software/config-resolver notes and in the consolidated 2026-11-19 master.

### STALE MATERIAL TO OVERRIDE

Several older 2026-11-19 batch notes still contain:
- 0x10E -> 0x3505
- 0x10F -> 0x2105

Those statements are superseded.

The correct owner of 0x3505 is internal 0x10D.
The correct owner of 0x2105 is internal 0x10E.

Do not use the old 0x10E/3505 chain as evidence.

---

## PASS 02 — 2105 PARAMETER IDENTITY

0x2105 is:

- name: Heating configuration
- type: u8
- range: 0..4
- default: 1
- local panel storage: 0x20021FAF
- parameter-map entry: 0x0801A5B0
- panel/internal index: 0x10E

[FW/DATA][CLOSED]

The snapshot representation is encoded with the panel flag/base; raw 257 corresponds to logical value 1 in the project register material.

---

## PASS 03 — DIRECT UI CAPABILITY FAN-OUT OF 2105

FUN_0803C178 is a UI eligibility/visibility resolver.

It maps selector values as follows:

- selector 1 -> internal 0x10E -> 0x2105 -> visible iff value >= 1
- selector 2 -> 0x2105 -> visible iff value >= 2
- selector 3 -> 0x2105 -> visible iff value >= 3
- selector 4 -> 0x2105 -> visible iff value >= 4
- selector 5 -> 0x10F -> 0x2106 -> visible iff value >= 1
- selector 6 -> 0x110 -> 0x2108 -> visible iff value >= 1
- selector 7 -> 0x111 -> 0x2107 -> visible iff value >= 1
- selector 8 -> 0x11C -> 0x350C -> visible iff nonzero
- selector 9 -> 0x122 -> 0x3525 -> visible iff nonzero
- other selectors at this resolver layer return visible=true.

[FW][CLOSED]

This is the first direct firmware-level bridge from 0x2105 to the four CO UI capability slots.

### IMPORTANT LIMIT

This proves:
0x2105 -> capability/visibility of CO1..CO4 row slots.

It does NOT yet prove:
0x2105 -> construction of C064 objects
or
0x2105 -> assignment of +0x12C instances.

Those remain separate OPEN questions.

---

## PASS 04 — MENU SEMANTICS CROSS-CHECK

The first 15 selectors of the constructor's proven menu group are:

0 Kocioł
10 Palnik
1 CO1
2 CO2
3 CO3
4 CO4
5 CWU
6 Solar
7 Buffer
8 Cascade
9 Additional fuel storage
11 Alarm history
13 Program information
17 Configuration
15 Menu level/PIN

[FW/DATA][CLOSED for this first group]

The semantic icon layer independently supports CO1..CO4 as selectors 1..4.

Therefore the resolver gates are not abstract placeholders:
they correspond to the actual CO1..CO4 menu entries.

---

## PASS 05 — 21-SLOT CONSTRUCTOR ARCHITECTURE

The raw table at 0x42348 contains 21 records.

The constructor performs:
- first stage: records 0..14,
- second stage: records 15..20 only when access level != 0,
- later 21-slot capability/update passes.

Each logical row object is separated by 0x274 bytes.

[FW][CLOSED]

Therefore:
- 21 logical row slots exist,
- construction is access-dependent,
- capability resolution is separate from initial row construction.

Do not collapse this into a simple static 15-row menu.

---

## PASS 06 — ACCESS LEVEL 0..3

FUN_08037E74 maps:
- 0 -> level 0
- 900 -> level 1
- 999 -> level 2
- 6154 (0x180A) -> level 3
- other nonzero -> preserve previous level

Level is stored at model/context +0x158.

[FW][CLOSED]

6154 is correct. 6164 is not the firmware code.

---

## PASS 07 — ACCESS LEVEL VS 21-SLOT SECOND STAGE

The 21-slot constructor's second stage checks only access != 0.

Therefore:
- level 1, 2, and 3 all qualify for the second-stage six rows.
- level 3 is NOT the unique condition for the six trailing records.

[FW][CLOSED]

This must not be confused with the separate >=3 numeric-editor gates.

---

## PASS 08 — LEVEL 3 / 6154 UNIQUE EFFECT

17 independent UI constructor/setup paths contain:

access_level >= 3
    -> add child parent+0x23C

Common handler FUN_0802FB04 establishes:
- parent+0x23C = increment/+
- parent+0x284 = decrement/-
- value lives at parent+0x60
- upper bound at parent+0x64.

[FW][CLOSED]

One branch is concretely anchored to:
TypedText 454 = "Próg zmniejszania stopnia mocy [%]".

Therefore 6154 changes the interactive widget tree, not merely a menu flag.

---

## PASS 09 — OFFICIAL DOCUMENTATION: HEATING COUNT

The official Tekla/Estyma installer manual explicitly lists:
"Ilość obwodów grzewczych" and states that it determines the number of CO circuits.

The 0x2105 firmware parameter:
- is named Heating configuration,
- has range 0..4,
- directly gates selectors 1..4.

[DOC + FW][STRONG/CLOSED at capability level]

This is now a much stronger chain than the earlier "semantic coincidence" argument.

---

## PASS 10 — OFFICIAL DOCUMENTATION: PROFILE IS ORTHOGONAL

Manufacturer documentation also defines distinct profiles:
- Profile 1: CO + CWU + Buffer
- Profile 2: CO1 + CO2 + CWU
- Profile 3: CO1 + CO2 + CWU + Buffer

The 2024 guide additionally states IgneoTouch can support up to 4 CO circuits and that CAN I/O STD can add up to 3 additional CO circuits.

[DOC][STRONG]

Therefore profile/module type and Heating configuration must remain separate axes.

---

## PASS 11 — ORTHOGONAL CONFIGURATION MATRIX

Current capability resolver axes are at least:

Heating 0..4
Hot water 0/1
Solar 0/1
Buffer 0/1
Cascade master 0/1
Additional fuel storage 0/1
Access level 0..3

This is not a single "CO count" variable.

At the resolver layer:
- Heating controls CO1..CO4,
- Hot water controls CWU,
- Solar controls Solar,
- Buffer controls Buffer,
- CascadeMaster controls Cascade,
- AdditionalStorage controls Additional fuel storage.

[FW][CLOSED]

---

## PASS 12 — 160 INSTALLATION CAPABILITY STATES

The five binary installation capabilities produce 2^5 = 32 combinations.
With Heating 0..4, there are 5*32 = 160 resolver-level installation states.

This is a synthetic state space for testing, not a claim that all 160 combinations are physically supported by every CAN I/O hardware profile.

[ANALYTIC][CLOSED]

---

## PASS 13 — 21-SLOT + CAPABILITY RESOLVER ARCHITECTURE

The strongest current menu/configuration pipeline is:

parameter/model state
  -> configuration resolver FUN_0803C178
  -> 21 logical row slots
  -> access-dependent construction
  -> capability visibility
  -> screen/menu dispatch
  -> widget tree

[FW][STRONG]

This is more precise than the previous model "main menu = 15 fixed rows".

---

## PASS 14 — 0x3505 RELOCATION / OUTSIDE SENSOR

0x3505 remains:
Outside temperature sensor configuration, range 0..2.

Its correct internal index is 0x10D, not 0x10E.

[FW/DATA][CLOSED]

The old 0x10E/3505 UI-threshold narrative is therefore stale.

A separate current consumer path for 0x10D should be traced if outside-sensor UI behavior is required, but it must not be merged with CO-count logic.

---

## PASS 15 — INSTANCE ENGINE REMAINS SEPARATE

Current hard invariant:

+0x12B = class/type
+0x12C = active instance

FUN_08036FF2 performs family-of-4 resolution using:
family base + (instance - 1)

[FW][CLOSED]

The existence of 0x2105 capability gating does not by itself prove how +0x12C gets populated.

---

## PASS 16 — C064 REMAINS THE OBJECT-CLASS BRIDGE

FUN_0803C064:
class = DAT_0803C218[param_2]

For classes 1..4 it writes class/type and instance fields into the module object.

[FW][CLOSED]

What remains open:
- exact param_2 values for CO1..CO4,
- exact indirect vtable/callback entry,
- exact relationship between configuration resolver and C064 invocation.

Do not manufacture this edge.

---

## PASS 17 — 6154 AND 2105 ARE ORTHOGONAL

2105 controls installation capability/visibility of CO rows.

6154 controls a separate access permission layer that inserts numeric + controls into specific editors.

Therefore the final implementation must have two independent dimensions:

configuration_capability
access_level

Neither should be encoded as the other.

---

## PASS 18 — 47290 / GRAPH / 151-152 SEPARATION

No new evidence merges:
- 47290 six-slot selector/list,
- graph resources 056/057,
- 151/152 selector state,
- Language selector 90.

The earlier rejection remains valid.

This area is not a blocker for the configuration correction above.

---

## PASS 19 — SOURCE-OF-TRUTH / STALE-DOC AUDIT

The following old statements must be treated as superseded:

1. 0x10E -> 0x3505
2. 0x10F -> 0x2105
3. 0x10E = outside-temperature configuration
4. 0x2105 has only UI-graphic significance

Current replacement:
1. 0x10D -> 0x3505
2. 0x10E -> 0x2105
3. 0x10D = outside-temperature configuration
4. 0x2105 directly gates CO1..CO4 capability rows.

The old notes are retained as history; they are not current source-of-truth.

---

## PASS 20 — FINAL ARCHITECTURE RESULT

Current strongest model:

hardware/module discovery
  |
  +--> profile / variant
  |
  +--> functional configuration
  |      0x2105 Heating
  |      0x2106 Hot water
  |      0x2107 Buffer
  |      0x2108 Solar
  |
  +--> access level 0..3
  |
  v
configuration/capability resolver
  |
  v
21 logical row slots
  |
  +--> access-dependent second-stage construction
  |
  +--> configuration visibility
  |
  v
screen/menu dispatcher
  |
  v
class/type + instance (+0x12B/+0x12C)
  |
  v
instance-aware parameter engine
  |
  v
record/CAN/storage engine
  |
  v
widget/resource/touch/write side effects

The key new closure is:

0x2105 (Heating configuration)
    -> internal 0x10E
    -> FUN_0803C178
    -> selectors 1..4
    -> CO1..CO4 visibility thresholds 1..4

This is HARD firmware evidence plus official documentation correlation.

It still does not prove the object-instantiation bridge to C064/+0x12C.

---

## NEXT HIGH-VALUE ATTACKS

1. Trace every consumer of internal 0x10D (outside-temperature config) and separate it from CO capability.
2. Trace exact source of param_2 entering C064 for the four CO classes.
3. Trace whether FUN_0803C178 output affects row object state, screen navigation, or only visibility.
4. Trace selectors 1..4 from row object -> click callback -> target screen.
5. For CO1..CO4, trace screen factory -> +0x12B/+0x12C -> FUN_08036FF2 -> parameter family.
6. Build exact access(0/1/2/3) x configuration matrix with row construction/visibility.
7. Resolve all 17 level-3 numeric-editor bindings.
8. Resolve trailing six second-stage selectors 90/97/100/98/95/0 by consumer, not label guessing.
9. Continue 370A only after the above configuration spine is stable.
10. Keep 47290 separate until a direct navigation edge is found.

## IMPORTANT HONESTY NOTE

This report consolidates multiple independent passes over the repository's raw-derived analysis, extracted data and official documentation. It does not claim that every one of the 143 analysis files was simultaneously held in one model-visible buffer. Historical files were searched/fetched in batches and cross-checked.

