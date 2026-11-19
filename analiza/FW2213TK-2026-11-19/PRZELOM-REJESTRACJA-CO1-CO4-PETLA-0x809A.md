# FW2213TK — przełom: statyczna rejestracja czterech instancji w pętli, 2026-11-19

## Kluczowe odkrycie

W funkcji rejestrującej parametry znajduje się pętla:
- raw 0x809A: r7 = 0
- raw 0x8254: r1 = r7 + 0x2000 + 0x32
- raw 0x825E: BL 0x1143C
- dalej analogiczne rejestracje używają tego samego r7,
- raw 0x9890: r7++
- raw 0x9894: porównanie z 4
- powrót do początku pętli.

### Zatem firmware faktycznie rejestruje 4 instancje

Dla pierwszego parametru: r7=0 -> 0x2032, r7=1 -> 0x2033, r7=2 -> 0x2034, r7=3 -> 0x2035.
Dla kolejnego: 0x2048..0x204B.
Dla trybu CO: 0x2064..0x2067.

To jest [FW] bezpośredni dowód, że rekordy CO2/CO3/CO4 są tworzone w głównej tablicy rekordów przez wywołania 0x1143C. Nie są tworzone dopiero przez runtime lookup.

## Najważniejsza konsekwencja

W tej samej pętli dla 0x2032:
- r2 = r5 + 0x70
- wcześniej r5 = r4 + 0x08
- r4 = 0x200208EC
- więc r5 = 0x200208F4
- r2 = 0x20020964.

Co ważne: w tej rejestracji r2 NIE zawiera +r7.

Cztery rekordy 0x2032, 0x2033, 0x2034, 0x2035 są rejestrowane z tym samym źródłem 0x20020964.
Analogicznie: 0x2048..0x204B -> 0x20020966, a 0x2064..0x2067 -> 0x2002096E.

## Interpretacja

To bardzo mocno sugeruje, że adresy z CSV (0x20020964 itd.) nie są osobnymi RAM-ami CO1/CO2/CO3/CO4.
Są wspólnymi buforami/zmiennymi parametrów używanymi przez panel dla całej rodziny indeksów. Indeks CAN wybiera instancję, natomiast lokalny storage panelu może być wspólny.

To tłumaczy, dlaczego nie dało się znaleźć CO2_RAM = CO1_RAM + stride.

## Korekta wcześniejszego dokumentowania

Wcześniejsze stwierdzenie, że nie znaleziono statycznej rejestracji 0x2033 było prawdziwe tylko dla wyszukiwania literalnych movw #0x2033. Pełny kod pokazuje, że 0x2033 powstaje jako 0x2032 + r7 w pętli rejestracyjnej.

Również wcześniejsza interpretacja record+0x0C jako deskryptora była błędna. record+0x0C = r2 jest przechowywany bezpośrednio, a 0x14728 kopiuje 5-bajtowe deskryptory do pól +0x14/+0x1C/+0x24.

## Nowy model

base parameter -> registration loop r7=0..3 -> CAN index = base + r7 -> record+0x0C = wspólny lokalny storage parametru -> runtime lookup wybiera rekord na podstawie base + instance - 1.

To jest obecnie znacznie pełniejszy i spójny model obsługi CO1–CO4.