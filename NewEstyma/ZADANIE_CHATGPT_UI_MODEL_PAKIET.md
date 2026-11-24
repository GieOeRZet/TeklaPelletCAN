# Zadanie dla ChatGPT: pakiet `ui_model` (schemat, walidator, indeks, README) - etap 1 teraz, etap 2 po komplecie danych

Właściciel: ChatGPT. Agent UI dalej dostarcza dane (listy, PROGRAM "Kopiuj", renderer); Ty budujesz kontrakt, który te dane sprawdza.
Przeczytaj `NewEstyma/METODYKA_EMULATOR.md` (pkt 5, 6, 8) i katalog `analiza/FW2213TK-2026-11-22/data/ui_model/` (menu_tree.json, alarms.json, outputs_test.json, live_sources.json, lists.json, program_screen.json, home_dialogs.json, internet_editor.json, sii_acceptance/*). Gałąź robocza: Twoja.

## Etap 1 (teraz, nie czekaj na komplet danych)
1. **JSON Schema** (draft 2020-12) dla każdego istniejącego pliku `ui_model/*.json`, w katalogu `ui_model/schema/`. Wspólne pola obowiązkowe: `evidence` (MEASURED/STRONG/INFERENCE/OPEN/REJECTED + opis), poziom dostępu tam gdzie ma znaczenie, PID jako `0x....` istniejący w `pid_matrix_655.csv`. Schematy mają być **addytywne**: nieznane pola dozwolone (`additionalProperties: true`), wersja schematu w polu `schema_version`, bo dane jeszcze rosną (listy, PROGRAM, renderer).
2. **Walidator** `tools/validate_ui_model.py`: sprawdza schematy, spójność odsyłaczy (PID w pid_matrix, węzły w menu_tree, ekrany/vtable), brak pustych `evidence`, duplikatów, liczb poza zakresem rekordu PID; wynik: lista błędów/ostrzeżeń + kod wyjścia. Bez emulatora i bez firmware.
3. **Indeks** `ui_model/INDEX.json` generowany skryptem `tools/build_ui_model_index.py`: lista plików, ich schemat, wersja, liczba rekordów, data, ścieżki dowodów (PNG/RUN_SUMMARY).
4. **README** `ui_model/README.md`: co jest w którym pliku, jak czytać `evidence`, jak odbudować kartę HA / stronę / ekran Androida z tych danych (tylko opis: który plik daje co), lista znanych luk (z `NewEstyma/OPEN_POD_MUREM.md`).
5. Znalezione niespójności zgłaszaj w raporcie jako listę (plik, pole, problem) - NIE poprawiaj cudzych danych; agent UI poprawia u siebie.

## Etap 2 (po komplecie danych - agent UI da sygnał w COORDINATION)
Uruchom walidator na pełnym zestawie, dopnij schematy do list/PROGRAM/renderera, wygeneruj końcowy INDEX, zrób test regresji: `tools/render_eval.py` (wymaga emulatora i atlasu) tylko raportuj, nie zmieniaj.

## Zasady
Ta sama metodyka i etykiety wyników; commit + push po etapie, raport krótki; surowe wyniki w repo. Nie ruszaj `tools/ui_session.py`, `live_sim.py`, `pid_diff.py` (wspólne narzędzia agenta UI).
