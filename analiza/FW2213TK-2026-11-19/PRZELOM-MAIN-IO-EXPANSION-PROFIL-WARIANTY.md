# FW2213TK – MAIN I/O + CH expansion + profil: przełomowy trace konfiguracji

Data: 2026-11-19

## 1. Najważniejsze znalezisko

W dekompilacji firmware istnieje realna logika, która łączy:

- `Main module type` = rejestr `0x3500`
- `CH expansion module type` = rejestr `0x3502`
- wewnętrzny `Profile number` = rejestr `0x350B`

z wyborem konkretnego wariantu konfiguracji obiektu.

Nie jest to już tylko nazwa z tabeli parametrów. Kod używa tych pól do wyboru jednego z kilku zestawów danych/struktur.

## 2. Potwierdzone pole + offset

W głównym obiekcie firmware:

- `object + 0x16BF` = Main module type
- `object + 0x16C0` = CH expansion module type
- `object + 0x16CC` = Profile number
- `object + 0x16C1` = kolejna flaga konfiguracyjna

Funkcja `0x08001AE4` rejestruje dwa pierwsze pola jako parametry CAN:

```
FUN_0801143c(..., 0x3500, object+0x16BF, ...)
FUN_0801143c(..., 0x3502, object+0x16C0, ...)
FUN_0801143c(..., 0x350B, object+0x16CC, ...)
```

Dla 0x3500 firmware używa stringa `Main module type`.

Dla 0x3502 firmware używa stringa `CH expansion module type`.

Dla 0x350B firmware używa stringa `Profile number`.

To jest bezpośredni kodowy dowód, że 0x3500/0x3502 są elementami wewnętrznej konfiguracji modułu, a nie przypadkowymi parametrami UI.

## 3. Najważniejszy fragment wyboru wariantu

W funkcji inicjalizacyjnej około `0x08001550` firmware wykonuje:

```
if (main_module_type == 2) {
    profile_variant = 1;
}
else if (main_module_type == 0) {

    if (ch_expansion_type == 0) {
        if (profile == 1) profile_variant = 2;
        if (profile == 2) profile_variant = 3;
        if (profile == 3) profile_variant = 4;
    }

    else if (ch_expansion_type == 1) {
        if (profile == 1) profile_variant = 5;
        if (profile == 2) profile_variant = 6;
        if (profile == 3) profile_variant = 7;
    }
}
```

Jest też osobna gałąź dla `main_module_type == 1`, w której firmware wybiera inny zestaw struktur.

Dokładny pseudokod powyżej jest skrótem logicznym z dekompilacji; nie należy jeszcze traktować nazw `profile_variant` jako nazw z firmware.

## 4. Co to oznacza dla BIG I/O

To bardzo mocno wspiera wcześniejszą hipotezę:

```
                 KONFIGURACJA MODUŁÓW
                         |
             +-----------+-----------+
             |                       |
      Main module type        CH expansion type
          0x3500                   0x3502
             |                       |
             +-----------+-----------+
                         |
                  Profile number
                     0x350B
                         |
                         v
              wybór wariantu obiektu
                         |
                         v
              odpowiedni zestaw struktur
              / obsługiwanych funkcji
```

W szczególności dla `Main module type == 0` (co w naszym emulatorze opisaliśmy jako BIG) obecność/typ modułu rozszerzenia zmienia warianty wybierane przez firmware.

To jest dużo mocniejszy dowód na istnienie warstwy konfiguracji sprzętowej niż samo występowanie nazw 0x3500/0x3502.

## 5. Związek z obiegami CO

W tym samym kodzie wybór wariantu jest zależny od `Profile number` oraz typu modułu rozszerzenia.

Nie znaleźliśmy jeszcze bezpośredniego odczytu `0x2105` w dekompilacji jako literalnej stałej. To ważne: `0x2105 = Heating configuration` pozostaje bardzo mocnym kandydatem na parametr liczby/konfiguracji obiegów, ale nie wolno jeszcze twierdzić, że ta wartość jest bezpośrednim wejściem do powyższego switcha.

Natomiast kod pokazuje, że firmware ma osobną, sprzętową warstwę wyboru wariantu przed dalszą logiką obiektów.

## 6. Ważna korekta wcześniejszego modelu

Nie powinniśmy na tym etapie przedstawiać architektury jako:

```
0x3501 autoconfig
    -> 0x3500/0x3502
    -> 0x2105
    -> CO1..CO4
```

jako faktu.

Aktualnie udowodnione są dwie równoległe warstwy:

### Warstwa sprzętowo-modułowa
```
0x3500 Main module type
0x3502 CH expansion module type
0x350B Profile number
        |
        v
wybór wariantu wewnętrznego obiektu
```

### Warstwa funkcjonalnej konfiguracji instalacji
```
0x2105 Heating configuration
0x2106 Hot water configuration
0x2107 Buffer configuration
0x2108 Solar configuration
```

Dla 0x2106..0x2108 mamy dodatkowy dowód z kodu projektu: są częścią listy `kConf` używanej przez silnik odczytu konfiguracji.

Co ciekawe, `0x2105` nie występuje w tej liście `kConf`. To oznacza, że jego rola może być obsługiwana inną ścieżką firmware/panelu i trzeba ją jeszcze znaleźć.

## 7. Dlaczego to jest istotne

Mamy teraz trzy niezależne poziomy, które można połączyć dopiero po dalszym trace:

```
[CONFIGURACJA MODUŁÓW]
0x3500 / 0x3502 / 0x350B
          |
          v
[WARIANT OBIEKTU / ZESTAW STRUKTUR]
          |
          v
[INSTANCJE MODUŁÓW]
module + 0x12C = 1..4
          |
          v
base_index + instance - 1
          |
          v
0x2032..0x2035 / 0x2048..0x204B / ...
```

Osobno istnieje:

```
[CONFIGURACJA INSTALACJI]
0x2105 / 0x2106 / 0x2107 / 0x2108
```

Następny cel to znalezienie miejsca, które spina te dwie warstwy.

## 8. Następny trace

Priorytet:

1. znaleźć inicjalizację/zapis pól `object+0x16BF`, `+0x16C0`, `+0x16CC`;
2. znaleźć kod odpowiadający za `Autoconfig activation` 0x3501;
3. znaleźć ścieżkę `0x2105` mimo braku literalnej stałej w dekompilacji;
4. sprawdzić, czy wybór wariantu prowadzi do tworzenia/aktywacji obiektów CO;
5. połączyć wybór wariantu z `module+0x12C`;
6. dopiero wtedy określić, czy `0x2105` oznacza bezpośrednio liczbę aktywnych obiegów 1..4, czy wariant instalacji.

## Status

**UDOWODNIONE:** 0x3500 + 0x3502 + 0x350B uczestniczą w realnym wyborze wariantu konfiguracji obiektu.

**UDOWODNIONE:** 0x3500 i 0x3502 są mapowane bezpośrednio na pola obiektu `+0x16BF/+0x16C0`.

**BARDZO PRAWDOPODOBNE:** Main I/O / BIG jest nadrzędnym wariantem sprzętowym, a expansion module zmienia dostępny zestaw konfiguracji.

**NIEUDOWODNIONE:** dokładne znaczenie wartości 0..4 w 0x2105 oraz bezpośrednie połączenie 0x2105 -> liczba instancji CO.
