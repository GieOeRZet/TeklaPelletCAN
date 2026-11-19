# 2026-11-19 — DYNAMICZNA INSTANCJA CO: źródło numeru instancji i granica dowodu

## Cel

Sprawdzono dalszy przepływ dla mechanizmu:

`base_index + instance - 1 -> lookup w tabeli rekordów`

oraz skąd bierze się `instance`. Jednocześnie sprawdzono, czy tabela rekordów `0x20008D84` jest statycznie rozszerzana dla instancji 2–4.

---

## 1. `0x200248D4` NIE jest tabelą rekordów

W kodzie przy runtime `0x080470C0` (raw `0x370C0`) firmware ładuje:

- `r6 = 0x200248D4`
- `[r6+0] =` flaga inicjalizacji
- `[r6+1] =` numer instancji.

To jest mały globalny stan pomocniczy.

Natomiast `r8` ładowany z literal pool `raw 0x3754C` ma wartość:

`0x20008D84`

i właśnie ten adres jest przekazywany do `0x0802167A` jako baza tabeli rekordów.

Czyli wcześniejsze potencjalne utożsamianie `0x200248D4` z tabelą rekordów było błędne.

---

## 2. Dynamiczny lookup jest bezpośrednio potwierdzony w firmware

Raw `0x370E8..0x37100`:

- `r0 = table_entry.base_index`
- `r1 = [0x200248D4 + 1] = instance`
- `r0 += r1`
- `r2 = r0 - 1`
- `uxth r2`
- `r1 = 0x20008D84`
- `BL 0x1167A`

Czyli dokładna formuła z firmware:

`lookup_index = base_index + instance - 1`

Przykłady:

- base `0x2032`, instance 2 -> `0x2033`
- base `0x2048`, instance 2 -> `0x2049`
- base `0x2064`, instance 2 -> `0x2065`
- base `0x4001`, instance 2 -> `0x4002`

To jest fakt z kodu, nie hipoteza.

---

## 3. Tabela pomocnicza przy `0x37B44` wiąże identyfikator panelowy z bazowym CAN indeksem

Początek tabeli:

| raw | pierwsze pole | drugi uint16 |
|---|---:|---:|
| 0x37B44 | 215 | 0x2065 |
| 0x37B48 | 168 | 0x22FD |
| 0x37B4C | 169 | 0x2032 |
| 0x37B50 | 170 | 0x2048 |
| 0x37B54 | 171 | 0x2166 |
| 0x37B58 | 172 | 0x2064 |
| 0x37B5C | 191 | 0x2126 |
| 0x37B60 | 192 | 0x212A |
| 0x37B64 | 193 | 0x212E |
| 0x37B68 | 194 | 0x2132 |
| 0x37B6C | 195 | 0x2136 |
| 0x37B70 | 196 | 0x213A |
| 0x37B74 | 197 | 0x213E |

Repo mapa panel-ID potwierdza m.in.:

- ID 168 -> `0x2065` = Tryb CO 2
- ID 169 -> `0x22FD`
- ID 170 -> `0x2032` = CO temperatura komfort
- ID 171 -> `0x2048` = CO temperatura eko
- ID 172 -> `0x2166`
- ID 191 -> `0x2064` = Tryb CO 1

Nie należy jednak automatycznie zakładać, że pierwsze pole każdej pozycji tej tabeli jest zawsze klasycznym panel-ID — jej rola jest potwierdzona dla tych konkretnych korelacji, ale cała semantyka tabeli wymaga dalszego śledzenia.

---

## 4. Skąd bierze się numer instancji?

Globalny obiekt zwracany przez `0x080314BA` znajduje się pod:

`0x20024814`

Funkcja `0x080314BA`:

- ładuje `0x20024814`
- zwraca zawartość tego globalnego wskaźnika.

Kod w `0x080470C0` pobiera z tego obiektu:

`[object + 0x12C]`

i zapisuje do:

`[0x200248D4 + 1]`

To pole `+0x12C` jest więc źródłem numeru instancji używanego później przez dynamiczny lookup.

---

## 5. Numer instancji 1..4 jest ustawiany przez kod konfiguracji modułu

Najważniejszy nowy dowód: runtime `0x08048130` (raw `0x38130`) ustawia:

`[module_object + 0x12C] = instance`

Przyjmuje parametr `r1` i normalizuje go do zakresu 1..4.

Dodatkowo runtime `0x0803C0B6` (raw `0x3C0B6`) wybiera jawnie:

- `r1 = 1`
- `r1 = 2`
- `r1 = 3`
- `r1 = 4`

i kończy przez branch do `0x38130`.

Jest też kod w okolicy raw `0x3212C`, który:

- sprawdza parametr `0x10E`,
- jeśli dostępna jest instancja 1, wywołuje `38130` z `r1=1`,
- jeśli dostępna jest instancja 2, wywołuje `38130` z `r1=2`.

To jest bezpośredni dowód, że firmware ma rzeczywisty mechanizm tworzenia/konfiguracji modułów dla instancji 1..4.

---

## 6. Co wiemy o rekordach tabeli `0x20008D84`

Funkcja rejestrująca `0x0802143C`:

- baza tabeli = `r0`
- CAN/index = `r1`
- źródło wartości = `r2`
- typ/metadata = `r3`

Rekord ma dokładnie `0x2C` bajtów.

Pola potwierdzone:

- `record + 0x08` = CAN/index
- `record + 0x0C` = źródło wartości przekazane przez caller
- `record + 0x10` = typ byte
- `record + 0x14`, `+0x1C`, `+0x24` = struktury/metadane tworzone przez `0x14728`

Funkcja `0x0802167A` przeszukuje cztery kolejne rekordy:

- `+0x00`
- `+0x2C`
- `+0x58`
- `+0x84`

czyli dokładnie cztery rekordy po `0x2C`.

---

## 7. Ważna granica: nie znaleziono jeszcze statycznego rejestrowania 0x2033/34/35

W głównej funkcji rejestracji (raw około `0x1CE8`) jest dokładnie 448 wywołań `0x1143C`.

Dla CO1 potwierdziliśmy bezpośrednio m.in.:

- `0x2032 -> 0x20020964`
- `0x2048 -> 0x20020966`
- `0x2064 -> 0x2002096E`
- `0x2166 -> 0x20020968`

Nie znaleziono w tej statycznej ścieżce literalnych rejestracji:

- `0x2033`
- `0x2034`
- `0x2035`
- `0x2049`
- `0x204A`
- `0x204B`

i analogicznych indeksów instancji.

To jest istotne: nie wolno obecnie twierdzić, że CO2 RAM jest po prostu CO1 RAM + stały stride.

Najbardziej prawdopodobna granica do dalszego śledzenia to runtime'owe tworzenie/uzupełnianie rekordów instancji przez mechanizm modułów, a nie statyczna lista 448 rejestracji.

---

## 8. Nowy model przepływu

Aktualnie mamy następujący łańcuch potwierdzony kodem:

`panel/module instance`
-> obiekt modułu
-> `object + 0x12C`
-> global `0x200248D4+1`
-> `instance`

równolegle:

`panel parameter ID`
-> tabela `0x37B44...`
-> `base CAN index`

następnie:

`base CAN index + instance - 1`
-> `lookup 0x0802167A`
-> tabela rekordów `0x20008D84`
-> odpowiedni rekord `0x2C`

To jest obecnie najmocniejszy model mechanizmu indeksowania.

---

## 9. Następny krok analizy

Nie będziemy już szukać tylko literalnych `0x2033` itd.

Następny cel to znaleźć kod, który przy utworzeniu/wykryciu kolejnej instancji:

1. tworzy lub klonuje rekord `0x2C`,
2. wpisuje do `record+0x08` indeks wynikający z `base + instance - 1`,
3. wiąże `record+0x0C` z właściwym RAM-em instancji,
4. oraz określa kolejność rekordów 1..4.

Dopiero ten krok pozwoli bez domysłów wyprowadzić dokładne RAM-y CO2/CO3/CO4.
