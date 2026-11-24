# PASS 71 — Tabela 23: domknięcie znaczenia przez caller FUN_080144E4

## Streszczenie

Dalszy statyczny ślad zamknął wcześniejszą hipotezę o znaczeniu tabeli `0x20008C50`.

Kluczowy dowód:

- `FUN_080144E4` ma caller w PROJECT `0x0805F612`.
- W tym callerze wcześniej wykonywane jest `ldr.w r10,[pc,#...]` z literałem PROJECT `0x0805F820`.
- Pod `0x0805F820` znajduje się **`0x20021FA0`**, czyli dokładnie blok ustawień zawierający PID `0x0004`.
- Następnie caller wykonuje `ldrh.w r0,[r10,#0x1A]`, czyli czyta **`[0x20021FA0+0x1A] = 0x20021FBA`**.
- `0x20021FBA` jest storage PID **0x0004 "Parameters set Number"**, u16, default 10.
- Ten u16 jest przekazywany do `FUN_080144E4`.
- `FUN_080144E4` szuka wartości w tej samej 23-elementowej tablicy co `FUN_080144B4` i zwraca pole `+0x0C` znalezionego rekordu.

To jest bezpośredni dowód, że 23-rekordowy katalog jest powiązany z **Parameters set Number**, a nie tylko hipotetycznym katalogiem mocy kotła.

## Dowód bajtowy

### Caller

PROJECT `0x0805F5D8..0x0805F612`:

- `0x0805F5D8`: `ldr.w r10,[pc,#0x244]`
- literal: `0x0805F820 = 0x20021FA0`
- `0x0805F60E`: `ldrh.w r0,[r10,#0x1A]`
- `0x0805F612`: `bl 0x080144E4`

Zatem:

`r10 = 0x20021FA0`

`r10+0x1A = 0x20021FBA`

`[r10+0x1A] = Parameters set Number (PID 0x0004)`.

### Lookup

PROJECT `0x080144E4` jest funkcją "find object by value" dla tego samego rejestru 23 rekordów:

- korzysta z bazy `0x20008C50`;
- porównuje wartość rekordu `[record+8]`;
- po trafieniu zwraca pole `[record+0xC]`.

`FUN_080144B4` używa tej samej tablicy jako predykatu membership i zwraca 1/0.

## Znaczenie tabeli

### FACT

23 rekordy są katalogiem wartości używanych dla **Parameters set Number (PID 0x0004)**.

To wyjaśnia, dlaczego wpisanie jednej z tych wartości do PIN powoduje przejście przez ten sam lookup: handler PIN współdzieli katalog "parameter set number" z ogólnym mechanizmem wyszukiwania obiektu.

### STRONG

Mechanizm PIN nie tworzy osobnego zestawu 23 kodów serwisowych. Reagowanie na 23 wartości jest **efektem współdzielenia katalogu Parameters set Number**.

To bardzo dobrze odpowiada wcześniejszej obserwacji: tabela 23 jest używana także przez zwykły kod UI, a nie wyłącznie przez handler PIN.

### INFERENCE

Pole `record+0xC` prawdopodobnie wskazuje drugi atrybut/obiekt związany z numerem zestawu parametrów. Nie nadaję mu jeszcze nazwy biznesowej.

## 23. wartość

Nadal **OPEN**.

Powód jest techniczny: baza `0x20008C50` znajduje się w SRAM inicjalizowanym z obrazu IAR/LZ77. Surowy BIN nie zawiera tej tablicy wprost pod adresem `0x20008C50`.

Nie zgaduję 23. wartości na podstawie podobieństwa liczbowego.

## Konsekwencja dla A1

A1 można uznać za statycznie domknięte:

- stały kod 1992,
- stały kod 6666,
- stały kod 0,
- oraz **23 wartości Parameters set Number**, które trafiają w wspólny lookup.

Nie ma dowodu na dodatkową, niezależną rodzinę ukrytych PIN-ów w tym handlerze.

## FACT / STRONG / INFERENCE / OPEN / REJECTED

### FACT
- `0x20021FBA` = storage PID `0x0004 Parameters set Number`.
- Caller `0x0805F612` przekazuje ten u16 do `FUN_080144E4`.
- `FUN_080144E4` i `FUN_080144B4` używają tej samej 23-elementowej tablicy `0x20008C50`.

### STRONG
- 23 wartości są katalogiem dozwolonych/znanych numerów zestawów parametrów.
- PIN lookup jest współdzielonym mechanizmem, nie osobnym katalogiem kodów.

### INFERENCE
- `record+0xC` jest drugim polem obiektu zestawu parametrów.

### OPEN
- 23. wartość.
- Semantyka `record+0xC`.
- Czy każdy numer zestawu ma związaną konfigurację, nazwę lub identyfikator modelu.

### REJECTED
- "23 liczby = bezpośrednio moce kotłów" — odrzucone jako zbyt mocna interpretacja. Mogą korelować z modelami/mocami, ale dowód bezpośredni mówi o **Parameters set Number**.
