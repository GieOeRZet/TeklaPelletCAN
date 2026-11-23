# TODO — kompletny UI panelu Estyma igneoTouch (rewers 1:1 i odtwarzalność) — stan 2026-11-23, autor: Claude

CEL NADRZĘDNY (Roman): mieć UI w pełni opisany **danymi**, tak aby później dało się odtworzyć interfejs (ekrany, widżety, zależności, akcje) w innej technologii (karty Home Assistant, WWW, Android). Każdy fakt: **FACT** (zmierzony w emulatorze / źródłowo odczytany), **STRONG**, **INFERENCE**, **OPEN**, **REJECTED**.
WYMIANA: tylko przez git. Pliki wspólne leżą na gałęzi **`ccr-be8a1bcb-5t76j0-pin`** (`NewEstyma/COORDINATION.md`, ten plik). Każdy agent **najpierw czyta, potem pisze** i dopisuje na dole z datą i podpisem. Nie tworzyć własnych kopii COORDINATION na innych gałęziach. Scala tylko Roman.

## 0. Docelowy model danych (to ma powstać; wszystko poniżej do tego zmierza)
```
ui_model/
  menu_tree.json        węzły = klasy ekranów (vtable), krawędzie = wiersz menu / przycisk, warunki = poziom dostępu 0..3, konfiguracja (PID=wartość)
  screens/<klasa>.json  widżety: pozycja, rola, zasób (bitmapa/TypedText), binding (PID, format, skala, jednostka, wartość 5678 = brak danych),
                        reguły (wartość -> vis / bitmapa / tekst / rect), akcje (dotyk -> handler -> efekt: nawigacja | zapis PID | dialog | CAN)
  dialogs.json          PIN, Paliwo, Ustaw czas, edycja wartości, tryby zasilania, AUTO (komfort/eco), potwierdzenia i błędy
  lists.json            wiersze NASTAWY / Konfiguracja / Statystyki wg poziomu: PID, nazwa, typ, min/max/krok, jednostka, format, dialog edycji
  alarms.json           kody, teksty 8 języków, warunki ustawienia/skasowania, prezentacja, ACK
  live_sources.json     PID live -> moduł CAN (węzeł) -> PDO -> kanał -> konwersja (do symulacji i do HA)
```
Test akceptacyjny 1:1: renderer z `ui_model/` + wartości PID daje zrzut zgodny z zrzutem emulatora (różnica pikseli poniżej progu) dla każdego ekranu/stanu.

## 1. STAN — co zamknięte (FACT, nie powtarzać)
- Emulator panelu, 655 parametrów, protokół CAN 0x584/0x604, menu, poziomy 0/1/2, 188 bitmap, czcionki, teksty 8 języków. PIN 900/999/6154 (poziomy 1/2/3), 1992/6666 specjalne. Zegar z CAN (0x2165 + 0x372F). Tabela 23 (23 wartości, ostatnia 1300 wg ChatGPT PASS 94; Claude zmierzył 16 na 15. miejscu — do uzgodnienia, patrz D3).
- Klasy ekranów po vtable: 12 (`data/pass63_view_classes.json`). Wszystkie NASTAWY = jedna klasa LISTA 0x808f944.
- Tabele klucz UI→PID: T1 49 (PID=value+inst−1), T2 372 (PID=value), bez wspólnych kluczy (ChatGPT PASS 107–109).
- Pomiar PID-diff: Kocioł, Palnik, Ogrzewanie 1, Woda (poziom 0): 45 wiązań + 2 nowe (niżej) — `data/pass63_pilot_kociol/BINDINGS_L0_pilot.md/.csv`.
- **NOWE (Claude, zmierzone, poprawione próbkowanie):** `0x22A1` (Room temp sensor type 0..5, Ogrzewanie 1): wartość 4 → obraz bmp 177/178 (255,70) widoczny, teksty (357,60) i (235,52) ukryte; wartość 0 → teksty ukryte; 1/2/3/5 → teksty widoczne; 5 → ikona (9,239) bmp 138 ukryta. Warunek ŁĄCZNY: typ=4 i `0x2301` (CH thermostat state) 0 → widget 0x20016aa8 (bmp 178), 1 → widget 0x20016a7c (bmp 177). To jest A69/A95 z PASS 83 (ChatGPT) — twardo zmierzone.
- Źródło LIVE (PASS 64): moduły CAN IO, PDO 0x180/0x280/0x380/0x480+node, watchdog 300 cykli; mapowanie kanał→PID w toku.

## 2. KOREKTY po weryfikacji pracy ChatGPT (2026-11-23)
- ChatGPT prowadził **własną kopię COORDINATION.md na swojej gałęzi** (423 linie) i nie czytał wpisów Claude na `-pin` (T1, raport środowiska, S10). Od teraz jeden plik na `-pin`.
- Pass 123–134 (parameter engine, provider, publikacja, extra TX callers) **nie służą odtworzeniu UI** — wartościowe jako dokumentacja, ale **wstrzymać** do czasu zakończenia sekcji C.
- PASS 113 (widget „Ochrona kotła” 0x200177ec, view_off 6068, text_id 30) — **POTWIERDZONE** u Claude (ten sam widget w inwentarzu). PASS 121 (7°C = klucz 0xCB → PID 0x22F5) — spójne (0x22F5 klasa live, nie wstrzykiwalny 0x584).
- PASS 95 (S9: węzły 5/6/7 jako źródło live kotła) — **błędne**: to SLAVE 1..3 kaskady (korekta w PASS 64).
- ChatGPT zgłosił brak surowych listingów (PASS 120/122): **Claude dodał** `data/raw_listings/` (0x08048468, 0x0804858A, 0x08054848, 0x08056028, 0x08056040, 0x08056A1C/44, 0x08054AB8) + `tools/dump_listing.py` (na gałęzi `ccr-be8a1bcb-5t76j0`). Dowolny adres: `python3 -I tools/dump_listing.py FW2213TK_kopia.bin OUTDIR 0xADRES:0xDLUGOSC`.

NOTA (Roman, 2026-11-23): integracja HA/ESP powstała ze skanowania rejestrów CAN i ręcznego dopasowania; nazwy zwykle zgadzają się z rejestrem, ale to NIE jest źródło prawdy — dane z HA mają status INFERENCE (tylko kontrola rzędu wielkości). Prawda = firmware + emulator + katalog 655 parametrów.

## A. ZADANIA ROMANA (żeby nie umknęły)
- A1. Powiedz ChatGPT: czytać `-pin` (ten plik + COORDINATION) i **wykonywać wyłącznie sekcję C po kolei**. Wklej mu prompt z końca tego pliku.
- A2. Potwierdź, czy ChatGPT **faktycznie uruchamia emulator** (raport środowiska w COORDINATION, wpis „RAPORT SRODOWISKA”). Jeśli tak → przejmuje pomiar T1 (sekcja C-E); jeśli nie → T1 robi Claude.
- A3. **Nagrania z prawdziwego panelu/kotła (najcenniejsze, jeśli możesz):** (a) log CAN z magistrali przy pracującym panelu (candump/ESP/analizator) ≥ 2 min — ramki PDO modułów (0x1xx/0x2xx/0x3xx/0x4xx), 0x584, 0x604 — przyspieszy to źródło LIVE i weryfikację; (b) zrzuty/zdjęcia prawdziwych ekranów z żywymi wartościami (Kocioł, Palnik, CO1, CWU, ekran główny) i nagranie wideo przejść między ekranami.
- A4. Decyzje zakresu: czy odtwarzamy poziom 3 (PIN 6154) i Kaskadę/Magazyn paliwa w pierwszej wersji; czy wykresy/statystyki są w zakresie 1:1; które języki (8 wszystkie?).
- A5. Scalanie gałęzi (`ccr-be8a1bcb-5t76j0`, `-pin`, `-chatgpt`) — tylko Ty.
- A6. Zdecyduj, czy ChatGPT ma po sekcji C wrócić do parameter engine / provider (dokumentacja), czy robić dalej UI.

## B. ZADANIA CLAUDE (emulator, dynamika) — kolejność
- B1. **Źródło LIVE** (symulator modułów CAN IO): zrzut tabel kanałów obiektów modułów i obiektów czujników, mapowanie kanał→PID dla 0x2001, 0x2277, 0x3333, 0x4000, 0x3628, 0x2007, 0x2120… → `live_sources.json`; potem pomiar wiązań live.
- B2. PID-diff pozostałych klas: Solary, Bufor, Alarmy, Info, Test wyjść, Sieć, Internet; CO2–CO4 (instancje); Kaskada i Magazyn (odsłonięcie `0x350C`, `0x3525`); poziomy 1 i 3; ekran główny. (Jeśli ChatGPT nie uruchamia emulatora — także warianty konfiguracji i delty poziomów = zadanie T1.)
- B3. Graf akcji: stuknięcia we **wszystkie** dotykowe widżety wszystkich klas (dziś 232 stuknięcia, 6/24 węzłów L0) → efekt (nawigacja/PID/CAN/dialog).
- B4. Dialogi jako dane: otwarcie, widżety, wiązania, zapis (ramki TX) — PIN, Paliwo, Ustaw czas, edycja wartości, tryby zasilania, AUTO.
- B5. Brakujące ekrany: PROGRAM (harmonogram), dialog czasu, wykresy/statystyki — wejście, inwentarz, wiązania.
- B6. Renderer „UI z danych” + test akceptacyjny 1:1 (różnica pikseli).
- B7. (niski priorytet, kolejka ChatGPT) B1/B2 z listy ChatGPT: 6666→PID 0x0005 i `+0x210`; bramka pollera `[0x2002466C+0x10]`; A3: dialog „Ustaw czas”→RTC + ramki TX; przełączenie 0x372F; zgodność 23. wartości tabeli 0x20008C50 (Claude 16 vs ChatGPT 1300).
- Zasady: pilot→skala, czas podawać Romanowi przed długim przebiegiem, maks. 3 procesy emulatora, bez haków Unicorn w callbackach, probkowanie: małe zakresy (≤8 wartości) wszystkie, pary warunkowe wstrzykiwać łącznie.

## C. ZADANIA CHATGPT (statyka) — wykonuj po kolei, po każdym commit + wpis w COORDINATION (na `-pin`)
Wejście: surowe listingi `data/raw_listings/` i `tools/dump_listing.py` (gałąź Claude), tabele T1/T2, presenter_map, pomiary Claude (`BINDINGS_L0_pilot.csv`, `pass63_view_classes.json`). Wynik: CSV w `analiza/FW2213TK-2026-11-22/data/cg_*.csv` + raport PASS 135+ (FACT/STRONG/INFERENCE/OPEN/REJECTED). Każdy wynik porównaj z pomiarem Claude; rozbieżności oznacz jawnie.
- C1. **Akcje przycisków (S3 domknięcie):** dla każdej klasy ekranu (12 + home) lista (offset widżetu, handler, efekt: nawigacja do klasy X / zapis PID / dialog / CAN) — z rejestrów `+0x3B4+i*0x274`, `FUN_0807EB00/EB36`, entry `0x08048493`, `0x080485A1` (listingi są w repo). `cg_actions_<klasa>.csv`.
- C2. **Warunki widoczności i dostępności (S4):** dla każdej klasy: widżet (offset) → warunek (PID/poziom/konfiguracja) → efekt (vis/touch/bitmapa) z kodu prezenterów; wzorzec: `0x08054848` (A69/A95), `0x08056028/40`. Weryfikuj z `BINDINGS_L0_pilot.csv` + nowe wiązanie 0x22A1/0x2301. `cg_visibility_rules.csv`.
- C3. **Lista PID-ów czytanych na każdym ekranie** (statyczny odpowiednik moich „kandydatów”): ekran→klucze UI→PID (T1/T2)→format. Porównaj z moimi (Kocioł: 0x2001,0x2002,0x2004,0x2005,0x216A,0x216F,0x2277,0x3333,0x350A,0x350D,0x3628,0x3629,0x370A,0x4000). `cg_screen_pids.csv`.
- C4. **Format wyświetlania każdego PID** (S5 → komplet 655 gdzie ustalalne): format, skala/dzielnik, jednostka, 5678 = brak danych, znak, zaokrąglenie, tekst dla wartości wyliczeniowych (np. typ czujnika, tryb). `cg_pid_display_format.csv`.
- C5. **Struktura menu i warunki wierszy:** z `FUN_0803E714`/`FUN_0804E714`: każdy wiersz menu → warunek (poziom, konfiguracja: 0x2105.., 0x350C, 0x3525, …) → klasa docelowa; oraz listy NASTAWY/Konfiguracja/Statystyki wg poziomu połączone z metadanymi PID (min/max/krok/jednostka/format/typ dialogu). `cg_menu_conditions.csv`, `cg_lists_full.csv`.
- C6. **Brakujące ekrany statycznie (S7):** PROGRAM (harmonogram: 7 dni × 0–24 h, bitmapa slotów 0x2126/0x2154…), dialog czasu, Statystyki 0x11, wykresy: klasa/vtable, konstruktor, widżety, kontrolki, skąd otwierane, jakie PID.
- C7. **Dialogi (S8):** katalog wszystkich okien (PIN, Paliwo, Ustaw czas, edycja wartości, tryby zasilania, AUTO, potwierdzenia, błędy): warunek otwarcia, przyciski, efekt, zapisywany PID, ramka TX.
- C8. **Alarmy (S6):** per-alarm warunki ustawienia/skasowania (caller/context trace dla asymetrii z PASS 110: clear-only 7,43,53,115,250; raise-only 131,139,140,150,160,161), teksty 8 języków, prezentacja (ikona 162, ekran Alarmy, ACK).
- C9. **S10 (źródło LIVE):** tabela kanałów obiektu modułu (`+0x28`, stride 0x24, 19 wpisów), lista obiektów czujników (`[obj+0x18]`=moduł, `[obj+0x1C]`=kanał, `[obj+0x20]`=brama) i ich PID, znaczenie `[r5+6]` w `0x0801EBC4`, zakres ważności raw (`raw−0x33 < 0xF6D`).
- C10. **Mapowanie lokalizacji tekstów:** TypedText (8 języków) → widżet/ekran (z presenterów), żeby dało się zbudować UI wielojęzyczny.
- ZAKAZ: nie rozpoczynać własnych targetów spoza C1–C10; nie edytować plików Claude (`tools/pid_diff*.py`, `ui_session.py`, `action_probe.py`, `cortexm_rtos.py`); nie commitować firmware.
- Jeśli potrafisz uruchamiać emulator (patrz A2): po C1–C3 przejmij **T1** (pomiar delt poziomów/konfiguracji wg wpisu w COORDINATION).

## D. OTWARTE ROZBIEŻNOŚCI (do rozstrzygnięcia)
- D1. Bitmapa 138: wiązana przez 0x22A1 (zmierzone) — NIE przez 0x2277 (REJECTED; pompa = animacja klatek 138→142).
- D2. 0x370A 1/2/3 → bitmapa widżetu 11/12/13 (zmierzone, 3 zrzuty) vs „REJECTED” w handoffie ChatGPT (prawdopodobnie odrzucono „bitmap ID = widget ID”; do potwierdzenia).
- D3. Tabela 23: 23. wartość 1300 (ChatGPT PASS 94, kolejność [wsk+8]) vs 16 jako 15. wpis (Claude, RAM) — to ta sama lista w innej kolejności; zostawić jedną kolejność źródłową.
- D4. 0x2114 / pole „7°C” Bufora vs 0x22F5 w Ogrzewaniu — rozdzielone (PASS 121).

## PROMPT DLA CHATGPT (do wklejenia)
Przeczytaj na gałęzi `ccr-be8a1bcb-5t76j0-pin` pliki `NewEstyma/TODO_UI_RECONSTRUCTION.md` i `NewEstyma/COORDINATION.md` (od wpisu „Claude -> ChatGPT: kolejka zadań”). Pobierz też gałąź `ccr-be8a1bcb-5t76j0` (surowe listingi w `analiza/FW2213TK-2026-11-22/data/raw_listings/`, pomiary Claude w `data/pass63_pilot_kociol/`). Wykonuj WYŁĄCZNIE sekcję C (C1…C10) po kolei, bez własnych targetów. Cel nadrzędny: UI opisany danymi tak, by dało się go później odtworzyć (model w sekcji 0). Każdy wynik porównuj z pomiarami Claude i jawnie oznaczaj rozbieżności. Piszesz tylko na `-pin` (COORDINATION) i na swojej gałęzi (`cg_*`); po każdym zadaniu commit + wpis z datą. Najpierw odpowiedz w COORDINATION na „RAPORT SRODOWISKA” (czy uruchamiasz emulator).
