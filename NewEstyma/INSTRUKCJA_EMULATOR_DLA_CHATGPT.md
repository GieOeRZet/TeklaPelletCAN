# Instrukcja pracy z emulatorem dla ChatGPT (zgodna z metodą agenta UI / Claude, stan 2026-11-24)

Cel: każdy wynik "dynamiczny" ma powstać tak samo jak u mnie: realny firmware → emulator → akcja → pomiar → powtórzenie → dane w repo. Binarka jest jedynym źródłem prawdy. Wspomnienia właściciela i integracja HA to tylko podpowiedź (INFERENCE).

## 0. Zakazy (twarde)
- Nigdy nie commituj `FW2213TK_kopia.bin` ani pełnego listingu/dezasemblacji firmware (tylko małe listingi na żądanie: `tools/dump_listing.py`).
- Zero sterowania prawdziwym kotłem: nie używaj HA (usługi, przyciski), `sdo_write`, `sdo_scan`. Emulator jest odizolowany - wszystko co wstrzykujesz leci tylko do emulatora.
- Nie ruszaj tematów kodów PIN, tabeli 23 i RTC (tematy właściciela). Zapis 0x2170 emulator i tak odrzuca.
- Maks. 3 procesy emulatora jednocześnie. Przed długim przebiegiem podaj czas (pilot na 1-2 przypadkach, potem skala).
- Nie dodawaj haków Unicorn (`mu.hook_add`) w trakcie działania ani na zakresy pamięci RAM (hak MEM_WRITE na rekordy PID wywala emulator: PC=0). Haki kodu na pojedynczy adres dodane PRZED uruchomieniem są OK (jak w `ui_session.enable_trace`).
- Nie używaj `presenter_trace.py` ani statycznego "view_off" jako faktów.

## 1. Środowisko
```bash
pip install unicorn capstone pillow numpy        # wymagane; Python 3.11+
git clone ... && git checkout ccr-be8a1bcb-5t76j0   # narzędzia w tools/
sha256sum FW2213TK_kopia.bin   # = 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071
```
Uruchamiaj skrypty jako `python3 -I tools/X.py ...` (izolacja). Plik firmware kładź obok, poza gitem (jest w `.gitignore`; sprawdź `git status` przed commitem).

## 2. Punkty kontrolne (obowiązkowe wejście na ekran)
NIE nawiguj przez `boot()` + `ListNav` w każdej sesji (to daje 10 zamiast 19 wierszy menu i `IndexError`). Zrób raz:
```bash
python3 -I tools/ui_prepare_cfg.py FW2213TK_kopia.bin /tmp/L1 1      # poziom 1; /tmp/L0 dla poziomu 0; wynik: menu.state, rows.pkl, rows.txt
python3 -I tools/action_probe.py ... --nodes 17_screen   # lub bezpośrednio: tools/action_probe.enter_node(s, dir, rows, "17_screen")
```
Wiersze menu (L1): 0 kociol, 1 palnik, 2-5 CO1-4, 6 cwu, 7 solar, 8 bufor, 9 alarmy, 10 info, 11 konfiguracja, 12 pin, 13 jezyk, 14 alarm_dzw, 15 test_wyjsc, 16 statystyki, 17 siec, 18 internet (+ kaskada/magazyn gdy 0x350C/0x3525). Węzeł = `<wiersz>_screen` lub `<wiersz>_settings` (np. `17_screen` = SIEĆ). Dalej każdy test: `UiSession.from_checkpoint(FW, "<dir>/node_17_screen.state", None)`.
Zrzut `shot()` to 480×272; ciało ekranu = y≥46.

## 3. Reguły fizyczne emulatora (zmierzone, ważne)
- **Czekaj**: po starcie/ze świeżego punktu 4500 tików zanim zaczniesz pracować na PID/CAN (inicjalizacja CAN RX). Po tapie `settle` 700-1000, po wstrzyknięciu PID ≥250.
- **CAN RX przyjmuje jedną ramkę naraz**: odstęp ≈12 tików między ramkami (`s.can(...)`, `s.wait(12)`). Paczki ramek się gubią. Wartości kanałów modułów są średnią z 8 próbek → ≥8 rund.
- **Wstrzyknięcie PID**: `s.inject_param(pid, v)` zwraca wartość ze storage - ZAWSZE sprawdzaj. Dla PID-ów z modułów CAN IO używaj `tools/live_sim.LiveSim` (PDO 0x280/0x380/0x480+node, NTC), nie 0x584. Mapowanie kanałów: `data/ui_model/live_sources.json`, skan: `tools/live_scan.py`.
- Moduły: 0x56 CAN IO BIG, 0x57 CAN IO BIG (drugi), 0x45 CAN IO 5, 0x5B VIDE NET WIFI, nieznany → UNKNOWN. SIEĆ pokazuje wiersz po heartbeat (0x700+node:05) + SDO identity (0x580+node: 43 18 10 02 + u32), jedna ramka na raz.
- Wykrywanie nowej wartości: kontroluj tło (PID-y 0x3726, 0x2311-0x2314, 0x2167, 0x229A zmieniają się same).
- Poziom dostępu: `s.set_access(level)`; układ ekranów zależy od poziomu (np. Alarmy L0 vs L1) - zawsze podawaj poziom w wyniku.

## 4. Standard testu (jak "Test wyjść"): każdy test ma wszystkie kroki
1. Realny firmware, `UiSession` z punktu kontrolnego węzła (nie mock).
2. Rzeczywisty TAP/swipe (`s.tap`, `s.swipe`, `drag_until_change`). Pozycje przycisków bierz z widgetów w RAM (rect +4..+0xB, absolutnie przez rodziców do `rd(0x20024818)+4`), nie "na oko" ze zrzutu (przewijana lista dryfuje o wiersz: po stuknięciu weryfikuj zrzutem, który wiersz się zmienił).
3. BEFORE → **przebieg kontrolny tej samej długości bez akcji** → akcja → AFTER. Zalicz tylko jeśli diff(akcja) ≠ 0 i diff(kontrola) = 0. Diff tylko ciała (y≥46), nie całego ekranu.
4. Przed akcją `n0 = len(s.can2.tx)`; po akcji nowe ramki 0x584 (`42 <pid_lo> <pid_hi> 01 <wartość u32 LE>`), z odfiltrowaniem okresowych (0x2167, 0x229A, 0x3723).
5. Widok = vtable `rd(rd(0x20024818))` (HOME 0x808f708, MENU 0x808f66c, SIEC 0x808f770, INFO 0x808f638, INTERNET 0x808f9ac, TEST_WYJSC 0x808f80c ...).
6. Powtórzenie z innej wartości/stanu (min. 2 niezależne przebiegi); wynik niezgodny = nie zaliczaj.
7. Zapis do repo: `RUN_SUMMARY.json` + małe PNG (ciało ekranu) w `analiza/FW2213TK-2026-11-22/data/ui_model/<temat>/`; surowe dowody MUSZĄ być w repo (nie `/mnt/data`).
Wzorzec gotowy: `tools/sii_acceptance.py FW STATEDIR OUT {siec|info|internet|all}`, `tools/sii_editor_probe.py`, `tools/audit_siec.py`.

## 5. Etykiety wyników
FACT-DYNAMIC = wykonane w emulatorze według pkt 4, dowód w repo. FACT-STATIC = z binarki bez wykonania. STRONG = spójne, bez pełnego dowodu. INFERENCE = wnioskowanie (np. od właściciela). OPEN = brak. REJECTED = obalone (podaj czym). Negatywny wynik = tylko "OPEN/NEGATIVE w tym teście" + warunki testu (czas, pacing, config) - nie wnioskuj "nigdy".

## 6. Git
Pracuj na swojej gałęzi, `git pull --rebase` przed pushem, commit + push po każdym etapie, bez PR. Krótki raport po etapie (co zmierzone / co otwarte). Nie dotykaj plików agenta UI w `ui_model/` bez ustalenia (dopisuj własne pliki/podkatalogi).

## 7. Co już jest zmierzone (nie powtarzaj)
Drzewo menu i warunki (`ui_model/menu_tree.json`), alarmy (`alarms.json`), PROGRAM, okna HOME, Test wyjść (`outputs_test.json`: kolumny A/OFF/ON, Ruszt+mieszacze A/CLOSE/OPEN, suwaki 0x2288/0x2298), źródła live (`live_sources.json`), SIEĆ (`audit_siec.py`, `sii_acceptance/siec`), edytor INTERNET (`internet_editor.json`: klawiatura rolkowa ^ v OK < ABC abc 123.0 ?!&; OK zapisuje znak do 0x3730 jako u32 BE-znak).
Otwarte dla Ciebie (propozycja): INTERNET - kasowanie `<`, wiele znaków/chunki 0x3730..35, limit 24/25, PASSWORD/SERIAL/PIN, trwałość, korelacja 0x5B; INFO - skąd teksty; SIEĆ - SW z PDO1 (bajty 6/7), 3+ moduły, 4. kolumna dla innych modułów.
