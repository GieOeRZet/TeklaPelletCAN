# FW2213TK — znalezienie nadrzędnej konfiguracji liczby obwodów CO

Data: 2026-11-19

## Przełom

W dokumentacji producenta menu instalatora zawiera pozycję „Ilość obwodów grzewczych”. Instrukcja opisuje ją wprost jako parametr określający ilość obwodów CO. Jednocześnie firmware FW2213TK zawiera parametr:

- CAN/SDO index: 0x2105
- nazwa firmware: Heating configuration
- typ: u8
- zakres: 0..4
- domyślna wartość: 1
- dostęp: nastawa
- lokalny storage: 0x20021FAF
- adres wpisu w mapie parametrów: 0x0801A5B0

W tabeli snapshotów wartość panela wynosi 257, czyli w używanym przez panel kodowaniu 0x100 + wartość daje 1.

To jest obecnie najlepszy kandydat na firmware'owy odpowiednik pozycji „Ilość obwodów grzewczych”.

## Ważne rozdzielenie

Nie należy utożsamiać tego z 0x3502.

0x3502 ma nazwę CH expansion module type, typ u8, zakres 0..1, storage 0x20021FAC. Jest osobnym parametrem opisującym typ modułu rozszerzenia CO.

Natomiast 0x2105 ma zakres 0..4 i nazwę Heating configuration, co znacznie lepiej pasuje do liczby aktywnych obwodów.

Powstaje więc model:

    menu Konfiguracja
          |
          +-- Ilość obwodów grzewczych
          |        |
          |        v
          |     0x2105
          |        |
          |        v
          |   0..4 aktywnych CO
          |
          +-- Główny moduł IO
          +-- Autokonfiguracja
          +-- CWU
          +-- Bufor
          +-- Solary
          +-- Numer profilu

## Powiązanie z odkrytym mechanizmem instancji

Mamy już niezależnie potwierdzone:

    CO1..CO4
       |
       +-- indeksy 0x2032..0x2035
       |
       +-- wspólny storage/deskryptor rodziny
       |
       +-- moduł +0x12C = instancja 1..4
       |
       +-- dynamiczne base + instance - 1
       |
       +-- lookup 0x1167A / zapis 0x11812

Naturalny następny trace:

    0x2105
      |
      +--> kod reagujący na konfigurację
      |
      +--> ustalenie liczby aktywnych instancji
      |
      +--> konfiguracja obiektów/modułów CH
      |
      +--> +0x12C
      |
      +--> widoczność Ogrzewanie 1..4
      |
      +--> lookup parametrów konkretnego obwodu

## Co jest już mocne, a czego jeszcze nie twierdzimy

Mocne:
- producent opisuje „Ilość obwodów grzewczych” jako konfigurację liczby CO;
- FW ma osobny parametr 0x2105 o zakresie 0..4 i nazwie Heating configuration;
- 0x2105 ma własny storage 0x20021FAF;
- firmware ma jawne cztery etykiety Ogrzewanie obwód 1..4;
- firmware ma mechanizm instancji 1..4 i dynamiczne indeksowanie.

Jeszcze do udowodnienia z kodu:
- dokładna semantyka wartości 0/1/2/3/4 dla 0x2105;
- funkcja, która odczytuje 0x20021FAF i na tej podstawie ogranicza liczbę aktywnych obwodów;
- dokładne miejsce, w którym ta wartość wpływa na UI;
- czy wartość 4 oznacza bezpośrednio cztery obwody, czy konfigurację wariantu obejmującego cztery obwody.

## Kierunek dalszego reverse engineeringu

Nie szukamy już „jak działa CO2”.

Szukamy teraz fan-outu 0x2105:

    0x2105 / 0x20021FAF
            |
       wszystkie odczyty
            |
       funkcje warunkowe
            |
       konfiguracja CH
            |
       UI / moduły / instancje
            |
       Ogrzewanie 1..4

Jeżeli znajdziemy ten fan-out, dostaniemy prawdopodobnie nadrzędny mechanizm konfiguracji całego panelu, a nie tylko mechanizm CO.
