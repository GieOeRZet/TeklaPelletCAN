# BATCH — KAWAŁEK INTERFEJSU JUŻ MOŻLIWY DO ODTWORZENIA 1:1 LOGICZNIE
Data: 2026-11-19

## Status
**[STRONG] Mamy już wystarczający materiał, żeby zbudować pierwszy działający fragment repliki Home/Main 480×272.**

Nie jest to jeszcze pixel-perfect screenshot clone, bo brakuje części dokładnych geometrii/bitmap dla elementów głównego ekranu. Architektura i kilka elementów dynamicznych są jednak określone na poziomie firmware.

## 1. Twardy szkielet Home/Main
Kandydat root: FUN_0803E5AC, wywoływany przez FUN_0803AFC0. Posiada wiele podkomponentów pod stałymi offsetami.
Najważniejszy dla dolnego paska: root + 0x92DC -> FUN_08047290.
FUN_08047290 tworzy dokładnie 6 powtarzalnych elementów, stride 0x40.
[STRONG] To jest wystarczająca podstawa do zbudowania kontenera dolnego paska jako sześciu osobnych obiektów, zamiast jednego obrazka.

## 2. Dynamiczny blok palnika
CAN 0x4005 -> panel id 59 / 0x3B -> FUN_0803CF54 -> FUN_080436B4.
FUN_080436B4 wykonuje value / 10 oraz value % 10. Raw 638 daje dokładnie 63.8.
Komponent pobiera też 0x299F Burning type, 0x2276 Grate move indicator, 0x2007 Burner state, 0x2250 Flame brightness i 0x2119.
[FW] 63.8 ma już twarde źródło CAN, panel ID i formatter.

## 3. Temperatura zewnętrzna
FUN_08031CCC pobiera panel id 1 -> CAN 0x215F = Outside temperature.
[FW] Dane dla tego pola są już znane; finalny widget i geometria nadal wymagają mapowania.

## 4. Blok 60/AUTO
FUN_08031CCC rozdziela panel id 11 -> 0x2002 Boiler program/mode, id 16 -> 0x2003 Boiler set manual temp oraz id 15 -> 0x2004 Boiler set result temp.
Kod przekazuje te dane do osobnych funkcji UI, m.in. FUN_0802D524 i FUN_0802D48A.
[STRONG] Możemy już odtworzyć logikę AUTO/MAN + wartość zadana, ale nie wolno jeszcze utożsamiać 60 wyłącznie z 0x2003 w każdym trybie.

## 5. Zasobnik
FUN_08031CCC pobiera id 328 -> 0x3601 Fuel remaining [kg], id 330 -> 0x3603 Fuel reserve [kg], id 327 -> 0x3740 nadal nierozwiązane.
Następnie liczy (id327 * 100) / id328 i przekazuje wynik do FUN_0802DA54.
[STRONG] Wizualizacja zasobnika jest dynamicznym komponentem, a nie statyczną bitmapą.

## 6. Geometria
FUN_08030358 = setGeometry(object, X, Y, W, H): r1=X, r2=Y, r3=W, stack=H.
FUN_080612E0 ustawia dla this+0x48 geometrię X=0, Y=0, W=480, H=272.

## 7. Pierwsze absolutne współrzędne widgetów
Komponent CO2:
- r4+0x8B4: TypedText 348 = „Błąd wygaszania”; X=205, Y=195, W=200, H=70.
- r4+0x8EC: TypedText 460 = „Liczba kotłów slave”; X=320, Y=195, W=200, H=70.
To są rzeczywiste firmware coordinates.

## 8. CO1/CO2
CO2 raw 0x46D2C / runtime 0x08056D2C oraz CO1 raw 0x4B618 / runtime 0x0805B618 mają różne vtable.
CO2 ma TypedText 58 = Ogrzewanie 2, pole +0x12A = 2 i wywołanie 0x0805D948. CO1 ma analogiczną własną strukturę.

## 9. Co możemy zbudować TERAZ
Pierwszy działający prototyp Home/Main może już zawierać:
1. canvas 480×272;
2. dolny kontener z 6 obiektami;
3. dynamiczny blok palnika z 63.8 + Modulacja + stanem palnika;
4. temperaturę zewnętrzną z 0x215F;
5. blok zadanej temperatury + AUTO/MAN z 0x2002/0x2003/0x2004;
6. blok zasobnika z pozostałym paliwem i rezerwą;
7. widoczność zależną od 0x3505 i 0x2105;
8. osobne komponenty CO1/CO2.

Nie mamy jeszcze twardych danych dla finalnych X/Y/W/H wszystkich elementów Home, bitmap ID wszystkich sześciu kafli, wszystkich fontów oraz callbacków touch. Dlatego obecny prototyp może być funkcjonalnie i architektonicznie zgodny, ale nie pixel-perfect.

## 10. Następny cel
Atakujemy FUN_0803E5AC -> +0x92DC / FUN_08047290 -> sześć obiektów -> vtable -> bitmap / TypedText / geometry -> callback.
Równolegle FUN_0803CF54 -> obiekt palnika -> vtable -> konstruktor -> geometry -> bitmap + TypedText.
Cel kolejnego raportu: pierwszy pełny rekord widget -> parent -> X/Y/W/H -> TypedText/Bitmap -> visibility -> callback -> panel ID -> CAN.

## Pewność
- [FW] CAN/panel/formatter/geometria.
- [STRONG] sześć elementów dolnego paska jako osobne obiekty.
- [STRONG] dynamiczne komponenty Home/Main.
- [HYPOTHESIS] przypisanie konkretnych sześciu pozycji do nazw ze screenshotu.