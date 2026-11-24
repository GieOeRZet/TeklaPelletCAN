# Plan zamknięcia prac i porządkowania repo (koordynuje agent UI / Claude; decyzje: właściciel)

Cel: zamknąć opis UI 1:1, potem zamrozić i uporządkować dane (`analiza/` → archiwum, nowy porządek w `NewEstyma/`) bez psucia narzędzi agentów. Zasada anty-pętlowa: **po zamrożeniu nowe tematy trafiają do BACKLOGU, nie do bieżącej pracy.**

## Tory pracy i bramki (gate = warunek ukończenia)
| Tor | Właściciel | Zakres | Bramka zamknięcia |
|---|---|---|---|
| T1 Listy | agent UI | etykiety wyliczeń, kroki/zakresy dialogu, kaskada/magazyn* | `list_scales.json` pełny dla 13 list; OPEN opisane |
| T2 PROGRAM "Kopiuj" | agent UI | zapis kopiowania harmonogramu | dane w `program_screen.json` |
| T3 Renderer | agent UI | listy, suwaki, 2 ekrany odstające | render_eval dla list/suwaków zmierzony |
| T4 Etap 3 (ChatGPT) | ChatGPT | A macierz pokrycia, B kaskada/magazyn (*przejmuje z T1), C otwarte SII | wpis w COORDINATION + dane w repo |
| T5 Gemini | właściciel (pośrednik) | analiza statyczna: alarmy L0, strzałki, zapis PID, ramka 0x3004 | odpowiedź wklejona do agenta UI, weryfikacja emulatorem |
| T6 ui_model etap 2 | ChatGPT | schematy dla list/PROGRAM/renderera, końcowy INDEX | walidator PASS na kompletnym zestawie |
| T7 "Pod murem" | agent UI | `OPEN_POD_MUREM.md` | decyzja właściciela per pozycja (rozwiązać / zaakceptować jako luka) |

## Zamrożenie (FREEZE) - kiedy
Gdy T1, T2, T4 i T6(etap 2) są zamknięte (T3 i T5 mogą trwać po zamrożeniu, bo nie przenoszą plików). Agent UI ogłasza FREEZE wpisem w COORDINATION; od tej chwili: zero nowych plików w `analiza/` i `ui_model/` poza porządkowaniem.
Czas nie jest ustalany z góry, ale limity: każdy tor ma maks. 2 dalsze iteracje poprawek po osiągnięciu bramki; nowe znaleziska idą do `NewEstyma/BACKLOG.md`.

## Porządkowanie (po FREEZE) - patrz rozmowa z właścicielem
1. Scalenie gałęzi ChatGPT do głównej; tag git `pre-reorg-2026-11-24` (powrót jednym poleceniem).
2. Inwentarz odwołań `analiza/` (tools, testy, docs, CI, integracje, instrukcje, prompty).
3. `tools/paths.py` - jedno źródło ścieżek; narzędzia przełączone; test dymny (walidator, 1 pid_diff, 1 live_scan, 1 list_scale) przed i po.
4. ChatGPT: lista duplikatów (sumy kontrolne + ręczny przegląd) i szkic mapy stary → nowy; agent UI zatwierdza dla swoich plików; właściciel zatwierdza całość.
5. `git mv` wg mapy + tabela przekierowań `NewEstyma/MAPA_PRZENIESIEN.md`; surowe dane w jednym miejscu z indeksem (zostają do końca projektu).
6. Aktualizacja instrukcji (CLAUDE.md, METODYKA, COORDINATION, prompty); na końcu `analiza` → `analiza_archiwum` (tylko do odczytu).
Usuwane są tylko pliki identyczne co do bajtu; reszta do archiwum z adnotacją "zastąpione przez".

## Zasady na czas pracy
- Nikt nie zmienia wspólnych narzędzi (`ui_session.py`, `live_sim.py`, `pid_diff.py`, `cortexm_rtos.py`) bez wpisu w COORDINATION; zmiany wstecznie zgodne.
- Własne pliki w osobnych podkatalogach; scalanie robi agent UI.
- Raport po każdym etapie (zmierzone / otwarte / ryzyka).
