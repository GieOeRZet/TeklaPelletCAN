# BATCH — granica 0x2105 vs warstwa modułów i znaczenie count=4
Data: 2026-11-19

## 1. Najważniejsza korekta modelu: panel FW nie musi tworzyć obiegów

**UDOWODNIONE**

Badany obraz `FW2213TK.bin` jest firmware panela IgneoTouch. Jego mechanizm:
- rejestruje parametry CANopen,
- mapuje indeks -> lokalny storage,
- obsługuje obiekty/instancje używane przez panel,
- wybiera warianty sprzętowe panela na podstawie `0x3500/0x3502/0x350B`.

Dlatego brak kodu typu:
`read 0x2105 -> create N circuits`
nie jest już dziwny.

`0x2105` może być parametrem **konfiguracji systemu przekazywanym przez CAN**, podczas gdy obiekty panelu są tworzone/konfigurowane na podstawie osobnej warstwy identyfikacji modułów.

To oznacza, że wcześniejsze założenie „musimy znaleźć w tym firmware bezpośrednie użycie 0x2105 do utworzenia +0x12C” było zbyt restrykcyjne.

## 2. 0x2105 ma bardzo mocną semantykę funkcjonalną

**BARDZO PRAWDOPODOBNE**

Mamy jednocześnie:
- parametr `0x2105` = `Heating configuration`,
- typ u8,
- zakres 0..4,
- domyślna wartość 1,
- własny storage panela `0x20021FAF`,
- cztery jawne etykiety `Ogrzewanie obwód 1..4`,
- cały zestaw parametrów CO oznaczony `count=4`,
- dynamiczny mechanizm instancji 1..4.

To jest bardzo silna korelacja z konfiguracją liczby lokalnych obiegów CO.

## 3. count=4 oznacza pojemność mechanizmu, nie liczbę aktywnych obiegów

**UDOWODNIONE**

Dla przykładowego:
`0x2032`
firmware ma:
`0x2032, 0x2033, 0x2034, 0x2035`

Analogicznie:
`0x2142 -> 0x2142..0x2145`

i dla dużej grupy parametrów CO:
- 0x22xx,
- 0x4001,
- 0x400C,
- nazwy obwodów 0x2321/2325/2329

katalog wskazuje `count=4`.

To znaczy:
**firmware panela ma model danych dla maksymalnie 4 instancji tego typu.**

Nie wynika z tego, że wszystkie cztery są aktywne.

## 4. Manual daje niezależny dowód, że CO2..CO4 są zależne od rozbudowy

**UDOWODNIONE z dokumentacji Estyma**

W analizowanej instrukcji:
- podstawowy system ma obwód CO1,
- moduł rozszerzeniowy nr 0 obsługuje trzy kolejne obwody: CO2, CO3, CO4,
- konfiguracja systemu zawiera parametr „Liczba obwodów CO”,
- możliwość konfiguracji jest uzależniona od liczby skonfigurowanych modułów rozszerzeniowych.

To jest dokładnie zgodne z obserwowanym w firmware rozdziałem:
`Main module` + `CH expansion module`.

Czyli strukturalnie mamy:

```
MAIN / BIG
  |
  +-- CO1
  |
  +-- expansion
        |
        +-- CO2
        +-- CO3
        +-- CO4
```

Nie twierdzimy jeszcze, że współczesna wersja FW2213TK implementuje identyczną fizyczną mapę jak stara instrukcja, ale architektura jest bardzo silnie zgodna.

## 5. 0x3502 jest bardzo prawdopodobnym wskaźnikiem właśnie tej granicy sprzętowej

**BARDZO PRAWDOPODOBNE**

`0x3502 = CH expansion module type` ma wartości 0/1.

W kodzie wybór wariantu dla Main=0 rozdziela się:

bez expansion:
- profile 1 -> wariant 2
- profile 2 -> wariant 3
- profile 3 -> wariant 4

z expansion:
- profile 1 -> wariant 5
- profile 2 -> wariant 6
- profile 3 -> wariant 7

To oznacza, że obecność expansion module zmienia cały zestaw struktur używany przez panel.

To jest dokładnie taki mechanizm, którego należałoby oczekiwać, jeśli dodatkowe obwody CO wymagają dodatkowego I/O.

## 6. +0x12C nie jest „liczbą obwodów”

**UDOWODNIONE**

`module+0x12C` przechowuje numer konkretnej instancji:
1, 2, 3 albo 4.

To jest selektor:
```
obiekt CO
   |
   +-- +0x12C = 1 -> indeks bazowy + 0
   +-- +0x12C = 2 -> indeks bazowy + 1
   +-- +0x12C = 3 -> indeks bazowy + 2
   +-- +0x12C = 4 -> indeks bazowy + 3
```

Liczba aktywnych obwodów musi więc być czymś nadrzędnym wobec samego selektora instancji.

## 7. Mamy teraz dwie różne osie konfiguracji

**UDOWODNIONE**

### Oś sprzętowa
```
0x3500 Main module type
0x3502 CH expansion module type
0x350B Profile number
+0x16C1 / +0x16D5
        |
        v
wariant sprzętowy / zestaw struktur
```

### Oś funkcjonalna
```
0x2105 Heating configuration
0x2106 Hot water configuration
0x2107 Buffer configuration
0x2108 Solar configuration
        |
        v
konfiguracja systemu grzewczego
```

I właśnie dlatego nie musimy już na siłę szukać jednego miejsca, w którym `0x2105` tworzy obiekty.

## 8. Nowa granica poszukiwań

Zamiast:
`0x2105 -> +0x12C`

szukamy teraz:

```
0x2105
  |
  v
konfiguracja systemu / liczba aktywnych CO
  |
  +--------------------+
  |                    |
  v                    v
warstwa modułów     widoczność/UI
  |                    |
  v                    v
CO1..CO4             Ogrzewanie obwód 1..4
  |
  v
+0x12C = konkretny numer instancji
  |
  v
base index + instance - 1
  |
  v
0x1167A
```

To jest obecnie znacznie bardziej spójny model niż wcześniejsze bezpośrednie `2105 -> create object`.

## 9. Szczególnie ważna konsekwencja dla naszego emulatora

Jeżeli chcemy odtworzyć panel, **nie należy traktować count=4 jako czterech zawsze aktywnych CO**.

Powinniśmy rozdzielić:
- `co_capacity = 4`,
- `co_count = wartość konfiguracji systemu`,
- `co_instance = 1..4`.

Wtedy:
- parametr `0x2032` + instance 1 = CO1,
- `0x2032` + instance 2 = CO2,
- itd.,
ale panel może pokazywać tylko instancje 1..`co_count`.

## Status po tym batchu

**UDOWODNIONE**
- count=4 = mechanizm czterech instancji.
- +0x12C = numer konkretnej instancji.
- 0x2105 = Heating configuration, 0..4.
- 0x3502 = CH expansion module type.
- expansion zmienia cały wariant sprzętowy.
- dokumentacja opisuje CO1 jako podstawowy obieg oraz CO2..CO4 jako obwody związane z modułem rozszerzeniowym.

**BARDZO PRAWDOPODOBNE**
- 0x2105 odpowiada funkcjonalnie za liczbę aktywnych lokalnych obiegów CO.
- 0x3502 jest sprzętowym warunkiem dostępności dodatkowych CO.
- liczba aktywnych instancji i pojemność mechanizmu są dwiema różnymi rzeczami.

**Nadal otwarte**
- dokładny kod, którym panel interpretuje wartość 0x2105,
- dokładne znaczenie wartości 0 w 0x2105,
- czy w FW2213TK wartość 2/3/4 jest ograniczana przez 0x3502,
- gdzie dokładnie powstają/uzyskują kontekst obiekty CO2..CO4.
