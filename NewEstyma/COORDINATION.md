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



### Nowe ustalenia ChatGPT — PASS 126 (2026-11-23)
Raport: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-126-PROVIDER-SLOT4-EXACT-TARGET-2026-11-23.md`

- Provider vtable RAW `0x931F0` ma sloty: 0=`0x0801DB31`, +4=`0x0801DB79`, +8=NULL, +C=NULL, +10=`0x080617FF`.
- `0x080617FF` jest interior entry `+0x23` funkcji `FUN_080617DC`, czyli CAN2 RX mailbox serializer; nie jest to potwierdzony "state/init" provider method.
- Poprzednia etykieta slotu 4 jako state/init została superseded. Dokładny basic-block/CFG wejścia +0x23 pozostaje OPEN do czasu odzyskania raw bytes/CFG.



### Nowe ustalenia ChatGPT — PASS 127 (2026-11-23)
Raport: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-127-SIDECAR-CLASS-MATRIX-CLOSURE-2026-11-23.md`

- R(i)+0x2C jest twardo zamknięte jako rejestracyjna/state class byte dla dwóch mechanizmów: guarded write i provider sync.
- class 1: akceptowana przez guarded write, nie wybierana przez sync.
- class 2: wybierana przez provider sync, odrzucana przez guarded write.
- class 3: wybierana przez provider sync i akceptowana przez guarded write; wszystkie 3 bezpośrednie rejestracje FUN_0801143C mają class=3 (0x3500/0x3502/0x350B).
- Dokładne biznesowe znaczenie klas oraz dynamiczne rejestracje pozostają OPEN.

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


### Nowe ustalenia ChatGPT — PASS 112 (2026-11-23)
Raport: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-112-UI-MODEL-HOME-BINDING-2026-11-23.md`

- Potwierdzono na bazie `data/presenter_map.csv` + `data/widgets_home_with_view_off.json`, że model UI należy łączyć przez `view_off`, a nie przez geometrię/ID bitmapy.
- Home root widoku ma `this=0x2001603c`, `view_off=4`; dzieci są w tym samym obiekcie z offsetami.
- Presenter map potwierdza m.in. Home PID bindings: 0x2001 -> Boiler temp, 0x2004 -> Boiler set result temp, 0x2005 -> Boiler on/off, 0x2007 -> Burner state, 0x2105 -> Heating configuration, 0x2014 -> Hot water program, 0x3728 -> Is reset required.
- Kocioł visual helper 0x08054848 ma HARD input pair 0x22A1 + 0x2301; nadal nie przypisuję arbitralnie A69/A95 do TypedText 87.
- Bufor: presenter map potwierdza 0x2280, 0x2115 i 0x3174; 7°C nadal OPEN na poziomie widget->setter.
- Pass nie zmienia właścicieli ani nie przejmuje dynamicznych zadań Claude.

### Następny autonomiczny target ChatGPT
S1: CFG-aware closure widget/view_off -> presenter setter -> UI key/PID dla ekranów Home/Kocioł/Bufor, z osobnym audytem A69/A95 i pola 7°C.

### Nowe ustalenia ChatGPT — PASS 113 (2026-11-23)
Raport: analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-113-A69-A95-7C-BINDING-2026-11-23.md

- Z widgets_invm2_L2_partial.json zamknięto konkretny widget etykiety „Ochrona kotła”: screen OGRZEWANIE 1, this=0x200177ec, view_off=6068, text_id=30, widoczny.
- Bezpośrednio obok znajduje się obraz this=0x20017820, view_off=6120, bitmapa 130, widoczny.
- To jest twarde zamknięcie lokalizacji/zasobów UI, ale nie dowód, czy A69 czy A95 jest źródłem widoczności tego konkretnego labela.
- Resolver T2 potwierdza: 0xF3 -> 0x2114, 0xF4 -> 0x2115, 0xF5 -> 0x2280; 0x2114/0x2115 mają min=7, a 0x2280 min=25.
- W presenter_map.csv nie ma obecnie wpisu dla UI key 0xF3 -> 0x2114; istnieje HARD wpis 0xF4 -> 0x2115 przez setter 0x08056040 oraz 0xF5 -> 0x2280 przez setter 0x08056028.
- Nie wolno twierdzić, że widget 7°C jest już przypisany do 0x2114. Jego dokładny setter/widget binding pozostaje OPEN.

### Następny target
S1.1: CFG/XREF 0x08054848 -> zapis A69/A95 -> obiekt/widget view_off 6068/6120; równolegle domknąć brakujący presenter setter dla UI key 0xF3/PID 0x2114 i jego widget offsets.

### Nowe ustalenia ChatGPT — PASS 114 (2026-11-23)
Raport: analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-114-UI-BINDING-NEGATIVE-AUDIT-2026-11-23.md

- Dodano konserwatywny audyt obecności par UI-key/PID w presenter_map.
- 0x00F3 -> 0x2114 NIE występuje jako para w presenter_map; nie jest to dowód, że parametr nie jest używany.
- 0x00F4 -> 0x2115 jest obecne przez setter 0x08056040.
- 0x00F5 -> 0x2280 jest obecne przez setter 0x08056028.
- 0x00B0 -> 0x22A1 i 0x00CD -> 0x2301 są obecne; helper 0x08054848 pozostaje twardym źródłem A69/A95.
- Pole 7°C nadal OPEN; nie promować 0x2114 bez widget->setter proof.
- UI-MODEL pozostaje metodą pomocniczą, nie źródłem semantycznego dowodu przy wieloznacznych offsetach.

### Następny autonomiczny target ChatGPT
S1.2: statyczne XREF/CFG callsite analysis dla helpera 0x08054848 oraz setterów 0x08056028/0x08056040; celem jest ustalenie obiektów/widgetów wywołujących te settery bez opierania się na samej geometrii.

### Nowe ustalenia ChatGPT — PASS 115 (2026-11-23)
Raport: analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-115-UI-CONTEXT-REGISTRY-2026-11-23.md

- Nie promujemy już view_off jako samodzielnego semantycznego dowodu UI.
- Zamknięto statycznie relację registry selector -> FUN_0803C064 -> +0x12B -> page-family resource.
- selector 16 -> +0x12B=0x11; selector 17 -> +0x12B=0x10; selector 18 -> osobna ścieżka.
- Context 3: 0x10->resource 0x35, 0x11->0x37, pozostałe->0x32.
- Context 2: +0x12B switch 0..10 -> rodzina resources 0x28..0x31.
- +0x12C pozostaje niezależnym active-instance selector 1..4.
- Nadal OPEN: semantyka rekordów 16/17/18 oraz A69/A95->widget 6068/6120 i F3/2114->widget.

### Następny autonomiczny target
S1.3: odzyskać source/runtime registry dla rekordów 16/17/18 i połączyć je z title/resource/PID/callback. Nie używać geometrii ani bitmap ID jako jedynego dowodu.

### Nowe ustalenia ChatGPT — PASS 116 (2026-11-23)
Raport: analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-116-REGISTRY-CLAUDE-TODO-AUDIT-2026-11-23.md

- Potwierdzono łańcuch FUN_0807EB00 -> registry +0x3B4/stride 0x274 -> FUN_0803C064 -> tabela 0x20005EF0.
- Selector 16 -> FUN_0803856C -> +0x12B=0x11; selector 17 -> FUN_08038568 -> +0x12B=0x10; selector 18 -> FUN_08038574.
- Ostatnie zadania dynamiczne Claude (B1/B2: 6666/PID 0x0005/+0x210 oraz poller +0x10) nadal są WSTRZYMANE; brak podstaw do oznaczenia ich jako wykonane.
- S1.3 pozostaje OPEN: title/PID/resource/callback rekordów 16/17/18 wymagają source/runtime initialization i descriptor binding.

### Następny autonomiczny target ChatGPT
S1.3 kontynuacja: XREF źródła registry 0x20005EF0 + inicjalizacja rekordów +0x3B4+i*0x274 oraz pola descriptorów. Równolegle S1.2: helper 0x08054848 i settery 0x08056028/0x08056040.


### Nowe ustalenia ChatGPT — PASS 118 (2026-11-23)
Raport: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-118-SELECTOR-16-17-18-DESCRIPTOR-CLOSURE-2026-11-23.md`

- Selector 16 i 17 używają dokładnie tego samego rekordu descriptor `0x38790` -> callback/config `0x08048493`.
- Selector 16 -> `+0x12B=0x11`; selector 17 -> `+0x12B=0x10`.
- Selector 18 używa osobnego descriptor `0x387B8` -> callback/config `0x080485A1`; case 18 samo nie zapisuje `+0x12B`.
- Wszystkie trzy kończą przez wspólny `FUN_08039494 -> FUN_080394A8` i instalację obiektu pod `+0x110`, wskaźnik w `+0x10C`.
- To zamyka dokładne wskaźniki callback/config; semantyka PID/resource/title nadal OPEN.

### Następny autonomiczny target ChatGPT
Decompilacja/CFG callbacków `0x08048493` i `0x080485A1` oraz ich XREF do presenter/PID/resource. Równolegle S1.2: `0x08054848`, `0x08056028`, `0x08056040`.
### Nowe ustalenia ChatGPT — PASS 119 (2026-11-23)
Raport: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-119-CALLBACK-ENTRY-NORMALIZATION-2026-11-23.md`

- Descriptor `0x38790 -> 0x08048493` jest Thumb entry pointem wewnątrz `FUN_08048468` (+0x2B), nie niezależnym startem funkcji.
- Descriptor `0x387B8 -> 0x080485A1` jest Thumb entry pointem wewnątrz `FUN_0804858A` (+0x17).
- Semantyki nie wolno dziedziczyć z początku funkcji kontenera bez CFG dowodu dla konkretnego entry pointu.

### Nowe ustalenia ChatGPT — PASS 120 (2026-11-23)
Raport: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-120-CALLBACK-CFG-S12-AUDIT-2026-11-23.md`

- Nie znaleziono w aktualnie zapisanych artefaktach repo dokładnego raw instruction/CFG body dla `0x08048493` ani `0x080485A1`; oba pozostają OPEN na poziomie basic-block.
- 16/17 nadal dzielą dokładnie ten sam entry `0x08048493`; ich twardym rozróżnikiem pozostaje `+0x12B=0x11` vs `0x10`.
- 18 używa `0x080485A1` i nie zapisuje `+0x12B` w samym case.
- S1.2: brak nowego callsite artifact dla `0x08054848`, `0x08056028`, `0x08056040`; istniejące dowody pozostają bez zmian: `0xF4->0x2115`, `0xF5->0x2280`, `0xF3->0x2114` nadal bez exact presenter pair.
- Nie wykonano żadnego semantycznego overclaimu.

### Następny autonomiczny target ChatGPT
Jeżeli pojawi się/da się odzyskać raw instruction listing: natychmiast CFG entry `0x08048493` i `0x080485A1`, następnie outgoing calls. Równolegle szukać callsite/XREF artefaktów S1.2; nie promować 7°C ani A69/A95 bez exact binding proof.
### Nowe ustalenia ChatGPT — PASS 121 (2026-11-23)
Raport: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-121-CLAUDE-TODO-STATIC-CLOSURE-2026-11-23.md`

- A1 hidden PIN: statycznie CLOSED — 900/999/6154 są jedynymi proven access-level PINs; 1992/6666/0 są specjalnymi stałymi w handlerze; nie ma podstaw do dopisywania kolejnych PIN-ów.
- A2 tabela 23: mechanizm/rola CLOSED jako katalog Parameters set Number; exact entry #23 nadal OPEN.
- B3: Heating 7°C CLOSED jako UI key 0xCB -> PID 0x22F5 (CH needed temp), więc nie jest to 0x2114. Buffer 0% i Buffer 7°C nadal OPEN.
- B4: gate 0x08054AB8 CLOSED jako level!=0 w kontekście CWU; L>=3 wrapper family CLOSED mechanicznie, indywidualne konteksty pozostają OPEN.
- B1/B2 pozostają WSTRZYMANE, bo wymagają wykonania firmware/emulatora i obserwacji dynamicznej.

### Aktualny stan właścicieli po PASS 121
- ChatGPT: statyczny rewers + narzędzia + dokumentacja.
- Claude: dynamic/emulator B1/B2; bez nowych wyników nie oznaczać jako CLOSED.
- S1.3: callback entries 0x08048493/0x080485A1 nadal OPEN do raw CFG.
- S1.2: helper/setters nadal wymagają exact caller/widget proof.
### Nowe ustalenia ChatGPT — PASS 122 (2026-11-23)
Raport: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-122-RAW-ARTIFACT-COMPLETENESS-2026-11-23.md`

- Wykonano repository-wide tree scan aktywnej gałęzi dla artefaktów 0x080485/0x080548/0x080560.
- Jedyny znaleziony raw snippet z rodziny 0x080485xx to `08048520-decompiled.c.txt`.
- Brak committed raw/decompiled artifactów dla 0x0804858A/entry 0x080485A1 oraz dla 0x08054848, 0x08056028, 0x08056040.
- To zamyka hipotezę, że obecne artefakty zostały tylko przeoczone; potrzebny jest nowy eksport Ghidra/BIN dla dalszego CFG/XREF.

### Aktualny hard boundary
- Statyczne TODO Claude: wszystko możliwe do zamknięcia bez wykonania firmware zostało oznaczone w PASS 121.
- B1/B2: WSTRZYMANE dynamiczne.
- S1.3/S1.2: OPEN wyłącznie z powodu braku wymaganych instrukcji/XREF w repo.

### PASS 123 — parameter engine evidence hardening — 2026-11-23

- Hardened `software/model/parameter_engine.py`: +0x14/+0x1C/+0x24 are descriptor-derived outputs, not proven raw scalar fields.
- +0x2C/+0x30 are next-record boundary/next-record data, never fields of the current record.
- Sidecar access classes: 0..3 correlate with access class; write gate accepts 1/3; synchronization covers 2/3; full 1/2/3 semantics remain OPEN.
- 260/568/660 remain separate namespaces: catalog / mapper / runtime scan bound.
- Report: `AUTONOMOUS-PASS-123-PARAMETER-ENGINE-EVIDENCE-HARDENING-2026-11-23.md`.
- Code commit: `3e35a33d530d53d29e70dd41c2b1349c6ff35a7f`.
- Report commit: `247a2b50b1c22090c9a6f2602c4a6ed033820dd7`.

Next: descriptor engine, provider slots, 260-row matrix, publication timing, callback CFG. B1/B2 remain dynamic-only.

### PASS 124 — provider/publication consistency audit — 2026-11-23
- Reconciled historical vs current provider evidence: slot0 GET and slot+0x04 SET are HARD; provider slot4 remains state/init OPEN by semantic name.
- Reconfirmed sink 0x20008D60 / vptr 0x080A4544 / slot0 FUN_0806E59C and the closed machine-level publication bridge.
- Reasserted descriptor boundary from PASS 123 and separation of 260/568/660 namespaces.
- Report: `AUTONOMOUS-PASS-124-CURRENT-STATE-CONSISTENCY-PROVIDER-PUBLICATION-2026-11-23.md`.
- Report commit: `b3c9379a7e0c752902ccb5b7b31a6d3be22f68ba`.

### PASS 125 — extra TX callers negative closure — 2026-11-23
- 0x08056A1C and 0x08056A44 are confirmed direct transfers to queue function 0x08057224, but no current committed body/context proves they are parameter-publication producers.
- They remain separate OPEN transport producers; no PID/StdId/command semantics were assigned.
- Report: `AUTONOMOUS-PASS-125-EXTRA-TX-CALLERS-NEGATIVE-CLOSURE-2026-11-23.md`.
- Report commit: `f11c53787fd927179cdf8a8af3ac891bc00a7124`.

Next autonomous targets: descriptor engine 0x08014728/0x08014734/0x0801155A; provider slot4; 260-slot direct evidence; publication timing/shadow; remaining UI class chains. B1/B2 remain dynamic-only.
