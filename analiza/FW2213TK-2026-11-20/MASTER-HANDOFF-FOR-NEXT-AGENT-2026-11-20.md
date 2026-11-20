# TEKLAPELLETCAN — MASTER HANDOFF / INSTRUKCJA DLA NOWEGO AGENTA
Data: 2026-11-20
Repozytorium: GieOeRZet/TeklaPelletCAN
Firmware: FW2213TK_kopia.bin
Firmware SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

## 0. Najważniejsza zasada

Celem projektu jest możliwie wierne, 1:1 odtworzenie całego softu Estyma/igneoTouch z firmware FW2213TK, z wyjątkiem fizycznej platformy docelowej.

Nie tworzymy tylko sterownika CAN.
Nie tworzymy „wersji podobnej”.
Nie przepisujemy starego projektu TeklaPelletCAN.
Nie przyjmujemy znaczeń rejestrów ze starego projektu bez potwierdzenia w firmware.

SOURCE OF TRUTH:
1. firmware i jego bezpośrednia analiza;
2. ekstrakty z firmware: kod, xref, tablice, bitmapy, TypedText, parametry, geometria, CAN;
3. dokumentacja producenta jako cross-check;
4. obserwacje użytkownika, zdjęcia ekranów i skany CAN jako dane testowe/hipotezy;
5. stary projekt jako materiał pomocniczy.

Jeżeli firmware przeczy staremu projektowi, firmware wygrywa.

## 1. Obowiązkowa lektura przed dalszą analizą

Czytaj w tej kolejności:

1. analiza/FW2213TK-2026-11-19/MASTER-STATE-CONSOLIDATED-2026-11-19.md
2. analiza/FW2213TK-2026-11-19/START-HERE-FOR-NEXT-AGENT.md
3. analiza/FW2213TK-2026-11-20/CHAT-CONTINUITY-2026-11-20-ARCHITECTURE-RESET.md
4. analiza/FW2213TK-2026-11-20/CHAT-ARCHIVE-RAW-STATUS.md
5. analiza/FW2213TK-2026-11-20/SOURCE-OF-TRUTH-POLICY-2026-11-20.md
6. analiza/FW2213TK-2026-11-20/DOCUMENTATION-COVERAGE-AUDIT-2026-11-20.md
7. wszystkie aktualne MULTIPASS/BATCH dotyczące 6154, UI, Home, bitmap i graph.
8. na końcu najnowszy checkpoint branży, nad którą kontynuujesz.

Nie zaczynaj od zera i nie odkrywaj ponownie rzeczy już zamkniętych.

## 2. Zasada pracy

Użytkownik oczekuje głębokiej analizy wieloprzebiegowej.

Nie kończ analizy po pierwszym znalezionym xref.

Dla ważnej gałęzi wykonuj równolegle:
- direct xref;
- indirect xref;
- vtable/caller/factory;
- konstruktor -> obiekt -> pole -> writer;
- dane/tabele;
- stringi PL/EN i pozostałe języki;
- bitmapy;
- geometria;
- gate/configuration;
- poziom dostępu;
- parametr/model;
- odczyt/zapis;
- CAN;
- host/content;
- warianty sprzętowe;
- korelację z instrukcją producenta.

Przydatne jest prowadzenie wielu niezależnych hipotez i zamykanie ich dowodami.

Nie zatrzymuj się po „fajnym” znalezisku. Najpierw zamknij gałąź na tyle, na ile pozwala firmware, potem wróć do mapy globalnej.

## 3. Dokumentowanie każdego chatu

Po każdym większym przebiegu zapisz do repo:
- czego chciał użytkownik;
- co zostało zbadane;
- twarde dowody;
- nowe odkrycia;
- korekty poprzednich hipotez;
- odrzucone interpretacje;
- OPEN;
- następny atak;
- commit SHA.

Nie twierdź, że zapisałeś surowy transcript, jeżeli nie masz dostępu do pełnego transkryptu.

CHAT-ARCHIVE-RAW-STATUS.md wyjaśnia ograniczenie: GitHub connector nie udostępnia pełnej historii rozmowy, w tym pominiętych/skróconych wiadomości. Prawdziwy raw transcript można zachować dopiero po uzyskaniu eksportu/pliku rozmowy.

## 4. Firmware i narzędzia

Lokalny firmware:
 /mnt/data/FW2213TK_kopia.bin

Rozmiar:
 2,031,616 bytes

SHA-256:
 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

Dostępne narzędzie:
 /usr/local/swift/usr/bin/llvm-objdump

Przydatna konwersja:
 llvm-objcopy --input-target binary --output-target elf32-littlearm FW2213TK_kopia.bin /tmp/fw.o

Disassembly:
 llvm-objdump -D --triple=thumbv7m /tmp/fw.o

W wielu analizach runtime address dla kodu jest interpretowany jako 0x08000000 + raw offset. Nie mieszać tego z bazą 0x08010000 używaną przy rozwiązywaniu części pointerów zasobów.

## 5. Bitmapy

Tabela bitmap:
 raw 0x54450
 stride 0x14
 188 entries, IDs 000..187

Pointer/resource mapping dla bitmapów używa bazy 0x08010000 w odpowiednich tabelach.

Najważniejsze potwierdzone zasoby:
- 056: 20x20, normalny marker graph;
- 057: 20x20, wariant zaznaczony/aktywny; ma także inne użycie, więc NIE nazywać graph-only;
- 151: 31x30;
- 152: 31x30, para selector dla komponentu 47290;
- 115: 40x41;
- 144: 36x41;
- 174: 40x38;
- 91/92: 39x23;
- 51/52/53: 34x29.

Bitmap 056/057 wizualnie są parą markerów: 056 szary, 057 z jasnym/zielonym środkiem.

Ważna luka artefaktowa: wiedza o bitmapach, mapa, wymiary i hashe są zapisane, ale komplet fizycznych PNG 000..187 nie jest obecnie potwierdzony jako trwały zestaw plików w GitHub. Nie twórz fałszywego twierdzenia, że są tam wszystkie PNG. Przy najbliższej okazji odtwórz i zapisz artefakty wraz z manifestem SHA-256, jeśli możliwości repo na to pozwolą.

## 6. TypedText / języki

Firmware zawiera 8 tabel TypedText:
- ES
- EST
- EN
- LT
- PL
- RO
- SK
- CZ

Każda ma 495 wpisów.
Tabela PL jest bezpośrednio odzyskiwalna.

Nie traktuj braku indeksowanego stringa jako dowodu braku funkcji.

Najważniejsze:
- ID 57 = Ogrzewanie 1;
- ID 99..102 = OGRZEWANIE 1..4;
- ID 119..122 = Ogrzewanie obwód 1..4;
- ID 183 PL = Wentylator wspomagający [%];
- ID 183 EN = Extra exhaust fan [%];
- ID 199 PL = Moc dmuchawy modulacja [%];
- ID 199 EN = Blower power modulation [%];
- ID 182 = Podajnik palnika;
- ID 454 = Próg zmniejszania stopnia mocy [%];
- ID 468 = Ruch rusztu interwał [min];
- ID 493 jest używany przez boiler widget.

Numericzne ID bitmapy i TypedText są osobnymi przestrzeniami. Bitmap 57 NIE oznacza TypedText 57.

## 7. Główna mapa menu / access

Tabela main menu raw 0x42348:
21 rekordów x 6 bytes.

Pierwsze 15 rekordów są budowane zawsze; rekordy 15..20 są dodawane, gdy access != 0.

Access == 0:
rows 0..14.

Access != 0:
rows 0..20.

Semantyka pierwszych zamkniętych pozycji:
0 Kocioł
10 Palnik
1 CO1
2 CO2
3 CO3
4 CO4
5 CWU
6 Solar
7 Buffer
8 Cascade
9 Additional fuel storage
11 Alarm history
13 Program information
17 Configuration
15 Menu level/PIN

Nie dopisuj Language/Sound alarm/Output test/Statistics/Network do tej grupy bez niezależnego dowodu.

Row builder:
FUN_0804BC6C(row, bitmap_A, bitmap_B)
- +0x8C używa A;
- +0x60 używa B;
- dalej geometria/resource/vtable.

A i B są warstwami stanu/dekoracji oraz semantycznego ikonu, nie traktuj ich automatycznie jako jednej rzeczy.

## 8. PIN / access level

Firmware:
0x180A = 6154

Resolver:
0900 -> level 1
0999 -> level 2
6154 -> level 3

Level 3 daje realne zmiany drzewa UI/interakcji.

17 znanych level-3 gates:
0x4A566
0x4AA42
0x4B22A
0x4C15A
0x4EA32
0x4F456
0x4F79A
0x4FEF2
0x501F2
0x504AE
0x5076A
0x50A7E
0x50D3A
0x50FF6
0x512B2
0x5156E
0x5FB0A

Wrappers:
0x4A510
0x4A9EC
0x4B1D4
0x4C104
0x4E9DC
0x4F400
0x4F744
0x4FE9C
0x5019C
0x50458
0x50714
0x50A28
0x50CE4
0x50FA0
0x5125C
0x51518
0x5FAB4

Handler FUN_0802FB04:
parent+0x23C = increment
parent+0x284 = decrement
parent+0x60 = current
parent+0x64 = upper bound

Concrete anchor:
FUN_0804A510 -> TypedText 454 -> Próg zmniejszania stopnia mocy [%], geometry X=439 Y=0 W=40 H=30.

## 9. Context / instance architecture

Do NOT collapse all context offsets into one meaning.

Established:
- +0x12A = global/application context/page-family byte; multiple values 0..5 exist.
- +0x12B = variant/class/resource-family selector.
- +0x12C = separate active-instance dimension, values 1..4 in traced paths.
- FUN_08036FF2 performs instance-aware parameter lookup.
- FUN_080370C0 / FUN_08037212 provide read/write-side instance indexing.
- FUN_0803E714 consumes +0x12B values 1..4 in a shared Heating UI branch.
- FUN_0803C064 has a TBB dispatcher:
  selector 16 -> +0x12B=0x11
  selector 17 -> +0x12B=0x10
  selector 18 -> alternate setter path.
- selector source is RAM table 0x20005EF0.
- caller around 0x0807EB00 walks registry at object+0x3B4 with 0x274-byte stride.
- exact semantic identity of registry entries 16/17/18 remains OPEN.
- +0x3D8 suspected callback/model binding, not closed.
- FUN_08035786 is position/slider/value interpolation/geometry, NOT proven CAN writer.

Known parameter families:
0x2032..0x2035
0x2048..0x204B
0x2064..0x2067

## 10. Blower graph — closed branch so far

User image shows:
Moc dmuchawy modulacja [%]
five graph points:
20 / 40 / 60 / 80 / 100.

Firmware:
0x2261 = 20%
0x2262 = 40%
0x2263 = 60%
0x2264 = 80%
0x2265 = 100%

FUN_0803EC18 has a graph-data branch resolving indices:
0x4A..0x4E -> 0x2261..0x2265.

Second family:
0x4F -> 0x2268
0x50 -> 0x226E
0x51 -> 0x226F
0x52 -> 0x2275
0x53 -> 0x227A

These are a second five-point family identified in firmware as exhaust/extra fan characteristic.

Do not merge the families into one ten-point graph.

Manufacturer manual cross-check:
- pkt 4.2.1 describes blower modulation graph;
- extra/boost/exhaust fan has characteristic like pkt 4.2.1;
- parameters can be hidden depending on menu/access/configuration.

## 11. Critical new branch: extra fan / configuration

TypedText:
ID 183 = Wentylator wspomagający [%] / Extra exhaust fan [%].

Direct executable path:
FUN_0803CF54
 -> resolver index 0x68 via FUN_08036FF2
 -> FUN_08043A36
 -> object at r0+0xF74

FUN_08043A36:
if incoming r1 == 1:
  TypedText 182 = Podajnik palnika
else:
  TypedText 183 = Wentylator wspomagający [%]

This is direct firmware evidence that the UI chooses between burner feeder and extra fan according to a configuration/state result.

Exact meaning of resolver index 0x68 remains OPEN.
Do NOT invent its parameter ID.

Next attack:
1. Find every code/data use of resolver 0x68.
2. Find the source of its returned value and gate.
3. Identify parent/host of object+0xF74.
4. Map neighboring controls in FUN_0803CF54.
5. Connect the branch to 0x2268..0x227A explicitly.
6. Identify module/equipment/source configuration causing it.
7. Then integrate into global configuration graph.

## 12. Graph component

FUN_08047604 constructs reusable graph content.
- five point objects at parent+0x2E8, stride 0xE4;
- four sibling graphic layers at +0x75C, stride 0x54;
- central region around +0xB80;
- geometry call gives X=35 Y=50 W=335 H=180;
- graph bounds include +0x68=100, +0x6C=0, +0x70=100.

FUN_08047A8A:
- receives point source pointer;
- count in +0x60;
- source pointer in +0x64/+0x68;
- point records stride 8.

FUN_08047C1A:
- clamps point coordinates;
- Y scale uses 300;
- X interpolation uses ~160;
- stores Y/X arrays;
- manipulates point graphics.

FUN_08047D80:
- refresh/selection path;
- writes bitmap 056 through FUN_080307BC.

FUN_0804752C / FUN_080475A4:
- directly write bitmap 057;
- exact parent/vtable origin still OPEN;
- therefore 057 is selected counterpart but not graph-only.

FUN_08048520:
- graph component at parent+0x963C;
- calls FUN_08047A8A;
- switches dynamic host/content with FUN_0802EADE(parent+0x84F4,...).

## 13. 47290 must stay separate

FUN_08047290 / FUN_08047334 are NOT proven to be the five-point graph.

47290:
- six slots;
- first object +0xA8;
- stride 0x40;
- positions X=100, Y=50+34*slot;
- labels supplied by caller object+0x08, six u16 TypedText IDs;
- bitmap selector pair 151/152.

Hard stack provenance:
caller object r4:
[r4+0x08] -> pointer to six TypedText IDs
[r4+0x07] -> byte argument
[r4+0x0C]-1 -> slot/count argument

FUN_08047334 consumes param_7[slot] as TypedText ID.

Do NOT infer that these six labels are 0x2261..0x2265 or the exhaust family.

## 14. Home / UI architecture

Full 480x272 frame is proven in relevant configuration path via FUN_08030358.

FUN_0803E5AC builds a large object tree including:
+0x380 FUN_08038ED0
+0x3BC FUN_08041E1C
+0x3EC FUN_08041E1C
+0x41C FUN_08047230
+0x42C repeated FUN_0800DCD4 stride 0x338 count 0x28
+0x84F4 host
+0x8F70 FUN_08047244
+0x92DC FUN_08047290
+0x963C graph
+0xA26C FUN_08047E54
+0xA5FC/+0xA628 FUN_08038ED0
+A654/A680 bitmap resource objects
+A6AC/A6BC/A6CC/A6DC graphic functions.

Important user correction:
The six vertical slots from 47290 are NOT on Home screen.

Do not assume every child of this tree is simultaneously visible on Home.
Dynamic host/content switching is hard evidence of reusable/dynamic content.

User visual anchors:
115 = lower-right Home settings/menu/power tile
144 = CO1 tile icon
174 = CWU tile icon

No direct immediate literal loads were found for these three, so indirect/vtable/resource tracing is required.

Bottom/status-like objects around 080480C0:
root+0xA604 container 480x50, bitmap 91 centered
root+0xA604+0x2C container 480x50, bitmap 92 centered
semantic role OPEN.

## 15. Boiler / hopper / animation

Boiler widget FUN_080469E8 instantiated four times:
+0x168 internal canvas 0,0,1000,1000
+0x13C resource 14
+0x5C TypedText 493 X=0 Y=130 W=70
+0xCC TypedText 493 X=25 Y=40 W=45 H=50
parent placement OPEN.

Hopper:
0802BDF0 / 0802C294 and 0802DA54 use bitmaps 51/52/53 as hopper state machine.
This proves state machine, not Home placement.

Animation engine:
0803079A / 080307AE / 08030708 / 08030640
- 138..143 pump
- 105..107 mixer
- 8..10 fan
- 36..44 feeder/grate/heater group

## 16. Main parameter/CAN facts

Configuration resolver selector 1..9:
1..4 heating/CO config
5 -> internal 0x10F
6 -> 0x110
7 -> 0x111
8 -> 0x350C
9 -> 0x3525

Known CAN mappings:
0x10F -> CAN 0x2105
0x110 -> CAN 0x2107
0x111 -> CAN 0x2106
0x114 -> CAN 0x2108

0x2105 is NOT yet proven source of C064 object creation.

DAT_0804107C / 0x08040FC2 is classified as Test I/O, not main CO activation bridge.

## 17. Main architectural warning

The old project and observed CAN registers are useful only as cross-checks.

Do not use:
- old register semantics,
- old UI assumptions,
- old screen layout,
- old module dependencies,
as implementation truth.

The final module must derive its behavior from the reconstructed firmware model.

The user's idea that add-on modules may obtain/use boiler configuration from Igneo Touch is plausible and should be tested in firmware, especially through:
- shared parameter records;
- CAN IDs;
- configuration propagation;
- module activation gates;
- source/room-controller configuration;
- restart/commit paths;
- parameter-copy mechanisms.

## 18. Manufacturer documentation

Permanent external cross-check sources supplied by user:

1. Estyma — InstrukcjaTeklaPelletInstalator_PL.pdf
https://estyma.pl/wp-content/uploads/2020/02/InstrukcjaTeklaPelletInstalator_PL.pdf

2. Tekla — instrukcja kotły automatyczne pellety 08/2025
https://www.teklakotly.pl/media/transfer/doc/instrukcja_kotly_automatyczne_pellety_08_25_compressed_2.pdf

3. Tekla — tabele nastaw kotłów serii BIO 02/2025
https://www.teklakotly.pl/media/transfer/doc/tabele_nastaw_kotlow_serii_bio_02_2025_min_2.pdf

4. Tekla — instrukcja kotłów automatycznych ekogroszek
https://www.teklakotly.pl/media/transfer/doc/instrukcja_kotly_automatyczne_ekogroszek_inst_rem_2.pdf

Use these as terminology/function cross-checks only.

## 19. Key previous reports / checkpoints

Important files include:
- MASTER-STATE-CONSOLIDATED-2026-11-19.md
- START-HERE-FOR-NEXT-AGENT.md
- BATCH-WHOLE-SOFTWARE-MULTIPASS-2026-11-20.md
- BATCH-ANIMATION-ENGINE-AND-ACTUATOR-MAPS-2026-11-20.md
- BATCH-ORIGINAL-TOUCH-HOME-IMPLEMENTATION-2026-11-20.md
- HOME-GEOMETRY-FW-ONLY-MULTIPASS-2026-11-20.md
- HOME-GEOMETRY-USER-VISUAL-CORRELATION-2026-11-20.md
- BATCH-ORIGINAL-SOFTWARE-ARCHITECTURE-RESET-2026-11-20.md
- CHAT-CONTINUITY-2026-11-20-ARCHITECTURE-RESET.md
- MULTIPASS-12-6154-DEEP-AUDIT-2026-11-20.md
- MULTIPASS-13-6154-NUMERIC-CONTROL-PARAM-BINDING-2026-11-20.md
- MULTIPASS-14-6154-17-WRAPPER-MATRIX-ATTACK-2026-11-20.md
- MULTIPASS-15-GRAPH-056-057-2261-227A-HARD-TRACE-2026-11-20.md
- MULTIPASS-16-REUSABLE-GRAPH-MARKERS-CONFIG-UI-2026-11-20.md
- MULTIPASS-2261-2265-GRAPH-VS-47290-CORRECTION-2026-11-20.md
- MULTIPASS-47290-3EC18-SEMANTIC-DISAMBIGUATION-2026-11-20.md
- MULTIPASS-47290-SOURCE-CONTEXT-DEEP-TRACE-2026-11-20.md
- CHECKPOINT-47290-SOURCE-CONTEXT-2026-11-20.md
- MULTIPASS-18-DIRECT-STRING-AND-FAN-BRANCH-2026-11-20.md
- CHAT-CONTINUITY-2026-11-20-BLOWER-FAMILIES-WHOLE-SOFTWARE-RESET.md
- DOCUMENTATION-COVERAGE-AUDIT-2026-11-20.md
- CHAT-ARCHIVE-RAW-STATUS.md

When a file is already a detailed report, read it instead of recreating its findings from scratch.

## 20. Current OPEN queue — priority

P0:
1. resolver 0x68 source/gate;
2. exact relation between extra fan UI branch and 0x2268..0x227A;
3. parent/vtable origin of FUN_0804752C / FUN_080475A4;
4. exact configuration/equipment condition exposing extra fan;
5. complete graph/resource reuse matrix.

P1:
6. complete 17-row 6154 parameter binding matrix;
7. +0x3D8 callback/model binding;
8. 47290 six TypedText ID source;
9. Home indirect resource traces for 115/144/174;
10. module/source/room-controller/CAN dependency graph.

P2:
11. persistent extraction of all 188 bitmap PNGs;
12. full parameter -> UI -> CAN catalogue;
13. full screen/state machine;
14. final 1:1 implementation mapping.

## 21. Required behavior for next agent

When starting:
- read this file;
- read START-HERE;
- read MASTER-STATE;
- read latest relevant multipass;
- verify current firmware hash;
- continue from OPEN queue.

Do not ask the user to repeat known project context.
Do not restart the analysis from scratch.
Do not assume the old TeklaPelletCAN implementation is correct.
Do not silently convert hypotheses into facts.
Mark confidence explicitly: HARD / HIGH / MEDIUM / OPEN / REJECTED.

After a substantial run:
- create/update a report in Git;
- include exact addresses, offsets, xrefs, raw evidence and confidence;
- add a continuity checkpoint;
- record corrections;
- only then summarize to the user.

The final implementation is downstream of reverse engineering. First reconstruct the firmware architecture and dependencies, then implement.

## 22. Current strategic direction

The immediate branch is the extra/boost/exhaust fan configuration branch because it is an excellent test case for the general mechanism:

configuration -> gate -> UI variant -> reusable graph -> parameter family -> model -> CAN.

But this branch is NOT the project goal by itself.

After it is closed, return to the global architecture and select the next high-value branch. The end state is a complete 1:1 map of the software, including variants and add-on modules.

## 23. Chat archive truth

The repository contains technical continuity records, not a fabricated complete raw transcript.

If a future agent receives an exported ChatGPT transcript as a file, it should be added verbatim to Git and referenced from CHAT-ARCHIVE-RAW-STATUS.md.

Never invent omitted conversation text.
Never claim a summary is a raw transcript.

## 24. Final instruction

Use maximum practical analysis resources.
Use many passes when necessary.
Do not stop at crumbs.
Trace branches from UI to model to CAN and back from configuration to visibility.
Keep the entire system map in view.
Persist every important result.
The objective is firmware-faithful reconstruction of the whole software, not a collection of isolated discoveries.


## 25. Latest execution checkpoint — 2026-11-20 / MULTIPASS-21

Execution-only pass requested by the external deep-analysis agent:
- inspected 0x89440..0x89490;
- extracted raw table bytes 0x08B4C8..0x08B4EE;
- recorded 32-bit words and derived relative targets 0x0784F5 and 0x06E68D;
- captured requested raw code windows around those targets;
- no contiguous source payload for destination 0x20011534..0x20011669 was identified in this specific table pass.

Full raw execution evidence:
- analiza/FW2213TK-2026-11-20/MULTIPASS-21-IAR-INIT-TABLE-EXECUTION-2026-11-20.md

Current workflow rule from the user:
- external deep agent performs semantic analysis;
- this assistant executes requested BIN/Git extraction and verification tasks;
- requested raw material should be returned as one copyable block when asked;
- do not add assistant-side analysis until the user explicitly asks for consolidation/own analysis;
- persist substantial execution results and conversation continuity in Git.


## 26. Latest execution checkpoint — 2026-11-20 / MULTIPASS-23

Closed execution chain recorded:
- 0x94644 = __iar_program_start
- 0x8B4A8 = __iar_init_vfp
- 0x8F74C = __cmain
- 0x89440 = __iar_data_init3
- 0x6E68C = __iar_lz77_init3
- 0x784F4 = __iar_zero_init3

IAR record 2:
- source 0x96114..0x9694E
- 2106 bytes compressed/input span as requested
- destination 0x20000000
- reconstructed output 0x118B3 = 71859 bytes
- target 310-byte block 0x20011534..0x20011669 fully reconstructed.

HARD branch closure:
- 0x47 = case 10 / Palnik, gate +0x158 != 0, first element at 0x200115D0.
- 0x48 = case 0 / Kocioł, gate +0x158 != 0, first element at 0x200115B0.
- 0x48 is NOT in case 10.
- case 0x10 = Konfiguracja.
- case 0x11 = Statystyki/Info.

Raw package:
- FUN_080480C0 complete Thumb disassembly 0x480C0..0x48422 recorded in MULTIPASS-23.
- raw 96-byte span 0x7F58C..0x7F5EB recorded in MULTIPASS-23.
- report: analiza/FW2213TK-2026-11-20/MULTIPASS-23-IAR-LZ77-47-48-CLOSURE-480C0-TYPEDTEXT-RAW-2026-11-20.md

FUN_080480C0 remains execution-level OPEN for downstream semantic filtering:
- no direct literal 0x47/0x48 comparison in this function window;
- downstream helpers/table still require external-agent semantic analysis.

Workflow:
- external deep-analysis agent performs semantic analysis;
- this assistant executes requested BIN/Git extraction and verification;
- raw requested material is returned as one copyable block when asked.


## 27. Consolidated checkpoint — uploaded FW2213TK analysis package + current execution state — 2026-11-20

The user supplied the previous analysis package `FW2213TK_wyniki_analizy_2026-11-20.zip`. It was inspected directly. The package contains:
- `RAPORT-FW2213TK-LZ77-I-PARAMETRY-2026-11-20.md`
- `FUN_0803E714_parametry_wg_PIN.json`
- `FUN_0803E714_parametry_wg_PIN.csv`

The package independently confirms and consolidates the following already-established HARD facts:
- firmware SHA-256: `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`;
- IAR startup/data-init chain through `__iar_lz77_init3` and `__iar_zero_init3`;
- reconstructed SRAM image length `0x118B3` / 71859 bytes;
- reconstructed list block `0x20011534..0x20011669` (310 bytes);
- complete FUN_0803E714 parameter lists by access level;
- `0x47` = Palnik / case 10 / first level-1 element at `0x200115D0`;
- `0x48` = Kocioł / case 0 / first level-1 element at `0x200115B0`;
- `0x47` graph family = `0x2261..0x2265`;
- `0x48` graph family = `0x2268,0x226E,0x226F,0x2275,0x227A`;
- 6154 is level 3, but FUN_0803E714 itself only has level-2 branching; level-3 UI exposure occurs through separate gates.

The uploaded report also preserves the raw 310-byte SRAM dump and the parameter-list JSON/CSV, so these are now treated as an external corroborating source package, not as a replacement for firmware-derived evidence.

Current execution-only state:
- the latest raw execution package sent to Gemini contains the complete `FUN_080480C0` Thumb window and raw `0x7F58C..0x7F5EB` span;
- Gemini is currently performing semantic analysis of that material;
- no new semantic conclusion is to be invented by the execution layer while Gemini is working;
- next work should execute Gemini's requested addresses/tables/helpers exactly and return raw evidence in one copyable block.

Current priority remains the OPEN branch around `FUN_080480C0`, resolver/index `0x68`, extra/boost/exhaust fan configuration, and the relation to graph family `0x48`, followed by the global software reconstruction queue.

Source package note:
- The uploaded ZIP was inspected successfully from the conversation sandbox.
- Its contents match the consolidated report already represented in the project handoff; no contradiction was found in the supplied package.


## 28. MULTIPASS-25 — 47290 / 0x47 / 0x48 option tables + PIN wrapper — 2026-11-20

Completed requested execution pass:
- corrected previous 0x7F58C address-base mistake;
- extracted real file offset 0x6F58C..0x6F5FF, 116 bytes;
- disassembled 0x4E9DC..0x4EA50;
- recorded requested HARD closures for FUN_080480C0 presenter-list filtering and 480x50 access-level separators;
- report: analiza/FW2213TK-2026-11-20/MULTIPASS-25-47290-47-48-OPTION-TABLES-PIN-4E9DC-2026-11-20.md
- commit: c33eeeee26327aeefbab3b67dcb20d96803d95e0

The corrected option-table bytes are now the authoritative raw extraction for this branch.

## 29. HOME SCREEN 02 — 2026-11-20 execution checkpoint

External-agent execution request completed against the verified firmware ELF.

Raw Thumb windows executed exactly as requested:
- 0x0802CA50..0x0802CEE0
- 0x0802CEE0..0x0802D050

Purpose:
- Home tile geometry / parent-child extraction;
- five activity-indicator geometry extraction.

No semantic reinterpretation was added by the execution layer. The complete raw disassembly was returned as a single copyable package to the external deep-analysis agent.

HOME-01 closures persisted in Git:
- REJECTED: no-direct-literal-load assumption for bitmap IDs 115/144/174;
- HARD: ButtonWithIcon tile state/background/icon configuration;
- HARD: CO1/CO2/CWU offsets and configuration/CAN gates;
- HARD: five activity indicator object/visibility offsets;
- HARD: Home summer/winter, WiFi and boiler-image setter paths;
- HARD: Buffer setter is no-op in Home path.

HOME-01 updated commit: 91e59c433f850f047fe1b2c958f1c74797a8e5ee

Next semantic step: derive exact X/Y/W/H and parent-child hierarchy from the raw 0x2CA50..0x2D050 windows, without replacing raw evidence by inference.