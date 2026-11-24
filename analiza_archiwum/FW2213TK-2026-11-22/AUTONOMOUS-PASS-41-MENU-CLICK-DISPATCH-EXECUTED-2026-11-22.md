# AUTONOMOUS PASS 41 — NAWIGACJA MENU: DOTYK WIERSZA → KLASA → EFEKT (WYKONANE W FIRMWARE) — 2026-11-22

Firmware SHA-256 `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`. Narzędzie: `tools/menu_click_probe.py` (asercje). Dane: `data/menu_click_effects_21.csv`. Adresy: PROJECT (RUNTIME = +0x10000).

## HARD (kod) — handler przycisku wiersza
`FUN_0807EB00(this, sender)` (RUNTIME `0x0808EB00`): `base = this[+0x3B4]`, `n = bajt this[+0x3B8]` (=21 w zbudowanym ekranie); pętla `i = 0..n−1`: jeśli `sender == base + i·0x274`, wywołuje
`FUN_0803C064(this[+0x3C], i)` — czyli dispatcher klas z **indeksem wiersza**; klasa = `0x20005EF0[i]`, dalej TBB (PASS 29). To jest wzorzec TouchGFX `buttonCallbackHandler(const AbstractButton&)`:
nadawca → indeks wiersza → akcja. Siostrzany handler `FUN_0807EB36` robi to samo z `FUN_0804EC18` (drugi callback — nie badany). Literały obu handlerów: RAW `0x63AB8` / `0x63AC0` (PASS 21).
To zamyka brakujące ogniwo „dotyk → callback → klasa”: **nie ma callbacka w wierszu (+0x26C = 0 po zbudowaniu, +0xF8 to stały wskaźnik `0x0807C540`)**; wiązanie jest na poziomie ekranu (rejestr wierszy + jeden handler).

## HARD (wykonanie) — efekty „kliknięcia” (poziom dostępu 3, harness `menu_click_probe.py`)
Obserwowane pola: `key3`/`currentLanguage` oraz kontekst modelu `+0x12A/+0x12B/+0x12C`.

| wiersz | klasa | zaobserwowany efekt |
|---|---|---|
| 0 | 0 | brak zmiany w obserwowanych polach (kod zapisuje `+0x12A = 1`, wartość już była 1; PASS 31) |
| 1 | 10 | `+0x12B ← 10` |
| 2 | 1 | `+0x12B ← 1` (`+0x12C` już było 1) |
| 3, 4, 5 | 2, 3, 4 | `+0x12B ← 2/3/4` **i** `+0x12C ← 2/3/4` (CO2..CO4) |
| 6, 7, 8, 9, 10 | 5, 6, 7, 8, 9 | `+0x12B ← 5, 6, 7, 8, 9` |
| 11, 12 | 11, 13 | brak zmian w obserwowanych polach (inny skutek — OPEN) |
| 13 | 17 | `+0x12B ← 0x10` |
| 14 | 15 | brak wyniku: wołanie przez NULL (ścieżka `0x08042318 → 0x0802EADE` wymaga obiektów niemodelowanych) |
| **15** | **12** | **`key3 0→1` i `currentLanguage 0→1` (zmiana języka, PASS 39)** |
| 16, 17, 19 | 14, 18, 19 | brak zmian w obserwowanych polach (OPEN) |
| 18 | 16 | `+0x12B ← 0x11` |
| 20 | 20 | `+0x12B ← 0x13` |

Wnioski:
- **Wiersz 15 (access≠0) = zmiana języka** — wcześniej STRONG, teraz potwierdzone wykonaniem ścieżki od handlera przycisku.
- **Klasy 1..4 (wiersze 2..5) wybierają obwód CO1..CO4**: `+0x12C` (aktywna instancja z PASS 25/34; rezolwer `PID = baza + instancja − 1`) dostaje 1..4 i `+0x12B` też. Tym samym **producent instancji `[ctx+0x12C]` dla rodziny CH jest HARD: wiersze CO1..CO4 w menu głównym** (zamyka OPEN nr 1 z PASS 35 dla tej ścieżki; inne ścieżki nie badane).
- `+0x12B` działa jak identyfikator strony/rodziny: 1..4 CO, 5..9 kolejne rodziny, 10 palnik, 0x10/0x11 (klasy 17/16), 0x13 (klasa 20). Sama zmiana strony (przełączenie ekranu) odbywa się dalej, poza zaobserwowanymi polami — OPEN.

## Granice dowodów
- To wywołanie handlera z poprawnym nadawcą, nie zdarzenie dotyku TouchGFX; dojście dotyku do handlera (hit-test, `Callback::execute`) nie jest wykonane.
- Presenter (`this[+0x3C]`) był pustym obszarem; klasy używające go (np. 11, 13, 14, 18, 19) mogą mieć skutki niewidoczne w obserwowanych polach lub niewykonane przez brakujące obiekty.
- Klasa 15 (wiersz 14) kończy się wywołaniem przez NULL.

## OPEN
1. Skutki klas 11, 13, 14, 18, 19 i 15 (wymagają szerszych obserwowanych pól i obiektów presentera).
2. Mechanizm samego przełączania ekranu po ustawieniu `+0x12A/+0x12B`.
3. Drugi handler `FUN_0807EB36` → `FUN_0804EC18` (callback, np. przytrzymanie/zwolnienie) i jego klasy.
4. Etykiety tekstowe wierszy i ekrany docelowe.
