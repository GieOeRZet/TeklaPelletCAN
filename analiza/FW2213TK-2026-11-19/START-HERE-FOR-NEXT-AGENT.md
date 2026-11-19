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
- 370A 1/2/3 = bitmapy 011/012/013,
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

