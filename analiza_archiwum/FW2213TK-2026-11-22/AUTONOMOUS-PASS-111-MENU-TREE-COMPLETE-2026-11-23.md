# AUTONOMOUS PASS 111 — MENU_TREE_COMPLETE — 2026-11-23

## 1. Cel

Domknięcie source-grounded szkieletu pełnego MenuTree dla 21 rekordów, ponad granicą wcześniejszego PASS 96.

PASS 96 zamykał tylko:
`row -> runtime class -> first-level handler`.

Ten pass łączy:
- root MenuTree record,
- budowę MenuRow,
- dostęp/capability,
- row-selection callback,
- runtime class,
- first-level dispatch,
- znane efekty click,
- znane semantyki stron,
- dostępne powiązania PID/CAN,
- status dowodu HARD / STRONG / INFERRED / OPEN.

Nie uzupełniano brakujących destination/resource/widgetów przez zgadywanie.

## 2. Źródła

Primary:
- `analiza_archiwum/FW2213TK-2026-11-22/data/menu_rows_21.csv`
- `analiza_archiwum/FW2213TK-2026-11-22/data/menu_click_effects_21.csv`
- `analiza_archiwum/FW2213TK-2026-11-22/data/cg_menu_dispatch_closure.csv`
- `analiza_archiwum/FW2213TK-2026-11-22/data/cg_ui_key_pid_t1_full.csv`
- `analiza_archiwum/FW2213TK-2026-11-22/data/cg_ui_key_pid_t2_full.csv`
- `analiza_archiwum/FW2213TK-2026-11-22/data/cg_view_callback_dual_closure.csv`
- `analiza_archiwum/FW2213TK-2026-11-22/MENUTREE-FULL-CLOSURE-2026-11-22.md`
- `analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-28-RUNTIME-CLASS-FIRST-LEVEL-UI-DISPATCH-2026-11-22.md`
- `analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-29-RUNTIME-CLASS-CALLBACK-DESCRIPTOR-LAYER-2026-11-22.md`
- `analiza_archiwum/FW2213TK-2026-11-20/BATCH-6154-CONTEXT-INSTANCE-AND-PAGE-FAMILY-MULTIPASS-2026-11-20.md`
- `NewEstyma/01_PROJECT_STATE.md`
- `NewEstyma/COORDINATION.md`

## 3. HARD — wspólny mechanizm MenuTree

Root table:
- PROJECT `0x08042348`
- RAW `0x42348`
- 21 rekordów × 6 B
- fields: selector, TypedText/resource ID, bitmap/resource ID.

Row construction:
- array base = object + `0x42C`
- stride = `0x274`
- count = 21
- row constructor = PROJECT `0x0804BB42` (Thumb entry from `0x0805BB43`).

Row resource attachment:
- field +2 -> row +`0x8C`
- field +4 -> row +`0x60`
- state child at +`0xF8`
- generic callbacks at +`0x26C` / +`0x270`.

Selection:
`0x0807EB00` resolves selected row pointer to index using parent+`0x3B4`, stride `0x274`, then calls `0x0803C064`.

Sibling:
`0x0807EB36` uses the same row registry and dispatches `0x0803EC18`; it is a separate graph/state path, not the main MenuTree page dispatcher.

Runtime class:
`0x0803C064` reads `0x20005EF0[index]` and TBB-dispatches values 0..20.

Important: root-table selector != runtime class in the universal model. The runtime table is a separate state layer.

## 4. HARD — 21 root records

| row | selector | text/resource | bitmap | initial/root role |
|---:|---:|---|---:|---|
| 0 | 0 | Kocioł | 83 | top-level boiler |
| 1 | 10 | Palnik | 85 | top-level burner |
| 2 | 1 | Palnik/CO1 family | 86 | CH family instance 1 |
| 3 | 2 | CO2 | 86 | CH family instance 2 |
| 4 | 3 | CO3 | 86 | CH family instance 3 |
| 5 | 4 | CO4 | 86 | CH family instance 4 |
| 6 | 5 | Ciepła woda użytkowa | 88 | CWU |
| 7 | 6 | Solary | 87 | Solar |
| 8 | 7 | Bufor | 84 | Buffer |
| 9 | 8 | Kaskada | 82 | Cascade |
| 10 | 9 | Dodatkowy magazyn paliwa | 99 | Additional fuel storage |
| 11 | 11 | Historia alarmów | 78 | Alarm history |
| 12 | 13 | Informacje o programie | 89 | Program information |
| 13 | 17 | Konfiguracja | 159 | Configuration |
| 14 | 15 | Poziom menu (PIN) | 96 | Access/PIN |
| 15 | 0 | Modulacja | 73 | internal/secondary family record; not proven top-level list item |
| 16 | 90 | Podtrzymanie | 75 | internal/secondary family record; not proven top-level list item |
| 17 | 97 | Praca | 78 | internal/secondary family record; not proven top-level list item |
| 18 | 100 | Alarm | 79 | internal/secondary family record; not proven top-level list item |
| 19 | 98 | Przepłukiwanie | 80 | internal/secondary family record; not proven top-level list item |
| 20 | 95 | Zamarzanie | 81 | internal/secondary family record; not proven top-level list item |

The last six are not to be interpreted as ordinary top-level navigation entries. Existing dynamic/static evidence shows they belong to a secondary/conditional construction layer.

## 5. Access / capability

HARD:
- rows 0..14 are built unconditionally by the MenuTree builder;
- rows 15..20 are added only when access != 0;
- access/PIN levels are separate from capability selection.

Capability resolver uses the runtime class table and configuration parameters:
- class 1..4 -> internal `0x10E`, threshold by class; corresponding CAN capability is `0x2105`;
- class 5 -> `0x10F` / Hot water configuration;
- class 6 -> `0x110` / Solar configuration;
- class 7 -> `0x111` / Buffer configuration;
- class 8 -> `0x11C`;
- class 9 -> `0x122`;
- other classes use default path.

Access/PIN:
- level 0 -> PIN 0
- level 1 -> 0900
- level 2 -> 0999
- level 3 -> 6154

The firmware has cumulative access gates; level >=3 wrappers add real widget-tree membership, not merely cosmetic visibility.

## 6. Runtime class -> first-level destination

| class | first-level destination | status |
|---:|---|---|
| 0 | `0x08038008` | HARD |
| 1 | `0x08038130(r1=1)` | HARD |
| 2 | `0x08038130(r1=2)` | HARD |
| 3 | `0x08038130(r1=3)` | HARD |
| 4 | `0x08038130(r1=4)` | HARD |
| 5 | `0x080381E4` | HARD |
| 6 | `0x0803809C` | HARD |
| 7 | `0x080383B0` | HARD |
| 8 | `0x08038278` | HARD |
| 9 | `0x080382CA` | HARD |
| 10 | `0x080382A6` | HARD |
| 11 | `0x080384B0` | HARD |
| 12 | special `0x080373BA/0x080373E6` | HARD |
| 13 | `0x0803850C` | HARD |
| 14 | return/no-op | HARD |
| 15 | `0x08042318` via object+`0x0C` | HARD |
| 16 | `0x0803856C` | HARD |
| 17 | `0x08038568` | HARD |
| 18 | `0x08038574` | HARD |
| 19 | `0x08038638` | HARD |
| 20 | `0x080382EE` | HARD |

Classes 1..4 write +`0x12B` and +`0x12C` and enter the common construction tail. Classes 16/17 write +`0x12B` = `0x10/0x11`. Class 14 is an actual empty branch. Classes 12/15/19/20 are structurally special.

## 7. Row-by-row closure matrix

The machine-level fields below are separated from semantic interpretation.

- rows 0..14 have HARD root text/bitmap records;
- row -> runtime class is NOT frozen to root selector because `0x20005EF0` is mutable runtime state;
- click effects are included only where already observed;
- PID/CAN is listed only where a direct existing binding is available.

| row | root selector | root text | click/runtime observation | known destination/family | PID/CAN | status |
|---:|---:|---|---|---|---|---|
| 0 | 0 | Kocioł | class 0 in observed click matrix | `0x08038008` | Kocioł PID matrix available; see PASS 98/103 | HARD |
| 1 | 10 | Palnik | class 10; +12B changes 0->10 | `0x080382A6` | burner PID family available in T2 resolver | HARD/STRONG |
| 2 | 1 | Palnik/CO1 | class 1; +12B=1, +12C=1 | `0x08038130`, variant 1 | T1 CH family, e.g. `0x22FD`, `0x2032`, `0x2064` etc. | HARD |
| 3 | 2 | CO2 | class 2; +12B=2, +12C=2 | `0x08038130`, variant 2 | T1 CH instance rule `PID=value+inst-1` | HARD |
| 4 | 3 | CO3 | class 3; +12B=3, +12C=3 | `0x08038130`, variant 3 | T1 CH instance rule | HARD |
| 5 | 4 | CO4 | class 4; +12B=4, +12C=4 | `0x08038130`, variant 4 | T1 CH instance rule | HARD |
| 6 | 5 | CWU | class 5 | `0x080381E4` | CWU family; e.g. `0x201A` result temp, `0x2110` measured | HARD |
| 7 | 6 | Solary | class 6 | `0x0803809C` | Solar family, e.g. `0x3120`, `0x2109`.. | HARD |
| 8 | 7 | Bufor | class 7 | `0x080383B0` | `0x2112..`, `0x2280`, `0x3171..` etc. | HARD |
| 9 | 8 | Kaskada | class 8 | `0x08038278` | Cascade family `0x3511..` etc. | HARD/STRONG |
| 10 | 9 | Dodatkowy magazyn paliwa | class 9 | `0x080382CA` | external fuel storage family `0x3520..` etc. | HARD/STRONG |
| 11 | 11 | Historia alarmów | class 11 | `0x080384B0` | alarm manager; reset memory `0x404E` | HARD |
| 12 | 13 | Informacje o programie | class 13 | `0x0803850C` | no direct PID binding established | HARD |
| 13 | 17 | Konfiguracja | class 17 in observed click path; +12B=0x11 | `0x08038568` first-level; context-dependent page construction | known configuration PIDs incl. `0x2105..0x2108`, `0x372F`, `0x3747`, `0x3603` | HARD |
| 14 | 15 | Poziom menu (PIN) | class 15 -> `0x08042318`; observed ERR at terminal emulation | `0x08042318 -> 0x0802EADE` special path | PIN mechanism closed; no direct CAN required | HARD |
| 15 | 0 | Modulacja | observed click class 12 -> language operation in row 15 context; not a normal root-list item | class 12 special `0x080373BA/0x080373E6` | PID `0x0003` Language | HARD for observed state |
| 16 | 90 | Podtrzymanie | observed class 14; no-op | return/no-op | none proven | HARD |
| 17 | 97 | Praca | observed class 18 | `0x08038574`; secondary descriptor builder | no direct PID binding | HARD |
| 18 | 100 | Alarm | observed class 16 -> +12B=0x11 | `0x0803856C` | no direct PID binding | HARD |
| 19 | 98 | Przepłukiwanie | observed class 19 | `0x08038638` | no direct PID binding | HARD |
| 20 | 95 | Zamarzanie | observed class 20 | `0x080382EE` | no direct PID binding | HARD |

### Important row 15 clarification

The root record's text/bitmap are hard evidence, but the observed click matrix shows row 15 dispatching as runtime class 12 and changing Language PID 0x0003. This demonstrates why root-table selector, runtime class and semantic destination must remain separate dimensions. The record should not be renamed to "Language" merely because the observed class-12 action is language switching.

## 8. Page family / context dimensions

From the independent 6154/context audit:

- +`0x12A` = page/context selector with at least values 0..5.
- +`0x12B` = separate page/variant selector; context 3 explicitly chooses resources for values `0x10/0x11/other`; context 2 uses a 0..10 resource family.
- +`0x12C` = active instance selector with direct values 1..4 in CH paths.

These are orthogonal dimensions. They must not be collapsed into a single menu index.

## 9. PID/CAN coverage boundaries

Directly established examples relevant to MenuTree pages:

- Kocioł:
  - `0x370A -> 0x20016894 -> bitmap 11/12/13`
  - `0x350D -> 0x20016A94 -> pressure visibility`
  - `0x350A -> 0x20016A24 -> return temperature visibility`
  - `0x2005 -> 0x20016918 -> boiler on/off`
  - `0x216F -> 0x20016ACC/0x20016B24`
  - `0x22A1` has multiple visual/visibility effects.
- Burner:
  - T2 resolver contains the complete burner-related PID family; no claim is made that every PID is visible on every burner screen.
- CH1..CH4:
  - T1 resolver has 49 UI keys and rule `PID=value+inst-1`.
- CWU:
  - `0x201A` result temperature and related CWU PIDs are directly in T2.
- Buffer:
  - `0x2112`, `0x2113`, `0x2114`, `0x2115`, `0x2280`, `0x3171..` etc.
- Solar:
  - T2 includes `0x3120`, `0x2109`.. etc.
- Configuration:
  - `0x2105..0x2108), `0x372F`, `0x3747`, `0x3603` are directly established.
- Alarm:
  - generic manager is closed; individual alarm predicates remain separate.

No global claim is made that a page consumes every PID in its family.

## 10. OPEN — intentionally not guessed

Still OPEN after this pass:

1. Exact final page constructor/resource/widget chain for most classes.
2. Complete runtime `0x20005EF0` writer/initializer history and final class value for every row across all configurations.
3. Exact destination semantics for classes 0,5..11,13,16..20 beyond their first-level handlers.
4. Exact screen family / widget tree for rows 15..20.
5. Complete callback graph from each row to widgets.
6. Full per-page PID/CAN binding.
7. Complete configuration × access × instance matrix.
8. Exact children relation between page families.
9. Exact TypedText-to-widget binding for most page families.
10. Exact CAN producer/channel/PDO for live sources where only static PID mapping exists.
11. Exact final constructors for PROGRAM / TIME_DIALOG / STATISTICS remain separate tasks.

## 11. Evidence discipline

HARD = direct source/dataflow or exact repository CSV/raw evidence.

STRONG = multiple independent traces but not complete semantic closure.

INFERRED = logical model not directly proven.

OPEN = insufficient source evidence.

No OPEN semantic field was promoted to HARD merely because the label looked plausible.

## 12. Result

MENU_TREE_COMPLETE now closes the **21-node machine-level skeleton** and reconciles it with the previously independent runtime-class, access, callback and PID evidence.

It does NOT claim that all 21 nodes have complete screen/widget/PID/CAN semantic closure. Those remain explicit OPEN fields for S3/S4/S5/S6/S7/S8.

## 13. Next static target

Proceed immediately to S1: full CFG-aware presenter setter offset closure, while preserving this MenuTree matrix as the canonical machine-level tree skeleton.
