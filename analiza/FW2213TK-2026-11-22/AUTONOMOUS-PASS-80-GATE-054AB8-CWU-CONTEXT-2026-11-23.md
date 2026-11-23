# AUTONOMOUS PASS 80 — LEVEL>=1 GATE 0x08054AB8 CONTEXT — 2026-11-23

## Cel
Domknąć B4 dla czwartej bramki poziomu: runtime PROJECT naming from previous artifacts uses `0x08054AB8`, caller `0x08054CA6`.

## FACT

### 1. Korekta adresowania
W RAW BIN funkcja znajduje się pod offsetem `0x44AB8`, czyli PROJECT/runtime-space address `0x08044AB8` przy regule `PROJECT = 0x08000000 + RAW`.

Poprzednie artefakty `access_gates_scan.csv` używają adresów runtime/re-pack w zakresie `0x0805xxxx`; po odjęciu `0x10000` otrzymujemy właściwe RAW/PROJECT code location.

Analogicznie:
- artifact caller `0x08054CA6` -> RAW `0x44CA6`.

### 2. To jest konstruktor/renderer ekranu CWU, a nie przypadkowa funkcja
W funkcji RAW `0x44AB8` znajduje się dalsza część budowy strony UI. Przy branchu poziomu:
- `ldrb [model,#0x158]`
- `cbz r0,...`
- dla level != 0 wykonywany jest dodatkowy widget.

W ścieżce gated:
- wywołanie wspólnego buildera `FUN_08040380`,
- bitmap ID `0x84`,
- presenter/view offset `0x1498`.

### 3. Offset 0x1498 ma zamkniętą identyfikację
`data/presenter_map.csv` zawiera:
- view_off `0x1498`,
- PID `0x201A`,
- nazwę **Hot water 1 result temperature** / **CWU – temperatura zadana (wynikowa)**.

Ten sam rekord ma presenter `0x08054DAC`.

Zatem gated element z `0x08054AB8` jest związany z wynikiem temperatury CWU, nie z Kaskadą ani Magazynem paliwa.

### 4. PID 0x201A jest potwierdzony jako runtime parameter
`pid_matrix_655.csv`:
- PID `0x201A`,
- u16,
- storage `0x200221D4`,
- nazwa Hot water 1 result temperature,
- class live.

### 5. Sąsiedni ekran/rodzina jest jednoznacznie CWU
W `presenter_map.csv` ta sama rodzina ma m.in.:
- `0x2010` Hot water 1 comfort temperature,
- `0x2012` Hot water 1 economical temperature,
- `0x2014` Hot water 1 program,
- `0x201A` Hot water 1 result temperature,
- `0x2110` Hot water 1 measured temperature.

To daje niezależne potwierdzenie kontekstu strony.

## WERDYKT

**HARD:** bramka `0x08054AB8` / odpowiadająca jej funkcja w RAW `0x44AB8` jest częścią budowy ekranu CWU i warunkuje dodatkowy element zależny od poziomu.

**HARD:** `0x1498` w tej ścieżce identyfikuje presenter dla PID `0x201A` — wynikowej temperatury CWU.

**STRONG:** PASS 72-owa hipoteza „może Kaskada/Dod. magazyn” jest odrzucona. To nie jest ta rodzina ekranów.

## OPEN

- dokładne znaczenie bitmapy `0x84` w tym gated widgetcie,
- dokładny tekst/format tego dodatkowego elementu (w kodzie ścieżka używa również ID `0x1A7` w wywołaniu widget buildera; katalog TypedText wskazuje `0x1A7` w rodzinie Statystyki/Info, więc nie wolno automatycznie nazywać go etykietą CWU),
- dynamiczne potwierdzenie wartości/warunku poza samym level != 0.

## REJECTED

- `0x08054AB8` = Kaskada,
- `0x08054AB8` = Magazyn paliwa.

## Narzędzia
Dowód oparty na RAW disassembly oraz istniejących artefaktach:
- `data/access_gates_scan.csv`
- `data/presenter_map.csv`
- `data/pid_matrix_655.csv`

