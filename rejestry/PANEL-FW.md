# Firmware panelu IgneoTouch (FW2213TK.bin) – analiza

- STM32F4, TouchGFX, obraz surowy pod 0x08000000, teksty UTF-16 (PL/EN/CZ/RO/LT/EE/ES).
- Tablica par (indeks CANopen, ID parametru panela): 420 par, offset 0x37576-0x37C0A -> `panel-fw-mapa-indeks-id.csv`.
  Potwierdzone: 0x3708->ID 23, 0x2207->18, 0x216C->33, 0x3604->363.
- 74 indeksy, ktorych nie ma w naszym katalogu (status BRAK), sa dowodem, ze rejestr istnieje; nie znamy jeszcze nazw/zakresow.
- Laczenie ID -> tekst/zakres NIE znalezione (brak wprost wskaznikow w obrazie; teksty nie sa w kolejnosci ID).
- Teksty menu istnieja: Antylegionella, Alarm dzwiekowy, Histereza, Wymiennik, Rezerwa paliwa, Wybieg pompy [min] - bez powiazania z indeksem.
- Wniosek: nowe indeksy (np. 0x3721-0x3750, 0x228D-0x228F, 0x218A-0x218C) warto skanowac sdo_scan i badac metoda roznicowa.

## Skan kotla 2026-11-06 (fw 1.4.14, sub 1, wezel 4)
- Przeskanowano zakresy 0x2000-0x2170, 0x2200-0x2330, 0x2990-0x29A0, 0x3000-0x3174, 0x3500-0x366B, 0x3700-0x3750, 0x4000-0x4056: odpowiedzialo 446 rejestrow, zadnego spoza katalogu.
- Z 288 indeksow, ktore panel zna, a firmware nie uzywa: 197 odpowiada na kotle, 91 NIE (m.in. 0x372F-0x374C, 0x228D-0x228F, 0x218A-0x218C, 0x3666-0x366B, 0x3500, 0x3502) - to pewnie opcje innych konfiguracji (kaskada, dodatkowe obiegi) albo ID tylko panelu.
- Kolumna `odpowiada_na_kotle_2026-11-06` w panel-fw-mapa-indeks-id.csv.
- Skan: usluga esphome.tekla_estyma_sdo_scan z sub=1 (sub 0/2 nic nie zwraca). Rejestry nieistniejace nie daja wpisu.

## Pełna mapa parametrów z FW2213TK (analiza kodu, 6.11)
Poprawna baza ładowania firmware panela to **0x08010000** (nie 0x08000000 – stąd wcześniejsze „ścięte” bitmapy). Parametry rejestruje kod funkcją `0x0802143C` (448 wywołań); ID parametru = indeks SDO. Wynik: [`panel-fw-parametry-FW2213TK.csv`](panel-fw-parametry-FW2213TK.csv) (id, nazwa, typ, min, max, domyślna, dostęp: 0 live / 1 komenda / 2-3 nastawa) – 372 z 448 jest w katalogu, 76 poza nim. Nazwy wszystkich 197 niewykorzystanych rejestrów: [`snap-197-nazwy-FW2213TK.csv`](snap-197-nazwy-FW2213TK.csv).
Odkryte m.in.: **0x201C** Temp. maks. CWU (40–80, raw 316 = 60), **0x2268/226E/226F/2275/227A** krzywa wentylatora spalin (20…60 %), **0x3506** Alarm dźwiękowy (flaga), **0x3508/0x3509** godziny ciszy od/do, **0x2297** Antylegionella (tylko flaga – panel nie ma osobnego dnia/godziny), **0x3610/0x3613–0x3616** średnia moc z 50 h i średni tlen 30/50/70/90 % (brakujące wiersze Statystyk), **0x3628** energia całkowita [kWh], **0x3710** zużycie paliwa [dkg/h], **0x3718/0x3719** data serwisu, **0x374B/0x374C** pompa cyrkulacyjna CWU, **0x3603** rezerwa paliwa, **0x3664** wersja softu, 0x3511–0x351C kaskada, 0x351E–0x352B zewnętrzny magazyn paliwa.
Grafiki panela (188 bitmap RGB565+A8, tablica @0x54450) zdekodowane – to własność Estymy (wszelkie prawa zastrzeżone); w repozytorium są jako opcjonalna funkcja zgodności karty (`grafiki: pelne`, `dist/img/panel/`) i zostaną usunięte na wyraźną prośbę właściciela praw.
