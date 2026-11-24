# POLECENIE DLA CHATGPT — tor UI (statyka + emulator) — wersja 2026-11-23 (autor: Claude, na zlecenie Romana)

Pisz po polsku. Właściciel: Roman. Cel: UI panelu Estyma igneoTouch (FW2213TK) opisany **danymi** tak, by dało się go później odtworzyć (karty Home Assistant, WWW, Android). Model danych i pełna lista zadań: `NewEstyma/TODO_UI_RECONSTRUCTION.md` (sekcja 0 i C). Czytaj ją najpierw.

## 1. GAŁĘZIE I WYMIANA (git jako jedyny kanał)
- Repo `GieOeRZet/TeklaPelletCAN`. Twoja gałąź: `ccr-be8a1bcb-5t76j0-chatgpt` (pliki `tools/cg_*`, `tools/test_cg_*`, `analiza/FW2213TK-2026-11-22/data/cg_*.csv`, raporty PASS 135+).
- Gałąź Claude (narzędzia emulatora, pomiary, surowe listingi): `ccr-be8a1bcb-5t76j0` — **tylko czytaj i uruchamiaj**.
- **Wymiana wyłącznie przez `NewEstyma/COORDINATION.md` na gałęzi `ccr-be8a1bcb-5t76j0-pin`.** Przed każdym wpisem `git pull --rebase`, wpis na dole z datą i podpisem, push. NIE prowadź własnej kopii COORDINATION na innych gałęziach.
- Commit i push po każdym zadaniu. Bez PR-ów. Scala tylko Roman.

## 2. ŚRODOWISKO I EMULATOR
Firmware `FW2213TK_kopia.bin` (2 031 616 B, SHA-256 `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`) skopiuj do katalogu repo i dopisz do `.git/info/exclude`. **Nie commituj.**
```
pip install unicorn capstone pillow numpy
git fetch origin ccr-be8a1bcb-5t76j0 && git checkout -b cg-ui origin/ccr-be8a1bcb-5t76j0     # tylko do uruchamiania narzędzi Claude
time python3 -I tools/render_screen.py FW2213TK_kopia.bin /tmp/home.png                         # test dymny ~10 s: „ekran 480x272 ... DMA2D operacji 1352”
mkdir -p /tmp/w/L0 && python3 -I tools/ui_explore.py FW2213TK_kopia.bin /tmp/w/L0 --level 0 --prepare   # ~80 s: menu.state, rows.pkl
python3 -I tools/pid_diff.py FW2213TK_kopia.bin /tmp/w/L0 analiza/FW2213TK-2026-11-22/data/widgets_inv_pass61_L0.json 6_screen /tmp/w/woda --phase all   # Woda ~50 s, kończy się „DONE”
python3 -I tools/pid_diff_report.py /tmp/w/woda.md /tmp/w/woda.csv FW2213TK_kopia.bin /tmp/w/woda.json
python3 -I tools/dump_listing.py FW2213TK_kopia.bin OUT 0xADRES:0xDLUGOSC                       # surowy listing Thumb (adresy PROJECT; RUNTIME = PROJECT+0x10000)
```
Testy `tools/test_*.py` uruchamiaj z katalogu `tools/`. Kontener: 4 rdzenie → **maks. 3 procesy emulatora naraz**; wyniki zapisuj przyrostowo (wznawialnie), loguj czas.
Narzędzia Claude (importuj, nie edytuj): `ui_session.py` (UiSession: wait, tap, shot, inject_param, set_local, set_access, checkpoint), `action_probe.py` (stuknięcia, tożsamość ekranu = vtable `[[0x20024818]]`), `pid_diff.py` (wiązania widżet→PID metodą różnicową), `ui_explore.py`, `cortexm_rtos.py`, `dump_listing.py`. Jeśli narzędzie wymaga poprawki — wpis w COORDINATION, poprawi Claude.
**Przed pierwszym użyciem emulatora:** wykonaj powyższy test i odpowiedz w COORDINATION („RAPORT SRODOWISKA”: system, nproc, python, wersje unicorn/capstone, SHA-256, czasy, czy procesy w tle przeżywają, czy git push działa). Jeśli któryś krok się nie uda — wklej dokładny błąd, nie obchodź go; wtedy robisz tylko statykę (zadania C), a pomiary robi Claude.

## 3. DANE Z PRAWDZIWEGO KOTŁA (Home Assistant) — tylko WSKAZÓWKA, nie źródło prawdy
Roman ma ESP32 z integracją HA (`custom_components/teklapelletcan`). **Integracja powstała ze skanowania rejestrów CAN i ręcznego porównywania „co jest, a czego nie ma”.** Nazwy i mapowania w niej zwykle zgadzają się z rejestrem i angielską nazwą parametru, ale to **nie jest dowód z firmware** — nie opieraj na niej żadnego wiązania, formatu ani warunku.
- Źródłem prawdy są: firmware (listingi, tabele), emulator (pomiar), katalog 655 parametrów z panelu. Dane z HA/ESP mają status **INFERENCE** i służą wyłącznie do sprawdzenia „czy wartość w emulatorze jest rzędu wielkości jak w prawdziwym kotle”.
- **Nie masz dostępu do Home Assistanta ani do ESP32 i nie planuj pracy z nimi.** Dostęp (tylko odczyt) ma Claude. Potrzebujesz konkretnej wartości lub logu z prawdziwego kotła? Wpis w COORDINATION: PID/zakres, oczekiwana obserwacja, po co — Claude odczyta i odpisze (jako INFERENCE).
- **Zakaz sterowania kotłem obowiązuje wszystkich agentów, także Claude: tylko odczyt.**
- **NIE zapisuj niczego do prawdziwego kotła** i nie proponuj zapisów (`sdo_write`, przyciski dmuchawy/podajnika/restartu, zmiana trybów) bez wyraźnej zgody Romana. Skanowanie zakresów tylko odczytowo i tylko na polecenie Romana.

## 4. ZADANIA (kolejność C1…C10 z TODO; po każdym commit + wpis)
C1 akcje przycisków (klasa ekranu → offset widżetu → handler → efekt: nawigacja / zapis PID / dialog / CAN); C2 warunki widoczności i dostępności widżetów (PID/poziom/konfiguracja → vis/touch/bitmapa); C3 PID-y czytane na każdym ekranie (klucze UI→T1/T2→PID→format); C4 format wyświetlania każdego PID (format, skala, jednostka, 5678=brak danych, wyliczenia); C5 struktura menu i warunki wierszy (poziom, konfiguracja 0x2105/0x350C/0x3525…) + listy NASTAWY z metadanymi PID; C6 brakujące ekrany (PROGRAM, dialog czasu, Statystyki, wykresy); C7 dialogi (PIN, Paliwo, Ustaw czas, edycja wartości, tryby zasilania, AUTO, potwierdzenia, błędy); C8 alarmy (per-alarm warunki, teksty 8 języków, prezentacja, ACK); C9 źródło LIVE (tabele kanałów modułów CAN IO, obiekty czujników → PID, konwersja `[r5+6]`); C10 mapowanie TypedText → widżet/ekran.
Wejście: surowe listingi w `analiza/FW2213TK-2026-11-22/data/raw_listings/`, T1/T2, `presenter_map.csv`, pomiary Claude (`data/pass63_pilot_kociol/BINDINGS_L0_pilot.md/.csv`, `data/pass63_view_classes.json`, `AUTONOMOUS-PASS-63/64`).
Jeśli emulator działa (sekcja 2): po C1–C3 przejmij pomiar T1 (delty poziomów/konfiguracji, klasy Solary/Bufor/Alarmy/Info/Test wyjść/Sieć/Internet, Kaskada i Magazyn) wg wpisu w COORDINATION; przed długim przebiegiem **podaj Romanowi szacowany czas**.

## 5. JAK PRACOWAĆ
- Fakty: **FACT** (zmierzone w emulatorze lub źródłowo odczytane), **STRONG**, **INFERENCE**, **OPEN**, **REJECTED**. Nie awansuj hipotezy bez dowodu. Odrzucone hipotezy zachowuj.
- Każdy wynik statyczny **porównaj z pomiarem Claude**; rozbieżność zapisz jawnie (nie wygładzaj). Wcześniejsze pomyłki do uniknięcia: węzły SDO 5/6/7 to kaskada (nie czujniki kotła); bitmapa 138 wiązana przez 0x22A1, nie 0x2277; geometria/ID bitmapy nie jest dowodem wiązania.
- Pilot przed skalą: nowe narzędzie najpierw na JEDNYM ekranie, uruchom dwa razy i porównaj (determinizm), dopiero potem skala.
- Wyniki: CSV + raport PASS 135+ (FACT/STRONG/INFERENCE/OPEN/REJECTED), test jednostkowy `tools/test_cg_*.py`.
- Raportuj krótko po każdym temacie: co zrobione, FACT/OPEN, co dalej.

## 6. CZEGO NIE ROBIĆ
- Nie zaczynaj własnych targetów spoza C1–C10 (parameter engine, provider, publikacja — wstrzymane do końca listy C).
- Nie edytuj plików Claude: `tools/pid_diff*.py`, `ui_session.py`, `action_probe.py`, `cortexm_rtos.py`, `ui_explore.py`, `dump_listing.py`, `NewEstyma/00..05`.
- **Nie używaj `tools/presenter_trace.py` ani statycznego `view_off` jako źródła faktów** (zawodne: PASS 59/61).
- **Nie dodawaj haków Unicorn w callbackach** (wywraca emulator); jedyny dopuszczalny hak to odczyt PID w fazie „cands” narzędzia `pid_diff.py`.
- Nie uruchamiaj pełnego przebiegu nieprzetestowanego narzędzia; nie więcej niż 3 procesy emulatora naraz.
- Nie commituj firmware ani plików powyżej limitu GitHuba; nie używaj `git clean`/`reset --hard`/force-push.
- Nie zapisuj do prawdziwego kotła (sekcja 3). Nie wykonuj ESP32/HA/Android/skalowania grafik — odłożone.
