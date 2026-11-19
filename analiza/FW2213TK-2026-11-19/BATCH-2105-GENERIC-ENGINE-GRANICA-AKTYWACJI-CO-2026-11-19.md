# BATCH — 2105 → generic engine → UI oraz granica aktywacji CO — 2026-11-19

## PRZEŁOM

Zrobiono nowy trace bezpośrednio na pełnym `decompiled.c`.

Najważniejsze: **0x2105 jest już potwierdzone w kodzie wykonywalnym, ale nie jako bezpośredni sterownik tworzenia obiektów CO.** Jego wejście do firmware odbywa się przez wspólny mechanizm mapowania panelowego.

### Twardy most

```
panel index 0x10F (271)
        ↓
FUN_08036FF2(context, 0x10F)
        ↓
tabela DAT_08037B4C / DAT_08037578
        ↓
CAN index 0x2105
        ↓
wartość Heating configuration
```

Mapa firmware potwierdza:
- panel index 270 (0x10E) → CAN 0x3505
- **panel index 271 (0x10F) → CAN 0x2105**
- panel index 272 (0x110) → CAN 0x2107
- panel index 273 (0x111) → CAN 0x2106
- panel index 276 (0x114) → CAN 0x2108
- panel index 277 (0x115) → CAN 0x3501

## UDOWODNIONE — 0x2105 jest realnie odczytywane

W `FUN_08031CCC` występują dwa odczyty:

```c
uVar1 = FUN_08036FF2(*(undefined4 *)(param_1 + 8), 0x10f);
FUN_0802d3e0(*(undefined4 *)(param_1 + 0xc), uVar1, uVar8);

uVar1 = FUN_08036FF2(*(undefined4 *)(param_1 + 8), 0x10f);
FUN_0802d91c(*(undefined4 *)(param_1 + 0xc), uVar1);
```

Czyli 0x2105 nie jest tylko wpisem w katalogu — firmware używa jego aktualnej wartości w logice panelu.

## UDOWODNIONE — 0x2105 steruje stanem UI

`FUN_0802D3E0` robi:

- wartość 0 → zeruje dwa pola stanu UI,
- wartość != 0 → ustawia oba pola na 1,
- przekazuje trzeci argument do dalszej aktualizacji obiektu.

`FUN_0802D91C` przełącza stan/obraz elementu zależnie od wartości 0x2105.

To jest bardzo mocny dowód, że `Heating configuration` jest używane do **aktywacji/wyświetlania funkcjonalności związanej z ogrzewaniem** na panelu.

## WAŻNA GRANICA

W pełnym `decompiled.c` wyszukiwanie literalnego panel index `0x10F` daje tylko tę ścieżkę `FUN_08031CCC` (poza niepowiązanym użyciem bajtu offsetu w innym obiekcie).

Nie znaleziono:

```
0x2105 -> FUN_08037D00
0x2105 -> ustawienie module+0x12B
0x2105 -> ustawienie module+0x12C
```

Nie ma więc podstaw, aby twierdzić, że 0x2105 bezpośrednio tworzy obiekty CO.

## NOWA, MOCNIEJSZA HIPOTEZA

Mamy teraz dwa równoległe mechanizmy:

### A. Warstwa konfiguracji sprzętowej

```
0x3500 + 0x3502 + 0x350B
        ↓
FUN_08000E34
        ↓
wariant 2..7
        ↓
zestaw tabel/obiektów sprzętowych
```

W `FUN_08000E34` indeks wariantu jest wybierany jawnie:
- Main=0, Expansion=0, Profile=1/2/3 → warianty 2/3/4
- Main=0, Expansion=1, Profile=1/2/3 → warianty 5/6/7

### B. Warstwa funkcjonalna

```
0x2105
  ↓
generic parameter engine
  ↓
FUN_08036FF2
  ↓
UI / widoczność / aktywność funkcji
```

To bardzo dobrze tłumaczy wcześniejszą obserwację, że profil BIG nie jest liczbą obiegów CO.

## CO1..CO4 — stan obecny

Warstwa obiektowa nadal jest niezależna:

```
module + 0x12B = typ/klasa
module + 0x12C = instancja 1..4
        ↓
FUN_08036FF2 / FUN_080370C0 / FUN_08037212
        ↓
base + instance - 1
        ↓
FUN_0801167A / FUN_08011812
        ↓
rekord parametru
```

Dodatkowo `FUN_0803C064` pokazuje, że istnieje tabela klasyfikacyjna:

```
class = DAT_0803C218[param_2]
```

i wartości 1..4 prowadzą bezpośrednio do instancji 1..4.

## NAJWAŻNIEJSZY NOWY KIERUNEK

Nie szukamy już ślepo `2105 -> create CO`.

Szukamy **momentu, w którym zmiana funkcjonalnej liczby CO powoduje wybór/udostępnienie obiektów instancji**.

Priorytet:

1. `DAT_0803C218` — odzyskać pełną tablicę klasyfikacji.
2. znaleźć wszystkie wejścia do `FUN_0803C064` pośrednio przez vtable/callback.
3. znaleźć miejsca, gdzie parametry konfiguracji (`2105..2108`) wpływają na `param_2` tej klasyfikacji.
4. połączyć to z `module+0x12B/+0x12C`.
5. dopiero potem zejść do konkretnego indeksu CAN dla CO1..CO4.

## WNIOSEK

**0x2105 → generic parameter engine → rzeczywisty odczyt wartości → logika aktywności UI jest UDOWODNIONA.**

**0x2105 → bezpośrednie utworzenie CO1..CO4 NIE jest udowodnione i obecnie wygląda na błędny model.**

To jest ważne zawężenie: most do znalezienia leży najprawdopodobniej pomiędzy **funkcjonalną konfiguracją systemu a klasyfikacją/instancjonowaniem obiektów**, a nie w samym rejestrze 0x2105.
