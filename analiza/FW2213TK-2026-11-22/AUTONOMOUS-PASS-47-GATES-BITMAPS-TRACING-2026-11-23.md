# AUTONOMOUS PASS 47 — BRAMKI POZIOMU DOSTĘPU (SKAN CAŁEGO FIRMWARE), EKSPORT BITMAP, ŚLEDZENIE ZASOBÓW — 2026-11-23

Firmware SHA-256 `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`. Adresy RUNTIME (PROJECT = −0x10000), jeśli nie zaznaczono inaczej.
Decyzje właściciela projektu (23.11): **ESP32 i Home Assistant odłożone do domknięcia reszty 1:1**; skalowanie/powiększanie grafik odłożone (konwerter PNG↔RGB565 tylko w razie potrzeby).

## HARD — skan wszystkich odczytów poziomu dostępu (`tools/access_gates_scan.py`, `data/access_gates_scan.csv`)
52 odczyty `ldrb.w Rt,[Rn,#0x158]` w 42 funkcjach: **17× `cmp #3 ; blt`** (poziom ≥ 3 — dokładnie 17 bramek z dawnych analiz), 13× „≠ 0" (`cbz`/`cmp #0; beq`), 2× `cmp #2` (≥ 2); 18 konstruktorów stron
(`0x0805A114, 0x0805A7B4, 0x0805AF9C, 0x0805BECC, 0x0805E7A4, 0x0805F1C8, 0x0805F50C, 0x0805FC64, 0x0805FF64, 0x08060220, 0x080604DC, 0x08060798, 0x08060AAC, 0x08060D68, 0x08061024, 0x080612E0, 0x0806F87C, 0x08073328`)
robi `ldrb r1,[model+0x158]; mov r0,r4; bl <pomocnik>` — poziom jest przekazywany do pomocnika strony, gdzie siedzi porównanie. **Nigdzie nie ma porównania „==” poziomu → poziomy są kumulatywne** (poziom 3 ma wszystko z 1 i 2 plus bramki ≥3).
`FUN_08037E74` (RUNTIME `0x08047E74`): `0→0, 900→1, 999→2, 6154→3`, zapis do `[this+0x158]`, `this = 0x20020784`.

## HARD — eksport wszystkich 188 bitmap (`tools/export_bitmaps.py`, `data/bitmaps/`, `data/bitmaps.zip`)
Tablica deskryptorów RAW `0x54450`, 188 × 0x14 B `{data_ptr, extra_ptr(A8), w, h, solid x,y,w,h}`; dane RGB565 LE + opcjonalnie A8 (121 z alfa, 67 bez). Rozmiary 188/188 zgodne z `DOKUMENTACJA/bitmap_sizes.tsv`; wygląd zweryfikowany na planszach; `manifest.csv` z SHA-256.
Format oryginału: surowy RGB565 + A8 (nie base64). PNG jest odwracalny do RGB565 (replikacja bitów). Zamyka lukę z handoffu 20.11 (brak trwałego kompletu PNG w GitHubie).
Skalowanie: tła/paski/przyciski (np. 6,7,21,22,24,79–81,102–104,160–163,168–169) rysować programowo; ikony skalują się lepiej; teksty to osobne czcionki (nie bitmapy). Odłożone.

## Śledzenie zasobów i PID (`UiSession.enable_trace`, `tools/resource_coverage.py`)
- Odczyty deskryptorów bitmap (`0x08064450`, 188×0x14) i wskaźników TypedText (8 tabel; wskaźnik języka = adres wpisu ID 57) przez firmware = zasoby użyte na ekranie. **Włączać PO rozruchu** (przy starcie czytane są wszystkie — test integralności). Otwarcie MENU: 33 bitmapy, 21 tekstów PL (ID 95–134, 265, 266, 270, 494).
- Hook wejścia wyszukiwania rekordu runtime (`0x080215F6`, r2 = klucz) tylko w GUITask (TCB `0x20001198`) → zbiór PID-ów czytanych przez ekran (`trace_*.json`, pole `pids`). Zastosowanie: ekran → PID bez zgadywania; sterowanie ekranem głównym danymi.

## KOREKTA (własny błąd)
Porównanie zrzutów poziomów 1, 2 i 3 wyszło „identyczne” **z winy narzędzia**: `scroll_capture` urywał się po 2 stronach stron USTAWIEŃ (kolejne przeciągnięcia gubione), a listy mają 24–28 pozycji. Poziom jest ustawiony poprawnie (ikona w nagłówku: osoba/klucz z cyfrą 1/2/3).
Wnioski o różnicy poziom 2 vs 3 NIE są jeszcze wyciągnięte. Naprawa: `ui_session.stitch_body` (zszycie całej listy w jeden obraz) + `tools/settings_tall.py` (28 zadań: 7 ekranów × 4 poziomy) — w toku.
Znane ograniczenie wejścia dotykowego: przeciągnięcia w dół bywają gubione zależnie od fazy odpytywania FT5x06 (~40 ms); stosować tylko ruchy w górę od stanu z punktu kontrolnego, stuknięcia z `hold ≥ 130` ticków.

## Stan procentowy (szacunek, nie metryka)
Transport CAN ~90% · silnik parametrów ~92% · macierz PID→CAN ~75% · menu i nawigacja ~88% · poziomy dostępu ~80% · ekrany USTAWIEŃ i dialogi ~60% · ekran główny ~65% · zasoby graficzne ~95% · wykresy ~50% · narzędzia ~92% · **całość rewersu 1:1 ~70%** · ESP32/HA 0% (odłożone).

## OPEN (kolejność)
1. Porównanie pełnych list ustawień 0/1/2/3 (`settings_tall`) → co dokładnie dodaje poziom 3 (17 bramek `≥3` → ekrany/widżety, np. pola „Ochrona kotła”, „7°C” na ekranie Ogrzewanie 1).
2. Dane na ekranie głównym: PID-y czytane przez Home (trace) i sterowanie nimi (`set_local`); warianty stanów, alarmów, kolorów tła, kafelków.
3. Pokrycie zasobów: ponowny przebieg `ui_explore` poziomu 3 z trasowaniem → lista bitmap i tekstów nigdy nieużytych (kandydaci na ukryte funkcje).
4. Ekrany Kaskada (klasa 8) i Dodatkowy magazyn paliwa (klasa 9); edycja wartości (dialogi) i skutki w CAN; wykresy (`0x47/0x48`).
5. Bramka pollera `0x2002466C+0x10` (co otwiera odbiór `0x584` w normalnej pracy).
