# Plan pracy agenta UI (Claude) - do zamkniecia projektu CAN (stan: 2026-11-24)

Cel: karta HA/www/Android/ESP wygladajaca i zachowujaca sie jak oryginalny panel (nie pikselowe 1:1). Raport po kazdym etapie w `NewEstyma/RAPORT_POSTEPU.md` ("zrobilem X z Y, pozostalo Z"), commit + push.

| Etap | Zakres | Kryterium ukonczenia |
|---|---|---|
| E1 | HANDOFF + `tools/rebuild_env.sh` + plan + raport | DONE (f9eee88) |
| E2 (DONE 2026-11-24: 13/13 <6%) | Dialogi: naprawa PIN, ikony przyciskow, tor suwaka, przyciemnienie tla w `dialog_render_eval.py`/`ui_render.py` | 5 dialogow < 8% rozn. pikseli; HOME okna (5) dolaczone |
| E3 (DONE: 644 komorek, mediana 0.2%) | Automat pokrycia: `tools/coverage_gen.py` - unikalne komorki (L1=L2=L3 pominiete), stany alarm/offline/dialog przez wstrzykniecie, 4 procesy, render_eval | tabela pokrycia + % w `ui_model/coverage_matrix_agent.json` |
| E4 (DONE: mediana 0.2%; ALARMY L0 OPEN) | Szlif renderera ekranow (naglowek, gradient tla), usuniecie artefaktow (wezly bez wlasnego ekranu) | mediana < 3% dla 38+ ekranow |
| E5 (DONE) | FREEZE + porzadek: `tools/paths.py`, test dymny, mapa stary->nowy, `git mv`, `analiza` -> `analiza_archiwum` | walidator PASS + test dymny przed/po zgodny |
| E6 (DONE) | Kontrakt API/ui_model dla ESP i karty: co wystawia integracja (`custom_components/teklapelletcan`), mapowanie PID->encja/API, schematy list/PROGRAM/renderer | `ui_model/API_KONTRAKT.md` + walidator PASS |
| E7 (W TOKU: 18 ekranow, dialog liczbowy, PROGRAM, tryb API) | Szkielet karty HA (web) z `ui_model`: nawigacja wg menu_tree, ekran Kociol + lista Nastawy z zywymi wartosciami (dane przykladowe) | prototyp w `web/` otwiera sie i nawiguje |

Zasady anty-petlowe: kazdy etap max 2 iteracje poprawek po osiagnieciu kryterium; nowe znaleziska -> `BACKLOG.md`. Jesli etap blokuje sie > 1 h bez postepu - zapis w `OPEN_POD_MUREM.md` i dalej.

## Harmonogram i raportowanie (ustalone z wlascicielem 2026-11-24, praca autonomiczna kilka godzin)
Raport "zrobilem X z Y, pozostalo Z" na gore `RAPORT_POSTEPU.md` + commit + push: po KAZDYM podetapie (nie rzadziej niz co ~30-40 min pracy), nawet krotki ("heartbeat" z liczbami).
Kolejnosc: E2a okna HOME x5 (osobno kazde okno = wpis) -> E2b dialog enum -> E2c tor suwaka + Kopiuj <5% -> E3 (a: generator komorek, b: stany alarm, c: offline/dialog, d: tabela %) -> E4 (paczki ekranow po ~8, wpis po paczce, % mediana) -> E5 (freeze, `git mv analiza analiza_archiwum` + odwolania, smoke_test przed/po) -> E6 odswiezenie po zmianach -> E7 rozbudowa prototypu (ekran Kociol, zywe wartosci przez pid_to_point).
Odtworzenie w nowym czacie: `HANDOFF_AGENT_UI.md` + `bash tools/rebuild_env.sh` (~3 min) + WYMAGANE ponowne wgranie `FW2213TK_kopia.bin` przez wlasciciela (poza gitem; decyzja o LFS/repo otwarta). Zasady: 4 procesy max, ESTYMA_IDLE_FAST=1, zakaz sterowania kotlem, merge `--no-rebase`.
