# CHAT CONTINUITY — 2026-11-20 — ARCHITECTURE RESET

## Powód zapisu

Użytkownik jednoznacznie ustalił, że **nie budujemy nowej wersji istniejącego TeklaPelletCAN** i nie traktujemy jego konfiguracji, funkcjonalności, zależności ani menu jako źródła prawdy.

### Cel projektu

Zbudować od zera nowy software działający na ESP z komunikacją CAN, który zachowuje się możliwie **1:1 względem oryginalnego firmware panela Estyma/igneoTouch**, z wyjątkiem warstwy sprzętowej:
- oryginał: MCU/ST + oryginalny hardware Touch,
- projekt: ESP + własna komunikacja/CAN + odpowiedni renderer.

"1:1" obejmuje:
- konfigurację,
- dostępne moduły,
- zależności,
- menu i nawigację,
- ekrany,
- widget tree,
- geometrię X/Y/W/H,
- warstwy/clipping,
- bitmapy,
- TypedText/fonty,
- kolory,
- visibility/state,
- animacje,
- touch/callbacki,
- parameter engine,
- rekordy,
- CAN read/write,
- storage/persistence,
- alarmy,
- timery/state machine,
- service/test,
- warianty sprzętowe,
- profile,
- zależności CO1..CO4/CWU/buffer/solar/cascade/fuel storage.

## Absolutny priorytet źródeł

1. [FW] bezpośredni dowód z FW2213TK_kopia.bin
2. [DATA] dane/asset tables wyciągnięte z BIN
3. [DOC] dokumentacja Estyma — tylko korelacja
4. [STRONG] wniosek wsparty wieloma ścieżkami
5. [OPEN] hipoteza

**Istniejący TeklaPelletCAN nie jest źródłem prawdy.**

## Status poprzedniego renderera

Wcześniejsza warstwa "original Touch Home" jest **prototypem/legacy** i nie definiuje architektury finalnego programu.

Nie wolno traktować wcześniejszego renderu jako dowodu geometrii ani kolorystyki. Użytkownik słusznie wskazał, że wcześniejszy render nie zachowywał geometrii i kolorów 1:1.

Finalny renderer ma być budowany dopiero z:
- prawdziwych bitmap FW,
- prawdziwych TypedText/fontów,
- prawdziwych X/Y/W/H,
- prawdziwych parent-child relationships,
- prawdziwych visibility/state,
- prawdziwych callbacków.

## Architekturę finalną ustalono

```
FW-equivalent parameter database
        ↓
configuration / installation resolver
        ↓
capability resolver
        ↓
access-level resolver
        ↓
screen/menu dispatcher
        ↓
screen state
        ↓
original widget/resource tree
        ↓
touch/callback mapping
        ↓
parameter engine
        ↓
record engine
        ↓
CAN/storage/side effects
        ↓
ESP/HA adapter
        ↓
renderer
```

Renderer nie może decydować, czy użytkownik ma bufor, solary, kaskadę itd.

## Wymagana konfiguracja dynamiczna

Muszą być obsłużone co najmniej syntetyczne warianty:
- CO1
- CO1+CWU
- CO1+CO2+CWU
- CO1+CO2+CWU+buffer
- CO1..CO4+CWU
- CO1..CO4+CWU+buffer+solar
- +additional fuel storage
- +cascade master
- różne profile/module types
- ograniczony access level
- installer/service level

Użytkownik nie posiada wszystkich wariantów fizycznie, dlatego testowanie będzie wykonywane przez syntetyczne konfiguracje równoważne wartościom firmware.

## Nowo zamknięte konfiguracje

Firmware mapping:
- internal 0x10E → panel/CAN 0x2105 = Heating configuration
- internal 0x10F → 0x2106 = Hot water configuration [STRONG]
- internal 0x110 → 0x2108 = Solar configuration [STRONG]
- internal 0x111 → 0x2107 = Buffer configuration [STRONG]

Selector logic FUN_0803C178:
- selector 5 → 0x10F → CWU gate
- selector 6 → 0x110 → Solar gate
- selector 7 → 0x111 → Buffer gate
- selectors 1..4 → 0x10E → heating/CO gate

To jest pierwszy twardy fundament capability resolvera.

## Ważne już zamknięte obszary z wcześniejszych analiz

### Bitmapy
- 188 bitmap resources
- descriptor table raw 0x54450
- record 20 B
- RGB565 + A8
- payload mapping: runtime pointer - 0x08010000
- poprawny dekoder RGB565 został ustalony
- prawdziwe assety mają być używane, nie generowane odpowiedniki

### Panel
- 480x272
- RGB565
- TouchGFX

### Parameter mapper
FUN_08036FF2:
- family-of-4 + instance +1
- druga część = singletony
- nie wolno spłaszczać CO1..CO4 do jednej wartości.

### Instance state
- +0x12B = class/type
- +0x12C = właściwa instancja 1..4
- +0x12C bierze udział zarówno w READ jak i WRITE.

### Record engine
- FUN_0801143C registration
- FUN_080115F6 lookup
- FUN_0801167A read +0x14
- FUN_080116E6 read +0x1C
- stride 0x2C
- +0x08 CAN/index
- +0x0C source/storage pointer
- +0x10 type
- +0x14 value/descriptor
- +0x1C alternate value
- +0x24 metadata

### CO family
- wspólny builder FUN_0803E714
- klasy 1..4
- 12 parametrów + opcjonalne 11
- dalsza droga przez mapper → widget record → refresh

### Burner animation
- 40..42 = burner feeder
- 36..38 = storage/fuel feeder
- 65..67 = igniter
- 8..10 = blower
- 58..59 = grate
- index 5 / +A38 unresolved
- timings: 14/14/18/6/25

### Pump
- 138..143 = wspólna 6-frame family
- wielokrotne instancje w firmware

### Mixer
- 105 base
- state 1 → 106
- state 2 → 107
- kierunek stanów jeszcze OPEN

### Hopper
- 0x147 → 0x3601 fuel remaining
- 0x148 → 0x3600 capacity
- 0x149 → 0x3603 reserve threshold
- 0x14A → 0x3602 reserve flag
- FUN_0802DA54: reserve=0 → bitmap 051; reserve!=0 → 053; 052 jest drugą warstwą
- obecne progi z TeklaPelletCAN nie są specyfikacją firmware.

## Geometria

Użytkownik wymaga odtwarzania geometrii 1:1. Nie wolno jej zgadywać.

Dla każdego widgetu trzeba zapisywać:
- parent,
- class/vtable evidence,
- resource/text,
- X,
- Y,
- W,
- H,
- visibility,
- clipping,
- z/layer,
- state,
- source parameter,
- callback/write path.

## Kolorystyka

Nie generować "podobnych" kolorów. Odtworzyć:
- prawdziwe bitmapy,
- prawdziwe RGB565,
- prawdziwe alpha/A8,
- prawdziwe TypedText/fonty,
- kolory widgetów z firmware, jeśli nie są bitmapą,
- gradienty/linie/Canvas tylko po odtworzeniu z kodu.

## Następne przebiegi

Priorytet:
1. wszystkie configuration strings → exact internal IDs
2. configuration screen widget tree
3. menu/screen dispatcher
4. Home complete tree
5. CO1..CO4 family
6. CWU
7. Buffer
8. Solar
9. Cascade
10. additional fuel storage
11. access-level matrix
12. touch/write paths
13. machine-readable capability matrix
14. synthetic configuration test harness
15. final renderer dopiero po zamknięciu behavior model

## Zasada dla kolejnego agenta

Nie zaczynaj od obecnego TeklaPelletCAN JS.

Najpierw przeczytaj:
- MASTER-STATE-CONSOLIDATED-2026-11-19.md
- START-HERE-FOR-NEXT-AGENT.md
- BATCH-WHOLE-SOFTWARE-MULTIPASS-2026-11-20.md
- BATCH-ANIMATION-ENGINE-AND-ACTUATOR-MAPS-2026-11-20.md
- BATCH-ORIGINAL-TOUCH-HOME-IMPLEMENTATION-2026-11-20.md
- BATCH-ORIGINAL-SOFTWARE-ARCHITECTURE-RESET-2026-11-20.md
- ten plik

Dopiero potem wykonuj nowe reverse engineering.

## Ważne wycofane hipotezy

Nie wracać do:
- 47290 = bottom bar
- 056/057 = 151/152
- 0x0801AB7E jako funkcja
- DAT_08046CC4 jako vtable
- 0x158/0x11C jako 370A
- +0x5DA/+0x5DE jako "progress fields"
- 36–44 jako jeden ciągły actuator
- 60/61 jako przypisany actuator bez proof
- prostego mapowania 370A 1/2/3 → 011/012/013
- FUN_08038ED0 jako pewnego konstruktora WheelSelectorExtra
- wcześniejszego wygenerowanego Home jako pixel-perfect

## GitHub

Repo:
GieOeRZet/TeklaPelletCAN

Branch:
ccr-be8a1bcb-5t76j0

Nowy dokument resetu:
analiza_archiwum/FW2213TK-2026-11-20/BATCH-ORIGINAL-SOFTWARE-ARCHITECTURE-RESET-2026-11-20.md

Reset commit:
0c17cdb6fd28cb8f69deac3cfc9c28ce77ffc598

Mapping correction/update commit:
8860ededfb891779177ccaf57c0edf221bda3e1c

Ten dokument jest zapisem decyzji i kontekstu rozmowy z 2026-11-20. Nie jest literalnym transcriptem czatu; jest trwałym handoffem technicznym.


## MULTIPASS-20 UPDATE — 2026-11-20

### New hard configuration spine

Current internal -> CAN mapping is:
- 0x10D -> 0x3505 = Outside temperature sensor configuration
- 0x10E -> 0x2105 = Heating configuration
- 0x10F -> 0x2106 = Hot water configuration
- 0x110 -> 0x2108 = Solar configuration
- 0x111 -> 0x2107 = Buffer configuration

**Superseded:** older 2026-11-19 notes that mapped 0x10E -> 0x3505 and 0x10F -> 0x2105.

### 0x2105 is now closed at capability/visibility level

FUN_0803C178 directly maps:
- selector 1 -> internal 0x10E / 0x2105, visible iff >=1
- selector 2 -> 0x2105, visible iff >=2
- selector 3 -> 0x2105, visible iff >=3
- selector 4 -> 0x2105, visible iff >=4

Because selectors 1..4 are the proven CO1..CO4 menu entries, this is direct firmware proof that Heating configuration controls CO1..CO4 capability/visibility.

Still OPEN: whether the same value directly triggers C064 object creation or +0x12C assignment. Keep capability resolution separate from object-instantiation resolution.

### Documentation correlation

Official Estyma/Tekla documentation explicitly states that "Ilość obwodów grzewczych" determines the number of CO circuits and that IgneoTouch supports up to 4 CO circuits. Profiles/module types remain a separate axis.

Full report:
`analiza_archiwum/FW2213TK-2026-11-20/MULTIPASS-20-DEEP-CONFIG-ACCESS-SOURCE-OF-TRUTH-2026-11-20.md`
