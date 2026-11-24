# PRZEŁOM-CO-2105-ROZDZIELENIE-COUNT-vs-CONFIG-2026-11-19

Data: 2026-11-19

## Cel

Rewalidacja mostu:

`0x10E / 0x3505` -> liczba/aktywacja instancji CO
`0x10F / 0x2105` -> konfiguracja ogrzewania
`+0x12C` -> numer instancji
`0x2032 + instance - 1` -> CAN CO1..CO4

## 1. Najważniejszy wynik

W bieżącej dekompilacji trzeba **rozdzielić 0x10E od 0x10F**.

Funkcja `FUN_08031CCC` używa obu parametrów zupełnie inaczej:

- `0x10E` jest sprawdzany jako próg:
  - `> 0` -> aktywacja pierwszego elementu CO,
  - `> 1` -> aktywacja drugiego elementu CO.
- `0x10F` jest przekazywany do `FUN_0802D3E0` oraz `FUN_0802D91C`.
- `FUN_0802D3E0` traktuje `0x10F` binarnie: 0 = ukryj, !=0 = pokaż/odśwież.
- `FUN_0802D91C` zmienia grafikę/stany zależnie od 0x10F.

Czyli wcześniejsze utożsamienie `0x2105` z liczbą obwodów CO było zbyt mocne i zostaje odrzucone.

## 2. Twardy most dla instancji

W raw firmware znaleziono ścieżki:

- raw `0x32146` / runtime `0x08042146`:
  - sprawdza parametr `0x10E`,
  - dla dostępnej instancji 1 wywołuje `0x38130` z `r1=1`.
- raw `0x32166` / runtime `0x08042166`:
  - analogicznie dla instancji 2,
  - wywołuje `0x38130` z `r1=2`.

Dodatkowo runtime `0x0803C0B6` zawiera bezpośrednie ścieżki z `r1=1,2,3,4`, wszystkie kończące się w `0x38130`.

To daje znacznie mocniejszy dowód:

```
0x10E
  |
  +-- dostępna instancja 1 -> 0x38130(r1=1)
  |
  +-- dostępna instancja 2 -> 0x38130(r1=2)
  |
  +-- inne ścieżki mogą wybrać 1..4
  |
  v
module + 0x12C = instance
```

## 3. 0x38130

Kod w `0x08048130` normalizuje wejściowe `r1` do zakresu 1..4 i zapisuje je do:

`module + 0x12C`

Jednocześnie zależnie od instancji ustawia powiązany typ/stan w obszarze około `+0x11F/+0x10C`.

To jest rzeczywisty mechanizm numerowania instancji, a nie interpretacja tabeli.

## 4. Dynamiczny lookup parametrów

Po ustawieniu `+0x12C` funkcje:

- `0x080370C0`
- `0x08037172`
- `0x08037212`
- `0x0801167A`

korzystają z numeru instancji.

Dla specjalnej tabeli parametrów obowiązuje:

`lookup = base_index + module[0x12C] - 1`

Dla rodziny CO:

- baza `0x2032`
- instancja 1 -> `0x2032`
- instancja 2 -> `0x2033`
- instancja 3 -> `0x2034`
- instancja 4 -> `0x2035`

To jest już twardy mechanizm indeksowania, niezależny od nazewnictwa UI.

## 5. Znaczenie 0x10E w tym mechanizmie

Najsilniejszy obecnie wniosek:

`0x10E` jest bezpośrednio związany z **dostępnością liczby instancji**, ponieważ kod tworzący/konfigurujący obiekty sprawdza go przed wywołaniem `0x38130` dla instancji 1 i 2.

Nie należy jednak jeszcze nazywać go bezwarunkowo „liczbą obwodów CO”, dopóki nie zostanie znaleziony cały kod obsługujący instancje 3/4 oraz źródło wartości 0x10E.

To ważne, bo mapa CAN mówi:

`panel 0x10E -> CAN 0x3505`

a rejestr `0x3505` ma w obecnym katalogu nazwę „Outside temperature sensor configuration”. Ta nazwa pochodzi z warstwy katalogowej/panelowej i nie jest wystarczającym dowodem semantyki runtime.

Kod ma pierwszeństwo.

Możliwa semantyka jest więc taka, że 0x3505/0x10E steruje dostępnością konfiguracji zależnej od obwodów, np. funkcji pogodowej, a nie samą liczbą obwodów. To wymaga dalszego trace'u.

## 6. 0x10F / 0x2105

Mapa:

- panel `0x10F`
- CAN `0x2105`
- nazwa panelowa: `Heating configuration`
- zakres panelowy: 0..4.

W `FUN_08031CCC` wartość ta:

1. trafia do `FUN_0802D3E0`,
2. trafia do `FUN_0802D91C`.

`FUN_0802D3E0`:

- 0 -> dwa pola UI = 0,
- !=0 -> dwa pola UI = 1,
- następnie odświeża widget przez `FUN_08033070`.

`FUN_0802D91C`:

- 0 -> grafika/styl wariantu OFF,
- !=0 -> grafika/styl wariantu ON.

Zatem w tym miejscu 0x2105 jest **konfiguracją/stanem funkcji ogrzewania dla UI**, a nie bezpośrednim generatorem instancji CO.

## 7. Rozdzielenie warstw

Obecny, bardziej poprawny model:

```
CAN 0x3505
    |
    v
panel index 0x10E
    |
    +----> logika dostępności / aktywacji instancji
    |          |
    |          +--> 0x38130(r1=1..4)
    |                    |
    |                    +--> module+0x12C
    |
    +----> UI zależne od dostępności CO/funkcji

CAN 0x2105
    |
    v
panel index 0x10F
    |
    +----> FUN_0802D3E0
    +----> FUN_0802D91C
              |
              +--> stan/grafika konfiguracji ogrzewania

module+0x12C
    |
    v
0x36FF2 / 0x370C0 / 0x37172 / 0x37212
    |
    v
base + instance - 1
    |
    v
0x2032 / 0x2033 / 0x2034 / 0x2035
```

## 8. Co to zmienia w dalszym reverse engineeringu

Najbliższy cel nie brzmi już:

`2105 -> CO1..CO4`

tylko:

`0x10E -> dokładna logika tworzenia/aktywacji instancji -> 0x38130 -> 0x12C -> 0x2032..35`

a osobno:

`0x2105 -> pełna funkcja Heating configuration`

Następnie trzeba znaleźć źródła wartości 0x10E i 0x10F oraz sprawdzić, czy 0x2105 wpływa na wybór klasy obiektu pośrednio.

## 9. Ważna obserwacja o 0x3C064

`FUN_0803C064` jest rzeczywistym dispatcherem klas obiektów:

`class = DAT_0803C218[param_2]`

Klasy 1..4 prowadzą do ustawienia instancji 1..4, natomiast klasy 5..10 oraz 0x0B..0x14 prowadzą do wyspecjalizowanych konstruktorów/ścieżek.

Nie znaleziono bezpośredniego call-site w dekompilacji; prawdopodobna jest ścieżka przez tabelę/vtable lub kod nierozpoznany przez Ghidrę.

To pozostaje jednym z kluczowych miejsc do odzyskania, ponieważ może być właśnie warstwą łączącą konfigurację funkcjonalną z typem obiektu.

## Status

**NOWY TWARDY WNIOSEK:**

`0x2105 != bezpośrednia liczba instancji CO`

oraz:

`0x10E -> warstwa dostępności instancji -> 0x38130 -> +0x12C`

jest obecnie najlepiej udokumentowanym mostem do CO1..CO4.

Następny priorytet: źródło 0x10E + pełna ścieżka instancji 3/4 + odzyskanie DAT_0803C218/vtable.
