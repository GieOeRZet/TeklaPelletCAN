# Plan pracy agenta UI (Claude) - do zamkniecia projektu CAN (stan: 2026-11-24)

Cel: karta HA/www/Android/ESP wygladajaca i zachowujaca sie jak oryginalny panel (nie pikselowe 1:1). Raport po kazdym etapie w `NewEstyma/RAPORT_POSTEPU.md` ("zrobilem X z Y, pozostalo Z"), commit + push.

| Etap | Zakres | Kryterium ukonczenia |
|---|---|---|
| E1 | HANDOFF + `tools/rebuild_env.sh` + plan + raport | DONE (f9eee88) |
| E2 | Dialogi: naprawa PIN, ikony przyciskow, tor suwaka, przyciemnienie tla w `dialog_render_eval.py`/`ui_render.py` | 5 dialogow < 8% rozn. pikseli; HOME okna (5) dolaczone |
| E3 | Automat pokrycia: `tools/coverage_gen.py` - unikalne komorki (L1=L2=L3 pominiete), stany alarm/offline/dialog przez wstrzykniecie, 4 procesy, render_eval | tabela pokrycia + % w `ui_model/coverage_matrix_agent.json` |
| E4 | Szlif renderera ekranow (naglowek, gradient tla), usuniecie artefaktow (wezly bez wlasnego ekranu) | mediana < 3% dla 38+ ekranow |
| E5 | FREEZE + porzadek: `tools/paths.py`, test dymny, mapa stary->nowy, `git mv`, `analiza` -> `analiza_archiwum` | walidator PASS + test dymny przed/po zgodny |
| E6 | Kontrakt API/ui_model dla ESP i karty: co wystawia integracja (`custom_components/teklapelletcan`), mapowanie PID->encja/API, schematy list/PROGRAM/renderer | `ui_model/API_KONTRAKT.md` + walidator PASS |
| E7 | Szkielet karty HA (web) z `ui_model`: nawigacja wg menu_tree, ekran Kociol + lista Nastawy z zywymi wartosciami (dane przykladowe) | prototyp w `web/` otwiera sie i nawiguje |

Zasady anty-petlowe: kazdy etap max 2 iteracje poprawek po osiagnieciu kryterium; nowe znaleziska -> `BACKLOG.md`. Jesli etap blokuje sie > 1 h bez postepu - zapis w `OPEN_POD_MUREM.md` i dalej.
