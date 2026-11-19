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
