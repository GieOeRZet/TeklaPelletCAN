# AUTONOMOUS PASS 39 — CLASS 12 = PRZEŁĄCZANIE JĘZYKA (setLanguage) — 2026-11-22

Firmware SHA-256 `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`. Narzędzie: `tools/lang_cycle_probe.py` (asercje). Adresy: PROJECT (RUNTIME = +0x10000).
Zamyka STRONG z PASS 35 §3.

## HARD — ścieżka wykonana w firmware
Sekwencja z RAW `0x3C12A` (case klasy 12): `r = FUN_080373BA()` (GET klucz 3) → `FUN_080373E6(r+1)`. `FUN_080373E6` liczy `v = r1 & 7` (`r1 − (r1>>3)<<3`), zapisuje **klucz 3** przez `0x08011812` (typ 5)
i **tail-call do `FUN_080391D6(v)`**. `FUN_080391D6` ustawia `currentLanguage` (u16 @ SRAM `0x20024860`) = v i `currentLanguagePtr` (`+4`) = `tablica[v]`, po czym odświeża pomocnicze stany (`0x0804BB12/BB18/BB0A`) — wzorzec TouchGFX `Texts::setLanguage`.
Wykonanie 10 kroków w emulatorze: `key3` oraz `currentLanguage` = 1,2,3,4,5,6,7,0,1,2 (**cykl mod 8**, asercje zaliczone).
`FUN_080391D6` ma 4 miejsca wywołania: `0x08036D76`, `0x08037412` (ta ścieżka), `0x08037CF2`, `0x08060280` — pozostałe 3 (prawdopodobnie przywrócenie języka przy starcie/zmiana z innego ekranu) OPEN.

## HARD — tablica języków i kolejność
Tablica `0x20011844` (SRAM, z danych IAR) ma **8 wskaźników** (wpis 8 to nie tabela) do tabel TypedText. Identyfikacja z treści (ten sam tekst w każdej tabeli):

| indeks | język | tabela (RAW) |
|---|---|---|
| 0 | PL | 0x5BE64 (baza ID 0 = 0x5BD80) |
| 1 | EN | 0x4AEEC |
| 2 | LT | 0x4B6A8 |
| 3 | SK | 0x4CDDC |
| 4 | CZ | 0x497B8 |
| 5 | ES | 0x49F74 |
| 6 | RO | 0x4C620 |
| 7 | EST | 0x4A730 |

(Wskaźnik języka = adres wpisu o ID 57; baza tabeli = wskaźnik − 57·4.) Zakres parametru Language (0..30) jest szerszy niż 8; wartości 8..30 przy odbiorze CAN są dopuszczone przez walidację zakresu (PASS 37), a UI ogranicza cykl do 0..7.
To jest wprost kolejność do odtworzenia na ESP32 (`Language` = indeks tablicy języków).
Uwaga: starsza lista kolejności „ES, EST, EN, LT, PL, RO, SK, CZ” z handoffu 20.11 opisuje kolejność tabel w pliku, nie wartość parametru.

## STRONG — który wiersz menu uruchamia class 12
Tablica klas `0x20005EF0` po starcie: `00 0a 01 02 03 04 05 06 07 08 09 0b 0d 11 0f 0c 0e 12 10 13 14` (niezmieniona względem danych IAR). **Wiersz 15 ma klasę 12** (rekord `00 00 | 0c 00 | 49 00`), a wiersze 15..20 są budowane tylko przy `access != 0` (PASS 21/22).
Zatem akcja zmiany języka jest dostępna po wprowadzeniu PIN-u (poziom ≠ 0); wiązanie „wiersz 15 → klasa 12” opiera się na indeksowaniu tablicy klas numerem wiersza (PASS 28/29), bez wykonania dotyku → OPEN do potwierdzenia na ścieżce UI.
Korekta wcześniejszych notatek: klasy wierszy 15..20 (12,14,18,16,19,20) pochodzą z pola `+2` rekordu (nie z selektora w polu `+0`, który ma wartości 0,90,97,100,98,95); dla wierszy 0..14 klasa = selektor.

## OPEN
1. Znaczenie pola `+2` rekordu menu dla wierszy 0..14 (odczyt jako ID tekstu daje nazwy stanów kotła, a dla 15..20 wartości będące klasami) — nie traktować jako etykiety menu.
2. Trzy pozostałe wywołania `setLanguage` i przywrócenie języka przy starcie (skąd wartość: key 3 z centrali/BKPSRAM?).
3. Dotyk → callback → class 12 w UI (nie wykonano).
