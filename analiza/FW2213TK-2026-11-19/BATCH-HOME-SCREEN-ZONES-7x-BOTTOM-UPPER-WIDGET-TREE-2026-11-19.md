# BATCH — HOME SCREEN: 7 DOLNYCH STREF + GÓRNY CONTENT — 2026-11-19

## 1. Screenshot ↔ firmware
Rzeczywisty ekran 480x272 ma górny obszar około 480x200 oraz dolny pasek około 72 px. Dolny pasek jest wizualnie podzielony na 7 stref.

## 2. Dolny pasek — bardzo mocne dopasowanie
FUN_08047244 tworzy osobny komponent z childem pod +0x18, własnym vptr DAT_0804728c i pozycją X=0x32, Y=0x37. Jest osobno od FUN_08047290.

FUN_08047290 tworzy dokładnie 6 slotów: blok elementów pod +0x2A, stride 0x40, count 6 oraz blok tekstów pod +0x8A, stride 0x34, count 6. FUN_08047334 pokazuje, że każdy slot ma osobny element wizualny, TypedText, własne X/Y, kolor i własne dzieci.

Najmocniejszy wniosek: 47244 + 47290[6] daje strukturę 1 + 6 = 7 dolnych stref. To jest bardzo dobry 1:1 odpowiednik podziału widocznego na screenshotach.

## 3. Każda dolna strefa jest złożona
Dla każdego z 6 slotów FUN_08047334 wykonuje m.in. FUN_0804c320, FUN_0804c392, FUN_080313A4, ustawienie pozycji, kolor oraz dodanie dzieci do rodzica. Czyli wizualna strefa na pasku jest kontenerem/kompozytem, a nie pojedynczym prostym widgetem.

## 4. Górna część — FUN_08047604
To osobny duży komponent Home. Konstruktor zawiera wiele childów: +0x28, +0x34, +0x3F, +0x4C, +0xA9, +0xBA, +0x22B, +0x2E0, +0x2F2, +0x304. Ma grupę 5 elementów pod +0xBA ze stride 0xE4, grupę 5 tekstów pod +0x2C2, stride 0x0C, cztery duże obiekty pod +0x1D7, stride 0x54 oraz dodatkowe obiekty.

To nie jest pojedynczy widget grafiki kotła. To jest kompozyt górnego Home.

## 5. Znaczenie 480x200
Cztery obiekty pod +0x1D7 dostają W=480, H=200 oraz X kolejno 0, 320, 640, 960 względem bazy. Są to duże obszary/warstwy/strony komponentu, wewnątrz których znajdują się kolejne dzieci.

## 6. Model Home
FUN_0803E5AC
  |
  +-- GÓRA / CONTENT ~480x200
  |   +-- FUN_08047604
  |       +-- wiele childów
  |       +-- grupy 5-elementowe
  |       +-- 4 obszary 480x200
  |       +-- dodatkowe obiekty
  |       +-- grafika kotła / 57.1 / 60 AUTO / Wyłączony / alarm / temperatura zewnętrzna / pozostałe elementy
  |
  +-- DÓŁ / ~72 px
      +-- FUN_08047244 = strefa 1, bardzo prawdopodobnie MENU
      +-- FUN_08047290 = strefy 2..7
          +-- slot 0
          +-- slot 1
          +-- slot 2
          +-- slot 3
          +-- slot 4
          +-- slot 5

## 7. CO2
Pusta siódma strefa może odpowiadać opcjonalnemu obwodowi CO2, ale jest to na razie hipoteza. Kod twardo pokazuje 6 slotów w 47290 oraz osobny komponent 47244; funkcji slotów nie przypisujemy bez dalszego śladu tekstu/ikony/callbacku.

## 8. Priorytet
Nie wracać do CO jako głównego toru. Najpierw rozebrać 47244, 47290/47334 oraz 47604 do poziomu childów, callbacków, TypedText, bitmap i vptr. Następnie spiąć 370A -> bitmap kotła.