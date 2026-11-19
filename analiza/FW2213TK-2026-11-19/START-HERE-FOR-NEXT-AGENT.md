> **NOWY GŁÓWNY HANDOFF:** przeczytaj również `analiza/FW2213TK-2026-11-19/HANDOFF-NOWY-CHAT-2026-11-19.md`. Zawiera pełny kontekst, zamknięte korekty i aktualny punkt wznowienia 6-slot menu. Następnie przeczytaj MASTER i wszystkie batch-notes.

# TeklaPelletCAN — START HERE — NOWY CHAT / AGENT
Data: 2026-11-19
Branch: ccr-be8a1bcb-5t76j0

## JEDEN PLIK, KTÓRY MASZ PRZECZYTAĆ NA START

**MASTER:**
`analiza/FW2213TK-2026-11-19/MASTER-STATE-CONSOLIDATED-2026-11-19.md`

To jest aktualny, skonsolidowany handoff. Nie zaczynaj od starszych notatek i nie pytaj użytkownika o kontekst, który jest w masterze.

---

# CEL

Reverse-engineering oryginalnego **FW2213TK.bin** panela IGNEO Touch.

Cel końcowy:
**odtworzenie panelu 1:1 funkcjonalnie i wizualnie, a następnie implementacja zachowania na ESP.**

Nie chodzi o mockup. Chodzi o:
- TouchGFX widget tree,
- parent/child,
- Bitmap/BitmapData,
- TypedText/font,
- X/Y/W/H,
- visibility,
- touch/callback,
- parameter engine,
- CAN/CANopen,
- konfigurację,
- CO1..CO4,
- startup,
- alarmy,
- service/test,
- storage,
- warianty sprzętowe.

---

# NAJWAŻNIEJSZE RZECZY JUŻ ZAMKNIĘTE — NIE ODKRYWAĆ OD NOWA

### Adresowanie
`runtime = 0x08000000 + raw_offset`.
Nie dodawać +0x10000 do funkcji.

### Panel
480×272, RGB565.

### TouchGFX
Prawdziwy ślad producenta:
`C:\Estyma\igneoTOUCH\app\nasze\igneoTFT\gui\src\components\WheelSelectorExtra.cpp`

Framework: Application, MVPApplication, Container, Bitmap, Slider, TypedText, RadioButtonGroup itd.

### Instancje CO
- +0x12B = typ/klasyfikacja,
- +0x12C = instancja 1..4.
Nie mylić.

### Mapper
`FUN_08036FF2()` realizuje fizycznie:
`panel index -> family-of-4 -> +0x12C -> resolved index`.

### Record engine
- `FUN_0801143C`
- `FUN_080115F6`
- `FUN_0801167A`
- `FUN_080116E6`
- stride 0x2C.

+0x12C uczestniczy zarówno w odczycie, jak i zapisie.

### Heating builder
`FUN_0803E714` -> 12 parametrów + opcjonalne 11 -> mapper -> widget/value refresh.

### Home/Main
`FUN_0803E5AC` = silny kandydat root.
`+0x92DC -> FUN_08047290` = dokładnie 6 powtarzalnych obiektów.

### Dynamic Home
- 0x4005 -> 63.8 modulation,
- 0x215F -> outside temperature,
- 0x2002/2003/2004 -> boiler mode/setpoint,
- 0x3601/3603 -> fuel remaining/reserve.

### Hardware/profile
- 0x3500,
- 0x3502,
- 0x350B,
plus +0x16C1/+0x16D5.

### Boiler identity / image
- 0x2125 = Device type,
- 0x3665 = igneTouch boiler short name,
- 0x3664 = soft. version,
- 0x370A = Boiler image selector, snapshot value 3.

### Real assets
011.png, 012.png, 013.png, 014.png są prawdziwymi assetami firmware.
Wcześniejszy wygenerowany kocioł **nie był assetem FW**.

### WheelSelector correction
`FUN_08038CF4` kończy się przed stringami:
- 0x08038D74 assert,
- 0x08038D9C WheelSelectorExtra.cpp path.

`FUN_08038ED0` **nie jest potwierdzonym konstruktorem**. Vptr proof brak.

---

# AKTUALNY ATAK — NIE SZEROKO, TYLKO PIONOWO

## 1. 370A -> Bitmap
Szukaj:
```
0x20021FA6 / 0x370A
 -> read/use
 -> switch/lookup
 -> resource/Bitmap ID
 -> BitmapData/Bitmap
 -> widget
 -> X/Y/W/H
```

Nie zakładaj:
`1->011, 2->012, 3->013`.

## 2. WheelSelectorExtra
Szukaj:
```
FUN_08038CF4
 -> this/vptr
 -> vtable
 -> 38DF0..390FC
 -> extraText / TypedText / resource
```

## 3. Home 6 widgets
```
FUN_0803E5AC
 -> +0x92DC
 -> FUN_08047290
 -> 6 objects
 -> vtable
 -> Bitmap/TypedText
 -> geometry
 -> callback
```

## 4. Heating widget builder
Rozwiń:
- FUN_080480C0
- FUN_0804842C
- FUN_0804E5BC
- FUN_08032316

## 5. Surowe tabele
Odzyskaj:
- DAT_08037B48 / DAT_08037B4C,
- DAT_0803C218,
- DAT_0803EEC0 (+0x62, +0x6E).

## 6. Identity/variant
Znajdź usages:
- 0x2125,
- 0x3665,
- 0x3664,
- 0x3500/3502/350B.

SERIAL zostaw na później — brak runtime call-chainu.

---

# ZAKAZY / KOREKTY

Nie wracaj do:
- 0x38130,
- 0x3212C,
- 0x32146,
- starego 0x42146 jako setterów instancji.

Nie twierdź:
- +0x12B = numer CO,
- +0x158 = numer CO,
- 0x2105 na pewno tworzy N obiektów CO,
- 370A 1/2/3 = zakres parametru; MAPOWANIE do bitmap 011..014 nadal NIEUDOWODNIONE,
- FUN_08038ED0 = konstruktor WheelSelectorExtra,
- SERIAL = runtime selector modelu.

---

# ZASADY RAPORTOWANIA

Użytkownik chce **duże, skonsolidowane wyniki**, nie mikro-raporty.

Każdy większy wynik:
1. kilka powiązanych dowodów,
2. pełny łańcuch,
3. korekty starych hipotez,
4. [FW] / [DATA] / [STRONG] / [HYPOTHESIS],
5. zapis na GitHub,
6. następny konkretny punkt ataku.

Nie zatrzymuj się po jednym adresie.

Nie generuj renderu przy każdym kroku. Render dopiero wtedy, gdy można użyć **rzeczywistych assetów + rzeczywistej geometrii**.

## Najbliższy sukces, którego szukamy

**Pierwszy pełny dowodowy widget:**
```
oryginalny source trace
 -> firmware class/vtable
 -> widget
 -> Bitmap/TypedText
 -> X/Y/W/H
 -> visibility
 -> panel index
 -> instance
 -> CAN/storage
```


# AKTUALIZACJA HANDOFF — PO MULTIPASS 2026-11-19

**Ostatni skonsolidowany commit:** 5e12b87454fca34c1540684e8716a197a7e052c0
**Najważniejszy dokument:** MASTER-STATE-CONSOLIDATED-2026-11-19.md

## CO ZMIENIŁ TEN PRZEBIEG
1. Potwierdzono, że pole callback/code parametrów nie musi wskazywać początku funkcji. Sąsiednie callbacki 3709/370C/370D wskazują także wnętrza większych funkcji.
2. 0x0801AB7E pozostaje nierozpoznanym wejściem, a nie nazwą funkcji do znalezienia.
3. 469E8 → FUN_080318B4 jest rejestracją widgetu w timer/update registry, nie bezpośrednim bindingiem 370A.
4. FUN_080317AE → vtable +0x50 jest właściwym runtime update boundary dla 469E8.

## INSTRUKCJA DLA AGENTA
Nie pytaj użytkownika o kontekst. Nie zaczynaj od zera.
Przeczytaj najpierw cały MASTER, szczególnie §§37–44. Następnie prowadź analizę wieloprzebiegowo:
3709..370D callback comparison → 0x0801AB7E → DAT_08046CC4+0x50 → 469E8 update → variable Bitmap ID → 370A → 011/012/013/014
Przy każdym odkryciu wykonuj dalej trace. Nie kończ przebiegu na pojedynczym adresie. Jeżeli znajdziesz mniejszy trop, analizuj go i wracaj do głównego łańcucha.

### PRIORYTET A — CALLBACK ENGINE
- porównaj 0x0801425C, 0x08015CCC, 0x0801659E, 0x08016614 z 0x0801AB7E;
- ustal wspólny sposób użycia pola callback przez parameter engine;
- dla każdego dostępnego callbacku określ poprzedni/następny blok i efekty;
- nie zakładaj, że callback = osobna funkcja.

### PRIORYTET B — 469E8 VTABLE
Odzyskaj DAT_08046CC4 + 0x50.
Następnie prześledź całą metodę: model read → condition → child +0x4F → resource/Bitmap/visibility.

### PRIORYTET C — 370A MAPPING
Dopiero po A/B szukaj: 0x20021FA6 → state → resource ID → 011/012/013/014.
Nie zakładaj 1→011, 2→012, 3→013.

### JEŚLI BRAKUJE RAW BIN
Nie udawaj, że bajty można odzyskać z decompiled.c. Wtedy:
- wykorzystaj istniejący decompiled.c, functions.txt i batch notes;
- kontynuuj tor DAT_08046CC4/vtable/update;
- wskaż dokładnie, jaki raw region jest potrzebny;
- nie zatrzymuj całej analizy.

## ZASADA KONSOLIDACJI
Po dużym przebiegu:
1. utwórz/uzupełnij batch note,
2. zaktualizuj MASTER,
3. zaktualizuj ten START-HERE, jeśli zmienił się punkt startowy,
4. commit,
5. podaj następnemu agentowi commit SHA i link do dokumentu.

Nigdy nie zostawiaj wiedzy tylko w odpowiedzi czatu.

## AKTUALNY PUNKT STARTOWY — PASS 2026-11-19 / CALLBACK ENGINE + 469E8

Nowy batch:
`analiza/FW2213TK-2026-11-19/BATCH-CALLBACK-ENGINE-317AE-469E8-VTABLE-2026-11-19.md`

Najpierw czytaj MASTER §45.

### Zamknięte w tym przebiegu

`FUN_080317AE`:
- registry count +0x64,
- pointers +0x04 + index*4,
- active bytes +0x68 + index,
- aktywne obiekty dostają wywołanie vtable +0x50,
- cleanup następuje dopiero po update loop.

`FUN_080318B4` = register/retain.  
`FUN_0803193A` = release/unregister.

`FUN_080469E8`:
- final vptr DAT_08046CC4,
- Bitmap child +0x4F,
- fixed constructor Bitmap ID 14,
- rejestruje parent 469E8 do timer registry.

### Nowa korekta callbacków

Nie nazywaj pól 3709..370D "callback functions".

- 3709 → 0x0801425C = FUN_0801417C +0xE0
- 370A → 0x0801AB7E = brak named function
- 370B → 0x08015CCC = brak named function
- 370C → 0x0801659E = FUN_080164F4 +0xAA
- 370D → 0x08016614 = FUN_080164F4 +0x120

Używaj nazwy: **handler/code boundary**.

### Natychmiastowy następny trace

1. `DAT_08046CC4 + 0x50`
2. concrete method
3. wszystkie model/state reads tej metody
4. child +0x4F / Bitmap/resource
5. równolegle raw `0x0801AB7E`
6. dispatcher consuming parameter-table code field
7. dopiero potem merge z `0x20021FA6` i mapowaniem Bitmap.

Ważny wzorzec porównawczy:
`FUN_08030762` już pokazuje dynamiczny Bitmap update:
unregister → variable resource ID → FUN_080307BC → Bitmap vtable +0x14.

Nie zakładaj jeszcze, że 469E8 korzysta z tego samego helpera.

Jeżeli raw BIN nadal nie jest dostępny:
**nie wymyślaj bajtów**. Kontynuuj tor vtable/update i oznacz raw boundary jako OPEN.



# RAW BIN AVAILABLE — START HERE AFTER COMMIT add3f95d1dd71284d49105c483f4a0f11667752b

A raw firmware copy is now available and verified:
`FW2213TK_kopia.bin`
SHA-256:
`1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`

IMPORTANT CORRECTIONS:
1. `0x0801AB7E` is raw data/resource in the BIN, NOT normal Thumb code.
2. `DAT_08046CC4` resolves to `0x08079F00), which is UTF-16 text, NOT a vtable.
3. Do NOT continue using the old graph `DAT_08046CC4 -> vtable +0x50` as a fact.
4. `FUN_080317AE +0x50` itself IS real and must be retained as the generic runtime indirect-dispatch boundary.
5. NEW strongest concrete path:
   `FUN_0803E45C -> model[0x158] + model[0x11C] -> FUN_08047040 -> four repeated 469E8-instance state bytes`.
6. The bridge `370A/RAM 0x20021FA6 -> model[0x158]` is now the key unresolved link.

Next pass:
- resolve why a registered 469E8 object can have a text pointer at +0 while 317AE expects a dispatch table there;
- identify model indices 0x158 and 0x11C;
- trace their upstream reads and find whether 0x20021FA6 reaches 0x158;
- trace +0x25 state bytes into visibility/update behavior;
- only then recover resource ID selection and 011/012/013/014 mapping.

Full details are in:
`MASTER-STATE-CONSOLIDATED-2026-11-19.md` §47
and
`BATCH-RAW-BIN-RECOVERY-469E8-47040-370A-CORRECTION-2026-11-19.md`.

Do not restart the investigation from the old vtable hypothesis.


# NEW RAW CORRECTION — START FROM §48 / COMMIT 9bbf8484531e8ff9ea50d58e1815e0a38bc24359

Do NOT use the old `0x158 -> 370A` hypothesis.

Raw mapping table proves:
- internal `0x121 -> external 0x370A`
- internal `0x158 -> external 0x351A` (Cascade slaves number)
- internal `0x11C -> external 0x350C` (Cascade master flag)

Thus:
`0x158/0x11C -> FUN_08047040` is cascade UI, not Boiler image selector.

Raw `FUN_080469E8` also corrected:
- Bitmap/resource child is `parent +0x13C`
- constructor writes resource ID 14 there
- old `+0x4F` attribution is withdrawn
- DAT_08046CC4 is not proven vtable; raw value points into UTF-16 text/resource area.

370A:
`0x370A -> internal 0x121 -> generic parameter engine -> storage 0x20021FA6 + data handler/table 0x0801AB7E`.

The next target is the **generic parameter path for internal index 0x121**. Find the structure/lookup that takes internal index 0x121 and resolves the 370A storage and handler/data descriptor.

Do not reconnect 370A to the cascade/469E8 branch without a hard call/data edge.


# FINAL HANDOFF UPDATE — RAW MULTIPASS 0x121 -> 0x370A -> BITMAP — 2026-11-19

Latest commits:
- batch: ab05fda54dbb6a87fb12ae15536139af086821f5
- MASTER: 4afb8524463c648f760e858335b364067fa620d9

Read MASTER §49 and batch:
BATCH-RAW-MULTIPASS-121-370A-UI-BITMAP-2026-11-19.md

## CLOSED — DO NOT REPEAT

The Boiler image selector chain is now hard-proven:

0x370A
 -> internal index 0x121
 -> FUN_08036FF2
 -> mapping table @ 0x08037984
 -> FUN_08037094
 -> FUN_080115F6
 -> record +0x0C
 -> storage 0x20021FA6
 -> u8 value 1..3
 -> FUN_0803CB04
 -> FUN_0803CACC
 -> value + 10
 -> FUN_080307BC
 -> Bitmap object +0x85C
 -> resource IDs 11,12,13

Therefore:
1 -> 11
2 -> 12
3 -> 13

This is now executable-code proof. Do NOT call this mapping a hypothesis anymore.

## IMPORTANT CORRECTION

0x0801AB7E is raw pixel/table data and is NOT the runtime 370A callback.

Do not continue trying to route:
370A -> 0x0801AB7E -> UI.

The actual runtime route is through FUN_0801143C / FUN_080115F6 and the storage pointer:
0x200208EC + 0x16BA = 0x20021FA6.

## ALSO KEEP SEPARATE

0x158 -> 0x351A = Cascade slaves number
0x11C -> 0x350C = Cascade master

Those feed:
FUN_0803E45C -> FUN_08047040 -> four 469E8 composites -> fixed Bitmap resource 14.

Do not reconnect this cascade branch to 370A without a new hard edge.

## NEXT ATTACK

Do not spend time proving 370A -> 11/12/13 again.

Go directly to:
1. FUN_0803CB04 class/vtable and constructor;
2. parent object containing Bitmap child +0x85C;
3. direct BitmapData/resource-table proof for resource IDs 11,12,13 and match to 011/012/013;
4. X/Y/W/H and visibility of +0x85C;
5. role of fixed resource 14;
6. separate provenance of 0x0801AB7E.

User expects several passes before a report. Find -> analyze -> continue -> return to main chain -> consolidate. Do not stop on a small finding.


# SECOND RAW PASS HANDOFF — 370A TARGET BITMAP +0x85C CLOSED — 2026-11-19

Latest commits:
- batch: 7322fe63e46d6bf9497c01cdefeee6c7864b502e
- MASTER: 64bd9f7ddb3995dc84ad3c300ef60fca0df07914

## NEW CLOSED FACT

FUN_0803C33E constructs a repeated visual composite with four real Bitmap children:
- +0x85C
- +0x888
- +0x8B4
- +0x8E0

All four are created through FUN_0802DF08, the concrete Bitmap constructor pattern.

The 370A update path specifically targets +0x85C:

0x370A
 -> internal 0x121
 -> FUN_08036FF2
 -> 0x20021FA6
 -> FUN_0803CB04
 -> FUN_0803CACC
 -> +10
 -> FUN_080307BC
 -> Bitmap +0x85C
 -> resource 11..13

FUN_0803C33E is instantiated by:
- FUN_08039A48
- FUN_08039B30
- FUN_08039C18

So there are three sibling composites using this visual structure.

## DO NOT REPEAT

The following are CLOSED:
- 0x121 -> 0x370A
- 370A -> 0x20021FA6
- 370A value 1/2/3 -> resource IDs 11/12/13
- target +0x85C is a real Bitmap object
- 469E8 resource 14 is a separate path

0x0801AB7E is raw data/resource and is NOT the 370A runtime callback.

## NEXT MULTIPASS TARGET

1. Identify exact class/vtable/source trace of FUN_0803C33E / FUN_0803CB04.
2. Recover X/Y/W/H of parent +0x85C and siblings +0x888/+0x8B4/+0x8E0.
3. Resolve resource IDs 11/12/13 to the actual extracted BitmapData entries.
4. Determine which of the three repeated composites is the Home/main boiler graphic.
5. Keep resource 14/469E8 separate.

User wants several passes before reporting. Continue finding -> analyzing -> tracing -> returning to the main chain, then consolidate.

# THIRD RAW PASS HANDOFF — 2026-11-19

Latest commits:
- batch: d136cffe0399462988097dad9f27e01c5b4ab836
- MASTER: b580e27a0157f83e34bbf38ed2d783311bbbf186

## NEW FACTS

FUN_0803C33E explicitly constructs six Bitmap children:
+0x330, +0x35C, +0x85C, +0x888, +0x8B4, +0x8E0.
All start with resource 0xFFFF through FUN_0802DF08.

370A still targets exactly +0x85C through FUN_0803CACC.

FUN_080307BC is the true Bitmap resource replacement routine:
resource -> Bitmap +0x26 -> derive width -> slot +0x38 -> derive height -> slot +0x3C -> recompute clipping/visibility.

## CLOSED
- 0x121 -> 0x370A
- 0x370A -> 0x20021FA6
- 370A value 1/2/3 -> resource 11/12/13
- target +0x85C is a real Bitmap object
- resource 14 is a separate higher-level path

## IMPORTANT CAUTION
Exact C++ vtable/class identity is NOT closed. Object +0 literals can point into data/text regions. Name the concrete routines, but do not invent vtable identities.

## NEXT MULTIPASS ATTACK
1. Trace +0x85C parent back to Home/Main root.
2. Recover actual geometry/placement around +0x84C/+0x85C.
3. Resolve which of 08039A48 / 08039B30 / 08039C18 is the main boiler screen.
4. Trace visibility/state callbacks around 0803CB04.
5. Then map resources 11/12/13 to concrete screen variant semantics.

Continue several passes before reporting. Find -> analyze -> continue -> consolidate. Do not stop on small findings.

# HANDOFF UPDATE — AFTER 370A UPDATE/GEOMETRY PASS

Latest consolidated commit: `d4d0902f294b0f8e1a07c4b1cd88015fae7d6525`
Batch: `BATCH-370A-UPDATE-GEOMETRY-2026-11-19.md`

## New corrections / facts

- `FUN_0803CB04` = constructor/wiring of the visual update object.
- `FUN_0803CB2C` = actual update/refresh method; it reads internal index `0x121` and calls `FUN_0803CACC`.
- `FUN_0804272C(object,X,Y)` is behaviorally an X/Y setter via object slots +0x2C/+0x30.
- `FUN_0803C5B4` explicitly targets Bitmap +0x85C with X=40, Y=70 and attaches it through parent+0x04.
- The dispatch mechanism into `FUN_0803C5B4` is still OPEN; do not promote it to a proven direct caller.

## DO NOT REPEAT

Closed 370A chain:
`0x370A -> 0x121 -> FUN_08036FF2 -> runtime record -> 0x20021FA6 -> u8 1..3 -> FUN_0803CB2C -> FUN_0803CACC -> +0x85C -> resource 11/12/13`.

## NEXT ATTACK

1. Find the indirect dispatch / method-table mechanism that reaches `FUN_0803C5B4`.
2. Enumerate every geometry/visibility mutation of +0x85C, +0x888, +0x8B4, +0x8E0.
3. Resolve W/H and visibility of +0x85C after resources 11/12/13 are installed.
4. Trace 08039A48 / 08039B30 / 08039C18 upstream into the Home/Main root.
5. Recover runtime BitmapData records for IDs 11/12/13 from the resource registry around 0x2002454C.
6. Keep resource 14 and 0x0801AB7E separate until a hard bridge appears.

Continue multi-pass: find -> analyze -> continue -> return to main chain -> consolidate. Do not stop on a small finding.


# HANDOFF AFTER FOURTH RAW PASS — 2026-11-19

Latest batch commit: `2551d0b130ba5b051d3bb6ab103d9878ffb5f344`
Latest MASTER commit: `972e39e85170e8c821cf60eaa96a2b6410d41dd4`

## New closed/strong facts

- Full raw BL scan finds exactly three direct C33E callers: 08039AD6, 08039BBE, 08039CA6, belonging to 08039A48/08039B30/08039C18.
- Those three sibling constructors instantiate the same C33E visual composite and wire CB04 updater objects.
- C33E has six Bitmap children (+330,+35C,+85C,+888,+8B4,+8E0) plus several helper/UI objects.
- +0x84C is a helper/container immediately before +0x85C, initialized by FUN_080424C4 with parent + two literal parameters.
- C5B4 uses +0x85C at X=40,Y=70 and attaches it through parent+0x04.
- C5B4 later uses +0x8E0 with fixed resource 0x7A, X=398, Y from runtime state.
- C5B4 dispatch itself is still OPEN: no direct BL or raw function-pointer occurrence was found.

## Next attack

Do not repeat the selector chain or the X/Y=40/70 proof.

1. Search indirect dispatch/vtable tables for C5B4.
2. Decode +0x84C helper/container.
3. Enumerate W/H/visibility writes to +0x85C across all methods.
4. Recover runtime resource records 11/12/13.
5. Compare 08039A48/39B30/39C18 beyond common C33E to identify Home/Main.
6. Keep resource 14 and 0x0801AB7E separate.

Continue multi-pass before reporting.


# CURRENT START OVERRIDE — 2026-11-19

**Read this section last. It is the active continuation point and overrides older START-HERE instructions.**
Persistent memory:
`analiza/FW2213TK-2026-11-19/BATCH-PERSISTENT-CONTINUATION-MEMORY-2026-11-19.md`
Latest MASTER after this checkpoint will be the parent document.

## DO NOT RESTART
The following are CLOSED and must not be rediscovered:
- 370A -> internal 0x121 -> storage 0x20021FA6 -> value 1..3 -> Bitmap +0x85C -> resources 11/12/13.
- 1->11, 2->12, 3->13.
- +0x85C is a real Bitmap.
- +0x85C X=40,Y=70 in C5B4.
- C33E has six Bitmap children: +330,+35C,+85C,+888,+8B4,+8E0.
- C33E has exactly three direct callers: 39A48,39B30,39C18.
- +0x84C is NOT proven as the parent/container; treat as separate OPEN helper.
- 0x0801AB7E is raw data/resource, not 370A callback.
- 0x158/0x11C cascade and resource 14 are separate.

## NEXT MULTIPASS
A. indirect dispatch -> FUN_0803C5B4
B. FUN_080424C4 -> exact semantics of +0x84C
C. all geometry/visibility/resource mutations of +0x85C/+0x888/+0x8B4/+0x8E0
D. resource registry -> BitmapData for 11/12/13 -> extracted 011/012/013
E. compare 39A48/39B30/39C18 to identify actual screen
F. only then render.

For every useful finding, continue tracing before reporting. Persist the next substantial checkpoint to GitHub. Do not ask the user to repeat context.


# CURRENT START OVERRIDE — PASS 5 HIDDEN METHOD CLUSTER

Latest batch:
`analiza/FW2213TK-2026-11-19/BATCH-METHOD-CLUSTER-C5B4-CACC-CB2C-2026-11-19.md`

New key finding:
`FUN_0803C550` size=100 ends exactly at `0x0803C5B4`, while C5B4 is not a functions.txt entry despite raw evidence of real code. CACC/CB04/CB2C are also absent from functions.txt. C33E sits in a similar gap between recognized functions. Treat this as a hidden/unrecognized UI method cluster.

NEXT:
1. recover boundaries of C33E/C5B4/CACC/CB04/CB2C;
2. search method-table/function-pointer storage;
3. test indirect C5B4 dispatch;
4. decode 424C4/+0x84C;
5. enumerate full Bitmap cluster mutations;
6. then differentiate 39A48/39B30/39C18.

Do not re-prove 370A -> 11/12/13.


# CURRENT START OVERRIDE — PASS 5 HIDDEN METHOD CLUSTER

Latest batch: `analiza/FW2213TK-2026-11-19/BATCH-METHOD-CLUSTER-C5B4-CACC-CB2C-2026-11-19.md`

[STRONG] C5B4, CACC, CB04, CB2C and C33E are manually recovered procedures inside gaps not represented as normal functions in functions.txt. Treat this as a hidden UI-method cluster.

NEXT: recover boundaries -> method-table/function-pointer storage -> indirect C5B4 dispatch -> 424C4/+0x84C -> full Bitmap mutations -> three sibling differentiation.

Do not re-prove 370A -> 11/12/13.


# CURRENT OVERRIDE — PASS 5B

New [FW]/[STRONG] finding: FUN_080424C4 is also absent from functions.txt and lies inside the gap between FUN_0804204A (ends 0x08042116) and FUN_0804272C. Therefore C33E/C5B4/424C4/CACC/CB04/CB2C form a recurring hidden UI-method recovery problem.

NEXT: map known recovered methods to function-list gaps -> recover nearby method-table/function-pointer storage -> test C5B4/C33E/424C4/CB04/CB2C membership -> then decode +0x84C and Bitmap cluster.


# CURRENT OVERRIDE — PASS 5M — 0x7A / +0x8E0 GEOMETRY CORRECTION

New [DATA]/[FW]/[STRONG] checkpoint:

- `FUN_0803C5B4` sets `+0x8E0` to resource `0x7A`.
- `0x7A = 122` decimal.
- Extracted firmware bitmap `122.png` is `35x37`.
- Therefore `+0x8E0` at X=398 has right edge X=433, **not 480**.
- The earlier `398+82=480` edge-alignment hypothesis is withdrawn.

[STRONG] `+0x8E0` is a small right-side UI element with runtime Y; exact semantic/icon identity remains OPEN.

## NEXT — DO NOT RESTART

1. Enumerate every `+0x8E0` resource/X/Y/visibility/clipping mutation.
2. Enumerate `+0x888` and `+0x8B4` mutations.
3. Decode `FUN_080424C4` / `+0x84C`.
4. Recover indirect method-table/function-pointer dispatch to `FUN_0803C5B4`.
5. Compare `39A48/39B30/39C18`.
6. Recover runtime BitmapData records for 11/12/13.

The closed 370A -> internal 0x121 -> storage 0x20021FA6 -> value 1..3 -> +0x85C -> resources 11/12/13 chain must NOT be re-proved.

Continue multi-pass before reporting. Persist the next substantial checkpoint.


# CURRENT OVERRIDE — PASS BITMAP DIRECT-BIN — 2026-11-19

**Do not redo bitmap extraction.** Complete direct raw-BIN bitmap map is committed in:
`analiza/FW2213TK-2026-11-19/BITMAP-MAP-DIRECT-BIN-2026-11-19.md`

Hard facts:
- firmware size 0x1F0000;
- correct load base = 0x08010000;
- bitmap descriptor table file 0x54450 / runtime 0x08064450;
- descriptor stride 0x14;
- 188 real firmware bitmap records, IDs 000..187;
- descriptor = data ptr, extraData ptr, W,H, solidRect x/y/w/h;
- RGB565 payload = W*H*2;
- non-zero extraData = A8 payload W*H;
- 76b is generated/historical and NOT a firmware resource.

**Critical correction:** runtime pointer -> file offset uses `ptr - 0x08010000`, NOT `ptr - 0x08000000`. The latter produces the previously observed garbage images.

Directly verified semantic anchors:
- 056/057 = graph point pair;
- 151/152 = 47290 state pair;
- 160/161 = real lower configuration/settings button pair;
- 011/012/013/014 = boiler-related original graphics;
- 102/103, 117/118, 168/169, 184/185 = known UI state pairs.

Use the direct-BIN map and its dimension groups as the canonical bitmap inventory. Do not rediscover the table, base address, descriptor layout, or 188-record count.

Next analysis remains the UI/resource call-site problem: map bitmap IDs to constructors/widgets/parents/geometry, especially 160/161 bottom bar and 151/152 vertical 47290 list, then continue Home/Main variant tracing.
