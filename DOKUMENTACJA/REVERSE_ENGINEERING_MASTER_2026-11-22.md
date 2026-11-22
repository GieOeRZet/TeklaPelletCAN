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
RE_PACK = PROJECT + 0x10000
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
