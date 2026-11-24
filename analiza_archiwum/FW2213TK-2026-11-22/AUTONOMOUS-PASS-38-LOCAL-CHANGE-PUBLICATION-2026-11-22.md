# AUTONOMOUS PASS 38 — PUBLIKACJA LOKALNEJ ZMIANY PARAMETRU (WYKONANA W FIRMWARE) — 2026-11-22

Firmware SHA-256 `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`. Narzędzie: `tools/publish_probe.py` (z asercjami). Adresy: PROJECT (RUNTIME = +0x10000).

## Eksperyment
Po emulacji startupu wywołano callback managera `FUN_08010FCE` (this = `0x20008D84`) 200 razy, potem **zmieniono bezpośrednio storage Language** (`0x20021FAA`: 0→7, symulacja lokalnej zmiany) i wywołano go ponownie 200 razy,
przechwytując rekordy trafiające do kolejki TX (prymityw `0x08057224`).

## HARD — wynik
- Po zmianie pojawia się **dokładnie jedna** ramka: **StdId `0x0584`, DLC 8, Data = `42 03 00 01 07 xx xx xx`** (cmd `0x42`, indeks `0x0003` LE, subindeks 1, wartość LE).
  Potwierdza to w wykonaniu PASS 20 (`FUN_0801117C` wykrywa zmianę lokalny/shadow i buduje `0x0584/0x42`; sink `0x20008D60` slot0 → adapter TX `0x0806E59C`).
- Kolejne 200 wywołań bez zmiany nie generuje nic (shadow zaktualizowany) — publikacja jest **zdarzeniowa (on-change)**, nie cykliczna.
- Bajty Data[5..7] ponad szerokość typu zawierają śmieci (np. `...46 00 00 20` dla wartości 0x46): nieużywane bajty wartości **nie są zerowane** w ramce. Odbiorca musi maskować do szerokości typu; moduł ESP32 powinien wysyłać je jako 0.
- 11 ramek „baseline” (10× klasa 0 live, 1× klasa 1) pojawia się przy pierwszych wywołaniach bez ingerencji — to publikacje wartości początkowych różniących się od shadow w stanie emulowanym (np. `0x2166`, `0x2299`, `0x22AD`, `0x22FD`, `0x2211`, `0x3171`);
  ich zawartość zależy od stanu emulacji (provider `0x20008D64` czyta sprzęt, który nie jest modelowany) i NIE jest wynikiem do przenoszenia.

## Wniosek protokołowy
Panel (node 4) ma dwa kierunki na tych samych COB-ID: wysyła `0x0604` (żądanie odczytu, PASS 37) i przyjmuje `0x0584/0x42` (odpowiedzi), a przy lokalnej zmianie **sam wysyła `0x0584/0x42` z nową wartością**
(push). Zapis przychodzący z centrali to ta sama ramka `0x0584/0x42` odebrana przez handler `0x08062A90` (PASS 37). Rola/kierunek każdego urządzenia na magistrali wymaga sprawdzenia na żywym CAN — OPEN.

## OPEN
1. Czy publikacja obejmuje wszystkie klasy (tu zaobserwowano klasy 0/1/3; klasa 2 nie testowana) i czy klasa 0 (live) zmieniona lokalnie też jest publikowana.
2. Okno przetwarzania (ile rekordów na wywołanie) i okres wywołań callbacku w rzeczywistości.
3. Szczegół: dlaczego „baseline” zawiera klasę 0 (brak rozróżnienia lokalne/live w stanie emulowanym).
