# Pakiet do przeglądu (wszystko w jednym pliku, bez dostępu do GitHuba)

Kolejność: 1 workflow, 2 metodyka, 3 lista 'pod murem', 4 kluczowe narzędzia (kod), 5 przykładowe dane. Firmware (FW2213TK_kopia.bin) nie jest dołączony i nie jest potrzebny do przeglądu metody.


---
## PLIK: NewEstyma/WORKFLOW_DO_PRZEGLADU.md

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

---
## PLIK: NewEstyma/METODYKA_EMULATOR.md

# Metodyka pracy z emulatorem (ogólna; dla ChatGPT i agenta UI/Claude)

Cel: każdy wynik "dynamiczny" ma powstać tak samo jak u mnie: realny firmware → emulator → akcja → pomiar → powtórzenie → dane w repo. Binarka jest jedynym źródłem prawdy. Wspomnienia właściciela i integracja HA to tylko podpowiedź (INFERENCE).

## 0. Zakazy (twarde)
- Nigdy nie commituj `FW2213TK_kopia.bin` ani pełnego listingu/dezasemblacji firmware (tylko małe listingi na żądanie: `tools/dump_listing.py`).
- Zero sterowania prawdziwym kotłem: nie używaj HA (usługi, przyciski), `sdo_write`, `sdo_scan`. Emulator jest odizolowany - wszystko co wstrzykujesz leci tylko do emulatora.
- Nie ruszaj tematów kodów PIN, tabeli 23 i RTC (tematy właściciela). Zapis 0x2170 emulator i tak odrzuca.
- Maks. 3 procesy emulatora jednocześnie. Przed długim przebiegiem podaj czas (pilot na 1-2 przypadkach, potem skala).
- Nie dodawaj haków Unicorn (`mu.hook_add`) w trakcie działania ani na zakresy pamięci RAM (hak MEM_WRITE na rekordy PID wywala emulator: PC=0). Haki kodu na pojedynczy adres dodane PRZED uruchomieniem są OK (jak w `ui_session.enable_trace`).
- Nie używaj `presenter_trace.py` ani statycznego "view_off" jako faktów.

## 1. Środowisko
```bash
pip install unicorn capstone pillow numpy        # wymagane; Python 3.11+
git clone ... && git checkout ccr-be8a1bcb-5t76j0   # narzędzia w tools/
sha256sum FW2213TK_kopia.bin   # = 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071
```
Uruchamiaj skrypty jako `python3 -I tools/X.py ...` (izolacja). Plik firmware kładź obok, poza gitem (jest w `.gitignore`; sprawdź `git status` przed commitem).

## 2. Punkty kontrolne (obowiązkowe wejście na ekran)
NIE nawiguj przez `boot()` + `ListNav` w każdej sesji (to daje 10 zamiast 19 wierszy menu i `IndexError`). Zrób raz:
```bash
python3 -I tools/ui_prepare_cfg.py FW2213TK_kopia.bin /tmp/L1 1      # poziom 1; /tmp/L0 dla poziomu 0; wynik: menu.state, rows.pkl, rows.txt
python3 -I tools/action_probe.py ... --nodes 17_screen   # lub bezpośrednio: tools/action_probe.enter_node(s, dir, rows, "17_screen")
```
Numer wiersza dowolnego ekranu: `<dir>/rows.txt` (po `ui_prepare_cfg.py`) lub `ui_model/menu_tree.json` (warunki widoczności wiersza). Węzeł = `<wiersz>_screen` lub `<wiersz>_settings` (np. `17_screen`). Ekrany spoza menu (okna HOME, dialogi, edytory) wchodzi się z węzła rodzica rzeczywistym tapem i zapisuje własny punkt kontrolny (`s.checkpoint(path)`) - wzór: `tools/home_dialogs.py`, `tools/overlay_probe.py`. Dalej każdy test: `UiSession.from_checkpoint(FW, "<dir>/node_17_screen.state", None)`.
Zrzut `shot()` to 480×272; ciało ekranu = y≥46.

## 3. Reguły fizyczne emulatora (zmierzone, ważne)
- **Czekaj**: po starcie/ze świeżego punktu 4500 tików zanim zaczniesz pracować na PID/CAN (inicjalizacja CAN RX). Po tapie `settle` 700-1000, po wstrzyknięciu PID ≥250.
- **CAN RX przyjmuje jedną ramkę naraz**: odstęp ≈12 tików między ramkami (`s.can(...)`, `s.wait(12)`). Paczki ramek się gubią. Wartości kanałów modułów są średnią z 8 próbek → ≥8 rund.
- **Wstrzyknięcie PID**: `s.inject_param(pid, v)` zwraca wartość ze storage - ZAWSZE sprawdzaj. Dla PID-ów z modułów CAN IO używaj `tools/live_sim.LiveSim` (PDO 0x280/0x380/0x480+node, NTC), nie 0x584. Mapowanie kanałów: `data/ui_model/live_sources.json`, skan: `tools/live_scan.py`.
- Moduły: 0x56 CAN IO BIG, 0x57 CAN IO BIG (drugi), 0x45 CAN IO 5, 0x5B VIDE NET WIFI, nieznany → UNKNOWN. SIEĆ pokazuje wiersz po heartbeat (0x700+node:05) + SDO identity (0x580+node: 43 18 10 02 + u32), jedna ramka na raz.
- Wykrywanie nowej wartości: kontroluj tło (PID-y 0x3726, 0x2311-0x2314, 0x2167, 0x229A zmieniają się same).
- Poziom dostępu: `s.set_access(level)`; układ ekranów zależy od poziomu (np. Alarmy L0 vs L1) - zawsze podawaj poziom w wyniku.

## 4. Standard testu (jak "Test wyjść"): każdy test ma wszystkie kroki
1. Realny firmware, `UiSession` z punktu kontrolnego węzła (nie mock).
2. Rzeczywisty TAP/swipe (`s.tap`, `s.swipe`, `drag_until_change`). Pozycje przycisków bierz z widgetów w RAM (rect +4..+0xB, absolutnie przez rodziców do `rd(0x20024818)+4`), nie "na oko" ze zrzutu (przewijana lista dryfuje o wiersz: po stuknięciu weryfikuj zrzutem, który wiersz się zmienił).
3. BEFORE → **przebieg kontrolny tej samej długości bez akcji** → akcja → AFTER. Zalicz tylko jeśli diff(akcja) ≠ 0 i diff(kontrola) = 0. Diff tylko ciała (y≥46), nie całego ekranu.
4. Przed akcją `n0 = len(s.can2.tx)`; po akcji nowe ramki 0x584 (`42 <pid_lo> <pid_hi> 01 <wartość u32 LE>`), z odfiltrowaniem okresowych (0x2167, 0x229A, 0x3723).
5. Widok = vtable `rd(rd(0x20024818))` (HOME 0x808f708, MENU 0x808f66c, SIEC 0x808f770, INFO 0x808f638, INTERNET 0x808f9ac, TEST_WYJSC 0x808f80c ...).
6. Powtórzenie z innej wartości/stanu (min. 2 niezależne przebiegi); wynik niezgodny = nie zaliczaj.
7. Zapis do repo: `RUN_SUMMARY.json` + małe PNG (ciało ekranu) w `analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/<temat>/`; surowe dowody MUSZĄ być w repo (nie `/mnt/data`).
Wzorzec gotowy: `tools/sii_acceptance.py FW STATEDIR OUT {siec|info|internet|all}`, `tools/sii_editor_probe.py`, `tools/audit_siec.py`.

## 5. Etykiety wyników
FACT-DYNAMIC = wykonane w emulatorze według pkt 4, dowód w repo. FACT-STATIC = z binarki bez wykonania. STRONG = spójne, bez pełnego dowodu. INFERENCE = wnioskowanie (np. od właściciela). OPEN = brak. REJECTED = obalone (podaj czym). Negatywny wynik = tylko "OPEN/NEGATIVE w tym teście" + warunki testu (czas, pacing, config) - nie wnioskuj "nigdy".

## 6. Git
Pracuj na swojej gałęzi, `git pull --rebase` przed pushem, commit + push po każdym etapie, bez PR. Krótki raport po etapie (co zmierzone / co otwarte). Nie dotykaj plików agenta UI w `ui_model/` bez ustalenia (dopisuj własne pliki/podkatalogi).

## 7. Jak podejść do DOWOLNEGO nowego tematu (szablon)
1. Ustal ekran: wiersz menu / węzeł (`menu_tree.json`), poziom dostępu, konfigurację (`ui_prepare_cfg.py ... 0xPID=wartość`). Zapisz punkt kontrolny.
2. Inwentarz widgetów ekranu: `tools/screen_inventory_menu.py` / `tools/ui_extras.py` (rect, widoczność efektywna przez rodziców, bitmapy, teksty) - to lista tego, co może się zmieniać.
3. Źródła wartości: `tools/pid_diff.py` (PID → widget, wartości z zakresu z `pid_matrix_655.csv`; PID-y modułowe: `live_diff.py`/`live_scan.py`).
4. Akcje: `tools/action_probe.py` (tap w każdy aktywny widget: nawigacja, dialog, nowe ramki 0x584, zmiana PID).
5. Każdy znaleziony fakt przechodzi test wg pkt 4 (kontrola + powtórzenie) zanim dostanie FACT-DYNAMIC.
6. Wynik jako DANE (json/csv), nie opis: widgety → PID → reguła, akcje, warunki. Opis w md tylko jako komentarz do danych.
7. Narzędzie, którego brakuje: stwórz/ulepsz w `tools/` (masz zgodę właściciela), wzór: czytelny docstring z użyciem, wynik przyrostowy i wznawialny, bez haków z pkt 0.

## 8. Podział pracy i przekazanie (ChatGPT ⟷ agent UI)
- Każdy ma swoje tematy; temat ma jednego właściciela naraz. Przydział i status: `NewEstyma/COORDINATION.md` (wpis: temat, właściciel, status, gałąź, pliki). Zmiana właściciela tylko wpisem.
- Pracuj na własnej gałęzi; nie edytuj cudzych plików w `ui_model/` - dopisuj własne pliki/podkatalogi. Wspólne narzędzia (`tools/ui_session.py`, `live_sim.py`, `pid_diff.py`...) zmieniaj tylko drobno i wstecznie zgodnie; zmianę opisz w commicie.
- **Przekazanie tematu** (np. ChatGPT zostawia, agent UI domyka): w COORDINATION podaj (a) co zmierzone i gdzie dowody w repo, (b) lista OPEN z warunkami testu, (c) polecenie odtworzenia (komenda + punkt kontrolny), (d) znane pułapki. Domykający NIE poprawia po cichu: błąd w cudzym wyniku zapisuje jako errata (co było, co jest, dowód) obok oryginału i dopiero potem podmienia dane.
- Audyt cudzego wyniku = ponowne uruchomienie jego testu na firmware + własny test kontrolny; rozbieżność zgłaszana, nie ukrywana.
- Po każdym etapie: commit + push, krótki raport (zmierzone / otwarte / ryzyka). Przy ~95% limitu kontekstu: zapis stanu do `NewEstyma/01_PROJECT_STATE.md` i handoff.

## 9. Stan wiedzy
Aktualne wyniki i otwarte punkty nie są w tym pliku (żeby się nie starzał): `NewEstyma/01_PROJECT_STATE.md`, `NewEstyma/COORDINATION.md`, `analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/` (menu_tree, alarms, outputs_test, live_sources, internet_editor, sii_acceptance ...) oraz raporty `AUTONOMOUS-PASS-*`.

---
## PLIK: NewEstyma/OPEN_POD_MUREM.md

# Lista "pod murem" (agent UI): rzeczy, których nie udało się rozgryźć, do narady na końcu
Zasada właściciela: cel to soft 1:1; wszystko ma być wyjaśnione. Tu trafiają tylko tematy, przy których zabrakło narzędzi/danych. Nic tu nie jest odpuszczone.

1. **Krzywa przepływomierzy 0x371A/0x371E**: liniowo 5,74 x surowy do 200, powyżej nieregularnie (300→252, 500→1401, 800→183, 1000→1332). Powód nieznany (filtr/odrzucanie próbek lub inna formuła). Następny krok: statyczna analiza funkcji ~0x8006970 (zapis flow) + test z jedną wartością długo (>=40 rund).
2. **Alarmy, układ L0 (przesunięcie o 80 px)**: deterministyczne, ale mechanizm poziomu nie znaleziony w kodzie widoku (czyta go wspólny nagłówek 0x0804A20C/0x0804A566 i bramka 0x0807FCAA).
3. **Tekstura strzałek alarmów (168/169)**: w binarce stała; czy przełącza się dynamicznie - brak dowodu.
4. **Zapis 0x2170 (videRoom PIN)**: emulator odrzuca (stored=0) - temat PIN-ów należy do właściciela.
5. **Ramka 0x20 04 30 01 do slave**: znaczenie bajtu 0x20 (download initiate bez rozmiaru?) i skutek po stronie slave - nie do sprawdzenia bez drugiej strony.

---
# 4. Kluczowe narzędzia (kod)

## PLIK: tools/ui_session.py
```python
#!/usr/bin/env python3
"""NewEstyma PASS 44: sesja UI sterowana krok po kroku na emulatorze systemowym (FreeRTOS + LTDC + DMA2D + CAN2 + I2C/FT5x06).
    s = UiSession("FW2213TK_kopia.bin"); s.boot(); s.tap(34,235); s.wait(600); img = s.shot("menu")
Wspolrzedne = EKRANOWE 480x272 (przeliczane na surowe kontrolera: x/0.375, y/0.354 — z FUN sampleTouch 0x080759DC).
Metody: wait(ticks), tap(x,y,hold=150), swipe(x0,y0,x1,y1,ticks=200), shot(name)->PIL.Image (zapis do outdir/name.png), can(id,data), set_param(pid,value) (przez CAN 0x584/0x42),
state() (przydatne liczniki). Tick ~ 1 ms (100000 instrukcji). Jedna sesja ~ kilka sekund rozruchu + ~3 s na 1000 tikow."""
import os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cortexm_rtos as C, stm32_i2c as I, render_screen as R
LTDC = 0x40016800
def screen_to_raw(sx, sy): return max(0, round((sx - 0.5) / 0.375)), max(0, round((sy - 0.5) / 0.354))

class UiSession:
    def __init__(self, binpath, outdir=None, tick=100000, rtc_start=None):
        self.b = C.Board(binpath, tick=tick); self.b.enable_dma2d(); self.can2 = self.b.enable_can2()
        self.rtc = self.b.enable_rtc(rtc_start) if rtc_start else None      # model RTC tylko na zyczenie (domyslnie: zegar sprzetowy = 0)
        self.ft = I.FT5x06(); self.b.enable_i2c(slaves={0x38: self.ft}); self.out = outdir; self.n = 0; self.shots = {}
        if outdir: os.makedirs(outdir, exist_ok=True)
        self._hook_extra = None
    def _hook(self, bd, *a):
        if bd.counters["svc"] == 0: return
        self.n += 1
        if self.n >= 100 and self.n % 10 == 0: bd.wr(LTDC + 0x38, 1); bd.raise_irq(88)
        if self._hook_extra: self._hook_extra(self.n)
    def wait(self, ticks):
        self.b.run(slices=ticks, hook=self._hook)
    def boot(self, ticks=700): self.wait(ticks)
    def tap(self, x, y, hold=150, settle=0):
        self.ft.touch(*screen_to_raw(x, y)); self.wait(hold); self.ft.release(); self.wait(max(60, settle))
    def swipe(self, x0, y0, x1, y1, ticks=240, steps=12, pause_end=0):
        self.ft.touch(*screen_to_raw(x0, y0)); self.wait(60)
        for i in range(1, steps + 1):
            x, y = x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps; self.ft._set(2, *screen_to_raw(x, y), 1); self.ft.last = screen_to_raw(x, y); self.wait(ticks // steps)
        if pause_end: self.wait(pause_end)          # zatrzymanie palca przed puszczeniem: brak predkosci => brak bezwladnosci (flick)
        self.ft.release(); self.wait(80)
    def shot(self, name=None):
        w, h, pf, addr = R.framebuffer(self.b); img = R.to_image(self.b, w, h, pf, addr)
        if name and self.out: img.save(os.path.join(self.out, name + ".png"))
        if name: self.shots[name] = img
        return img
    def can(self, can_id, data): self.can2.inject(can_id, data)
    def set_param(self, pid, value, size=4):
        self.can2.inject(0x584, bytes([0x42, pid & 255, pid >> 8, 1]) + (value & 0xFFFFFFFF).to_bytes(4, "little"))
    POLLER = 0x2002466C   # obiekt pollera: +0x0C okno odpowiedzi, +0x10 bramka (handler RX 0x08072A90 przyjmuje 0x584 tylko gdy oba != 0)
    def inject_param(self, pid, value, repeats=3, ticks=80):
        """realistyczne wstrzykniecie wartosci jak odpowiedz sterownika (CAN 0x584/0x42) przez prawdziwy RX handler: zwalnia okno odpowiedzi i bramke pollera
        i powtarza ramke (jedna ramka bywa gubiona, gdy GUI jest zajete). Zwraca wartosc odczytana ze storage."""
        for _ in range(repeats):
            self.b.wr(self.POLLER + 0xC, 1, 1); self.b.wr(self.POLLER + 0x10, 1, 1); self.set_param(pid, value); self.wait(ticks)
        r = self._record(pid); n = {1: 1, 2: 2, 3: 4, 4: 2, 5: 4}[r[1]]; return self.b.rd(r[0], n)
    def _record(self, pid):
        """rekord tabeli runtime managera 0x20008D84 (stride 0x2C, baza +8): (storage, typ) albo None"""
        base = 0x20008D84 + 8
        for i in range(660):
            a = base + i * 0x2C
            if self.b.rd(a) == pid: return self.b.rd(a + 4), self.b.rd(a + 8)
        return None
    def set_local(self, pid, value):
        """zapis wprost do storage'u parametru (jak ustawienie wczytane z pamieci nieulotnej); szerokosc wg typu rekordu (1=u8, 2=u16, 3/5=u32, 4=s16).
        UWAGA: omija walidacje i publikacje; to stan poczatkowy, nie zapis uzytkownika."""
        r = self._record(pid)
        if r is None: raise KeyError("brak rekordu dla PID 0x%X" % pid)
        st, ty = r; n = {1: 1, 2: 2, 3: 4, 4: 2, 5: 4}[ty]; self.b.wr(st, value & ((1 << 8 * n) - 1), n); return st
    MODEL = 0x20020784   # singleton modelu (FUN 0x080414BA); poziom dostepu = bajt MODEL+0x158 (FUN_08037E74: PIN 900->1, 999->2, 6154->3)
    def set_access(self, level): self.b.wr(self.MODEL + 0x158, level, 1)
    def access(self): return self.b.rd(self.MODEL + 0x158, 1)
    @staticmethod
    def body_hash(im, y0=46):
        """skrot obrazu BEZ naglowka (y<y0): w naglowku zmienia sie licznik procentowy"""
        import hashlib
        return hashlib.md5(im.crop((0, y0, im.width, im.height)).tobytes()).hexdigest()
    def drag_until_change(self, x0, y0, x1, y1, attempts=5, ticks=240, steps=12, pause_end=160):
        """przeciagniecie powtarzane z przesunieciem fazy wzgledem odpytywania kontrolera (~40 tikow), az obraz (bez naglowka) sie zmieni.
        Pojedyncze przeciagniecia (zwlaszcza w dol od dolu listy) bywaja gubione zaleznie od fazy; zwraca True, gdy sie zmienilo."""
        for k in range(attempts):
            h0 = self.body_hash(self.shot()); self.swipe(x0, y0, x1, y1, ticks=ticks, steps=steps, pause_end=pause_end); self.wait(250)
            if self.body_hash(self.shot()) != h0: return True
            self.wait(7 + 9 * k)
        return False
    def go_top(self, tries=8):
        last = None
        for _ in range(tries):
            moved = self.drag_until_change(240, 70, 240, 240)
            if not moved: return True          # nie przewija sie juz => gora
        return False
    def scroll_capture(self, name, maxpages=8, dy=150, x=240, ytop=230):
        """robi zrzut, przewija w gore o dy i powtarza, az obraz przestanie sie zmieniac; zwraca liste obrazow"""
        import hashlib
        imgs, last = [], None
        for i in range(maxpages):
            im = self.shot("%s_%d" % (name, i)); h = self.body_hash(im)
            if h == last: break
            imgs.append(im); last = h; self.drag_until_change(x, ytop, x, ytop - dy, attempts=3)
        return imgs
    def checkpoint(self, path):
        """zapisuje stan emulatora i licznik tikow sesji (patrz Board.save_state)"""
        self.b.save_state(path, extra=dict(n=self.n))
    @classmethod
    def from_checkpoint(cls, binpath, path, outdir=None):
        s = cls(binpath, outdir); ex = s.b.load_state(path); s.n = ex["n"]; return s
    BITMAP_TABLE = (0x08064450, 188, 0x14)          # RUNTIME: tablica deskryptorow bitmap (RAW 0x54450, 188 wpisow po 0x14 B)
    TEXT_LANG_PTRS = (0x0806BE64, 0x0806AEEC, 0x0806B6A8, 0x0806CDDC, 0x080697B8, 0x08069F74, 0x0806C620, 0x0806A730)   # wskazniki tabel TypedText (PL EN LT SK CZ ES RO EST) = adres wpisu ID 57
    def enable_trace(self):
        """sledzi, ktore bitmapy i teksty (ID) firmware CZYTA przy rysowaniu: odczyty deskryptorow bitmap i wskaznikow TypedText (flash). Wynik: self.trace = {'bitmaps': set, 'text': set((jezyk, id))}"""
        from unicorn import UC_HOOK_MEM_READ
        self.trace = {"bitmaps": set(), "text": set(), "pids": set()}; base, n, stride = self.BITMAP_TABLE
        # PID-y odczytywane przez GUITask: wejscie w wyszukiwanie rekordu runtime (RUNTIME 0x080215F6; r2 = klucz). Tylko gdy biezace zadanie = GUITask (TCB 0x20001198)
        from unicorn import UC_HOOK_CODE
        from unicorn.arm_const import UC_ARM_REG_R2
        def look(uc, a, sz, ud):
            try:
                if self.b.rd(self.b.tcb_ptr) == 0x20001198: self.trace["pids"].add(uc.reg_read(UC_ARM_REG_R2) & 0xFFFF)
            except Exception: pass
        self.b.mu.hook_add(UC_HOOK_CODE, look, begin=0x080215F6, end=0x080215F6)
        def rb(uc, a, ad, sz, v, ud): self.trace["bitmaps"].add((ad - base) // stride)
        self.b.mu.hook_add(UC_HOOK_MEM_READ, rb, begin=base, end=base + n * stride - 1)
        for li, ptr in enumerate(self.TEXT_LANG_PTRS):
            tb = ptr - 57 * 4
            def rt(uc, a, ad, sz, v, ud, li=li, tb=tb): self.trace["text"].add((li, (ad - tb) // 4))
            self.b.mu.hook_add(UC_HOOK_MEM_READ, rt, begin=tb, end=tb + 495 * 4 - 1)
    def dump_trace(self, path):
        import json
        json.dump(dict(bitmaps=sorted(self.trace["bitmaps"]), text=sorted(self.trace["text"]), pids=sorted(self.trace["pids"])), open(path, "w"))
    def state(self): return dict(self.b.counters, tick=self.n, task=self.b.task_name())


def stitch_body(s, drag=60, maxsteps=60, maxerr=3):
    """sklada CALE przewijalne cialo ekranu (pod naglowkiem, y>=46) w jeden wysoki obraz: przeciagniecia w gore + dopasowanie przesuniecia; zwraca PIL.Image"""
    from PIL import Image
    B0 = ListNav.BODY0; frames = [s.shot()]; offs = [0]
    for _ in range(maxsteps):
        prev = frames[-1]
        if not s.drag_until_change(240, 235, 240, 235 - drag, attempts=4): break
        cur = s.shot()
        if s.body_hash(cur) == s.body_hash(prev): break
        err, d = ListNav._shift(prev, cur)
        if d == 0 or err > maxerr: break
        frames.append(cur); offs.append(offs[-1] + d)
    h = offs[-1] + frames[-1].height - B0; tall = Image.new("RGB", (480, h))
    for f, o in zip(frames, offs): tall.paste(f.crop((0, B0, 480, f.height)), (0, o))
    return tall


class ListNav:
    """Nawigator przewijanej listy (np. glowne MENU): skleja cala liste w jeden obraz (przesuniecie miedzy zrzutami wykrywane korelacja),
    potem dla dowolnego wiersza przewija tak, by byl widoczny, i zwraca wspolrzedna ekranowa do stuniecia. Wiersze maja stale rozstaw ~50 px.
    Uzycie: nav = ListNav(session); nav.build(); nav.rows (lista dict: idx, chevron); nav.tap_row(idx)."""
    BODY0 = 46      # poczatek obszaru listy (pod naglowkiem)
    PITCH = 50
    def __init__(self, s): self.s = s; self.tall = None; self.rows = []
    @staticmethod
    def _shift(a, b):
        """o ile pikseli lista przesunela sie miedzy a i b (b jest przewiniete w gore): minimalny blad dopasowania"""
        import numpy as np
        A = np.asarray(a.convert("L"), dtype=int)[ListNav.BODY0:, :460]; B = np.asarray(b.convert("L"), dtype=int)[ListNav.BODY0:, :460]
        best = None
        for d in range(0, A.shape[0] - 30):
            e = np.abs(A[d:] - B[:A.shape[0] - d]).mean()
            if best is None or e < best[0]: best = (e, d)
        return best
    def build(self, drag=60, maxsteps=30):
        from PIL import Image
        s = self.s; assert s.go_top(); frames = [s.shot()]; offs = [0]
        for _ in range(maxsteps):
            prev = frames[-1]; s.drag_until_change(240, 235, 240, 235 - drag, attempts=3); cur = s.shot()
            if s.body_hash(cur) == s.body_hash(prev): break
            err, d = self._shift(prev, cur)
            if d == 0 or err > 3: break
            frames.append(cur); offs.append(offs[-1] + d)
        h = offs[-1] + frames[-1].height - self.BODY0
        tall = Image.new("RGB", (480, h)); 
        for f, o in zip(frames, offs): tall.paste(f.crop((0, self.BODY0, 480, f.height)), (0, o))
        self.tall = tall; self.offs = offs; n = max(1, round((h - 4) / self.PITCH)); self.rows = []
        for i in range(n):
            cy = 29 + self.PITCH * i; self.rows.append(dict(idx=i, cy=cy, chevron=self._chevron(tall, cy)))
        return self.rows
    @staticmethod
    def _chevron(img, cy):
        px = img.convert("L").load(); h = img.height
        c = sum(1 for yy in range(max(0, cy - 9), min(h, cy + 9)) for xx in range(432, 452) if px[xx, yy] > 150)
        return c > 6
    def offset(self, img):
        """aktualny offset przewiniecia ekranu wzgledem sklejonej listy"""
        import numpy as np
        T = np.asarray(self.tall.convert("L"), dtype=int); B = np.asarray(img.convert("L"), dtype=int)[self.BODY0:, :460]
        best = None
        for o in range(0, T.shape[0] - B.shape[0] + 1):
            e = np.abs(T[o:o + B.shape[0], :460] - B).mean()
            if best is None or e < best[0]: best = (e, o)
        return best
    def tap_row_from_top(self, idx, settle=800):
        """jak tap_row, ale TYLKO ruchy w gore (niezawodne); zaklada, ze lista jest na gorze (np. po wczytaniu punktu kontrolnego)"""
        s = self.s; cy = self.rows[idx]["cy"]
        for _ in range(14):
            err, o = self.offset(s.shot()); y = self.BODY0 + cy - o
            if 70 <= y <= 250: s.tap(240, y, settle=settle); return True
            if y < 70: return False
            if not s.drag_until_change(240, 235, 240, 175, attempts=4): return False
        return False
    def tap_row(self, idx, settle=800):
        s = self.s; cy = self.rows[idx]["cy"]
        for _ in range(6):
            err, o = self.offset(s.shot())
            y = self.BODY0 + cy - o
            if 56 <= y <= 262: s.tap(240, y, settle=settle); return True
            if y > 262: s.drag_until_change(240, 235, 240, 135)
            else: s.drag_until_change(240, 80, 240, 180)
        return False
```

## PLIK: tools/pid_diff.py
```python
#!/usr/bin/env python3
"""PASS 63: PID-diff - wiazania widget -> PID przez roznicowanie stanu widgetow po wstrzyknieciu wartosci PID.

Pilot na jednym wezle (np. 0_screen = Kociol, poziom 0). Bez hakow MEM_WRITE i bez hakow na settery.
Jedyny hak (tylko w fazie "cands", przed przebiegami pomiarowymi): odczyt PID przez GUITask (UiSession.enable_trace()["pids"]).

Fazy:
  cands : punkt kontrolny wezla -> 400 tikow z hakiem -> lista PID czytanych przez GUITask  -> OUT.cands.json
  diff  : dla kazdego PID z listy i kilku wartosci: load_state(punkt kontrolny) -> inject_param -> wait(settle) -> stan widgetow
          (vis +0x25, touch +0x24, rect +4, bitmapa +0x26, tekst bufora +0x34) + zrzut. Przebieg kontrolny (bez wstrzykniecia)
          o tej samej dlugosci. Widget zalezny od wartosci = stan rozny dla >=2 roznych wartosci (po odjeciu tego,
          co zmienia sie samo - kontrola). Wynik zapisywany przyrostowo po kazdym PID (wznawialny).
Uzycie: python3 -I tools/pid_diff.py FW.bin DIR INV.json NODE OUT_PREFIX [--phase cands|diff|all] [--settle 200] [--pids 0x2001 ...]
"""
import argparse, csv, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, action_probe as AP, live_sim as L
import pickle

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analiza_archiwum", "FW2213TK-2026-11-22", "data")
VIEW = 0x20024818
S16 = lambda lo, hi: (lo | hi << 8) - (1 << 16) if (lo | hi << 8) & 0x8000 else (lo | hi << 8)


def pid_meta():
    m = {}
    for r in csv.DictReader(open(os.path.join(DATA, "pid_matrix_655.csv"), encoding="utf-8")):
        m[int(r["pid"], 16)] = r
    return m


def read_text(s, this):
    bp = s.b.rd(this + 0x34)
    if not (0x20000000 <= bp < 0x2002FFC0): return None
    t = []
    for i in range(48):
        c = s.b.rd(bp + 2 * i, 2)
        if c == 0: break
        t.append(chr(c))
    return "".join(t)


def read_state(s, widgets):
    rd = s.b.rd; out = {}
    for w in widgets:
        a = int(w["this"], 16)
        st = dict(vis=rd(a + 0x25, 1), touch=rd(a + 0x24, 1),
                  rect=[S16(rd(a + 4 + 2 * i, 1), rd(a + 5 + 2 * i, 1)) for i in range(4)])
        if w["role"] == "image": st["bmp"] = rd(a + 0x26, 2)
        if w["role"] == "text": st["text"] = read_text(s, a)
        out[w["this"]] = st
    return out


def sample_values(meta):
    """3-5 wartosci: min, max, 0/1 (jesli w zakresie), typowa (srodek), 5678 ('brak danych', jesli w zakresie) - bez duplikatow"""
    lo, hi = int(meta["min"]), int(meta["max"])
    if hi - lo <= 8: return list(range(lo, hi + 1))      # male zakresy (typy, wyliczenia): wszystkie wartosci (np. 0x22A1 =4 steruje „Ochrona kotla”)
    cand = [lo, hi, (lo + hi) // 2, 1, 0, 5678]
    vals = []
    for v in cand:
        if lo <= v <= hi and v not in vals: vals.append(v)
    return vals[:5] if len(vals) > 5 else vals


def sample_live(meta):
    """wartosci dC dla PID-ow temperaturowych z modulow (typowe zakresy; surowy odczyt NTC ma ograniczony zakres)"""
    return [100, 400, 650, 900]


def good_widgets(inv_node):
    """odrzuca wpisy-smieci inwentarza (rect poza ekranem: pola nie-Drawable)"""
    out = []
    for w in inv_node["widgets"]:
        if w["role"] == "other" and (w["w"] < 0 or abs(w["ax"]) > 2000 or w["w"] > 2000 or w["vis"] > 1 or w["touch"] > 1): continue
        out.append(w)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bin"); ap.add_argument("dir"); ap.add_argument("inv"); ap.add_argument("node"); ap.add_argument("out")
    ap.add_argument("--phase", default="all"); ap.add_argument("--settle", type=int, default=200)
    ap.add_argument("--pids", nargs="*"); ap.add_argument("--shots", default="")
    a = ap.parse_args()
    inv = {n["node"]: n for n in json.load(open(a.inv, encoding="utf-8"))}[a.node]
    rows = pickle.load(open(os.path.join(a.dir, "rows.pkl"), "rb"))
    meta = pid_meta(); t0 = time.time()
    s = U.UiSession.from_checkpoint(a.bin, os.path.join(a.dir, "menu.state"), None)
    st_path = AP.enter_node(s, a.dir, rows, a.node)
    cands_path = a.out + ".cands.json"
    if a.phase in ("cands", "all") and not os.path.exists(cands_path):
        s.enable_trace(); s.b.load_state(st_path); s.trace["pids"].clear(); s.wait(400)
        json.dump(sorted(s.trace["pids"]), open(cands_path, "w")); print("cands", len(s.trace["pids"]), "%.0fs" % (time.time() - t0), flush=True)
        if a.phase == "cands": return
        s = U.UiSession.from_checkpoint(a.bin, os.path.join(a.dir, "menu.state"), None)   # swiat bez haka dla pomiarow
    if a.phase == "cands": return
    cands = [int(p, 16) for p in a.pids] if a.pids else json.load(open(cands_path))
    ws = good_widgets(inv)
    sim = L.LiveSim(s); base_t = {p_: 40.0 for p_ in sim.where}
    res_path = a.out + ".json"
    res = json.load(open(res_path)) if os.path.exists(res_path) else dict(node=a.node, widgets=ws, control=None, pids={})
    if res["control"] is None:
        s.b.load_state(st_path); v0 = s.b.rd(s.b.rd(VIEW)); res["view_vptr"] = hex(v0)
        s.wait(a.settle + 240); res["control"] = read_state(s, ws); s.shot("x")
        res["control_dump"] = None
    if a.shots: os.makedirs(a.shots, exist_ok=True)
    for pid in cands:
        key = "0x%04X" % pid
        if key in res["pids"]: continue
        m = meta.get(pid)
        if not m: res["pids"][key] = dict(skipped="brak w pid_matrix"); continue
        runs = []
        live = pid in sim.where                                  # PID z modulu CAN IO: wartosc wchodzi przez ramki PDO (PASS 67), nie przez 0x584
        for v in (sample_live(m) if live else sample_values(m)):
            s.b.load_state(st_path)
            try:
                if live:
                    sim.raw = {n: [1000] * 12 for n in sim.raw}
                    for p_, t_ in base_t.items(): sim.set(p_, t_)
                    sim.set(pid, v / 10.0); sim.run(700); got = s.b.rd(s._record(pid)[0], 2)
                else: got = s.inject_param(pid, v)
            except Exception as e: got = "ERR %s" % e
            s.wait(a.settle); im = s.shot()
            shot = None
            if a.shots:
                shot = "%s_%s_%s.png" % (a.node, key, v); im.save(os.path.join(a.shots, shot))
            runs.append(dict(value=v, stored=got, view_vptr=hex(s.b.rd(s.b.rd(VIEW))), state=read_state(s, ws), shot=shot))
        res["pids"][key] = dict(name=m["name"], type=m["type"], min=m["min"], max=m["max"], runs=runs)
        json.dump(res, open(res_path, "w"), ensure_ascii=False)
        print(key, m["name"], [r["stored"] for r in runs], "%.0fs" % (time.time() - t0), flush=True)
    print("DONE %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
```

## PLIK: tools/live_scan.py
```python
#!/usr/bin/env python3
"""PASS 70: skan zrodel LIVE: dla modulu CAN IO (node) i kazdego z 12 kanalow analogowych podaje surowa wartosc przez ramki PDO (LiveSim, pojedynczo z odstepem)
i zapisuje, ktore PID-y zmieniaja sie wzgledem przebiegu bazowego (wszystkie kanaly 1000). Tylko odczyt/wstrzykniecie na emulatorze (nie dotyka kotla).
live_scan.py FW DIR OUT.json NODE [--chan 0 1 ..] [--vals 500 2000 3000] [--set PID=VAL ...]   (--set: wstepna konfiguracja przez inject_param)"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, action_probe as AP, live_sim as L
ap = argparse.ArgumentParser(); ap.add_argument("fw"); ap.add_argument("dir"); ap.add_argument("out"); ap.add_argument("node")
ap.add_argument("--chan", nargs="*", type=int, default=list(range(12))); ap.add_argument("--vals", nargs="*", type=int, default=[500, 2000, 3000])
ap.add_argument("--set", nargs="*", default=[]); a = ap.parse_args()
node = int(a.node, 16); BG = {0x3726, 0x2311, 0x2312, 0x2313, 0x2314, 0x2167, 0x229A}
s = U.UiSession.from_checkpoint(a.fw, os.path.join(a.dir, "menu.state"), None); s.wait(4500)
for kv in a.set:
    p, v = kv.split("="); s.inject_param(int(p, 16), int(v, 0))
s.wait(300); base = os.path.join(os.path.dirname(a.out) or ".", "scanbase_%s.state" % a.node); s.checkpoint(base)
sim = L.LiveSim(s); sim.raw.setdefault(node, [1000] * 12); recs = AP.pid_records(s)
def run(ch, v):
    s.b.load_state(base); sim.raw = {n: [1000] * 12 for n in set(sim.raw) | {node}}
    if ch is not None: sim.raw[node][ch] = v
    sim.run(800, nodes=(node,)); s.wait(200); return AP.pid_snap(s, recs)
b0 = run(None, 0); res = json.load(open(a.out)) if os.path.exists(a.out) else {}
res.setdefault("node", a.node); res.setdefault("chan", {})
for ch in a.chan:
    if str(ch) in res["chan"]: continue
    out = {}
    for v in a.vals:
        sn = run(ch, v)
        for p in sn:
            if p not in BG and sn[p] != b0.get(p): out.setdefault("0x%04X" % p, {})[v] = [b0.get(p), sn[p]]
    res["chan"][str(ch)] = out; json.dump(res, open(a.out, "w"), indent=1)
    print(ch, {k: [x[1] for x in v.values()] for k, v in out.items()}, flush=True)
```

## PLIK: tools/live_sim.py
```python
#!/usr/bin/env python3
"""PASS 67: symulator ZRODEL LIVE: modul CAN IO wysyla ramki PDO (0x280/0x380/0x480 + node: 4 x u16 kanalow analogowych; 0x180 + node: PDO1), a panel przelicza surowy odczyt (12-bit ADC)
na temperature wg krzywej NTC. Mapowanie kanal->PID zmierzone przy domyslnej konfiguracji (data/ui_model/live_sources.json).
    sim = LiveSim(session); sim.set(0x2001, 65.0); sim.run(300)     # temperatury w stopniach C
Ramki musza isc POJEDYNCZO z odstepem (~12 tikow): odbiornik CAN przyjmuje jedna naraz. Wartosci uspredniane (filtr 8 probek), wiec potrzeba >= 8 rund."""
import json, os, bisect
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analiza_archiwum", "FW2213TK-2026-11-22", "data", "ui_model")
class LiveSim:
    def __init__(self, session, src=None):
        self.s = session; self.src = json.load(open(src or os.path.join(D, "live_sources.json")))
        self.curve = sorted((int(k), (v - 65536 if v > 32767 else v)) for k, v in self.src["ntc_curve"]["points_raw_to_dC"].items())      # raw -> dC (malejaca)
        self.raw = {n: [1000] * 12 for n in (0x56, 0x45, 0x40, 0x46, 0x78)}
        self.where = {}
        for node, m in self.src["modules"].items():
            for slot, info in m["slots"].items():
                for pid in info["pids_primary"]: self.where[int(pid, 16)] = (int(node, 16), int(slot))
    def temp_to_raw(self, dC):
        xs = [v for _, v in self.curve]; rs = [r for r, _ in self.curve]; best = min(range(len(xs)), key=lambda i: abs(xs[i] - dC))
        if best > 0 and best < len(xs) - 1:
            for a, b in ((best - 1, best), (best, best + 1)):
                if (xs[a] - dC) * (xs[b] - dC) <= 0 and xs[a] != xs[b]: return int(rs[a] + (rs[b] - rs[a]) * (xs[a] - dC) / (xs[a] - xs[b]))
        return rs[best]
    def set(self, pid, celsius):
        node, slot = self.where[pid]; self.raw[node][slot] = self.temp_to_raw(int(round(celsius * 10)))
    def round_(self, nodes=(0x56, 0x45)):
        for node in nodes:
            for j, base in enumerate((0x280, 0x380, 0x480)):
                self.s.can(base + node, b"".join(v.to_bytes(2, "little") for v in self.raw[node][4 * j:4 * j + 4])); self.s.wait(12)
            self.s.can(0x180 + node, bytes([1, 0, 0, 0, 0, 0, 0, 0])); self.s.wait(12)
    def run(self, ticks, nodes=(0x56, 0x45)):
        per = 12 * 4 * len(nodes); n = max(8, ticks // per)
        for _ in range(n): self.round_(nodes)
```

## PLIK: tools/action_probe.py
```python
#!/usr/bin/env python3
"""PASS 61: rzeczywisty przebieg stukniec (zrodlo zdarzen dla tools/action_graph.py).

Dla wezla inwentarza (screen_inventory_menu.py: node "IDX_screen" / "IDX_settings") odtwarza wejscie z menu.state
(ten sam deterministyczny przebieg => te same adresy widgetow), zapisuje punkt kontrolny ekranu i dla kazdego
dotykalnego, widocznego widgetu (Drawable +0x24 touch, +0x25 vis) stuka w srodek prostokata. Kazde stukniecie
startuje z tego samego punktu kontrolnego. Rejestrowane skutki (wylacznie zaobserwowane, nic nie jest zgadywane):
  view      - zmiana klasy aktywnego widoku: vptr obiektu [0x20024818] (TouchGFX trzyma wszystkie widoki w jednym
              buforze, wiec sam wskaznik widoku sie nie zmienia - porownujemy jego vtable)
  body/head - zmiana obrazu ciala (y>=46) / naglowka (y<46) wzgledem przebiegu kontrolnego bez dotyku
  pid       - zmiany wartosci w storage'ach 655 parametrow (stara -> nowa)
  can       - ramki TX, ktorych NIE ma w przebiegu kontrolnym tej samej dlugosci (tlo: heartbeat, SDO, poller)
  texts     - TypedText ustawione na nowo (setTypedText) po stuknieciu, z tekstem PL; tytul = najwyzszy szeroki tekst
Uzycie:
  python3 -I tools/action_probe.py FW.bin DIR INV.json OUT.json --nodes 0_screen 0_settings [--max N] [--settle 700]
DIR = katalog z ui_explore.py --prepare (menu.state, rows.pkl, menu_tall.png). Wynik: lista akcji
{node, tap, widget(this), x, y, effects{...}} gotowa dla action_graph.py.
"""
import argparse, hashlib, json, os, pickle, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, ctor_trace as C
from PIL import Image

VIEW = 0x20024818
B = 0x08010000

def pid_records(s):
    base = 0x20008D84 + 8; out = []
    for i in range(660):
        a = base + i * 0x2C; pid = s.b.rd(a)
        if pid == 0 or pid > 0xFFFF: continue
        st, ty = s.b.rd(a + 4), s.b.rd(a + 8)
        if ty in (1, 2, 3, 4, 5) and 0x20000000 <= st < 0x20030000: out.append((pid, st, {1: 1, 2: 2, 3: 4, 4: 2, 5: 4}[ty]))
    return out

def pid_snap(s, recs): return {p: s.b.rd(st, n) for p, st, n in recs}

def hsh(im, box): return hashlib.sha1(im.crop(box).tobytes()).hexdigest()[:12]

def can_key(f): return (f["id"], bytes(f["data"]).hex())

def enter_node(s, d, rows, node, settle=700):
    """punkt kontrolny wezla inwentarza (IDX_screen / IDX_settings), ta sama sekwencja co screen_inventory_menu.grab"""
    st_path = os.path.join(d, "node_%s.state" % node)
    if os.path.exists(st_path): return st_path                      # gotowy punkt kontrolny (np. node_home.state z home_inventory.py)
    idx, kind = node.split("_", 1); idx = int(idx)
    if not os.path.exists(st_path):
        s.b.load_state(os.path.join(d, "menu.state")); s.wait(60)
        nav = U.ListNav(s); nav.tall = Image.open(os.path.join(d, "menu_tall.png")); nav.rows = rows
        nav.tap_row_from_top(idx); s.wait(settle)
        if kind == "settings": s.tap(400, 245, settle=800); s.wait(settle)
        s.checkpoint(st_path)
    return st_path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bin"); ap.add_argument("dir"); ap.add_argument("inv"); ap.add_argument("out")
    ap.add_argument("--nodes", nargs="+", required=True); ap.add_argument("--max", type=int, default=0)
    ap.add_argument("--settle", type=int, default=700); ap.add_argument("--shots", default="")
    a = ap.parse_args()
    raw = open(a.bin, "rb").read()
    def pl(i):
        try:
            p = struct.unpack_from("<I", raw, 0x5BD80 + 4 * i)[0]; o = p - B; r = []
            while True:
                c = struct.unpack_from("<H", raw, o)[0]
                if c == 0: break
                r.append(chr(c)); o += 2
            return "".join(r)
        except Exception: return "?"
    inv = {n["node"]: n for n in json.load(open(a.inv, encoding="utf-8"))}
    rows = pickle.load(open(os.path.join(a.dir, "rows.pkl"), "rb"))
    s = U.UiSession.from_checkpoint(a.bin, os.path.join(a.dir, "menu.state"), None)
    t = C.Tracer(s); recs = None; res = []
    if os.path.exists(a.out): res = json.load(open(a.out, encoding="utf-8"))
    done = {(r["node"], r["widget"]) for r in res}
    if a.shots: os.makedirs(a.shots, exist_ok=True)
    for node in a.nodes:
        if node not in inv: print("brak wezla w inwentarzu:", node, flush=True); continue
        st_path = enter_node(s, a.dir, rows, node, a.settle)
        if recs is None:
            s.b.load_state(st_path); recs = pid_records(s)
        # przebieg kontrolny: ta sama dlugosc bez dotyku
        s.b.load_state(st_path); s.can2.tx.clear(); v0 = s.b.rd(s.b.rd(VIEW)); p0 = pid_snap(s, recs)
        s.wait(150 + max(60, a.settle)); im0 = s.shot(); bg = {can_key(f) for f in s.can2.tx}; pc = pid_snap(s, recs)
        body0, head0 = hsh(im0, (0, 46, 480, 272)), hsh(im0, (0, 0, 480, 46))
        cands = [w for w in inv[node]["widgets"] if w.get("touch") and w.get("vis") and w["w"] > 0 and w["h"] > 0
                 and w["w"] * w["h"] < 480 * 272 * 0.6]
        seen_xy = set(); n = 0
        for w in sorted(cands, key=lambda w: (w["ay"], w["ax"])):
            cx = min(479, max(0, w["ax"] + w["w"] // 2)); cy = min(271, max(0, w["ay"] + w["h"] // 2))
            if (cx, cy) in seen_xy or (node, w["this"]) in done: continue
            seen_xy.add((cx, cy))
            if a.max and n >= a.max: break
            n += 1
            s.b.load_state(st_path); s.can2.tx.clear(); t.log.clear()
            s.tap(cx, cy, hold=150, settle=a.settle); im = s.shot(); v1 = s.b.rd(s.b.rd(VIEW)); p1 = pid_snap(s, recs)
            if a.shots: im.save(os.path.join(a.shots, "%s_%s.png" % (node, w["this"])))
            texts = {}
            for r in t.log:
                if r["op"] == "text": texts[hex(r["this"])] = r["id"]
            new_texts = sorted({pl(i + 57) for i in texts.values() if i < 496})
            title = ""
            if v1 != v0:
                ws = C.widget_table(s, t)
                for x in sorted(ws, key=lambda x: x["ay"]):
                    if x["role"] == "text" and 0 <= x["ay"] < 46 and x["w"] >= 300:
                        title = x["wildcard"] or (pl(x["text_id"] + 57) if x["text_id"] is not None and x["text_id"] < 496 else ""); break
            can = [dict(id=hex(f["id"]), data=bytes(f["data"]).hex()) for f in s.can2.tx if can_key(f) not in bg]
            pid = [dict(pid="0x%04X" % k, old=pc[k], new=p1[k]) for k in pc if pc[k] != p1.get(k)]   # wzgledem przebiegu kontrolnego (liczniki tla odpadaja)
            eff = dict(view_changed=v1 != v0, from_vptr=hex(v0), view_vptr=hex(v1), title=title,
                       body_changed=hsh(im, (0, 46, 480, 272)) != body0, head_changed=hsh(im, (0, 0, 480, 46)) != head0,
                       pid=pid, can=can, texts=new_texts[:40])
            kindc = ("SCREEN" if v1 != v0 else "PID" if pid else "CAN" if can else "VISUAL" if eff["body_changed"] or eff["head_changed"] else "NONE")
            res.append(dict(node=node, tap="tap", widget=w["this"], x=cx, y=cy, w=w["w"], h=w["h"], role=w.get("role"),
                            text_pl=w.get("text_pl") or w.get("wildcard") or "", bitmap_id=w.get("bitmap_id"), effect=kindc, effects=eff,
                            handler=None))
            print(node, w["this"], (cx, cy), kindc, title or "", pid[:3], can[:2], flush=True)
            json.dump(res, open(a.out, "w"), ensure_ascii=False, indent=1)
    print("DONE", len(res))

if __name__ == "__main__":
    main()
```

## PLIK: tools/sii_acceptance.py
```python
#!/usr/bin/env python3
"""PASS 70: poprawiony harness akceptacyjny SIEC / INFO / INTERNET (zastepuje screen_acceptance_sii.py z gałęzi ChatGPT).
Realny firmware -> emulator (UiSession) -> punkt kontrolny ekranu (ui_prepare_cfg/action_probe: node_10/17/18) -> BEFORE -> akcja -> AFTER.
Poprawki wzgledem wersji ChatGPT: (1) wejscie przez punkty kontrolne, nie ListNav; (2) diff tylko ciala (y>=46) z przebiegiem kontrolnym tej samej dlugosci;
(3) CAN TX liczony przed i po akcji (nowe ramki 0x584, bez okresowych 0x2167/0x229A); (4) sprawdzenie `stored` po inject_param; (5) widok = vtable [[0x20024818]]; (6) wyniki do OUT/RUN_SUMMARY.json + PNG.
Uzycie: sii_acceptance.py FW STATEDIR OUT {siec|info|internet|all}"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U
from PIL import Image, ImageChops
FW, SD, OUT, WHICH = sys.argv[1:5]; os.makedirs(OUT, exist_ok=True)
PER = {0x2167, 0x229A}; VIEW = 0x20024818
def new(node): s = U.UiSession.from_checkpoint(FW, os.path.join(SD, "node_%s_screen.state" % node), None); s.wait(300); return s
def body(im): return im.crop((0, 46, 480, 272))
def bb(a, b): return ImageChops.difference(body(a), body(b)).getbbox()
def vt(s): return hex(s.b.rd(s.b.rd(VIEW)))
def tx584(s, n0): return [bytes(f["data"]).hex() for f in s.can2.tx[n0:] if f["id"] == 0x584 and int.from_bytes(bytes(f["data"])[1:3], "little") not in PER]
def save(im, name): body(im).save(os.path.join(OUT, name + ".png"))
def step(s, name, act, settle=300):
    """BEFORE -> kontrola (bez akcji, ta sama dlugosc) -> akcja -> AFTER; kontrola i akcja z tego samego punktu: zapis stanu przed akcja"""
    st = os.path.join(OUT, "_tmp.state"); s.checkpoint(st)
    b = s.shot(); s.wait(settle); c = s.shot(); ctrl = bb(b, c)
    s.b.load_state(st); b = s.shot(); n0 = len(s.can2.tx); info = act(s); s.wait(settle); a = s.shot(); save(a, name)
    return dict(test=name, control_diff=ctrl, action_diff=bb(b, a), changed=bool(bb(b, a)) and not ctrl, view=vt(s), tx584=tx584(s, n0), info=info)
res = {}
if WHICH in ("siec", "all"):
    def feed(nodes):
        def f(s):
            for _ in range(6):
                for n in nodes: s.can(0x700 + n, [5]); s.wait(12); s.can(0x580 + n, [0x43, 0x18, 0x10, 2, 0, 0, 0, 0]); s.wait(12)
                s.wait(120)
        return f
    res["SIEC"] = [step(new(17), "siec_" + n, feed(x), 100) for n, x in (("empty", []), ("n56", [0x56]), ("n57", [0x57]), ("n56_57", [0x56, 0x57]), ("n57_56", [0x57, 0x56]), ("n5B", [0x5B]), ("n45", [0x45]), ("n22_unknown", [0x22]))]
if WHICH in ("info", "all"):
    r = []
    for pid, v in ((0x3664, 0x0214), (0x3664, 0x0215), (0x3665, 1), (0x2170, 0), (0x2170, 1), (0x2170, 5678), (0x2170, 65535)):
        r.append(step(new(10), "info_%04X_%d" % (pid, v), lambda s, p=pid, v=v: dict(stored=s.inject_param(p, v), pid=hex(p), value=v)))
    res["INFO"] = r
if WHICH in ("internet", "all"):
    r = []
    for pid, v in ((0x373E, 1), (0x373E, 0), (0x3741, 1), (0x3741, 0), (0x373D, 2), (0x373D, 0)):
        r.append(step(new(18), "int_%04X_%d" % (pid, v), lambda s, p=pid, v=v: dict(stored=s.inject_param(p, v), pid=hex(p), value=v)))
    def ssid(s): return dict(stored=[s.inject_param(0x3730 + i, x) for i, x in enumerate([0x486f6d65, 0, 0, 0, 0, 0])])
    r.append(step(new(18), "int_ssid_chunks", ssid))
    r.append(step(new(18), "int_tap_ssid", lambda s: s.tap(180, 62, settle=1000)))
    res["INTERNET"] = r
json.dump(res, open(os.path.join(OUT, "RUN_SUMMARY.json"), "w"), ensure_ascii=False, indent=1, default=str)
for k, v in res.items():
    for t in v: print(k, t["test"], "changed=%s ctrl=%s view=%s tx=%s %s" % (t["changed"], t["control_diff"], t["view"], t["tx584"][:3], t["info"] if not isinstance(t["info"], type(None)) else ""))
```

---
# 5. Przykładowe dane

## PLIK: ui_model/live_sources.json
```json
{
 "evidence": "MEASURED (PASS 67, emulator, konfiguracja domyslna 0x2105=4,0x2106..8=1; ramki PDO wstrzykiwane pojedynczo)",
 "transport": {
  "frames": "CAN RX: 0x180+node PDO1, 0x280+node PDO2, 0x380+node PDO3, 0x480+node PDO4; PDO2-4 = 4 x u16 LE; kanal n = slot (PDO2: 0-3, PDO3: 4-7, PDO4: 8-11)",
  "watchdog": "moduly offline po ~300 cyklach bez ramki (obiekt +0xA); PDO1 bajty 6/7 = wersja oprogramowania modulu (PIDy 0x3658/0x3659 dla 0x56, 0x3635/0x363D dla 0x45, 0x3630/0x3638 dla 0x40)",
  "rx_rule": "odbiornik przyjmuje jedna ramke naraz: ramki musza isc z odstepem ~12 tikow; wartosc = srednia z 8 probek (potrzeba >= 8 rund)"
 },
 "ntc_curve": {
  "description": "surowy odczyt PDO (12-bit ADC) -> PID temperatury [dC]; zmierzone dla 0x2001 (node 0x56 slot 0); identyczne dla pozostalych kanalow temperaturowych",
  "points_raw_to_dC": {
   "60": 1500,
   "180": 1358,
   "300": 1150,
   "420": 1020,
   "540": 924,
   "660": 848,
   "780": 786,
   "900": 732,
   "1020": 683,
   "1140": 640,
   "1260": 599,
   "1380": 564,
   "1500": 529,
   "1620": 495,
   "1740": 465,
   "1860": 434,
   "1980": 404,
   "2100": 376,
   "2220": 346,
   "2340": 319,
   "2460": 290,
   "2580": 261,
   "2700": 232,
   "2820": 201,
   "2940": 171,
   "3060": 139,
   "3180": 104,
   "3300": 68,
   "3420": 28,
   "3540": 65518,
   "3660": 65465,
   "3780": 65399,
   "3900": 65309
  },
  "valid_raw_range": "51..4000 (poza zakresem = blad czujnika)",
  "clamp_dC": "max 1500 (150.0 C)"
 },
 "modules": {
  "0x56": {
   "name": "CAN IO BIG",
   "object": "0x20023F54",
   "pdo_slots": {
    "PDO2 (0x280+node)": "kanaly 0-3",
    "PDO3 (0x380+node)": "kanaly 4-7",
    "PDO4 (0x480+node)": "kanaly 8-11"
   },
   "slots": {
    "0": {
     "pdo": "PDO2",
     "byte_offset": 0,
     "pids_primary": [
      "0x2001"
     ],
     "names": [
      "Boiler temp[dC]"
     ],
     "also_changes": []
    },
    "3": {
     "pdo": "PDO2",
     "byte_offset": 6,
     "pids_primary": [
      "0x215F"
     ],
     "names": [
      "Outside temperature"
     ],
     "also_changes": []
    },
    "4": {
     "pdo": "PDO3",
     "byte_offset": 0,
     "pids_primary": [
      "0x2110"
     ],
     "names": [
      "Hot water 1 measured temperature"
     ],
     "also_changes": []
    },
    "6": {
     "pdo": "PDO3",
     "byte_offset": 4,
     "pids_primary": [
      "0x226C"
     ],
     "names": [
      "Burner feeder temperature [dC]"
     ],
     "also_changes": []
    },
    "5": {
     "pdo": "PDO3",
     "byte_offset": 2,
     "pids_primary": [
      "0x4000"
     ],
     "names": [
      "Boiler return temp [dC]"
     ],
     "also_changes": [],
     "condition": "aktywny tylko gdy 0x350A (Return to boiler temperature sensor)=1; krzywa NTC jak pozostale (500->953, 2000->399); MEASURED PASS 70"
    }
   },
   "online_effects": {
    "0x215f": {
     "idle": 0,
     "online": 691,
     "name": "Outside temperature"
    },
    "0x2001": {
     "idle": 0,
     "online": 691,
     "name": "Boiler temp[dC]"
    },
    "0x2250": {
     "idle": 0,
     "online": 100,
     "name": "Burner brightness"
    },
    "0x226c": {
     "idle": 0,
     "online": 691,
     "name": "Burner feeder temperature [dC]"
    },
    "0x2110": {
     "idle": 0,
     "online": 691,
     "name": "Hot water 1 measured temperature"
    },
    "0x201a": {
     "idle": 0,
     "online": 30,
     "name": "Hot water 1 result temperature"
    },
    "0x2278": {
     "idle": 0,
     "online": 1,
     "name": "Hot water pump state"
    },
    "0x350a": {
     "idle": 0,
     "online": 1,
     "name": "Return to boiler temperature sensor"
    },
    "0x3607": {
     "idle": 0,
     "online": 1,
     "name": "Reserve sensor state"
    },
    "0x4014": {
     "idle": 0,
     "online": 196613,
     "name": "Alarm register"
    },
    "0x4028": {
     "idle": 0,
     "online": 975542400,
     "name": "Alarm date timestamp"
    },
    "0x403c": {
     "idle": 5678,
     "online": 0,
     "name": "Alarm confirm timestamp"
    },
    "0x404c": {
     "idle": 4,
     "online": 5,
     "name": "Alarm next index"
    },
    "0x404d": {
     "idle": 3,
     "online": 4,
     "name": "Number of alarms"
    }
   }
  },
  "0x45": {
   "name": "CAN IO 5",
   "object": "0x20021A40",
   "pdo_slots": {
    "PDO2 (0x280+node)": "kanaly 0-3",
    "PDO3 (0x380+node)": "kanaly 4-7",
    "PDO4 (0x480+node)": "kanaly 8-11"
   },
   "slots": {
    "0": {
     "pdo": "PDO2",
     "byte_offset": 0,
     "pids_primary": [
      "0x3171"
     ],
     "names": [
      "Buffer T1 measured temperature"
     ],
     "also_changes": [
      [
       "0x3174",
       "Buffer internal energy [%]"
      ]
     ]
    },
    "1": {
     "pdo": "PDO2",
     "byte_offset": 2,
     "pids_primary": [
      "0x2112"
     ],
     "names": [
      "Buffer top measured temperature"
     ],
     "also_changes": [
      [
       "0x2004",
       "Boiler set result temp[C]"
      ],
      [
       "0x2211",
       ""
      ],
      [
       "0x3174",
       "Buffer internal energy [%]"
      ]
     ]
    },
    "2": {
     "pdo": "PDO2",
     "byte_offset": 4,
     "pids_primary": [
      "0x2113"
     ],
     "names": [
      "Buffer bottom measured temperature"
     ],
     "also_changes": [
      [
       "0x3174",
       "Buffer internal energy [%]"
      ]
     ]
    },
    "4": {
     "pdo": "PDO3",
     "byte_offset": 0,
     "pids_primary": [
      "0x3172"
     ],
     "names": [
      "Buffer T2 measured temperature"
     ],
     "also_changes": [
      [
       "0x3174",
       "Buffer internal energy [%]"
      ]
     ]
    },
    "5": {
     "pdo": "PDO3",
     "byte_offset": 2,
     "pids_primary": [
      "0x2109"
     ],
     "names": [
      "Solar temperature 1 [C]"
     ],
     "also_changes": []
    },
    "6": {
     "pdo": "PDO3",
     "byte_offset": 4,
     "pids_primary": [
      "0x2102"
     ],
     "names": [
      "Solar temperature 2 [C]"
     ],
     "also_changes": [
      [
       "0x311c",
       "Solar pump state"
      ],
      [
       "0x3120",
       "Solar status"
      ]
     ]
    },
    "7": {
     "pdo": "PDO3",
     "byte_offset": 6,
     "pids_primary": [
      "0x2103"
     ],
     "names": [
      "Solar temperature 3 [C]"
     ],
     "also_changes": []
    },
    "8": {
     "pdo": "PDO4",
     "byte_offset": 0,
     "pids_primary": [
      "0x2104"
     ],
     "names": [
      "Solar temperature 4 [C]"
     ],
     "also_changes": []
    },
    "9": {
     "pdo": "PDO4",
     "byte_offset": 2,
     "pids_primary": [
      "0x3173"
     ],
     "names": [
      "Buffer T3 measured temperature"
     ],
     "also_changes": [
      [
       "0x3174",
       "Buffer internal energy [%]"
      ]
     ]
    }
   },
   "online_effects": {
    "0x2112": {
     "idle": 0,
     "online": 691,
     "name": "Buffer top measured temperature"
    },
    "0x2113": {
     "idle": 0,
     "online": 691,
     "name": "Buffer bottom measured temperature"
    },
    "0x2280": {
     "idle": 0,
     "online": 45,
     "name": "Buffer top set temperature"
    },
    "0x3171": {
     "idle": 19990,
     "online": 691,
     "name": "Buffer T1 measured temperature"
    },
    "0x3172": {
     "idle": 19990,
     "online": 691,
     "name": "Buffer T2 measured temperature"
    },
    "0x3173": {
     "idle": 19990,
     "online": 691,
     "name": "Buffer T3 measured temperature"
    },
    "0x3174": {
     "idle": 0,
     "online": 100,
     "name": "Buffer internal energy [%]"
    },
    "0x2109": {
     "idle": 0,
     "online": 691,
     "name": "Solar temperature 1 [C]"
    },
    "0x2102": {
     "idle": 0,
     "online": 691,
     "name": "Solar temperature 2 [C]"
    },
    "0x2103": {
     "idle": 0,
     "online": 691,
     "name": "Solar temperature 3 [C]"
    },
    "0x2104": {
     "idle": 0,
     "online": 691,
     "name": "Solar temperature 4 [C]"
    },
    "0x3620": {
     "idle": 5678,
     "online": 150,
     "name": "Inside temp [C] CAN IO 5"
    }
   }
  },
  "0x50": {
   "name": "Lambda module",
   "evidence": "MEASURED (PASS 70, live_scan, config 0x3605=1 itd.)",
   "pdo_slots": {
    "PDO2 (0x280+node)": "kanaly 0-3"
   },
   "slots": {
    "3": {
     "pdo": "PDO2",
     "byte_offset": 6,
     "pids_primary": [
      "0x2120"
     ],
     "names": [
      "Lambda oxygen [%]"
     ],
     "also_changes": [
      [
       "0x371F",
       "Lambda oxygen averaged [%]"
      ]
     ],
     "scale": "raw u16 = wartosc PID 1:1 (500->500, 2000->2000); 0x371F = usredniona"
    }
   },
   "pdo1": "bajty 0-1 = wersja SW modulu lambda (0x365A/0x365B)"
  },
  "0x54": {
   "name": "Airflowmeter 1",
   "evidence": "MEASURED (PASS 70, 12 rund ramki PDO1, konfiguracja 0x362B=1)",
   "pdo1": "0x180+node: bajty 6-7 (u16 LE) = surowy odczyt przeplywu -> 0x371A; bajty 0-1 = wersja SW (('0x3666', '0x3667'))",
   "pids_primary": [
    "0x371A"
   ],
   "raw_to_value_samples": {
    "0": 0,
    "20": 114,
    "50": 287,
    "100": 574,
    "200": 1148,
    "300": 252,
    "500": 1401,
    "800": 183,
    "1000": 1332,
    "1500": 1263,
    "2000": 1194,
    "3000": 1056,
    "4000": 919
   },
   "note": "zakres 0..200: wartosc = 5.74 x surowy (liniowo); powyzej 200 nieregularnie (filtr 8 probek / odrzucanie bledow - OPEN: dokladna krzywa i jednostka)"
  },
  "0x55": {
   "name": "Airflowmeter 2",
   "evidence": "MEASURED (PASS 70, 12 rund ramki PDO1, konfiguracja 0x362B=1)",
   "pdo1": "0x180+node: bajty 6-7 (u16 LE) = surowy odczyt przeplywu -> 0x371E; bajty 0-1 = wersja SW (PID wersji nie zmierzony)",
   "pids_primary": [
    "0x371E"
   ],
   "raw_to_value_samples": {
    "0": 0,
    "20": 114,
    "50": 287,
    "100": 574,
    "200": 1148,
    "300": 252,
    "500": 1401,
    "800": 183,
    "1000": 1332,
    "1500": 1263,
    "2000": 1194,
    "3000": 1056,
    "4000": 919
   },
   "note": "zakres 0..200: wartosc = 5.74 x surowy (liniowo); powyzej 200 nieregularnie (filtr 8 probek / odrzucanie bledow - OPEN: dokladna krzywa i jednostka)"
  }
 },
 "derived_by_controller": [
  "0x2278 Hot water pump state, 0x350A, 0x3607, 0x201A, 0x2250 (po wlaczeniu modulu 0x56)",
  "0x3174 Buffer internal energy [%] z temperatur bufora (T1..T3)",
  "0x311C/0x3120 Solar pump state/status z temperatur solarnych",
  "stany pomp i palnika (0x2277, 0x2007) wyliczane przez logike EstymaTask z temperatur - nie sa wejsciami"
 ],
 "unmapped_live": [],
 "scan_pass70": {
  "tool": "tools/live_scan.py",
  "method": "kazdy z 12 kanalow wezla dostaje surowe 500/2000/3000 (reszta 1000), roznica wszystkich PID-ow wzgledem bazy; bez hakow",
  "nodes_scanned": [
   "0x56",
   "0x45",
   "0x40",
   "0x46",
   "0x78",
   "0x50",
   "0x54",
   "0x55",
   "0x7A"
  ],
  "result": "0x56: tylko sloty 0,3,4,6 (jak PASS 67), pozostale kanaly 1,2,5,7-11 NIE wplywaja na zadne PID (rowniez przy 0x350D=1, 0x350A=1, 0x3707=1); 0x45: sloty 0,1,2,4,5,6,7,8,9 (jak PASS 67), 3/10/11 puste; 0x40,0x46,0x78,0x54,0x55: brak wplywu na PID przez PDO analogowe; 0x50 kanal 3: 0x2120 (lambda) i 0x371F",
  "not_via_pdo_analog": [
   "0x3333 Boiler pressure",
   "0x4000 Boiler return temp (wartosc 691 przy 0x350A online - nie z kanalu analogowego)",
   "0x3628 energy",
   "0x371A/0x371E flow",
   "SLAVE 1..3 SDO"
  ],
  "next": "tylko odczyt: sledzenie zapisu do rekordu PID (hak MEM_WRITE przed uruchomieniem zawiesza emulator - blad PC=0, nie powtarzac) albo analiza statyczna funkcji wokol 0x8006970/0x80069f0 (flow), 0x800bd0e (energy)",
  "correction": "wczesniejszy skan bez poprawnej konfiguracji nie widzial slotu 5; po 0x350A=1 kanal 5 wezla 0x56 -> 0x4000. Skan z 0x350D=1/0x3605/0x3629/0x362B/0x3707/0x3505/0x3529 nie wykryl zrodla 0x3333, 0x3628, 0x371A/E w kanalach 0x56/0x45/0x40 (dla 0x46/0x78 nie powtorzony z pelna konfiguracja)",
  "flowmeters": "MEASURED: 0x54 PDO1 bajty 6-7 -> 0x371A; 0x55 PDO1 bajty 6-7 -> 0x371E (tools/live_scan_pdo1.py). PDO1 byl pomijany we wczesniejszych skanach."
 },
 "controller_fed": {
  "evidence": "MEASURED (PASS 70): inject_param (ramka 0x584/0x42, odpowiedz sterownika) zapisuje wartosc do rekordu: 0x3333=1500 -> stored 1500, 0x3628=12345 -> stored 12345. Zadne PDO/kanal modulu nie zmienia tych PID-ow (skany PDO1-4 wezlow 0x40-0x5A, 0x78).",
  "pids": [
   "0x3333 Boiler pressure[mbar]",
   "0x3628 Statistics - total energy produced [kWh]"
  ],
  "conclusion": "STRONG: te wartosci dostarcza sterownik kotla protokolem 0x584 (jak wiekszosc PID-ow), nie modul CAN IO; w modelu UI zrodlo = \"controller\", wstrzykiwanie przez 0x584 jest wlasciwe. Uwaga: 0x371A po inject 777 -> stored 65487 (nadpisywane przez wlasne zrodlo PDO1)."
 },
 "cascade_slaves": {
  "evidence": "MEASURED (PASS 70, emulator; kaskada wlaczona: 0x350C=2, 0x351A=3 przez inject_param; odpowiedzi wstrzykiwane po jednej ramce, 8 powtorzen)",
  "requests_from_panel": "co ~1000 tikow dla kazdego slave: 0x605/0x606/0x607 dane 40 01 20 01 00 00 00 00 (SDO upload obiektu 0x2001:01) oraz 20 04 30 01 00 00 00 00 (obiekt 0x3004:01, wartosc wysylana do slave: zadana temperatura wirtualnego odbiornika energii; w tym stanie 0)",
  "responses": {
   "frame": "0x585/0x586/0x587 = 0x580+node (node 5,6,7), dane 4B 01 20 01 <u16 LE> (SDO expedited 2 bajty) -> wartosc w dC bez krzywej",
   "mapping": {
    "0x585 (SLAVE 1)": "0x200A Remote boiler 1 temp[dC] s16 0..1500",
    "0x586 (SLAVE 2)": "0x200B Remote boiler 2 temp[dC]",
    "0x587 (SLAVE 3)": "0x200C Remote boiler 3 temp[dC]"
   },
   "notes": "wartosc ujemna (65436 = -100) zapisuje sie jako s16; odpowiedzi na 0x3004 (4B i ack 60) nie zmieniaja zadnego PID"
  },
  "open": [
   "czy slave odpowiada tez na inne obiekty (kolejne zapytania pojawiaja sie wg poziomu mocy 0x3512..0x3514)",
   "zachowanie przy braku odpowiedzi (offline slave) - wyswietlanie na ekranie Kaskada"
  ]
 }
}```
