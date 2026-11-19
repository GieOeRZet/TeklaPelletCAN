# FW2213TK — architektura wartości parametrów instancjonowanych CO1–CO4

## 1. Dowód z firmware

Rejestracja parametrów odbywa się w pętli `r7=0..3`.
For base 0x2032 firmware calls 0x1143C with CAN index `0x2032 + r7`.
For base 0x2048: `0x2048 + r7`.
For base 0x2064: `0x2064 + r7`.

Najważniejsze: argument `r2` przekazywany do 0x1143C nie zależy od `r7`.

Przykłady z kodu:
- 0x2032..0x2035 -> r2 = 0x20020964
- 0x2048..0x204B -> r2 = 0x20020966
- 0x2064..0x2067 -> r2 = 0x2002096E

## 2. Co robi 0x1143C

0x1143C zapisuje:
- `record+0x08 = CAN/index`
- `record+0x0C = r2`
- `record+0x14`, `+0x1C`, `+0x24` = trzy 5-bajtowe deskryptory/metadane
- `record+0x10 = typ`.

0x14728 kopiuje 5 bajtów deskryptora. 0x14734 odczytuje wartość z deskryptora według typu.

## 3. Dowód, że +0x0C jest właściwym lokalnym storage

0x11812 wyszukuje rekord po CAN/index. Następnie:
- `r7 = record + 0x0C`
- odczytuje typ z `record+0x10`
- dla typu 1/2/3/4/5 zapisuje nową wartość pod adresem wskazanym przez `[record+0x0C]`.

Zatem dla 0x2032..0x2035 wszystkie cztery rekordy wskazują ten sam adres lokalny 0x20020964.

## 4. Jeszcze mocniejszy dowód: inicjalizacja

0x115BC przechodzi przez 0x294 rekordów. Dla każdego pobiera deskryptor z `record+0x24` przez 0x1155A, a następnie przekazuje tę wartość do 0x11812.

To oznacza, że `record+0x24` jest używany jako wartość inicjalizacyjna/resetowa, natomiast `record+0x0C` jest miejscem bieżącej wartości lokalnej.

## 5. Wniosek architektoniczny

Panel nie musi przechowywać czterech niezależnych kopii bieżącej wartości parametru CO. Dla rodziny instancji może mieć jeden lokalny cache/working value, podczas gdy numer CAN 0x2032/0x2033/0x2034/0x2035 identyfikuje instancję po stronie modułu.

Model:

CAN index 0x2032..0x2035
        |
        v
record[instance]  (osobny rekord 0x2C)
        |
        +--> +0x0C ----+
                      |
                      v
                 wspólny RAM
                 0x20020964

To nie jest już hipoteza oparta wyłącznie na podobieństwie adresów: wspólność wskaźnika `record+0x0C` wynika bezpośrednio z kodu rejestracji.

## 6. Mechanizm wyboru instancji

Funkcje 0x370C0/0x37172 i 0x37212 pobierają numer instancji z pola modułu `+0x12C` i obliczają:
`index = base_index + instance - 1`.

0x37212 następnie przekazuje obliczony indeks do 0x11812, więc aktualizacja parametru dla CO2 trafia do rekordu 0x2033, ale rekord ten wskazuje ten sam lokalny working storage.

## 7. Znaczenie dla dalszego reverse engineeringu

Najważniejszym kolejnym celem nie jest już szukanie osobnego RAM-u `CO2 = CO1 + stride`.
Należy znaleźć ścieżkę, która przy zmianie/odczycie aktywnego obwodu pobiera wartość z modułu po CAN i ładuje ją do wspólnego working storage panelu.

To powinno połączyć trzy warstwy:
1. CAN index 0x2032/0x2033/...
2. moduł/instancję wskazywaną przez `+0x12C`
3. lokalny cache używany przez UI.

### Status
- [FW] CO1–CO4 są rejestrowane jako osobne indeksy CAN.
- [FW] rekord ma 0x2C bajta.
- [FW] `record+0x0C` wskazuje lokalne storage.
- [FW] dla pokazanych rodzin CO1–CO4 wszystkie instancje wskazują ten sam lokalny storage.
- [FW] wybór instancji odbywa się przez `base_index + instance - 1`.
- [DO ZNALEZIENIA] dokładna ścieżka odczytu wartości instancji z magistrali CAN do wspólnego working storage.