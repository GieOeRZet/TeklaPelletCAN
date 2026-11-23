# PEŁNY RAPORT PRAC CHATGPT / OPENAI DLA CLAUDE
## NewEstyma / TeklaPelletCAN — stan 2026-11-23

> Raport zbiorczy przekazujący Claude'owi cały wykonany przez ChatGPT zakres RE. Jest to dokument handoff, nie nowy etap analizy.
> Źródła: `NewEstyma/00_AGENT_START_HERE.md`, `NewEstyma/01_PROJECT_STATE.md`, `DOKUMENTACJA/REVERSE_ENGINEERING_MASTER_2026-11-22.md` oraz raporty AUTONOMOUS-PASS w `analiza/FW2213TK-2026-11-22/`.

---

# 1. CEL I ZASADA PRACY

Cel projektu:
- możliwie pełne odtworzenie Estymy 1:1,
- implementacja uniwersalna, nie tylko pod jeden konkretny kocioł,
- docelowo ESP32-C6 + CAN + Home Assistant/Web/Android,
- ESP32/HA są odłożone do czasu domknięcia rewersu 1:1.

Podział pracy:
- ChatGPT/OpenAI: statyczny reverse engineering, skanery, korelacje, dowody RAW, dokumentacja i raportowanie;
- Claude: dynamic/emulator, UI i dalsza korelacja wykonawcza.

Zasady:
- RAW BIN jest źródłem prawdy;
- PROJECT = 0x08000000 + RAW;
- RUNTIME = PROJECT + 0x10000;
- HARD != ukończenie projektu;
- FACT / STRONG / INFERENCE / OPEN / REJECTED są rozdzielane;
- odrzucone hipotezy są zachowywane;
- każde istotne domknięcie ma raport;
- nie wolno promować hipotezy bez dowodu.

Firmware:
- `FW2213TK_kopia.bin`
- 0x1F0000 = 2,031,616 B
- SHA-256: `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`
- firmware nie jest commitowany do repo.

---

# 2. STAN POCZĄTKOWY / FUNDAMENTY REWERSU

W pierwszej fazie ChatGPT wykonał szeroki reverse engineering firmware:
- mapowanie RAW/PROJECT/RUNTIME,
- skany BL/XREF,
- skany ASCII/UTF-16,
- inwentaryzację funkcji,
- analizę tabel parametrów,
- analizę CAN2,
- analizę obiektów i vtable,
- identyfikację parameter managera,
- identyfikację warstwy UI/resources.

Globalne statystyki z master RE:
- 11,337 krawędzi BL,
- 2,810 unikalnych targetów BL,
- 9,656 ASCII >=5,
- 5,604 ASCII >=7,
- 3,957 UTF-16LE >=5,
- 3,299 UTF-16LE >=7.

Najważniejsze anchory:
- CAN2 = `0x40006800`
- parameter manager = `0x20008D84`
- provider = `0x20008D64`
- publication sink = `0x20008D60`
- manager vtable = `0x080A44F0`
- provider vtable runtime = `0x080A31F0`
- provider vtable PROJECT = `0x080931F0`
- provider vtable RAW = `0x931F0`
- provider slot0 = GET
- provider slot1 = SET
- manager callback = `FUN_08010FCE`
- runtime parameter stride = `0x2C`
- runtime scan bound = 660
- catalog = 260 entries
- READ = StdId `0x0604`, command `0x40`
- publication = StdId `0x0584`, command `0x42`.

---

# 3. PASS 1–18 — PARAMETER CATALOG / INIT / RESOLVER

W pierwszym dużym bloku pracy odzyskano katalog 260 parametrów oraz ich warstwę inicjalizacji.

Najważniejsze wyniki:
- 260 unikalnych slotów,
- 260 unikalnych param_id,
- brak duplicate param_id,
- brak duplicate slotów,
- katalog znajduje się w okolicy RAW `0x037578`,
- 247 pozycji ma init caller `0x0801143C`,
- 11 ma bezpośredni init `0x08014700`,
- 248 ma przynajmniej jeden z tych mechanizmów,
- 12 nie ma żadnego z tych dwóch mechanizmów,
- w analizowanym `0x08014700` występuje 512 różnych non-catalog PID,
- znaleziono 409 string entries w zakresie RAW `0x024C00..0x027700`.

Zidentyfikowane funkcje:
- resolver `0x08010FC2`,
- `0x08014700` / `08/10/18/20` — warianty zapisu z typami,
- `0x08014734` — getter według typu,
- `0x080115F6` — lookup runtime records,
- `0x08011812` — update/commit.

12 pozycji bez bezpośredniego matchu init:
```
0x002a -> 0x4000
0x002c -> 0x211a
0x0049 -> 0x3002
0x0060 -> 0x3000
0x0074 -> 0x2269
0x0080 -> 0x228d
0x0081 -> 0x228e
0x0082 -> 0x228f
0x0095 -> 0x218b
0x00a1 -> 0x3700
0x00f5 -> 0x2280
0x0112 -> 0x3500
```

Istotne korekty:
- brak matchu nie oznacza braku parametru;
- katalog 260 NIE jest kompletną tabelą runtime;
- nie wolno utożsamiać indeksu katalogu z PID bez dowodu.

---

# 4. PASS 15–18 — DALSZA WERYFIKACJA INIT

Dla PID `0x218C` odnaleziono realną inicjalizację:
```
MOVW R0,#0x218C
MOVS R1,#0x28
ADD R0,R4
BL 0x08014700
```
czyli default = 40.

Sekwencja sąsiednich parametrów:
`2174, 218C, 2198, 21A4, 21B0, 21BC, 21C8, 21D4, 21E0`.

Powstała unified platform-agnostic catalog.

---

# 5. PASS 19–34 — OBIEKTY UI / RUNTIME CLASS / CALLBACK / MENU FOUNDATION

W tej fazie odzyskano strukturę obiektową UI i runtime class layer.

Najważniejsze domknięcia:
- 21-entry runtime-class TBB graph,
- generic runtime classes zbiegają do `0x08037F88`,
- obiekt tworzony/kopiowany jest pod parent+0x110,
- vtable tymczasowego obiektu = `0x0809F848`,
- callback/config pointer pool = RAW `0x386A8..0x387D8`,
- klasy 1..4 współdzielą `0x08038130`,
- class 14 kończy się natychmiast,
- class 12 ma specjalną ścieżkę parameter-managera,
- class 15 omija generic construction przez `0x08042318 -> 0x0802EADE`,
- classes 16/17 współdzielą `0x08038488`,
- class 18 ma osobny builder,
- callback `0x08048037` zapisuje parent+0x12A = 1.

Vtable `0x0809F848`:
- sloty 2/3,
- 8/9,
- 14/15,
tworzą trzy powtarzające się pary metod callback/state.

Class 12:
- początkowo zidentyfikowana jako operacja na runtime key 3;
- `0x080373BA` pobiera key 3, inkrementuje i zapisuje;
- caller wykonuje drugi increment i modulo 8;
- później PASS 35 wykazał, że key 3 = PID `0x0003` = Language;
- finalnie class 12 = zmiana języka.

Języki:
- 0 PL
- 1 EN
- 2 LT
- 3 SK
- 4 CZ
- 5 ES
- 6 RO
- 7 EST.

Ważna korekta:
- wcześniejsze określenie „logical key 3” zostało zastąpione przez „runtime parameter lookup key 3”, a następnie zamknięte jako PID 0x0003.

---

# 6. PASS 35–39 — RUNTIME PARAMETER TABLE I CAN

## PASS 35
Uruchomienie firmware w emulatorze i odczyt tabeli runtime:
- 655 rekordów aktywnej tabeli po starcie,
- runtime key = PID,
- 448/448 katalogowych PID znalezionych,
- key 3 = PID 0x0003 Language,
- storage Language = `0x20021FAA`,
- `0x200208EC` = blok ustawień,
- +0x16C3..+0x16C6 = 0x2105..0x2108,
- resolver `0x08036FF2` ma dwie tabele,
- tabela 1 = 49 rekordów CH,
- tabela 2 = 372 rekordy.

## PASS 36
Sidecar class `record+0x24` = tryb dostępu:
- 0 live — 208,
- 1 komenda — 49,
- 2 lustro z centrali — 44,
- 3 nastawa — 354.

Zgodność 448/448 z katalogiem panelu.

Kluczowe:
- `0x300B` = Stop burning wood,
- class 1 = command.

## PASS 37
CAN READ:
`0x0604 / 0x40 / PID LE / sub 1`.

Poller:
- 655 żądań,
- każdy PID raz,
- RX `0x0584 / 0x42 / sub 1`,
- zapis wartości z walidacją min/max,
- działa także dla live i wartości signed.

Silna zgodność z CANopen SDO expedited została odnotowana, ale nie należy jej rozszerzać poza dowód.

## PASS 38
Lokalna zmiana Language 0->7:
- dokładnie jedna ramka `0x584`,
- DLC 8,
- `42 03 00 01 07 xx xx xx`,
- brak powtórzeń bez zmiany.

Ważne:
- `0x08011812` NIE jest automatycznie dirty-bit/TX setterem;
- bridge lokalna zmiana -> CAN pozostawał wtedy częściowo OPEN.

## PASS 39
Class 12 finalnie zamknięta jako setLanguage:
- GET PID 0x0003,
- +1,
- SET modulo 8,
- tail-call setLanguage,
- 8 wpisów językowych.

---

# 7. PASS 40–47 — MENU, EMULATOR, TOUCH, ACCESS LEVELS, BITMAPY

## PASS 40
Wiersze menu budowane są w firmware.
- access 0: rows 0..14,
- access 3: rows 0..20,
- vptr ekranu = `0x0808F66C`,
- rows +0xF8 = `0x0807C540`.

Korekta:
- argumenty `FUN_0804BC6C(row,A,B)` = bitmap IDs, nie teksty.

## PASS 41
Touch/menu dispatch:
- `FUN_0807EB00`,
- sender -> row index,
- `FUN_0803C064(this+0x3C,i)`,
- runtime class z `0x20005EF0[i]`.

Wykonanie:
- row 15 / class 12 = language,
- rows 2..5 / classes 1..4 = wybór CO1..CO4,
- zapis +0x12B/+0x12C = 1..4.

## PASS 42
Pełna emulacja systemowa:
- FreeRTOS,
- GUITask,
- EstymaTask,
- CanRxTask,
- CanTxTask,
- IDLE,
- LTDC 480x272 RGB565,
- DMA2D,
- double buffering,
- firmware sam wyrenderował ekran główny,
- 1352 operacje DMA2D.

## PASS 43
CAN boot traffic:
- panel zaczyna TX po ~3.3 s,
- heartbeat 0x704,
- SDO do node 5,6,7,
- publikacje 0x584,
- rodziny PDO-podobne,
- skan `0x1018:02`,
- tablica obecności node'ów.

Ważne:
- heartbeat/identity nie otwierały pollera 0x604,
- bramka pollera jest ustawiana przez kod UI/menu.

## PASS 44
FT5x06:
- I2C1,
- adres 0x38,
- ~25 Hz,
- x_screen = 0.375*x_raw,
- y_screen = 0.354*y_raw.

Emulowane/zweryfikowane ekrany:
- Ustaw czas,
- Paliwo,
- MENU,
- Kocioł,
- Palnik,
- Ogrzewanie 1,
- Historia alarmów.

## PASS 45
Po ustawieniu konfiguracji:
- 0x2105=4,
- 0x2106=1,
- 0x2107=1,
- 0x2108=1,

menu obejmuje:
- Kocioł,
- Palnik,
- CO1..CO4,
- CWU,
- Solary,
- Bufor,
- Historia alarmów,
- Informacje o programie,
- Konfiguracja,
- Poziom menu/PIN.

Konfiguracja -> PID:
- 0x3720 = 12 h,
- 0x372A = lato 18,
- 0x3747 = kalibracja 0.0,
- 0x3603 = rezerwa paliwa 40 kg,
- 0x372F = auto synchronizacja zegara,
- 0x3601 = Paliwo 180 kg.

PIN:
- 6154 daje level 3,
- znika kłódka z kafelka palnika.

## PASS 46
Wykonanie `FUN_0803E714` dla klas 0..0x11 i poziomów 0..3.

Liczby parametrów:
- Kocioł 3/13/13,
- CO 12/23/23,
- CWU 8/12/12,
- Solary 3/7/7,
- Bufor 2/7/7,
- Kaskada 9,
- Dod. magazyn 4/7/7,
- Palnik 5/24/28,
- Konfiguracja 5/24/26,
- Statystyki 13.

Poziom 3 = dodatkowa warstwa w tym konstruktorze.

## PASS 47
Eksport 188 bitmap:
- descriptor table RAW 0x54450,
- 188 rekordów,
- RGB565 + opcjonalny A8,
- wszystkie 000..187 wyeksportowane,
- manifest SHA256.

Audit access gates:
- 52 odczyty model+0x158,
- 17 x >=3,
- 13 x !=0,
- 2 x >=2,
- brak porównań ==,
- poziomy są kumulatywne.

---

# 8. PASS 48–58 — DOMKNIĘCIA UI / ALARMÓW / EKRANU GŁÓWNEGO / ZASOBÓW

W tym bloku ChatGPT przygotował i przekazał Claude'owi dalsze dane do odtworzenia UI:
- katalog widgetów i ekranów,
- mapowanie zasobów,
- atlas ekranów,
- alarmy,
- ekran główny,
- Kaskada/Internet,
- kłódkę „zakazu rozpalania”,
- korelacje tekstów i bitmap,
- obserwacje sliderów,
- przygotowanie dalszego UI model/action graph.

Najważniejsze zamknięcia wynikające z tej fazy:
- komplet 188 bitmap jest dostępny i zweryfikowany,
- alarmy i część ekranów głównych zostały odwzorowane,
- `0x2006` = Burner external permission,
- kłódka UI jest zależna od tego PID-u,
- sama ramka 0x2006 wysłana do panelu nie jest dowodem fizycznej blokady kotła.

Slider:
- dialog numeryczny: tło 163 + niebieskie wypełnienie 165,
- gradient temperatur: 163 + 167,
- power: 186 + 187,
- w nowym UI właściciel chce gradient na sliderach temperatury, ale to nie jest zmiana repliki 1:1.

---

# 9. PASS 59 — UI MODEL

Utworzone:
- `tools/ui_model.py`
- `tools/test_ui_model.py`
- raport PASS 59.

Cel:
połączyć inventory widgetów z `presenter_map.csv` poprzez `widget.view_off`.

Statusy:
- EXACT_VIEW_OFF,
- AMBIGUOUS_VIEW_OFF,
- UNRESOLVED_VIEW_OFF.

Zasada:
- nie zgadywać PID na podstawie geometrii.

---

# 10. PASS 60 — UI ACTION GRAPH

Utworzone:
- `tools/action_graph.py`
- `tools/test_action_graph.py`.

Model:
widget/this/address lub node+tap -> handler -> effects.

Efekty:
- ekran/dialog,
- handler,
- zmiana modelu,
- potencjalny CAN/PID tylko gdy istnieje dowód.

Nie przypisywano efektu CAN/PID bez trace/harness.

---

# 11. PASS 61–69 — DALSZY BLOK RE / PRZYGOTOWANIE A1–A3/B

W tej fazie utrwalono podział zadań:
- A1: hidden PIN,
- A2: tabela 23 liczb,
- A3: RTC/time,
- B1: 6666,
- B2: poller gate,
- B3: ochrona kotła / Buffer,
- B4: czwarta bramka + L>=3.

Ustalono ownership:
- ChatGPT: static RE,
- Claude: dynamic/emulator,
- ChatGPT nie przejmuje zadań Claude, ale przygotowuje twarde granice statyczne.

---

# 12. PASS 70 — PIN + TABLE 23 + RTC

Raport:
`AUTONOMOUS-PASS-70-PIN-TABLE23-RTC-2026-11-23.md`.

PIN handler:
`FUN_0803C21C -> FUN_08018634 + FUN_08037E74`.

Poziomy:
- 0 -> level 0,
- 900 -> level 1,
- 999 -> level 2,
- 6154 -> level 3.

6666:
- `FUN_08018634`,
- ustawia `[obj+7]=1`,
- odpowiada za reset/default-settings request.

1992:
- dodaje 365 dni = 31,536,000 s do timestampu,
- zapisuje `[obj+0x24]`.

Tabela 23:
- baza katalogu = 0x20008C50,
- `FUN_080144B4` wyszukuje po record+8,
- iteracja 23 rekordów,
- `FUN_080144E4` zwraca record+0x0C.

RTC:
- `FUN_08018E94` zapisuje RTC peripheral,
- `FUN_08018F18` czyta,
- `FUN_08018FF8` rozpakowuje BCD,
- `FUN_0801906E` konwertuje pola.

---

# 13. PASS 71 — TABELA 23 = PARAMETERS SET NUMBER

Caller `0x0805F612`:
- r10 = 0x20021FA0,
- PID 0x0004 = Parameters set Number,
- następnie `FUN_080144E4`.

Wniosek:
- 0x20008C50 to katalog wartości Parameters set Number,
- record+0x08 = Parameters set Number,
- record+0x0C = wartość zwracana.

23. wartość nadal OPEN.

---

# 14. PASS 72 — GATE INVENTORY / L>=3

Utworzone:
- `tools/cg_gate_inventory.py`
- test.

`0x08054AB8`:
- gate level != 0,
- caller `0x08054CA6`,
- ścieżka prowadzi do bitmap/resource 0x84 i view offset 0x1498.

0x1498:
- PID 0x201A,
- Hot water 1 result temperature.

Wrappery L>=3:
- 0x0805A9EC,
- 0x0805B1D4,
- 0x0805F400,
- 0x0805FE9C,
plus później znane wrappery:
- 0x0806125C,
- 0x08061518.

Wspólny wzorzec:
- access level,
- +0x23C,
- CPU/load/header family.

---

# 15. PASS 73 — RTC AUTOSYNC

`FUN_08062638` = bezpośrednia ścieżka autosync.

Gate:
- PID 0x372F = Is automatic time synchronization.

Gdy:
`[object+0x10] != [object+0x0C]`
i autosync jest włączony:
- źródłem jest object+0x0C,
- `FUN_08039370` rozkłada timestamp,
- `FUN_08018E94` zapisuje hardware RTC,
- object+0x10 zostaje zsynchronizowany.

---

# 16. PASS 74 — RTC VTABLE DISPATCH

`FUN_08062638` = runtime 0x08072639.

Vtable:
- runtime 0x080A446C,
- PROJECT 0x0809446C.

slot0 -> `FUN_08062638`.

Konstruktor zapisuje vptr.

---

# 17. PASS 75 — RTC OBJECT IDENTITY

Startup:
- base `0x20008CD0`,
- constructor r0 = +0x4C,
- RTC object = `0x20008D1C`.

Pola:
- +0x00 vptr,
- +0x08 prior state,
- +0x0C = `0x20008D28`,
- +0x10 = `0x20008D2C`,
- +0x14 invocation counter,
- +0x1E..+0x28 date/time fields.

`0x20008D28` = PID 0x2165 Compatibility timestamp.

---

# 18. PASS 76 — RTC SCHEDULER CLOSURE

Base constructor:
- `FUN_08014824`,
- rejestracja w schedulerze.

Scheduler:
- state `0x200246E8`,
- list fields +0x04/+0x08/+0x0C.

`FUN_080147C8`:
- iteruje scheduler,
- wywołuje vtable slot0.

Wniosek:
RTC object jest scheduler method, a gate 0x372F jest lokalny dla RTC, nie scheduler-wide.

---

# 19. PASS 77–79 — TIMESTAMP CAN PRODUCER

## PASS 77
PID:
- `0x2165` = Compatibility timestamp,
- u32,
- storage `0x20008D28`.

RX chain:
`CAN RX -> FUN_08062B22 -> PID -> FUN_080115F6 -> record -> FUN_08011812 -> 0x20008D28`.

## PASS 78
Dokładny transport:
- StdId 0x584,
- generic write decoder,
- PID bytes frame+4/+5 LE,
- frame+6 == 1,
- wire type 5 = u32,
- frame+7..+10 = value LE,
- `FUN_08014720` stores word/type 3.

## PASS 79
Standard publishers:
- normal publisher i special publisher jawnie wykluczają PID 0x2165.

Wniosek:
panel nie publikuje własnego 0x2165 przez standardowy 0x584/0x42 path.

Model:
external/boiler-side source -> 0x584 WRITE PID 0x2165 -> parameter manager -> 0x20008D28 -> RTC autosync gate 0x372F.

Otwarte:
- exact external node,
- ACK,
- exact source trigger,
- solicited vs unsolicited.

---

# 20. PASS 80 — BRAMKA 0x08054AB8 = CWU

Gate:
- `0x08054AB8`,
- RAW `0x44AB8`,
- caller RAW `0x44CA6`.

Warunek:
`ldrb [model,#0x158]; cbz`
czyli level != 0.

Gated path:
- `FUN_08040380`,
- bitmap 0x84,
- view offset 0x1498,
- PID 0x201A = Hot water 1 result temperature / CWU wynikowa temperatura.

To zamknęło kontekst B4 jako CWU.

---

# 21. PASS 81 — L>=3 WRAPPERS + TABLE23 SOURCE

Wrappery:
- 0x0805A9EC -> RAW 0x4A9EC,
- 0x0805B1D4 -> RAW 0x4B1D4,
- 0x0805F400 -> RAW 0x4F400,
- 0x0805FE9C -> RAW 0x4FE9C.

Wspólny skeleton:
- init widgets/subobjects,
- `FUN_080314BA`,
- model+0x158,
- cmp #3,
- >=3 -> pole +0x23C,
- init +0x210,
- vtable slot0.

Caller/vtable inventory został wykonany dla pierwszych wrapperów.

WAŻNA KOREKTA:
wcześniejsze utożsamienie `0x20008D84` z 23-elementową source array zostało odrzucone później. 0x20008D84 jest parameter managerem, a rekordy runtime mają stride 0x2C. Rzeczywista baza 23 source records pozostaje OPEN.

---

# 22. PASS 82 — BUFFER L1 + 0%

Raport:
`AUTONOMOUS-PASS-82-BUFFER-L1-PROTECTION-2026-11-23.md`.

Menu/list builder:
`FUN_0804E714`.

Class 7 = Bufor.

Hard gate:
- pierwszy element jest tworzony zawsze,
- drugi element jest tworzony po odczycie model+0x158,
- `cmp #0`,
- branch przy zero omija drugi element.

Wniosek:
**Buffer L>=1**.

Buffer presenter:
- key 0xF1 -> PID 0x2112 Buffer top measured temperature,
- 0xF2 -> PID 0x2113 Buffer bottom measured temperature,
- 0xF5 -> PID 0x2280,
- 0xF4 -> PID 0x2115,
- 0xF8 -> PID 0x3171,
- 0xF9 -> PID 0x3172,
- 0xFA -> PID 0x3173,
- 0xFB -> PID 0x3174 Buffer internal energy [%].

**0% = PID 0x3174**.

Korekta:
- 0x2114 i 0x2115 mają min 7°C,
- 0x2280 jest osobnym live/read-only parametrem,
- nie wolno utożsamiać 0x2280 z 0x2114 tylko przez nazwę,
- dokładne źródło konkretnego pola „7°C” pozostaje OPEN.

---

# 23. PASS 83 — OCHRONA KOTŁA + KOREKTA TABLE23

Ochrona kotła:
- presenter Ogrzewanie czyta UI key 0xB0,
- 0xB0 = PID 0x22A1 Room temp sensor type,
- key 0xCD = PID 0x2301 CH thermostat state,
- helper RAW 0x44848 tworzy dwie flagi widoku.

Hard:
```
A95 = (Room temp sensor type != 4) ? 1 : 0
A69 = (Room temp sensor type == 4 && CH thermostat state == 1) ? 1 : 0
```

Ważna REJECTED:
- wcześniejsza hipoteza, że Ochrona kotła jest bezpośrednio sterowana przez CH status 0x22FD, została odrzucona dla tej ścieżki.

Nadal OPEN:
- czy TypedText 87 odpowiada A69 czy A95,
- dokładne widget/resource mapping.

Table23:
- 0x20008D84 nie jest bazą 23-record source array,
- jest parameter managerem,
- runtime records mają stride 0x2C,
- katalog 0x20008C50 nadal jest zamknięty,
- source-array base i record #23 +0x0C nadal OPEN.

---

# 24. PASS 84 — PROVIDER / FLASH PERSISTENCE

Provider:
- runtime vtable 0x080A31F0,
- PROJECT 0x080931F0,
- RAW 0x931F0.

slot0:
- runtime 0x0801DB31,
- PROJECT 0x0800DB31,
- RAW 0xDB30,
- persistent GET.

slot1:
- runtime 0x0801DB79,
- PROJECT 0x0800DB79,
- RAW 0xDB78,
- persistent SET / typed encoding.

slot4:
- PROJECT 0x080617FF,
- RAW 0x517FE,
- state/init transition.

GET:
- FUN_08014BBA,
- flash regions around 0x08008000 / 0x0800C000,
- bookkeeping around 0x200247D4 / 0x200248D8.

SET:
- FUN_08014C14,
- FUN_08014CC0,
- validation/commit through flash layer.

Wniosek:
**0x080A31F0 jest backendem trwałej pamięci flash parameter managera, nie kolejnym CAN providerem.**

---

# 25. PASS 85 — CAN TIMESTAMP ROLE BOUNDARY

RAW 0x62AE4:
- buduje request StdId 0x604,
- cmd 0x40,
- PID LE,
- subindex 1.

RAW 0x62A90:
- przyjmuje StdId 0x584,
- dispatchuje generic parameter write.

Połączenie:
```
remote/boiler-side source
        ↓
0x584 parameter write
        ↓
PID 0x2165
        ↓
0x20008D28
        ↓
RTC autosync / PID 0x372F
```

CLOSED:
- exact PID,
- storage,
- wire envelope,
- panel TX exclusion,
- fixed 0x604 read request.

OPEN:
- exact trigger,
- exact remote node,
- ACK,
- solicited vs unsolicited timestamp write.

---

# 26. NAJWAŻNIEJSZE KOREKTY I ODRZUCONE HIPOTEZY

Nie używać jako aktualnych faktów:
- 0x68 = extra-fan gate,
- 0x10E = 0x3505,
- 0x10F = 0x2105,
- graph 47290,
- bitmap ID = widget ID,
- 370A 1/2/3 -> bitmap 011/012/013,
- 174 = Home-only,
- 0x08011812 = prosty dirty-bit/TX setter,
- 0x08078578 == 0x08094508,
- 0x08079704 = conventional executable vtable,
- wcześniejsze „0x20008D84 = 23-record source array”,
- Ochrona kotła bezpośrednio sterowana 0x22FD,
- 0x2280 utożsamiane z 0x2114 tylko przez nazwę.

---

# 27. CO CHATGPT PRZYGOTOWAŁ W REPO

Najważniejsze narzędzia:
- `tools/emu_startup.py`
- `tools/runtime_param_table.py`
- `tools/resolver_tables.py`
- `tools/bl_xref.py`
- `tools/disasm_thumb.py`
- `tools/pid_matrix.py`
- `tools/poller_trace.py`
- `tools/can_rx_inject.py`
- `tools/publish_probe.py`
- `tools/lang_cycle_probe.py`
- `tools/menu_rows_probe.py`
- `tools/menu_click_probe.py`
- `tools/cortexm_rtos.py`
- `tools/stm32_dma2d.py`
- `tools/render_screen.py`
- `tools/stm32_can.py`
- `tools/can_boot_trace.py`
- `tools/stm32_i2c.py`
- `tools/touch_screen.py`
- `tools/ui_session.py`
- `tools/ui_model.py`
- `tools/action_graph.py`
- `tools/access_gates_scan.py`
- `tools/export_bitmaps.py`
- `tools/cg_pin_rtc_scan.py`
- `tools/cg_gate_inventory.py`
- `tools/cg_rtc_vtable_scan.py`
- `tools/cg_timestamp_producer_scan.py`
- `tools/cg_can_timestamp_frame_scan.py`
- `tools/cg_timestamp_tx_exclusion_scan.py`
- `tools/cg_gate_054ab8_scan.py`
- `tools/cg_l3_table23_scan.py`

Do narzędzi dodawano testy jednostkowe tam, gdzie skan był wielokrotnie używany.

---

# 28. NAJWAŻNIEJSZE ARTEFAKTY DLA CLAUDE

- `NewEstyma/00_AGENT_START_HERE.md`
- `NewEstyma/01_PROJECT_STATE.md`
- `NewEstyma/02_WORKFLOW.md`
- `NewEstyma/03_TOOLING.md`
- `NewEstyma/05_PLAN_1TO1.md`
- `NewEstyma/COORDINATION.md`
- `DOKUMENTACJA/REVERSE_ENGINEERING_MASTER_2026-11-22.md`
- katalog PID / runtime data,
- `data/pid_matrix_655.csv`,
- `data/presenter_map.csv`,
- `data/bitmaps/`,
- atlas ekranów,
- `WIDGETS-BY-SCREEN-2026-11-23.md`,
- `MENU-TREE-2026-11-23.md`,
- `SPEC-POZIOMY-DOSTEPU-0-1-2.md`.

---

# 29. AKTUALNE OPENY PO STRONIE STATIC RE

## A2
- rzeczywista baza source array dla katalogu 23,
- record #23 +0x0C.

## B3
- exact widget association A69/A95,
- exact 7°C widget/PID.

## B4 / L>=3
- dokładny semantyczny kontekst wszystkich czterech/sześciu wrapperów,
- resource/widget/PID effect każdego wrappera.

## Provider
- pełna semantyka slot4,
- szczegółowy format persistence entry.

## CAN timestamp
- remote node,
- trigger,
- ACK,
- solicited vs unsolicited.

## UI
- pełne widget -> presenter -> resource -> PID -> handler mapping,
- remaining screen/action graph.

---

# 30. ZAMKNIĘTY MODEL — NAJWAŻNIEJSZY SKRÓT DLA CLAUDE

Parameter path:
```
CAN RX 0x584
  -> 0x08062A90
  -> 0x08062B22
  -> PID
  -> 0x080115F6
  -> runtime record (+0x2C stride)
  -> 0x08011812
  -> storage
```

CAN read:
```
poller
  -> 0x080629FC
  -> 0x08062AE4
  -> 0x604 / 0x40 / PID / sub1
```

Local publication:
```
storage change
  -> manager callback 0x08010FCE
  -> 0x584 / 0x42
```

RTC:
```
remote PID 0x2165
  -> 0x20008D28
  -> RTC object
  -> vtable slot0 FUN_08062638
  -> PID 0x372F gate
  -> HAL RTC
```

Persistence:
```
parameter manager
  -> provider 0x20008D64
  -> vtable 0x080A31F0
  -> slot0 GET / slot1 SET
  -> flash backend
```

UI:
```
runtime class
  -> presenter/resource layer
  -> widget
  -> PID getter/setter
  -> manager
  -> CAN / storage
```

---

# 31. STATUS OGÓLNY

Według ostatniego master state szacunkowo:
- CAN ~90%
- parametry ~92%
- PID->CAN ~75%
- menu ~88%
- access levels ~80%
- USTAWIENIA/dialogi ~60%
- ekran główny ~65%
- grafiki ~95%
- wykresy ~50%
- narzędzia ~92%
- całość 1:1 ~70%.

To są orientacyjne wartości, nie metryka formalna.

---

# 32. HANDOFF DLA CLAUDE

Claude powinien traktować ten raport jako zbiorczy zapis pracy ChatGPT i nie powtarzać zamkniętych passów.

Najważniejsze rzeczy do kontynuacji:
1. dynamicznie zweryfikować OPEN-y B3/A2/L>=3,
2. nie przywracać odrzuconych hipotez bez nowego RAW proof,
3. używać `COORDINATION.md` jako bieżącej synchronizacji,
4. przy nowych wynikach aktualizować `01_PROJECT_STATE.md`,
5. static RE może dalej zamykać zależności, gdy pojawi się nowa gałąź dowodowa.

**Raport obejmuje cały potwierdzony zakres prac ChatGPT dostępny w bieżącym repo/stanie do PASS 85.**
