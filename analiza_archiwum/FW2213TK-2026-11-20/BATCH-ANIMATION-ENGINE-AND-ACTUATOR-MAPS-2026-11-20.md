# TeklaPelletCAN — ANIMATION ENGINE / ACTUATOR MAP — 2026-11-20

## Cel przebiegu
Weryfikacja użytkownikowej listy animacji: 138–143 pompa, 105–107 mieszacz, 36–44 podajnik/ruszt/grzałka, 8–10 wentylator. Analiza bez ponownej ekstrakcji bitmap.

## [FW] Wspólny silnik animacji — 0x0803079A / 0x080307AE / 0x08030708 / 0x08030640

`FUN_0803079A(object, first_resource, last_resource)` zapisuje:
- `+0x30 = first_resource`
- `+0x32 = last_resource`

`FUN_080307AE(object, ticks)` ustawia:
- `+0x34 = ticks`
- `+0x35 = 0`

`FUN_08030708(object, &dir, &enable, &... )` zapisuje stan kierunku/aktywacji do:
- `+0x36`
- `+0x37`

`FUN_08030640(object)` jest krokiem/update animacji:
- zwiększa licznik `+0x35`,
- po osiągnięciu `+0x34` zmienia bieżący resource `+0x26`,
- zależnie od `+0x36` przechodzi w stronę `+0x32` albo `+0x30`,
- przy `+0x37` instaluje wyliczony resource przez `FUN_080307BC`,
- obsługuje zakończenie/rejestrację update.

To jest twardy dowód, że `+0x30/+0x32` są granicami zakresu klatek/resource IDs, a nie przypadkowymi polami geometrii.

## [FW] 138–143 — zakres sześciu klatek
W konstruktorze przy runtime `0x08044CE?` (dokładnie call `0x08044CE6`):
```text
r1 = 0x8A = 138
r2 = 0x8F = 143
FUN_0803079A(object=parent+0x85C, first=138, last=143)
...
FUN_080307AE(object+0x85C, 3)
```
Ta sama konfiguracja `138..143` występuje również w powtarzalnych konstruktorach w blokach `0x0804C60C`, `0x0804C988`, `0x0804CC90`, `0x0804CF5C`, `0x0804D208`, `0x0804D51C`, `0x0804D830`, `0x0804DB44`.

[STRONG] To bardzo mocno potwierdza rodzinę animowanego obrazka pompy jako współdzielonego komponentu w wielu ekranach/instancjach. Sam BIN nie dowodzi jeszcze, że każda z tych instancji jest dokładnie CO/CWU/Home.

## [FW] 105–107 — mieszacz: stan 0/1/2 i trzy zasoby
Konstruktor `FUN_0803C4C4`:
- `+0x2C` dostaje resource `0x69 = 105`
- `+0x58` dostaje resource `0x6B = 107`
- `+0x32 = 3`

`FUN_0803C550(object, state)`:
- `state=0`: `+0x25=0`, nie przełącza `+0x58` na 106/107
- `state=1`: `+0x25=1`, `+0x58 = 0x6A = 106`
- `state=2`: `+0x25=1`, `+0x58 = 0x6B = 107`

`FUN_0803CA6E(object,state)` jest upstream dispatcherem:
- state 0 lub 1 -> `FUN_0803C550`
- state 2 -> bezpośrednio resource 107 na `+0xAEC` i dalszy refresh.

Caller `FUN_0803CBD6` pobiera panel ID `0x29` i przekazuje wynik do `FUN_0803CA6E`.

[STRONG] User observation „105 + 106/107 zależnie od otwierania/zamykania mieszacza” jest zgodna z wykonaniem firmware. 105 jest bazowym/stabilnym zasobem, 106 i 107 są stanami przejścia kierunkowego; dokładne przypisanie open vs close wymaga jeszcze rozstrzygnięcia wartości parametru 0x29 w runtime.

## [FW] 36–42 — dwie zakresowe animacje 3-klatkowe w jednym agregacie
W konstruktorze bloku `0x08042EEC`:
- object `+0x90C`: `FUN_0803079A(first=0x24=36,last=0x26=38)`, `FUN_080307AE(ticks=0x0E=14)`
- object `+0x948`: `FUN_0803079A(first=0x28=40,last=0x2A=42)`, `FUN_080307AE(ticks=0x0E=14)`

Oba dostają aktywację przez `FUN_08030708`.

[STRONG] To zamyka co najmniej dwa podajniko/ruchowe zestawy 36–38 oraz 40–42. Nie znaleziono w tym silniku bezpośredniego zakresu 36..44; zasoby 43/44 nie zostały jeszcze przypisane do tego samego mechanizmu.

## [FW] 8–10 — zakres animacji wentylatora
W tym samym konstruktorze `0x08042EEC`:
```text
object +0x9C0
FUN_0803079A(first=0x08=8,last=0x0A=10)
FUN_08030708(...)
FUN_080307AE(ticks=0x06=6)
```
Dodatkowo w funkcji sterującej `0x08043954` obiekt `+0x9C0` jest jednym z sześciu wybieralnych actuator/animation objects; dla indeksu `3` ustawiany jest jego stan enable/direction.

[STRONG] To jest twardy firmware'owy ślad animacji 8→9→10. Użytkownikowa identyfikacja jako wentylator jest bardzo wiarygodna, ale bez bezpośredniego label/source stringu nadal oznaczamy semantykę jako STRONG, nie FW.

## [FW] Sześciokanałowy agregat animacji / actuatorów
`FUN_08043954(object, index, enable)` przyjmuje `index 0..5` i przełącza jeden z sześciu obiektów:
- index 0 -> `+0x948`
- index 1 -> `+0x90C`
- index 2 -> `+0x984`
- index 3 -> `+0x9C0`
- index 4 -> `+0x9FC`
- index 5 -> `+0xA38`

W tym samym agregacie konstruktor `0x08042EEC` ustawia co najmniej:
- `+0x90C` = 36..38
- `+0x948` = 40..42
- `+0x984` = 65..67
- `+0x9C0` = 8..10
- `+0x9FC` = 58..59
- `+0xA38` = animowany/sterowany obiekt, dokładny resource range nadal OPEN.

[STRONG] To jest znacznie ważniejsze niż pojedyncze bitmapy: firmware posiada wspólny sześciokanałowy mechanizm sterowania animacjami/actuator icons, a `index` wybiera konkretną animację.

## [FW] 138–143 w wielu instancjach
Konfiguracja `138..143` jest powtarzana w ośmiu miejscach konstrukcyjnych. To sugeruje współdzielony komponent pompy, a nie pojedynczy ekran.

## [OPEN]
1. Rozstrzygnąć dokładne znaczenie indeksów 0..5 z nazw/source trace lub panel IDs.
2. Przypisać 36..38 / 40..42 / 65..67 / 8..10 / 58..59 / A38 do: podajnik, ruszt, grzałka, wentylator, pompa itd.
3. Zamknąć semantykę 138..143: CO, CWU i ewentualnie Home tile.
4. Rozstrzygnąć open/close dla 106/107 na podstawie runtime parametru 0x29.
5. Sprawdzić, czy 43/44 należą do innego mechanizmu animacji.

## USER CORRECTIONS — 2026-11-20

- 8–10 = wentylator/dmuchawa palnika.
- 58–59 = ruch rusztu palnika; okoliczności uruchomienia OPEN.
- 65–67 = animacja grzałki palnika; dokładne stany OPEN.
- 60–61 = semantyka nieznana; nie przypisywać bez call-site.
- 138–143 = pracująca pompa; użytkownik potwierdza CO i CWU; Home pozostaje do sprawdzenia w BIN.

Dla 36–38 i 40–42 nadal szukamy konkretnego urządzenia.

## Najważniejsza korekta względem wcześniejszego tropu hoppera
Pola `+0x30/+0x32/+0x34/+0x36/+0x37` są teraz częściowo zamknięte jako pola mechanizmu animacji w konkretnych obiektach. Nie wolno jednak automatycznie przenosić tej semantyki na `parent+0x5A8` hoppera bez proof, ponieważ hopper ma własny kontekst i może współdzielić strukturę tylko częściowo.

## [FW] 2026-11-20 — ZAMKNIĘCIE INDEKSÓW 0..4 PRZEZ UPSTREAM DATAFLOW

Nowy twardy krok względem wcześniejszego „index -> asset”.

FUN_08043954(object, index, enable) ma 5 bezpośrednich call-site'ów:
- 0x0803D100: index=1, enable = U8(FUN_08036FF2(ctx, 0x41))
- 0x0803D112: index=0, enable = U8(FUN_08036FF2(ctx, 0x45))
- 0x0803D124: index=2, enable = U8(FUN_08036FF2(ctx, 0x46))
- 0x0803D136: index=3, enable = U8(FUN_08036FF2(ctx, 0x47))
- 0x0803D148: index=4, enable = U8(FUN_08036FF2(ctx, 0x75))

W pełnym skanie bezpośrednich BL nie ma call-site FUN_08043954(..., index=5, ...). +0xA38 ma więc inną ścieżkę sterowania.

### [FW] internal ID -> panel parameter ID

FUN_08036FF2 skanuje tablicę mapującą internal IDs na identyfikatory parametrów panela. Tablica jest adresowana przez ADR z tej funkcji; jej baza runtime to 0x0803757C, czyli file offset 0x357C.

Interesujące rekordy:
- file 0x37640: 0x46 -> 0x2253, 0x47 -> 0x2254, 0x41 -> 0x2251
- file 0x37650: 0x45 -> 0x2252
- file 0x376A0: 0x75 -> 0x2276

### [FW/DATA] Semantyka parametrów

Nazwy zapisane w firmware / katalogu parametrów:
- 0x2251 = Burner storage feeder
- 0x2252 = Burner burner feeder
- 0x2253 = Burner igniter
- 0x2254 = Burner blower
- 0x2276 = Grate move indicator

### [FW] Zamknięte mapowanie indeksów

| index | obiekt | resource range | enable source | semantyka |
|---:|---|---|---|---|
| 0 | +0x948 | 40..42 | 0x45 -> 0x2252 | podajnik palnika |
| 1 | +0x90C | 36..38 | 0x41 -> 0x2251 | podajnik paliwa / storage feeder |
| 2 | +0x984 | 65..67 | 0x46 -> 0x2253 | zapalarka / grzałka palnika |
| 3 | +0x9C0 | 8..10 | 0x47 -> 0x2254 | dmuchawa palnika |
| 4 | +0x9FC | 58..59 | 0x75 -> 0x2276 | ruch rusztu |
| 5 | +0xA38 | OPEN | brak bezpośredniego call-site | OPEN |

### [STRONG + USER] 36–42

Użytkownik potwierdza:
- 36–38 = podajnik paliwa
- 40–42 = podajnik palnika

BIN potwierdza to niezależnym łańcuchem dataflow: storage feeder -> 0x2251 -> index 1 -> 36..38; burner feeder -> 0x2252 -> index 0 -> 40..42.

### [FW] 58–59

0x2276 = Grate move indicator, więc 58..59 mają zamknięte źródło sterowania: wskaźnik ruchu rusztu. Dokładny warunek/kierunek ruchu pozostaje OPEN.

### [FW] 65–67

0x2253 = Burner igniter, więc 65..67 są sterowane przez parametr zapalarki. To mocniejszy dowód niż sama grafika; rozdział klatek 65/66/67 na konkretne stany pozostaje OPEN.

### [OPEN] 39

Bitmap 039 ma 30x18 + A8. Resource 0x27=39 występuje w osobnym komponencie przy runtime około 0x0802FA00, razem z resource 168/169. Dowodzi to użycia 39 w UI, ale nie dowodzi jeszcze, że jest to dokładnie ikona drugiego kafelka „Magazyn paliwa”. Wizualnie pasuje do małej grafiki mechanizmu/transportera; parent/widget nadal wymaga trace.

## [OPEN] Następne przebiegi

1. Trace index 5 / +0xA38.
2. Trace 0x2276 i zamknąć warunki 58/59.
3. Trace 0x2253 i rozdzielić 65/66/67.
4. Trace 0x2254 i sprawdzić logikę 8/9/10.
5. Trace 0x2251/0x2252 i rozdzielić dokładną logikę klatek feederów.
6. Trace parent/widget resource 39.

## [FW] MULTIPASS 2026-11-20 — PARAMETRY + TIMER + KIERUNEK

Pełny raw disassembly potwierdza nie tylko zakresy resource, ale także parametry czasowe i stan startowy silnika.

### [FW] Konstruktor agregatu 0x08042EEC

Dla wszystkich pięciu zamkniętych kanałów konstruktor przekazuje do FUN_08030708:
- direction = 0
- enable = 1

Następnie ustawia tick count:
- 36..38: ticks = 14
- 40..42: ticks = 14
- 65..67: ticks = 18
- 8..10: ticks = 6
- 58..59: ticks = 25

W FUN_08030640 kierunek +0x36=0 oznacza inkrementację resource, a +0x36!=0 dekrementację. Przy standardowej konfiguracji startowej wszystkie pięć kanałów ma ruch first -> last.

### [FW] FUN_08043954 nie ustawia bezpośrednio kierunku dla kanałów 0/1/2/4

- index 0: zapisuje bool do parent+0x96D i odświeża +0x948
- index 1: zapisuje bool do parent+0x931 i odświeża +0x90C
- index 2: zapisuje bool do parent+0x9A9 i odświeża +0x984
- index 3: jawnie wywołuje FUN_08030708 na +0x9C0 z direction=0, enable=1; wejściowy bool trafia do parent+0xBB5
- index 4: zapisuje bool do parent+0xA21 i odświeża +0x9FC

Wniosek: wejściowy enable FUN_08043954 nie jest automatycznie polem +0x37 silnika animacji dla wszystkich kanałów.

### [STRONG] Konsekwencja

Nie należy jeszcze mówić, że parametr 0x2251 bezpośrednio włącza/wyłącza timer animacji 36..38. Twardo wiemy, że wartość steruje flagą powiązaną z tym kanałem i powoduje refresh; sam obiekt animacyjny jest konfigurowany niezależnie.

### [FW] 0x23 -> 0x216A i kontekst nazw

W FUN_08036FF2 internal 0x23 mapuje się przez tabelę file 0x375CC na panel parameter 0x216A.

Parametry 0x216A..0x216F są rejestrowane kolejno około 0x302E..0x3252. W katalogu stringów występuje kolejność:
- Burner state
- Burner storage feeder
- Burner burner feeder
- Burner igniter
- Burner blower
- Burner storage feeding time [dS]

[STRONG] Z wysoką pewnością:
0x216A = Burner state
0x216B = Burner storage feeder
0x216C = Burner burner feeder
0x216D = Burner igniter
0x216E = Burner blower
0x216F = Burner storage feeding time [dS].

### [FW] Nowy trop dla 36..38

Funkcja około 0x0803C8D2:
- pobiera internal parameter 0x23
- mapowanie daje 0x216A
- zamienia wynik na bool
- zapisuje go do parent+0x931
- odświeża obiekt +0x90C = zakres 36..38.

To nie dowodzi jeszcze, że 36..38 są animowane wyłącznie podczas konkretnego stanu palnika, ale jest bezpośredni firmware'owy związek Burner state -> stan obiektu 36..38.

### [FW] Resource 39 — osobny komponent

Funkcja 0x0802F9FC ustawia komponent przy parent+0xA8. W zależności od stanu ustawia resource 39 oraz parę 168/169; 168/169 są zamieniane miejscami między wariantami.

To jest osobny mechanizm od agregatu FUN_08043954.

[OPEN] Brak jeszcze bezpośredniego parent/widget -> konkretny kafelek menu „Magazyn paliwa”.

### [FW] Resource 60/61

W bezpośredniej konstrukcji agregatu 0x08042EEC nie występuje zakres 60..61. Nie ma dowodu, że 60/61 należą do tego samego sześciokanałowego silnika. Pozostają OPEN.

### [FW] Resource 43/44

Nie ma bezpośredniego zakresu 43..44 w konstruktorze agregatu. 43/44 pozostają poza tym engine i wymagają osobnego trace.
