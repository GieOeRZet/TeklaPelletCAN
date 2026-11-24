# BATCH-ANALIZA-MOST-2105-WARIANTY-INSTANCJE-2026-11-19

## Cel
Kolejny pakiet analizy mostu:
`0x2105 Heating configuration` -> konfiguracja modułów -> wariant -> obiekty/instancje CO.

## 1. Wariant sprzętowy jest wybierany przez trzy pola obiektu głównego

**UDOWODNIONE**

W `FUN_08000e34` / okolicach `0x08001xxx` firmware buduje indeks `iVar14`, który wybiera wpisy z wielu równoległych tablic `local_48 .. local_328`.

Dla:
- `Main module type = 0`
- `CH expansion module type = 0`

profil:
- 1 -> wariant 2
- 2 -> wariant 3
- 3 -> wariant 4

Dla:
- Main = 0
- expansion = 1

profil:
- 1 -> wariant 5
- 2 -> wariant 6
- 3 -> wariant 7

Dodatkowo:
- Main = 1 lub 2 ma osobne ścieżki,
- Main = 2 może kończyć się bez części wskaźników,
- wariant nie jest pojedynczym parametrem: ten sam indeks wybiera dziesiątki struktur/wskaźników naraz.

To jest mocniejszy dowód niż samo istnienie rejestrów 3500/3502/350B: te wartości realnie sterują architekturą obiektów.

## 2. 0x3500 / 0x3502 / 0x350B są częścią stanu głównego obiektu

**UDOWODNIONE**

`FUN_08001ae4` rejestruje:
- `object+0x16BF` -> `0x3500` Main module type
- `object+0x16C0` -> `0x3502` CH expansion module type
- `object+0x16CC` -> `0x350B` Profile number

Ta sama trójka jest później eksportowana do struktury diagnostyczno-statusowej:
- byte 0 = `16BF`
- byte 1 = `16C0`
- byte 2 = `16CC`

Czyli nie są to przypadkowe wpisy mapy parametrów. Są to trzy realne pola konfiguracji głównego obiektu.

## 3. Odkryte czwarte pole konfiguracji: +0x16C1

**UDOWODNIONE**

`object+0x16C1` jest używane niezależnie od:
- Main module type `+0x16BF`
- expansion `+0x16C0`
- profile `+0x16CC`

Wpływa na wybór wskaźnika/struktury w dwóch głównych gałęziach:

Main=0:
- `16C1 == 2` -> `object+0x199C`
- inaczej -> struktura z obszaru `+0x77A0`

Main=1/2:
- `16C1 == 2` -> `object+0x199C`
- inaczej -> struktura z obszaru `+0x7DCC`

Pole `16C1` jest również eksportowane jako byte 9 statusu konfiguracji.

**WNIOSEK:** obecny model `3500 + 3502 + 350B` nie opisuje całej konfiguracji sprzętowej. Istnieje co najmniej jeszcze jeden bit/bajt konfiguracji wpływający na wybór implementacji.

Nie nadaję mu jeszcze nazwy — brak dowodu, który parametr CAN go zasila.

## 4. +0x16D5 to inny warunek, nie należy go utożsamiać z 0x16C1

**UDOWODNIONE**

`object+0x16D5` występuje w inicjalizacji ścieżki zależnej od Main module type:
- przy Main=0 sprawdza `16D5 == 1`,
- przy Main=1 sprawdza `16D5 != 1`.

To pole nie pojawia się w tym samym statusowym bloku co 16C1 i nie jest rejestrowane przez pokazany fragment `FUN_08001ae4`.

**WNIOSEK:** mamy więcej niż trzy pola sprzętowo-konfiguracyjne. Nie wolno próbować wtłoczyć całej logiki w 3500/3502/350B.

## 5. 0x2105 jest prawdziwym parametrem konfiguracji, ale nie ma literalnego użycia w kodzie zdekompilowanym

**UDOWODNIONE**

Mapa panela:
- `0x2105`
- `Heating configuration`
- u8
- zakres 0..4
- default 1
- storage panela `0x20021FAF`
- wpis mapy parametrów `0x0801A5B0`

Jednocześnie pełny aktualny blob `decompiled.c` nie zawiera literalnych referencji do:
- `0x2105`
- `0x20021FAF`
- `0x0801A5B0`

To jest ważne negatywne znalezisko.

**Wniosek:** 0x2105 prawdopodobnie nie jest obsługiwany przez zwykłą ścieżkę, w której występują jawne stałe indeksów w kodzie. Najbardziej prawdopodobne miejsca to:
1. dane/tabele parametrów,
2. kod pośredni generujący dostęp do indeksu,
3. fragment firmware, którego Ghidra nie zrekonstruowała jako literalnej referencji.

Dlatego NIE twierdzimy jeszcze, że `0x2105 -> +0x12C`.

## 6. 0x2106..0x2108 są w warstwie konfiguracji aplikacyjnej, ale 0x2105 jest z niej wyjęty

**UDOWODNIONE**

W naszym silniku rekonstrukcyjnym `kConf` zawiera:
`0x3501, 0x3500, 0x3505, 0x3720, 0x2106, 0x2108, 0x2107, ...`

`0x2105` nie występuje.

To pasuje do obserwacji z firmware: 0x2105 ma inny status niż 2106/2107/2108.

**BARDZO PRAWDOPODOBNE:** `Heating configuration` nie jest zwykłą flagą funkcjonalną typu CWU/bufor/solar, tylko parametr uruchamiający lub opisujący strukturę obwodów grzewczych. To nadal nie dowodzi dokładnej semantyki wartości 0..4.

## 7. DAT_0803C218 to osobna tablica klasyfikacji obiektów

**UDOWODNIONE**

`FUN_0803C064(param_1,param_2)` robi:

`class = DAT_0803C218[param_2]`

i dla klas 1..4 ustawia:
- instancję 1
- instancję 2
- instancję 3
- instancję 4

Natomiast klasy 5..10 i dalsze wartości kierują do wyspecjalizowanych konstruktorów.

To bardzo dobrze pasuje do wcześniej znalezionego:
- `+0x12B` = klasyfikacja obiektu
- `+0x12C` = numer instancji 1..4

**ALE:** w obecnym decompiled.c nie ma zwykłego bezpośredniego call-site do `FUN_0803C064`; występuje tylko definicja. Nie będziemy więc jeszcze przypisywać konkretnych wpisów tej tablicy do CO.

## 8. DAT_0804107C: 22 wpisy są rzeczywiście używane jako konfiguracja instancji

**UDOWODNIONE**

`FUN_08040FC2`:
- iteruje dokładnie 22 wpisy,
- z każdego wpisu pobiera pierwszy element jako indeks parametru,
- pobiera drugi/konfiguracyjny element,
- wywołuje `FUN_08036FF2(..., index)`,
- następnie `FUN_08040E46(..., entry_number, result)`,
- dla indeksów `0x85` i `0x141` wykonuje dodatkowe mapowanie.

`FUN_08041020` zapisuje później parametr przez:
`FUN_08037212(..., table[param_2*3])`.

Czyli ta tablica jest realnym mostem:
**parametr CAN -> obiekt/slot -> zapis do obiektu**.

Nie mamy jeszcze samych 22 wartości tabeli, ponieważ Ghidra nie wyemitowała danych `DAT_0804107C` jako inicjalizatora w decompiled.c.

## 9. Co z tego wynika dla 0x2105

Aktualny obraz architektury jest teraz:

```
0x3500 Main module type
0x3502 CH expansion module type
0x350B Profile number
0x16C1 dodatkowa konfiguracja
0x16D5 dodatkowy warunek
        |
        v
 wybór wariantu 1..7
        |
        v
 zestaw wielu struktur/wskaźników
        |
        v
 obiekty modułów
   +0x12B = klasa
   +0x12C = instancja 1..4
        |
        +--> 0x36FF2 / 0x37212 / 0x1167A
        |
        v
   parametry CO1..CO4
```

Osobno:
```
0x2105 Heating configuration (0..4)
        |
        ?  <- nadal szukamy
        v
utworzenie/aktywacja liczby obiektów CO
```

Najważniejsze: **nie znaleźliśmy jeszcze mostu 2105 -> wariant**, ale znaleźliśmy dodatkowe pola konfiguracji, które tłumaczą, dlaczego wcześniejsze próby sprowadzenia całej logiki do jednego 2105 były zbyt proste.

## Następny cel

Teraz priorytetowo:
1. odzyskać dane `DAT_0804107C`,
2. odzyskać dane `DAT_0803C218`,
3. znaleźć źródła pól `16C1` i `16D5`,
4. znaleźć wszystkie mechanizmy tworzenia obiektów CO,
5. dopiero wtedy wrócić do `0x2105` i sprawdzić, czy jego wartości 0..4 sterują liczbą instancji, widocznością, czy tylko trybem konfiguracji.

Do czasu znalezienia tego mostu 0x2105 pozostaje **BARDZO PRAWDOPODOBNYM kandydatem na „liczbę obwodów”, ale nie dowodem implementacyjnym**.
