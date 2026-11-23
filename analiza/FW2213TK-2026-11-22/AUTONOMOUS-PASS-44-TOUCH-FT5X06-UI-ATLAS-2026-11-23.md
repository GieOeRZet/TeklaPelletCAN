# AUTONOMOUS PASS 44 — DOTYK (FT5x06), PRZELICZENIE WSPÓŁRZĘDNYCH, PIERWSZY ATLAS EKRANÓW Z FIRMWARE — 2026-11-23

Firmware SHA-256 `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`. Narzędzia: `tools/stm32_i2c.py` (I2C + slave `FT5x06`), `tools/touch_screen.py`, `tools/ui_session.py` (sesja krok po kroku). Obrazy: `data/atlas/*.png`.
Adresy: PROJECT (RUNTIME = +0x10000). Wymaga emulatora systemowego z PASS 42/43.

## HARD — kontroler dotyku i protokół
- Kontroler dotyku to **FocalTech FT5x06 na I2C1, adres 7-bit `0x38`** (bajty adresu `0x70`/`0x71`). Odpytywanie co ~40 tików (25 Hz) przez GUITask: `START, 0x70, 0x03, START, 0x71, odczyt 1 B, STOP`; po wykryciu zdarzenia blok `0x03..0x07` (P1_XH/XL/YH/YL).
  Ślad wywołań w momencie odczytu: `taskEntry 0x080661F3 → 0x080662AB (HAL tick) → 0x080759E7 (sampleTouch) → 0x08072251 (odczyt I2C)`.
- **Przeliczanie współrzędnych** (`FUN` PROJECT `0x080759DC` = `sampleTouch(&x,&y)`, RUNTIME `0x080759DC`/`0x08065…` wg tabeli): `x_ekran = (x_raw·3750 + 5000)/10000 ≈ 0,375·x_raw`, `y_ekran = (y_raw·354 + 500)/1000 ≈ 0,354·y_raw`.
  Czyli panel raportuje ok. **1280×768**, a ekran ma 480×272; współrzędne ekranowe trzeba przeliczyć na surowe (`x/0,375`, `y/0,354`). Pierwsza próba bez przeliczania lądowała w lewym górnym rogu.
- Zwolnienie palca w FT5x06 niesie **ostatnią pozycję** (nie 0,0); inaczej TouchGFX uznaje puszczenie poza przyciskiem i nie wykonuje akcji.

## HARD (wykonanie) — ekrany wyrenderowane przez firmware po dotyku
Atlas (domyślny stan: brak centrali, język PL, poziom dostępu 0), mapowanie ekranowe dotyku → ekran:
| akcja (współrzędne ekranowe) | ekran | plik |
|---|---|---|
| start | Ekran główny | `home.png` |
| tap zegar `(30,40)` | dialog „Ustaw czas” (wybór godzin/minut, OK) | `dialog_ustaw_czas.png` |
| tap kafelek zasobnika `(100,235)` | dialog „Paliwo” (180 kg, +/-, OK) | `dialog_paliwo.png` |
| tap MENU `(34,235)` | **MENU**: Kocioł, Palnik, Ogrzewanie obwód 1, Historia alarmów, Informacje o programie, Konfiguracja, Poziom menu (PIN) | `menu_top.png`, `menu_scrolled.png` |
| MENU → Kocioł | KOCIÓŁ (obraz kotła, wartość `0.0`, `0 AUTO`, harmonogram 0–24, kafelek ustawień) | `kociol.png` |
| MENU → Palnik | PALNIK: `Wyłączony`, spalanie[kg/h]=0.0, moc[kW]=0.0, moc[%]=0, jasność=0, T. palnika=0 | `palnik.png` |
| MENU → Ogrzewanie obwód 1 | OGRZEWANIE 1 (grzejnik, `70`, przycisk off, harmonogram) | `ogrzewanie_1.png` |
| MENU → Historia alarmów | HISTORIA ALARMÓW (lista pusta, przyciski góra/dół) | `historia_alarmow.png` |
- **Zgodność z analizą widoczności wierszy (PASS 21/41):** przy poziomie dostępu 0 firmware zbudował 15 wierszy, ale **widoczne jest 7** — CO2..CO4, CWU, Solar, Buffer itd. są ukryte przez konfigurację (`0x2105 = 1` → tylko Ogrzewanie obwód 1). To wizualne potwierdzenie resolvera możliwości (`FUN_0803C178`, progi `>=1..4`).
- **Etykiety wierszy menu (zamyka OPEN z PASS 40/41):** wiersz „Kocioł” (klasa 0), „Palnik” (klasa 10), „Ogrzewanie obwód 1” (klasy 1..4, instancja 1), „Historia alarmów” (klasa 11), „Informacje o programie” (klasa 13), „Konfiguracja” (klasa 17), „Poziom menu (PIN)” (klasa 15) — czyli kolejność i nazwy z `docs` handoffu 20.11 potwierdzone obrazem.

## OBSERWACJA (OPEN) — kolor tła zależny od stanu
Pierwsze wejście w podekran zmienia tło wypełnień DMA2D z ciemnoszarego `0x2945` (41,40,41) na czerwone `0xF945` (255,40,41) i zostaje czerwone także po powrocie na ekran główny (przedtem czarne `0x0`).
Nie zależy od czasu (kontrola: ekran główny bez dotyku do 6500 tików pozostaje czarny). Hipoteza (INFERENCE): kolor odzwierciedla stan kotła (`Wyłączony`) ustawiany przy wejściu w ekran Kocioł/Palnik; do sprawdzenia przez wstrzyknięcie stanów z CAN.

## Co jeszcze nie jest zrobione
- Ekrany po PIN-ie (poziom 1..3), Konfiguracja, Informacje o programie, Poziom menu (PIN), pozostałe CO/CWU/Solar/Buffer (wymagają zmiany konfiguracji `0x2105..0x2108` przez CAN albo ustawień), dialogi edycji parametrów.
- Ekrany z danymi (wartości z centrali przez `0x584`).
- Zapis atlasu automatycznie (skrypt eksploracji) — narzędzie `ui_session.py` jest gotowe.

## OPEN / następny atak
1. Wstrzyknąć `0x2105..0x2108` (Heating/Hot water/Buffer/Solar configuration) przez `UiSession.set_param` i wyrenderować menu z CO1..CO4, CWU, Buffer, Solar.
2. Wstrzyknąć stan kotła i temperatury (PIDy z macierzy PASS 36) i zobaczyć ekran główny z danymi oraz zmianę koloru tła.
3. Wprowadzić PIN `0900/0999/6154` w ekranie „Poziom menu (PIN)” i wyrenderować wiersze 15..20 oraz ukryte ekrany.
4. Zautomatyzować eksplorację (BFS po tapach) i powiązać `ekran → widżet → zasób → PID` z macierzą PID.
