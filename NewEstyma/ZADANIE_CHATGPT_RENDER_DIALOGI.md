# Zadanie dla ChatGPT: renderowanie dialogów i okien z danych (równolegle z agentem UI)

Cel renderera: dowód, że dane `ui_model` wystarczają do odbudowy ekranu 1:1 (renderer rysuje ekran TYLKO z danych, bez firmware; potem porównanie pikseli ze zrzutem z emulatora). Istniejący rdzeń: `tools/ui_render.py` (rysowanie tekstu fontami firmware, bitmap, kolor RGB565), `tools/render_compare.py` (porównanie z atlasem), `tools/render_eval.py` (tabela wyników). NIE zmieniaj tych trzech plików - są własnością agenta UI. Piszesz OSOBNY moduł i osobny runner, żeby nic się nie rozjechało.

## Podział
- **Agent UI** (nie ruszasz): listy parametrów, przełączniki (gałka), suwaki Testu wyjść, dwa ekrany odstające (`L1_12_screen`, `L0_11_settings`) - moduł `tools/ui_render_lists.py`.
- **Ty:** okna i dialogi - moduł `tools/ui_render_dialogs.py` + `tools/render_dialogs_eval.py` + wyniki w `ui_model/render_dialogs_eval.csv/.md` (nowe pliki).

## Zakres (stan domyślny, poziom 3 jeśli nie napisano inaczej)
1. Okna HOME (`home_dialogs.json`, `home_dialogs_widgets.json`, `home_overlays_changed.json`): auto, czas, data, paliwo, zasilanie.
2. Dialogi edycji: liczbowy (tytuł, duża wartość, min/max, suwak, -/+, OK), wyboru radio, PIN (`dialogs_edit_pin.json`), klawiatura rolkowa INTERNET (`internet_editor.json`), okno "Kopiuj na inne dni" i okno dnia w PROGRAM (`program_screen.json`).
3. Dla każdego: zrzut referencyjny z emulatora (punkt kontrolny wg `NewEstyma/METODYKA_EMULATOR.md`; gotowe zrzuty w `ui_model/dialog_shots/`), render z danych, różnica pikseli (diff ciała), wynik w tabeli. Metryka jak w `render_eval.py` (procent pikseli różnych, mediana).
4. Gdzie danych brakuje do narysowania - NIE zmyślaj; wpisz w raporcie co dokładnie brakuje (pole/pozycja/tekstura/kolor) i oznacz `BRAK_DANYCH`. Dopisz brakujące dane tylko jako nowy plik pomocniczy w swoim katalogu (`ui_model/chatgpt/`), agent UI włączy.

## Zasady
- Metodyka i etykiety jak zawsze; dowody (PNG referencja/render/diff, RUN_SUMMARY) w repo, bez firmware.
- Własna gałąź, commit + push po etapie, krótki raport z liczbami (ile dialogów, mediana %, lista BRAK_DANYCH).
- Interfejs: Twój moduł wystawia `render_dialog(name, data) -> PIL.Image`; agent UI podepnie go do wspólnego runnera po zamknięciu list.
- Użyj `ESTYMA_IDLE_FAST=1` (3x szybciej) i do 4 procesów, jeśli Twoje środowisko ma rdzenie.
