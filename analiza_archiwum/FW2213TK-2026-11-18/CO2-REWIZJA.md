# CO2 – rewizja ustaleń po odkryciu bazy TypedText

## Nowe twarde dane

Tablica CANopen ↔ panel ID zawiera:
- 0x2064 -> ID 191 = Tryb CO 1
- 0x2065 -> ID 168 = Tryb CO 2
- 0x2032 -> ID 170 = CO – temperatura komfort (zadana)
- 0x2048 -> ID 171 = CO – temperatura eko (zadana)
- 0x2166 -> ID 172 = obecnie bez nazwy w katalogu

Czyli CO2 ma bezpośrednio potwierdzony panel-ID 168 dla trybu CO2. To jest mocniejsze ustalenie niż wcześniejszy kandydat.

Nie znaleziono jeszcze potwierdzonego osobnego zestawu rejestrów dla wszystkich nastaw CO2. Nie zakładamy więc, że 0x2032/0x2048 są wyłącznie CO1 lub wyłącznie CO2.

## Teksty CO2

- TypedText 58 = Ogrzewanie 2 / Heating 2
- TypedText 100 = OGRZEWANIE 2 / HEATING 2
- TypedText 120 = Ogrzewanie obwód 2 / Heating 2

ID 120 jest szczególnie ważny: w serii 119..122 firmware ma jawne etykiety obwodów 1..4.

## Rewizja wcześniejszego wniosku

rejestry/GHIDRA-FW2213TK-PRZEWODNIK.md zawiera wcześniejszą hipotezę o wspólnym zestawie nastaw CO1/CO2. Nie usuwamy jej, ale po odkryciu bazy TypedText nie można jej traktować jako dowodu braku osobnego UI CO2.

## Następny krok

Znając ID 58/100/120, szukamy w kodzie miejsc, gdzie te wartości są ładowane do TypedText/TextArea, obiektu ekranu, warunku wyboru numeru obwodu, callbacków oraz powiązania z ID panela/CANopen.