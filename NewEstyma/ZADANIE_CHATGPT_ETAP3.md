# Zadanie dla ChatGPT: etap 3 (równolegle z agentem UI)

Obowiązuje `NewEstyma/METODYKA_EMULATOR.md` w całości (kontrola, powtórzenie, dowody w repo, etykiety). Pracujesz na swojej gałęzi, bez edycji plików agenta UI w `ui_model/` (dopisuj własne pliki/podkatalogi). Agent UI robi w tym czasie: etykiety wyliczeń w listach, PROGRAM "Kopiuj", renderer list i suwaków.
Szybkość: ustaw `ESTYMA_IDLE_FAST=1` (3x szybciej, wynik identyczny - sprawdzone); masz do 4 procesów jeśli Twoje środowisko ma rdzenie.

## A. Macierz pokrycia wyglądu (priorytet) - cel: policzyć, ile % wyglądu panelu faktycznie mamy
1. Zbuduj `tools/coverage_matrix.py`: wymiary = ekran/węzeł (z `ui_model/menu_tree.json`) × poziom dostępu 0-3 × konfiguracja bramkująca (0x2105 k=1..4, 0x2106, 0x2107, 0x2108, 0x350C, 0x3525, 0x350A, 0x350D, 0x362B itd. - z warunków w menu_tree) × stan (domyślny; alarm aktywny; moduł offline/online; dialog otwarty dla ekranów z dialogami).
2. Dla każdej komórki: czy mamy zrzut w atlasie (`ui_model/atlas/`), czy jest wynik `render_eval` (`tools/render_eval.py`, `ui_model/render_eval.csv`), jaka różnica pikseli. Brakujące komórki: dociągnij zrzuty z emulatora (punkty kontrolne przez `ui_prepare_cfg.py` + `enter_node`) i policz render_eval.
3. Wynik: `ui_model/coverage_matrix.json` + krótki `.md` z procentem pokrycia (komórki z różnicą < X% / wszystkie) i listą luk. Samego renderera nie zmieniaj - tylko raportuj.

## B. Kaskada i Magazyn - listy parametrów (0x08 KASKADA, 0x09 MAGAZYN)
Ekrany wymagają konfiguracji 0x350C (kaskada) i 0x3525 (magazyn). Uruchom `tools/list_scale.py` i `tools/list_switch.py` (wzór użycia w nagłówkach plików; wyniki scala `tools/list_scales_build.py`) dla tych dwóch list: skala/format wyświetlania, przełączniki (gałka), enumy. Wyniki zapisz osobno (`ui_model/chatgpt/list_scales_kaskada_magazyn.json`), agent UI włączy do `list_scales.json`.

## C. Twoje otwarte punkty SIEĆ / INFO / INTERNET (z `WERYFIKACJA_SII_STAGE2.md`)
Timeout offline SIEĆ (dokładna liczba tików), mechanizm braku "SW" dla 0x57, źródło nazwy kotła i "videRoom PIN" w INFO (pełny pid_diff zakresów), SERIAL/PIN w INTERNET, korelacja z 0x5B. Format SW: potwierdź `v<b6>.<b7>` dziesiętnie po >=10 rundach (u Ciebie wyszło `v52.1c`, u agenta UI `v52.18`).

## Format
Dane + RUN_SUMMARY + PNG w repo, commit + push po etapie, krótki raport; po zakończeniu wpis w COORDINATION.
