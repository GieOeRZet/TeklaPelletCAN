# BATCH — SPINE: Home/Main root -> Heating class -> instance-aware widget values
Data: 2026-11-19

## [FW] Najważniejszy nowy klej między obiektem CO a realnym widgetem wartości

Dotychczas mieliśmy osobno:
- kandydata na root/Home: `FUN_0803E5AC` budujący duży obiekt z wieloma podkomponentami, w tym `+0x92DC -> FUN_08047290`, gdzie powstaje dokładnie 6 powtarzalnych elementów;
- komponenty CO1/CO2 z własnymi konstruktorami/vtable;
- mechanizm `+0x12C` -> `FUN_08036FF2` -> rekord parametru;
- `FUN_08031CCC` jako główny refresh/config controller Home;
- `FUN_0803E714` jako konsument `+0x12B`.

Nowy trace łączy środkową część tego modelu:

```
active object
  |
  +0x12B = 1..4
  +0x12C = instance 1..4
  +0x158 = niezależny gate wariantu UI
  |
  v
FUN_0803E714
  |
  +--> FUN_0803EFDA(param_1, DAT_0803EEC0 + 0x62, 12)
  |       |
  |       +--> 12 kolejnych 16-bitowych panel parameter IDs
  |
  +--> opcjonalnie 11 kolejnych ID z DAT_0803EEC0 + 0x6E
  |
  v
dla każdego ID:
  FUN_08036FF2(context, parameter_id)
       |
       +--> instance-aware base + (+0x12C - 1)
       |
       v
  FUN_0804842C(...)
       |
       +--> widget record = param_1 + index*0x338 + 0x42C
       +--> FUN_0804E5BC(value)
       +--> FUN_08032316(refresh)
```

To jest [FW] end-to-end: **klasa/instancja obiektu -> lista parametrów Heating -> mapper instancji -> konkretny rekord widgetu -> wartość -> refresh**.

## [STRONG] Co to zmienia w modelu 1:1

Nie trzeba rekonstruować czterech niezależnych ekranów CO1/CO2/CO3/CO4.

Firmware ma wspólny builder dla klas `+0x12B=1..4`. Różnica między CO1..CO4 powstaje w engine parametrów przez `+0x12C`.

Czyli właściwy model źródłowy jest bliższy:

```
Heating/CO component class
        |
        +-- common widget tree
        |
        +-- parameter ID list
        |
        +-- active instance selector
                 |
                 +-- CO1 / CO2 / CO3 / CO4
```

To bardzo dobrze pasuje do architektury TouchGFX/C++ z reużywalnymi Container/widgetami.

## [FW] Niezależny trzeci wymiar

`+0x158` nie jest numerem CO.

`FUN_08037E74(param_1,param_2)` mapuje:
- 0 -> +0x158=0
- 900 -> 1
- 999 -> 2
- 0x1BF1 -> 3

Przy `+0x158 != 0` builder dopina drugą grupę 11 parametrów.

Zatem nie wolno modelować tego jako:
`+0x158 = CO number`.

Mamy trzy osobne osie:
1. `+0x12B` = klasa/rodzina obiektu,
2. `+0x12C` = instancja CO1..CO4,
3. `+0x158` = wariant/tryb UI.

## [STRONG] Najbardziej prawdopodobne miejsce „kleju” dla ekranu głównego

`FUN_0803E5AC` pozostaje mocnym kandydatem na konstruktor dużego Home/Main obiektu:
- tworzy wiele podkomponentów pod stałymi offsetami,
- `+0x92DC -> FUN_08047290`,
- `FUN_08047290` tworzy dokładnie 6 powtarzalnych elementów.

Nie ma jeszcze bezpośredniego dowodu, że `FUN_0803E714` jest wywoływane bezpośrednio z `FUN_0803E5AC`; tego nie dopisywać jako fakt.

Natomiast mamy już logiczny model:
```
Home/Main root candidate
  |
  +--> repeated navigation/status widgets
  |
  +--> Heating class object
          |
          +--> common 12/11-param widget list
          |
          +--> instance-aware value lookup
```

## [DATA] Co nadal blokuje pełną rekonstrukcję menu Heating

Brakuje surowych słów tabeli:
`DAT_0803EEC0 + 0x62` — 12 bazowych ID,
`DAT_0803EEC0 + 0x6E` — 11 dodatkowych ID.

Brakuje również zawartości:
`DAT_0803C218` — 108 B klasyfikacji `param_2 -> class`.

Po odzyskaniu tych danych można zrobić dokładną tabelę:
`class -> parameter ID -> instance -> resolved record -> widget`.

## [CORRECTION]

Nie wracać do:
- `+0x12B = numer CO` — błędne;
- `+0x158 = numer CO` — błędne;
- `0x2105) jako udowodnionego źródła liczby aktywnych CO — nadal nieudowodnione;
- czterech kopii całego drzewa UI — firmware wskazuje na wspólny builder klas 1..4.

## Następny atak

1. Odzyskać `DAT_0803EEC0` i `DAT_0803C218` z pamięci Ghidra/BIN.
2. Rozwinąć `FUN_080480C0/FUN_0804842C/FUN_0804E5BC` do konkretnych typów widgetów i ich TypedText/Bitmap.
3. Znaleźć indirect/vtable entry do `FUN_0803E714`.
4. Równolegle znaleźć parent/add() dla komponentów CO1/CO2 i root `FUN_0803E5AC`.
5. Dopiero wtedy przypinać konkretne pozycje Home screenshotu do obiektów.

Status:
- [FW] klasa -> lista parametrów -> instance -> widget value -> refresh
- [STRONG] wspólny builder dla CO1..CO4
- [HYPOTHESIS] bezpośrednie osadzenie 3E714 w Home root nadal niepotwierdzone
