# HANDOFF agent UI (Claude) - pelny kontekst do wznowienia pracy w nowym czacie (stan: 2026-11-24)

Wznawiasz prace "agenta UI" w repo `GieOeRZet/TeklaPelletCAN`, galaz robocza **`ccr-be8a1bcb-5t76j0`** (wszystko scalone tutaj; inne galezie ChatGPT sa scalone i do skasowania recznie przez wlasciciela - proxy nie pozwala kasowac). Klon lokalny: `/home/user/TeklaPelletCAN`. Wlasciciel: Roman (po polsku, rozmowa w jezyku polskim, krotko i konkretnie).

## 0. Zasady wlasciciela (TWARDE)
- Pracuj AUTONOMICZNIE, bez pytan; po kazdym etapie krotki raport "zrobilem X z Y, pozostalo Z" w `NewEstyma/RAPORT_POSTEPU.md` + commit + push (`git pull --rebase` tylko gdy wiesz ze historia jest liniowa; po scaleniach galezi UZYWAJ `git pull --no-rebase` albo samego push - rebase moze rozbic merge'e). Bez PR.
- Firmware `FW2213TK_kopia.bin` (SHA-256 `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`) NIGDY do repo ani pelny listing/dezasemblacja (tylko male listingi na zadanie: `tools/dump_listing.py`, katalog `nogit_gemini/` jest wykluczony). Plik firmware lezy poza gitem w katalogu repo (`.gitignore`); jesli go nie ma - poproc wlasciciela.
- **ZAKAZ sterowania prawdziwym kotlem** (tylko odczyt): zadnych uslug HA, `sdo_write`, `sdo_scan`, zadnych przyciskow. Emulator jest odizolowany - wstrzykiwanie ramek w emulatorze jest OK.
- Nie ruszaj tematow PIN/tabela 23/RTC (to tematy wlasciciela/ChatGPT); zapis 0x2170 emulator odrzuca.
- Binarka jest jedynym zrodlem prawdy (wspomnienia wlasciciela o prawdziwym panelu = INFERENCE).
- Max 4 procesy emulatora (4 rdzenie); `ESTYMA_IDLE_FAST=1` (3x szybciej, wynik identyczny - zweryfikowane). Bez hakow Unicorn na pamiec RAM (hak MEM_WRITE wywala emulator, PC=0); hak CODE na pojedynczy adres dodany PRZED uruchomieniem jest OK.
- Etykiety wynikow: FACT-DYNAMIC (wykonane w emulatorze, dowod w repo) / FACT-STATIC / STRONG / INFERENCE / OPEN / REJECTED. Wynik negatywny = "OPEN/NEGATIVE w tym tescie" z warunkami.
- ChatGPT i Gemini: ChatGPT ZAKONCZONY (decyzja wlasciciela); Gemini = tylko analiza tekstu (wlasciciel jest posrednikiem; plik `nogit_gemini/ZADANIE_GEMINI.md` byl wyslany, odpowiedzi brak).

## 1. CEL projektu (doprecyzowany przez wlasciciela)
NIE chodzi o piksel-w-piksel 1:1, tylko: **karta Home Assistant (i www/Android/ESP) wygladajaca i zachowujaca sie jak oryginalny panel Estyma igneoTouch**: wyglad, konfiguracja, sposob wyswietlania, co/kiedy/gdzie i zaleznosci, klik -> wlasciwy ekran wg drzewa menu (z warunkami konfiguracji/poziomu). Docelowo urzadzenie ESP z tym softem dziala jak dzis TeklaPelletCAN (karty, www, Android, integracja), jak najmniej encji, glownie po API (integracja `custom_components/teklapelletcan` uzywa REST `/api/v1/states` z katalogu elementow urzadzenia). Po domknieciu "projektu CAN" - pelna dekompilacja (osobny etap). Wlasciciel zamierza odpalic agenta w Dockerze na N100/16GB (ciagla praca).

## 2. Stan (procentowo, ocena agenta)
Menu+warunki ~95%, widget->PID ~80%, HOME+okna ~85%, PROGRAM ~85% (Kopiuj zmierzone), alarmy ~85%, Test wyjsc ~95%, zrodla live ~90% (wszystkie zmapowane), listy ~70% (skale 153 wierszy, przelaczniki=galka; brak: kroki dialogu, etykiety enum), SIEC ~85%, INFO ~70%, INTERNET ~75%, renderer glownych ekranow 0.2-9% roznicy pikseli (mediana 6.3%; dialogi 6-21%, PIN 98%), warianty stanu (macierz pokrycia ChatGPT: 133 z 1120 zmierzone), pakiet `ui_model` (schematy+walidator PASS) ~60%. Razem ~78%.

## 3. Struktura repo (wazne)
- `tools/` - narzedzia (emulator: `cortexm_rtos.py`, `ui_session.py`, `live_sim.py`, `pid_diff.py`, `action_probe.py`, `live_scan*.py`, `list_*`, `dialog_render_eval.py`, `ui_render.py`, `render_eval.py`, `coverage_matrix.py`(ChatGPT), `validate_ui_model.py`, `build_ui_model_index.py`, `inventory_repo.py`, `sii_acceptance.py`, `audit_siec.py`, `flow_curve.py`, `ui_prepare_cfg.py`).
- `analiza/FW2213TK-2026-11-22/data/ui_model/` - **jedyne zrodlo prawdy**: `menu_tree.json`, `alarms.json`, `outputs_test.json`, `live_sources.json`, `lists.json`, `list_scales.json`, `program_screen.json`, `home_dialogs*.json`, `dialogs_edit_pin.json`, `internet_editor.json`, `schema/`, `INDEX.json`, atlas/dialog_shots/sii_acceptance/dialog_render.
- `NewEstyma/` - dokumentacja: `METODYKA_EMULATOR.md` (OBOWIAZKOWA), `PLAN_ZAMKNIECIA_I_PORZADKU.md`, `PLAN_PRACY_AGENT_UI.md`, `RAPORT_POSTEPU.md`, `BACKLOG.md`, `OPEN_POD_MUREM.md`, `COORDINATION.md`, `WERYFIKACJA_SII_STAGE2.md`, `porzadek/` (ChatGPT inwentarz), `porzadek_lokalny/` (moj inwentarz: linie+SHA-256).
- `analiza/` ma zostac zmieniona na `analiza_archiwum` PO zamrozeniu i porzadkowaniu (ustalone z wlascicielem; najpierw `tools/paths.py`, test dymny, `git mv`; odwolania do `analiza/`: 9 w narzedziach, ~207 w dokumentacji).

## 4. Odtworzenie srodowiska (po utracie /tmp)
```bash
cd /home/user/TeklaPelletCAN && bash tools/rebuild_env.sh      # buduje /tmp/w/{L0,L1,L3,LC3}: menu.state, rows.pkl, menu_tall.png (kilka minut)
```
Wymagania: python3.13, `pip install unicorn capstone pillow numpy` (jesli brak), firmware w katalogu repo. Punkty kontrolne wezlow (`node_N_screen.state`, `node_N_settings.state`) powstaja leniwie przez `action_probe.enter_node` (tez w `list_scale.py` itd.). Poziomy: L0/L1/L3 = `ui_prepare_cfg.py FW DIR LEVEL [0xPID=wart ...]`; kaskada+magazyn: `LC3` = poziom 3 + `0x350C=1 0x3525=1 0x351A=2` (wiersze menu 9 i 10).
Wiersze menu (L1/L3): 0 kociol,1 palnik,2-5 CO1-4,6 cwu,7 solar,8 bufor,9 alarmy,10 info,11 konfiguracja,12 pin,13 jezyk,14 alarm_dzw,15 test_wyjsc,16 statystyki,17 siec,18 internet. Wezel = `<wiersz>_screen|_settings`.

## 5. Fizyka emulatora (zmierzone, pulapki)
- Wait 4500 tikow po starcie zanim PID/CAN; CAN RX przyjmuje JEDNA ramke naraz (odstep ~12 tikow), kanal = srednia 8 probek (>=8 rund). `inject_param` zwraca `stored` - zawsze sprawdzaj. PID modulow przez `LiveSim`/PDO, reszta (cisnienie 0x3333, energia 0x3628...) przez 0x584 = sterownik.
- Przewijanie list: `drag_until_change` (pause_end=160, zatrzymanie palca); szybki swipe otwiera dialog. Punkt kontrolny wezla `N_settings` NIE jest na gorze listy (np. Palnik startuje przewiniety). TouchGFX listy: widgety wierszy sa wspolne; kolejnosc wierszy zalezy od poziomu/grup.
- Przyciski testu wyjsc: kolumny A/OFF/ON lub A/CLOSE/OPEN (Ruszt+mieszacze), suwaki Dm. 0x2288 / WentWyc 0x2298 (0-100).
- Zrodla live: moduly CAN IO przez PDO 0x280/0x380/0x480+node (krzywa NTC), PDO1 0x180+node: przeplywomierze 0x54/0x55 (bajt6 calk., bajt7 ulamek 8.8 -> PID=X*1469/65536), lambda 0x50 kanal 3 -> 0x2120; 0x4000 = wezel 0x56 kanal 5 gdy 0x350A=1; SLAVE kaskady: panel pyta 0x605-0x607 `40 01 20 01`, odpowiedz 0x585-0x587 `4B 01 20 01 <u16>` -> 0x200A-C; ramka `20 04 30 01` (obiekt 0x3004) - znaczenie OPEN.
- PIN: poziom 3 = 7153 (6154 REJECTED); poziomy 0000/0900/0999/7153.
- PROGRAM Kopiuj: OK zapisuje natychmiast, ramka 0x584 per dzien tylko gdy wartosc sie rozni (PID dni: Pn 0x2209, Wt 0x220A, ...).
- Edytor INTERNET: klawiatura rolkowa (^ v OK < ABC abc 123.0 ?!&), SSID 24 znaki w 0x3730..0x3735 (4 znaki/u32, big-endian w u32), PASSWORD 0x3736, WiFi 0x373E, zdalne 0x3741, SERIAL/PIN 0x373F/0x3740 bez edytora.
- Czerwone tla = brak resetu DMA2D (naprawione w `stm32_dma2d.py`).

## 6. Znane bledy/niedokonczone
- `tools/list_dialog_step.py`: wyniki wiarygodne tylko Kociol wiersze 0,1,2,4 (krok 1); reszta = blad metody (patrz BACKLOG).
- Etykiety enum: widget zmienia tid (+0x26), ale mapowanie tablica PL daje nietrafne napisy; metoda `tools/list_enum_dialog.py` (dialog radio + hak odczytu tekstow) dziala czesciowo (IN17, Energy meter type).
- Dialogi render (`tools/dialog_render_eval.py`): INTERNET edytor 6.1%, PROGRAM dzien 19.3%, Kopiuj 19.0%, liczbowy 20.9%, PIN 98.7% (widgety PIN tworza sie przed punktem sledzenia). Braki: ikony eco/comfort w przyciskach, tor suwaka (czesc ciemna), przyciemnienie tla.
- Odpowiedz Gemini (zadanie A-D: alarmy L0, strzalki 168/169, zapis PID/0x3333/0x3628, ramka 0x3004) - brak.
- Kasowanie galezi zdalnych i tagow niemozliwe z proxy (403); decyzja wlasciciela: skasuje sam.

## 7. Nastepne kroki
Patrz `NewEstyma/PLAN_PRACY_AGENT_UI.md` (etapy E2-E7) i raportuj do `NewEstyma/RAPORT_POSTEPU.md`.
