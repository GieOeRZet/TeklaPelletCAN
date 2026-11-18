# FW2213TK — mechanizm mapowania indeksu parametru / instancji

Data: 2026-11-19

## Najważniejsze odkrycie

W firmware istnieje rzeczywista funkcja raw 0x36FF2 (runtime 0x08046FF2), która dostaje r0 = kontekst obiektu, r1 = indeks parametru, wyszukuje indeks w dwóch tabelach Flash i zwraca panelowy numer/slot z korektą zależną od bajtu obiektu +0x12C.

To jest kod z firmware, nie domysł.

## Mechanizm 0x36FF2

Funkcja 0x36FF2:
- 0x36FF8 zachowuje indeks z r1
- 0x36FFA pobiera kontekst przez 0x314BA
- 0x36FFE odczytuje context + 0x12C
- 0x37002 rozpoczyna wyszukiwanie w tabeli pod 0x37B46
- po znalezieniu odczytuje drugie pole, dodaje context[0x12C] i odejmuje 1
- jeśli nie znajdzie wpisu w tabeli specjalnej, przeszukuje drugą tabelę pod 0x37572.

Wzór wynikający bezpośrednio z kodu:

wynik = panel_slot_z_tabeli + context[0x12C] - 1

## Tabela specjalna — raw 0x37B46

49 wpisów po 4 bajty, format: int16 indeks_parametru + uint16 panel_slot.

| CAN index | panel slot |
|---:|---:|
| 0x2065 | 168 |
| 0x22FD | 169 |
| 0x2032 | 170 |
| 0x2048 | 171 |
| 0x2166 | 172 |
| 0x2064 | 191 |
| 0x2126 | 192 |
| 0x212A | 193 |
| 0x212E | 194 |
| 0x2132 | 195 |
| 0x2136 | 196 |
| 0x213A | 197 |
| 0x213E | 201 |
| 0x2299 | 202 |
| 0x22B9 | 198 |
| 0x2016 | 199 |
| 0x4001 | 178 |
| 0x22A5 | 176 |
| 0x22A1 | 200 |
| 0x22AD | 174 |
| 0x22B1 | 188 |
| 0x2146 | 175 |
| 0x2142 | 325 |
| 0x22DD | 326 |
| 0x22C9 | 190 |
| 0x22BD | 177 |
| 0x22C1 | 180 |
| 0x22C5 | 181 |
| 0x400C | 182 |

## Druga tabela — raw 0x37576

420 wpisów, format uint16 CANopen_index + uint16 panel_id. To jest znana już wcześniej tabela mapowania.

Sprawdzone w binarce:
- 0x2032 -> 170
- 0x2048 -> 171
- 0x2064 -> 191
- 0x2065 -> brak w tabeli 420 rekordów, ale występuje w tabeli specjalnej jako 168
- 0x4001 -> 178
- 0x400C -> 182

## Co to daje dla CO1 / CO2

To jest pierwszy twardy mechanizm pokazujący, że firmware może używać jednego wpisu bazowego dla rodziny parametrów, a numer instancji uwzględniać przez context+0x12C.

Przykład: 0x2032 ma bazowy panel slot 170, a kod wykonuje korektę 170 + context[0x12C] - 1.

To bardzo mocno łączy mechanizm firmware z wcześniej znalezionym count=4 dla parametrów obwodów.

## Ważna granica dowodu

Nie wolno jeszcze pisać: CO2 RAM = CO1 RAM + stały stride.

Udowodniliśmy natomiast:
1. firmware ma jawny mechanizm indeks -> panel slot,
2. mechanizm używa context+0x12C jako korekty instancji,
3. parametr bazowy może być reprezentowany jednym wpisem tabeli, a numer instancji jest uwzględniany w kodzie,
4. tabela 0x37B46 zawiera rzeczywiste indeksy parametrów CO i ich sloty,
5. tabela 0x37576 zawiera drugi, 420-elementowy poziom mapowania.

## Następny krok

Teraz trzeba prześledzić pełny łańcuch: CAN index -> panel slot -> odczyt/zapis wartości -> konkretna lokalizacja RAM.

Najważniejsze funkcje do dalszej analizy: 0x1167A, 0x14728, 0x14734, rodzina 0x2D3xx/0x2D4xx/0x2D7xx/0x2D8xx/0x2DBxx oraz struktura obiektu zwracana przez 0x314BA.

### Status
- [FW] 0x36FF2 jest funkcją mapowania indeksu.
- [FW] 0x37B46 = 49-entry special mapping.
- [FW] 0x37576 = 420-entry mapping.
- [FW] context+0x12C wpływa na wynik mapowania.
- [INFERENCJA] +0x12C jest selektorem instancji obwodu/parametru; dokładna nazwa pola nadal do potwierdzenia.
- [NIEUDOWODNIONE] stały offset RAM pomiędzy CO1 i CO2.