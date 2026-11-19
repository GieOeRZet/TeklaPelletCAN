# BATCH — 051/052 PELLET HOPPER TRACE — 2026-11-19

## Cel przebiegu
051/052 → widget → ilość pelletu → próg/state.
Nie powtarzano ekstrakcji 188 bitmap. Nie użyto ponownie błędnych hipotez 47290=bottom bar, 056/057=151/152, 0x0801AB7E=function ani DAT_08046CC4=vtable.

## 1. Twardy stan bitmap
- 051 = 34x29
- 052 = 34x29
- 053 = 34x29
- rodzina 051..053 jest osobną grupą wymiarową 34x29.

## 2. Najważniejszy nowy trop: firmware path zasobnika
W FUN_08031CCC znaleziono dynamiczną ścieżkę zasobnika:
- panel ID 327 → 0x3740 — nadal nierozwiązana wartość,
- panel ID 328 → 0x3601 = How much fuel left in tank [kg],
- panel ID 330 → 0x3603 = Fuel reserve [kg].

Następnie firmware wykonuje:
(value_327 * 100) / value_328 → FUN_0802DA54

Wniosek [STRONG]: FUN_0802DA54 jest bezpośrednim odbiorcą wyliczonego poziomu zasobnika w istniejącym Home refresh/config path.

## 3. Most do 051/052
CAN 0x3601 (fuel remaining kg) → panel ID 328 → FUN_08031CCC → percentage calculation → FUN_0802DA54 → [OPEN] exact hopper widget state/geometry/resource writer → [OPEN] resource 051 / 052 / possibly 053.

Użytkownik potwierdził na rzeczywistym panelu, że 051/052 są drugim kafelkiem od lewej i że ich stan zależy od ilości/poziomu pelletu w zasobniku. To jest obserwacja UI, nie zastępuje firmware call-site proof.

## 4. Ważna korekta metodologiczna
Nie znaleziono w aktualnie zaindeksowanych artefaktach bezpośredniego jawnego FUN_080307BC(..., 0x33) ani FUN_080307BC(..., 0x34).
Nie wolno więc jeszcze twierdzić, że 051/052 są ustawiane przez prosty hard-coded writer call-site.

To nie obala semantyki z obserwacji użytkownika. Najbardziej prawdopodobny jest dynamiczny/pośredni widget path, analogiczny do innych komponentów, gdzie resource ID pochodzi z pola/tabeli/metody aktualizacji.

## 5. FUN_0802DA54 — obecny status
functions.txt potwierdza: 0802da54 FUN_0802da54 172 B.
Repo nie zawiera obecnie wystarczającego indeksowanego raw-disassembly/decompiled snippet, aby uczciwie zamknąć jego child/resource writer.
Nie zgadujemy, że 2DA54 bezpośrednio ustawia 051/052.

Następny właściwy krok:
1. odzyskać surowy body FUN_0802DA54 z BIN/dekompilacji,
2. rozrysować wszystkie BL/BLX oraz pola this+offset,
3. znaleźć child Bitmap/Progress/Container,
4. sprawdzić resource ID/table index,
5. sprawdzić warunek dla procentu,
6. dopiero wtedy zamknąć 051↔052 oraz ewentualne 053.

## 6. Rejestry potwierdzone
0x3600 = Tank capacity [kg]
0x3601 = How much fuel left in tank [kg]
0x3602 = Is fuel reserve
0x3603 = Fuel reserve [kg]
0x3604 = Fuel reserve stop [kg]
Panel map: 328 -> 0x3601; 329 -> 0x3600; 330 -> 0x3603.

## 7. Hipoteza progu — NIE ZAMYKAĆ
Nie wpisywać np. 20% albo 40% jako progu 051↔052 bez body 2DA54 / kolejnego caller chain.
Możliwe są: próg binarny, kilka progów, stan rezerwy, osobny parametr 0x3602/0x3603, albo tabela wyboru bitmap.

## 8. Następny punkt ataku
FUN_0802DA54 — pełny raw body.
Docelowy łańcuch: 0x3601 → panel ID 328 → FUN_08031CCC → percent → FUN_0802DA54 → hopper widget → resource selection → 051/052(/053) → threshold/state → second Home tile.

## 9. Status
051/052 semantic target = USER CONFIRMED; firmware writer/state = OPEN; upstream fuel source = STRONG/CLOSED at 0x3601 → ID328 → percentage → FUN_0802DA54.


# MULTIPASS RAW-BIN BREAKTHROUGH — FUN_0802DA54 / 051-052-053 — 2026-11-19

## PASS 1 — COMPLETE RAW BODY OF FUN_0802DA54

functions.txt: `0802da54 FUN_0802da54 172`.

Raw Thumb disassembly from BIN proves signature/roles:
`FUN_0802DA54(param_1, param_2, param_3)`

- param_1 = parent/widget object.
- param_2 = calculated fuel percentage.
- param_3 = u8 reserve-state value.

Exact first branch:
- stores param_3 at `parent + 0x2C3`;
- `CBNZ param_3` selects two resource paths.

### param_3 == 0
- `parent + 0x5A8`
- resource ID `0x33` = bitmap **051**
- `parent + 0x5F9 = 1`
- then performs geometry/position math from param_2.

### param_3 != 0
- `parent + 0x5F9 = 0`
- `parent + 0x5A8`
- resource ID `0x35` = bitmap **053**

Therefore **051/053 are not a guessed writer path anymore**. The firmware directly selects them inside FUN_0802DA54.

## PASS 2 — THE MISSING 052

Raw constructor trace shows the same parent has at least two Bitmap objects initialized with resource `0xFFFF`:
- `parent + 0x5A8`
- `parent + 0x5D4`

This comes from the constructor region beginning at `0x0802BDF0`, where both offsets are initialized through the Bitmap constructor path.

In the large setup function beginning at `0x0802C294`, the second child is explicitly assigned:
- `parent + 0x5D4`
- resource ID `0x34` = bitmap **052**
- then attached to the parent through the UI object path.

So the firmware structure is now:

`+0x5D4 = fixed 052 layer`
`+0x5A8 = dynamic 051/053 layer`

FUN_0802DA54 refreshes both `+0x5A8` and `+0x5D4` through the common refresh/dirty path at `FUN_08032316`.

This is the first hard structural explanation for why all three 051/052/053 resources belong to the same hopper visual subsystem.

## PASS 3 — EXACT CAN PARAMETER CORRECTION

The generic parameter mapper table around `0x08037984` was re-read directly from BIN.

Critical mapping entries are:

- internal `0x147` (decimal 327) -> CAN `0x3601`
- internal `0x148` (decimal 328) -> CAN `0x3600`
- internal `0x149` (decimal 329) -> CAN `0x3603`
- internal `0x14A` (decimal 330) -> CAN `0x3602`

This corrects the older ID numbering interpretation in the hopper notes. The raw mapping table is authoritative.

Therefore:
- 0x3601 = fuel remaining [kg]
- 0x3600 = tank capacity [kg]
- 0x3602 = fuel-reserve state/flag
- 0x3603 = fuel-reserve quantity/related reserve parameter

## PASS 4 — COMPLETE PERCENTAGE CHAIN IN FUN_08031CCC

At the end of FUN_08031CCC the raw sequence is:

1. `MOVW r7,#0x147`
2. generic lookup of internal `0x147` -> current `0x3601` fuel remaining
3. generic lookup of internal `0x148` -> current `0x3600` tank capacity
4. `100 * remaining / capacity` using ARM `SDIV`
5. generic lookup of internal `0x14A` -> current `0x3602` reserve flag
6. `UXTB` reserve flag
7. `BL FUN_0802DA54`

Exact call semantics:

`FUN_0802DA54(context, 100 * CAN_0x3601 / CAN_0x3600, (u8)CAN_0x3602)`

This is now **RAW-BIN PROOF**, not inference from the earlier panel CSV.

## PASS 5 — SEMANTIC RESOURCE INVENTORY

Corrected direct-BIN visual assets:
- **051** = empty/unfilled hopper outline.
- **052** = pellet-filled hopper.
- **053** = orange/yellow `E` / empty-reserve warning graphic.

The visual semantics are consistent with the firmware structure:
- 052 is the fixed hopper layer.
- 051/053 are selected dynamically on the second layer according to the reserve-state branch.

Do not invent a percentage threshold between 051 and 052: **FUN_0802DA54 does not choose 052 dynamically.** Its branch condition is the reserve-state parameter `CAN 0x3602`.

## PASS 6 — 2DA54 PERCENTAGE GEOMETRY

When reserve flag is zero, FUN_0802DA54 also computes a scaled vertical quantity from:
- `param_2` percentage,
- signed halfword at `parent + 0x5DE`,
- fixed-point multiply by `0x51EB851F` followed by `>> 5`.

`0x51EB851F` is the fixed-point reciprocal used for division by 100.

It then updates:
- `parent + 0x96A`
- `parent + 0x966`
- `parent + 0x5DA`

This is strong evidence that the percentage is used for **geometry/fill positioning**, not merely for choosing a bitmap.

## CLOSED/UPDATED GRAPH

`CAN 0x3601 (remaining kg)`
`        +`
`CAN 0x3600 (capacity kg)`
`        ↓`
`100 * remaining / capacity`
`        ↓`
`CAN 0x3602 (reserve flag)`
`        ↓`
`FUN_0802DA54(context, percent, reserve_flag)`
`        ├── reserve=0 -> Bitmap 051 on +0x5A8`
`        └── reserve!=0 -> Bitmap 053 on +0x5A8`
`                + fixed Bitmap 052 on +0x5D4`
`                ↓`
`FUN_08032316 refresh/dirty path`

## IMPORTANT METHODOLOGICAL CORRECTION

Older notes saying:
- ID328 -> 0x3601
- ID329 -> 0x3600
- ID330 -> 0x3603

were based on an offset interpretation of the panel ID table and are superseded by the raw mapping table. The firmware mapping table directly proves the internal indices above.

Do not use the old numbering for future raw traces.
