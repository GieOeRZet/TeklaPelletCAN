# NewEstyma — INSTANCE/CAPABILITY GRAPH ATTACK 01 — 2026-11-22

## 1. Capability resolver — HARD

FUN_0803C178 is a row eligibility/visibility resolver.

Direct caller:
0x0804227A, iterating 21 row slots.

For selector families:
- selectors 1..4 use internal index 0x10E / CAN 0x2105;
- selector 1 visible iff value >=1;
- selector 2 visible iff value >=2;
- selector 3 visible iff value >=3;
- selector 4 visible iff value >=4.

Other proven configuration gates:
- selector 5 -> 0x10F / CWU configuration;
- selector 6 -> 0x110 / solar;
- selector 7 -> 0x111 / buffer;
- selector 8 -> 0x11C;
- selector 9 -> 0x122.

Therefore capability is computed dynamically from configuration state, not hard-coded only in screen layout.

## 2. 21-slot MenuTree relation — HARD/STRONG

Menu constructor creates:
- rows 0..14 always;
- rows 15..20 only when access != 0.

After construction:
21 row slots are passed through capability processing.

This establishes:
MenuRow[21]
 -> capability resolver
 -> visible/eligible state

It does NOT yet establish touch/navigation.

## 3. Instance-aware parameter path — HARD/STRONG

The common page/widget machinery uses an instance-aware parameter lookup:

FUN_08036FF2(context, parameter_id)
 -> instance-aware base / record selection
 -> FUN_0804842C
 -> widget record +0x42C + index*0x338
 -> value update + refresh.

For CO1..CO4, the firmware uses common machinery rather than four independent screen implementations.

## 4. +0x12A/+0x12B/+0x12C — boundary

Confirmed:
- these fields are page/context-related;
- traced constructors read/write them;
- +0x12C participates in active-instance selection in the instance-aware paths;
- +0x12B participates in variant/context/resource-family selection in traced paths.

However, the exact universal semantic labels for all three fields are NOT CLOSED.

Do not encode:
"+0x12A = parent"
"+0x12B = CO number"
"+0x12C = generic menu index"

as universal facts.

## 5. 2105 -> capability graph

CAN 0x2105
 -> internal parameter 0x10E
 -> FUN_0803C178
 -> selector 1..4 thresholds
 -> CO1..CO4 row eligibility.

This is capability/visibility evidence, not proof of object creation count.

## 6. Access/PIN layer

Access:
PIN 0 -> level 0
0900 -> level 1
0999 -> level 2
6154 -> level 3

Level stored at context/model +0x158.

Level >=3 adds UI children in multiple constructors.

This is a second gate, separate from installation/configuration capability.

## 7. Graph model

Configuration state
   |
   +--> capability resolver
   |       |
   |       +--> row eligibility
   |
Access level
   |
   +--> access-gated construction
   |
Page/context
   |
   +--> instance/variant fields
   |
   +--> common parameter lookup
           |
           +--> widget record
           +--> value/refresh

## 8. CLOSED

- configuration -> capability resolver;
- 2105/0x10E -> CO1..CO4 thresholds;
- 21-slot post-construction capability pass;
- access-level gating;
- common instance-aware widget factory.

## 9. OPEN

- exact source/producer of +0x12A/+0x12B/+0x12C for every page family;
- exact instance object creation bridge;
- touch/navigation callback;
- full 0x20005F08 runtime contents/producer;
- complete capability matrix for all 21 selectors and all configuration combinations;
- exact relationship between capability result and row state child/visibility method.
