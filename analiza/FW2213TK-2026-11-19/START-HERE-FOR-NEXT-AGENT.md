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
