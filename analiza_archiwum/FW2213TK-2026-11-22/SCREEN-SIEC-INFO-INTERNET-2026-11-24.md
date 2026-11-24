# PASS — SIEĆ / INFO / INTERNET — 2026-11-24

## Zakres

Domknięcie dwóch małych/średnich ekranów:
- SIEĆ: `0x808f770`
- INFO: `0x808f638`
- INTERNET: `0x808f9ac`

Źródła: firmware FW2213TK_kopia.bin oraz istniejące wyniki emulatora/PASS 65–69.
Firmware SHA-256: `1d679d6810cfb44a4c1d862d67552b7220f3edb3a2807f3067d46185d0c5071`.

Legenda:
- FACT-DYNAMIC = zaobserwowane w działającym emulatorze.
- FACT-STATIC = wynika bezpośrednio z binarki/katalogów danych.
- OPEN = nadal brak wystarczającego dowodu.

## 1. INFO — 0x808f638

FACT-DYNAMIC:
- ekran ma 16 widgetów; dwa warianty różnią się wyłącznie ikoną poziomu w nagłówku.
- stałe:
  - `INFO`
  - `Controller by Estyma (www.estyma.pl)`
- dynamiczne pola:
  - `igneoTouch v<wersja>`
  - nazwa kotła
  - `videRoom PIN <wartość>`
- widget wersji używa wildcardu; obserwacja emulatora: `2.213 TE`.
- nazwa kotła: obserwacja `Bio Compact 10kW`.
- videRoom PIN: obserwacja `0` w zrzucie/emulatorze (wartość katalogowa parametru ma domyślnie 5678; nie utożsamiać tych dwóch obserwacji bez dalszego testu).

FACT-STATIC / mapowanie:
- wersja oprogramowania: PID `0x3664`, `soft. version`, u16, live.
- nazwa kotła: PID `0x3665`, `igneTouch boiler short name`, u32.
- videRoom PIN: PID `0x2170`, `VideRoom PIN`, u16, live.
- tekst producenta jest stały i nie ma PID.
- nagłówek/ikona/CPU są elementami wspólnymi ekranu, nie polami danych.

Wniosek:
INFO jest ekranem prawie całkowicie zamkniętym: 3 pola danych + 2 główne teksty stałe. Pozostaje tylko zweryfikować dokładny formatter/wildcard dla `0x3665` i `0x2170` oraz wartość rzeczywistą przy różnych danych CAN.

## 2. INTERNET — 0x808f9ac

FACT-DYNAMIC:
Pola widoczne:
- SSID
- PASSWORD
- SERIAL
- PIN
- WiFi
- Zmiany zdalne
- wskaźnik zasięgu WiFi.

Zidentyfikowane PID:
- SSID: `0x3730..0x3735` — 6 × u32, 24 znaki.
- PASSWORD/KEY: `0x3736..0x373B` — 6 × u32.
- status: `0x373C`, `0x373D` (u8, live/status); `0x373D=2` steruje obecnością ikony WiFi w dotychczasowym teście.
- WiFi: `0x373E` (u8, setting, klasa 3).
- SERIAL: `0x373F` (u32).
- PIN: `0x3740` (u32).
- Zmiany zdalne: `0x3741` (u8, setting, klasa 3).
- dodatkowe flagi/statusy używane przez renderer: `0x3744`, `0x3745`, `0x3746` (u8).
- dodatkowo istnieje `0x372F` = automatyczna synchronizacja zegara (u8, setting, klasa 3), ale nie jest to pole ekranu INTERNET.

Format SSID:
- każdy PID jest u32;
- kolejność bajtów w obrębie u32 jest big-endian dla tekstu (np. `Home` = `0x486F6D65`);
- łącznie 24 znaki.

FACT-DYNAMIC — zapis przełączników:
- WiFi: dotknięcie przełącznika ustawia `0x373E: 0 -> 1` i generuje CAN `0x584`, payload `42 3E 37 01 01 00 00 00`.
- Zmiany zdalne: dotknięcie ustawia `0x3741: 0 -> 1` i generuje CAN `0x584`, payload `42 41 37 01 01 00 00 00`.

FACT-DYNAMIC — pola tekstowe:
- tap pola SSID (≈ x=192,y=62) powoduje zmianę obrazu, ale w obecnym zestawie PASS 65 nie wykazano jeszcze vtable/dialogu klawiatury ani zapisu PID.
- tap pola PASSWORD (≈ x=219,y=92) analogicznie powoduje zmianę obrazu, ale ścieżka edytora/zapisu nie jest jeszcze zamknięta.

OPEN:
- dokładny dialog klawiatury znakowej (vtable, widgety, układ klawiszy, backspace/OK/cancel).
- sposób składania znaków do sześciu PID-ów.
- moment zapisu SSID/PASSWORD i dokładne ramki CAN.
- walidacja długości/znaków.
- pełna logika kolorów etykiet i wskaźnika WiFi zależna od `0x373C..0x3746`.

Architektura:
- panel nie ma własnego interfejsu WiFi; konfiguracja dotyczy zewnętrznego modułu VIDE NET/WIFI na CAN.
- zidentyfikowane w firmware węzły obejmują m.in. `0x5B = VIDE NET WIFI`.

## 3. SIEĆ — 0x808f770

FACT-DYNAMIC:
- ekran ma 133 widgety w jednym wariancie.
- układ: nagłówek + kontener 460×232 z 8 wierszami po 28 px.
- każdy wiersz ma 4 pola tekstowe:
  - x=15, szer. 135
  - x=150, szer. 110
  - x=260, szer. 80
  - x=340, szer. 90
- przy braku partnerów CAN emulator pokazuje puste wiersze.

Ważna errata:
- zasoby TypedText użyte w czterech kolumnach mają ID 474/471/473/472. W bazie TypedText odpowiadają one tekstom `Auto synchronizacja zegara`, `Przepływomierz powietrza`, `Ciśnienie max. [bar]`, `Ciśnienie min. [bar]`.
- NIE traktujemy tego jako semantyki kolumn SIEĆ. Jest to artefakt współdzielenia zasobów/nieustalonego wildcardu w obecnym przebiegu. W istniejących raportach ekran SIEĆ jest opisany jako lista modułów/urządzeń CAN, a bez partnerów linie pozostają puste.
- nie ma obecnie wiarygodnego dowodu, że wiersze SIEĆ są zasilane bezpośrednio z PID-ów panelu. To jest przede wszystkim lista wykrytych węzłów/identyfikacji CAN.

Zidentyfikowana architektura sieci:
- `0x5A` = VIDE GSM
- `0x5B` = VIDE NET WIFI
- `0x5C` = VIDE NET
- `0x56/0x57` = CAN IO BIG
- `0x40..0x47` = CAN IO 0..7
- `0x64..0x67` = VIDE ROOM 1..4
- `0x6E..0x75` = CAN GATEWAY 0..7
- `0x78..0x7F` = CAN IO MINI 0..7
- `0x08` = RADIO GATEWAY
- `0x05..0x07` = SLAVE 1..3.

OPEN:
- dokładne kolumny (nazwa/typ/wersja/status) należy potwierdzić na panelu/emulatorze z co najmniej jednym prawdziwie zasymulowanym partnerem CAN.
- źródło każdego pola wiersza (IDENT / Object Dictionary / heartbeat / PDO) nie powinno być zgadywane jako PID.

## 4. Następny przebieg

Priorytet dla INTERNET:
1. odtworzyć dialog tekstowy po tap SSID;
2. przechwycić każdy klawisz;
3. ustalić bufor edycji i mapowanie znak -> 6 × u32;
4. nacisnąć OK;
5. potwierdzić PID-diff i ramkę `0x584`;
6. powtórzyć dla PASSWORD;
7. testy graniczne: pusty tekst, 1/24 znaków, znaki specjalne.

Priorytet dla SIEĆ:
1. zbudować minimalnego partnera CAN z poprawnym heartbeat/IDENT;
2. doprowadzić do pojawienia się jednego wiersza;
3. porównać BEFORE/AFTER i log CAN;
4. dopiero wtedy przypisać semantykę czterem kolumnom.

## Status zadania

- INFO: **~90%** — dane i stałe zidentyfikowane; formattery wymagają krótkiej weryfikacji.
- INTERNET: **~70%** — PID-y i przełączniki zamknięte; edytor SSID/PASSWORD i zapis OPEN.
- SIEĆ: **~45%** — geometria i architektura CAN zamknięte, semantyka wierszy/kolumn wymaga partnera CAN.

Nie oznaczam niezmierzonych elementów jako FACT-DYNAMIC.
