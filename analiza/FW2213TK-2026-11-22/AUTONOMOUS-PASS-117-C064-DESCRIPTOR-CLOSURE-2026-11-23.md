# AUTONOMOUS PASS 117 — C064 CASE 16/17/18 DESCRIPTOR-CLOSURE — 2026-11-23

Firmware: FW2213TK_kopia.bin
SHA-256: `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`

## Cel
Dalsze S1.3: rozdzielić dokładnie ścieżki dispatcherów selectorów 16/17/18 i sprawdzić, czy selector 18 jest tylko „alternate setter”, czy pełnym wariantem tego samego mechanizmu budowy obiektu/struktury.

## [NEW-HARD] C064 ma wspólny post-dispatch descriptor path

Z committed raw snippet `0803c064-decompiled.c.txt`:

- selector 16:
  - `FUN_080314ba()`
  - `context+0x12B = 0x11`
  - `puVar5 = &DAT_08038790`
  - następnie `FUN_08039494(..., *puVar5, puVar5[1])`
  - wynik przez `FUN_080394A8(context+0x110, result)`
  - `context+0x10C = context+0x110`

- selector 17:
  - `FUN_080314ba()`
  - `context+0x12B = 0x10`
  - `puVar5 = &DAT_08038790`
  - identyczny wspólny builder `08039494 -> 080394A8`
  - `context+0x10C = context+0x110`

- selector 18:
  - `FUN_080314ba()`
  - `puVar5 = &DAT_080387B8`
  - przechodzi przez TEN SAM `08039494 -> 080394A8`
  - `context+0x10C = context+0x110`

### Wniosek
Selector 18 NIE jest wyłącznie „innym setterem +0x12B”. Jest osobnym wariantem tego samego końcowego mechanizmu konstrukcji/instalacji obiektu pod `context+0x110`, różniącym się źródłem descriptor pair:

- 16/17 -> `DAT_08038790`
- 18 -> `DAT_080387B8`

To zamyka wcześniejszą zbyt ogólną etykietę „selector 18 -> alternate setter path”.

## [NEW-HARD] Selector 20 ma jeszcze trzeci wariant
Case 20:
- `FUN_080314ba()`
- bezpośrednio zapisuje `context+0x12B = 0x13`
- buduje końcowy obiekt przez wspólny mechanizm `08039494/080394A8`
- descriptor zależy od `context+0x12A`: `DAT_08038770` albo `DAT_08038778`.

Czyli klasy 16/17/18/20 tworzą spójną rodzinę „context variant -> descriptor pair -> object install”, ale nie są tym samym wariantem.

## [STRONG] Znaczenie +0x10C/+0x110
Dla przypadków 16/17/18:
- `context+0x110` jest miejscem docelowym wyniku buildera,
- `context+0x10C` dostaje wskaźnik na `context+0x110`.

Nie oznacza to jeszcze semantycznie „model”, „presenter” ani „CAN callback”. Nazwa pozostaje OPEN.

## [OPEN]
Nadal nie znamy literalnej zawartości descriptorów:
- `DAT_08038790` (pair używany przez 16/17),
- `DAT_080387B8` (pair używany przez 18),
ani dokładnego znaczenia argumentów `FUN_08039494`.

To jest teraz najkrótsza droga do rozróżnienia semantycznego 16/17/18 bez zgadywania z bitmap/geometrii.

## Status S1.3
- registry index -> C064: CLOSED
- 16 -> +0x12B 0x11: CLOSED
- 17 -> +0x12B 0x10: CLOSED
- 18 -> separate path: CLOSED
- 18 -> SAME builder family, DIFFERENT descriptor pair: NEW-HARD
- human title/PID/resource/callback of records 16/17/18: OPEN
- literal descriptor bytes 0x08038790/0x080387B8: OPEN

## Następny atak
1. odzyskać bytes/data declarations dla 0x08038790 i 0x080387B8;
2. rozebrać FUN_08039494 i FUN_080394A8;
3. prześledzić obiekt powstały pod context+0x110 do widget/presenter/model;
4. dopiero wtedy przypisać semantykę rekordom 16/17/18.
