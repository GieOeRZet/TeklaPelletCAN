# BATCH — BITMAP ATLAS → CO1/CO2 + KONFIGURACJA WIDOCZNOŚCI — 2026-11-19

## Nowy stan po kolejnym przebiegu

### 1. Assety CO są już znane wizualnie
W katalogu `web/img/panel/`:
- 144.png = 41x36, CO1 — aktywna ikona grzejnika z numerem 1.
- 145.png = 41x36, wariant CO1.
- 146.png = 43x36, CO2 — aktywna ikona grzejnika z numerem 2.
- 147.png = 43x36, wariant CO2.

To jest zgodne z rzeczywistym screenshotem użytkownika: czwarty kafelek dolnej belki to CO1; piąty jest pusty przy konfiguracji jednego obwodu i może stać się CO2 przy drugim obwodzie.

### 2. Ważna korekta architektury
Poprzednie dokumenty zawierały zbyt mocne twierdzenie:
`FUN_08047244 + FUN_08047290[6] = siedem dolnych kafelków`.

Pełna analiza `FUN_08047334` wykazała, że `FUN_08047290` układa sześć rekordów PIONOWO, z Y około:
50, 84, 118, 152, 186, 220 px.
Dlatego `47290` nie jest sześcioma poziomymi kafelkami dolnego paska. Ta interpretacja jest anulowana.

`FUN_08047244` pozostaje osobnym komponentem, ale jego dokładna semantyka/resource nadal wymaga dowodu.

### 3. Twardy mechanizm warunkowej aktywacji UI
W `FUN_08031CCC`:
`FUN_08036FF2(context, 0x10E)` daje wartość używaną jako próg:
- value > 0 → pierwszy element UI,
- value > 1 → drugi element UI.

To jest bezpośredni fan-out do dwóch elementów, ale NIE dowodzi jeszcze, że są to dokładnie CO1/CO2.

Osobna ścieżka:
`0x10F -> 0x2105 -> FUN_0802D3E0 / FUN_0802D91C`
steruje stanem/grafiką konfiguracji ogrzewania. Nie należy utożsamiać 0x2105 z liczbą obwodów CO.

### 4. CO1..CO4 istnieją jako osobne elementy UI
Firmware ma:
- TypedText 119 = Ogrzewanie obwód 1
- TypedText 120 = Ogrzewanie obwód 2
- TypedText 121 = Ogrzewanie obwód 3
- TypedText 122 = Ogrzewanie obwód 4

To jest niezależny twardy dowód, że UI przewiduje co najmniej cztery numerowane obwody.

### 5. Czego jeszcze NIE twierdzimy
Nie znaleziono jeszcze bezpośredniego, twardego call-site w dostępnych repozytoryjnych artefaktach:
`FUN_080307BC(..., 0x90)` dla resource 144,
ani analogicznego `0x92` dla 146.

Wniosek: 144/146 są potwierdzonymi assetami semantycznymi przez rzeczywisty UI/repo, ale ich bezpośredni firmware resource writer pozostaje do odzyskania z raw BIN lub z nierozpoznanego fragmentu dekompilacji.

### 6. Aktualny kierunek
Nie wracamy do zgadywania po geometrii.

Najbliższy trace:
`0x10E -> D3BC/D3CE -> konkretny obiekt UI -> pola bitmap/TypedText/visibility`
oraz osobno:
`0x10F/0x2105 -> D3E0/D91C -> obiekt/grafika`.

Równolegle trzeba odzyskać dokładny child/resource dla `FUN_08047244` i sprawdzić, czy jest to pierwszy element dolnej belki, a następnie znaleźć pozostałe komponenty siedmiu stref po ich rzeczywistych bitmapach.

## Zasada
Każde przypisanie kafelka do funkcji musi mieć co najmniej:
1. rzeczywisty asset,
2. firmwareowy resource/child albo TypedText,
3. oraz ślad warunku/obiektu.
