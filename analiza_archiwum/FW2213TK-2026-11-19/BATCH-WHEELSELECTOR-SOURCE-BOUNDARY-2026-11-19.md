# BATCH — WheelSelectorExtra: granica prawdziwego compile unitu — 2026-11-19

## 1. Nowa korekta: nie FUN_08038ED0 jest obecnie najlepszym punktem identyfikacji pliku źródłowego

Mamy:
- string assert: `0x08038D74` = `extraTextIndex < NUMBER_OF_EXTRA_TEXTS`
- string ścieżki: `0x08038D9C` = `C:\\Estyma\\igneoTOUCH\\app\\nasze\\igneoTFT\\gui\\src\\components\\WheelSelectorExtra.cpp`

Lista funkcji:
- `FUN_08038CF4` zaczyna się `0x08038CF4`, ma 126 B i kończy się na `0x08038D71`.
- następne rozpoznane funkcje zaczynają się dopiero:
  - `0x08038DF0`
  - `0x08038E04`
  - `0x08038E18`
  - `0x08038E2C`
  - itd.

Czyli oba stringi z assertu/ścieżki leżą **bezpośrednio po końcu FUN_08038CF4**, odpowiednio od `0x08038D74` i `0x08038D9C`.

## 2. [STRONG] Co to zmienia

To daje znacznie mocniejszy związek:

```
FUN_08038CF4
     |
     +-- literal/reference pool
     |
0x08038D74  "extraTextIndex < NUMBER_OF_EXTRA_TEXTS"
0x08038D9C  "...WheelSelectorExtra.cpp"
     |
     v
następne metody tego samego gęstego bloku:
38DF0
38E04
38E18
38E2C
38E80
38E94
38ED0
38F80
39010
3904C
39068
3907C
39090
390A4
390BA
390FC
```

To jest obecnie lepszy dowód na granicę compile-unitu/custom componentu niż wcześniejsze przypisanie `FUN_08038ED0` do konstruktora.

## 3. [CORRECTION] FUN_08038ED0 nie nazywamy już konstruktorem WheelSelectorExtra

Wcześniej zapisaliśmy:

`root+0xA5FC -> FUN_08038ED0`
`root+0xA628 -> FUN_08038ED0`

i postawiliśmy hipotezę, że `FUN_08038ED0` może być konstruktorem WheelSelectorExtra.

Na obecnym materiale nie mamy vptr/write proof.

Dlatego:
- nadal jest to funkcja należąca do **bardzo silnie podejrzanego bloku custom TouchGFX**,
- ale nie nazywamy jej konstruktorem,
- nie twierdzimy jeszcze, że dwa obiekty Home są instancjami WheelSelectorExtra.

Wymagany dowód: zapis vptr / wejście z konstruktora / tabela wirtualna.

## 4. [STRONG] FUN_08038CF4 jest teraz najlepszym kandydatem na funkcję zawierającą kod związany z assert-em WheelSelectorExtra

Powód jest czysto adresowy:
`FUN_08038CF4` kończy się dokładnie przed stringiem assertu.

To nadal nie pozwala nazwać funkcji np. `setExtraText()`, ponieważ nie mamy dekompilacji tego konkretnego ciała w repo dostępnym przez indeks GitHub.

Nie zgadujemy nazwy metody.

## 5. [FW] Gęsty blok metod

Funkcje tego obszaru mają bardzo charakterystyczny rozkład rozmiarów:

- 38CF4 — 126 B
- 38DF0 — 16 B
- 38E04 — 16 B
- 38E18 — 16 B
- 38E2C — 68 B
- 38E80 — 16 B
- 38E94 — 58 B
- 38ED0 — 20 B
- 38F80 — 62 B
- 39010 — 28 B
- 3904C — 26 B
- 39068 — 16 B
- 3907C — 16 B
- 39090 — 20 B
- 390A4 — 22 B
- 390BA — 66 B
- 390FC — 122 B

Taki układ jest zgodny z obecnością wielu małych metod/getterów/setterów/wrapperów wokół większych metod klasy C++, ale bez vtable/call-site nie przypisujemy jeszcze konkretnych ról.

## 6. [FW] Home/Main nadal ma dwa wywołania FUN_08038ED0

Niezależnie od powyższej korekty zachowujemy twardy wynik wcześniejszej analizy:

```
FUN_0803E5AC (kandydat Home/Main root)
  +0xA5FC -> FUN_08038ED0
  +0xA628 -> FUN_08038ED0
```

To jest fakt o konstrukcji dużego obiektu.

Interpretacja „dwa WheelSelectorExtra” pozostaje hipotezą.

## 7. [DATA] Prawdziwe bitmapy pozostają osobną, zamkniętą warstwą

Potwierdzone:
- 189 plików PNG w `web/img/panel/` pochodzi z tablicy bitmap FW pod `0x54450`.
- 011 = 105x126
- 012 = 108x141
- 013 = 82x145
- 014 = 54x100

Kod webowej repliki jawnie traktuje `013.png` jako domyślny „czerwony kocioł / oryginalny kocioł Estyma”, a alternatywy 011/012/014 mają własne proporcje.

**Ale:** to jest informacja o implementacji repliki WWW i wyciągniętych assetach, nie dowód call-chainu firmware `0x370A -> 013`.

## 8. [STRONG] Wniosek z rozbieżności 1..3 vs 11..14

Mamy:
- FW: `0x370A = 1..3`
- assety: `011..014` = cztery grafiki

Zatem proste mapowanie 1:1 jest niemożliwe.

Co najmniej jeden z tych mechanizmów musi zachodzić:
1. selector 1..3 wybiera klasę/rodzinę, a bitmapa jest wybierana dodatkowo;
2. jedna bitmapa jest fallbackiem/defaultem;
3. hardware/profile wybiera jeden poziom, a 370A drugi;
4. numeracja 11..14 w aplikacji jest mapowaniem wyższego poziomu.

To jest ważne: **nie będziemy już próbować zgadywać 1→11, 2→12, 3→13.**

## 9. [NEXT] Najcenniejszy następny dowód

Dwa konkretne cele:

### A. WheelSelectorExtra
Odzyskać:
```
FUN_08038CF4
    ↓
vptr / this layout
    ↓
vtable
    ↓
38DF0...390FC
    ↓
konkretna metoda / pola extraText
```

### B. Boiler image
Odzyskać:
```
0x370A / RAM 0x20021FA6
    ↓
read/use
    ↓
warunek 1..3
    ↓
resource index
    ↓
TouchGFX Bitmap
```

Dopiero wtedy możemy zbudować pierwszy fragment Home, który będzie miał jednocześnie:
- prawdziwy asset,
- prawdziwy parametr wariantu,
- prawdziwy obiekt TouchGFX,
- prawdziwą geometrię.

## 10. Nie regresować

- `0x370A` jest nazwane przez oryginalny FW: **Boiler image selector**.
- jego wartość ze snapshotu to 3 po odjęciu flagi 256.
- nie utożsamiać 370A z numeracją bitmap 11..14.
- nie utożsamiać numeru seryjnego z mechanizmem runtime bez call-chainu.
- nie nazywać FUN_08038ED0 konstruktorem bez vptr proof.
- grafika z wcześniejszego renderu była generowana i nie jest assetem FW.
