# ETAP 3 — ChatGPT — 2026-11-24

## Status

Branch: `ccr-be8a1bcb-5t76j0-chatgpt-etap3`  
Firmware SHA: `1d679d6810cfb44a4c1d862d67552b7220f3edb3a2807f3067d46185d0c5071`

Obowiązująca metodyka: `NewEstyma/METODYKA_EMULATOR.md`.

## A — macierz pokrycia wyglądu

Dodano:

- `tools/coverage_matrix.py`
- `analiza_archiwum/FW2213TK-2026-11-24/data/ui_model/coverage_matrix.json`

Narzędzie bierze wyłącznie dane istniejące w repo:

- `menu_tree.json` — 30 węzłów, poziomy 0..3 i rzeczywiste warianty `visible_in`,
- `atlas/*.png`,
- `render_eval.csv`.

Macierz jest konserwatywna: **nie przypisuje jednego zrzutu do alarmu/offline/dialogu jako dowodu tych stanów**. Zrzut z atlasu może potwierdzać tylko stan domyślny, dopóki nie ma osobnego dowodu stanu.

### Wynik baseline

| Stan | Komórki | Zrzut | render_eval |
|---|---:|---:|---:|
| default | 350 | 133 | 133 |
| alarm | 350 | 0 | 0 |
| module_offline | 350 | 0 | 0 |
| dialog | 70 | 0 | 0 |
| **razem** | **1120** | **133** | **133** |

Przy progu `pct_diff < 5%`:

- 95/133 ocenionych zrzutów spełnia próg = **71,43%**,
- 133/1120 wszystkich komórek ma jakikolwiek istniejący zrzut = **11,88%**,
- 95/1120 wszystkich komórek spełnia próg = **8,48%**.

**To nie jest procent „jak dobrze wygląda panel”.** To jest rygorystyczne pokrycie macierzy wariantów. Wynik pokazuje przede wszystkim, że obecne repo nie posiada jeszcze osobnych dowodów dla alarm/offline/dialog i części konfiguracji. Nie wolno tego mieszać z wcześniejszą oceną statycznego wyglądu znanych ekranów.

Brakujące komórki pozostają `OPEN`; nie wygenerowano fałszywych zrzutów.

## B — KASKADA / MAGAZYN

Sprawdziłem dostępność istniejących narzędzi:

- `tools/list_scale.py`
- `tools/list_switch.py`
- `tools/list_scales_build.py`

Istnieją i są przygotowane do pomiaru emulatorowego.

W aktualnym checkout/runtime nie ma jednak reprodukowalnego checkpointu `menu.state + rows.pkl` dla KASKADA/MAGAZYN. W `/mnt/data` nie ma żadnego pliku `*.state` ani `rows.pkl`; lokalny katalog repo runtime `/mnt/data/teklacore` również nie istnieje.

Dlatego **nie oznaczam B jako wykonane** i nie wpisuję zmyślonych wyników.

Znane statycznie:
- KASKADA wymaga `0x350C != 0`,
- MAGAZYN wymaga `0x3525 != 0`,
- `list_scales.json` nadal jawnie pozostawia oba ekrany jako niezmierzone.

## C — SIEĆ / INFO / INTERNET

### SIEĆ

Na podstawie zweryfikowanego przebiegu emulatorowego Claude'a:

- `0x57` **pojawia się**, jako `CAN IO BIG Node ID=87`, ale bez kolumny `SW`.
- `0x5B` **pojawia się**, jako `VIDE NET WIFI Node ID=91 SW v0.0`.
- kolejność wielu modułów jest zgodna z sortowaniem po Node-ID / limitem 8.
- dla `0x45`: czwarta kolumna to temperatura wewnętrzna; `5678` oznacza brak danych.
- przy **1500 tikach bez ramek** wpis pozostaje.
- dostępny lokalnie dodatkowy zrzut przy **10000 tikach** również pokazuje wpis nadal obecny.

Wniosek: **nie znaleziono timeoutu offline do 10000 tików**. Nie wolno z tego robić „brak timeoutu kiedykolwiek”; dokładny próg ewentualnego timeoutu pozostaje `OPEN`.

### SW

Rozbieżność `v52.1c` vs `v52.18` została rozstrzygnięta na korzyść:

**`SW v52.18`**

W zweryfikowanym przebiegu po 10 rundach stabilizacji użyto bajtów PDO1 `34 12`:

- `0x34 = 52`,
- `0x12 = 18`.

`v52.1c` pochodziło z wcześniejszego, niedostatecznie ustabilizowanego uśredniania 8 próbek.

### INFO

Twarde/static:

- `0x3665` jest nazwanym parametrem firmware **igneTouch boiler short name**, RAM `0x20008D4C`; snapshot `0x54450000` = `TE\0\0`.
- firmware zawiera literal `Bio Compact 10kW` oraz inne nazwy modeli.
- widget INFO dla nazwy kotła używa TypedText/wildcard ID 492; zrzut pokazuje `Bio Compact 10kW`.
- `0x2170` jest parametrem **VideRoom PIN**, ale zapis przez obecny kanał emulatorowy jest odrzucany (`stored=0`).

Dynamiczne próby `0x3664/0x3665/0x2170` nie zmieniły ciała INFO. Dlatego:

- źródło wyświetlanej nazwy `Bio Compact 10kW` jako runtime producer pozostaje `OPEN`,
- źródło wartości `videRoom PIN 0` pozostaje `OPEN`,
- nie przypisuję arbitralnie 0x3665 ani 0x2170 jako źródła wildcarda tylko dlatego, że nazwy pasują.

### INTERNET

Z istniejącego pomiaru PID-diff dla `18_screen`:

- `0x373F` → widget tekstowy `SERIAL:`, dynamicznie zmieniający się wraz z wartością,
- `0x3740` → widget tekstowy `PIN:`, dynamicznie zmieniający się wraz z wartością,
- `0x373E` → status WiFi,
- `0x3741` → Zmiany zdalne.

To jest wystarczające do zamknięcia samego **SERIAL/PIN widget → PID**. Nadal otwarte są m.in. pełna ścieżka źródła `0x5B`, persystencja i pełna obsługa edytora PASSWORD.

## Klasyfikacja

### FACT-DYNAMIC
- SIEĆ: 0x57 jest widoczny bez SW.
- SIEĆ: 0x5B jest widoczny.
- SIEĆ: wpis pozostaje po 1500 tikach; dodatkowy lokalny zrzut pokazuje go również przy 10000.
- SW: ustabilizowane `v52.18`.
- INTERNET: SERIAL/PIN są związane z `0x373F/0x3740` w istniejącym pomiarze PID-diff.

### FACT-STATIC
- 0x3665 = `igneTouch boiler short name`.
- 0x2170 = `VideRoom PIN`.
- `Bio Compact 10kW` jest literalem firmware.
- KASKADA = gate 0x350C; MAGAZYN = gate 0x3525.

### OPEN
- dokładny timeout offline SIEĆ >10000 tików,
- runtime producer nazwy kotła INFO,
- runtime producer videRoom PIN INFO,
- pełna korelacja 0x5B → INTERNET,
- pełna persystencja/obsługa PASSWORD,
- pełne list_scale/list_switch dla KASKADA/MAGAZYN.

## Ważne

Nie zmieniałem renderera ani plików pomiarowych agenta UI. Nie promowałem żadnego wyniku negatywnego do „never”.

