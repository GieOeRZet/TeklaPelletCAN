# NewEstyma — CURRENT PROJECT STATE

Date: 2026-11-22

## Goal
Full universal reconstruction of Estyma firmware behavior, eventually targeting ESP32-C6 + CAN and reusable cross-platform model.

## HARD highlights
- CAN2 RX/TX transport and hardware path.
- Node 4 object architecture.
- Parameter resolver and typed storage model.
- 260-entry catalog uniqueness.
- 660-record runtime search space, stride 0x2C.
- PID/storage/type geometry.
- +0x14 MIN, +0x1C MAX, +0x24 DEFAULT descriptors.
- Basic parameter READ/WRITE protocol paths.
- MenuTree control-flow mechanism.
- Concrete parameter manager 0x20008D84.
- Concrete provider 0x20008D64 behind +0x7178.
- Concrete publication sink 0x20008D60 behind +0x7180.
- Scheduler registration leading to FUN_08010FCE.

## Main OPENs
- Provider vtable 0x080A31F0: slots 0/1 HARD (GET/SET); remaining interface OPEN.
- Full 260-row cross-layer matrix.
- Descriptor/record ownership and multi-instance mapping.
- Local parameter write -> outbound CAN publication bridge (machine-level HARD; timing/shadow semantics OPEN).
- Complete UI semantic graph and visibility mapping.
- Sidecar class 1/2/3 exact semantics.
- Complete response/publication graph.

## Current parameter-manager architecture
Constructor: 0x0800DDC0
this = 0x20008D84
provider = 0x20008D64
sink = 0x20008D60
manager vtable = 0x080A44F0
manager vtable slot 0 = FUN_08010FCE
provider vtable runtime = 0x080A31F0
provider vtable PROJECT = 0x080931F0
provider vtable RAW = 0x931F0
provider slot0 GET = runtime 0x0801DB31 / PROJECT 0x0800DB31
provider slot1 SET = runtime 0x0801DB79 / PROJECT 0x0800DB79

## Protocol anchors
READ: StdId 0x0604, command 0x40
Publication: StdId 0x0584, command 0x42

Address rule:
- runtime pointer = PROJECT + 0x10000
- PROJECT = RAW + 0x08000000
- never index RAW using a runtime pointer directly.

Do not confuse:
- catalog 260 with runtime 660
- RAW offset with PROJECT address
- manager/provider/sink objects
- MenuTree selector with runtime class byte
- mechanism closure with semantic closure


## PASS 20 closure

`FUN_08011812` writes the validated local value into record storage; `FUN_0801117C` detects local/shadow changes and builds StdId 0x0584 command 0x42; +0x7180 resolves to 0x20008D60; sink slot0 resolves to FUN_0806E59C; TX queue/CAN2 path is already HARD. The machine-level local-write -> outbound publication bridge is CLOSED.


## PASS 21 — MenuTree raw/runtime anchor audit

Canonical BIN re-scan is now automated by `tools/menu_matrix_scan.py`.

HARD:
- 21×6 B MenuTree table at RAW 0x42348 / PROJECT 0x08042348.
- Runtime class table pointer 0x20005EF0 has one direct literal anchor at RAW 0x3C218.
- Access/update table pointer 0x20005F08 has one direct literal anchor at RAW 0x42314.
- Row constructor Thumb pointer 0x0805BB43 has one literal anchor at RAW 0x3C030.
- Main row-selection resolver 0x0808EB01 has one literal anchor at RAW 0x63AB8.
- Sibling resolver 0x0808EB37 has one literal anchor at RAW 0x63AC0.
- Root-table selector is not itself the direct page-navigation key; runtime class dispatch remains a separate layer.

OPEN:
- producers and runtime contents of 0x20005EF0 and 0x20005F08;
- exact runtime class -> screen/widget mapping;
- complete widget tree, visibility/access matrix and PID/CAN cross-link.


## PASS 22 — IAR data / Menu runtime tables

HARD:
- IAR `.data` reconstruction: RAW 0x96114..0x9694D -> SRAM 0x20000000, size 0x118B3.
- 0x20005EF0[0..20] exact initial bytes recovered.
- 0x20005F08[0..20] exact initial bytes recovered; identical to 0x20005EF0.
- Both 21-byte runtime tables initially equal the 21 root-table selectors at RAW 0x42348.
- Configuration-driven MenuTree eligibility remains HARD: classes 1..4 use 0x10E/0x2105; 5 uses 0x10F/0x2106; 6 uses 0x110/0x2108; 7 uses 0x111/0x2107; 8 uses 0x11C; 9 uses 0x122.

OPEN:
- later writes/mutations of 0x20005EF0 and 0x20005F08;
- exact semantics/navigation for rows 15..20;
- complete widget/resource/callback graph.


## AUTONOMOUS PASS 24 — THUMB-2 BOUNDARY / POINTER-FLOW CORRECTION — 2026-11-22

Report:
analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-24-THUMB2-POINTER-FLOW-CORRECTION-2026-11-22.md

### CRITICAL CORRECTION

The PASS 23 alleged store at RAW 0x3C1FE into 0x20005EF0+6 is REJECTED.

RAW 0x3C1FC..0x3C1FF is one Thumb-2 instruction:
MOV.W r1,#0x122.
0x3C1FE is its second halfword, not a STRB.

Therefore:
- no direct static write to 0x20005EF0+6 is currently proven;
- the previous semantic OPEN derived from that alleged write is removed;
- pointer-flow scanning must remain Thumb-2 width aware.

### NEW-HARD

- 0x20005EF0 has two direct literal materializations: RAW 0x3C068 -> r0 and RAW 0x3C17A -> r2.
- Both consumers perform real byte reads: RAW 0x3C06A and 0x3C17C.
- 0x20005F08 is materialized at RAW 0x422CE -> r5.
- PROJECT 0x080422C8 scans all 21 bytes of 0x20005F08 sequentially.
- The 0x20005F08 consumer advances its row/object base by 0x274 per entry.
- access-table value 0x0E triggers a path through 0x08032F08 -> 0x0803C270 -> 0x08037212.
- 0x08032F08 is a direct getter of object +0x2C.
- 0x0803C270 gates on object +0x10 == 1 and forwards the returned value using parameter ID 0x0117.
- Runtime-class table values 0..20 feed a TBB dispatch mechanism.

### TOOLING

pointer_flow_scan.py was upgraded to:
- respect Thumb-2 32-bit instruction boundaries;
- decode common Thumb-2 memory forms;
- recognize MOVW/MOVT;
- recognize Thumb-2 PUSH.W when finding function starts;
- keep SRAM targets in SRAM address space;
- preserve candidate/static evidence discipline.

Regression test passed on the canonical BIN.

### OPEN

- arithmetic/alias/indirect writers of both SRAM tables;
- r4/r8 object identity in PROJECT 0x080422C8;
- mapping of 0x274-stride objects to the 21 MenuTree rows;
- semantic meaning of access-table 0x0E and PID 0x0117;
- complete runtime-class 0..20 handler -> page/widget/resource graph;
- complete PID/UI/CAN matrix.


## AUTONOMOUS PASS 25 — MENU ACCESS TABLE → ROW OBJECT → PID 0x0117 — 2026-11-22

Report:
analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-25-MENU-ACCESS-ROW-PID117-CLOSURE-2026-11-22.md

### NEW-HARD

- PROJECT 0x080422C8 is vtable slot 4 implementation for runtime vtable 0x0808F66C.
- Constructor PROJECT 0x08074508 installs that vptr.
- The constructor initializes a 21-element repeated region at object +0x42C, stride 0x274, count 0x15.
- 0x080422C8 uses r8=object+0x524 and increments by 0x274, so each iteration addresses row[i]+0xF8.
- If 0x20005F08[i] == 0x0E, the path reads row[i]+0x124 through 0x08032F08.
- The returned value reaches 0x0803C270.
- 0x0803C270 gates on a state object's +0x10 == 1 and forwards the value with logical key 0x0117 to 0x08037212.
- 0x08037212 uses manager 0x20008D84 and resolves the logical key before calling 0x08011812.

### NEW STRUCTURAL MODEL

0x20005F08[i]
-> row[i] (+0x42C + i*0x274)
-> row[i]+0x124
-> state gate
-> logical key 0x0117
-> 0x08037212 resolver
-> parameter manager
-> 0x08011812

### OPEN

- final PID/value/type resolved from logical key 0x0117;
- identity of object+0x3C and its +0x10 gate;
- producer/initializer of row[i]+0x124;
- exact mapping of 21 runtime rows to root MenuTree selectors;
- runtime-class 0..20 -> page/widget graph;
- remaining arithmetic/alias writers of the two SRAM tables.


## AUTONOMOUS PASS 26 — PID 0x0117 RESOLVER NEGATIVE CLOSURE — 2026-11-22

Report:
analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-26-PID0117-RESOLVER-NEGATIVE-CLOSURE-2026-11-22.md

### NEW-HARD

- 0x08037212 receives logical key 0x0117 from the 0x0E Menu access path.
- The first 0x31-entry resolver table contains no key 0x0117.
- The second 0x174-entry resolver table contains no key 0x0117.
- Therefore this canonical static path does not call 0x08011812 for key 0x0117.
- The second table does contain key 0x2123 -> value 0x0117 at RAW 0x3797A. [SUPERSEDED/REJECTED przez PASS 35 §6: odczyt przesunięty o 2 B; poprawny rekord (0x0117 -> 0x3506) @RAW 0x3797C]

### CORRECTION

PASS 25 wording that the 0x0E path reaches the parameter manager is superseded.

Correct chain:
0x0E -> row[i]+0x124 -> state gate -> 0x0803C270 -> key 0x0117 -> 0x08037212 -> no static resolver match -> no 0x08011812.

### OPEN

- semantic identity of 0x0117;
- runtime producer of row[i]+0x124;
- relation key 0x2123 -> value 0x0117 to the 260-slot catalog;
- runtime class -> page/widget graph;
- remaining SRAM-table writers/aliases.


## AUTONOMOUS PASS 27 — ROW +0xF8 DESCRIPTOR / VALUE 0x15 — 2026-11-22

Report:
analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-27-ROW-F8-DESCRIPTOR-VALUE15-CLOSURE-2026-11-22.md

### NEW-HARD

- Row constructor PROJECT 0x08089570 stores 0x0807C540 at row+0xF8.
- A second row constructor at PROJECT 0x08089594 stores the same 0x0807C540 at +0xF8.
- PROJECT 0x08032F08 reads byte +0x2C from that pointer.
- Canonical static byte at 0x0807C540+0x2C is 0x15.
- Therefore constructor-established 0x08032F08 result is 0x15.

### REVISED 0x0E PATH

0x20005F08[i]==0x0E
-> row[i]+0xF8
-> 0x0807C540
-> byte +0x2C = 0x15
-> 0x0803C270
-> logical key 0x0117
-> 0x08037212
-> no static resolver-key match
-> no 0x08011812.

### OPEN

- mutation of row+0xF8 after construction;
- identity/role of 0x0807C540;
- reason for logical key 0x0117 on this path;
- 260-slot catalog correlation;
- runtime-class/page/widget graph;
- remaining SRAM-table writers.


## AUTONOMOUS PASS 28 — RUNTIME CLASS 0..20 FIRST-LEVEL UI DISPATCH — 2026-11-22

Report:
analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-28-RUNTIME-CLASS-FIRST-LEVEL-UI-DISPATCH-2026-11-22.md

### NEW-HARD

- 0x20005EF0 values 0..20 feed a complete 21-entry TBB dispatch at RAW 0x3C076.
- Class 1..4 share 0x08038130 with r1=1..4.
- Classes 5..13 mostly enter distinct first-level UI handlers.
- Class 14 is an immediate return.
- Classes 12,15,19,20 use structurally distinct paths.
- Classes 1..4 directly write object+0x12B and object+0x12C.
- Classes 5..10 write selector-state bytes including object+0x12B.
- Runtime class is therefore a behavior selector layer, distinct from root MenuTree selectors.

### OPEN

- common tail 0x08037F88;
- concrete widget/page constructors for classes 0..20;
- special class 12/15/19/20 graph;
- resource/text/bitmap/PID/CAN links;
- SRAM-table writers/aliases.


## AUTONOMOUS PASS 29 — RUNTIME CLASS → CALLBACK/DESCRIPTOR LAYER — 2026-11-22

Report:
analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-29-RUNTIME-CLASS-CALLBACK-DESCRIPTOR-LAYER-2026-11-22.md

### NEW-HARD

- Complete 21-byte runtime-class TBB table at RAW 0x3C076 is resolved.
- Generic classes converge into PROJECT 0x08037F88.
- 0x08037F88 constructs/copies the object at parent+0x110.
- Temporary object vtable is 0x0809F848.
- Static callback/config pointer pool is around RAW 0x386A8..0x387D8.
- Classes 1..4 share 0x08038130 and explicitly pass r1=1..4.
- Class 14 is immediate return.
- Class 12 is an inline parameter-manager path, structurally distinct.
- Class 15 bypasses the generic constructor through 0x08042318 -> 0x0802EADE.
- Classes 16/17 share 0x08038488 after setting 0x10/0x11 at object+0x12B.
- Class 18 uses a separate +0x110 descriptor builder.
- At least callback 0x08048037 directly writes object+0x12A=1.

### OPEN

- vtable 0x0809F848 slot semantics;
- callback -> widget/resource/text/PID graph;
- class 12 key-3 parameter operation;
- class 15 object/navigation path;
- remaining runtime-table writers/aliases;
- complete UI/PID/CAN graph;
- provider/persistence/260-row matrix.


## AUTONOMOUS PASS 30 — UI CALLBACK OBJECT VTABLE 0x0809F848 — 2026-11-22

Report:
analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-30-UI-CALLBACK-OBJECT-VTABLE-2026-11-22.md

### NEW-HARD

- 0x08039494 installs vtable 0x0809F848.
- Vtable RAW = 0x8F848.
- Non-zero slots: 2,3,8,9,14,15.
- The object at parent+0x110 has fields +0x00 vptr, +0x04 context, +0x08 callback/table pointer, +0x0C signed/index field.
- Slots 2 and 8 implement an indirect callback dispatch algorithm.
- Slots 3 and 9 implement the corresponding boolean/state-check family.
- Therefore parent+0x110 is an executable polymorphic runtime object, not passive metadata.

### OPEN

- exact vtable slot semantics;
- callback pointer -> widget/resource/text/PID graph;
- slots 14/15;
- constructor 0x08039394 static pair;
- class 12/15 special paths;
- remaining runtime-table writers;
- full UI/PID/CAN matrix.


## AUTONOMOUS PASS 31 — VTABLE SLOT 2 → STATIC CALLBACK BRIDGE — 2026-11-22

Report:
analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-31-VTABLE-SLOT2-CALLBACK-BRIDGE-2026-11-22.md

### NEW-HARD

- Generic 0x08037F88 descriptors have second word 0, so generic object+0x110 gets +0x0C=0.
- Generic object+0x110 +0x08 is the selected callback pointer.
- Vtable slot 2 then directly invokes [object+0x08] with [object+0x04] as argument.
- Class 0 selects callback 0x08048037.
- 0x08048037 writes object+0x12A = 1.
- Vtable contains three repeated method pairs: 2/3, 8/9, 14/15.

### OPEN

- vtable slot-2 call sites;
- all callback -> object/resource/PID effects;
- slot pair semantics;
- class 12/15;
- runtime table writers;
- full UI/PID/CAN graph.


## AUTONOMOUS PASS 32 — CLASS 12 PARAMETER-3 CYCLIC OPERATION — 2026-11-22

HARD:
- Runtime class 12 is a special action path at RAW 0x3C12A.
- 0x080373BA reads logical key 3 through concrete parameter manager 0x20008D84, increments it, and commits the increment with type 5 via 0x08011812.
- The class-12 caller increments the returned value again and 0x080373E6 writes the result modulo 8, again using logical key 3, manager 0x20008D84 and type 5.
- Therefore the class-12 branch performs two real parameter writes and returns the final 0..7 modulo result.

OPEN:
- semantic identity/PID of logical key 3;
- caller-level meaning of the returned 0..7 state;
- whether the intermediate write is externally observable;
- full class-12 UI/resource linkage.


## AUTONOMOUS PASS 33 — RUNTIME KEY 3 PROVENANCE — 2026-11-22

HARD:
- 0x080115F6 is a runtime-record lookup over the 660-position table, stride 0x2C; it is not itself the 260-catalog PID resolver.
- Runtime key 3 is concretely initialized by 0x0801143C with manager 0x20008D84, storage 0x20021FAA and type code 1.
- 0x0801143C populates the runtime record with key/storage/type metadata.
- Class 12 therefore operates on a real runtime parameter record keyed by 3.

CORRECTION:
- Do not call key 3 a catalog PID without direct proof. Preferred term: runtime parameter lookup key 3.

OPEN:
- key3 -> catalog PID mapping;
- semantic identity of storage 0x20021FAA;
- reason class12 writes type 5 after startup type 1;
- UI meaning of the 0..7 result.


## AUTONOMOUS PASS 34 — RUNTIME KEY 3 STORAGE / TYPE CLOSURE — 2026-11-22

Report: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-34-RUNTIME-KEY3-STORAGE-TYPE-CLOSURE-2026-11-22.md`

### NEW-HARD
- Runtime key 3 startup storage is `0x20021FAA = 0x200208EC + 0x16BE`.
- Startup runtime record type for key 3 is 1.
- `FUN_08011812` stores type-1 records with byte-width `STRB`; key 3 is therefore physically byte-backed.
- Class 12's type-5 temporary does not imply type-5 storage; final width is controlled by the located runtime record.
- Key 4 similarly uses `0x20021FBA = 0x200208EC + 0x16CE`, type 2.
- Nearby startup keys `0x3500/0x3502/0x350B` and `0x3721...` share the same broader configuration base.

### OPEN
- semantic identity of `0x20021FAA`;
- direct key3 -> catalog PID bridge;
- other UI/resource consumers;
- full runtime-key startup matrix;
- provider/persistence/CAN behavior for key 3.

### CORRECTION
Do not infer catalog PID identity from runtime lookup key 3. Key 3 is a runtime-manager key backed by a byte field.

## AUTONOMOUS PASS 35 — RUNTIME PARAMETER TABLE Z EMULACJI STARTUPU — 2026-11-22

Report: analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-35-RUNTIME-PARAM-TABLE-EMULATION-2026-11-22.md
Data: analiza/FW2213TK-2026-11-22/data/ (runtime_param_table_655.csv, resolver_t1.csv, resolver_t2.csv)

### NEW-HARD
- Startup firmware uruchomiony w emulatorze (tools/emu_startup.py); 655 wywołań 0x0801143C wypełnia 655 unikalnych rekordów tabeli manager'a 0x20008D84.
- Układ rekordu (stride 0x2C): +0 key, +4 storage, +8 typ, +0xC min, +0x10 typ min, +0x14 max, +0x18 typ max, +0x1C default, +0x20 typ default, +0x24 klasa sidecar, +0x28 wskaźnik nazwy ASCII.
  Pola wartości znaczą tylko tyle bajtów, ile mówi ich własny kod typu (reszta = śmieci ze stosu). Default 5678 = brak.
- Klucz runtime = PID. Wszystkie 448 PID katalogu panelu w tabeli, nazwy 448/448 identyczne.
- KEY 3 = PID 0x0003 "Language" (u8, 0..30, storage 0x20021FAA = 0x200208EC+0x16BE; nazwa z BIN). Key 4 = "Parameters set Number".
- 0x200208EC to blok ustawień: 603/655 storage'ów leży w +0x08..+0x3DD9; +0x16C3..+0x16C6 = 0x2105..0x2108 (konfiguracje sterujące widocznością menu).
- 15 statystyk (0x3608..0x3619, 0x3628, 0x362A, 0x362C) w BKPSRAM 0x40024000.
- Rezolwer FUN_08036FF2: tabela 1 @RAW 0x37B48 (49 rekordów CH, PID = baza + instancja - 1, instancja = [ctx+0x12C]); tabela 2 @RAW 0x37578 (372 rekordy, PID wprost).
  196/196 instancji CH1..CH4 obecnych w runtime.

### STRONG
- Class 12 = przełączanie języka (key 3 Language, modulo 8 = 8 tabel TypedText). Brak dowodu widgetu wywołującego.

### CORRECTIONS
- PASS 26 REJECTED: rekord (0x0117 -> 0x3506 "Sound alarm activation") istnieje @RAW 0x3797C; PASS 26 odczytał tabelę z przesunięciem o 2 B.
  Ścieżka 0x0E -> klucz 0x0117 dochodzi więc do PID 0x3506 i dalej do 0x08011812.
- "logical key 3" -> PID 0x0003 Language.

### OPEN
- producent instancji [ctx+0x12C]; 21 rozbieżnych par min/max i dynamiczne zakresy; 10 kluczy tabeli 2 poza runtime po starcie;
  20 rekordów bez nazwy; semantyka klasy sidecar +0x24; model kolejnych zadań FreeRTOS w emulatorze.

### RECONCILIATION z PASS 34 (równoległy raport „KEY3 STORAGE/TYPE CLOSURE”)
PASS 34 zabrania utożsamiania key 3 z PID 3 „bez bezpośredniego mostu”. Most istnieje i jest HARD: rekord key 3 niesie wskaźnik na nazwę ASCII `"Language"` (BIN `0x08034C00`),
a dla wszystkich 448 PID katalogu panelu nazwa z rekordu = nazwa z katalogu (448/448). Zakaz z PASS 34 jest tym samym uchylony; jego ustalenia o typie (key 3 bajtowy, STRB) pozostają w mocy i są zgodne z typem u8 w rekordzie.


## AUTONOMOUS PASS 36 — MACIERZ PID I KLASA DOSTĘPU — 2026-11-22
Raport: analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-36-PID-MATRIX-ACCESS-CLASS-2026-11-22.md ; dane: data/pid_matrix_655.csv ; narzędzie: tools/pid_matrix.py

HARD: klasa sidecar (rekord +0x24) = tryb dostępu: 0 live (208), 1 komenda (49), 2 lustro z centrali (44), 3 nastawa (354); zgodna 448/448 z `access` katalogu panelu;
bramki kodu: 0x08011812 z kontrolą przyjmuje 1,3; sync 0x08011368 obejmuje 2,3. 557/655 PID ma klucz UI (T1 z instancjami + T2). Key 3 Language nie ma klucza UI (dostęp bezpośredni z class 12).
STRONG/INFERENCE: 0x300B "Stop burning wood" jest klasy 1 (komenda), więc etykieta Podajnik/Wentylator zależy od stanu komendy w czasie pracy, nie od konfiguracji sprzętu (koryguje wcześniejsze przypuszczenie).
OPEN: wartość 0x300B w runtime; semantyka klasy 2 (INFERENCE: stan tylko z centrali); 98 PID bez klucza UI; weryfikacja PID == indeks CAN na żywym busie.


## AUTONOMOUS PASS 37 — SEKWENCJA ODCZYTU 0x0604 I ZACHOWANIE RX 0x0584 — 2026-11-22
Raport: analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-37-CAN-POLLER-AND-RX-BEHAVIOR-2026-11-22.md ; dane: data/poll_sequence_655.csv ; narzędzia: tools/poller_trace.py, tools/can_rx_inject.py

HARD (wykonane w firmware): ramka odczytu na szynie = StdId 0x0604, DLC 8, Data = 40 idx_lo idx_hi 01 00 00 00 00 (Data[0]=cmd, [1..2]=indeks LE, [3]=subindeks 1, [4..7]=wartość). Poller wysyła 655 żądań (każdy PID raz, kolejność slotów).
RX 0x0584/cmd 0x42/sub 1: wartość zapisywana z walidacją min/max rekordu (także klasa live, także s16 ujemne); ignorowane cmd 0x60, sub != 1, StdId 0x585.
STRONG: struktura zgodna z CANopen SDO expedited (0x600+4/0x580+4, 0x40/0x42/0x20/0x60/0x80).
KOREKTA: "Data[3]=0x40, Data[4..5]=indeks, Data[6]=1" w starszych dokumentach to offsety struktury kompaktowej, nie numeracja bajtów na szynie.
OPEN: okres pollera i producent +0x08/+0x10; timeout/+0x0C; pełna zgodność z CiA 301.


## AUTONOMOUS PASS 38 — PUBLIKACJA LOKALNEJ ZMIANY PARAMETRU — 2026-11-22
Raport: analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-38-LOCAL-CHANGE-PUBLICATION-2026-11-22.md ; narzędzie: tools/publish_probe.py
HARD (wykonane w firmware): lokalna zmiana storage Language 0->7 + callback managera 0x08010FCE => dokładnie jedna ramka 0x584, DLC 8, Data 42 03 00 01 07 xx xx xx; brak powtórzeń bez zmiany (on-change).
Nieużywane bajty wartości ponad szerokość typu nie są zerowane (śmieci) — moduł ESP32 ma wysyłać zera, odbiorca maskować.
OPEN: klasa 2 i klasa 0 lokalnie zmieniona; okno przetwarzania i okres callbacku; kierunki/role urządzeń na żywym CAN.


## AUTONOMOUS PASS 39 — CLASS 12 = PRZEŁĄCZANIE JĘZYKA (setLanguage) — 2026-11-22
Raport: analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-39-LANGUAGE-CLASS12-SETLANGUAGE-2026-11-22.md ; narzędzie: tools/lang_cycle_probe.py
HARD (wykonane w firmware): class 12: GET key 3 -> +1 -> zapis key 3 (mod 8, typ 5) -> tail-call FUN_080391D6 = setLanguage (currentLanguage u16 @0x20024860, currentLanguagePtr = tablica[v]); cykl 0..7 potwierdzony.
HARD: tablica języków SRAM 0x20011844 ma 8 wpisów: 0 PL, 1 EN, 2 LT, 3 SK, 4 CZ, 5 ES, 6 RO, 7 EST (identyfikacja z treści tabel TypedText).
STRONG: wiersz menu 15 (klasa 12, budowany przy access != 0) uruchamia zmianę języka. KOREKTA: klasy wierszy 15..20 pochodzą z pola +2 rekordu menu.
OPEN: 3 pozostałe wywołania setLanguage i przywracanie języka przy starcie; znaczenie pola +2 rekordu dla wierszy 0..14; dotyk -> class 12.
