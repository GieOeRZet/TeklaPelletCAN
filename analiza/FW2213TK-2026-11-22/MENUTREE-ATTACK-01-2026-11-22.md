# NewEstyma — MENU TREE ATTACK 01
Date: 2026-11-22
Firmware: FW2213TK_kopia.bin
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071
Branch: ccr-be8a1bcb-5t76j0

## 0. Cel

Rozpoczynam autonomiczny wątek MenuTree niezależnie od Pass 18 przekazanego Gemini.

Cel nie jest jeszcze implementacją menu. Celem jest odtworzenie relacji:

MENU ROOT
 -> row slot
 -> selector/context
 -> visibility/capability
 -> access
 -> screen/page
 -> child/widget
 -> TypedText/Bitmap
 -> touch/navigation
 -> parameter/CAN action

Zasada: FACT / STRONG / INFERENCE / OPEN. Nie zamykam semantyki bez data-flow/call-path proof.

## 1. Stan wejściowy po dotychczasowych passach

Twardo ustalone:
- tabela @ RAW 0x42348 ma 21 rekordów po 6 B;
- konstruktor FUN_08042160 buduje rekordy 0..14 zawsze;
- gdy access != 0, drugi etap buduje rekordy 15..20;
- row objects zaczynają się od object+0x380 i mają stride 0x274;
- późniejszy pass wykonuje 21 iteracji i używa FUN_0803C178(model,slot);
- osobny 21-iteracyjny pass korzysta z runtime array 0x20005F08;
- access level jest w context/model +0x158;
- selector 90 jest powiązany z Language;
- pierwsza grupa selectorów ma mocne mapowanie:
  0 Kocioł, 10 Palnik, 1..4 CO1..CO4, 5 CWU, 6 Solar, 7 Buffer, 8 Cascade, 9 dodatkowy magazyn paliwa, 11 Historia alarmów, 13 Informacje o programie, 17 Konfiguracja, 15 Poziom menu/PIN.

## 2. Kluczowa korekta, której nie wolno zgubić

Nie modelować tabeli jako:
- 15 zwykłych pozycji + 6 niezwiązanych rekordów,
ani jako:
- 21 zawsze widocznych pozycji.

Aktualny model firmware:
- MenuRow[21] jako rodzina slotów;
- konstrukcja 15 bazowych;
- konstrukcja 6 dodatkowych zależna od access != 0;
- następnie capability/access processing dla całej rodziny 21 slotów.

Semantyka sześciu rekordów access-dependent nadal OPEN:
0:(12,73)
90:(14,75)
97:(18,78)
100:(16,79)
98:(19,80)
95:(20,81)

## 3. Nowy kierunek MenuTree

### A — zamknąć row-object class

Punkt wejścia:
FUN_08042160 -> FUN_0804BC6C(row,A,B)

Trzeba odzyskać:
- vtable row;
- constructor/base constructor;
- child +0x60;
- child +0x8C;
- child +0xF8;
- geometria;
- parent assignment;
- visibility/state fields;
- touch handler.

Nie wolno utożsamiać samego bitmap_A/B z funkcją nawigacyjną.

### B — zamknąć post-processing

FUN_0803C178(model,slot) jest capability resolverem dla 21 slotów.

Dla każdego slotu potrzebny jest osobny rekord:

slot
selector
capability gate
access gate
constructed?
visible?
resource A
resource B
parent
screen target
touch target

### C — zamknąć runtime 0x20005F08

21 bajtów jest konsumowanych jeden-na-jeden z 21 slotami.

Wymagane:
- wszystkie writer/xref;
- initialization;
- znaczenie wartości 0x0E;
- związek z FUN_08032F08;
- związek z FUN_0803C270.

Na obecnym materiale nie wolno jeszcze nazwać 0x0E konkretnym stanem menu.

### D — zamknąć navigation

Trzeba znaleźć, jak selector row przechodzi do:
- konkretnego screen/page constructor;
- kontekstu +0x12A/+0x12B/+0x12C;
- ewentualnie modelu/parametru.

Szczególnie ważne jest rozdzielenie:
- selector menu,
- page context,
- instance selector,
- parameter ID.

## 4. Istotny most architektoniczny

Dotychczasowe wyniki pokazują, że firmware nie ma jednego prostego indeksu „menu item”.

Występują niezależne wymiary:
- selector row;
- installation/capability configuration;
- access level +0x158;
- page context +0x12A;
- secondary family/context +0x12B;
- active instance +0x12C;
- parameter ID.

Dlatego finalny MenuTree musi być grafem/relacją, a nie płaską tablicą nazw.

## 5. Priorytet śledzenia

P0:
1. FUN_08032F08
2. FUN_0803C270
3. writers/readers 0x20005F08
4. row constructor/vtable
5. selector -> navigation callback

P1:
6. 17 level-3 wrapper/page families
7. +0x12A/+0x12B/+0x12C -> concrete pages
8. selector 90 -> Language screen
9. second-stage selectors 97/100/98/95 -> concrete screens
10. exact child/widget tree per screen

P2:
11. parameter -> widget -> CAN write path for each setting screen
12. full configuration/access matrix

## 6. Current evidence matrix

| Element | Status |
|---|---|
| 21-slot row family | HARD |
| 15 base + 6 access-dependent construction | HARD |
| capability pass over 21 slots | HARD |
| runtime 21-byte array @ 0x20005F08 | HARD address/usage, contents OPEN |
| row builder A/B resources | HARD |
| first 15 selector semantics | STRONG |
| six access-dependent selector semantics | OPEN |
| row class/vtable | OPEN |
| exact row geometry | OPEN |
| selector -> screen navigation | OPEN |
| 0x20005F08 producer | OPEN |
| FUN_08032F08 semantics | OPEN |
| FUN_0803C270 semantics | OPEN |
| complete MenuTree | OPEN |

## 7. Stale-hypothesis guard

Do not reintroduce:
- 47290 as Home vertical menu;
- 47290 as proven Language selector;
- selector 90 -> 47290 without navigation proof;
- selector IDs as direct screen IDs;
- bitmap IDs as widget IDs;
- +0x12A as parent pointer;
- +0x12B as CO number;
- +0x12C as generic menu index.

## 8. Immediate execution target

The next concrete pass should recover the bodies/XREFs around:
FUN_08032F08
FUN_0803C270
and the row class used by FUN_0804BC6C.

Success criterion:
at least one complete chain of the form

row slot
 -> state/capability
 -> touch/callback
 -> navigation
 -> concrete screen constructor
 -> context selector
 -> child/widget

with every edge tagged FACT or INFERENCE.

