# TeklaPelletCAN — MASTER STATE CONSOLIDATED / HANDOFF
Data: 2026-11-19
Repo: GieOeRZet/TeklaPelletCAN
Branch: ccr-be8a1bcb-5t76j0

> **JEDEN DOKUMENT STARTOWY DLA NOWEGO CHATA/AGENTA.**
> Najpierw przeczytaj ten plik. Potem dopiero sięgaj do batchy wskazanych w §18.
> Nie zaczynaj analizy od zera.

---

# 1. CEL NADRZĘDNY

Badamy **oryginalny firmware panela IGNEO Touch — FW2213TK.bin**.

Cel końcowy:
**odtworzyć panel możliwie 1:1, a następnie wykorzystać wiedzę do własnej implementacji na ESP.**

1:1 oznacza:
- ekrany, przejścia i menu,
- TouchGFX widget tree / parent-child,
- bitmapy, TypedText, fonty,
- X/Y/W/H, warstwy i clipping,
- visibility/state,
- touch/callbacki,
- parameter engine,
- CAN/CANopen read/write,
- CO1..CO4,
- konfigurację funkcjonalną i sprzętową,
- startup/display,
- alarmy/statusy/timery/state machine,
- service/test I/O,
- storage/persistencję,
- warianty sprzętowe,
- zależności pomiędzy UI, logiką i CAN.

**Nie budujemy „ładnego podobnego ekranu”. Odtwarzamy zachowanie oryginału.**

---

# 2. ŹRÓDŁO ANALIZY

Firmware panela:
- `firmware/FW2213TK-ghidra/decompiled.c`
- `firmware/FW2213TK-ghidra/functions.txt`
- `firmware/FW2213TK-ghidra/strings.txt`
- `firmware/FW2213TK-ghidra/README.md`

BIN:
- rozmiar: **2 031 616 B**
- SHA256: `1d679d6810cfb44a1c862d67552b7220f3edeb3a2807f3067d46185d0c5071`

To jest **firmware panela**, nie nasz ESP32-C6.

Adresowanie:
```
runtime/Ghidra = 0x08000000 + raw_offset
```

**Nie dodawać +0x10000 do adresów funkcji.**
Osobna przestrzeń +0x10000 dotyczy części wskaźników tekstów/assetów.

---

# 3. NAJWAŻNIEJSZY MODEL SYSTEMU

Docelowy model reverse engineeringu:

```
BOOT / INIT
   ↓
HW / DISPLAY
   ↓
APPLICATION / ROOT OBJECT
   ↓
CONFIG / PERSISTENT STATE
   ↓
CAN / PARAMETER ENGINE
   ↓
APPLICATION STATE
   ↓
SCREEN / MENU DISPATCH
   ↓
TouchGFX WIDGET TREE
   ↓
Bitmap / TypedText / Geometry / Visibility
   ↓
Touch / Callback
   ↓
Parameter READ/WRITE
   ↓
CAN / STORAGE / SIDE EFFECTS
```

Każdy ważny element opisujemy:
**wejście → warunek → funkcja → stan → wyjście → efekt → zależności.**

---

# 4. PRAWDZIWY TOUCHGFX PRODUCENTA — KLUCZOWY TROP

Firmware zawiera ślad konkretnego projektu producenta:

```
C:\Estyma\igneoTOUCH\app\nasze\igneoTFT\gui\src\components\WheelSelectorExtra.cpp
```

oraz:
```
extraTextIndex < NUMBER_OF_EXTRA_TEXTS
```

Adresy:
- `0x08038D74` — assert,
- `0x08038D9C` — ścieżka `WheelSelectorExtra.cpp`.

Potwierdzone ślady frameworka:
- Application.cpp
- MVPApplication.hpp
- Container.cpp
- Bitmap.cpp
- Slider.cpp
- TypedText.hpp
- Bitmap.hpp
- RadioButtonGroup.hpp
- Canvas.cpp
- HAL.cpp
- LCD16bpp.cpp.

**Wniosek [STRONG]:** analizujemy nie anonimowy GUI, lecz ślad konkretnego projektu TouchGFX Estymy.

---

# 5. WHEELSELECTOREXTRA — AKTUALNA KOREKTA

`FUN_08038CF4`:
- start `0x08038CF4`,
- 126 B,
- kończy się `0x08038D71`.

Bezpośrednio po nim leżą stringi assert/path związane z WheelSelectorExtra.

Gęsty blok:
```
38CF4
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

**[STRONG]** Jest to bardzo silny kandydat na blok metod customowego komponentu/compile unitu.

**[CORRECTION]** Nie nazywać `FUN_08038ED0` konstruktorem WheelSelectorExtra bez vptr proof.

Fakt:
```
FUN_0803E5AC
  +0xA5FC -> FUN_08038ED0
  +0xA628 -> FUN_08038ED0
```

Interpretacja „dwa WheelSelectorExtra” = nadal **[HYPOTHESIS]**.

Następny dowód:
```
38CF4
 ↓
this layout / vptr
 ↓
vtable
 ↓
38DF0...390FC
 ↓
pola extraText / metody
```

---

# 6. 480×272 — TWARDY FAKT

Panel:
- szerokość = **480**
- wysokość = **272**
- RGB565.

Jawny startup:
```
FUN_0805fd2a
  -> FUN_0806024c(..., 0x1E0, 0x110, ...)
```
gdzie:
- 0x1E0 = 480,
- 0x110 = 272.

Dodatkowo:
```
FUN_08030358(object, X, Y, W, H)
```
jest rozpoznanym helperem geometrii.

---

# 7. STARTUP / ROOT APPLICATION

Łańcuch:

```
FUN_0805fd78
  ↓
hardware/display init
  ↓
FUN_0805fd2a
  ↓
FUN_0806024c
  ↓
FUN_08061020
  ↓
główny obiekt aplikacyjny
  ↓
FUN_08037CA4 / FUN_08037E9C
  ↓
obiekt modułu +0x12B/+0x12C
```

`FUN_08061020` tworzy główną strukturę oraz moduł przy `+0x2A17`.

`FUN_08037CA4` ustawia vtable-ish pointers i zeruje m.in.:
- +0x129,
- +0x12A,
- +0x12B.

`FUN_08037E9C` ustawia:
- +0x128 = 1,
- +0x12B = 0,
- +0x12C = 1.

To jest fundament dla dalszego parameter/UI engine.

---

# 8. CO1..CO4 — COUNT=4 TO RODZINA INSTANCJI

**[FW] count=4 nie oznacza czterech bajtów parametru.**
Oznacza rodzinę czterech instancji.

Twarde rodziny:
- `0x2032..0x2035` — CH comfort,
- `0x2048..0x204B` — CH eco,
- `0x2064..0x2067` — CH program/mode,
- duże grupy `0x21xx/`, `0x22xx`,
- `0x4001..0x4004`,
- `0x400C..0x400F`,
- nazwy obwodów `0x2321/2325/2329`.

CO2:
- `0x2033`,
- `0x2049`,
- `0x2065` = Tryb CO 2,
- `0x4002`,
- `0x400D`,
- oraz pozostałe rodziny count=4.

Nie wyliczać RAM CO2 bez przejścia przez instancję/record engine.

---

# 9. +0x12B VS +0x12C — NIE MYLIĆ

W obiekcie:
- **+0x12B** = typ/klasyfikacja,
- **+0x12C** = właściwa instancja 1..4.

To jest jedna z najważniejszych korekt całego researchu.

**Nie pisać: +0x12B = numer CO.**

`FUN_0803C064(param_1,param_2)`:
```
class = DAT_0803C218[param_2]
```
Dla klas 1..4:
```
class 1 -> +0x12B=1, +0x12C=1
class 2 -> +0x12B=2, +0x12C=2
class 3 -> +0x12B=3, +0x12C=3
class 4 -> +0x12B=4, +0x12C=4
```

C064 prawdopodobnie wchodzi pośrednio przez vtable/callback; bezpośredniego call-site w decompiled.c nie ma.

Druga niezależna ścieżka:
`FUN_08037D00()` również ustawia +0x12C = 1..4.

---

# 10. NAJWAŻNIEJSZY PARAMETER MAPPER

`FUN_08036FF2(context, panel_index)`:

```
current object
   ↓
+0x12C = instance
   ↓
lookup panel_index in family-of-4 table
   ↓
resolved = base + instance - 1
   ↓
FUN_08037094
   ↓
FUN_080115F6
```

Pierwsza część tabeli to:
**49 rodzin po 4**.

Druga część:
**0x174 = 372 singletony**.

To jest bezpośrednia implementacja count=4 w kodzie, a nie tylko opis CSV.

---

# 11. RECORD ENGINE — TWARDY ŁAŃCUCH

Prawidłowe funkcje:
- `FUN_0801143C` — rejestracja rekordu,
- `FUN_080115F6` — lookup,
- `FUN_0801167A` — odczyt +0x14,
- `FUN_080116E6` — odczyt +0x1C.

Record stride = **0x2C**.

Istotne pola:
- +0x08 = CAN/index,
- +0x0C = source/storage pointer,
- +0x10 = type,
- +0x14 = value/descriptor,
- +0x1C = alternate value,
- +0x24 = metadata.

Odczyt:
```
panel index
 → family-of-4
 → +0x12C
 → resolved index
 → record
 → +0x14 / +0x1C
```

Zapis:
`FUN_08037212()` używa tego samego +0x12C mechanizmu przed `FUN_08011812()`.

**[STRONG]** +0x12C nie jest tylko selektorem UI. Uczestniczy w READ i WRITE.

---

# 12. HEATING UI — WSPÓLNY BUILDER

`FUN_0803E714()`:
- dla klas 1..4 korzysta ze wspólnego buildera,
- dodaje 12 kolejnych ID przez:
`FUN_0803EFDA(param_1, DAT_0803EEC0 + 0x62, 0x0C)`.

Dodatkowe 11 ID są dodawane, gdy:
`+0x158 != 0`.

Dalej:
```
+0x12B / class
 ↓
FUN_0803E714
 ↓
12 / 11 parameter IDs
 ↓
FUN_08036FF2(+0x12C)
 ↓
FUN_0804842C
 ↓
widget record
 ↓
FUN_0804E5BC
 ↓
FUN_08032316 refresh
```

**[STRONG]** CO1..CO4 korzystają ze wspólnego buildera parametrów; nie ma potrzeby zakładać czterech całkowicie niezależnych drzew.

---

# 13. +0x158 — OSOBNY GATE WARIANTU UI

`+0x158` nie jest numerem CO.

`FUN_08037E74(param_1,param_2)`:
- 0 → +0x158 = 0,
- 900 → +0x158 = 1,
- 999 → +0x158 = 2,
- 0x1BF1 → +0x158 = 3.

To jest osobna bramka wariantu/trybu UI.

---

# 14. 0x2105 — KONFIGURACJA HEATING

Panel:
- 0x2105 = Heating configuration,
- u8,
- zakres 0..4,
- default 1,
- RAM 0x20021FAF,
- panel index 0x10F.

`FUN_08031CCC()` pobiera 0x10F przez mapper i przekazuje wartość do:
- `FUN_0802D3E0()`,
- `FUN_0802D91C()`.

**[FW]** 0x2105 realnie steruje UI.

**[NIEUDOWODNIONE]** Nie ma jeszcze twardego mostu:
`0x2105 -> liczba aktywnych obwodów -> tworzenie CO1..CO4`.

Hipoteza, że 0x2105 reprezentuje konfigurację/liczbę aktywnych CO, jest sensowna, ale nadal oznaczona jako [HYPOTHESIS].

---

# 15. WARSTWA HARDWARE / PROFILE

Twarde:
- `0x3500` = Main module type,
- `0x3502` = CH expansion module type,
- `0x350B` = Profile number.

W głównym obiekcie:
- +0x16BF,
- +0x16C0,
- +0x16CC.

Dla Main=0:
- expansion=0: profile 1/2/3 -> wariant 2/3/4,
- expansion=1: profile 1/2/3 -> wariant 5/6/7.

Dodatkowo:
- +0x16C1 wpływa na wybór struktur,
- +0x16D5 jest osobnym warunkiem.

**[STRONG]** Hardware profile i liczba aktywnych CO to dwie różne warstwy.

---

# 16. TOŻSAMOŚĆ KOTŁA / WARIANT / GRAFIKA

Oryginalny FW ma:

### 0x2125 — Device type
- u32,
- RAM 0x20022088,
- default 1000070001,
- snapshot = 1000070001 = 0x3B9BDB71.

### 0x3665 — igneTouch boiler short name
- u32,
- RAM 0x20008D4C,
- snapshot = 0x54450000.

Bajty 54 45 mogą dawać „TE”, ale **nie przypisywać znaczenia bez dodatkowego dowodu**.

### 0x3664 — soft. version
- u16,
- RAM 0x200114E8,
- default = 2213,
- snapshot = 2118.

Nie utożsamiać automatycznie nazwy FW2213TK z bieżącą wartością parametru 0x3664.

### 0x370A — Boiler image selector
- u8,
- zakres 1..3,
- default 1,
- RAM 0x20021FA6,
- rejestracja/callback 0x0801AB7E,
- snapshot raw=259 → **wartość 3**.

To jest twardy parametr nazwany przez firmware **Boiler image selector**.

---

# 17. 370A VS PRAWDZIWE BITMAPY

Wyciągnięte assety z tablicy bitmap:
- 011.png = 105×126,
- 012.png = 108×141,
- 013.png = 82×145,
- 014.png = 54×100.

To są rzeczywiste bitmapy firmware.

**Grafika kotła z wcześniejszego renderu była generowana — nie pochodziła z tych assetów.**

Mamy:
```
FW: 370A = 1..3
ASSETY: 011..014 = 4 grafiki
```

Dlatego **nie wolno zakładać**:
```
1 -> 011
2 -> 012
3 -> 013
```

Możliwe:
1. 370A wybiera klasę/rodzinę,
2. hardware profile wybiera dodatkowy wariant,
3. jedna bitmapa jest fallbackiem,
4. numeracja 011..014 jest mapowaniem wyższego poziomu.

Następny twardy cel:
```
370A / 0x20021FA6
 ↓
read/use
 ↓
switch/lookup
 ↓
Bitmap/resource index
 ↓
BitmapData/Bitmap
 ↓
widget
 ↓
X/Y/W/H
```

---

# 18. HOME / MAIN — CO JEST JUŻ UDOWODNIONE

`FUN_0803E5AC` = silny kandydat dużego Home/Main root.

Tworzy wiele podkomponentów pod stałymi offsetami, m.in.:
- +0x041C → FUN_08047230
- +0x042C → FUN_0800DCD4
- +0x84F4 → FUN_0802E716
- +0x8F70 → FUN_08047244
- +0x92DC → FUN_08047290
- +0x963C → FUN_08047604
- +0xA26C → FUN_08047E54
- +0xA5FC → FUN_08038ED0
- +0xA628 → FUN_08038ED0
- +0xA654 → FUN_0802DF08
- +0xA680 → FUN_0802DF08
- +0xA6AC → FUN_08047FD4
- +0xA6BC → FUN_08047FE8
- +0xA6CC → FUN_08047FFC
- +0xA6DC → FUN_08047FE8.

`FUN_08047290` tworzy **dokładnie 6 powtarzalnych obiektów**, stride 0x40.

**[STRONG]** To daje podstawę do traktowania dolnego paska jako sześciu obiektów, nie jednego obrazka.

Przypisanie tych 6 obiektów do konkretnych ikon/nazw nadal wymaga vtable/resource proof.

---

# 19. HOME — DYNAMICZNE DANE JUŻ ZMAPOWANE

### Modulacja
```
CAN 0x4005
 → panel id 59
 → FUN_0803CF54
 → FUN_080436B4
 → raw 638 = 63.8
```

Komponent pobiera też:
- 0x299F = Burning type,
- 0x2276 = Grate move indicator,
- 0x2007 = Burner state,
- 0x2250 = Flame brightness,
- 0x2119.

### Temperatura zewnętrzna
```
panel id 1 → CAN 0x215F
```

### Tryb / zadana
- id 11 → 0x2002 = Boiler program/mode,
- id 16 → 0x2003 = Boiler set manual temp,
- id 15 → 0x2004 = Boiler set result temp.

Nie utożsamiać „60°C” wyłącznie z 0x2003 w każdym trybie.

### Zasobnik
- id 327 → 0x3740 — nadal nierozwiązana wartość,
- id 328 → 0x3601 — fuel remaining [kg],
- id 330 → 0x3603 — fuel reserve [kg].

Kod:
```
(id327 * 100) / id328
 → FUN_0802DA54
```

**[STRONG]** zasobnik jest dynamicznym komponentem.

---

# 20. GEOMETRIA / KONKRETNE WIDGETY

`FUN_08030358`:
- r1 = X,
- r2 = Y,
- r3 = W,
- stack = H.

CO2:
```
r4+0x8B4
 → TypedText 348
 → "Błąd wygaszania"
 → X=205 Y=195 W=200 H=70

r4+0x8EC
 → TypedText 460
 → "Liczba kotłów slave"
 → X=320 Y=195 W=200 H=70
```

Te współrzędne są rzeczywiste z firmware.

CO2 chain:
```
raw 0x46D2C
 → runtime 0x08056D2C
 → 0x080414BA
 → global 0x20024814
 → +0x12A = 2
 → 0x0805D948
 → 0x080612E0
 → child +0x48
 → geometry 0,0,480,272
```

CO1:
- raw 0x4B618,
- runtime 0x0805B618,
- osobna vtable.

Nie nazywać child +0x48 „Root/Screen” bez vptr/parent proof.

---

# 21. TYPEDTEXT / CO

Potwierdzone zasoby:
- 57 = Ogrzewanie 1,
- 58 = Ogrzewanie 2,
- 99..102 = OGRZEWANIE 1..4,
- 119..122 = Ogrzewanie obwód 1..4.

Dodatkowe:
- 159 = temperatura maksymalna,
- 170 = temperatura CO dla 0°C,
- 171 = temperatura CO dla 10°C,
- 172 = współczynnik korekcji t. CO,
- 179 = stała pompa.

Nie traktować pojedynczego konstruktora/reużywalnego komponentu jako pełnego ekranu.

---

# 22. CO JEST JUŻ „BUILDABLE” W PIERWSZEJ REPLICE

Można już logicznie zbudować:
1. canvas 480×272,
2. sześć osobnych elementów dolnego paska,
3. dynamiczny blok palnika / 63.8,
4. temperaturę zewnętrzną,
5. AUTO/MAN + setpoint,
6. zasobnik / fuel remaining / reserve,
7. visibility związane z 0x3505 / 0x2105,
8. komponenty CO1/CO2,
9. wspólny engine instancji CO1..CO4.

**Nie jest to jeszcze pixel-perfect.**
Brakuje m.in. pełnej geometrii Home, wszystkich bitmap ID, fontów, parent-child, touch callbacków.

---

# 23. CZEGO NIE ROBIĆ PONOWNIE

Nie wracać do:
- wyciągania bitmap od początku,
- ponownego udowadniania 480×272,
- ponownego udowadniania count=4,
- ponownego odkrywania +0x12B/+0x12C,
- 63.8,
- podstawowego 0x2105/0x3505 rozdziału,
- twierdzenia, że +0x12B = numer CO,
- twierdzenia, że +0x158 = numer CO,
- twierdzenia, że 0x2105 na pewno tworzy N obiektów CO,
- twierdzenia, że 370A 1/2/3 = 011/012/013,
- twierdzenia, że FUN_08038ED0 jest konstruktorem WheelSelectorExtra,
- traktowania wcześniejszej wygenerowanej grafiki jako assetu FW.

Wycofane adresy setterów:
- 0x38130,
- 0x3212C,
- 0x32146,
- stary trop 0x42146.
Nie używać ich jako potwierdzonego settera instancji.

Prawidłowe adresy record engine:
- 0x0801143C,
- 0x080115F6,
- 0x0801167A,
- 0x080116E6.

---

# 24. OTWARTE TABELE / BRAKUJĄCE MOSTY

## A. DAT_08037B48 / DAT_08037B4C
Potrzebne:
```
panel index → dokładna grupa 4 → base index
```

## B. DAT_0803C218
108 B:
```
param_2 → class → +0x12B/+0x12C
```
Nie zgadywać bajtów.

## C. DAT_0803EEC0
Potrzebne:
- +0x62 → 12 ID,
- +0x6E → 11 ID.

## D. C064 indirect/vtable
Szukać w:
- 0x08037C00..0x080386xx,
- DAT_08038694,
- DAT_08038698,
- DAT_0803869C.

## E. 370A
Najważniejsze:
```
0x20021FA6 / 370A
 → use
 → selector
 → bitmap
```

## F. WheelSelectorExtra
Najważniejsze:
```
38CF4
 → this/vptr
 → vtable
 → 38DF0..390FC
 → extraText
```

## G. Home root
Najważniejsze:
```
3E5AC
 → 92DC / 47290
 → 6 objects
 → vtable
 → Bitmap/TypedText/geometry
```

## H. 0x2125 / 0x3664 / 0x3665
Szukać:
```
read/use
 → branch/table
 → hardware/UI variant
```

## I. SERIAL
Stringi PASSWORD:/SERIAL:/PIN istnieją, ale:
**brak dowodu, że numer seryjny steruje runtime UI.**
Informację o procesie aktualizacji producenta traktować jako zewnętrzny trop, nie fakt implementacyjny.

---

# 25. NAJLEPSZA KOLEJNOŚĆ DALSZEJ PRACY

### PRIORYTET 1 — 370A → Bitmap
To może dać pierwszy naprawdę dowodowy fragment grafiki.

### PRIORYTET 2 — WheelSelectorExtra vptr
To może odsłonić realną klasę customowego komponentu i jej pola.

### PRIORYTET 3 — Home 6 widgets
`3E5AC → 47290` → vtable → resources → geometry.

### PRIORYTET 4 — 3E714 / widget builder
Rozwinąć:
`480C0 / 4842C / 4E5BC / 32316`.

### PRIORYTET 5 — DAT_0803EEC0 / C218 / 37B4C
Odzyskać surowe tabele.

### PRIORYTET 6 — 2125/3665/3500…
Dopiero po znalezieniu usages ustalić, jak wariant urządzenia wpływa na UI.

### PRIORYTET 7 — SERIAL / updater
Dopiero gdy znajdziemy runtime call-chain.

---

# 26. ZASADY PRACY DLA NOWEGO AGENTA

1. **Nie zaczynaj od zera.**
2. Najpierw przeczytaj ten plik.
3. Potem tylko potrzebne batch notes.
4. Nie raportuj pojedynczego adresu jako „wyniku”.
5. Konsoliduj kilka powiązanych odkryć.
6. Każdy większy wynik zapisuj na GitHub.
7. Używaj:
   - [FW] = bezpośredni dowód z binarki/dekompilacji,
   - [DATA] = tabela/asset/surowe dane,
   - [STRONG] = silny wniosek,
   - [HYPOTHESIS] = hipoteza.
8. Każdą korektę starego wniosku zapisuj jawnie.
9. Nie zastępuj dowodu ogólną wiedzą o TouchGFX.
10. Nie twórz kolejnych mockupów UI bez potrzeby. **Render dopiero wtedy, gdy wykorzystuje rzeczywiste odzyskane assety + geometrię.**
11. Nie pytaj użytkownika ponownie o kontekst, który jest w tym pliku/GitHubie.
12. Nie zatrzymuj się na mikro-wynikach. Szukaj pionowego łańcucha:
```
source trace
 → class/vtable
 → object
 → widget
 → resource
 → geometry
 → visibility
 → callback
 → panel ID
 → instance
 → CAN/storage
```

---

# 27. DOKUMENTY HISTORYCZNE — NIE SĄ RÓWNORZĘDNE Z TYM PLIKIEM

Najważniejsze batch notes:
- `BATCH-SPINE-HOME-HEATING-INSTANCE-WIDGET-2026-11-19.md`
- `BATCH-UI-FRAGMENT-ALREADY-BUILDABLE-2026-11-19.md`
- `BATCH-DUZA-TOZSAMOSC-KOTLA-TOUCHGFX-WARIANT-GRAFIKA-2026-11-19.md`
- `BATCH-WHEELSELECTOR-SOURCE-BOUNDARY-2026-11-19.md`

Starsze:
- `analiza/FW2213TK-2026-11-18/TOUCHGFX-REPLIKA-1-1.md`
- `rejestry/GHIDRA-FW2213TK-PRZEWODNIK.md`
- `rejestry/REJESTRY.md`
- `rejestry/panel-fw-mapa-indeks-id.csv`

Jeżeli stary dokument przeczy temu masterowi, **najpierw zweryfikuj aktualny decompiled.c i nowsze batch notes**.

---

# 28. DEFINICJA „DUŻEGO WYNIKU”

Dobry kolejny commit powinien dostarczyć przynajmniej jeden pełny łańcuch, np.:

```
0x370A
 → funkcja odczytu
 → branch/lookup
 → resource index
 → BitmapData
 → Bitmap
 → widget
 → X/Y/W/H
```

albo:

```
WheelSelectorExtra.cpp
 → vptr
 → vtable
 → metoda
 → pole extraText
 → TypedText/resource
 → widget instance
```

albo:

```
Home root
 → child
 → vtable
 → TypedText/Bitmap
 → geometry
 → visibility
 → panel index
 → CAN
```

Nie wystarczy samo „znalazłem adres X”.

---

# 29. AKTUALNY STATUS W JEDNYM BLOKU

[FW] 480×272 / RGB565.

[FW] TouchGFX + custom source trace `WheelSelectorExtra.cpp`.

[FW] count=4 = rodziny instancji.

[FW] +0x12B = class/type; +0x12C = instance 1..4.

[FW] `FUN_08036FF2` fizycznie realizuje family-of-4 + instance.

[FW] record engine stride 0x2C.

[FW] +0x12C uczestniczy w READ i WRITE.

[FW] Heating builder `FUN_0803E714` używa wspólnej listy 12/11 parametrów.

[FW] Home/Main candidate `FUN_0803E5AC`; `FUN_08047290` tworzy 6 obiektów.

[FW] dynamic Home: 0x4005/63.8, 0x215F outside temp, 0x2002/2003/2004 mode/setpoint, 0x3601/3603 fuel.

[FW] 0x2125 Device type = 0x3B9BDB71.

[FW] 0x3665 boiler short name = 0x54450000.

[FW] 0x3664 soft version = default 2213, snapshot 2118.

[FW] 0x370A Boiler image selector = 3 in snapshot.

[FW] 3500/3502/350B = hardware/profile selection.

[FW] WheelSelectorExtra source path is real firmware string.

[DATA] 011..014 are real extracted bitmap assets.

[STRONG] 370A cannot be naively mapped 1:1 to 011..014.

[STRONG] hardware/profile and functional Heating configuration are separate layers.

[HYPOTHESIS] 0x2105 may encode active heating circuit configuration/count.

[HYPOTHESIS] FUN_08038ED0 may belong to WheelSelectorExtra block, but constructor not proven.

[NIEUDOWODNIONE] serial number is runtime UI selector.

---

# 30. PUNKT STARTOWY DLA NASTĘPNEGO CHATA

**Nie pytaj „co mam analizować?”.**

Od razu:
1. sprawdź `0x370A -> Bitmap`,
2. sprawdź vptr dla `FUN_08038CF4 / 38DF0..390FC`,
3. sprawdź `3E5AC -> 47290 -> 6 widgets`,
4. zapisz duży skonsolidowany wynik,
5. dopiero potem przechodź dalej.

Cel:
**pierwszy pełny, dowodowy widget oryginalnego Home/Heating od C++/firmware aż do assetu, geometrii i źródła danych.**


---

# 31. NOWY WYNIK — CO2 / 0x080612E0 / GRANICA UI ↔ MODEL — 2026-11-19

[FW] Kontynuacja łańcucha:
`CO2 0x08056D2C -> 0x0805D948 -> 0x080612E0`.

[FW] `FUN_080314BA()` nie jest kolejnym konstruktorem UI. Jest wcześniej potwierdzonym accessorem aktywnego obiektu:
`FUN_080314BA() -> *DAT_08031A8C`.

[FW] `FUN_080612E0` wykonuje BL m.in. do:
`0x080393B2, 0x08030354, 0x08030358, 0x08039474, 0x080307BC, 0x080314BA, 0x08027DEC, 0x080313A4, 0x08039424, 0x08031426, 0x0804272C, 0x080347DC, 0x0803A0F8`.

[FW] `0x08030358` = helper geometrii X/Y/W/H, a `this+0x48` dostaje `0,0,480,272`.

[STRONG] `FUN_080313A4(object, typedTextId)` jest setterem/konfiguratorem pola tekstowego: komponent CO1 wywołuje go z `object=r4+0xA4, id=0x39` (TypedText 57 = „Ogrzewanie 1”), a CO2 analogicznie z `id=0x3A` (TypedText 58 = „Ogrzewanie 2”).

[STRONG] Granica UI/model nie przebiega dopiero po `0x080612E0`. Wewnątrz tego łańcucha występują równocześnie:
- konfiguracja child/widgetów i geometria,
- dostęp do aktywnego obiektu modelu przez `FUN_080314BA`,
- pola obiektu `+0x12A/+0x12B/+0x12C`.

Właściwy model:
```
CO2 0x08056D2C
  -> 0x0805D948
      -> 0x080612E0
          -> UI child +0x48 / geometry 0,0,480,272
          -> TypedText/config helpers
          -> FUN_080314BA() -> active model object
          -> dalsze value/visibility helpers
```

[CORRECTION] Nie traktować `FUN_080314BA` jako widgetu ani kolejnego konstruktora. Nie nadawać jeszcze nazw klas TouchGFX funkcjom `0x0804272C/0x080347DC` bez vtable/call-convention proof.

Następny atak:
`0x080612E0 -> 0x080313A4 / 0x0804272C / 0x080347DC -> vptr/child -> value/visibility -> panel index -> FUN_08036FF2 -> CAN`.

Pełny batch:
`analiza/FW2213TK-2026-11-19/BATCH-CO2-612E0-HELPER-BOUNDARY-2026-11-19.md`


---

# 32. NOWY TWARDY SPINE — +0x12C -> dynamic CAN index -> record 0x2C — 2026-11-19

To jest istotne uzupełnienie mastera, którego brakowało w poprzedniej konsolidacji.

## [FW] Dynamiczny lookup instancji jest bezpośrednio odtworzony

W runtime/raw `0x080470C0 / raw 0x370C0` firmware wykonuje:

```
ldrh r0,[r7,#2]      ; base CAN/index z rekordu pomocniczego
ldrb r1,[r6,#1]      ; instance
adds r0,r0,r1
subs r2,r0,#1
uxth r2,r2
BL 0x0802167A
```

Globalny stan pomocniczy jest pod `0x200248D4`; bajt `+1` jest numerem instancji używanym przez lookup.

Wzór jest więc **literalnie**:

```
lookup_index = base_index + instance - 1
```

Przykłady z firmware:

- `0x2032 + 2 - 1 = 0x2033`
- `0x2048 + 2 - 1 = 0x2049`
- `0x2064 + 2 - 1 = 0x2065`
- `0x4001 + 2 - 1 = 0x4002`

## [FW] 0x1167A wybiera rekord po obliczonym indeksie

`0x0802167A` przeszukuje rekordy o rozmiarze `0x2C`. Rejestracja przez `0x0802143C` zapisuje m.in.:

- record+`0x08` = CAN/index,
- record+`0x0C` = źródło wartości,
- record+`0x10` = typ,
- kolejne pola = struktury/metadane.

To oznacza, że brak literalnych rejestracji `0x2033/0x2034/0x2035` nie obala mechanizmu CO2..CO4. Indeks instancji jest tworzony **dopiero w runtime lookup**.

## [STRONG] Pełny fragment ścieżki instancji

```
module +0x12C
       |
       v
global 0x200248D4 + 1
       |
       v
base_index + instance - 1
       |
       v
0x0802167A
       |
       v
record 0x2C
       |
       v
parameter storage / CAN mapping
```

Dla CO:

```
CO base 0x2032 -> instance 1/2/3/4
                 -> 0x2032/2033/2034/2035

CO base 0x2048 -> instance 1/2/3/4
                 -> 0x2048/2049/204A/204B

CO base 0x2064 -> instance 1/2/3/4
                 -> 0x2064/2065/2066/2067
```

To jest mocniejszy dowód niż samo `count=4`: znamy dokładną instrukcję tworzącą indeks instancji.

## [CORRECTION]

Nie próbujemy już znaleźć statycznych `0x2033/34/35` jako osobnych wywołań rejestracji. To był zły poziom poszukiwania.

Nadal NIE wiemy:
- gdzie dokładnie powstają rekordy dla instancji 2..4,
- jaki RAM jest przypisany do CO2/CO3/CO4,
- skąd dokładnie przychodzi pierwszy zapis do `module+0x12C).

Ale wiemy już bezpośrednio, jak `+0x12C` kończy się na konkretnym indeksie CAN.

## [FW] Znaczenie dla dalszego reverse engineeringu

Dalszy trace można teraz podzielić na dwa niezależne problemy:

**A — źródło instancji**
`C064 / D00 / inne źródło -> +0x12B/+0x12C`

**B — konsumpcja instancji**
`+0x12C -> 0x200248D4+1 -> base+instance-1 -> 0x1167A -> record`

Problem B jest już zamknięty na poziomie mechanizmu.

Następny atak koncentrujemy więc wyłącznie na problemie A oraz na Home/UI:
`0x0803E5AC -> 0x08047290` i `CO component -> parent/add -> widget`.

Pełny batch źródłowy:
`analiza/FW2213TK-2026-11-19/1167A-CO-INSTANCE-LOOKUP.md`


# 33. HOME/MAIN ROOT + GRAFIKA KOTŁA — NOWY TWARDY SPINE — 2026-11-19

Po powrocie do surowego `decompiled.c` zamknięto ważną korektę architektury Home/Main. `FUN_0803E5AC` rzeczywiście składa duży root i bezpośrednio tworzy kluczowe podkomponenty:

```
+0x23DC -> FUN_08047244
+0x24B7 -> FUN_08047290
+0x258F -> FUN_08047604
+0x289B -> FUN_08047E54
+0x297F -> FUN_08038ED0
+0x298A -> FUN_08038ED0
```

### 33.1 47290 — korekta „6 widgetów”
`FUN_08047290` nie jest sześcioma konstruktorami widgetów. Tworzy/organizuje dwa bloki po 6 elementów i w pętli stride `0x40` wiąże sześć slotów ze wspólnymi obiektami pod `+0x20/+0x24`. To jest sześcioslotowy komponent/rekord, nie sześć niezależnych klas.

### 33.2 47604 — duży komponent Home/Main
`FUN_08047604` tworzy m.in. cztery obiekty pod `+0x1D7`, stride `0x54`. Każdy dostaje przez vtable geometrię:
- X/Y z pól rodzica,
- W = `0x1E0 = 480`,
- H = `200`,
po czym jest dołączany przez `FUN_08030380`. Nie ma jeszcze dowodu, że są to cztery bitmapy kotłów; nie zgadujemy.

### 33.3 38ED0
`FUN_08038ED0` jest krótkim konstruktorem z vptr `DAT_08038EE4` i zerowaniem pola +0x28. W Home/Main występuje trzy razy. Bez vptr proof nie utożsamiać go automatycznie z WheelSelectorExtra.

### 33.4 Kierunek grafiki kotła
Twarde końce nadal są dwa:
- FW `0x370A` = **Boiler image selector**, 1..3, RAM `0x20021FA6`, snapshot = 3;
- prawdziwe bitmapy firmware: `011.png` 105x126, `012.png` 108x141, `013.png` 82x145, `014.png` 54x100.

Nie ma jeszcze dowodu mapowania `370A=1/2/3 -> 011..014`. Następny atak ma znaleźć rzeczywisty call-site Bitmap/BitmapData zależny od wariantu i dopiero wtedy spiąć selector -> bitmap -> widget -> geometria Home.

Pełny batch: `analiza/FW2213TK-2026-11-19/BATCH-HOME-ROOT-BOILER-GRAPHICS-SPINE-2026-11-19.md`.


# 34. KOREKTA GEOMETRII HOME — 480x200 = CONTENT AREA, NIE GRAFIKA KOTŁA — 2026-11-19

Użytkownik zweryfikował geometrię na realnych screenshotach Home. Ekran firmware ma `480x272`; screenshot pełnego ekranu zachowuje proporcję ~480:272. Drugi screenshot jest praktycznie dokładnie wycinkiem/projekcją obszaru `480x200`. Pozostałe ~72 px odpowiadają dolnemu paskowi nawigacyjnemu.

Wniosek: `FUN_08047604` i jego cztery obiekty `+0x1D7` nie należy interpretować jako „grafika kotła”. Ich `480x200` odpowiada całemu obszarowi content/Home, w którym siedzi wiele niezależnych elementów UI.

Co więcej, kod pokazuje dla 4 instancji:
- W = `0x1E0 = 480`, H = `0xC8 = 200`;
- X kolejno: baza, baza+`0x140` (320), baza+`0x280` (640), baza+`0x3C0` (960);
- Y = baza;
- stride obiektu = `0x54`.

To oznacza cztery instancje tego samego typu obiektu ustawione względem siebie co 320 px, przy szerokości 480 px. Nie są to cztery „kotły”. Są to raczej cztery pełne warstwy/panele/strony/obszary tego samego komponentu, potencjalnie przesuwane lub zarządzane jako zestaw. Kod dodatkowo wywołuje `FUN_0804E218(piVar8,param_1+0x22b)`, co wzmacnia hipotezę o związaniu tych obiektów z mechanizmem nadrzędnym/pozycjonowaniem.

Dlatego następny krok dla grafiki kotła musi zejść **wewnątrz obiektu z `+0x1D7` / jego vptr `DAT_08047E34` oraz do funkcji obsługujących jego dzieci**, zamiast utożsamiać jego prostokąt z bitmapą.

Geometria użytkownika jest zgodna z firmware i bardzo cenna: `480x200` to praktycznie dokładnie **główna powierzchnia Home nad paskiem 72 px**. To jest właściwy „canvas” do rozpisania wszystkich widgetów.

# 35. HOME — 7 DOLNYCH STREF + ZŁOŻONY GÓRNY CONTENT — 2026-11-19

Najmocniejsza korelacja screenshot ↔ kod do tej pory: dolny pasek widoczny jako 7 stref odpowiada strukturze 1 + 6.

- FUN_08047244 tworzy osobny komponent z childem +0x18, vptr DAT_0804728c, pozycja X=50, Y=55.
- FUN_08047290 tworzy dokładnie 6 slotów: elementy +0x2A stride 0x40 count 6 oraz teksty +0x8A stride 0x34 count 6.
- FUN_08047334 pokazuje, że każdy slot ma własny element wizualny, TypedText, geometrię, kolor i kolejne dzieci.

To daje bardzo mocny model dolnego paska: 47244 + 47290[6] = 7 wizualnych stref. Każda strefa jest sama w sobie kompozytem widgetów, co zgadza się z obserwacją użytkownika.

Górny obszar jest osobnym dużym kompozytem FUN_08047604. Konstruktor ma wiele childów, grupę 5 elementów stride 0xE4, grupę 5 tekstów stride 0x0C, cztery duże obiekty stride 0x54 o geometrii 480x200 oraz dodatkowe obiekty. Zatem 480x200 jest obszarem content, a nie grafiką kotła.

Pełny batch: BATCH-HOME-SCREEN-ZONES-7x-BOTTOM-UPPER-WIDGET-TREE-2026-11-19.md.


# 36. KOREKTA — 47290 NIE JEST DOLNYM PASKIEM — 2026-11-19

Ponowna analiza pełnego `FUN_08047334` wykazała, że sześć slotów `FUN_08047290` jest ustawianych **pionowo**. Dla 6 pozycji wartości Y wynikają z kodu jako około `50,84,118,152,186,220` px. To wyklucza wcześniejszą interpretację `47244 + 47290[6] = 7 poziomych stref dolnego paska 480x72`.

Wcześniejszy zapis tej korelacji zostaje anulowany. `47290` jest obecnie klasyfikowane jako **sześciopozycyjna lista/menu/selektor**, bez przypisania do konkretnego ekranu.

Również `47604` zostało rozstrzygnięte jako komponent wykresowy: 5 serii/punktów, normalizacja X/Y, `FUN_08047C1A`, oraz cztery przesuwane obszary 480x200. Nie jest to grafika kotła ani dolny pasek.

Nowy ciekawy komponent to `47E54 -> 2DF80`. `2DF80` tworzy wieloelementowy kompozyt małych elementów rozmieszczonych w dwóch rzędach, a `47E54` ustawia dodatkowo TypedText `0x1D4=468` przy X=135, Y=60, W=200. Semantyka tego komponentu pozostaje otwarta.

Pełny batch korekty: `BATCH-HOME-47290-ROLE-CORRECTION-2026-11-19.md`.


# 37. TWARDY KANDYDAT GRAFIKI KOTŁA — FUN_080469E8 -> BITMAP 14 — 2026-11-19

W firmware znaleziono komponent `FUN_080469E8`, który w konstruktorze jawnie wykonuje `FUN_080307bc(..., 0x0E)`. Z tabeli zasobów `DOKUMENTACJA/bitmap_sizes.tsv` wynika `014.png = 54x100`.

Ten sam komponent buduje lokalny kompozyt około 70 px szerokości z bitmapą 54x100 oraz czterema elementami TypedText:
- ID 493, X=0, Y=130, W=70, H=70,
- ID 493, X=25, Y=40, W=50, H=45,
- ID 494, X=0, Y=50, W=50, H=70,
- ID 493, X=30, Y=100, W=100, H=45.

Bitmapa jest ustawiana na Y=20, a X jest wyliczane z szerokości 70 i wymiaru zasobu. Na końcu komponent wiąże się z aktywnym modelem przez `FUN_080314BA -> FUN_080318B4`.

`FUN_0803E34C` tworzy cztery identyczne instancje `FUN_080469E8` w stride `0x19C` bajta. Nie jest jeszcze dowiedzione, że `FUN_0803E34C` jest bezpośrednim rodzicem Home/Main ani że wszystkie cztery są widoczne równocześnie.

To jest obecnie **najmocniejszy znaleziony kandydat na rzeczywisty widget grafiki kotła**: geometria kompozytu i bitmapa 54x100 bardzo dobrze odpowiadają screenshotowi użytkownika.

Nadal otwarte jest kluczowe połączenie:
`0x370A (Boiler image selector, 1..3) -> aktualizacja Bitmap ID -> 011/012/013/014`.
Konstruktor `469E8` ustawia ID 14 statycznie, więc trzeba znaleźć metodę aktualizującą child `+0x4F` po zmianie modelu.

Pełny batch: `BATCH-HOME-BOILER-WIDGET-469E8-2026-11-19.md`.


# 38. 469E8 — WRITER BITMAP ID ZAMKNIĘTY, 370A NADAL OTWARTE — 2026-11-19

[FW] Surowy decompiled.c zamyka rolę FUN_080307BC: zapisuje Bitmap/resource ID bezpośrednio do pola child +0x26, a następnie przez vtable +0x38/+0x3C pobiera/ustawia zależne wymiary zasobu.

[FW] W FUN_080469E8 child grafiki znajduje się pod +0x4F. Konstruktor wykonuje:
- child +0x4F,
- FUN_080307BC(..., 0x0E),
- pozycjonowanie przez vtable +0x2C/+0x30,
- Y = 20,
- attach przez FUN_08030380.

[FW] Finalny vptr komponentu 469E8 = DAT_08046CC4.

[FW] Parent 469E8 ma literalne W=70, H=150. Bitmap ID=14, asset 014.png=54x100.

[FW] FUN_0803E34C tworzy cztery instancje 469E8 pod +0x251, +0x2B8, +0x31F i +0x386, ze stride 0x19C bajta.

[FW] Ważny wynik negatywny: w całym eksportowanym decompiled.c nie znaleziono bezpośredniego, statycznego wywołania FUN_080307BC na tych czterech adresach poza konstruktorem FUN_0803E34C. Nie dowodzi to braku zmiany bitmapy, bo nadal możliwa jest ścieżka pośrednia/vtable/parent traversal.

[CORRECTION] Nie szukamy już ogólnie „writera Bitmap ID”. Writer jest zamknięty: FUN_080307BC -> child+0x26. Szukamy teraz call-site, który podaje do tego writera zmienny resource ID.

[STRONG] Nowy najlepszy atak:
DAT_08046CC4 -> vtable/metody klasy 469E8 -> parent/model binding -> ewentualny pośredni wybór Bitmap ID.

Równolegle obiekt +0x213 z FUN_080469D4 ma vptr DAT_080469E4 i przechowuje parent + callback/object metadata; to jest obecnie mocny kandydat na most między czterema instancjami wizualnymi a modelem.

[STRONG] Nadal NIE zamykamy 370A -> 11/12/13/14. Fakty pozostają rozdzielone:
370A = Boiler image selector, 1..3, RAM 0x20021FA6, snapshot=3;
469E8 = Bitmap ID 14 -> 014.png 54x100.

Pełny batch: BATCH-469E8-BITMAP-WRITER-VTABLE-TRACE-2026-11-19.md.


# 39. 370A CALLBACK BOUNDARY — NOWY WYNIK MULTIPASS — 2026-11-19

[FW] Sąsiednie wpisy tabeli: 3709→0x0801425C, 370A→0x0801AB7E, 370B→0x08015CCC, 370C→0x0801659E, 370D→0x08016614. Callback fields nie muszą wskazywać początku nazwanej funkcji.

[FW] 0x0801425C leży wewnątrz FUN_0801417C (do ok. 0x080143DE); 0x0801659E i 0x08016614 leżą wewnątrz FUN_080164F4 (0x080164F4..0x080166B8); 0x08015CCC nie jest początkiem nazwanej funkcji. To jest twardy dowód, że pole callback/code może wskazywać wewnętrzny punkt większego bloku.

[STRONG] 0x0801AB7E pozostaje nierozpoznanym wejściem pomiędzy FUN_08019462 a FUN_0802BDF0. Nie wolno nazywać go zwykłą funkcją. Trzeba odzyskać dispatcher/branch/continuation z raw BIN albo przez porównanie sąsiednich callbacków.

Nowy model: parameter engine → callback/code 0x0801AB7E → dispatcher/internal entry → use/write RAM 0x20021FA6 → model notification → Home/469E8.

# 40. 469E8 — REJESTRACJA ≠ UPDATE — 2026-11-19

[FW] FUN_080469E8 ustawia vptr DAT_08046CC4, tworzy Bitmap child +0x4F, zapisuje ID 14 przez FUN_080307BC, pobiera active module przez FUN_080314BA i rejestruje obiekt przez FUN_080318B4.

[FW] FUN_080318B4 jest registry timer/update, nie bindingiem parametru. FUN_080317AE później dispatchuje zarejestrowany obiekt przez vtable slot +0x50.

Aktualny brak: DAT_08046CC4 + 0x50 → konkretny update method → model read/370A? → child +0x4F/resource ID.

# 41. DWIE NIEZALEŻNE GRANICE

Gałąź A:
370A → RAM 0x20021FA6 → callback 0x0801AB7E → UNKNOWN DISPATCH.

Gałąź B:
active module → FUN_080318B4 → FUN_080317AE → DAT_08046CC4+0x50 → UNKNOWN UPDATE → 469E8 child +0x4F → Bitmap/resource.

Bez dowodu nie łączyć ich bezpośrednio.

# 42. PRIORYTET NASTĘPNEGO PRZEBIEGU

1. Porównać callbacki 3709..370D i ich dokładne wejścia/wyjścia.
2. Odzyskać raw boundary 0x0801AB7E.
3. Odzyskać DAT_08046CC4 + 0x50.
4. Prześledzić update 469E8.
5. Znaleźć zmienny Bitmap ID.
6. Dopiero wtedy zamknąć 370A→011/012/013/014.

# 43. STATUS

[FW] 370A = Boiler image selector, u8 1..3, RAM 0x20021FA6, snapshot raw 259→3, callback 0x0801AB7E.
[FW] 469E8 = Bitmap ID 14 / asset 014.png 54x100.
[FW] Bitmap writer = FUN_080307BC → child +0x26.
[FW] 469E8 registration = FUN_080318B4; real runtime dispatch = FUN_080317AE → vtable +0x50.
[STRONG] 370A→469E8 nadal niezamknięte.

# 44. PUNKT STARTOWY NOWEGO AGENTA

Nie zaczynaj od bitmap, CO1..CO4 ani ogólnego Home. Zacznij od §39–44 tego mastera, następnie wykonaj: callback comparison 3709..370D → 0x0801AB7E → DAT_08046CC4+0x50 → 469E8 update → variable Bitmap ID → 370A mapping.

Jeżeli raw BIN nie jest dostępny, nie udawaj rekonstrukcji bajtów z decompiled.c. Kontynuuj drugi tor vtable/update i dokładnie oznacz brakujący raw region.


# 45. MULTIPASS — CALLBACK ENGINE + 469E8 RUNTIME DISPATCH — 2026-11-19

Nowy batch: `BATCH-CALLBACK-ENGINE-317AE-469E8-VTABLE-2026-11-19.md`.

[FW] Pełny eksport `decompiled.c` został ponownie odzyskany z blob SHA `9620d0c85259d34bb6a20d3b03b038945dfe4c1a`. Repo nadal nie zawiera surowego BIN, więc nie rekonstruujemy bajtów 0x0801AB7E ani vtable z domysłów.

## 45.1 317AE — zamknięta semantyka

`FUN_080317AE`:
- registry count = object +0x64,
- object pointers = +0x04 + index*4,
- active/reference bytes = +0x68 + index,
- dla aktywnego wpisu wywołuje registered_object->vtable +0x50,
- dopiero później usuwa wpisy nieaktywne.

Zatem:

`318B4 = register/retain`  
`3193A = release/unregister`  
`317AE = runtime/tick traversal → vtable +0x50`.

[STRONG] +0x50 jest rzeczywistą granicą metody runtime, nie hipotezą o "update gdzieś dalej".

## 45.2 469E8 — dokładny obiekt rejestrowany

`FUN_080469E8`:
- finalny vptr = DAT_08046CC4,
- Bitmap child = +0x4F,
- konstruktor zapisuje resource ID 14,
- pozycjonuje Bitmap,
- tworzy 4 dzieci tekstowe,
- rejestruje **parent 469E8**, a nie Bitmap child, przez `FUN_080318B4`.

Brakująca krawędź jest więc dokładnie:

`DAT_08046CC4 + 0x50 → concrete 469E8 runtime method`.

## 45.3 Dynamiczny Bitmap pattern odzyskany gdzie indziej

`FUN_08030762` pokazuje istniejący w firmware wzorzec:

`unregister Bitmap → wybór ID z pól obiektu → FUN_080307BC(variable ID) → Bitmap vtable +0x14`.

To nie jest jeszcze dowód dla 469E8, ale jest teraz najlepszym wzorcem porównawczym dla jego nieznanej metody.

## 45.4 Callback field — korekta nazewnictwa

Zweryfikowane zakresy:
- 3709 → 0x0801425C = FUN_0801417C +0xE0,
- 370A → 0x0801AB7E = brak nazwanej funkcji,
- 370B → 0x08015CCC = brak nazwanej funkcji,
- 370C → 0x0801659E = FUN_080164F4 +0xAA,
- 370D → 0x08016614 = FUN_080164F4 +0x120.

[STRONG] Pole tabeli nie może być obecnie nazywane zwykłym "callback function pointer". Konserwatywna nazwa: **handler/code boundary**.

Szczególnie ważne:
- FUN_0801417C jest builderem/tabelą nazw modeli kotłów,
- FUN_080164F4 jest realną funkcją stanu/logiki,
- 0x08015CCC i 0x0801AB7E leżą poza nazwanymi funkcjami.

To oznacza, że dopiero raw dispatch może powiedzieć, jak te adresy są konsumowane.

## 45.5 Aktualny graf architektury

```
PARAMETER TABLE
   |
   +-- 370A
   |    +-- RAM 0x20021FA6
   |    +-- handler/code boundary 0x0801AB7E
   |             |
   |             +-- UNKNOWN parameter dispatch
   |
   +-- neighboring handler boundaries 3709/370B/370C/370D

ACTIVE MODULE
   |
   +-- FUN_080318B4
   |      |
   |      +-- timer/update registry
   |
   +-- FUN_080317AE
          |
          +-- registered_object.vtable +0x50
                  |
                  +-- 469E8 concrete runtime method [OPEN]
                          |
                          +-- child +0x4F [KNOWN]
                          |
                          +-- Bitmap ID 14 at construction [KNOWN]
                          |
                          +-- dynamic ID/update [OPEN]
```

## 45.6 Następny przebieg

Priorytet A:
`DAT_08046CC4 + 0x50` → concrete method → model/state read → child/resource.

Priorytet B:
raw `0x0801AB7E` → dispatcher → read/write/notification of `0x20021FA6`.

Priorytet C:
porównanie 469E8 z istniejącym dynamicznym Bitmap patternem `FUN_08030762`.

Dopiero po A/B/C:
`370A → resource ID → 011/012/013/014`.



# 46. MULTIPASS — PARAMETER RECORD ENGINE ≠ 370A CODE TABLE — 2026-11-19

Nowy istotny rozdział po zejściu do `FUN_0801143C / 115F6 / 1167A / 11812`.

[FW] `FUN_0801143C` rejestruje runtime record o stride `0x2C`:
- +0x08 = panel/CAN index,
- +0x0C = source/storage pointer,
- +0x10 = type,
- +0x14 = value/descriptor,
- +0x1C = second value/limit,
- +0x24 = third descriptor,
- +0x2C = access/flag byte,
- +0x30 = metadata.

[FW] `FUN_080115F6`, `FUN_0801167A`, `FUN_080116E6` wyszukują rekord po indeksie i odczytują odpowiednio descriptor/value/alternate value.

[FW] `FUN_08011812` wykonuje typowanie, zakresy i zapis do storage wskazanego przez record +0x0C.

[STRONG] To jest runtime **record engine**, a nie miejsce przechowywania adresu 0x0801AB7E.

Wniosek architektoniczny:

```
PARAMETER CONFIG / PANEL TABLE
   |
   +-- ID 370A
   +-- RAM 0x20021FA6
   +-- code/handler boundary 0x0801AB7E
   |
   +--------------------+
                        |
                        v
                 parameter engine
                        |
                        v
               runtime record 0x2C
                        |
                        +-- storage/CAN/value
```

Nie wolno więc szukać `0x0801AB7E` jako pola w rekordzie `FUN_0801143C`.

To zawęża dalszy atak: trzeba odzyskać **osobną konfigurację parametru** oraz kod, który interpretuje jej code/handler field, a nie próbować wciskać 370A do record stride 0x2C.

[OPEN] Dokładny layout konfiguracji parametrów i dispatcher consuming `0x0801AB7E` nadal wymaga raw/data-region recovery.



# 47. RAW BIN RECOVERY — 469E8/47040/370A MAJOR CORRECTION — 2026-11-19

Raw firmware is now available and verified:
- file: `FW2213TK_kopia.bin`
- size: `0x1F0000` = 2,031,616 bytes
- SHA-256: `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`
- vector table: SP `0x20013F28`, reset `0x080A3209`
- flat mapping `raw = address - 0x08000000` is confirmed.

## 47.1 370A / 0x0801AB7E — HARD CORRECTION

Raw offset `0x1AB7E` is data/resource, not executable Thumb code. The bytes are repeated pixel/table-like values. Therefore the field `370A -> 0x0801AB7E` must NOT be called a direct function pointer.

Neighboring fields are heterogeneous:
- 3709 -> `0x0801425C`: executable code inside a larger block,
- 370A -> `0x0801AB7E`: raw data/resource region,
- 370B -> `0x08015CCC`: data/table region,
- 370C -> `0x0801659E`: executable code inside `FUN_080164F4`,
- 370D -> `0x08016614`: executable code inside the same routine.

Conservative term: **handler/code/data boundary**, not uniform callback pointer.

## 47.2 DAT_08046CC4 — HARD CORRECTION

Raw `FUN_080469E8` loads:
- `DAT_08046CC0 = 0x0807C660`
- `DAT_08046CC4 = 0x08079F00`

Both addresses point into UTF-16 localization strings. `0x08079F00` begins with text equivalent to `"žeistas kambario daviklis 2"`.

Therefore the previous statement "DAT_08046CC4 = vtable" is invalidated.

The raw BIN proves:
- 469E8 is a real composite visual widget,
- it creates Bitmap child +0x4F,
- it writes Bitmap/resource ID 14,
- it creates multiple text children,
- it registers itself,
but its first word is not a persistent vtable pointer as previously assumed.

## 47.3 317AE +0x50 remains real

Raw `FUN_080317AE` proves the runtime traversal:
`registered_object -> *(object+0) -> *(vtable+0x50) -> BLX`.

Thus +0x50 is a real indirect dispatch boundary.

The unresolved contradiction is now explicit: a registered 469E8 object finishes with a text/resource pointer at +0 while 317AE expects a dispatch table there. The next pass must find where/when the runtime object representation changes, or prove that 469E8 registration participates in a different registry state than assumed.

## 47.4 NEW — FUN_08047040 is a concrete 1..3 visual selector

Raw code at `0x08047040` directly controls four repeated 469E8-instance-local bytes:

```
parent+0x969 = instance(+0x944)+0x25
parent+0xB05 = instance(+0xAE0 )+0x25
parent+0xCA1 = instance(+0xC7C )+0x25
parent+0xE3D = instance(+0xE18 )+0x25
```

For enable != 0:
- selector 1 -> +0xB05 = 1
- selector 2 -> +0xB05 = 1, +0xCA1 = 1
- selector 3 -> +0xB05 = 1, +0xCA1 = 1, +0xE3D = 1
- +0x969 always receives enable.

For enable == 0 all four state bytes are cleared.

This is the first raw-proof 1..3 selector path touching the four repeated 469E8 instances.

## 47.5 NEW — FUN_0803E45C supplies the selector

There is one direct raw call to `FUN_08047040`, from `FUN_0803E45C`.

Immediately before the call:
- model index `0x158` is converted to u8 and passed as selector,
- model index `0x11C` is converted to u8 and passed as enable.

Therefore:

```
model[0x158], model[0x11C]
        ↓
FUN_08047040
        ↓
four repeated 469E8 instance state bytes
```

Do NOT yet rename `model[0x158]` as 370A. The bridge remains open.

## 47.6 New architecture

```
370A
  ├─ RAM 0x20021FA6
  └─ table field 0x0801AB7E
       └─ data/descriptor/dispatcher boundary [OPEN]

MODEL / HOME UPDATE
  └─ FUN_0803E45C
       ├─ model[0x158]
       ├─ model[0x11C]
       └─ FUN_08047040
            ├─ parent+0x969
            ├─ parent+0xB05
            ├─ parent+0xCA1
            └─ parent+0xE3D

469E8
  ├─ child +0x4F
  ├─ Bitmap ID 14 at construction
  ├─ text children
  └─ registration via FUN_080318B4
```

## 47.7 Next attack

1. Resolve the runtime object representation contradiction around 469E8 +0 and 317AE.
2. Identify semantics of model indices `0x158` and `0x11C`.
3. Search raw code/data for the bridge between RAM `0x20021FA6` and model `0x158`.
4. Trace state bytes +0x25 to actual visibility/update behavior.
5. Only then map 370A to resource IDs.
6. Keep 011/012/013/014 mapping OPEN.

Full raw pass: `BATCH-RAW-BIN-RECOVERY-469E8-47040-370A-CORRECTION-2026-11-19.md`.



# 48. RAW CORRECTION — INTERNAL 0x121 = 0x370A; 0x158/0x11C = CASCADE — 2026-11-19

The raw mapping table around `0x08037984` proves:
`0x121 -> 0x370A`.

This is the internal-index representation of the external Boiler image selector.

The same raw table proves:
- `0x158 -> 0x351A` = Cascade slaves number, 1..3
- `0x11C -> 0x350C` = Is this device cascade master, 0..1.

Therefore the previously recovered path:
`FUN_0803E45C -> 0x158/0x11C -> FUN_08047040`
is a **cascade UI path**, not the 370A path. It must be kept separate.

## 48.1 47040 semantic closure

`FUN_08047040` is a cascade selector:
- selector 1/2/3 controls how many of four repeated components receive state byte +0x25,
- enable is the cascade-master flag.

This explains the 1..3 selector without invoking 370A.

## 48.2 469E8 raw bitmap-child correction

Raw `FUN_080469E8` sets resource ID 14 by calling `FUN_080307BC` with object:
`parent + 0x13C`.

Therefore:
- resource ID 14 remains hard fact,
- bitmap child = parent +0x13C,
- old `+0x4F` attribution is withdrawn.

## 48.3 370A raw data boundary

`0x0801AB7E` is raw data/table, not Thumb code.

The heterogeneous neighboring parameter fields now strongly support a generic handler/conversion/metadata field:
- 3709 code,
- 370A data,
- 370B data,
- 370C code,
- 370D code.

## 48.4 370A RAM reference

No direct literal occurrence of absolute `0x20021FA6` was found in raw code, nor a MOVW/MOVT construction of that address. The storage is therefore likely reached through the generic parameter/configuration object rather than direct absolute access.

## 48.5 Revised graph

```
external 0x370A
      ↓
internal index 0x121
      ↓
generic parameter engine [OPEN]
      ├── storage 0x20021FA6 [KNOWN]
      └── data handler 0x0801AB7E [KNOWN DATA]

SEPARATE:
0x351A / 0x350C
      ↓
FUN_0803E45C
      ↓
FUN_08047040
      ↓
four 469E8 composites
      ↓
Bitmap ID 14 at child +0x13C
```

The 370A -> Bitmap 011/012/013/014 mapping remains OPEN.


# 49. RAW MULTIPASS — 0x121 → 0x370A → 0x20021FA6 → VARIABLE BITMAP 11..13 — 2026-11-19

This section **supersedes the remaining OPEN parts of §48 concerning the 370A runtime path**.

## 49.1 Internal 0x121 is definitively 0x370A

Raw mapping table around 0x08037934 is a sequence of 16-bit internal/external parameter pairs.

Exact entry:
- 0x08037984 = 0x0121
- 0x08037986 = 0x370A

[FW] Therefore internal model index 0x121 is the runtime representation of external Boiler image selector 0x370A.

The same table independently proves:
- 0x158 -> 0x351A = Cascade slaves number,
- 0x11C -> 0x350C = Cascade master flag.

Therefore 0x158/0x11C remains a separate cascade branch.

## 49.2 FUN_08036FF2 is the generic resolver

FUN_08036FF2:
1. reads the current object's +0x12C instance;
2. searches the internal-index mapping table;
3. resolves 0x121 to external 0x370A;
4. combines the mapped ID with the instance component;
5. passes the resolved external ID to FUN_08037094.

[FW] This closes the internal-index -> external-parameter namespace boundary.

## 49.3 FUN_08037094 -> FUN_080115F6 -> runtime record

FUN_08037094 passes the resolved external ID to FUN_080115F6.

FUN_080115F6 searches runtime records with stride 0x2C. The relevant fields are:
- +0x08 = external/CAN index,
- +0x0C = backing storage pointer,
- +0x10 = type.

The lookup then dereferences record +0x0C to obtain the current value.

FUN_08014734 extracts the value according to type. For the 370A u8 parameter, the resulting value is consumed as a byte.

[FW] This proves that 370A reaches its backing RAM through the generic record engine.

## 49.4 370A registration closes the RAM address

The raw registration sequence for 370A contains:

movw r0,#0x16BA
adds r2,r4,r0
movw r1,#0x370A
...
BL FUN_0801143C

Inside FUN_0801143C:
- record +0x08 receives the external ID,
- record +0x0C receives r2,
- record +0x10 receives the type.

The relevant configuration base is the literal 0x200208EC.

Therefore:

0x200208EC + 0x16BA = 0x20021FA6

[FW] The exact storage chain is now:

0x121 -> 0x370A -> runtime record -> 0x20021FA6 -> u8 value.

No direct MOVW/MOVT reference to 0x20021FA6 is necessary.

## 49.5 0x0801AB7E is no longer part of the 370A runtime chain

Raw bytes at 0x0801AB7E are pixel/table-like data, not executable Thumb code.

More importantly, the complete runtime path above reaches 0x20021FA6 through the record engine without using 0x0801AB7E.

[CORRECTION] The previous interpretation of 0x0801AB7E as a 370A callback/handler is withdrawn.

Do not:
- treat 0x0801AB7E as a normal function,
- put it into the 0x2C runtime record,
- use it as the 370A -> UI bridge.

Its independent data/resource provenance remains OPEN.

## 49.6 UI directly requests internal 0x121

FUN_0803CB04 contains the exact call sequence:

ldr r0,[r4,#0x8]
movw r1,#0x121
BL FUN_08036FF2
UXTB r1,r0
ldr r0,[r4,#0xC]
BL FUN_0803CACC

[FW] The visual component therefore reads the Boiler image selector through the same generic 0x121 resolver.

## 49.7 FUN_0803CACC closes the variable Bitmap/resource selection

Raw FUN_0803CACC:

adds r1,#0xA
strh r1,[sp]
addw r0,r0,#0x85C
mov r1,sp
BL FUN_080307BC

Therefore:
- resource ID = 370A value + 10,
- target Bitmap object = UI parent +0x85C,
- FUN_080307BC writes the resource ID.

This is direct executable proof.

## 49.8 Exact 370A -> resource mapping is now CLOSED

370A metadata:
- u8,
- range 1..3,
- name: Boiler image selector.

Code:
resource_id = value + 10.

Therefore:

| 370A value | resource ID |
|---:|---:|
| 1 | 11 |
| 2 | 12 |
| 3 | 13 |

[FW] The earlier suspected mapping 1->011, 2->012, 3->013 is now proven by executable code, not inferred from filenames.

Resource 14 remains separate: FUN_080469E8 independently constructs a Bitmap with fixed ID 14. Do not merge that branch with 370A.

## 49.9 New complete architecture

Boiler image path:

0x370A
  -> internal 0x121
  -> FUN_08036FF2
  -> mapping table
  -> FUN_08037094
  -> FUN_080115F6
  -> record +0x0C
  -> 0x20021FA6
  -> u8 value 1..3
  -> FUN_0803CB04
  -> FUN_0803CACC
  -> +10
  -> FUN_080307BC
  -> Bitmap object +0x85C
  -> resource 11..13

Separate cascade path:

0x351A / 0x350C
  -> FUN_0803E45C
  -> FUN_08047040
  -> four 469E8 composites
  -> fixed resource 14

## 49.10 Next attack

The 370A value-to-resource bridge is closed. Do not spend another pass proving it.

Next:
1. identify the exact C++ class/vtable behind FUN_0803CB04;
2. recover constructor/parent path for Bitmap object +0x85C;
3. recover direct BitmapData/resource-table proof for resource IDs 11, 12, 13 and match them to 011/012/013;
4. recover X/Y/W/H and visibility for +0x85C;
5. determine the independent role of resource 14;
6. resolve 0x0801AB7E only as a separate data/resource question.

Full batch:
BATCH-RAW-MULTIPASS-121-370A-UI-BITMAP-2026-11-19.md


# 50. SECOND RAW PASS — 370A TARGET +0x85C IS A REAL BITMAP CHILD — 2026-11-19

Further raw analysis closes the widget side left open in §49.

## 50.1 FUN_0803C33E constructs the target parent

FUN_0803C33E creates a repeated visual composite.

It constructs four Bitmap children with FUN_0802DF08:
- parent +0x85C, initial resource 0xFFFF,
- parent +0x888, initial resource 0xFFFF,
- parent +0x8B4, initial resource 0xFFFF,
- parent +0x8E0, initial resource 0xFFFF.

FUN_0802DF08 is the concrete Bitmap constructor pattern: it initializes the visual object, installs Bitmap class data, stores the 16-bit resource ID at child +0x26, and derives/stores dimensions from that resource.

[FW] Therefore parent +0x85C is a real Bitmap child object.

## 50.2 The same visual composite is instantiated three times

FUN_0803C33E is called by:
- FUN_08039A48,
- FUN_08039B30,
- FUN_08039C18.

These sibling constructors also create FUN_0803CB04 update components.

FUN_0803CB04 reads internal model indices including 0x121. The 0x121 read is then sent to FUN_0803CACC, which writes value+10 into the Bitmap at parent +0x85C.

[STRONG] This establishes a repeated visual composite whose first Bitmap child is directly controlled by Boiler image selector 370A.

Do not yet assign the three instances to screen names or specific boilers without more parent/model proof.

## 50.3 370A and 469E8 are now structurally separate

370A path:
FUN_0803C33E
 -> Bitmap child +0x85C
 -> FUN_0803CACC
 -> resource 11..13

469E8 path:
FUN_080469E8
 -> Bitmap child +0x13C
 -> fixed resource 14

[FW] Resource 14 is not part of the 370A value+10 selector path.

## 50.4 Updated closed graph

0x370A
 -> internal 0x121
 -> FUN_08036FF2
 -> mapping table
 -> FUN_08037094
 -> FUN_080115F6
 -> record +0x0C
 -> 0x20021FA6
 -> u8 value 1..3
 -> FUN_0803CB04
 -> FUN_0803CACC
 -> value +10
 -> FUN_080307BC
 -> Bitmap child +0x85C
 -> resource 11..13

## 50.5 Next attack

The next useful target is no longer the selector chain itself.

Attack:
1. identify the exact class/vtable/source trace of FUN_0803C33E and FUN_0803CB04;
2. recover geometry X/Y/W/H of parent +0x85C and sibling Bitmap children;
3. connect resource IDs 11/12/13 to the actual extracted BitmapData entries;
4. determine which of the three repeated composites is the Home/main boiler graphic;
5. only then investigate the separate fixed resource 14 path.

# 51. THIRD RAW PASS — BITMAP CONSTRUCTOR/WRITER REVALIDATION — 2026-11-19

## 51.1 FUN_0803C33E contains six explicit Bitmap children

Direct raw disassembly shows:
- +0x330 -> FUN_0802DF08, initial resource 0xFFFF
- +0x35C -> FUN_0802DF08, initial resource 0xFFFF
- +0x85C -> FUN_0802DF08, initial resource 0xFFFF
- +0x888 -> FUN_0802DF08, initial resource 0xFFFF
- +0x8B4 -> FUN_0802DF08, initial resource 0xFFFF
- +0x8E0 -> FUN_0802DF08, initial resource 0xFFFF

[FW] Earlier shorthand saying the composite had only the four +0x85C-family Bitmaps was incomplete. The constructor explicitly creates six Bitmap children.
The 370A path nevertheless targets only +0x85C.

## 51.2 FUN_080307BC is a true Bitmap resource replacement operation

Raw code:
- resource ID is read from argument;
- stored at Bitmap +0x26;
- width is derived by FUN_0803439C and passed through object slot +0x38;
- height is derived by FUN_080343EA and passed through object slot +0x3C;
- clipping/visibility state is recomputed and a flag is stored at +0x29.

[FW] FUN_0803CACC therefore performs a genuine runtime Bitmap resource replacement, not a cosmetic ID write.

## 51.3 Extracted resource dimensions

The repository's firmware extraction records:
- resource 11 / 011.png = 105x126
- resource 12 / 012.png = 108x141
- resource 13 / 013.png = 82x145
- resource 14 / 014.png = 54x100

Because the Bitmap writer derives dimensions from the resource, the three 370A choices naturally produce different runtime dimensions.

## 51.4 Conservative class identity

Object +0 contains pointer-like values, but raw values seen in this region can resolve into UTF-16/data areas. Therefore:

[FW] We can name the concrete routines:
- FUN_0802DF08 = Bitmap constructor
- FUN_080307BC = Bitmap resource setter/update
- Bitmap object methods are dispatched through relative slots +0x38/+0x3C.

[OPEN] Exact C++ vtable/class identity remains unproven.
Do not promote object +0 literals to recovered vtables without executable method-table evidence.

## 51.5 Shared low-level Bitmap subsystem, separate higher-level paths

Variable selector:
FUN_0803CB04
 -> FUN_0803CACC
 -> parent+0x85C
 -> FUN_080307BC
 -> resources 11..13

Separate fixed path:
FUN_080469E8
 -> child+0x13C
 -> FUN_080307BC
 -> fixed resource 14

[FW] The two paths share the same Bitmap resource setter but use different higher-level components/children.

## 51.6 Next attack

1. Trace the constructor's +0x85C parent into its actual Home/Main root.
2. Recover placement/geometry around +0x84C/+0x85C.
3. Determine which of 08039A48 / 08039B30 / 08039C18 corresponds to the main boiler screen.
4. Trace visibility/state callbacks around FUN_0803CB04.
5. Only after that, connect the three resource images to concrete screen variant semantics.

# 52. RAW MULTIPASS — 370A UPDATE BODY + FIRST HARD GEOMETRY — 2026-11-19

[FW] Important function-role correction: `FUN_0803CB04` is the constructor/wiring routine for the visual update object. The actual refresh method starts at `FUN_0803CB2C`.

`FUN_0803CB2C` reads a sequence of model indices and performs UI mutations. Its 370A operation is exact:

```
ldr r0,[r4,#0x8]
movw r1,#0x121
BL FUN_08036FF2
UXTB r1,r0
ldr r0,[r4,#0xC]
BL FUN_0803CACC
```

Thus the closed path should use `CB2C` as the actual update body:

```
0x370A
 -> internal 0x121
 -> FUN_08036FF2
 -> runtime record
 -> 0x20021FA6
 -> u8 1..3
 -> FUN_0803CB2C
 -> FUN_0803CACC
 -> Bitmap +0x85C
 -> resource 11..13
```

## 52.1 First hard geometry

`FUN_0804272C` is behaviorally a two-coordinate setter: it forwards r1 through object slot +0x2C and r2 through slot +0x30.

A nearby layout/update routine `FUN_0803C5B4` explicitly does:

```
r0 = parent + 0x85C
r1 = 0x28
r2 = 0x46
BL FUN_0804272C
```

[STRONG] Therefore Bitmap child +0x85C is positioned at:
- X = 40
- Y = 70

The same routine then calls `FUN_08030380(parent+0x04, parent+0x85C)`, proving attachment of that child to the parent/container structure in this layout path.

Caveat: the flat-code scan currently has no direct BL caller for `FUN_0803C5B4`; therefore its dispatch mechanism and exact C++ class identity remain OPEN. The coordinate behavior and values are hard raw evidence.

## 52.2 Composite structure

`FUN_0803C33E` explicitly constructs six Bitmap children:
- +0x330
- +0x35C
- +0x85C
- +0x888
- +0x8B4
- +0x8E0

All start with resource 0xFFFF. Only +0x85C is directly controlled by 370A.

The same `FUN_0803C5B4` layout path later targets +0x8E0 with resource 0x7A and X=398, further supporting that it is a multi-child layout/update routine.

## 52.3 Resource dimensions

`FUN_0803439C` / `FUN_080343EA` select resource records from a runtime registry rooted around 0x2002454C and return width/height fields at record +0x08/+0x0A. This confirms the dimensions of the 370A Bitmap are resource-driven after `FUN_080307BC`.

## 52.4 Current status

CLOSED:
- 0x121 -> 0x370A
- 370A -> 0x20021FA6
- 370A 1/2/3 -> resources 11/12/13
- actual update body = FUN_0803CB2C
- target Bitmap = +0x85C
- first hard geometry = X40/Y70

OPEN:
- dispatch path into FUN_0803C5B4
- W/H and visibility for +0x85C
- exact parent/Home/Main mapping of the three 08039A48/39B30/39C18 instances
- direct BitmapData table entries for resources 11/12/13
- fixed resource 14 role
- independent provenance of 0x0801AB7E

Batch: `BATCH-370A-UPDATE-GEOMETRY-2026-11-19.md`.


# 53. FOURTH RAW PASS — DIRECT COMPOSITE CALLERS + GEOMETRY CORRELATION — 2026-11-19

## 53.1 FUN_0803C33E has exactly three direct raw callers

Full Thumb BL scan of FW2213TK_kopia.bin finds direct calls to FUN_0803C33E at:
- 0x08039AD6
- 0x08039BBE
- 0x08039CA6

These belong to FUN_08039A48, FUN_08039B30 and FUN_08039C18 respectively.

Immediately after C33E returns, each sibling constructor wires the returned composite into a FUN_0803CB04 updater when the relevant second component exists.

[FW] This closes the fact that the three sibling constructors instantiate the same visual composite rather than merely sharing similar code.

## 53.2 C33E has more structure than the four 85C-family Bitmaps

Direct raw disassembly:
- +0x330 Bitmap, resource 0xFFFF
- +0x35C Bitmap, resource 0xFFFF
- +0x388 helper/object
- +0x464 helper/object
- +0x498 helper/object
- +0x84C helper/container
- +0x85C Bitmap, resource 0xFFFF
- +0x888 Bitmap, resource 0xFFFF
- +0x8B4 Bitmap, resource 0xFFFF
- +0x8E0 Bitmap, resource 0xFFFF
- +0x90C/+0x948/+0x97C and later additional UI objects

[FW] +0x84C is initialized through FUN_080424C4 with parent pointer plus two literal parameters and sits directly before the 370A Bitmap at +0x85C. Exact semantic class of this helper remains OPEN.

## 53.3 C5B4 geometry is independently hard

FUN_0803C5B4 uses:
- child = parent +0x85C
- X=0x28 (40)
- Y=0x46 (70)
- FUN_0804272C(child,40,70)
- FUN_08030380(parent+0x04,child)

It later configures +0x8E0 with fixed resource 0x7A and X=0x18E (398), Y from runtime state, and attaches it through the same parent+0x04 mechanism.

[STRONG] This is now a genuine multi-child layout/initialization path, not merely an isolated coordinate assignment.

## 53.4 C5B4 dispatch remains OPEN

A raw BL scan finds no direct call to FUN_0803C5B4 and no literal function-pointer occurrence of 0x0803C5B5.

Therefore do not claim a direct C33E -> C5B4 call or an exact vtable slot. The proven relation is structural: C33E constructs the object layout; C5B4 operates on that same offset layout and supplies hard geometry.

## 53.5 Three-instance architecture

The strongest current model is:

SIBLING CONSTRUCTOR
 -> FUN_0803C33E
 -> common composite (+0x330/+0x35C/+0x85C/+0x888/+0x8B4/+0x8E0 + helpers)
 -> FUN_0803CB04
 -> FUN_0803CB2C
 -> internal 0x121 / 370A
 -> FUN_0803CACC
 -> +0x85C
 -> resource 11/12/13

Separate layout method:
FUN_0803C5B4
 -> +0x85C at (40,70)
 -> +0x8E0 at (398,Yruntime)

## 53.6 Next attack

1. Resolve indirect dispatch into C5B4.
2. Identify +0x84C helper/container.
3. Recover all W/H/visibility writes for +0x85C.
4. Resolve resource-registry records 11/12/13.
5. Differentiate the three sibling instances into concrete Home/Main roles.


# PERSISTENT CONTINUATION OVERRIDE — 2026-11-19

**This section is the current checkpoint for every future chat/agent. It overrides older handoff sections when they conflict.**
Persistent memory file:
`analiza/FW2213TK-2026-11-19/BATCH-PERSISTENT-CONTINUATION-MEMORY-2026-11-19.md`

## User operating contract
The investigation is continuous across chats. GitHub is the durable memory. A new chat must read the persistent memory file and this MASTER, then continue from the CURRENT START POINT below. Do not restart from the beginning. User expects several deep passes: find -> analyze -> continue -> return to main chain -> repeat. Do not stop at small findings. Never invent graphics, geometry, class names, vtables or callbacks.

## Verified raw firmware
`FW2213TK_kopia.bin`
SHA-256:
`1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`

## CLOSED 370A -> Bitmap chain
`0x370A -> internal 0x121 -> FUN_08036FF2 -> table 0x08037984 -> FUN_08037094 -> FUN_080115F6 -> record +0x0C -> 0x20021FA6 -> value 1..3 -> FUN_0803CB2C -> FUN_0803CACC -> Bitmap +0x85C -> FUN_080307BC -> resource 11/12/13`.

Therefore: 1->11, 2->12, 3->13. This is hard executable-code proof.

## CLOSED C33E geometry facts
`FUN_0803C33E` creates six Bitmap children: +0x330, +0x35C, +0x85C, +0x888, +0x8B4, +0x8E0.
Exactly three direct callers: 08039A48, 08039B30, 08039C18.
`FUN_0803CB04` = constructor/wiring; `FUN_0803CB2C` = runtime update.
`FUN_0803C5B4` sets +0x85C to X=40,Y=70 and attaches it via parent+0x04. It later sets +0x8E0 to resource 0x7A, X=398,Y=runtime.
Resource dimensions: 11=105x126, 12=108x141, 13=82x145.

## CRITICAL CORRECTION
`+0x84C` is NOT proven to be the container/parent of +0x85C. It is separately initialized by `FUN_080424C4`. Current status: separate helper/object, semantics OPEN.

## CURRENT START POINT FOR NEXT CHAT
1. Resolve indirect dispatch reaching `FUN_0803C5B4`.
2. Decode `FUN_080424C4` and +0x84C semantics.
3. Enumerate all resource/X/Y/W/H/visibility/clipping/attachment mutations of +0x85C,+0x888,+0x8B4,+0x8E0.
4. Recover runtime BitmapData/resource records for 11/12/13 and correlate with 011.png/012.png/013.png.
5. Compare the three C33E siblings to identify concrete screen semantics.
6. Only after that render anything, and only with real assets/geometry.

Keep 0x158/0x11C cascade branch and resource 14 separate from 370A unless a new hard bridge is found. Keep 0x0801AB7E separate; it is raw data/resource, not the 370A runtime callback.

Latest previous MASTER commit: `972e39e85170e8c821cf60eaa96a2b6410d41dd4`.
Latest previous batch: `2551d0b130ba5b051d3bb6ab103d9878ffb5f344`.


# PASS 5 — HIDDEN UI METHOD CLUSTER — 2026-11-19

Batch:
`analiza/FW2213TK-2026-11-19/BATCH-METHOD-CLUSTER-C5B4-CACC-CB2C-2026-11-19.md`

## New [FW]/[STRONG] finding

Canonical `functions.txt` shows:
- `FUN_0803C550` starts at 0x0803C550 and has size 100 bytes,
- therefore ends exactly at 0x0803C5B4,
- but `0x0803C5B4` has no own functions.txt entry even though raw analysis identifies real code there.

Likewise key recovered procedures `FUN_0803CACC`, `FUN_0803CB04`, and `FUN_0803CB2C` do not appear as normal entries in functions.txt.

C33E has the same class of problem: `FUN_0803C284` ends at 0x0803C312, next listed function is 0x0803C4C4, while raw analysis independently recovers `FUN_0803C33E` inside that gap.

This means the current C33E/C5B4/CB04/CB2C area contains a **hidden/unrecognized method cluster** relative to the automatic Ghidra function list.

## Interpretation

[STRONG] This does not yet prove a C++ vtable slot. It does, however, strongly explain why:
- direct BL scans miss C5B4,
- literal function-pointer scans may miss C5B4,
- object methods can exist outside the Ghidra call graph.

The next dispatch attack should therefore search the **hidden method cluster and method-table/function-pointer storage**, not only literal BL targets.

## Current continuation

1. Recover exact boundaries of C33E/C5B4/CACC/CB04/CB2C and neighboring unrecognized procedures.
2. Search nearby/associated method-table or function-pointer storage.
3. Test whether C5B4 is an indirect target.
4. Decode FUN_080424C4/+0x84C.
5. Enumerate all mutations of +0x85C/+0x888/+0x8B4/+0x8E0.
6. Compare 39A48/39B30/39C18 only after the method cluster is understood.

Do not reopen the closed 370A -> 11/12/13 chain.


# PASS 5 — HIDDEN UI METHOD CLUSTER — 2026-11-19

Batch: `analiza/FW2213TK-2026-11-19/BATCH-METHOD-CLUSTER-C5B4-CACC-CB2C-2026-11-19.md`

[FW] `FUN_0803C550` starts at 0x0803C550 and has size 100 bytes, therefore ends exactly at 0x0803C5B4. Yet 0x0803C5B4 has no functions.txt entry although raw analysis identifies real code there. 

[FW] `FUN_0803CACC`, `FUN_0803CB04`, and `FUN_0803CB2C` likewise have no normal functions.txt entries despite independently recovered executable behavior. C33E sits in an analogous functions.txt gap: FUN_0803C284 ends at 0x0803C312 and the next listed function is 0x0803C4C4, while raw analysis recovers C33E at 0x0803C33E.

[STRONG] The C33E/C5B4/CB04/CB2C area contains a hidden/unrecognized UI-method cluster relative to the automatic Ghidra function list. This does not by itself prove a vtable, but it explains why direct call-graph evidence is incomplete and changes the dispatch attack.

## CURRENT CONTINUATION
1. Recover exact boundaries of C33E/C5B4/CACC/CB04/CB2C and neighboring unrecognized procedures.
2. Search method-table/function-pointer storage associated with this cluster.
3. Test whether C5B4 is an indirect target.
4. Decode FUN_080424C4/+0x84C.
5. Enumerate all mutations of +0x85C/+0x888/+0x8B4/+0x8E0.
6. Then differentiate 39A48/39B30/39C18.

Do not reopen the closed 370A -> 11/12/13 chain.


# PASS 5B — +0x84C CONSTRUCTOR CONFIRMS HIDDEN-METHOD PATTERN — 2026-11-19

Batch: `analiza/FW2213TK-2026-11-19/BATCH-METHOD-CLUSTER-C5B4-CACC-CB2C-2026-11-19.md`

[FW] `FUN_0804204A` has size 204 bytes and ends exactly at `0x08042116`; the next functions.txt entry is `FUN_0804272C`. Yet raw analysis independently recovers `FUN_080424C4`, the constructor of +0x84C. Thus 424C4 is another executable procedure inside a Ghidra function-recognition gap.

The manually recovered UI procedures outside normal functions.txt now include C33E, C5B4, 424C4, CACC, CB04 and CB2C.

[STRONG] This is a recurring custom-UI method recovery problem, not an isolated missing C5B4 caller. The dispatch investigation should therefore recover the method-table/function-pointer structure first, then test membership of these procedures.

Do not promote this to a specific vtable/class identity yet.


# PASS 5M — RESOURCE 0x7A / +0x8E0 GEOMETRY CORRECTION — 2026-11-19

Batch:
`analiza/FW2213TK-2026-11-19/BATCH-PERSISTENT-CONTINUATION-MEMORY-2026-11-19.md`

[DATA] The firmware bitmap extraction maps resource IDs to PNG assets. `0x7A` is decimal `122`, and `DOKUMENTACJA/bitmap_sizes.tsv` records `122.png = 35x37`.

This closes the previously proposed edge-alignment test for `+0x8E0`:

- `+0x8E0` resource = `0x7A = 122`
- X = `398`
- W = `35`
- right edge = `433`, not 480
- H = `37`
- Y = runtime value

[FW] The firmware still proves the runtime placement `X=398, Y=runtime`; the resource table now proves the fixed bitmap dimensions.

[STRONG] Therefore `+0x8E0` is a small right-side UI element, not a bitmap aligned to the physical right edge of the 480-px display. Do not use the old `398+82=480` hypothesis.

This is a **correction**, not a weakening: we have eliminated one false geometric interpretation and narrowed the role of `+0x8E0` to a small UI resource.

## ACTIVE NEXT ATTACK

1. `+0x8E0`: find every resource/X/Y/visibility/clipping mutation.
2. `+0x888` and `+0x8B4`: recover resource and geometry mutations.
3. `FUN_080424C4` / `+0x84C`: exact object semantics.
4. Hidden method cluster: indirect dispatch to `FUN_0803C5B4`.
5. Three sibling constructors: distinguish `39A48/39B30/39C18` by upstream/downstream evidence.

No render yet.
