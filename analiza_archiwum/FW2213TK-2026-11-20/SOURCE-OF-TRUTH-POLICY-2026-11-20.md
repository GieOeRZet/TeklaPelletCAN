# SOURCE-OF-TRUTH-POLICY — TeklaPelletCAN

## Cel

Cała dokumentacja reverse engineeringu ma pozostać w repozytorium GieOeRZet/TeklaPelletCAN.
Nie tworzyć drugiego repo tylko na dokumentację. Nie kopiować tej samej bazy wiedzy między repozytoriami.

## Hierarchia dowodów

### Poziom A — źródło pierwotne
- FW2213TK.bin / FW2213TK_kopia.bin
- surowe bajty
- kod Thumb-2
- xref
- tablice
- konstruktory
- vtable
- obiekty i pola
- bitmapy
- TypedText
- konfiguracja i gate’y
- parametry
- CAN IDs / rekordy

### Poziom B — bezpośrednie ekstrakty z firmware
- CSV katalogów
- mapy bitmap
- mapy stringów
- mapy parametrów
- wykryte tablice
- geometria wynikająca z kodu
- wykryte grafy zależności

### Poziom C — dokumentacja producenta
Instrukcje Estyma/Tekla są terminologicznym i funkcjonalnym cross-checkiem. Pomagają interpretować funkcję, ale nie mogą być używane do dopisywania funkcji, której firmware nie potwierdza.

### Poziom D — obserwacje użytkownika
Zdjęcia ekranów, obserwacje menu, zachowanie sterownika, wyniki skanowania CAN. Są bardzo wartościowe jako testy rzeczywiste i do generowania hipotez.

### Poziom E — stary projekt
Stary projekt może służyć do porównania i wyszukiwania tropów, ale jego semantyka nie jest normatywna.

## Reguła
Jeżeli A/B przeczy C/D/E: A/B wygrywa.
Jeżeli D pokazuje funkcję, której jeszcze nie znaleziono w A/B: nie oznacza to, że funkcji nie ma. Oznacza to OPEN i wymaga dalszego reverse engineeringu.
Jeżeli E mówi, że rejestr ma znaczenie X: nie przenosimy X do nowej implementacji bez potwierdzenia w firmware.

## Dokumentowanie
Każdy większy chat/przebieg: osobny plik continuity, lista nowych dowodów, korekty poprzednich interpretacji, lista OPEN, następny plan ataku, commit SHA.
Nie deklarować istnienia surowego transkryptu, jeżeli zapisano tylko streszczenie techniczne.

## Cel końcowy
Rekonstrukcja 1:1 całego softu: architektura UI, menu, poziomy dostępu, konfiguracja, warianty kotła, moduły, parametry, CAN, grafika, stringi, interakcje, logika stanów i zależności między elementami.
Nie implementować na podobieństwo. Najpierw dowód z firmware, potem implementacja.