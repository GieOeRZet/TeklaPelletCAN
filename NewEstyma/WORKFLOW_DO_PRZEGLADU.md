# Workflow agenta UI (Claude) - opis do przeglądu przez drugi, mocniejszy silnik

Cel projektu: opis całego UI panelu igneoTouch jako DANE (ekrany → widgety → PID/reguły, akcje, dialogi, drzewo menu, alarmy, źródła live) z binarki, tak by dało się odbudować interfejs 1:1. Binarka jest jedynym źródłem prawdy.

## Pętla pracy (każdy temat)
1. **Punkt kontrolny ekranu** (snapshot stanu emulatora: pickle+zlib całego Board) - `ui_prepare_cfg.py` → `menu.state` + lista wierszy menu; `action_probe.enter_node` → `node_N_screen.state`.
2. **Inwentarz widgetów** z RAM (rect, widoczność efektywna po drzewie rodziców, bitmapy, bufory tekstu) - `ui_extras.py`, `screen_inventory_menu.py`.
3. **Różnicowanie**: wczytaj snapshot → zmień jeden czynnik (PID przez ramkę 0x584 / kanał PDO / tap) → odczytaj stan widgetów → porównaj z przebiegiem kontrolnym → wiązanie widget→PID (`pid_diff.py`, `live_diff.py`, `live_scan.py`, `action_probe.py`).
4. **Pomiar**: tap/swipe → BEFORE / kontrola / AFTER, diff pikseli ciała, nowe ramki CAN TX, vtable widoku (tożsamość ekranu).
5. **Zapis jako dane** (`ui_model/*.json`), raport `AUTONOMOUS-PASS-*.md`, commit + push po każdym etapie.
6. Walidacja: renderer z danych vs atlas z emulatora (`render_eval.py`, mediana różnicy 6,3% pikseli).

## Stos
Python + Unicorn (Cortex-M4, FreeRTOS: GUITask/EstymaTask/CanRxTask), modele LTDC, DMA2D, CAN2, dotyk FT5x06. `tools/cortexm_rtos.py`, `ui_session.py`, `live_sim.py`. Firmware nie jest w repo.

## Gdzie to boli (wąskie gardła, błędy które się zdarzyły)
- Emulator jednowątkowy (Python): 15-70 s na pojedynczy pomiar; limit 3 równoległych procesów; wszystko seryjne.
- Skrypty jednorazowe żyją w `/tmp` (nie w repo) → odtwarzalność i przekazanie kosztują; wiedza o "pułapkach" (czekaj 4500 tików, jedna ramka CAN naraz co 12 tików, dryf przewijanej listy o wiersz, red-bg DMA2D, poziom dostępu zmienia układ) siedzi w raportach i głowie.
- Błędy metody, nie kodu: stuknięcie w niewłaściwy wiersz (dryf scrolla), brak kontroli (diff całego ekranu), przedwczesny snapshot (przed init CAN), konfiguracja bramkuje źródła (0x350A, 0x350C...), hak MEM_WRITE wywala emulator (PC=0).
- Skan "wszystko × wszystko" jest ręcznie zawężany (kanały modułów, PID-y, wartości), nie automatyczny.
- Brak automatycznego testu regresji: po zmianie narzędzia (np. DMA2D) trzeba było ręcznie odbudować snapshoty.
- Brak jednego, maszynowego indeksu `ui_model` (schemat, walidator) - jeszcze nie zrobiony.
- Statyczna analiza (capstone) jest tylko na żądanie; pełna dezasemblacja nie może trafić do repo (zasada właściciela), więc wnioskowanie o kodzie jest wąskie.

## Pytania do mocniejszego silnika (czego szukam)
1. Jak zautomatyzować skan wiązań: dla ekranu N wszystkie PID-y z odczytu GUITask × wartości z zakresu → macierz widgetów zależnych (z kontrolą), bez ręcznego prowadzenia? (snapshot-fork zamiast ładowania stanu za każdym razem)
2. Czy da się przyspieszyć emulator (Unicorn w C/Rust harness, pomijanie bezczynności, zrzut tylko RAM zmienianych stron, równoległość przez fork snapshotu)?
3. Śledzenie zapisu do rekordu PID bez haka MEM_WRITE (np. skan różnicowy RAM co N tików + odwracanie: kto pisze?), albo bezpieczny sposób haka.
4. Statyczna rekonstrukcja: tablica rekordów PID → konsumenci (kto czyta/zapisuje rekord), bez trzymania pełnego listingu w repo (generowanie na żądanie + zapis tylko wniosków).
5. Format `ui_model` jako kompletny kontrakt (JSON Schema + walidator + generator kart HA/web/Android) i test akceptacji "renderer vs emulator" w CI.
6. Otwarte zagadki: `OPEN_POD_MUREM.md`.

## Pliki do przeczytania (kolejność)
`NewEstyma/METODYKA_EMULATOR.md`, `NewEstyma/OPEN_POD_MUREM.md`, `tools/ui_session.py`, `tools/pid_diff.py`, `tools/live_scan.py`, `analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/` (menu_tree, alarms, outputs_test, live_sources, internet_editor), `AUTONOMOUS-PASS-63..70`.
