# NewEstyma — MENU TREE ATTACK 03 — 2026-11-22

Firmware: FW2213TK_kopia.bin
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071
Branch: ccr-be8a1bcb-5t76j0

## Cel

Ponowna weryfikacja MenuTree na pełnym blobie decompiled.c (SHA 9620d0c85259d34bb6a20d3b03b038945dfe4c1a), ze szczególnym naciskiem na class-family 0x0804BB42/BC6C/BD7C, child state 0x08032D7C..F08 oraz rzeczywiste granice C064/C178/C270.

## 1. HARD — FUN_0804BB42 rzeczywiście odzyskuje konkretny class layout

Pełny blob:

- vptr = DAT_0804BC60;
- +0x60 = FUN_0802DF08;
- +0x8C = FUN_0802FC10;
- +0xC4 = FUN_0802FC10;
- +0xF8 = FUN_08032D7C;
- +0x24? / +0x2C area = FUN_08031BD4 child;
- +0x26C = 0;
- +0x270 = 0;
- dodatkowe callback/helper objects przy +0x24C/+0x25C.

Konstruktor zwraca ten sam obiekt i ustawia geometrię/attachment bazowej klasy.

Status: FACT.

## 2. HARD — FUN_0804BC6C nie jest dowodem unikalnego MenuRow

Pełny blob pokazuje:

- FUN_0804BC6C(row,param_2,param_3) operuje na +0x8C, +0x60, +0xF8;
- dołącza trzy dzieci przez parent vtable +0x64;
- ale ta sama funkcja jest również wywoływana z FUN_0804E4F8 z inną sygnaturą/argumentacją.

Wniosek:

FUN_0804BC6C należy traktować jako metodę/helper klasy-family, a nie jako definitywnie unikalny konstruktor Main Menu Row.

Zatem wcześniejsze zdanie "FUN_08042160 -> FUN_0804BC6C = konkretny MenuRow class" zostaje obniżone do:

RAW MenuTree konstruktor używa FUN_0804BC6C jako row-builder/helper, ale identyfikacja pełnej klasy wymaga bezpośredniego RAW XREF/constructor path.

Status:
- helper/class-family relation: HARD;
- unique MenuRow identity: STRONG, nie HARD.

## 3. HARD — state child 0x08032D7C jest stanowym obiektem, nie zwykłym bajtem

FUN_08032D7C inicjalizuje własny obiekt:

- vptr = DAT_08032E7C;
- state byte at child+0x2C;
- child+0x30 jest obiektem wartości/interpolacji;
- child+0x150 jest callback/action pointer;
- FUN_08032E80 zapisuje child+0x2C i skaluje wartość do 0..100;
- FUN_08032EB8 wylicza stan z child+0x60, zapisuje child+0x2C i jeżeli callback +0x150 jest aktywny, wywołuje jego vtable +0x08;
- FUN_08032F08 tylko zwraca child+0x2C.

Dla obiektu z FUN_0804BB42 child ten znajduje się pod row+0xF8.

Zatem:

row + 0xF8
 -> state child
 -> +0x2C = state byte
 -> +0x150 = callback/action object
 -> FUN_08032E80 / FUN_08032EB8 / FUN_08032F08

Status: HARD.

Ważne: +0x2C nie jest dowiedzionym selector ID.

## 4. HARD — FUN_0804BD7C jest osobnym callback/action dispatcherem row-class family

FUN_0804BD7C:

1. czyta pointer row+0x26C;
2. wywołuje callback vtable +0x0C;
3. jeśli aktywny, wywołuje callback vtable +0x08 z row.

Konstruktor FUN_0804BB42 zeruje +0x26C.

To daje dwa różne poziomy callbacków:

A) state-child:
row+0xF8 + 0x150 -> callback przy zmianie stanu;

B) row-class:
row+0x26C -> callback/action dispatcher FUN_0804BD7C.

Nie wolno ich scalać bez RAW producer proof.

Status: HARD.

## 5. HARD — korekta nazewnictwa FUN_0803C178

functions.txt zawiera tylko:

0803c064 FUN_0803c064 558

Nie istnieje osobny entry FUN_0803C178.

Adres 0x0803C178 = 0x0803C064 + 0x114.

Analogicznie:
0x0803C270 = 0x0803C064 + 0x20C.

Oba adresy leżą wewnątrz jednego zakresu funkcji C064.

Dlatego:

- "FUN_0803C178" = historyczna nazwa robocza dla RAW sub-entry/tailu;
- "FUN_0803C270" = historyczna nazwa robocza dla RAW sub-entry/tailu;
- formalny Ghidra/function boundary: FUN_0803C064.

Nie wolno nazywać C178/C270 osobnymi funkcjami bez bezpośredniego RAW proof.

Status: FACT / boundary correction.

## 6. HARD — C064 jest dispatcherem class/type

Pełny body C064:

class = byte[DAT_0803C218 + param_2]

switch po klasie 0..20.

Klasy 1..4 ustawiają:
- object +0x12B = 1..4;
- object +0x12C = 1..4;

inne klasy kierują do innych rodzin konstrukcji/descriptorów.

C064 jest więc class/type dispatcherem. Nie należy utożsamiać go z selector navigation.

## 7. STRONG — co zmienia się w modelu MenuTree

Aktualny model ma rozdzielone warstwy:

raw MenuTree table
 -> row slot construction
 -> row class-family helper
 -> capability/access processing
 -> state child / row callback
 -> navigation (nadal OPEN)

C064/C178/C270 należy traktować jako osobną warstwę class/instance/descriptor dispatch, dopóki RAW argument flow nie pokaże bezpośredniego połączenia z touch/navigation.

## 8. Najważniejsza nowa obserwacja dla dalszego trace

W FUN_08032EB8 callback state-child jest wywoływany po zmianie stanu:

child+0x2C = threshold result
callback = child+0x150
callback vtable +0x08(child)

To jest bardziej obiecujący punkt niż samo FUN_08032F08 do znalezienia źródła zmiany visual/state row.

Równoległy row callback:

row+0x26C
 -> FUN_0804BD7C
 -> callback vtable +0x08(row)

Następny trace powinien rozwiązać producentów tych dwóch callback pointers.

## 9. OPEN — nadal wymagany RAW

Nie ma w aktualnym repo canonical BIN ani kompletnego raw Thumb window dla:

- 0x08042100..0x08042320;
- 0x20005EF0..0x20005F5B;
- literal row vtable DAT_0804BC60;
- producer row+0x26C;
- producer state-child+0x150.

Bez tego nie zamykamy:
- touch -> callback;
- selector -> navigation;
- six second-stage destination screens;
- exact 0x0E side effect;
- full MenuTree.

## 10. Status

CLOSED:
- state-child semantics;
- row-class callback dispatcher;
- C064 formal boundary;
- C178/C270 boundary correction;
- BC6C class-family/helper status;
- child offsets and attachment.

OPEN:
- raw MenuTree call path into actual class constructor;
- callback producers;
- touch/navigation;
- runtime 0x20005F08;
- second-stage destination mapping;
- complete MenuTree.

## 11. Source discipline

The decompiled blob was fetched directly by Git blob SHA 9620d0c85259d34bb6a20d3b03b038945dfe4c1a.

The canonical BIN is still the primary source. This pass does not invent missing bytes from decompiled.c.

