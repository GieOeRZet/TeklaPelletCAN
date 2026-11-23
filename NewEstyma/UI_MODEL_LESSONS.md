# UI-MODEL — wnioski z PASS 59–63 i plan nowego narzędzia (2026-11-23)

Status: prace nad UI-MODEL **zatrzymane decyzją właściciela** (2026-11-23 14:30). Ten plik zbiera, co zadziałało, co zawiodło
i jak przepisać narzędzie. Nowy wątek zaczyna od pilota na JEDNYM ekranie (Kocioł), dopiero potem skaluje.

## 1. Co zostało zrobione (dane trwałe w repo)
| element | plik | ocena |
|---|---|---|
| Inwentarz widżetów 24 węzłów poziomu 0 i 30 węzłów poziomu 2 (ekran wiersza menu + ekran po stuknięciu 400,245) | `analiza/FW2213TK-2026-11-22/data/widgets_inv_pass61_L0.json`, `..._L2.json`, wiersze menu `menu_rows_pass61_L*.txt` | **dobre** (te same dane co PASS 57, komplet). Pola: this, view_off, ax/ay, x,y,w,h, parent, vis (+0x25), touch (+0x24), text_id, bitmap_id, wildcard, text_pl, font |
| Stuknięcia w kontrolki (graf akcji) | `data/actions_pass61_L0_partial.json` (232 stuknięcia: 71 SCREEN, 108 VISUAL, 53 NONE; węzły 0..5 poziomu 0) | **dobre, częściowe**. Potwierdzone: nagłówek „<” → MENU, ikona domu → ekran główny, pasek programu → PROGRAM, zębatka → NASTAWY |
| PASS 62: zegar z CAN | `AUTONOMOUS-PASS-62-RTC-SYNC-FROM-CAN-EXECUTED-2026-11-23.md` | **HARD** |
| Narzędzia | `tools/action_probe.py`, `tools/presenter_trace.py`, `tools/ui_model.py` (--active, --resolver), `tools/ui_model_screens.py`, `tools/condition_probe.py`, `tools/action_graph.py` (target_screen) | patrz §3 |

## 2. Dlaczego obecne narzędzia UI-MODEL zawodzą
1. **Statyczne `view_off` (PASS 59) daje głównie przypadkowe zgodności.** `presenter_map.csv` zbiera stałe `movw 0x100..0x8000` ze WSZYSTKICH setterów wszystkich widoków; te same offsety występują w różnych klasach widoków. Na 3577 widżetach: 24 EXACT, 154 AMBIGUOUS, reszta brak. Bez wiedzy, który setter należy do aktywnego widoku, wynik jest bezwartościowy.
2. **Tracer zapisów (`presenter_trace.py --inv`) przypisywał zapisy cudzym widżetom.** Settery wywoływane przez `b.w` (tail call z prezentera) nie wracają pod adres za `BL`, więc „ramka settera” zostawała na stosie i wszystkie późniejsze zapisy (np. przebieg odświeżania ekranu) szły na konto ostatniego settera. Przykład: Kocioł, setter `0x0804CA42` (klucz 0x10, Boiler program) „zapisywał” 21 widżetów. Próby naprawy:
   - v3 (pop przy SP > SP wejścia): niewystarczające, bo kod wywołującego działa na tym samym SP.
   - dodawanie haka powrotu W TRAKCIE emulacji (`uc.hook_add` w callbacku): **wywraca emulator** (FAULT, pc=0xA5A5A5A4 w EstymaTask) na ekranie Konfiguracja. Unicorn nie toleruje dodawania haków kodu w trakcie `emu_start`.
   - v4 (przebieg wstępny zbiera LR, haki dodawane między przebiegami): na teście 11 czystych wiązań, ale w pełnym przebiegu z `--ticks 300` znowu 30 — setter z tail call nie zawsze wywołuje się w przebiegu wstępnym. **Niedeterministyczne pokrycie = niewiarygodne.**
3. **Wolność.** Hak `UC_HOOK_MEM_WRITE` na zakresie widoku + haki na ~150 setterów: ~1,5–3 min na węzeł (wejście z menu ~1–2 min + śledzenie). 54 węzły × 2 poziomy na 3 rdzeniach to > 1 h na przebieg; każda poprawka narzędzia = przebieg od nowa. Ekrany NASTAWY (~500 widżetów, lista) są najwolniejsze.
4. **Brak pilota.** Narzędzie skalowano na 54 węzły przed potwierdzeniem poprawności na jednym ekranie z ręcznie sprawdzonym wynikiem. Błędy wychodziły dopiero po godzinie.
5. **Tytuły ekranów po stuknięciu** z „najwyższego szerokiego tekstu” są zawodne (np. „Kaskada” dla MENU). Tożsamość ekranu = **vtable widoku** `[[0x20024818]]` (wszystkie widoki TouchGFX leżą w jednym buforze, więc sam wskaźnik widoku się nie zmienia).
6. **Liczniki tła.** PID 0x3726, 0x2311, 0x2312 zmieniają się same (ChatGPT PASS 79: wyłączone z publikacji). Każdy pomiar „PID zmieniony po akcji” musi odejmować przebieg kontrolny bez dotyku (action_probe to robi).

## 3. Co zachować, co przepisać
ZACHOWAĆ (działa, sprawdzone):
- `tools/cortexm_rtos.py`, `ui_session.py` (Board, UiSession, ListNav, checkpoint/from_checkpoint, inject_param), `ctor_trace.py` (widget_table), `screen_inventory_menu.py`, `ui_explore.py --prepare` — inwentarz i nawigacja.
- `tools/action_probe.py` — model stuknięć: punkt kontrolny ekranu, przebieg kontrolny, różnice (vtable widoku, obraz ciała/nagłówka, PID względem kontroli, ramki CAN spoza tła). ~5 s na stuknięcie. Zachować; dopisać etykietowanie ekranu po vtable.
- `tools/condition_probe.py` — pomysł dobry (wstrzyknięcie wartości PID przez prawdziwy RX i odczyt vis/tekst/bitmapa widżetów); nie był uruchomiony na danych, bo zależy od UI-MODEL.
- `tools/stm32_rtc.py` z poprawką PASS 62 (INIT lub INITF).
PRZEPISAĆ:
- `presenter_trace.py` (wiązanie dynamiczne) — patrz §4. `ui_model.py` zostawić jako format wyjścia, ale źródłem wiązań ma być nowe narzędzie.

## 4. Plan NOWEGO narzędzia UI-MODEL (pilot -> skala)
Pomysł: zamiast śledzić „kto jest w setterze” przez stos, **różnicować stan widżetów po zmianie jednego PID**. To jest odporne na tail calle, nie wymaga haków kodu w trakcie emulacji i daje od razu warunki widoczności.
1. Wejście: punkt kontrolny ekranu (jak `action_probe.enter_node`) + inwentarz widżetów tego węzła.
2. Lista PID-ów kandydatów dla ekranu: PID-y czytane przez GUITask na tym ekranie (`UiSession.enable_trace()["pids"]`, tani hak na 0x080215F6) — to jest zbiór ograniczony (kilkanaście–kilkadziesiąt).
3. Dla każdego PID i 3–5 wartości (min, max, 0/1, 5678 „brak danych”, typowa): wczytaj stan, `inject_param(pid, v)` (prawdziwy RX, walidacja firmware), odczekaj ~200 tików, odczytaj ze snapshotu RAM wszystkich widżetów węzła: vis, touch, rect, bitmap, tekst bufora. Widżet, którego stan zależy od wartości PID = **wiązanie FACT** (z regułą: wartość -> tekst/bitmapa/widoczność).
4. Bez haków MEM_WRITE i bez haków na settery w trakcie emulacji. Jedyny hak: odczyt PID (enable_trace) w przebiegu kandydatów.
5. Wyjście: `ui_model_<ekran>.json` w formacie `ui_model.py` (binding = `PID_DIFF`, z próbkami), + raport MD z tabelą ekran -> widżet -> PID -> reguła.

### Pilot: ekran Kocioł (poziom 0, węzeł `0_screen`)
Kryteria sukcesu (wszystkie muszą być spełnione, zanim narzędzie pójdzie na inne ekrany):
- K1. Wynik deterministyczny: dwa przebiegi dają identyczny JSON.
- K2. Czas: ≤ 10 min na ekran na jednym rdzeniu.
- K3. Zgodność z ręczną weryfikacją na zrzutach: temperatura kotła (PID 0x2001, format %d.%d, skala 0.1) zmienia duży tekst; ciśnienie (0x3333) i widoczność etykiety „Ciśnienie=” zależna od 0x350D; „T. powrotu=” zależna od 0x350A; ikona pompy (bitmapa 138) od 0x2277; obraz kotła od 0x370A (Boiler image selector). To są oczekiwania z PASS 61 (częściowo HARD z zapisów setterów); każda niezgodność ma być wyjaśniona, a nie zignorowana.
- K4. Zero wiązań „hurtowych” (jeden PID zmieniający > 10 widżetów bez widocznego powodu na zrzucie).
- K5. Zrzut ekranu przed/po dla każdego wiązania zapisany jako dowód.
Dopiero po K1–K5: Palnik, Ogrzewanie 1, Woda (różne klasy widoków), potem reszta węzłów, NASTAWY na końcu (listy).

## 5. Zasady na przyszłość
- Pilot na 1 ekranie z kryteriami, potem skala. Nigdy pełny przebieg nieprzetestowanego narzędzia.
- Nie dodawać haków Unicorn w callbackach emulacji.
- Długie przebiegi: maks. 3 procesy, zapis przyrostowy do pliku (wznawialny), log postępu z czasem.
- Każdy pełny przebieg poprzedzić szacunkiem czasu i podać go właścicielowi.
