# BATCH — MULTIPASS CONTINUATION: C064/VTable + 0x10E/0x110..0x114 AUDIT — 2026-11-19

## Cel
Kontynuacja po repo-audycie bez cofania do początku. Ten batch konsoliduje kilka ścieżek, które były łatwe do pomieszania.

## 1. C064 / VTABLE — co faktycznie mamy

`FUN_08037CA4` ustawia pierwszy word obiektu na `DAT_08038694`, a następnie na `DAT_0803869C`. W tym samym obszarze:
- `FUN_08037C1E`
- `FUN_08037C70`

wykonują rzeczywiste wywołania przez vtable na slotach m.in. +0x04/+0x08/+0x0C/+0x10/+0x14/+0x28.

To jest twardy dowód, że **moduł/aktywny obiekt ma prawdziwą warstwę polimorficzną i indirect dispatch**.

Nie wolno jednak przenosić automatycznie tej konkretnej vtable na C33E/C5B4. Dla C33E/C5B4 nadal nie mamy dowodu konkretnej tablicy.

## 2. C064 — aktualny model

```
param_2
  -> DAT_0803C218[param_2]
  -> class/type
  -> +0x12B = type
  -> +0x12C = instance dla class 1..4
  -> descriptor
```

`+0x12B` nie jest „numerem CO”; wartości 1..4 są jednocześnie klasami i instancjami w tej gałęzi, ale enum obejmuje także 0, 5..10, 0x10, 0x11, 0x13 itd.

`FUN_08037D00` dodatkowo normalizuje istniejący type +0x12B do +0x12C.

## 3. Druga ścieżka +0x12C — 4107C

`FUN_08040FC2` zapisuje +0x12C z trzeciego pola `DAT_0804107C`, ale dalszy audyt repo sklasyfikował tę tabelę jako **Test I/O** (22 testy pomp/mieszaczy itd.), nie jako główny mechanizm aktywacji CO.

Nie używać jej jako mostu 2105 -> CO.

## 4. 0x10E

Twardy kod w `FUN_08031CCC`:

```
FUN_08036FF2(context, 0x10E)
  -> value > 0
  -> FUN_0802D3BC(...)

FUN_08036FF2(context, 0x10E)
  -> value > 1
  -> FUN_0802D3CE(...)
```

Daje to rzeczywisty fan-out:
- 0: oba elementy wyłączone,
- 1: pierwszy,
- >=2: pierwszy + drugi.

Ale nie wolno utożsamiać tych dwóch widgetów z CO1/CO2 bez mostu obiektowego.

Panel mapuje 0x10E -> CAN 0x3505. Katalogowa nazwa 3505 jest niespójna z tym, co robi kod, dlatego semantyka musi być rozstrzygana z runtime, nie z samej nazwy.

## 5. 0x10F / 0x110 / 0x111 / 0x114

Potwierdzona mapa:

- 0x10F -> CAN 0x2105
- 0x110 -> CAN 0x2107
- 0x111 -> CAN 0x2106
- 0x114 -> CAN 0x2108
- 0x115 -> CAN 0x3501

W `FUN_08031CCC` twardo udowodnione jest bezpośrednie użycie **0x10F**:
```
0x10F -> FUN_0802D3E0(value,...)
0x10F -> FUN_0802D91C(value)
```

Wyszukiwanie repo nie dostarczyło nowego twardego call-site dla 0x110/0x111/0x114 do D3BC/D3CE/D3E0/D91C. Zatem nie wolno obecnie budować teorii „0x110=CO3, 0x111=CO4” tylko dlatego, że są sąsiednimi parametrami.

## 6. CO1..CO4 — prawdziwa wspólna warstwa

Twardy łańcuch pozostaje:

```
class 1..4
  -> FUN_0803E714
  -> DAT_0803EEC0 + 0x62
  -> 12 kolejnych 16-bit IDs
  -> FUN_08036FF2(id)
  -> FUN_0804842C
  -> widget/value refresh

+0x158 != 0
  -> dodatkowe 11 IDs
```

Znane rodziny count=4:
- 0x2032..0x2035
- 0x2048..0x204B
- 0x2064..0x2067

Engine używa `base + instance - 1`.

To jest właściwa architektura CO1..CO4, ale nadal brakuje:
- zawartości C218,
- źródła param_2,
- dokładnych 12/11 IDs z EEC0.

## 7. CO assets 144/146

Potwierdzone:
- 144.png = CO1 active
- 145.png = CO1 variant
- 146.png = CO2 active
- 147.png = CO2 variant

Brak bezpośredniego potwierdzenia `FUN_080307BC(...,0x90/0x92)` w dostępnych artefaktach.

Nie łączyć ich jeszcze z 0x10E tylko przez screenshot/geometrię.

## 8. C33E/C5B4 — stan bez zmian

C33E tworzy sześć Bitmap:
`+0x330,+0x35C,+0x85C,+0x888,+0x8B4,+0x8E0`.

C5B4:
- +0x85C -> (40,70), attach przez parent+0x04
- +0x8E0 -> resource 0x7A=122, X=398, Y=runtime
- 122.png = 35x37

+0x84C jest osobnym obiektem/helperem inicjalizowanym przez 424C4; nie jest udowodnionym parentem +0x85C.

C5B4 nadal nie ma bezpośredniego BL ani potwierdzonego function-pointer target.

## 9. Ważna meta-korekta dokumentacji

Starsze batch'e zawierają sprzeczne opisy obecności CACC/CB04/CB2C w `functions.txt`. Aktualny odczyt canonical `functions.txt` pokazuje normalne wpisy dla:
- CACC
- CB2C

Dlatego najnowsza korekta repo-auditu ma pierwszeństwo: nie traktować CACC/CB2C jako „hidden” tylko na podstawie starszego batcha.

## 10. Aktualny priorytet

Nie wracamy do zamkniętego 370A.

Najbardziej wartościowe nierozwiązane gałęzie:

A.
```
C33E
 -> C5B4 dispatch
 -> +0x84C / 424C4
 -> +0x888/+0x8B4/+0x8E0 mutations
```

B.
```
C064 indirect entry
 -> param_2
 -> C218
 -> class 1..4
 -> D00
 -> +0x12C
 -> E714
 -> EEC0
 -> widget/value
```

C.
```
0x10E
 -> D3BC/D3CE
 -> exact UI objects
 -> determine whether they meet 144/146
```

Najbardziej potrzebny artefakt do zamknięcia B to surowy export pamięci:
- 0x0803C218..0x0803C283
- 0x0803EEC0..0x0803F008
- DAT_08038694/98/9C

Jeżeli BIN zostanie ponownie dostarczony, te zakresy należy odczytać bezpośrednio zamiast zgadywać.

## Status
Nie znaleziono jeszcze nowego mostu 0x10E -> 144/146.
Nie znaleziono nowego mostu 2105 -> C064.
Najważniejszy utrzymany wynik: oddzieliliśmy konfigurację UI, klasyfikację obiektu, instancję i wspólny Heating builder jako cztery różne warstwy.
