# BATCH — HOME ROOT: KOREKTA ROLI 47290 + NOWY KIERUNEK GRAFIKI — 2026-11-19

## 1. Twarda korekta wcześniejszej interpretacji
Po ponownym odczytaniu całego FUN_08047334 nie wolno już traktować FUN_08047290 jako sześciu dolnych kafli Home.

Powód jest bezpośrednio geometryczny. Dla slotu uVar6 funkcja ustawia pozycję tekstu:
- X = pole slotu + 10,
- Y = 0x3C + uVar6*0x26, gdy liczba pozycji < 6,
- albo Y = 0x32 + uVar6*0x22, gdy jest 6 pozycji.

Dla dokładnie 6 slotów daje to Y około: 50, 84, 118, 152, 186, 220 px. To jest układ pionowej listy 6 pozycji, a nie 6 poziomych stref dolnego paska 480x72.

Zatem wcześniejsze twierdzenie `47244 + 47290[6] = 7 dolnych stref` zostaje anulowane.

## 2. Co 47290 faktycznie robi
47290 tworzy 6 powtarzalnych rekordów oraz 6 obiektów tekstowych. FUN_08047334 ustawia ich pozycje pionowo i dla każdego przypina osobny TypedText z tablicy `param_7`.

To wygląda znacznie bardziej jak lista/menu/selektor z sześcioma pozycjami. Może być jednym z ekranów lub overlayów zarządzanych przez Home root, ale nie mamy prawa utożsamiać go z dolnym paskiem.

## 3. 47604 też odpada jako grafika kotła
Pełny konstruktor 47604 jest jednoznacznie komponentem wykresowym:
- 5 powtarzanych rekordów danych;
- FUN_08047C1A normalizuje wartości X/Y;
- obliczenia używają zakresu 300 i 0x78;
- rysowane są serie/krzywe;
- cztery duże obiekty 480x200 są przesuwanymi obszarami tego komponentu.

To nie jest kocioł ani dolny pasek.

## 4. Nowy ciekawy komponent: 47E54 -> 2DF80
FUN_08047E54 tworzy osobny komponent i w swoim setupie wywołuje `FUN_0802DF80(param_1 + 0x18)`.

FUN_0802DF80 tworzy własny złożony zestaw elementów:
- trzy obiekty `FUN_0802DD74` pod +0x0B, +0x1D, +0x2F;
- kilka dodatkowych obiektów;
- tekst/TypedText pod +0xA2;
- kolejne elementy pod +0x41, +0x52, +0x63, +0x74;
- elementy są rozmieszczone w szeregu X=0, 0x33, 0x66, 0x99 oraz drugi rząd Y=0x3C.

To jest rzeczywisty kompozyt wielu małych elementów, ale jego semantyki nie przypisujemy jeszcze do alarmu/kotła bez identyfikacji zasobów.

47E54 dodatkowo tworzy TypedText 0x1D4 (468) na pozycji X=0x87=135, Y=0x3C=60, szerokość 200.

## 5. Co teraz jest właściwym celem
Skoro 47290 i 47604 nie odpowiadają wizualnie za dolny pasek/kocioł, należy przejść przez pozostałe dzieci FUN_0803E5AC i identyfikować je po GEOMETRII + zasobach, a nie po samej liczbie obiektów.

Priorytet:
1. 47E54 / 2DF80 — rozwiązać TypedText 468 oraz bitmapy/małe obiekty.
2. 2E716 — rozwiązać jego childy i funkcje `34A2C/34A40/34A54/34A68`.
3. 47244 — ustalić dokładny child/vptr i resource.
4. obiekty 38ED0 / 2DF08 / 47FD4/FE8/FFC — ustalić, czy są elementami widocznego Home.
5. Dopiero po identyfikacji konkretnego Image/Bitmap przejść do `370A`.

## 6. Zasada dalszej analizy
Nie wolno już mapować komponentu do fragmentu screenshotu tylko dlatego, że ma podobną liczbę elementów. Wymagamy co najmniej dwóch niezależnych dowodów: geometria + TypedText/Bitmap/resource albo geometria + callback/model.