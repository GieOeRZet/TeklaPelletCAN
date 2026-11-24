# Audyt: SIEC / INFO / INTERNET (gałąź ccr-be8a1bcb-5t76j0-chatgpt, commit 5cceb36) - wykonał agent UI (Claude)

Metoda: przeczytany harness `tools/screen_acceptance_sii.py`, raporty `AUTONOMOUS-PASS-SIEC-DYNAMIC-ACCEPTANCE` i `AUTONOMOUS-PASS-INTERNET-DYNAMIC-BASELINE`, harness uruchomiony na tym samym firmware (SHA 1d679d68...c5071 zgodny) w emulatorze, potem własny test SIEC (`tools/audit_siec.py`, montaż `data/ui_model/audit_siec/siec_cases_montage.png`). Wszystko poniżej oznaczone MEASURED zostało wykonane przeze mnie na firmware w emulatorze.

## Odpowiedzi na pytania 1-5 (harness)
1. **Emulator, nie mock: TAK.** Używa `UiSession` z `tools/ui_session.py` (ten sam plik co na mojej gałęzi, diff = 0), Board/Unicorn, CAN2.
2. **Akcje rzeczywiste: częściowo.** `tap`, `can`, `inject_param` są rzeczywiste. Ale: (a) `inject_param` zwraca wartość zapisaną do storage, a harness jej NIE sprawdza (nie wiadomo, czy wstrzyknięcie weszło); (b) w INTERNET wartości SSID wstrzykiwane są do `0x3730..0x3735` jako założona serializacja, bez dowodu.
3. **Snapshot BEFORE/AFTER i diff: wadliwe.** `body_changed = bool(getbbox())` dla CAŁEGO ekranu (z nagłówkiem, zegarem, ikonami) i bez przebiegu kontrolnego (ten sam czas bez akcji). Dla INFO/INTERNET możliwy fałszywy "changed". Poprawka: crop do ciała (y>=46), przebieg kontrolny tej samej długości, test jest zaliczony tylko gdy diff(akcja) != 0 i diff(kontrola) == 0; dodatkowo odczyt tekstu z widgetów (bufor +0x34) zamiast samego bboxa.
4. **CAN TX przed/po: BŁĄD.** W `internet_suite` `tx_before=len(s.can2.tx)` jest liczone PO akcji, więc `tx_before == tx_after`. Poprawka: `n0=len(tx)` przed akcją i porównanie tylko ramek 0x584 z kluczem nowych.
5. **Nawigacja: harness NIE DZIAŁA w obecnym repo.** `menu_to_row(s,12|17|18)` kończy się `IndexError` w `ListNav.tap_row_from_top`: po `boot()` + `set_local(0x2105..0x2108)` + `set_access(level)` `ListNav.build()` widzi tylko 10 wierszy (zmierzone dla level 1 i 3). Indeksy 12/17/18 pochodzą z mojego drzewa menu (inna konfiguracja: pełny przygotowany stan `tools/ui_prepare_cfg.py`). Raporty ChatGPT mówią o "trzech gestach swipe" - to nie jest ten harness. **Wnioski z raportów nie są odtwarzalne z kodu w repo**, a surowych dowodów (`/mnt/data/...png`, `RUN_SUMMARY.json`) nie ma w repo.
   Poprawka: wejście przez gotowy punkt kontrolny (`ui_prepare_cfg.py` + `action_probe.enter_node`, SIEC = węzeł `17_screen`, INTERNET `18_screen`, INFO `10_screen`) i zapis `RUN_SUMMARY.json` + PNG do repo (małe).

## SIEC (pytanie 6) - MEASURED przeze mnie (po jednej ramce, odstęp 12 tików; każdy przypadek w osobnej sesji)
Format wpisu: nazwa | `Node ID=<dec>` | `SW v<ver>` | (4. kolumna).
| przypadek | wynik |
|---|---|
| pusta magistrala | 8 pustych wierszy |
| 0x56 | `CAN IO BIG  Node ID=86  SW v0.0` |
| 0x57 | `CAN IO BIG  Node ID=87` (BEZ "SW") - **ChatGPT: "pusty"; to błąd, 0x57 się pojawia** |
| 0x56 + 0x57 (i 0x57 + 0x56) | dwa wiersze, kolejność zawsze 0x56 pierwszy (nie kolejność przybycia: stała/po Node-ID, do potwierdzenia przy trzech+ modułach) |
| 0x5B | `VIDE NET WIFI  Node ID=91  SW v0.0` - **ChatGPT: "negatywny"; to błąd** |
| 0x45 | `CAN IO 5  Node ID=69  SW v0.0  T=5678` - czwarta kolumna = temperatura wewnętrzna modułu (5678 = brak danych) |
| 0x22 (nieznany) | `UNKNOWN  Node ID=34` |
| timeout (1500 tików bez ramek) | wiersz **zostaje** (ani znika, ani oznaczany) |
| ponowne pojawienie | bez zmiany |
Test pacingu: harness w wersji "dwie ramki naraz" (heartbeat+SDO bez odstępu) też dawał wpis (różnica bbox identyczna), więc negatywy ChatGPT nie wynikają z pacingu w tym harnessie, tylko z innego przebiegu (poza repo).
Kontrola bez akcji: brak różnicy (0 pikseli). Zamknięcie SIEC: ok. 75% (brak: znaczenie `SW v` z PDO1 bajty 6/7 - PASS 67 podaje wersję w PDO1; test z niezerową wersją; czwarta kolumna dla 0x40/0x46/0x78; zachowanie przy 3+ modułach i przy pełnej tablicy; offline długoterminowy).

## INFO (pytanie 7) - NIE WYKONANE dynamicznie w sposób do zaakceptowania
Harness crashuje przy nawigacji, brak wyników w repo. Fakty ze statycznych/pid_diff źródeł nie są FACT-DYNAMIC dla tego harnessu. Zamknięcie INFO: ok. 25%. Do zrobienia: INFO z punktu kontrolnego `10_screen`, odczyt tekstów z widgetów przed/po dla 0x3664, 0x3665, 0x2170 (0, 1, 5678, 65535) z kontrolą.

## INTERNET (pytanie 8) - NIE WYKONANE dynamicznie w sposób do zaakceptowania
Raport ChatGPT sam mówi: wstrzyknięcie 0x373E bez różnicy po 50 tikach (to za krótko: potrzebne settle >= 250 i okno odpowiedzi - mój `inject_param` robi to prawidłowo). Brak: edytor SSID/PASSWORD (tap w SSID nie został zbadany poza śladem), klawiatura, zapis, serializacja do PID, 0x5B -> INTERNET. Zamknięcie INTERNET: ok. 20%.

## Ocena
- **METODOLOGIA: FAIL** (diff całego ekranu bez kontroli, tx_before po akcji, brak sprawdzenia `stored`, nawigacja nie działa, dowody poza repo).
- **DYNAMICZNE WYKONANIE: FAIL** dla harnessu z repo (crash przy nawigacji); raportowane wyniki SIEC dla 0x56 były poprawne (potwierdzone), dla 0x57 i 0x5B - błędne.
- SIEĆ ok. 75%, INFO ok. 25%, INTERNET ok. 20%.
- Najważniejsze ryzyka: fałszywe negatywy 0x57 i 0x5B wpisane jako OPEN; wnioski bez dowodów w repo; założona serializacja SSID.
- Do wykonania: poprawić harness wg punktów 3-5; INFO i INTERNET z punktów kontrolnych; edytor tekstowy INTERNET (tap w SSID: widok i vtable), zapis do PID, trwałość; SIEC: SW z PDO1, 3+ moduły.

## Aktualizacja: poprawiony harness (tools/sii_acceptance.py) i wyniki
Poprawki wg punktow 3-5 wdrozone; uruchomione na firmware, wyniki w `data/ui_model/sii_acceptance/*/RUN_SUMMARY.json` + PNG.
- SIEC: 8 przypadkow, kontrola bez akcji = 0 px, wszystkie przypadki z modulem 'changed' (zgodnie z tabela powyzej).
- INFO i INTERNET: wstrzykiwanie PID (`stored` sprawdzone) nie zmienia ciala ekranu; rzeczywista akcja UI (tap w SSID) otwiera edytor klawiaturowy - opis i zapis w `data/ui_model/internet_editor.json` (`tools/sii_editor_probe.py`).
- Nowe zamkniecie: SIEC ~75%, INFO ~40% (teksty statyczne zmierzone; zrodla niewstrzykiwalne), INTERNET ~50% (edytor: wybor znaku, klasy znakow, OK->PID 0x3730 zmierzone; brak: kasowanie, wiele znakow, PASSWORD, trwalosc).
