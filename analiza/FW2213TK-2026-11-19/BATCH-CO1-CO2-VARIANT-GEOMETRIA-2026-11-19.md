# BATCH — 2026-11-19 — CO1/CO2 WIDGETS + HARD GEOMETRY + VARIANT LAYER

## Cel
Przestać zbierać luźne bitmapy i połączyć konfigurację wariantu z rzeczywistymi komponentami UI.

## 1. Warstwa wariantu sprzętowego — utrzymana
Twardy trace:
- object+0x16BF = 0x3500 Main module type
- object+0x16C0 = 0x3502 CH expansion module type
- object+0x16CC = 0x350B Profile number
- object+0x16C1 = dodatkowe pole konfiguracyjne wpływające na wybór struktur
- object+0x16D5 = osobny warunek inicjalizacji

Dla Main=0:
- expansion=0: profile 1/2/3 -> wariant 2/3/4
- expansion=1: profile 1/2/3 -> wariant 5/6/7
Main=1/2 mają osobne gałęzie.

Wybrany wariant nie jest pojedynczym przełącznikiem: indeks wybiera wiele równoległych struktur/wskaźników.

## 2. Ważna korekta 0x2105
0x2105 = Heating configuration, zakres 0..4, ale nie znaleziono literalnego call-site do 0x2105 w aktualnym decompiled.c.

Nie wolno twierdzić:
0x2105 -> liczba CO
ani:
0x2105 -> +0x12C

C064 i DAT_0804107C nie są dowodem aktywacji liczby obwodów:
- C064 = dispatcher klasy/instancji
- DAT_0804107C/410FC2 = Test I/O (pompy/mieszacze CO1..CO4), nie źródło aktywacji Home CO.

## 3. CO1/CO2 mają realne, odrębne komponenty UI
W raw BIN potwierdzono dwa duże komponenty:
- raw 0x46D2C / runtime 0x08056D2C -> TypedText 58 = „Ogrzewanie 2”
- raw 0x4B618 / runtime 0x0805B618 -> TypedText 57 = „Ogrzewanie 1”

Są to osobne warianty klas/vtable, nie tylko ten sam widget z innym napisem.

## 4. CO2 ma rzeczywistą geometrię z firmware
W komponencie runtime 0x08056D2C:
- TypedText 348 = „Błąd wygaszania”
  - X=205 Y=195 W=200 H=70
- TypedText 460 = „Liczba kotłów slave”
  - X=320 Y=195 W=200 H=70
- TypedText 68 = „Moc 2”
  - obecny w komponencie przy child +0x85C

Helper 0x08030358 jest rzeczywistym setGeometry:
caller przekazuje X,Y,W,H; metody vtable +0x34/+0x38/+0x3C zapisują kolejne współrzędne/wymiary.

Niezależny test 0x0805F87C ustawia X=0,Y=0,W=480,H=272, potwierdzając pełny obszar ekranu.

## 5. CO1/CO2 posiadają osobne vtable
W raw BIN:
- CO2 vtable ok. raw 0x7EE20 zawiera Thumb pointer 0x08056D2D
- CO1 vtable ok. raw 0x7F778 zawiera Thumb pointer 0x0805B619

Wspólne metody otoczenia + różny wpis implementacji potwierdzają osobne warianty komponentu.

## 6. Seria 8 powtarzalnych konstruktorów
W firmware istnieje 8 podobnych konstruktorów:
0x0804C410
0x0804C78C
0x0804CA94
0x0804CD9C
0x0804D00C
0x0804D320
0x0804D634
0x0804D948

Każdy ma wspólną rodzinę UI:
- wybór TypedText 40..49 zależnie od +0x12B
- TypedText 159 = Temp. maksymalna [°C]
- TypedText 170 = Temperatura CO dla 0°C [°C]
- TypedText 171 = Temperatura CO dla 10°C [°C]

Nie utożsamiać jeszcze 8 konstruktorów z 8 obwodami CO. To może być rodzina reużywalnych komponentów/ekranów.

## 7. CO1..CO4 — tekstowa rodzina
Potwierdzone TypedText:
- 99..102 = OGRZEWANIE 1..4
- 119..122 = Ogrzewanie obwód 1..4
- 57 = Ogrzewanie 1
- 58 = Ogrzewanie 2

To daje nam cztery niezależne warstwy tekstowe dla CO1..CO4, ale nadal nie jest dowodem, które z nich są widoczne w konkretnym wariancie Home.

## 8. Co nadal brakuje
Najważniejsze otwarte połączenie:
variant 1..7
 -> konkretny konstruktor Home/Main
 -> konkretny CO1/CO2/... child
 -> parent/add()
 -> visibility
 -> bitmap + TypedText + runtime values.

Szczególnie nadal trzeba odzyskać:
- parent dla runtime 0x08056D2C / 0x0805B618,
- miejsce dodania tych komponentów do hierarchii ekranu,
- upstream selection wariantu,
- dynamiczne bitmap writers dla CO tile.

## 9. Następny atak
Nie wracać do 370A.
Priorytet:
1. znaleźć add/parent dla CO1/CO2 przez vtable/indirect calls,
2. zidentyfikować, który z komponentów jest tworzony przez FUN_0803E5AC / jego dzieci,
3. rozebrać FUN_08047604 i 0802E716 pod kątem tych samych vtable/TypedText,
4. dopiero wtedy mapować 480x200 pages do wariantów 1..7.

## 10. Dowód jakości
Ten batch rozdziela:
- HARDWARE/PROFILE variant layer,
- FUNCTIONAL configuration 2105..2108,
- object class/instance layer,
- actual CO UI classes,
- Home root.

Nie łączymy tych warstw bez bezpośredniego mostu.
