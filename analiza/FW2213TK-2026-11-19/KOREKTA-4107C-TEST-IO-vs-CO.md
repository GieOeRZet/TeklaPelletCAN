# KOREKTA: 22-entry table 0x0804107C / CO1..CO4 / BIG

Data: 2026-11-19

## Najważniejsza korekta poprzedniej analizy

Wcześniej potraktowaliśmy DAT_0804107C i funkcję 0x08040FC2 jako potencjalny most konfiguracji instancji CO. To było zbyt mocne.

Repozytoryjny kod symulatora zawiera niezależnie odtworzoną listę kTix[22], która odpowiada dokładnie temu zakresowi funkcjonalnemu:

- 0x2259 feeder test
- 0x2283 blower test
- 0x2284 igniter test
- 0x2286 boiler pump test
- 0x311F solar pump test
- 0x229D/0x229E/0x229F/0x22A0 pompy CO1..CO4 test
- 0x214A/0x214B/0x214C/0x214D mieszacze CO1..CO4 test
- 0x216D return mixer test
- 0x351E/0x351F external fuel storage motors
- pozostałe wpisy są również komendami testowymi wyjść.

W engine.cpp lista jest nazwana kTix, a on_read() zapisuje jej wyniki do test_vals_[22]. To bardzo mocno wskazuje, że DAT_0804107C jest tabelą Test I/O, a nie tabelą tworzenia instancji CO.

## Co to zmienia

0x08040FC2 nadal jest ważną funkcją, ale należy ją klasyfikować jako warstwę obsługi/odświeżania 22 testów wyjść, nie jako źródło liczby obwodów.

Most 0x2105 -> liczba aktywnych CO pozostaje więc nieznaleziony.

## Co jest natomiast coraz mocniej potwierdzone

### 1. Firmware panela ma fizyczny model CO1..CO4

W kodzie projektu odtworzono parametry testowe:
- 0x229D = pompa CO1 test
- 0x229E = pompa CO2 test
- 0x229F = pompa CO3 test
- 0x22A0 = pompa CO4 test

oraz:
- 0x214A = mieszacz CO1 test
- 0x214B = mieszacz CO2 test
- 0x214C = mieszacz CO3 test
- 0x214D = mieszacz CO4 test

To jest bezpośredni dowód, że Touch ma zdefiniowane kanały wykonawcze CO1..CO4 jako logiczną rodzinę.

### 2. UI ma osobne teksty dla obwodów 1..4

TouchGFX zawiera serię:
- TypedText 119 = Ogrzewanie obwód 1
- TypedText 120 = Ogrzewanie obwód 2
- TypedText 121 = Ogrzewanie obwód 3
- TypedText 122 = Ogrzewanie obwód 4

To nie dowodzi jeszcze, że wszystkie cztery są aktywne równocześnie. Dowodzi natomiast, że firmware ma pełny model UI dla czterech obwodów.

### 3. Mechanizm +0x12C = instancja pozostaje niezależnym dowodem

Nadal obowiązuje twardy ślad:
module+0x12C = 1..4
oraz base_index + instance - 1 i lookup przez 0x1167A / zapis przez 0x11812.

To jest właściwy kandydat na mechanizm parametryzacji CO1..CO4. Nie należy go łączyć z tabelą 22 testów.

## Aktualny model

IGNEO TOUCH
  |
  +-- konfiguracja systemu / I/O
  |      +-- 0x2105 Heating configuration
  |      +-- 0x2106 CWU
  |      +-- 0x2107 Buffer
  |      +-- 0x2108 Solar
  |      +-- 0x3500 Main module type
  |      +-- 0x3502 CH expansion module type
  |      +-- 0x350B Profile number
  |      +-- 0x16C1 / 0x16D5 dodatkowe pola
  |
  +-- model obiektów
         +-- CO1
         +-- CO2
         +-- CO3
         +-- CO4
               +-- +0x12C = 1..4

BIG / CAN I/O
  +-- fizyczne kanały wykonawcze
  +-- konfiguracje zależne od profilu
  +-- dodatkowe moduły CAN, np. Lambda

## Ważna korelacja z architekturą BIG

Lista testów CO1..CO4 nie oznacza, że BIG zawsze fizycznie posiada cztery kompletne obwody CO. Oznacza, że Touch zna logiczne kanały CO1..CO4 i ma dla nich komendy testowe.

Dopiero konfiguracja systemu + profil I/O + dostępność modułów określają, które z tych kanałów mają sens w konkretnej instalacji.

To dobrze pasuje do korekty architektury: Touch jest regulatorem, BIG jest modułem I/O, a CO1..CO4 są logicznymi obiektami systemu.

## Następny właściwy cel reverse engineeringu

1. znaleźć wszystkie odczyty bajtu/storage 0x20021FAF przez mechanizmy pośrednie;
2. znaleźć kod tworzący/wybierający obiekty dla +0x12C;
3. znaleźć warunek, który ogranicza CO1..CO4;
4. zestawić go z 0x3500/3502/350B i dodatkowymi polami konfiguracji;
5. dopiero wtedy ustalić rolę 0x2105.

## Status

- DAT_0804107C = BARDZO PRAWDOPODOBNIE tabela Test I/O, a nie tabela instancji CO.
- CO1..CO4 jako logiczne kanały Touch = UDOWODNIONE.
- +0x12C = instancja 1..4 = UDOWODNIONE.
- 0x2105 = liczba aktywnych CO = nadal BARDZO PRAWDOPODOBNE, ale bez mostu w kodzie.
- 0x2105 -> +0x12C = NIEUDOWODNIONE i nie należy tak tego modelować bez dalszego dowodu.
