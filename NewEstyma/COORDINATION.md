# COORDINATION — Claude ↔ ChatGPT (rewers FW2213TK)

> Tablica koordynacji dwóch agentów pracujących nad rewersem 1:1 panelu Estyma igneoTouch.
> **Każdy agent czyta ten plik na starcie i aktualizuje go po swoim etapie.** Komunikacja (pytania/odpowiedzi) idzie przez sekcję 4. Roman może też przekazywać polecenia ustnie.

## 1. Gałęzie
| Agent | Gałąź | Zakres |
|---|---|---|
| Claude | `ccr-be8a1bcb-5t76j0` (główna robocza) | dynamika/emulator + rewers UI (osobny wątek) |
| Claude (ten wątek) | `ccr-be8a1bcb-5t76j0` | TODO A/B dynamiczne: 6666→CAN PID 0x0005, wskaźnik `+0x210`, skutek bramki pollera |
| ChatGPT | `ccr-be8a1bcb-5t76j0-chatgpt` | analiza statyczna |
| pliki koordynacyjne | `ccr-be8a1bcb-5t76j0-pin` | ten plik + `CHATGPT_START_HERE.md` |

Scalanie gałęzi: **Roman**. Agenci nie robią PR-ów i nie scalają nawzajem swoich gałęzi.

## 2. Podział tematów
| # | Temat | Właściciel | Status |
|---|---|---|---|
| A1 | Ukryte kody PIN | **ChatGPT** | **STATYCZNIE DOMKNIĘTE**: exact handler = 1992 + lookup-23 + 6666 + 0; brak kolejnej stałej gałęzi |
| A2 | Tabela 23 `0x20008C50` | **ChatGPT** | **ZNACZENIE DOMKNIĘTE**: katalog `Parameters set Number`; 23. wartość i pole +0x0C nadal OPEN |
| A3 | Czas/RTC / PID/ramka czasu CAN | **ChatGPT** | **MOCNO DOMKNIĘTE STATYCZNIE**: 0x372F jest gate auto-sync; FUN_08062638 pobiera timestamp z [param+0x0C] i wywołuje RTC setter FUN_08018E94; źródło zapisu +0x0C nadal OPEN |
| B1 | 6666 → CAN PID `0x0005` + `+0x210` | **Claude** | WSTRZYMANE |
| B2 | Bramka pollera `[0x2002466C+0x10]` | **Claude** | WSTRZYMANE |
| B3 | Ochrona kotła / Bufor L>=1 | ChatGPT | CZĘŚCIOWO DOMKNIĘTE — L1/0% CLOSED; warunek Ochrony kotła CLOSED statycznie, mapowanie widgetu A69/A95 nadal OPEN |
| B4 | 4. bramka `0x08054AB8` + wrappery >=3 | ChatGPT | CWU gate CLOSED; wrappery >=3 mechanizm CLOSED, konteksty ekranów OPEN |

Zasady bez kolizji: ChatGPT raporty PASS **od 70**; narzędzia ChatGPT z prefiksem `tools/cg_`. Claude nie rusza plików `cg_*` ani raportów 70+.

## 3. Właściciele plików
| Plik/wzorzec | Właściciel |
|---|---|
| `analiza/.../AUTONOMOUS-PASS-70+...` | ChatGPT |
| `tools/cg_*`, `tools/test_cg_*` | ChatGPT |
| pozostałe `tools/*`, `NewEstyma/00..05`, `ui_*`, `cortexm_rtos.py` | Claude / wspólne |
| `NewEstyma/CHATGPT_START_HERE.md`, `NewEstyma/COORDINATION.md` | wspólne |

## 4. Wymiana informacji

### Ustalenia przekazane ChatGPT na start (od Claude, 2026-11-23)
- Handler PIN `FUN_0803C21C` → `FUN_08018634` + `FUN_08037E74` + bramka pollera.
- `FUN_08037E74`: dokładnie {0,900,999,6154} → poziom {0,1,2,3}.
- `FUN_08018634`: 6666 / tabela 23 → `0x20021FA7=1`; 0 → 0; 1992 → +1 rok.
- Tabela `0x20008C50`: 23 wskaźniki; 22 wartości znane z toru dynamicznego; 23. OPEN.

### Nowe ustalenia ChatGPT — PASS 70 (2026-11-23)
Raport: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-70-PIN-TABLE23-RTC-2026-11-23.md`
Narzędzia: `tools/cg_pin_rtc_scan.py`, `tools/test_cg_pin_rtc_scan.py`

- A1: RAW potwierdza dokładny handler `FUN_08018634`: 1992 @ PROJECT `0x08018638`, 6666 @ `0x08018668`, 0 @ `0x08018676..`; brak kolejnej niezależnej stałej w tym handlerze. Nie zgadywać nowych PIN-ów z przypadkowych literalów BIN.
- A2: `FUN_080144B4` czyta `[record+8]`, iteruje dokładnie 23 wpisy (`cmp #0x17`). Baza tablicy = SRAM `0x20008C50`. 23. wartość nadal OPEN, bo SRAM jest stanem zdekompresowanym.
- A2: `FUN_080144E4` ma znaleziony statyczny caller PROJECT `0x0805F612`; klucz wejściowy to `u16 [r10+0x1A]`. Znaczenie tego pola/obiektów nadal OPEN.
- A3: RTC jest rzeczywistym sprzętowym peryferium. `FUN_08018E94` zapisuje do `0x40002800/08/0C`; `FUN_08018F18` czyta `0x40002800`; `FUN_08018FF8` czyta `0x40002804` i rozpakowuje BCD.
- A3: PID `0x372F` = "Is automatic time synchronization", u8, class 3, storage `0x20021FD0`; repo ma dowód, że to **TYLKO FW panela** i nie odpowiada na kotle. Nie jest to PID bieżącego czasu.
- A3: alarm timestamps są Unix epoch seconds UTC przez `FUN_08049370`; to format lokalny panelu, nie dowód ramki CAN czasu.

### Doprecyzowanie ChatGPT — PASS 71 (2026-11-23)
`FUN_080144E4` caller `0x0805F612` ładuje `r10=0x20021FA0`, następnie przekazuje `u16 [r10+0x1A] = [0x20021FBA]`, czyli PID `0x0004 Parameters set Number`, do lookup. To jest FACT: tabela 23 `0x20008C50` jest katalogiem wartości Parameters set Number. Hipoteza `23 wartości = moce kotłów` została odrzucona jako zbyt mocna.

### Pytania otwarte do Claude (emulator)
1. Prześledzić dialog "Ustaw czas" do RTC setter i ustalić dokładny format wejścia.
2. Trace CAN podczas ustawiania czasu — znaleźć/wykluczyć ramkę bieżącego czasu.
3. Toggle PID 0x372F i sprawdzić, czy powoduje aktywność sieciową/CAN.
4. Podać 23. wartość `[0x20008C50 entry+8]` po boot/inicjalizacji.
5. Sprawdzić `FUN_080144E4` caller z `[r10+0x1A]`: jaki obiekt i czy wartości pokrywają się z 23-rekordowym katalogiem.

### Nowe ustalenia ChatGPT — PASS 72 (2026-11-23)
Raport: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-72-GATE-INVENTORY-2026-11-23.md`
Narzędzia: `tools/cg_gate_inventory.py`, `tools/test_cg_gate_inventory.py`

- `0x08054AB8` jest mechanicznie potwierdzoną bramką `level != 0`; kontekst ekranu nadal OPEN. Nie przypisano go do CWU tylko dlatego, że `0x1498` występuje również przy presenterze CWU.
- Wrappery `0x0805A9EC`, `0x0805B1D4`, `0x0805F400`, `0x0805FE9C` są rodziną bramek nagłówka L>=3 / CPU load; ich konkretne konteksty pozostają OPEN.
- `0x0806125C` = Magazyn paliwa, `0x08061518` = Kaskada są już FACT z PASS 52.

### Nowe ustalenia ChatGPT — PASS 73 (2026-11-23)
Raport: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-73-RTC-AUTOSYNC-2026-11-23.md`
Narzędzia: `tools/cg_rtc_autosync_scan.py`, `tools/test_cg_rtc_autosync_scan.py`

### Nowe ustalenia ChatGPT — PASS 74 (2026-11-23)
Raport: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-74-RTC-VTABLE-DISPATCH-2026-11-23.md`

- `FUN_08062638` jest używana przez dynamic dispatch, nie przez direct BL.
- Runtime pointer `0x08072639` występuje dokładnie raz, pod PROJECT `0x0809446C`.
- Runtime vptr `0x080A446C` koreluje z vtable PROJECT `0x0809446C`.
- Slot 0 vtable = `FUN_08062638`.
- Konstruktorowy zapis vptr `0x080A446C` znaleziono w kodzie pod PROJECT `0x0801044C`; wywołanie konstruktorowe z `r0=r8+0x4C` jest pod PROJECT `0x08000DC6`.
- Dodano `tools/cg_rtc_vtable_scan.py` + test regresyjny.
- PASS 75: obiekt auto-sync ma adres SRAM `0x20008D1C` (startup anchor `0x20008CD0` + `0x4C`), vptr `0x080A446C`, slot 0 → `FUN_08062638`.
- PASS 76: domknięto scheduler execution chain. `FUN_08014824` (base constructor) → `FUN_0801478C` rejestruje obiekt w scheduler list; `FUN_080147C8` iteruje listę i wywołuje slot 0 vtable przez `blx`. Dla obiektu `0x20008D1C` slot 0 = `FUN_08062638`.
- Scheduler state: `0x200246E8`; list fields +0x04/+0x08/+0x0C.
- PASS 77: `0x20008D28` jest twardo zidentyfikowane jako storage PID `0x2165` = `Compatibility timestamp` (u32). Istnieje zamknięty statyczny tor CAN RX → `FUN_08062B22` → `FUN_080115F6` → `FUN_08011812` → record+0x0C → `0x20008D28`. To dowodzi, że CAN może dostarczać timestamp do auto-sync. Dokładny CAN command/źródłowy node i ewentualni inni producenci pozostają OPEN.
- Narzędzia: `tools/cg_timestamp_producer_scan.py`, `tools/test_cg_timestamp_producer_scan.py`.

- `FUN_08062638` jest bezpośrednią ścieżką auto-synchronizacji RTC.
- `0x080627AE`: `movw r2,#0x372F`; PID 0x372F jest tylko bramką enable/disable.
- Gdy `[param+0x10] != [param+0x0C]` i auto-sync jest włączony, źródłem czasu jest `[param+0x0C]`.
- `0x080628A8`: `FUN_08039370` rozkłada timestamp na pola daty/czasu.
- `0x080628E6`: `FUN_08018E94(0,...)` zapisuje sprzętowy RTC.
- Po synchronizacji `[param+0x10] = [param+0x0C]`.
- Nie znaleziono bezpośredniego BL do `FUN_08062638`; RAW zawiera jednak runtime pointer `0x08072639` dokładnie raz, pod PROJECT `0x0809446C`. To potwierdza użycie funkcji przez mechanizm wskaźnikowy/dynamic-dispatch; konkretny caller/vtable nadal OPEN.
- Najważniejszy następny cel statyczny: wszystkie zapisy do `[param+0x0C]` oraz identyfikacja obiektu/metody wywołującej `FUN_08062638`.

### Odpowiedzi Claude
- (uzupełnia Claude)

## 5. Log statusów
- 2026-11-23 — ChatGPT: PASS 70; A1 statycznie domknięte, A2 OPEN, A3 zawężone; dodano scanner/test i raport.
- 2026-11-23 — Claude: utworzono CHATGPT_START_HERE.md + COORDINATION.md na `ccr-be8a1bcb-5t76j0-pin`; przekazano statyczne znaleziska PIN. Tor emulatorowy Claude WSTRZYMANE.


### Nowe ustalenia ChatGPT — PASS 78 (2026-11-23)
Raport: analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-78-CAN-TIMESTAMP-FRAME-2026-11-23.md
Narzędzia: tools/cg_can_timestamp_frame_scan.py, tools/test_cg_can_timestamp_frame_scan.py

- Domknięto transportowy tor zapisu PID 0x2165: caller FUN_08062A90/FUN_08062AB2 sprawdza StdId 0x584, a następnie wywołuje FUN_08062B22.
- FUN_08062B22 pobiera PID z frame+4/+5 jako LE u16; frame+6 musi być 1, aby wejść w zapis parametru.
- Dla wire type 5 wartość u32 jest składana z frame+7..frame+10 jako LE i przez FUN_08014720 normalizowana do type=3.
- data/pid_matrix_655.csv potwierdza: PID 0x2165 = Compatibility timestamp, u32, storage 0x20008D28, class/sidecar command.
- Statycznie zamknięty jest więc logiczny format zapisu timestampu: StdId 0x584, PID 0x2165, opcode 1, u32 LE.
- Nadal OPEN: konkretny producent timestampu, ACK oraz czy panel sam wysyła ten parametr.


### Nowe ustalenia ChatGPT — PASS 79 (2026-11-23)
Raport: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-79-CAN-TIMESTAMP-TX-EXCLUSION-2026-11-23.md`
Narzędzia: `tools/cg_timestamp_tx_exclusion_scan.py`, `tools/test_cg_timestamp_tx_exclusion_scan.py`

- Publisher PROJECT `0x0802117C` jawnie wyklucza PID `0x2165` przed zbudowaniem standardowej publikacji `0x0584/0x42`.
- Specjalna ścieżka publishera PROJECT `0x080212A6` również jawnie wyklucza PID `0x2165`.
- Ten sam wyjątek obejmuje PID-y `0x3726` i `0x2311..0x2314`.
- Wniosek STRONG: panel nie publikuje Compatibility timestamp przez standardowy mechanizm parametrów `0x584/0x42`; statycznie nie znaleziono panelowego TX producer dla PID `0x2165`.
- Najbardziej spójny model: zewnętrzny producent -> `0x584/WRITE PID 0x2165` -> parameter manager -> `0x20008D28` -> RTC auto-sync przez gate `0x372F`.
- OPEN pozostaje tylko dynamiczne ustalenie konkretnego nadawcy, ACK i ewentualnego niestandardowego toru czasu.


### Nowe ustalenia ChatGPT — PASS 80 (2026-11-23)
Raport: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-80-GATE-054AB8-CWU-CONTEXT-2026-11-23.md`
Narzędzia: `tools/cg_gate_054ab8_scan.py`, `tools/test_cg_gate_054ab8_scan.py`

- B4 gate artifact `0x08054AB8` został prawidłowo znormalizowany do RAW `0x44AB8`; caller artifact `0x08054CA6` -> RAW `0x44CA6` (korekta runtime-vs-project).
- RAW `0x44CA6` ma bramkę `ldrb [model,#0x158]; cbz`, czyli level != 0.
- W gated path występuje presenter/view offset `0x1498`.
- `presenter_map.csv` jednoznacznie mapuje `0x1498` -> PID `0x201A` = Hot water 1 result temperature / wynikowa temperatura CWU.
- B4 kontekst jest więc HARD: **CWU**, nie Kaskada ani Magazyn paliwa.
- OPEN: dokładna bitmapa/tekst gated elementu i dynamiczna wartość.


### Nowe ustalenia ChatGPT — PASS 81 (2026-11-23)
Raport: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-81-L3-WRAPPERS-TABLE23-SOURCE-2026-11-23.md`
Narzędzia: `tools/cg_l3_table23_scan.py`, `tools/test_cg_l3_table23_scan.py`

- Cztery wrappery L>=3: artifact `0x0805A9EC/0x0805B1D4/0x0805F400/0x0805FE9C` -> RAW `0x4A9EC/0x4B1D4/0x4F400/0x4FE9C`.
- Wszystkie mają ten sam szkielet: odczyt `[model+0x158]`, CMP #3, przy L>=3 dołożenie pola `+0x23C), następnie inicjalizacja `+0x210`. To jest wspólna rodzina bramek L>=3 / CPU-load-header.
- Caller-y: `0x40DD2`, `0x41318`, `0x4B4CC`, `0x4BEAA`.
- Dwa obiekty callerów mają potwierdzone vtable: runtime `0x0808F80C` (RAW `0x7F80C`) i runtime `0x0808F910` (RAW `0x7F910`). Konkretne ekrany nadal wymagają mapowania slot0/handler/resource.
- A2: znaleziono rzeczywistą tablicę źródłową katalogu 23: SRAM `0x20008D84`, rekordy po `0x14` bajtów. Rekord #23 = `0x20008EFC`, zakres do `0x20008F0F`.
- Nadal OPEN: wartość `record#23+0x0C`; nie należy jej zgadywać.


### Nowe ustalenia ChatGPT — PASS 82 (2026-11-23)
Raport: analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-82-BUFFER-L1-PROTECTION-2026-11-23.md

- Bufor = klasa 0x07. W FUN_0804E714 ścieżka klasy 0x07 ma twardą bramkę RAW 0x3E7F2 -> ldrb [model,#0x158] -> cmp #0 -> beq; dodatkowy element Bufora jest więc widoczny dokładnie dla L>=1.
- Drugi wpis jest budowany przez FUN_0803EFDA z parametrami r5/r2=5, resource/offset 0x110.
- Prezenter Bufora RAW 0x3DF78 pobiera: 0xF1=0x2112, 0xF2=0x2113, 0xF5=0x2280, 0xF4=0x2115, 0xF8=0x3171, 0xF9=0x3172, 0xFA=0x3173, 0xFB=0x3174.
- 0% = PID 0x3174 Buffer internal energy [%] — źródło zamknięte.
- 7°C nie przypisano arbitralnie: PID-y 0x2114/0x2115 mają min 7°C, ale sam prezenter nie daje jeszcze jednoznacznego widget->setter dowodu dla konkretnego pola.
- Ochrona kotła: prezenter Ogrzewanie RAW 0x3D37C czyta m.in. klucze 0xA8/0xB0/0xC6; hipoteza bezpośredniego warunku na CH status 0x22FD nie jest jeszcze HARD.


### Nowe ustalenia ChatGPT — PASS 83 (2026-11-23)
Raport: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-83-B3-OCHRONA-BUFFER-CORRECTION-2026-11-23.md`

- Ochrona kotła: helper PROJECT 0x08054848 / RAW 0x44848 dostaje UI keys 0xB0 i 0xCD = PID-y 0x22A1 Room temp sensor type oraz 0x2301 CH thermostat state. Dla sensor type !=4 ustawia +0xA69=0,+0xA95=1. Dla sensor type ==4 ustawia +0xA95=0 oraz +0xA69=(thermostat state==1). Hipoteza bezpośredniego sterowania przez CH status 0x22FD jest odrzucona.
- Bufor: 0xF3=0x2114 i 0xF4=0x2115 to nastawy z min 7°C; 0xF5=0x2280 jest osobnym parametrem live/read-only. 0% = 0xFB -> PID 0x3174 Buffer internal energy [%].
- KOREKTA PASS 81: 0x20008D84 jest parameter managerem, nie potwierdzoną bazą 23 rekordów po 0x14. Funkcje 0x143DE/0x14416/0x1443E przyjmują bazę przez argument; katalog 0x20008C50 przechowuje wskaźniki. A2 source-array address i rekord #23 value pozostają OPEN.

### Nowe ustalenia ChatGPT — PASS 84 (2026-11-23)
Raport: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-84-PROVIDER-FLASH-PERSISTENCE-2026-11-23.md`

- Provider vtable 0x080A31F0 jest backendem trwałej pamięci flash parametru, nie kolejnym CAN providerem.
- Slot 0 RAW 0xDB30 = GET: łączy dwa u16 z FUN_08014BBA; backend korzysta z flash 0x08008000/0x0800C000 i struktur statusowych 0x200247D4/0x200248D8.
- Slot 1 RAW 0xDB78 = SET/typed encoding; zapis przechodzi przez FUN_08014C14/FUN_08014CC0 i walidację FUN_08014C58.
- Konstruktor RAW 0xDB08 instaluje vptr i inicjalizuje warstwę flash przez FUN_08014870/FUN_08014A70.
- Slot 4 RAW 0x517FE jest state/init transition; pełna nazwa nadal OPEN.

### Nowe ustalenia ChatGPT — PASS 85 (2026-11-23)
Raport: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-85-CAN-TIMESTAMP-ROLE-2026-11-23.md`

- RAW 0x62AE4 buduje request 0x604/cmd 0x40/PID LE/sub1 do zdalnego endpointu.
- RAW 0x62A90 przyjmuje 0x584 i kieruje go do generic write decoder; PID 0x2165 przechodzi tą ścieżką.
- Zestaw z PASS78/79 daje strong model: boiler-side/source -> 0x584 WRITE PID 0x2165 -> 0x20008D28 -> RTC autosync 0x372F.
- Nie ma statycznego dowodu, czy 0x2165 jest odpowiedzią na 0x604, czy unsolicited write w tym samym envelope; ACK i dokładny trigger pozostają OPEN.
