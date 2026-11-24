# Zadanie dla ChatGPT: inwentarz repozytorium przed porządkowaniem (TYLKO ODCZYT - nic nie przenosisz, nie usuwasz, nie zmieniasz)

Kontekst: po zamrożeniu uporządkujemy dane (`analiza_archiwum/` → `analiza_archiwum`, nowy porządek w `NewEstyma/`). Plan: `NewEstyma/PLAN_ZAMKNIECIA_I_PORZADKU.md`. Ty dostarczasz materiał do decyzji; agent UI zatwierdza dla swoich plików, właściciel zatwierdza całość. Do czasu FREEZE agent UI nadal pisze do `analiza_archiwum/FW2213TK-2026-11-22/` i `ui_model/` - NIE dotykaj tych plików, tylko je czytaj z gałęzi `ccr-be8a1bcb-5t76j0` (bierz najnowszy stan: `git fetch`; Twoje wyniki zapisuj tylko na swojej gałęzi, w nowym katalogu `NewEstyma/porzadek/`).

## 1. Inwentarz odwołań do `analiza_archiwum/` (kto czego używa)
Przeszukaj całe repo (wszystkie katalogi: `tools/`, `tests/`, `NewEstyma/`, `docs/`, `custom_components/`, `firmware/`, `android/`, `web/`, workflowy CI, `CLAUDE.md`, prompty, skrypty) pod kątem wszystkich ścieżek zaczynających się od `analiza_archiwum/`. Wynik `NewEstyma/porzadek/odwolania.csv`: kolumny `plik_zrodlowy, linia, sciezka_docelowa, rodzaj` (kod / test / dokumentacja / konfiguracja / CI), oraz `tools/` które mają ścieżki wpisane na sztywno (to one wymagają `tools/paths.py`). Osobno wskaż odwołania spoza `tools/`, `tests/` i dokumentacji (np. ESP/HA/Android/CI) - są najgroźniejsze.

## 2. Lista duplikatów
a) Identyczne bajtowo (sumy SHA-256) w całym `analiza_archiwum/` oraz między `analiza_archiwum/` a resztą repo: `NewEstyma/porzadek/duplikaty_identyczne.csv` (grupa, pliki, rozmiar).
b) Duplikaty semantyczne - te same dane w kilku plikach/formatach/wersjach (np. `widgets_inv_*`, `pass61/65/70` warianty, `panel_lists_by_level.csv` vs `lists.json`, `cg_*.csv` vs `ui_model/*`, kilka raportów o tym samym temacie): `duplikaty_semantyczne.csv` (temat, pliki, który wygląda na kanoniczny i dlaczego, który zastąpiony, co różni wersje).
c) Dla każdego pliku w `analiza_archiwum/` (JSON/CSV/MD/PNG): tag `kanoniczny / zastapiony / surowy-roboczy / dowod / raport-historyczny` - `NewEstyma/porzadek/klasyfikacja.csv`. Pliki, których nie jesteś pewien: tag `DO_PYTANIA` (nie zgaduj).

## 3. Szkic mapy docelowej
`NewEstyma/porzadek/MAPA_DOCELOWA.md`: proponowana struktura w `NewEstyma/` (wejście dla człowieka README + mapa "czego szukać gdzie", `ui_model/` jako jedyne źródło prawdy, `evidence/` na dowody, `raw/` na surowe wyniki z indeksem - surowe zostają do końca projektu), tabela stary adres → nowy adres dla KAŻDEGO pliku, tabela tematów (np. ALARMY → dane + raport + narzędzie + dowody). Zasada: usuwane tylko pliki identyczne bajtowo; reszta do archiwum z adnotacją "zastąpione przez X"; erraty zostają przy oryginałach.

## 4. Zasady
- Nie zmieniaj żadnego istniejącego pliku, nie przenoś, nie usuwaj. Same nowe pliki w `NewEstyma/porzadek/`.
- Nie zgaduj: niepewne = `DO_PYTANIA` + powód.
- Metodyka i etykiety jak zawsze; commit + push po etapie na swojej gałęzi; krótki raport (liczby: plików, duplikatów, odwołań, `DO_PYTANIA`).
- Skrypty do tego (np. `tools/inventory_repo.py`) zostają w repo, powtarzalne (będą uruchomione ponownie po FREEZE na świeżym stanie).
