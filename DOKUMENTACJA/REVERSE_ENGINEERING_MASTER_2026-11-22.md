# NewEstyma / TeklaPelletCAN — MASTER REVERSE ENGINEERING HANDOFF

Stan: 2026-11-22  
Repo: GieOeRZet/TeklaPelletCAN  
Branch: `ccr-be8a1bcb-5t76j0`

## 0. Cel

Celem NewEstymaCan/TeklaPelletCAN jest możliwie pełne odtworzenie Estymy 1:1 jako uniwersalnej implementacji. ESP32-C6 ma być dodatkowym modułem Estymy na tej samej magistrali CAN, nie zamiennikiem sterownika. Docelowo ten sam model ma obsługiwać CAN, ESP32, Home Assistant, Web i Android.

Gemini pełni rolę lead RE/proof authority; ChatGPT/OpenAI jest execution lab. Jeśli podczas wykonywania pojawia się wyraźna nowa gałąź RE, można ją autonomicznie pogłębić i zapisać jako kolejny Pass.

## 1. Canonical firmware

Plik: `FW2213TK_kopia.bin`  
Size: `0x1F0000 = 2,031,616 B`  
SHA-256: `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`

Mapowanie:

```
PROJECT = 0x08000000 + RAW
RUNTIME/RE_PACK = PROJECT + 0x10000
RAW = RUNTIME - 0x08010000

Important: vtable/function-pointer values stored by the running firmware are runtime addresses. They must be translated by -0x10000 before indexing RAW.
```

Surowy BIN jest źródłem prawdy. Komentarze ze starych deasemblacji nie są dowodem.

## 2. Najważniejsze zasady RE

- zachowuj RAW + PROJECT,
- wykonuj szeroki skan i Pass 2,
- rozdzielaj FACT od INFERENCE,
- nie utożsamiaj braku znalezionego XREF z brakiem funkcji,
- nie zakładaj CANopen/SDO bez dowodu,
- nie traktuj katalogu 260 jako wszystkich parametrów firmware,
- nie buduj pełnego menu wyłącznie z katalogu parametrów.

## 3. CAN2 — potwierdzone

CAN2: `0x40006800`

RX:
- storage `0x200244BC`
- queue handle `0x200244DC`
- producer `0x0806F9F8`
- serializer `0x080617DC`
- CanRxTask `0x0806E94C`
- dispatcher `0x08063B80`

TX:
- storage `0x200244E0`
- queue `0x200244EC`
- queue primitive `0x08057224`
- CanTxTask `0x080654A8`
- hardware TX `0x08061734`

TX chain:
`0x0806E59C -> 0x200244EC -> 0x08057224 -> CanTxTask -> 0x08061734 -> CAN2`.

RX serializer:
- TIR IDE `&4`
- standard ID `>>21`
- extended ID `>>3`
- RTR `&2`
- DLC `TDTR&0xF`
- FMI `TDTR>>8`
- data `+0x0B..+0x12`.

CanRxTask: queue 100 × 20 B, handle przy object+0x20, frame przy +0x0C.

## 4. Vector/startup

VTOR = `0x08010000`, zapis PROJECT `0x08064620` / RAW `0x64620`.

Reset vector:
- RE_PACK `0x080A3209`
- PROJECT `0x08093209`
- RAW `0x93208`.

CAN2 RX0 vector:
- IRQn 64, vector index 80
- vector[80] `0x0807F9F9`
- PROJECT `0x0806F9F9`
- Thumb RAW `0x6F9F8`.

Brak rozpoznanego osobnego CAN2 RX1/SCE consumer path.

## 5. Protokół — obecny stan dowodów

Potwierdzone:
- `0x20` write
- `0x40` read
- `0x42` response/value
- `0x60` ACK
- `0x80` error

Known READ:
- StdId `0x0604`
- DLC 8
- Data[3]=`0x40`
- Data[4..5]=parameter index
- Data[6]=`0x01`

Publication/response path: `0x0584`.

## 6. Node 4 / obiekty

`FUN_0800FF44(0x200114C0,0x20008D60,0x20008D84)` ustawia:

```
[0x200114C0+0] = 0x20008D60
[0x200114C0+4] = 0x20008D84
[0x200114C0+8] = 4
```

FACT: node ID = 4.

D60:
- startup/dekompresja potwierdza `[0x20008D60]=0x080A4544`
- PROJECT vtable `0x08094544`
- slot0 PROJECT `0x0806E59D` / `FUN_0806E59C`.

Nie mylić z vtable PROJECT `0x08094568` dla RAM `0x2002466C`.

## 7. Parameter engine

Najważniejsze:
- resolver `0x08010FC2`
- `0x08014700`: zapis wartości + type 5
- `0x08014708`: type 2
- `0x08014710`: type 1
- `0x08014718`: type 4
- `0x08014720`: type 3
- `0x08014734`: getter wg typu
- `0x080115F6`: operacje na strukturach o kroku `0x2C`
- `0x08011812`: update/commit; pełna semantyka nadal OPEN
- `0x08062B22`: parser parametru; ID = Data[4] | Data[5]<<8; specjalne 3722/3723; resolver; typy 1..5.

Kluczowy anchor: `0x20008D84`.

## 8. 0x20008CD0 / D60 / D84

`0x20008CD0` ma bezpośrednie literal refs RAW:
`0x000DE8, 0x001AD8, 0x00473C, 0x006288, 0x007838, 0x00C60C, 0x00D7E0`.

`0x20008D60` nie ma bezpośredniego LE32 literal reference; jest wyprowadzane m.in. jako r8+0x90.

D0 potwierdzone pola:
- +0x0B = `0x20008CDB`
- +0x14 = `0x20008CE4`, param `0x3004`
- +0x20 = `0x20008CF0`, param `0x371E`
- +0x58 = `0x20008D28`, param `0x2165`
- +0x74 = `0x20008D44`, sub-IDs `0x3701`, `0x2250`
- +0x7C = `0x20008D4C`, param `0x3665`, init `0x54450000`
- +0x80 D50, +0x90 D60, +0x94 D64, +0x98 D68.

Pełny layout/ownership D84 nadal OPEN.

## 9. 260-slot catalog

Pass 7–10 potwierdziły:
- 260 unikalnych slotów,
- 260 unikalnych param_id,
- 260 unikalnych slotów,
- 0 duplicate param_id,
- 0 duplicate slots.

Tabela jest w okolicy RAW `0x037578`.

Pass 18 (stan końcowy):
- 260 katalogowych slotów,
- 247 ma init caller `0x0801143C`,
- 11 ma bezpośredni init `0x08014700`,
- 248 ma przynajmniej jeden z tych mechanizmów,
- 12 nie ma żadnego z nich,
- 512 różnych non-catalog PID pojawia się w analizowanym `0x08014700`,
- 409 string entries w `0x024C00..0x027700`.

12 bez żadnego match:
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

Brak matchu nie oznacza braku parametru.

## 10. Pass 12–18

### Pass 12
448 callerów `0x0801143C`, wzbogaconych o param_id/slot/nazwy/MOVW/literals.

### Pass 13
64 callerów miało nierozpoznane R1 w pierwotnym oknie; 13 slotów nie miało init caller.

### Pass 14
12/13 nie miało bezpośredniego MOVW; `0x218C` znaleziono jako realne użycie.

### Pass 15
Blok RAW `0x012C00..0x012D20` zawiera regularny init sąsiednich ID. Dla `0x218C`:

```
MOVW R0,#0x218C
MOVS R1,#0x28
ADD R0,R4
BL 0x08014700
```

FACT: init value = 40.

Sekwencja obejmuje m.in. `2174,218C,2198,21A4,21B0,21BC,21C8,21D4,21E0`.

### Pass 16/17
Przeskanowano wszystkich callerów `0x08014700` i zbudowano macierz 260.

### Pass 18
Powstał unified platform-agnostic catalog.

## 11. Znane ID/nazwy

Potwierdzone:
- `0x2105` = Heating configuration
- `0x2106` = Hot water configuration
- `0x2107` = Buffer configuration
- `0x2108` = Solar configuration
- `0x300B` = Stop burning wood

Potwierdzone: `0x68 -> 0x300B -> Stop burning wood`.

## 12. UI/resources

Bitmap runtime base: `0x08010000`. Descriptor table RAW `0x54450`. Potwierdzono 188 bitmap IDs 000..187.

Rozkład typów:
- type0 139
- type1 31
- type2 3
- type3 12
- type4 1
- type5 2.

Renderer: `0x0805570E`, RGB565 + A8 alpha.

TypedText PL pointer table: RAW `0x5BE64`.

Potwierdzone CO/CWU alignments:
- 00A9/00D9 comfort temp
- 00AA/00DA economy temp
- 00AC/00DC Program
- 00AF mode
- 00B0 room sensor
- 00B4..00B7 heating curve -20..10C.

## 13. Konfiguracja UI

Potwierdzone:
- internal 0x10E -> CAN 0x2105 Heating configuration; u8 0..4, default 1, RAM 0x20021FAF, code 0x0801A5B0
- 0x10F -> 0x2106
- 0x110 -> 0x2108
- 0x111 -> 0x2107.

`0x08037212` ma 33 UI callers i feeds local parameter write.

## 14. Access level / PIN

`FUN_08037E74`:
- 0 -> level 0
- 900 -> level 1
- 999 -> level 2
- 6154 -> level 3
- inne nonzero -> zachowuje poprzedni.

Level stored przy +0x158.

6154:
- UI constructors sprawdzają level >=3,
- dodają dodatkowe children,
- używany jest parent+0x23C,
- `0x0802FB04` +0x23C,
- +0x284 decrement,
- +0x60 value,
- +0x64 upper bound.

FACT: 6154 odblokowuje dodatkową warstwę UI.

## 15A. MenuTree — aktualizacja 2026-11-22

Nowy pass: analiza/FW2213TK-2026-11-22/MENUTREE-ATTACK-02-2026-11-22.md

Zamknięte nowe fakty:
- FUN_08032F08 jest metodą klasy childa utworzonego przez FUN_08032D7C; czyta child+0x2C. W MenuRow ten child jest twardo inicjalizowany pod +0xF8 przez FUN_0804BB42.
- 0x0803C270 nie jest osobnym entry-pointem Ghidra; leży wewnątrz FUN_0803C064 (+0x20C), więc nie nazywamy go niezależną funkcją bez RAW proof.
- FUN_0804BB42 jest odzyskanym konstruktorem klasy z layoutem zgodnym z row-builderem i vptr DAT_0804BC60; utożsamienie go z konkretnym MenuRow jest nadal STRONG, ale wymaga bezpośredniego RAW XREF.
- Odzyskany class layout ma twarde dzieci: +0x60 (FUN_0802DF08), +0x8C (FUN_0802FC10), +0xC4 (FUN_0802FC10), +0xF8 (FUN_08032D7C), dodatkowy +0x2C (FUN_08031BD4).
- FUN_0804BC6C operuje na tych samych child offsets i dołącza je przez vtable +0x64.
- capability resolver FUN_0803C178 jest osobną warstwą eligibility/visibility, nie nawigacją.
- Row class-family ma callback/action pointer przy +0x26C; FUN_0804BD7C sprawdza callback vtable +0x0C i wywołuje vtable +0x08 z row. Touch origin i selector/navigation target pozostają OPEN.

Nadal OPEN:
- dokładny RAW argument FUN_08032F08 w ścieżce 0x422C8;
- row vtable literal / konkretne sloty callbacków;
- touch/navigation;
- producer/content 0x20005F08;
- dokładna semantyka RAW sub-entry 0x0803C270;
- screen destinations selectorów 0/90/97/100/98/95;
- kompletne MenuTree.


## 15. Menu — WAŻNE: nadal NIE mamy pełnego drzewa

Nie mamy jeszcze kompletnego, dowiedzionego:
```
menu -> screen -> submenu -> child -> visibility condition -> parameter -> widget/text/bitmap -> handler
```

Mamy fragmenty:
- access-level gating,
- konfiguracje 2105..2108,
- część konstruktorów,
- część handlerów,
- parametry,
- bitmapy/TypedText.

Brakuje pełnej relacji parent->child i kompletnej tabeli warunków widoczności dla każdej konfiguracji.

## 16. Odrzucone hipotezy

Nie używać ponownie bez nowych dowodów:
- 0x68 = extra-fan gate
- 0x10E = 0x3505
- 0x10F = 0x2105
- graph 47290
- 47290 = Home seven horizontal zones
- 056/057 = 151/152
- bitmap ID = widget ID
- 370A 1/2/3 -> bitmap 011/012/013
- 174 = Home-only
- 0x08011812 = prosty dirty-bit/TX setter
- 0x08078578 == 0x08094508
- 0x08079704 = conventional executable vtable.

## 17. Global scan

- 11,337 BL edges
- 2,810 unique BL targets
- 9,656 ASCII >=5
- 5,604 ASCII >=7
- 3,957 UTF-16LE >=5
- 3,299 UTF-16LE >=7.

Top callers:
- 0x014700 = 872
- 0x010FC2 = 453
- 0x01143C = 448
- 0x014710 = 175
- 0x014720 = 80
- 0x015260 = 89.

## 18. Najważniejsze artefakty

- `BULK_FW2213TK_MAP.md`
- `BULK_FW2213TK_CROSSREF.md`
- `BULK_FW2213TK_SUBSYSTEMS.md`
- `BULK_FW2213TK_FOCUS_DECODE.md`
- `BULK_FW2213TK_MEGA.md`
- `out_pass10/pass10_portable_catalog.json`
- `out_pass12/pass12_mega_report.json`
- `out_pass13/pass13_mega_report.json`
- `out_pass14/pass14_mega_report.json`
- `out_pass15/pass15_mega_report.json`
- `out_pass16/pass16_mega_report.json`
- `out_pass17/pass17_mega_report.json`
- `out_pass18/pass18_mega_unified_catalog.json`
- `out_pass18/pass18_mega_unified_catalog.md`.

## 19. Najważniejsze luki

### P0
1. Pełny layout rekordów 0x2C.
2. Pełny model 0x20008D84.
3. Resolver -> descriptor -> getter/setter.
4. Pełne drzewo MENU/UI i visibility conditions.

### P1
5. Pełny CAN catalog: ID -> descriptor -> type -> getter/setter -> frame.
6. 12 catalog IDs bez match.
7. 512 non-catalog IDs z 0x08014700.
8. heartbeat/presence.

### P2
9. watchdog bit 0x2 owner.

## 20. Najlepszy następny kierunek

Nie robić kolejnego ślepego skanu 260 ID.

### Priorytet A — MENU TREE / UI VISIBILITY

Skanować:
- konstruktorów ekranów,
- addChild/removeChild,
- parent offsets,
- access_level,
- 0x2105..0x2108,
- inne configuration IDs,
- CMP/CBZ/CBNZ/Bxx,
- wejście/wyjście z ekranów,
- handlerów,
- bitmap,
- TypedText,
- parametrów.

Budować rekord:
```
SCREEN
  parent
  child
  visibility_condition
  access_level
  parameter
  text
  bitmap
  handler
  FACT/INFERENCE/UNKNOWN
```

### Priorytet B — parameter model

```
0x20008D84
 -> 0x2C records
 -> 0x08010FC2
 -> descriptor
 -> getter/setter
 -> CAN
 -> UI
```

### Priorytet C

Rozgryźć `0x218B <-> 0x218C <-> 0x2198...`, bo 0x218C ma potwierdzony default 40 i sąsiednią sekwencję inicjalizacji.

## 21. Minimalny handoff

> Mamy twardo potwierdzony CAN2 runtime, node 4, RX/TX, podstawowy protokół, resolver/parameter engine, pełną tabelę 260 slotów, dużą część UI/resources i access-level gating. Nie mamy jeszcze kompletnego modelu 0x2C/descriptorów ani pełnego drzewa menu z warunkami widoczności. To są obecnie najważniejsze cele. Pass 18 jest aktualnym punktem odniesienia.

**Firmware SHA-256:** `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`.


## MENU TREE ATTACK 03 — 2026-11-22 — class-family / C064 boundary correction

Nowy pass: `analiza/FW2213TK-2026-11-22/MENUTREE-ATTACK-03-2026-11-22.md`.

Najważniejsze korekty:
- `FUN_0804BC6C` jest metodą/helperem class-family; pełny decompiled.c pokazuje również call z `FUN_0804E4F8`, więc nie traktujemy go jako unikalnego konstruktora Main Menu Row. Utożsamienie row class pozostaje STRONG do czasu bezpośredniego RAW XREF.
- `FUN_08032D7C` tworzy stanowy child; w layoutcie odzyskanym przez `FUN_0804BB42` znajduje się pod row+0xF8. Jego +0x2C jest stanem, +0x150 jest callback/action pointer. `FUN_08032EB8` może wywołać ten callback po zmianie stanu.
- `FUN_0804BD7C` jest osobnym dispatcherem callback/action przez row+0x26C.
- `functions.txt` zawiera formalnie tylko `FUN_0803C064` (558 B). Adresy `0x0803C178` i `0x0803C270` są wewnętrznymi adresami/sub-entry/tailami w obrębie C064, odpowiednio +0x114 i +0x20C. Nie nazywamy ich osobnymi funkcjami bez RAW proof.
- C064 pozostaje class/type dispatcherem przez `DAT_0803C218[param_2]`; nie utożsamiamy go z nawigacją MenuTree.

Aktualny status MenuTree po Attack 03:
CLOSED = state child, row callback dispatcher, child offsets/attachment, formal C064 boundary.
OPEN = bezpośredni RAW constructor/XREF MenuRow, producenci callbacków, touch/navigation, runtime 0x20005F08, sześć second-stage destinations, kompletne MenuTree.


## CAN WRITE / TX ATTACK 01 — 2026-11-22

Nowy pass: `analiza/FW2213TK-2026-11-22/CAN-WRITE-ATTACK-01-2026-11-22.md`.

### Zamknięte
- `0x08057224` = FreeRTOS queue-send primitive.
- `0x200244EC` = `CanMessagesToTransmit`.
- CAN TX consumer: `CanTxTask @ 0x080654A8 -> 0x08061734 -> CAN2`.
- `0x0806E59C` = wyspecjalizowany TX adapter dla `StdId 0x0604`; buduje lokalny rekord i wysyła go do kolejki.
- dispatch table `0x08094508`: slot 5 -> `0x0806E59C`, slot 8 -> `0x080629FC`.
- `0x080629FC -> 0x08062AE4` tworzy request `0x0604/0x40`; dalszy BLX idzie przez `[obj+0x14]`.
- RX parameter WRITE: `CAN2 -> 0x080617DC -> ReceivedCanMessages -> 0x08063B80 -> 0x08062A90 -> 0x08062B22 -> 0x08011812`.
- UI local WRITE: `UI -> 0x08037212 -> 0x08011812 -> parameter RAM`.

### Nadal OPEN
- dokładne przypisanie instancji `[obj+0x14]` do vtable `0x08094508`;
- consumer lokalnego zapisu parametru, który prowadzi do CAN TX;
- pełny UI WRITE -> CAN bridge.

Nie wolno traktować `0x08011812` jako dirty-bit/TX settera bez nowego RAW proof.


## PAGE/WIDGET FACTORY + 188 RESOURCE REGISTRY — CLOSURE 01 — 2026-11-22

Nowy pass: `analiza/FW2213TK-2026-11-22/PAGE-WIDGET-FACTORY-RESOURCE-REGISTRY-CLOSURE-01-2026-11-22.md`.

CLOSED/HARD:
- `DAT_0804866C` = 188-resource registry, 16 B/record.
- type counts: 0=139, 1=31, 2=3, 3=12, 4=1, 5=2.
- TypedText base = `0x5BE64`.
- `FUN_080480C0` = central resource/presenter dispatcher; type routes 1->`0804E598`, 2/5->`0804E740`, 3->`0804E75A`, general path ->`0804E5BC`.
- `FUN_0803E714 -> FUN_08036FF2 -> FUN_0804842C -> FUN_0804E5BC -> FUN_08032316` is the proven parameter-list -> widget-value -> refresh path.
- widget records use `+0x42C + index*0x338`.
- CO1..CO4 are implemented through common instance-aware machinery; +0x12C is an active-instance selector in traced paths, +0x12B is a separate variant/context selector.

OPEN:
- field-by-field semantics of all 16-byte resource descriptors;
- exact helper internals and complete resource->widget->Bitmap/TypedText/callback mapping;
- full screen parent/child/navigation graph.


## PARAMETER ↔ CAN GRAPH ATTACK 01 — 2026-11-22

Nowy pass: `analiza/FW2213TK-2026-11-22/PARAMETER-CAN-GRAPH-ATTACK-01-2026-11-22.md`.

CLOSED:
- parameter engine anchors: `0x08010FC2`, `0x08014700/08/10/18/20`, `0x08014734`, `0x080115F6`, `0x08011812`, `0x08062B22`;
- 260-slot catalog uniqueness;
- CAN READ request construction: `0x080629FC -> 0x08062AE4 -> 0x0604/0x40 -> indirect dispatch -> TX queue`;
- CAN RX parameter WRITE: `0x0584 -> 0x08062B22 -> 0x08011812`;
- UI local WRITE: `0x08037212 -> 0x08011812`.

OPEN:
- full 260-row parameter->CAN matrix;
- local-write->CAN-TX bridge;
- exact descriptor/record ownership and multi-instance mapping;
- complete response/publication graph.

Nie utożsamiać automatycznie katalogu 260 slotów z katalogiem CAN ID.


## INSTANCE/CAPABILITY GRAPH ATTACK 01 — 2026-11-22

Nowy pass: `analiza/FW2213TK-2026-11-22/INSTANCE-CAPABILITY-GRAPH-ATTACK-01-2026-11-22.md`.

CLOSED/HARD:
- `FUN_0803C178` = row eligibility/visibility resolver; direct caller `0x0804227A` iterates 21 slots.
- selectors 1..4 are gated from internal `0x10E` / CAN `0x2105` with thresholds >=1..>=4.
- selectors 5/6/7 use separate configuration indices `0x10F/0x110/0x111`; 8/9 also have distinct configuration indices.
- access/PIN layer is separate from configuration capability.
- common page/widget path is instance-aware.

BOUNDARY:
- `+0x12A/+0x12B/+0x12C` are page/context/instance-related fields, but universal semantic labels are NOT CLOSED. Nie należy wpisywać ich jako sztywne parent/CO/menu-index bez RAW producer proof.

OPEN:
- producers of context fields;
- exact object-instantiation bridge;
- touch/navigation;
- runtime `0x20005F08` producer/content;
- complete 21-selector capability matrix.


## MENU TREE FULL CLOSURE — 2026-11-22

MenuTree control-flow is now closed as a mechanism.

Closed RAW chain:
`0x08042348 -> 21 row objects @ object+0x42C/0x274 -> access/capability -> selected row -> 0x0807EB00 -> row index -> 0x0803C064 -> [0x20005EF0+index] -> class 0..20 destination family`.

Direct RAW row-array constructor proof:
`0x0803BF80 -> array constructor 0x0805BB43 -> FUN_0804BB42`.

The MenuTree root table is 21×6 bytes and its exact selectors/text/bitmap IDs are documented in:
`analiza/FW2213TK-2026-11-22/MENUTREE-FULL-CLOSURE-2026-11-22.md`.

Important boundary:
the first-byte menu selector and runtime class byte at `0x20005EF0` are distinct layers. The implementation must preserve that separation; do not substitute one for the other.

The six additional records use selectors 0/90/97/100/98/95 and text IDs 12/14/18/16/19/20. The firmware resource/string correlation in the current MenuTree closure identifies this second-stage/access-dependent group as: selector 0 = Modulacja, 90 = Podtrzymanie, 97 = Praca, 100 = Alarm, 98 = Przepłukiwanie, 95 = Zamarzanie. These selectors are not fed directly to C064; runtime class dispatch remains a separate layer. Treat the labels as firmware resource/string correlation, not as a replacement for the runtime class table.

MenuTree status: CLOSED at the control-flow/mechanism level. No guessed semantic mapping for +0x12A/+0x12B/+0x12C was introduced.


## PARAMETER 0x2C RUNTIME TABLE CLOSURE 01 — 2026-11-22

Nowy pass: `analiza/FW2213TK-2026-11-22/PARAMETER-2C-RUNTIME-TABLE-CLOSURE-01-2026-11-22.md`.

### NEW-HARD
Bezpośredni disassembly `FUN_080115F6` dowodzi, że runtime tabela parametrów pod `0x20008D84` jest skanowana rekordami o stałym kroku `0x2C` i limicie `0x294 = 660` rekordów.

Dla `record = 0x20008D84 + index*0x2C` twardo potwierdzone są:
- +0x08 = 16-bit PID używany w porównaniu,
- +0x0C = pointer do storage wartości; dereferencja daje bieżącą wartość,
- +0x10 = 8-bit type tag,
- +0x2C = następny rekord,
- +0x58 = rekord +2*0x2C,
- +0xB0 = rekord +4*0x2C.

### WAŻNA KOREKTA MODELU
260-slot catalog NIE jest kompletną runtime tabelą rekordów parametrów.

```
260-slot catalog
        !=
660-record runtime parameter table @ 0x20008D84
```

260 pozostaje osobnym katalogiem/index layer. 660 jest twardo potwierdzonym maksimum skanowania runtime engine.

### Nadal OPEN
- pełne pola +0x00..+0x2B,
- dokładny status/commit przy +0x2C używany przez `0x08011368`,
- które z 660 rekordów są aktywne/populowane,
- mapowanie 660 rekordów ↔ 260 catalog ↔ CAN IDs,
- pełna własność descriptor/value storage i instance mapping.

### Aktualizacja P0
1. Pełny layout 0x2C — **częściowo CLOSED**: geometria + PID/value-pointer/type CLOSED; reszta OPEN.
2. Pełny model 0x20008D84 — **częściowo CLOSED**: runtime extent 660 + kluczowe pola CLOSED; pełna semantyka OPEN.
3. Resolver -> descriptor -> getter/setter — nadal OPEN.
4. Pełne MENU/UI — nadal OPEN semantycznie; control-flow mechanism CLOSED.


## PARAMETER ENGINE CROSS-LAYER CLOSURE 01 — 2026-11-22

Nowy dokument: `analiza/FW2213TK-2026-11-22/PARAMETER-ENGINE-CROSS-LAYER-CLOSURE-01-2026-11-22.md`.

Makro-korekta modelu:
- 260 = osobny catalog/index layer,
- mapper = 49 rodzin × 4 + 372 singletony = 568 pozycji logicznej przestrzeni UI/model,
- runtime engine = baza `0x20008D84`, stride `0x2C`, scan bound `660` pozycji.

**Ważne:** 660 jest potwierdzonym limitem przestrzeni skanowania runtime, NIE potwierdzoną liczbą wypełnionych rekordów.

**Korekta wcześniejszej notacji:** `record +0x2C` nie może być polem tego samego rekordu, ponieważ `0x2C` jest jego krokiem. Analogicznie `+0x30` leży 4 bajty wewnątrz następnego rekordu. Stare przypisania `+0x2C=access/flag` i `+0x30=metadata` należy traktować jako REJECTED. Pozostałe wcześniej potwierdzone pola `+0x08/+0x0C/+0x10/+0x14/+0x1C/+0x24` pozostają w mocy.

To rozdzielenie jest obecnie kluczowe dla docelowego modelu ESP: `catalog -> mapper -> external PID -> runtime record -> typed storage -> UI/CAN/persistence`.


## RECORD ENGINE CROSS-LAYER CLOSURE 02 — 2026-11-22

Nowy pass: `analiza/FW2213TK-2026-11-22/RECORD-ENGINE-CROSS-LAYER-CLOSURE-02-2026-11-22.md`.

### NEW-HARD / STRONG
- `FUN_0801143C` tworzy jeden rekord na wywołanie; nie klonuje automatycznie 4 instancji.
- `+0x08` = PID/index, `+0x0C` = pointer do local working storage, `+0x10` = type.
- `+0x14/+0x1C/+0x24` są 5-bajtowymi strukturami/deskryptorami obsługiwanymi przez `0x08014728`/getter path.
- `0x080115BC` przechodzi przez `0x294` rekordów i używa `+0x24` jako źródła wartości inicjalizacyjnej/resetowej przez `0x0801155A` -> `0x08011812`.
- Dla pokazanych rodzin CO1..CO4 osobne PID-y instancji wskazują ten sam local working storage przez `+0x0C`.
- Istnieją również wywołania `0x0801167A` z bazą tablicy przekazaną przez obiekt; dlatego `0x20008D84` jest główną potwierdzoną bazą, ale nie jedyną możliwą bazą lookup.

### REJECTED
- `record+0x2C` i `record+0x30` jako pola tego samego rekordu.
- Założenie, że 660 oznacza 660 aktywnych rekordów.
- Założenie, że każdy PID instancji ma osobny lokalny storage.
- Założenie, że wszystkie lookup-y `0x0801167A` muszą używać bezpośrednio `0x20008D84`.

### P0 update
Pełna geometria rekordu jest zamknięta; PID/storage/type są zamknięte, +0x24 ma zamkniętą rolę użycia inicjalizacyjnego/resetowego, ale pełna struktura deskryptorów +0x14/+0x1C/+0x24 oraz semantyka pozostałych bajtów nadal pozostają OPEN.


## RECORD/DESCRIPTOR HARD CLOSURE 03 — 2026-11-22

New direct closure from the complete decompilation blob (`9620d0c85259d34bb6a20d3b03b038945dfe4c1a`):
- `+0x14`, `+0x1C`, `+0x24` are exact 5-byte typed descriptors: u32 value + u8 type.
- `0x08014728` is the 5-byte copy primitive; `0x08014734` decodes descriptor values by type.
- `0x080115F6` = current value/type getter from `+0x0C/+0x10`.
- `0x0801167A` = getter for descriptor `+0x14`.
- `0x080116E6` = getter for descriptor `+0x1C`.
- `0x0801155A` = getter for descriptor `+0x24`.
- `0x080117B4` = writer/replacer for descriptor `+0x24`.
- `0x08011812` uses `+0x14/+0x1C` directly for range validation and writes current value through `+0x0C` according to `+0x10`.
- `0x0801113A` uses `+0x24` during range-repair/reset flow.

### Important correction
`+0x2C/+0x30` remain outside the 0x2C body geometrically, but they are deliberately written by `0x0801143C` and `0x08011812` reads `R+0x2C` as a state/access gate when `param_5 != 0`. Therefore the correct model is an adjacent-slot/prefix sidecar relationship, NOT a 0x30-byte record and NOT an unused offset.

New report: `analiza/FW2213TK-2026-11-22/RECORD-DESCRIPTOR-HARD-CLOSURE-03-2026-11-22.md`.


## RECORD SEMANTIC CLOSURE 04 — 2026-11-22

Generic parameter definition is now closed at the record-engine level:
- `+0x14` = minimum/lower bound descriptor.
- `+0x1C` = maximum/upper bound descriptor.
- `+0x24` = default/reset descriptor.
- descriptor type 1 = u8, 2 = u16, 3 = u32, 4 = signed i16, 5 = signed i32.
- `FUN_0801143C` therefore registers PID + storage + type + min + max + default.
- `FUN_08011812(param_6=1)` directly enforces max then min, returning status 6/7.
- `FUN_0801113A` uses +0x24 for out-of-range repair/reset.

New report: `analiza/FW2213TK-2026-11-22/RECORD-SEMANTIC-CLOSURE-04-2026-11-22.md`.

Next macro target: full 260-parameter registration tuple extraction and PID -> storage/type/min/max/default -> mapper/CAN/UI cross-link.


## 2026-11-22 — 10-pass parameter sync/publication closure
- 10-pass report: `analiza/FW2213TK-2026-11-22/10-PASS-PARAMETER-SYNC-PUBLICATION-2026-11-22.md`.
- +0x7178 remains an unresolved concrete provider interface, but its contract is hard: slot 0 GET(PID, 5-byte descriptor) -> status; slot +4 SET(PID, value, type).
- GET/SET are used at registration and periodic sync for sidecar classes 2/3.
- +0x7180 is a shared outbound publication sink used by local-change publication and periodic round-robin publication.
- Publication wire contract is hard: StdId 0x0584, DLC 8, command 0x42, PID/value type-aware encoding.
- FUN_08010fce contains the sync/publication scheduler body: provider sync -> tracked local publication -> delayed round-robin publication. Warm-up byte +0x717D, then one record per periodic step through 0..0x293.
- FUN_08011368 processes at most 11 records per invocation and only sidecar 2/3.
- FUN_0801100C + FUN_0801113A form a separate type-aware validation/default-repair path for sidecar 2/3.
- Three statically visible FUN_0801143C registrations (0x3500/0x3502/0x350B) all use sidecar class 3; this does not exclude dynamic class-2 registration.
- Remaining target: recover EstymaTask/indirect route to FUN_08010FCE and concrete implementations behind +0x7178/+0x7180.


## 100% closure — parameter response final dispatch
- `0x0800FF50` final response dispatch is closed at machine level.
- Response is constructed as `object+0x08+0x580`, command `0x80`, then `0x080100C6 BLX` executes vtable slot +0x00 of the object stored at `[0x200114C0+0]`.
- Whole-BIN literal scan found exactly one reference to `0x200114C0`: `0x08063D04`, loaded before the call to `0x0800FF50`.
- Exact initializer/constructor of `[0x200114C0+0]` remains OPEN; protocol semantic label (e.g. SDO) remains OPEN.
- Closure artifact: `analiza/FW2213TK-2026-11-22/PARAMETER-RESPONSE-DISPATCH-100-CLOSURE-2026-11-22.md`.


## AUTONOMOUS PASS 07 — 2026-11-22

New artifact: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-07-MENU-D60-RECONCILIATION-2026-11-22.md`.

### NEW-HARD — Menu selector 8/9 capability gates
- selector 8 -> internal index 0x11C -> CAN 0x350C -> visible iff nonzero.
- selector 9 -> internal index 0x122 -> CAN 0x3525 -> visible iff nonzero.
These are capability/visibility gates, not navigation targets.

### IMPORTANT SOURCE RECONCILIATION — D60
A current summary statement previously said startup/decompression confirms `[0x20008D60]=0x080A4544`. Canonical-BIN-derived OPEN1 evidence contradicts that as a direct proof: whole-BIN direct LE32 occurrence counts are 0 for both `0x20008D60` and `0x080A4544`, and startup path `0x08094644 -> 0x0808F74C -> 0x08062D82` is not a conventional .data/.bss copy into D60.

Therefore:
- candidate D60 vptr `0x080A4544`: OPEN;
- D60 slot 0 -> `FUN_0806E59C`: OPEN;
- do not promote this edge to HARD until the actual runtime write/object-construction proof is recovered.

RAW BIN remains the source of truth.


## AUTONOMOUS 10-PASS 08 — CAN OBJECT GRAPH — 2026-11-22

Report: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-10-PASS-08-CAN-OBJECT-GRAPH-2026-11-22.md`.

### Net closure
- 0x2002466C is HARD-confirmed as the poller object with vptr 0x080A4568 -> slot0 0x080629FC.
- 0x08062AE4 is HARD-confirmed as a separate READ-frame producer: StdId 0x0604, command 0x40, then BLX through [poller+0x14].
- Physical table 0x08094508 is HARD-confirmed: slot5 -> 0x0806E59C, slot8 -> 0x080629FC; constructor 0x080157A0 installs it.
- 0x0806E59C -> 0x200244EC -> 0x08057224 is HARD transport path.
- No direct 0x08062AE4 -> 0x0806E59C BL was found; object/vtable boundary is therefore real and must remain modeled.

### Progress estimate
Previous heuristic: ~55–60%. Current recommended heuristic: **~57–61%**, approximately **+1 to +2 percentage points**. This is a functional-coverage estimate, not a formal metric.

### Main OPEN
- concrete object stored at [poller+0x14];
- its vptr and slot0;
- first write/source of 0x20008D60;
- full UI local-write -> outbound CAN bridge.


## AUTONOMOUS PASS 09 — 2026-11-22 — OPEN-1 RUNTIME CLOSURE

New artifact:
analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-09-OPEN1-RUNTIME-CLOSURE-2026-11-22.md

A supplied emulator execution document now provides runtime write evidence that was unavailable during the earlier static-only passes.

### NEW-HARD — D60 runtime materialization
Runtime log:
- PC 0x0807E6CC -> [0x20008D60] <- 0x44
- bytes 44 45 0A 08 reconstruct little-endian as 0x080A4544

Therefore:
- [0x20008D60] = 0x080A4544
- vtable PROJECT = 0x08094544
- slot 0 = 0x0807E59D -> physical 0x0807E59C -> PROJECT FUN_0806E59C

The earlier static result "zero direct LE32 occurrence" is not contradictory: the value is materialized by runtime decompression/object initialization.

### NEW-HARD — concrete poller object linkage
Runtime log:
- [0x2002466C] = 0x080A4568
- [0x2002466C+0x14] = 0x20008D60
- [0x2002466C+0x18] = 0x20008D84

Thus the previously OPEN object assignment is closed:
poller -> +0x14 -> D60 object -> vtable 0x080A4544 -> slot0 FUN_0806E59C.

### NEW-HARD — node 4 runtime object
Runtime log:
- [0x200114C0] = 0x20008D60
- [0x200114C4] = 0x20008D84
- [0x200114C8] = 4

This independently confirms the earlier FUN_0800FF44 object layout.

### CLOSED combined READ/TX path
0x080629FC
-> 0x08062AE4
-> [poller+0x14] = 0x20008D60
-> D60.vtable[0] = 0x0807E59D
-> FUN_0806E59C
-> TX queue 0x200244EC
-> 0x08057224
-> CanTxTask 0x080654A8
-> 0x08061734
-> CAN2 0x40006800

### Remaining OPEN
The main remaining CAN parameter boundary is:
UI/local write
-> FUN_08011812
-> local-change/publication mechanism
-> +0x7180 sink
-> StdId 0x0584 / command 0x42

Still unresolved:
- concrete +0x7180 target,
- EstymaTask -> FUN_08010FCE route,
- complete 260-slot parameter/CAN matrix,
- remaining UI/CAN object graphs.

### Evidence discipline
This upgrade is based on the supplied emulator result document. Independent reproduction still requires executing the canonical BIN in the emulator; the source document itself records the run and its expected/observed write log.


## AUTONOMOUS PASS 10 — EstymaTask / scheduler boundary (2026-11-22)

- EstymaTask entry is now HARD: `DAT_08062EB0 -> 0x08062C95` (Thumb), physical entry `0x08062C94`.
- `FUN_08062D82` creates EstymaTask through `FUN_08057630` with task name `EstymaTask` and priority 3.
- Recovered EstymaTask direct-call set does **not** include `0x080629FC`, `0x0806E59C`, or `0x08010FCE`.
- Therefore the remaining route to `FUN_08010FCE` is indirect/timer/framework based; no target is guessed.
- `0x08062920` region is rejected as the missing parameter-TX builder.
- Detailed evidence: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-10-ESTYMA-TASK-SPINE-2026-11-22.md`.

## AUTONOMOUS PASS 11 — parameter manager caller closure

- Whole decompilation blob contains one recovered direct caller of FUN_0801143C: FUN_08001AE4.
- FUN_08001AE4 statically registers 0x3500, 0x3502 and 0x350B, all with sidecar/class 3.
- This does not exclude dynamic/indirect registration; it proves only the complete direct-call set in the recovered export.
- +0x7178 provider GET is exercised at registration and periodic synchronization; SET is used on provider/local mismatch.
- Added static RE scanner: tools/re_scan.py, with self-test tools/test_re_scan.py.
- Detailed pass: analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-11-PARAMETER-MANAGER-CLOSURE-2026-11-22.md
## AUTONOMOUS PASS 12 — range/default engine

- FUN_0801100C is CLOSED as a local MIN/MAX validator, not a hidden provider/cache comparison.
- Upper bound = record +0x1C; lower bound = record +0x14; current value comes from the local record.
- On violation FUN_0801100C returns the offending PID; otherwise it returns 0xFFFFFFFF.
- FUN_0801113A is the default-repair loop: offending PID -> FUN_0801155A default (+0x24) -> FUN_08011812 commit.
- No direct caller of FUN_0801113A exists in the recovered C export; trigger remains indirect/runtime OPEN.
- Sidecar 2/3 are hard-confirmed in provider synchronization and range validation; sidecar 1 is excluded from both loops.
## AUTONOMOUS PASS 13 — startup registration chain

- HARD chain: FUN_08062D82 -> FUN_08000E34 -> FUN_08001AE4 -> FUN_0801143C x3.
- FUN_08062D82 invokes FUN_08000E34 before creating GUITask, EstymaTask, CanRxTask and CanTxTask.
- Therefore the three visible static parameter registrations are established during startup, before task execution.
- The missing runtime bridge remains the parameter-manager object/framework behind +0x7178/+0x7180; no direct C edge from EstymaTask to FUN_08010FCE was found.

## AUTONOMOUS PASS 17 — parameter-manager object / scheduler closure — 2026-11-22

Report: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-17-PARAMETER-MANAGER-SCHEDULER-CLOSURE-2026-11-22.md`.

### NEW-HARD — concrete parameter-manager ownership

RAW constructor `PROJECT 0x0800DDC0` receives:
- r0 = this,
- r1 = provider,
- r2 = publication sink,

calls scheduler base constructor `0x08014824`, installs vtable `0x080A44F0), then stores:
- `[this+0x7178] = r1`
- `[this+0x7180] = r2`.

Startup call at `0x0800024A` supplies:
- `this = 0x20008D84`
- provider = `0x20008D64`
- publication sink = `0x20008D60`.

Therefore:
- parameter manager = `0x20008D84`
- `+0x7178` concrete provider = `0x20008D64`
- `+0x7180` concrete publication sink = `0x20008D60`
- manager vtable = `0x080A44F0`.

### NEW-HARD — provider concrete object

`0x20008D64` is constructed by `0x0800DB08` and receives vptr `0x080A31F0`.
Its complete slot mapping remains a separate target; no unverified slot is promoted.

### NEW-HARD — scheduler route

Because `0x0800DDC0` invokes scheduler base constructor `0x08014824` for `this=0x20008D84`, the parameter manager is registered through `0x0801478C` into scheduler manager `0x200246E8`.
Scheduler loop `0x080147C8` invokes registered objects through virtual slot 0.
Vtable `0x080A44F0` slot 0 is `FUN_08010FCE`.

Architectural route:
`0x080001AC -> 0x0800DDC0(0x20008D84,0x20008D64,0x20008D60) -> 0x08014824 -> 0x0801478C -> 0x080147C8 -> vtable[0] -> FUN_08010FCE`.

### Correction of stale OPEN statements

Earlier PASS 10/13 text saying the concrete `+0x7178/+0x7180` objects and scheduler route were fully unresolved is superseded by PASS 17.
The remaining work is now remaining provider slots/persistence semantics, independent runtime tick trace, and the 260-slot cross-layer matrix.



## NEWESTYMA SELF-CONTAINED HANDOFF — 2026-11-22

A dedicated continuation package now exists at `NewEstyma/`.

**First file for every new agent:** `NewEstyma/00_AGENT_START_HERE.md`

Then read:
- `NewEstyma/01_PROJECT_STATE.md`
- `NewEstyma/02_WORKFLOW.md`
- `NewEstyma/03_TOOLING.md`
- `NewEstyma/04_FIRMWARE_MANIFEST.md`
- latest pass reports

The package intentionally does not duplicate every historical report: `analiza/` remains the evidence archive and this master remains the canonical consolidated state. NewEstyma is the navigation/handoff layer.

Canonical BIN integrity remains SHA-256 `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`, size `0x1F0000`.




## PASS 18 CORRECTION — superseded by PASS 19

The PASS 18 address-base correction is superseded. The observation that RAW 0xA31F0 is erased is correct, but 0x080A31F0 is a RUNTIME pointer, not a PROJECT address.

Correct translation:
- provider vtable runtime 0x080A31F0
- provider vtable PROJECT 0x080931F0
- provider vtable RAW 0x931F0

Report: analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-18-PROVIDER-VTABLE-GET-CLOSURE-2026-11-22.md


## AUTONOMOUS PASS 19 — PROVIDER GET/SET + ADDRESS-BASE CLOSURE — 2026-11-22

Report: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-19-PROVIDER-GET-SET-ADDRESS-BASE-CLOSURE-2026-11-22.md`.

### NEW-HARD
The runtime address base is 0x08010000. Provider vptr 0x080A31F0 therefore maps to PROJECT 0x080931F0 / RAW 0x931F0. The canonical BIN at RAW 0x931F0 contains real provider interface pointers.

Provider slot 0 = runtime 0x0801DB31 / PROJECT 0x0800DB31: GET path. FUN_0801143C calls it with PID and output context.

Provider slot 1 = runtime 0x0801DB79 / PROJECT 0x0800DB79: SET path. FUN_08011368 calls it with PID and current value when provider/local values differ.

Therefore provider GET/SET are HARD. The earlier PASS 18 claim that the slots were absent from the BIN was caused by applying the runtime address as a raw offset and is REJECTED.

### Current provider boundary
- slots 0/1: HARD
- remaining slots: OPEN
- persistence semantics: OPEN
- full PID/catalog mapping: OPEN


## AUTONOMOUS PASS 20 — LOCAL WRITE -> PUBLICATION -> CAN TX BRIDGE — 2026-11-22

Report: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-20-LOCAL-WRITE-PUBLICATION-CAN-BRIDGE-2026-11-22.md`.

### NEW-HARD
`FUN_08011812` writes validated values into runtime record local storage. `FUN_0801117C` scans records, detects local/shadow differences, constructs StdId 0x0584 / DLC 8 / command 0x42 publication frames, and calls `[this+0x7180]` through vtable slot 0. The sink is 0x20008D60, vtable runtime 0x080A4544 / PROJECT 0x08094544, slot0 -> runtime 0x0807E59D / PROJECT FUN_0806E59C. FUN_0806E59C queues the frame through 0x200244EC -> 0x08057224 -> CanTxTask -> CAN2.

Machine-level bridge CLOSED:
`local write -> record storage -> change detection -> 0x0584/0x42 publication -> 0x20008D60 -> FUN_0806E59C -> TX queue -> CAN2`.

Remaining OPEN is semantic/timing detail: exact invocation cadence of FUN_0801117C, shadow table semantics, and full PID/catalog/CAN matrix.


## AUTONOMOUS PASS 21 — MENU RAW MATRIX / RUNTIME ANCHOR AUDIT — 2026-11-22

Canonical BIN was re-read directly and a deterministic scanner was added:
- `tools/menu_matrix_scan.py`
- `tools/test_menu_matrix_scan.py`
- report: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-21-MENU-RAW-MATRIX-RUNTIME-ANCHOR-AUDIT-2026-11-22.md`

HARD:
- MenuTree table = RAW 0x42348 / PROJECT 0x08042348, 21 records × 6 B.
- Runtime class table address 0x20005EF0 has exactly one direct LE32 literal occurrence: RAW 0x3C218.
- Access/update table address 0x20005F08 has exactly one direct LE32 literal occurrence: RAW 0x42314.
- Row constructor Thumb pointer 0x0805BB43 occurs once: RAW 0x3C030.
- Main row-selection resolver Thumb pointer 0x0808EB01 occurs once: RAW 0x63AB8.
- Sibling resolver Thumb pointer 0x0808EB37 occurs once: RAW 0x63AC0.
- The root-table selector and runtime class byte remain distinct layers; navigation cannot be implemented as selector->page.

OPEN:
- runtime producers/contents of 0x20005EF0 and 0x20005F08;
- exact runtime class -> screen/page family mapping;
- exact row vtable/touch callback producers;
- complete screen/widget/visibility/access/PID/CAN matrix.

PASS 21 does not invalidate the existing 21-slot / 15+6 access-dependent construction closure; it provides direct physical-BIN anchor verification for that model.


## AUTONOMOUS PASS 22 — IAR .DATA / MENU RUNTIME TABLE CLOSURE — 2026-11-22

Added deterministic `tools/iar_data_extract.py` and regression test. Physical canonical BIN was decompressed using the already proven IAR LZ77 algorithm.

HARD:
- `.data` source RAW 0x96114..0x9694D, decompressed size 0x118B3 to SRAM 0x20000000.
- `0x20005EF0[0..20] = 00 0A 01 02 03 04 05 06 07 08 09 0B 0D 11 0F 0C 0E 12 10 13 14`.
- `0x20005F08[0..20]` is byte-identical.
- Both tables initially equal the first-byte selectors of the 21-entry root MenuTree table at RAW 0x42348.
- Configuration-driven visibility mapping is consistent with the recovered C064/C178 logic: 1..4 -> 0x10E/0x2105; 5 -> 0x10F/0x2106; 6 -> 0x110/0x2108; 7 -> 0x111/0x2107; 8 -> 0x11C; 9 -> 0x122.

MODEL CORRECTION:
The selector and runtime class are separate physical layers, but their initial values are identical. Do not claim their values are inherently different. Do not collapse the layers either, because the firmware reads them through different addresses/paths.

OPEN:
- later writes/mutations to both runtime tables;
- exact navigation semantics for rows 15..20;
- complete widget/resource/callback graph.


## AUTONOMOUS PASS 23 — POINTER FLOW / MENU RUNTIME TABLE MUTATION AUDIT — 2026-11-22

Report: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-23-POINTER-FLOW-MENU-RUNTIME-MUTATION-AUDIT-2026-11-22.md`

Added:
- `tools/pointer_flow_scan.py`
- `tools/test_pointer_flow_scan.py`

NEW-HARD:
- SRAM table `0x20005EF0` is materialized twice from literal pool RAW `0x3C218`: LDR literals at RAW `0x3C068` -> r0 and `0x3C17A` -> r2.
- Function candidate PROJECT `0x0803C064` performs an indexed byte read through `0x20005EF0`.
- Function candidate PROJECT `0x0803C178` performs an indexed byte read and a concrete byte store at `0x20005EF0 + 6`.
- SRAM table `0x20005F08` is materialized by LDR literal RAW `0x422CE` -> r5; function candidate PROJECT `0x080522C8` performs a byte read at RAW `0x422DE`.

The scanner uses two-stage pointer provenance:
`LDR literal -> literal-pool word -> SRAM address -> same-function memory access`.
This closes a layer that direct LE32/XREF scanning could not expose.

Still OPEN:
- semantic meaning of the +6 write;
- complete mutation graph for all 21 entries of both tables;
- MOVW/MOVT/address-arithmetic aliases;
- full runtime-class/access-table -> page/widget/PID/CAN mapping.


## AUTONOMOUS PASS 24 — THUMB-2 BOUNDARY / POINTER-FLOW CORRECTION — 2026-11-22

Report: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-24-THUMB2-POINTER-FLOW-CORRECTION-2026-11-22.md`

### CRITICAL CORRECTION

PASS 23's alleged STRB at RAW 0x3C1FE into `0x20005EF0+6` is REJECTED.

RAW 0x3C1FC..0x3C1FF is one Thumb-2 `MOV.W r1,#0x122`; RAW 0x3C1FE is the second halfword. No direct static write to `0x20005EF0+6` is currently proven.

### NEW-HARD

- `0x20005EF0`: two direct literal materializations at RAW 0x3C068 -> r0 and RAW 0x3C17A -> r2.
- Consumers are real indexed byte reads at RAW 0x3C06A and 0x3C17C.
- `0x20005F08`: direct literal materialization RAW 0x422CE -> r5.
- PROJECT `0x080422C8` sequentially reads all 21 bytes of `0x20005F08`.
- The 21-entry loop advances its row/object base by `0x274` per entry.
- access-table value `0x0E` triggers `0x08032F08 -> 0x0803C270 -> 0x08037212`.
- `0x08032F08) reads object +0x2C.
- `0x0803C270) requires object +0x10 == 1 and forwards the value with PID `0x0117).
- Runtime-class values 0..20 feed a TBB dispatch mechanism.

### TOOLING CORRECTION

`tools/pointer_flow_scan.py` is now Thumb-2 width aware and no longer decodes second halfwords as independent Thumb-1 instructions. It also recognizes common Thumb-2 memory forms, MOVW/MOVT candidates, and PUSH.W function starts.

### OPEN

- arithmetic/alias/indirect writers of both runtime tables;
- identity of r4/r8 in PROJECT 0x080422C8;
- 0x274-stride object -> 21-row MenuTree mapping;
- semantics of access-table 0x0E and PID 0x0117;
- complete runtime-class handler -> page/widget/resource graph;
- complete PID/UI/CAN matrix.



## AUTONOMOUS PASS 25 — MENU ACCESS TABLE → ROW OBJECT → PID 0x0117 CLOSURE — 2026-11-22

Report: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-25-MENU-ACCESS-ROW-PID117-CLOSURE-2026-11-22.md`

### NEW-HARD

- PROJECT 0x080422C8 is vtable slot 4 of runtime vtable 0x0808F66C.
- Constructor PROJECT 0x08074508 installs vptr 0x0808F66C.
- The same constructor initializes 21 repeated objects at object+0x42C, stride 0x274, count 0x15.
- 0x080422C8 uses object+0x524+i*0x274 = row[i]+0xF8.
- access-table byte 0x0E triggers a read of row[i]+0x124.
- row[i]+0x124 reaches 0x0803C270.
- 0x0803C270 requires state-object +0x10 == 1 and forwards the value with logical key 0x0117.
- 0x08037212 uses manager 0x20008D84 and resolves that logical key before calling 0x08011812.

### CLOSED STRUCTURAL CHAIN

`0x20005F08[i]`
-> `row[i] (+0x42C + i*0x274)`
-> `row[i]+0x124`
-> state gate
-> logical key `0x0117`
-> `0x08037212`
-> parameter manager `0x20008D84`
-> `0x08011812`

### OPEN

- final PID/value/type for logical key 0x0117;
- identity of object+0x3C and +0x10 state gate;
- producer/initializer of row[i]+0x124;
- exact 21-row MenuTree selector mapping;
- runtime class 0..20 -> page/widget graph;
- remaining arithmetic/alias writers of the two SRAM tables.



## AUTONOMOUS PASS 26 — PID 0x0117 RESOLVER NEGATIVE CLOSURE — 2026-11-22

Report: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-26-PID0117-RESOLVER-NEGATIVE-CLOSURE-2026-11-22.md`

### NEW-HARD

- 0x08037212 receives key 0x0117 from the 0x0E access-table path.
- Neither of its static resolver tables contains key 0x0117.
- Therefore the canonical static path does not call 0x08011812 for this input.
- The second resolver table contains key 0x2123 -> value 0x0117 at RAW 0x3797A. [SUPERSEDED/REJECTED przez PASS 35 §6: poprawny rekord (0x0117 -> 0x3506) @RAW 0x3797C]

### CORRECTION OF PASS 25

The 0x0E path reaches the resolver 0x08037212, but it does not statically resolve to the parameter-manager write engine.

Correct:
`0x0E -> row[i]+0x124 -> state gate -> 0x0803C270 -> key 0x0117 -> 0x08037212 -> no static match -> no 0x08011812`.

### OPEN

- semantic identity of 0x0117;
- runtime producer of row[i]+0x124;
- key 0x2123 -> value 0x0117 relation to catalog;
- runtime class -> page/widget graph;
- remaining SRAM table writers/aliases.



## AUTONOMOUS PASS 27 — ROW +0xF8 DESCRIPTOR / VALUE 0x15 CLOSURE — 2026-11-22

Report: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-27-ROW-F8-DESCRIPTOR-VALUE15-CLOSURE-2026-11-22.md`

### NEW-HARD

- Row constructors at PROJECT 0x08089570 and 0x08089594 store 0x0807C540 at row+0xF8.
- PROJECT 0x08032F08 reads byte +0x2C from that pointer.
- Canonical static value at 0x0807C540+0x2C is 0x15.
- Therefore constructor-established 0x08032F08 result is 0x15.

### REVISED 0x0E PATH

`0x20005F08[i]==0x0E -> row[i]+0xF8 -> 0x0807C540 -> +0x2C = 0x15 -> 0x0803C270 -> key 0x0117 -> 0x08037212 -> no static resolver match`.

No 0x08011812 call is proven on this path.

### OPEN

- mutation of row+0xF8;
- identity/role of 0x0807C540;
- reason for key 0x0117;
- catalog correlation;
- runtime-class/page/widget graph;
- remaining SRAM-table writers.



## AUTONOMOUS PASS 28 — RUNTIME CLASS 0..20 FIRST-LEVEL UI DISPATCH — 2026-11-22

Report: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-28-RUNTIME-CLASS-FIRST-LEVEL-UI-DISPATCH-2026-11-22.md`

### NEW-HARD

- The 21 runtime classes 0..20 from 0x20005EF0 have a complete TBB first-level dispatch at RAW 0x3C076.
- Classes 1..4 share 0x08038130 and write object+0x12B/object+0x12C.
- Classes 5..13 mostly use distinct first-level handlers.
- Class 14 returns immediately.
- Classes 12,15,19,20 are structurally distinct paths.
- Runtime class and internal selector state are separate layers.

### OPEN

- 0x08037F88 common UI construction tail;
- concrete page/widget constructors;
- special class paths;
- resource/text/bitmap/PID/CAN links;
- SRAM-table writers/aliases.



## AUTONOMOUS PASS 29 — RUNTIME CLASS → CALLBACK/DESCRIPTOR LAYER — 2026-11-22

Report: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-29-RUNTIME-CLASS-CALLBACK-DESCRIPTOR-LAYER-2026-11-22.md`

### NEW-HARD

- Complete 21-entry runtime-class TBB graph at RAW 0x3C076.
- Generic runtime classes converge on PROJECT 0x08037F88.
- 0x08037F88 constructs/copies the object at parent+0x110.
- Temporary object vtable = 0x0809F848.
- Callback/config pointer pool = RAW 0x386A8..0x387D8.
- Classes 1..4 share 0x08038130 with r1=1..4.
- Class 14 returns immediately.
- Class 12 is an inline special parameter-manager path.
- Class 15 bypasses generic construction via 0x08042318 -> 0x0802EADE.
- Classes 16/17 share 0x08038488 after selector writes 0x10/0x11.
- Class 18 has a distinct +0x110 builder.
- Callback 0x08048037 directly writes object+0x12A=1.

### OPEN

- vtable 0x0809F848 semantics;
- callback -> widget/resource/text/PID graph;
- class 12 key-3 operation;
- class 15 navigation/object graph;
- remaining runtime-table writers/aliases;
- complete UI/PID/CAN graph;
- provider/persistence/260-row matrix.



## AUTONOMOUS PASS 30 — UI CALLBACK OBJECT VTABLE 0x0809F848 — 2026-11-22

Report: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-30-UI-CALLBACK-OBJECT-VTABLE-2026-11-22.md`

### NEW-HARD

- 0x08039494 installs vtable 0x0809F848 at the object created/copied into parent+0x110.
- Vtable RAW = 0x8F848; non-zero slots are 2,3,8,9,14,15.
- Object layout is +0x00 vptr, +0x04 context, +0x08 callback/table pointer, +0x0C signed/index field.
- Slots 2/8 implement indirect callback dispatch.
- Slots 3/9 implement the corresponding boolean/state-check family.
- The +0x110 object is therefore an executable polymorphic runtime object.

### OPEN

- vtable slot semantics;
- callback -> widget/resource/text/PID graph;
- slots 14/15;
- constructor 0x08039394 static pair;
- class 12/15 paths;
- runtime-table writers;
- complete UI/PID/CAN matrix.



## AUTONOMOUS PASS 31 — VTABLE SLOT 2 → STATIC CALLBACK BRIDGE — 2026-11-22

Report: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-31-VTABLE-SLOT2-CALLBACK-BRIDGE-2026-11-22.md`

### NEW-HARD

- Generic descriptor records have second word 0, so generic object+0x110 +0x0C = 0.
- Vtable slot 2 therefore directly invokes the selected callback at object+0x110+0x08 with object+0x110+0x04 as argument.
- Class 0 selects callback 0x08048037, which writes parent-object +0x12A = 1.
- Vtable 0x0809F848 has three repeated method pairs: slots 2/3, 8/9, 14/15.

### OPEN

- slot-2 call sites;
- callback effects;
- full slot semantics;
- class 12/15;
- table writers;
- UI/PID/CAN matrix.



## AUTONOMOUS PASS 32 — CLASS 12 PARAMETER-3 CYCLIC OPERATION — 2026-11-22

NEW HARD:
- Runtime class 12 at RAW 0x3C12A is a concrete parameter action, not an unresolved UI-only branch.
- 0x080373BA uses concrete manager 0x20008D84 and logical key 3, reads a type-5 value, increments it and commits it through 0x08011812.
- The class-12 caller increments the returned value and 0x080373E6 commits logical key 3, type 5, modulo 8, returning the final value.
- Combined: class12 -> GET key3 -> +1 SET -> caller +1 -> modulo8 SET -> return 0..7.

Interpretation boundary: the 0..7 cyclic-selector interpretation remains STRONG until the key-3 UI/PID semantic is recovered.


## AUTONOMOUS PASS 33 — RUNTIME KEY 3 PROVENANCE — 2026-11-22

NEW HARD:
- 0x080115F6 is a runtime-record lookup over the 660-position parameter table, not the catalog PID resolver.
- Class-12 key 3 is a concrete runtime lookup key.
- Startup code at RAW 0x1D62 initializes key 3 through 0x0801143C with storage 0x20021FAA and type code 1.
- Therefore class 12 is operating on a real manager-owned runtime parameter record.

Correction to terminology: "logical key 3" is now replaced by "runtime parameter lookup key 3" unless a direct PID mapping is proven.


## AUTONOMOUS PASS 34 — RUNTIME KEY 3 STORAGE / TYPE CLOSURE — 2026-11-22

Report: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-34-RUNTIME-KEY3-STORAGE-TYPE-CLOSURE-2026-11-22.md`.

### NEW-HARD
- Runtime key 3 is initialized at RAW `0x1D62` with manager `0x20008D84`, storage `0x20021FAA = 0x200208EC+0x16BE`, and runtime type 1.
- `FUN_08011812` ultimately stores according to the runtime record type; type 1 uses byte storage (`STRB`).
- Therefore key 3 is physically byte-backed.
- Class 12's type-5 temporary/input is normalized by the runtime setter to the record's type; there is no type contradiction.
- Key 4 uses `0x20021FBA = 0x200208EC+0x16CE`, type 2. Nearby runtime keys share the same configuration/storage region.

### NEGATIVE / BOUNDARY
- No direct LE32 literal for `0x20021FAA) exists in the canonical BIN; startup forms it arithmetically.
- No direct semantic consumer of `+0x16BE` beyond the startup registration was found.

### OPEN
- exact semantic name of key 3 storage;
- key3 -> catalog PID bridge;
- other UI/resource consumers;
- runtime-key startup matrix;
- provider/persistence/CAN semantics for key 3.

Terminology remains: **runtime parameter lookup key 3**, not catalog PID 3.

## PASS 35 — RUNTIME PARAMETER TABLE Z EMULACJI STARTUPU (2026-11-22)

Raport: `analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-35-RUNTIME-PARAM-TABLE-EMULATION-2026-11-22.md`; dane: `analiza/FW2213TK-2026-11-22/data/`.

HARD:
- 655 rekordów tabeli runtime (manager 0x20008D84, stride 0x2C) odczytane z RAM po emulacji startupu; układ rekordu i dekodowanie pól wartości wg własnego kodu typu — patrz raport §1.
- Klucz runtime = PID; 448/448 PID katalogu panelu w tabeli, nazwy zgodne. Key 3 = PID 0x0003 "Language" (u8 0..30, storage 0x20021FAA = 0x200208EC+0x16BE).
- 0x200208EC = blok ustawień (603 storage'ów); +0x16C3..+0x16C6 = 0x2105..0x2108; 15 statystyk w BKPSRAM 0x40024000.
- Rezolwer 0x08036FF2: tabela 1 (RAW 0x37B48, 49 rekordów CH, PID = baza + instancja - 1) i tabela 2 (RAW 0x37578, 372 rekordy, PID wprost).
- (0x0117 -> 0x3506 "Sound alarm activation") @RAW 0x3797C.

STRONG: class 12 = przełączanie języka (8 języków, modulo 8).

KOREKTA: PASS 26 (negative closure klucza 0x0117) jest ODRZUCONY (przesunięty odczyt tabeli o 2 B). Sekcja 15A MenuTree o ścieżce 0x0E pozostaje, ale rezolucja dochodzi do PID 0x3506.
REJECTED także: "logical key 3" jako nieznany klucz — to PID 0x0003.

OPEN: producent [ctx+0x12C]; dynamiczne zakresy (21 par min/max); 10 kluczy tabeli 2 poza runtime; semantyka klasy sidecar +0x24; model kolejnych zadań FreeRTOS w emulatorze.
Narzędzia: tools/emu_startup.py, runtime_param_table.py, resolver_tables.py, bl_xref.py, disasm_thumb.py (+ testy).


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
STRONG: wiersz menu 15 (klasa 12, budowany przy access != 0) uruchamia zmianę języka. UWAGA: klasy wierszy 15..20 są równe polu +2 rekordu menu (nie selektorowi z pola +0); wyprowadzenie nie wykazane.
OPEN: 3 pozostałe wywołania setLanguage i przywracanie języka przy starcie; znaczenie pola +2 rekordu dla wierszy 0..14; dotyk -> class 12.


## AUTONOMOUS PASS 40 — WIERSZE MENU ZBUDOWANE W FIRMWARE — 2026-11-22
Raport: analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-40-MENU-ROWS-BUILT-IN-FIRMWARE-2026-11-22.md ; dane: data/menu_rows_21.csv ; narzędzie: tools/menu_rows_probe.py
HARD (wykonane w firmware): access 0 -> row-builder dla wierszy 0..14, access 3 -> 0..20; vptr ekranu 0x0808F66C, wiersze +0xF8=0x0807C540 (zgodnie z PASS 27). Pełny konstruktor ekranu RUNTIME 0x0804BF7C (z konstruktorem bazowym).
KOREKTA: argumenty FUN_0804BC6C(row,A,B) to ID BITMAP (A: 60..81, B: 82..101,159), nie ID tekstów; wcześniejszy odczyt "Sterownik/Palnik/..." z pola +2 był błędny.
STRONG: wiersze 15..20 czytają (A,B)=(u16@+4,u16@+6) i klasę u16@+2; "selektory" 90/97/100/98/95 to pola sąsiednich rekordów = bitmapy B, więc teza "selector 90 -> Language" z MENUTREE jest niepewna.
OPEN: źródło etykiet i ekranów docelowych; pętla drugiego etapu 15..20 z kodu; emulacja kończy się wywołaniem przez NULL po zbudowaniu wierszy.


## AUTONOMOUS PASS 41 — NAWIGACJA MENU: DOTYK WIERSZA -> KLASA -> EFEKT — 2026-11-22
Raport: analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-41-MENU-CLICK-DISPATCH-EXECUTED-2026-11-22.md ; dane: data/menu_click_effects_21.csv ; narzędzie: tools/menu_click_probe.py
HARD (kod): handler przycisku FUN_0807EB00(this, sender): sender == this[+0x3B4] + i*0x274 -> FUN_0803C064(this[+0x3C], i) -> klasa 0x20005EF0[i]. Wiersz nie ma własnego callbacka (+0x26C = 0).
HARD (wykonanie): wiersz 15 (klasa 12) = zmiana języka (key3 i currentLanguage 0->1); wiersze 2..5 (klasy 1..4) ustawiają +0x12B i +0x12C = 1..4 (wybór CO1..CO4) — producent instancji [ctx+0x12C] dla rodziny CH to menu główne.
OPEN: klasy 11/13/14/15/18/19; samo przełączenie ekranu po +0x12A/+0x12B; drugi handler FUN_0807EB36 -> 0804EC18; etykiety i ekrany docelowe.


## AUTONOMOUS PASS 42 — EMULACJA SYSTEMOWA (FreeRTOS + LTDC + DMA2D) I RENDER EKRANU GŁÓWNEGO — 2026-11-22
Raport: analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-42-FULL-SYSTEM-EMULATION-HOME-SCREEN-RENDER-2026-11-22.md ; obraz: data/screen_home_emulated.png ; narzędzia: tools/cortexm_rtos.py, stm32_dma2d.py, render_screen.py (+ test_render_screen.py)
HARD: zadania firmware EstymaTask, GUITask, CanRxTask, CanTxTask, IDLE uruchomione; LTDC IRQ 88 (vsync -> signalVSync), DMA2D IRQ 90 (semafor bufora ramki); LTDC: RGB565 480x272, bufor 0xC0000000/0xC003FC00 (podwojne buforowanie).
HARD (wynik): ekran glowny wyrenderowany przez firmware (1352 operacje DMA2D) — godzina, dzien, "0.0", "Wylaczony", obraz kotla, 7 kafelkow; stan domyslny (brak CAN/RTC/dotyku).
Poprawki modelu wyjatkow: SysTick po svc; PendSV po instrukcji zapisu ICSR; STKALIGN (bit 9 xPSR); tick ~100k instrukcji; FPU lazy stacking niemodelowany.
OPEN: wstrzykniecie CAN (IRQ64) i dotyku; eksport wszystkich ekranow; ekran -> widzet -> zasob -> PID jako obrazy.


## AUTONOMOUS PASS 43 — RUCH CAN PANELU PO STARCIE (PUSTA MAGISTRALA), TABLICA WEZLOW, BRAMKA POLLERA — 2026-11-23
Raport: analiza/FW2213TK-2026-11-22/AUTONOMOUS-PASS-43-CAN-BOOT-TRAFFIC-NODE-TABLE-2026-11-23.md ; dane: data/can_tx_boot_no_partners.csv ; narzędzia: tools/stm32_can.py, can_boot_trace.py (+test)
HARD (wykonanie): panel nadaje dopiero po ~3.3 s (scheduler obiektow okresowych 0x080247C8, licznik 30); przy pustej magistrali: heartbeat 0x704=05 co 1 s; SDO do wezlow 5,6,7: zapis 0x3004:01=0 i odczyt 0x2001:01 co 1 s; publikacje 0x584; serie ramek PDO-podobnych 0x240..0x247, 0x250, 0x254/5, 0x26F..0x271, 0x278..0x27F, 0x340..0x347, 0x378..0x37F, 0x440..0x447, 0x540..0x547, 0x201.
HARD (kod): tablica obecnosci wezlow (handler 0x0800F894: heartbeat 0x701..0x77F i SDO 0x581..0x5FF, waznosc 300) i skan tozsamosci 0x600+k: 40 18 10 02 (obiekt 0x1018 sub 2 wg CiA 301) -> protokol to CANopen SDO.
HARD (eksperyment): heartbeaty i odpowiedzi tozsamosci nie wlaczaja pollera 0x604; STRONG: bramka obj+0x10 jest ustawiana przez kod klas menu (0x0804C24E, 0x0804C260), nie przez wykrycie magistrali.
OPEN: ktore klasy ustawiaja obj+0x10/+8; kto wola skan 0x1018:02; semantyka ramek 0x2xx..0x5xx po podaniu danych; odpowiedzi wezlow 5..7.
