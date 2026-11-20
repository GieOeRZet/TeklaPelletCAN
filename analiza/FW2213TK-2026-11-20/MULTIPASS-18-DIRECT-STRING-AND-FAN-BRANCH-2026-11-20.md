# MULTIPASS-18 — Direct firmware string closure for second fan UI branch — 2026-11-20

## New hard finding

The Polish TypedText database was rechecked directly from FW2213TK_kopia.bin. TypedText ID 183 is exactly:

- PL: `Wentylator wspomagający [%]`
- EN: `Extra exhaust fan [%]`
- ES: `Función extra extractor humos [%]`
- EST: `Suitsugaasi ventilaator [%]`
- LT: `Ištraukimo ventiliatorius`
- RO: `Ventilator exhaustare extra [%]`
- SK: `ventilátor odťahový [%]`

TypedText ID 199 is:
- PL: `Moc dmuchawy modulacja [%]`
- EN: `Blower power modulation [%]`

This closes the terminology much more strongly than the previous generic wording. The firmware itself calls the second function an extra/exhaust fan family.

## Direct code path to TypedText 183

FUN_0803CF54 is a large UI/configuration builder. It calls FUN_08043A36 at raw offset 0x3D07C.

At 0x3D070..0x3D07C:
- `LDR r0,[r4,#0x08]`
- `MOVS r1,#0x68`
- `BL FUN_08036FF2`
- returned value is `UXTB` into r1
- `LDR r0,[r4,#0x0C]`
- `BL FUN_08043A36`

FUN_08043A36 then:
- creates/updates object at `r0 + 0xF74`
- if incoming r1 == 1 it selects TypedText 182
- otherwise it selects TypedText 183
- TypedText 182 = `Podajnik palnika`
- TypedText 183 = `Wentylator wspomagający [%]`
- also uses TypedText 168/169 for `Temperatura CO dla -20°C` and `Temperatura CO dla -10°C`.

Therefore TypedText 183 is not merely a dead language-table string. It is directly selected by executable UI-building code.

## Important interpretation

This path is stronger evidence for configuration-dependent UI than the earlier generic argument about missing menu items.

However, the exact meaning of panel/resolver index 0x68 is still OPEN. FUN_08036FF2 does not find literal index 0x68 in the two static parameter-index tables already mapped, so its return value may be zero/default or may belong to a different/special context. Do not invent a parameter ID for 0x68.

The immediate branch in FUN_08043A36 is nevertheless closed: r1=1 -> `Podajnik palnika`; r1!=1 -> `Wentylator wspomagający [%]`.

## Strategic consequence

The correct next attack is no longer simply 'find the Polish string'. It is:
1. identify what configuration/state produces resolver index 0x68 = 1;
2. identify which UI parent/host owns `parent+0xF74` in this builder;
3. identify the adjacent controls created by FUN_0803CF54;
4. determine whether this is the second fan selection/configuration branch;
5. connect this branch to the five `exh. fan char.` parameters 0x2268/0x226E/0x226F/0x2275/0x227A;
6. find the exact gate/variant relation;
7. then integrate it into the global whole-software configuration graph.

## Source-of-truth note

All semantic conclusions above are from firmware-extracted TypedText and direct Thumb-2 control flow. The manufacturer manual is only used as external terminology cross-check.

## Confidence

- ID 183 PL/EN semantics: HIGH / direct firmware string extraction.
- ID 183 direct executable selection: HIGH.
- FUN_0803CF54 is a configuration/UI builder: HIGH from its resolver-heavy UI construction pattern.
- 0x68 is the configuration gate for burner feeder vs extra exhaust fan: MEDIUM/HIGH for the branch relationship, exact underlying parameter OPEN.
- 0x68 maps to a specific static parameter ID: NOT PROVEN.
- 0x2268..0x227A are the same function selected by this branch: NOT YET PROVEN; must be connected explicitly.