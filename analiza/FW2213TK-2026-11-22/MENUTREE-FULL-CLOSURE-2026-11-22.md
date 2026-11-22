# MENU TREE — FULL STATIC/CONTROL-FLOW CLOSURE — 2026-11-22

## Scope

This document closes the MenuTree mechanism from raw table -> row construction -> eligibility/access -> row selection callback -> row-index resolver -> screen-family dispatch.

Source of truth: RAW `FW2213TK_kopia.bin`.

## 1. Root MenuTree table

RAW: `0x42348`  
PROJECT: `0x08042348`

21 records × 6 bytes:

| row | selector | TypedText ID | Bitmap ID | text |
|---:|---:|---:|---:|---|
| 0 | 0 | 60 | 83 | Kocioł |
| 1 | 10 | 61 | 85 | Palnik |
| 2 | 1 | 62 | 86 | Palnik/CO1 family |
| 3 | 2 | 63 | 86 | CO2 |
| 4 | 3 | 64 | 86 | CO3 |
| 5 | 4 | 65 | 86 | CO4 |
| 6 | 5 | 66 | 88 | Ciepła woda użytkowa |
| 7 | 6 | 71 | 87 | Solary |
| 8 | 7 | 67 | 84 | Bufor |
| 9 | 8 | 70 | 82 | Kaskada |
| 10 | 9 | 69 | 99 | Dodatkowy magazyn paliwa |
| 11 | 11 | 72 | 78 | Historia alarmów |
| 12 | 13 | 74 | 89 | Informacje o programie |
| 13 | 17 | 77 | 159 | Konfiguracja |
| 14 | 15 | 76 | 96 | Poziom menu (PIN) |
| 15 | 0 | 12 | 73 | Modulacja |
| 16 | 90 | 14 | 75 | Podtrzymanie |
| 17 | 97 | 18 | 78 | Praca |
| 18 | 100 | 16 | 79 | Alarm |
| 19 | 98 | 19 | 80 | Przepłukiwanie |
| 20 | 95 | 20 | 81 | Zamarzanie |

The first byte is the menu selector. Bytes 1 is padding. Bytes 2..3 are the TypedText/resource ID. Bytes 4..5 are the bitmap/resource ID.

## 2. Construction

The 21 row objects are not individually allocated by the MenuTree method.

A generic constructor at `0x0803BF80` creates the row array:

- base = object + `0x42C`
- element size = `0x274`
- count = `0x15` (21)
- constructor pointer = runtime `0x0805BB43` -> Thumb entry `0x0804BB42`.

This is direct RAW evidence that the 21-element array uses the recovered MenuRow class constructor.

## 3. Row setup

MenuTree builder `FUN_08042160`:

- first pass: rows 0..14 are always configured;
- at `0x42204` access state is tested;
- second block extends construction to 21 rows when access != 0;
- row pointer advances by `0x274`;
- table pointer advances by 6 bytes.

For each row the table values are passed to `FUN_0804BC6C`.

`FUN_0804BC6C`:
- table field +2 -> text/resource child at row +`0x8C`;
- table field +4 -> bitmap/resource child at row +`0x60`;
- performs the normal child attachment/update path.

Special row construction logic also uses selector byte for rows corresponding to special selectors 12/14; this is not the general navigation mechanism.

## 4. Capability / visibility

The capability layer is separate from navigation.

Formal function boundary:

`FUN_0803C064` is the actual Ghidra function. Historical labels `0x0803C178` and `0x0803C270` are internal entries/tails inside it, not independent functions.

The eligibility logic reads:

`DAT_0803C218 -> 0x20005EF0`

and evaluates the class/selector byte for the requested row.

Closed gating:

- class 1 -> internal parameter `0x10E`, minimum value >= 1
- class 2 -> `0x10E`, >= 2
- class 3 -> `0x10E`, >= 3
- class 4 -> `0x10E`, >= 4
- class 5 -> `0x10F`
- class 6 -> `0x110`
- class 7 -> `0x111`
- class 8 -> `0x11C`
- class 9 -> `0x122`
- other classes -> default eligible path.

For the first four heating rows the corresponding CAN capability is `0x2105`.

Access/PIN is a separate layer:
- level 0: PIN 0
- level 1: PIN 0900
- level 2: PIN 0999
- level 3: PIN 6154.

The last six root records are only constructed under non-zero access in the MenuTree builder.

## 5. Row selection -> index

The actual row-selection resolver is:

`0x0807EB00` (Thumb runtime pointer `0x0808EB01`).

It receives:
- r0 = parent/menu object
- r1 = selected row object.

It:
1. obtains the row-array base from parent + `0x3B4`;
2. iterates row indices from 0;
3. computes row address = array element + index × `0x274`;
4. compares the selected row pointer with that address;
5. on match calls `FUN_0803C064(parent->field+0x3C, index)`.

This closes the important edge:

`selected MenuRow -> row index -> C064 dispatcher`.

There is also a sibling callback at `0x0807EB36` (runtime `0x0808EB37`) which resolves the same row pointer but dispatches through `FUN_0803EC18`; this is the separate graph/state family and is not the main MenuTree page dispatcher.

## 6. Menu page-family dispatcher

`FUN_0803C064` reads:

`class = ((uint8_t*)0x20005EF0)[row_index]`

and dispatches class values 0..20 through a Thumb jump table.

Closed destination family:

| class | destination/action |
|---:|---|
| 0 | `0x08038008` |
| 1 | `0x08038130` with argument 1 |
| 2 | `0x08038130` with argument 2 |
| 3 | `0x08038130` with argument 3 |
| 4 | `0x08038130` with argument 4 |
| 5 | `0x080381E4` |
| 6 | `0x0803809C` |
| 7 | `0x080383B0` |
| 8 | `0x08038278` |
| 9 | `0x080382CA` |
| 10 | `0x080382A6` |
| 11 | `0x080384B0` |
| 12 | `0x08038638` |
| 13 | `0x080382EE` |
| 14 | return/no-op path |
| 15 | `0x08042318` using parent field +0x0C |
| 16 | `0x08038568` |
| 17 | `0x08038568` |
| 18 | `0x08038574` |
| 19 | `0x08038638` |
| 20 | `0x080382EE` |

Out-of-range class values (>20) go to the default handler at `0x0803850C`.

## 7. Important distinction

The six large selector values in root-table rows 16..20 (90, 97, 100, 98, 95) are **not** the values used directly by `FUN_0803C064`. The dispatcher consumes the runtime class byte from `0x20005EF0`.

Therefore the correct universal model is:

`MenuTable.selector` != necessarily `runtime class byte`.

The runtime class table is an independent dispatch layer.

This resolves the previous incorrect assumption that the first-byte selector alone was the complete navigation ID.

## 8. Row runtime object

Recovered MenuRow layout relevant to MenuTree:

- +`0x60`: resource/image child
- +`0x8C`: text child
- +`0xC4`: second text/resource child
- +`0xF8`: state child created by `FUN_08032D7C`
- +`0x26C`: generic callback/action slot
- +`0x270`: second generic callback/action slot.

The state child at +`0xF8` owns state at child+`0x2C`. Its callback machinery is separate from the root navigation resolver.

## 9. Complete logical graph

The closed control-flow model is:

```
Menu object
  |
  +-- row table @ 0x08042348, 21 × 6 B
  |
  +-- row objects @ object+0x42C, stride 0x274
  |      |
  |      +-- text/resource
  |      +-- bitmap/resource
  |      +-- state child
  |
  +-- access gate
  |
  +-- capability resolver / 0x20005EF0 class byte
  |
  +-- selected MenuRow
          |
          v
      0x0807EB00
          |
          v
      row pointer -> row index
          |
          v
      0x0803C064
          |
          v
      class byte = [0x20005EF0 + row_index]
          |
          +-- class 0..20
          |
          v
      page-family destination
```

## 10. Status

The **MenuTree mechanism is closed**: raw table, 21 row objects, construction, access gating, capability filtering, row selection/index resolution, and page-family dispatch are all connected by direct RAW evidence.

The runtime byte contents of `0x20005EF0` are intentionally represented as a runtime table rather than guessed from the visual selector values. This is required for a universal 1:1 implementation because the firmware itself separates menu-table selectors from runtime class dispatch.

No semantic mapping of `+0x12A/+0x12B/+0x12C` is inferred here.

## Evidence anchors

- Menu table: RAW `0x42348`
- Menu builder: `0x08042160`
- Row constructor: `0x0804BB42`
- Array construction: `0x0803BF80` -> `0x0805BB43`
- Capability/class dispatcher: `0x0803C064`
- Runtime class table: `0x20005EF0`
- Row selection resolver: `0x0807EB00`
- Second sibling resolver: `0x0807EB36`
- Second MenuTree context: `0x20005F08`
