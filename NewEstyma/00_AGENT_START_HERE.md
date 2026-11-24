# NewEstyma — AGENT START HERE

READ THIS FILE FIRST.

## Mission
Reconstruct the Estyma controller firmware as completely and faithfully as possible (target: 1:1), then use the recovered model as the basis for a universal ESP32-C6 + CAN implementation and integrations.

## Canonical firmware
Filename: FW2213TK_kopia.bin
Size: 0x1F0000 = 2,031,616 bytes
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

Mapping:
PROJECT = 0x08000000 + RAW
RUNTIME/RE_PACK = PROJECT + 0x10000
RAW = RUNTIME - 0x08010000

Important: vtable/function pointers stored in the running image are runtime addresses; translate them to PROJECT before indexing the raw BIN.

RAW BIN is the source of truth.

## Rules
1. Continue autonomously. Do not stop after a fixed number of passes.
2. HARD means a fact is proven; HARD is not 100% project completion.
3. If a tool becomes insufficient, improve or create it and continue.
4. Every meaningful pass gets a report under analiza_archiwum/FW2213TK-2026-11-22/.
5. Update the master state after important closures.
6. Separate FACT, STRONG, INFERENCE, OPEN and REJECTED.
7. Never promote an inference because it looks plausible.
8. Preserve negative results and rejected hypotheses.
9. Do not repeat closed work unless required to close a dependent boundary.
10. Continue until meaningful OPEN space is exhausted or explicitly bounded.

## Current anchors
- CAN2: 0x40006800
- parameter manager: 0x20008D84
- provider: 0x20008D64
- publication sink: 0x20008D60
- manager vtable: 0x080A44F0
- provider vtable runtime address: 0x080A31F0
- provider vtable PROJECT address: 0x080931F0
- provider vtable RAW offset: 0x931F0
- provider slot0 GET: runtime 0x0801DB31 / PROJECT 0x0800DB31
- provider slot1 SET: runtime 0x0801DB79 / PROJECT 0x0800DB79
- manager callback: FUN_08010FCE
- runtime parameter stride: 0x2C
- runtime scan bound: 660
- catalog: 260 entries
- READ: StdId 0x0604, command 0x40
- publication: StdId 0x0584, command 0x42

## Latest scheduler closure
startup -> 0x0800DDC0(0x20008D84,0x20008D64,0x20008D60) -> 0x08014824 -> scheduler registration -> 0x080147C8 -> vtable slot 0 -> FUN_08010FCE

## Latest provider closure
Provider vtable slots 0/1 are now HARD. Slot 0 is GET(PID, output) and slot 1 is SET(PID, value/type). This closure also corrected the runtime-vs-PROJECT address-base interpretation.

## Next targets
1. Recover remaining provider interface slots and persistence semantics.
2. Independently validate scheduler expiry -> FUN_08010FCE at runtime.
3. Build the complete 260-row cross-layer matrix.
4. Close sidecar class 1/2/3 semantics.
5. Continue UI/CAN object graphs.

## Tool workflow
re_scan -> vtable/interface -> object lifecycle -> runtime correlation -> PID matrix -> focused RAW proof -> pass report -> master update

Existing tools:
- tools/re_scan.py
- tools/vtable_scan.py
- tools/runtime_trace_analyzer.py
- tools/test_re_scan.py
- tools/test_re_tools.py

If a repeated manual operation appears, automate it.

## Reading order
1. this file
2. 01_PROJECT_STATE.md
3. 02_WORKFLOW.md
4. 03_TOOLING.md
5. 04_FIRMWARE_MANIFEST.md
6. DOKUMENTACJA/REVERSE_ENGINEERING_MASTER_2026-11-22.md
7. newest pass reports in analiza_archiwum/

Important: 260 catalog != 660 runtime table. Mechanism closure != semantic closure. HARD != 100%.


## PASS 35 — emulator startupu
Do odczytu stanu RAM po inicjalizacji użyj `tools/emu_startup.py` / `boot()` (patrz 03_TOOLING.md). Tabela runtime 655 rekordów jest w `analiza_archiwum/FW2213TK-2026-11-22/data/`. Klucz runtime = PID (z nazwą ASCII w rekordzie).


## STAN NA 2026-11-23 (PASS 35..43) — CZYTAJ TO PIERWSZE
**Metoda pracy zmieniła się:** zamiast tylko czytać kod, wykonujemy firmware. Preferowany emulator: `tools/cortexm_rtos.py` (`Board`, pełny FreeRTOS + LTDC + DMA2D + CAN2), patrz `03_TOOLING.md` sekcje PASS 35/42/43. Firmware: `FW2213TK_kopia.bin` (SHA w tym pliku wyżej; nie ma go w repo — wymagany lokalnie).
Szybki start (kilka sekund): `python3 -I tools/render_screen.py FW2213TK_kopia.bin ekran.png` oraz `python3 -I tools/test_can_boot_trace.py FW2213TK_kopia.bin`.

| PASS | wynik (HARD = wykonane/udowodnione) | raport |
|---|---|---|
| 35 | tabela runtime 655 parametrów (klucz=PID, nazwa z BIN), key 3 = Language, rezolwer UI (2 tabele), PASS 26 ODRZUCONY | AUTONOMOUS-PASS-35 |
| 36 | klasa sidecar = tryb dostępu (0 live, 1 komenda, 2 lustro, 3 nastawa), macierz PID `data/pid_matrix_655.csv` | AUTONOMOUS-PASS-36 |
| 37 | ramka odczytu na szynie `0x604: 40 idx 01`, poller 655 żądań, walidacja min/max na RX `0x584/0x42` | AUTONOMOUS-PASS-37 |
| 38 | lokalna zmiana parametru -> jedna ramka `0x584/0x42` (on-change) | AUTONOMOUS-PASS-38 |
| 39 | class 12 = przełączanie języka (setLanguage), kolejność PL EN LT SK CZ ES RO EST | AUTONOMOUS-PASS-39 |
| 40 | wiersze menu zbudowane w firmware; argumenty row-buildera = ID bitmap | AUTONOMOUS-PASS-40 |
| 41 | dotyk wiersza -> handler 0x0807EB00 -> klasa -> efekt (wiersz 15 = język, wiersze 2..5 = CO1..CO4) | AUTONOMOUS-PASS-41 |
| 42 | **emulacja systemowa; firmware sam rysuje ekran główny** (`data/screen_home_emulated.png`) | AUTONOMOUS-PASS-42 |
| 47 | bramki poziomu dostepu (skan calego firmware: 17x >=3, kumulatywne), eksport 188 bitmap, sledzenie zasobow i PID | AUTONOMOUS-PASS-47 |
| 46 | **poziomy dostepu: listy parametrow ekranow USTAWIEN wg poziomu (FUN_0803E714 wykonana), Konfiguracja od poziomu 1 edytuje 0x2105..0x2108** | AUTONOMOUS-PASS-46 |
| 45 | menu z pelna konfiguracja (CO1..4, CWU, Solary, Bufor), dialog PIN, ekran Konfiguracja -> PID (0x3720, 0x372A, 0x3747, 0x3603, 0x372F) | AUTONOMOUS-PASS-45 |
| 44 | **dotyk FT5x06 + atlas ekranow** (MENU, Kociol, Palnik, Ogrzewanie 1, alarmy, dialogi); przeliczenie wspolrzednych 0.375/0.354 | AUTONOMOUS-PASS-44 |
| 43 | ruch CAN panelu po starcie przy pustej magistrali (heartbeat 0x704, SDO do węzłów 5..7, rodziny PDO-podobne), skan 0x1018, poller włączany z menu | AUTONOMOUS-PASS-43 |

**Najważniejsze otwarte (kolejność):** (1) `tools/ui_session.py`: wyrenderować pozostałe ekrany (CO2..4/CWU/Solar/Buffer po wstrzyknięciu 0x2105..0x2108, PIN, Konfiguracja) jako obrazy (ekran -> widżet -> zasób -> PID); (2) wstrzyknąć odpowiedzi CAN (`0x584`, węzły 5..7 `0x585..0x587`) i obserwować zmianę ekranu;
(3) ustalić, które klasy menu ustawiają bramkę pollera `0x2002466C+0x10/+8`; (4) semantyka ramek PDO-podobnych `0x2xx..0x5xx`; (5) czy skan tożsamości `0x1018:02` jest wywoływany i jakie ID uznaje za centralę.
**Zasady, które kosztowały błędy:** adresy narzędzi = RUNTIME (PROJECT+0x10000); tick ~100000 instrukcji; PendSV po instrukcji zapisu ICSR; wyrównanie ramki wyjątku (STKALIGN); rekordy tabel są wyrównane do bazy (odczyt z przesunięciem 2 B dawał fałszywe pary); pola wartości w rekordzie parametru znaczą tylko szerokość własnego typu.
Pomyłki poprzednich passów są oznaczone `REJECTED/SUPERSEDED` w raportach (m.in. PASS 26, odczyt „tekstów” wierszy menu).


## DECYZJE WLASCICIELA I PROCENTY (2026-11-23)
- **ESP32-C6 i Home Assistant odlozone** do czasu domkniecia reszty rewersu 1:1. Skalowanie grafik na wieksze panele odlozone.
- Szacunek (nie metryka): CAN ~90% · parametry ~92% · PID->CAN ~75% · menu ~88% · poziomy dostepu ~80% · USTAWIENIA/dialogi ~60% · ekran glowny ~65% · grafiki ~95% · wykresy ~50% · narzedzia ~92% · **calosc ~70%**.
- Kolejnosc prac: (1) porownanie pelnych list ustawien 0..3 (`tools/settings_tall.py`); (2) dane na ekranie glownym przez PID-y z trace (`UiSession.enable_trace`); (3) pokrycie zasobow (`tools/resource_coverage.py`); (4) Kaskada/Dod. magazyn, edycja wartosci, wykresy; (5) bramka pollera.
- Uwaga praktyczna: przeciagniecia w dol sa zawodne -> uzywaj punktow kontrolnych (`UiSession.checkpoint/from_checkpoint`) i ruchow w gore; stuknieciom daj hold >= 130 ticków; trace wlaczaj po rozruchu.


## TODO (zlecone przez wlasciciela 2026-11-23) — na SAM KONIEC rewersu, ale PRZED ESP32
### A. PIN i funkcje zalezne od poziomu (domknac PRZED punktem B; wlasciciel nie ma dostepu do kotla — weryfikacja wylacznie emulatorem)
- "Ochrona kotla" (TypedText 87) na ekranach Ogrzewanie L>=1: ustalic warunek wyswietlenia (hipoteza: CH status 0x22FD).
- Bufor L>=1 (klasa 0x08055A8C): "0%" (po lewej zbiornika) i "7°C" (prawy dol) — zrodlo danych/klucze UI/PID.
- Czwarta bramka "poziom!=0" `0x08054AB8` (nie osiagnieta; moze Kaskada/Dod. magazyn) oraz 6 wrapperow bramki >=3 nietrafionych (0x805A9EC, 0x805B1D4, 0x805F400, 0x805FE9C, 0x806125C, 0x8061518).
- Wskaznik `+0x210` w naglowku zalezny od flagi `0x20021FA7` (PID 0x0005): wyglad/znaczenie.
- Bramka pollera `[0x2002466C+0x10]=(poziom!=0)`: weryfikacja skutku.
- Menu glowne `0x0803C294` na poziomie != 0: co dodaje. Naprawa narzedzia: `set_local` nie odswieza cache modelu.
- Tabela 23 liczb `0x20008C50` (flaga jak 6666) — znaczenie; szukanie innych "ukrytych" kodow w polu PIN.
### B. Kod 6666 (reset fabryczny)
- **Kod 6666 = reset ustawien fabrycznych (potwierdzone przez wlasciciela).** W firmwarze: `0x08028634` (wywolywana z handlera PIN `0x0804C21C` PRZED ustawieniem poziomu `0x08047E74`) porownuje wpisana liczbe z 6666 (`movw #0x1a0a` @0x08028668) i ustawia `0x20021FA7` (= storage PID 0x0005 "Default settings request", u8 0..1) na 1; flaga wygasa po 61 tikach (licznik obj+0xE6 @0x08028684). Ten sam obiekt `0x20021FA0`; tabela 23 liczb w RAM `0x20008C50` (10,12,15,18,25,30,35,50,75,120,150,180,220,230,300,500,1220,1300,1550,2000,2500,3000) tez ustawia flage (znaczenie: do zbadania).
  DO ZROBIENIA: (a) w emulatorze wpisac 6666 w ekran PIN i sprawdzic ramke CAN dla PID 0x0005 + reakcje wskaznika naglowka `+0x210`; (b) zaimplementowac w kliencie/ESP32 (NIE testowac na zywym kotle bez weryfikacji — skasuje konfiguracje); (c) szukac innych "ukrytych" kodow wpisywanych w polu PIN (poza 0900/0999/6154/6666).
- Bramka pollera: `0x0804C234..0x0804C24E` zapisuje `[0x2002466C+0x10] = (poziom != 0)` po wpisaniu PINu — zweryfikowac, czy to warunek dzialania pollera.

## UWAGA WLASCICIELA (2026-11-23) — do poprawy w NOWYM UI (po wiernym 1:1 / przy ESP32)
Oryginalny firmware ma prawdopodobnie zamienione tekstury wypelnienia sliderow: slider TEMPERATURY (dialog numeryczny, np. "Temperatura zadana") jest niebieski, a slider USTAWIEN/trybu (okno power, "Woda uzytkowa", "Ogrzewanie") ma kolorowy gradient niebieski->zolty->czerwony.
Zyczenie: gradient (zimno->cieplo) na sliderze temperatury, jednolity niebieski na sliderze ustawien/trybu. W replice 1:1 zachowac oryginal; zmiana tylko w nowym interfejsie. POTWIERDZONE sledzeniem bitmap (emulator): dialog numeryczny (slider temperatury/wartosci) rysuje tlo **163** + wypelnienie **165** (niebieskie, 301x16); okno power (slider trybu) rysuje tlo **186** + wypelnienie **187** (gradient niebieski->zolty->czerwony, 181x11). Podglad: `analiza_archiwum/FW2213TK-2026-11-22/screens/pass52_slider_bitmaps_163_165_186_187.png`. W nowym UI: gradient (187, rozciagniety/przeskalowany) dla sliderow temperatury, niebieski (165) dla slidera trybu.

## TODO (pytanie wlasciciela 2026-11-23) — emulacja "zakazu rozpalenia" w NASZYM projekcie (nie w replice 1:1)
Klodka na kafelku palnika = PID 0x2006 "Burner external permission" == 0 (PASS 53). Emulacja: wysylac ramke 0x584 `42 06 20 01 <0|1> 00 00 00` jako wezel sterownika. Uwaga: to zmienia tylko UI panelu; blokada rozpalania jest po stronie sterownika/modulu BIG.

## TODO (wlasciciel, 2026-11-23) — "programowy zakaz rozpalania" w HA/integracji (etap ESP32/HA)
Cel: kociol zachowuje sie jak przy zakazie rozpalania (nie rozpali, reszta dziala normalnie) BEZ fizycznego rozwarcia wejscia na module CAN BIG. Ustalone: wejscie zezwolenia na BIG (domyslnie zwarte = zgoda; otwarty obwod = zakaz) jest odczytywane przez sterownik, panel tylko wyswietla klodke (PID 0x2006). Sama ramka 0x2006 do panelu NIE blokuje kotla (sterownik czyta wejscie sprzetowe).
Do zbadania: (a) czy sterownik/BIG ma polecenie CAN rownowazne wejsciu (np. przez parametr komendy / inna klasa PID, "Stop burning wood" 0x300B?, "Boiler on/off" 0x2005 + program); (b) rozwiazanie sprzetowe: przekaznik/optoizolator sterowany z ESP32 wpiety w obwod zezwolenia BIG (najpewniejsze); (c) emulacja stanu 0x2006 tylko dla UI. Decyzja po analizie sterownika (poza zakresem panelu).

## TODO (wlasciciel, 2026-11-23) — synchronizacja czasu w NASZYM module (etap ESP32/HA/Android)
Zalozenie: nasz modul (ESP32/sterownik) pobiera godzine po polaczeniu z HA / aplikacja Android / przegladarka (prawdziwy czas z sieci); gdy tego nie ma — synchronizuje sie z kotla. Gdy ma prawdziwa godzine, WYPYCHA ja na kociol (korekta dryfu zegara kotla — wlasciciel zauwazyl niewielkie opoznienie rzedu miesiaca, wina sprzetu RTC).
Do ustalenia w RE (przed wdrozeniem): jak godzina jest ustawiana/odczytywana po CAN (dialog "Ustaw czas" na panelu zapisuje RTC panelu: HAL RTC `0x08028F78`/`0x08028FF8`; panel -> sterownik: czy jest ramka/PID czasu; alarmy uzywaja czasu panelu jako unix UTC `0x08049370`). Zrodlo prawdy zegara = RTC panelu.

### Sprostowanie (tekstury sliderow, po eksploracji UI)
Bitmapy 301x16: tlo 163, wypelnienie niebieskie 165, wypelnienie GRADIENT 167. Bitmapy 181x11: tlo 186, wypelnienie gradient 187 (brak niebieskiego wariantu 181).
Uzycie w oryginale: dialog numeryczny NASTAWY (np. "Temperatura zadana") = 163+165 (niebieski); okno temperatur komfort/eco (Ogrzewanie, Woda) = suwaki z gradientem (163+167); okno power (tryb off/eco/harmonogram/komfort) = 186+187 (gradient). Zyczenie wlasciciela: gradient na KAZDYM sliderze temperatury (takze w dialogu numerycznym dla parametrow temperaturowych), niebieski na sliderze trybu/ustawien (w nowym UI przeskalowac 165 do 181 px).

## STAN NA KONIEC SESJI 2026-11-23 (limit zasobow sesji) — jak kontynuowac
Plan: `NewEstyma/05_PLAN_1TO1.md`. Zrobione w tej sesji: czcionki (A1), teksty 8 jezykow (A4), katalog widgetow `analiza_archiwum/FW2213TK-2026-11-22/WIDGETS-BY-SCREEN-2026-11-23.md`, drzewo menu `MENU-TREE-2026-11-23.md`, specyfikacja poziomow 0/1/2 `SPEC-POZIOMY-DOSTEPU-0-1-2.md`, alarmy PASS 51, ekran glowny/Kaskada/Internet PASS 52-54, kloda zakazu rozpalania PASS 53.
NASTEPNE KROKI (kolejnosc): (1) `UI-MODEL`: polaczyc inwentarz widgetow z mapa prezenterow (`data/presenter_map.csv`) przez `view_off` = this - widok (`tools/ctor_trace.py`; czesciowe wyniki: `data/widgets_home_with_view_off.json`, `widgets_invm2_*_partial.json`; pelny przebieg: `tools/screen_inventory_menu.py FW DIR OUT.json` na stanach z `ui_explore.py --prepare`); (2) graf akcji: dotykanie srodka kazdej kontrolki (nowe narzedzie), skutki = ekran/dialog/ramka CAN/zmiana PID; (3) warunki widocznosci i dialogi jako dane; (4) test akceptacyjny 1:1 (korpus zrzutow + porownywarka); (5) alarmy (wybor biezacego wpisu, dzwiek), formatowanie pol, luki ekranow (PROGRAM edycja, dialog czasu, wykresy).
Uwagi praktyczne: emulator ~2-3 min/ekran, max 3 procesy naraz (4 rdzenie); pliki stanu/scratchpad NIE sa w repo (po restarcie trzeba odtworzyc: `tools/ui_explore.py`, `ui_fuzz.py`).


## STAN NA 2026-11-23 14:40 — PRZEKAZANIE UI DO NOWEGO WATKU (czytaj przed 05_PLAN)
- Pracuja dwa tory: **Claude** (dynamika/emulator + UI, galaz `ccr-be8a1bcb-5t76j0`, raporty PASS 61..69) i **ChatGPT** (statyka, galaz `ccr-be8a1bcb-5t76j0-chatgpt`, PASS 70+, narzedzia `tools/cg_*`). Wymiana: `NewEstyma/COORDINATION.md` na galezi `ccr-be8a1bcb-5t76j0-pin`. Scala galezie tylko Roman.
- UI-MODEL wstrzymany; **zacznij od `NewEstyma/UI_MODEL_LESSONS.md`** (co dziala, co wadliwe, plan pilota PID-diff na ekranie Kociol z kryteriami K1-K5).
- Domkniete dzis: zegar panelu z CAN (PASS 62: `0x584 42 65 21 01 <unix LE>` + 0x372F=1 -> RTC, bez strefy czasowej); tabela 23 w RAM (brakujaca wartosc 16).
- Srodowisko: `pip install unicorn capstone pillow numpy`; firmware od Romana jako zalacznik, SHA-256 jak wyzej, kopiowac do katalogu repo i dopisac do `.git/info/exclude` (nie commitowac). Testy `tools/test_*.py` uruchamiac z katalogu `tools/`.
