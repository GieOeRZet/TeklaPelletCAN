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