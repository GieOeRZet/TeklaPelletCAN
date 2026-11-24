# NewEstyma — RECORD ENGINE CROSS-LAYER CLOSURE 02 — 2026-11-22

Firmware: `FW2213TK_kopia.bin`
SHA-256: `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`
Branch: `ccr-be8a1bcb-5t76j0`

## Cel makro-pass

Domknąć to, co można obecnie udowodnić o rejestracji, rekordzie 0x2C, getterach/inicjalizacji i relacji z instancjami CO1..CO4, bez ponownego używania odrzuconych pól +0x2C/+0x30.

## 1. HARD — geometria runtime

W ścieżce głównej parametr engine:

`record(index) = 0x20008D84 + index * 0x2C`

`FUN_080115F6`:
- porównuje PID jako u16 z `record+0x08`,
- przechodzi do kolejnego rekordu krokiem `0x2C`,
- ma limit skanowania `0x294 = 660`,
- po znalezieniu rekordu dereferencjonuje `record+0x0C`,
- odczytuje typ z `record+0x10`.

Potwierdzone geometrycznie:
- +0x2C = następny rekord,
- +0x58 = rekord + 2*0x2C,
- +0xB0 = rekord + 4*0x2C.

Wniosek: 660 to limit przestrzeni skanowania, nie dowód, że 660 rekordów jest wypełnionych.

## 2. HARD — podstawowe pola

Dla rekordu R:

| Offset | Status | Znaczenie |
|---:|---|---|
| +0x08 | HARD | 16-bit parameter/CAN index |
| +0x0C | HARD | wskaźnik do lokalnego storage/current-value |
| +0x10 | HARD | type tag u8 |
| +0x14 | STRONG | deskryptor/metadane obsługiwane przez 0x14728/0x14734 |
| +0x1C | STRONG | drugi deskryptor/metadane używany w getter/validation path |
| +0x24 | STRONG/HARD-use | deskryptor używany przez inicjalizację/reset |
| +0x2C | REJECTED-as-field | początek następnego rekordu |
| +0x30 | REJECTED-as-field | +0x04 następnego rekordu |

Nie wolno ponownie opisywać +0x2C ani +0x30 jako pól tego samego rekordu.

## 3. HARD/STRONG — rejestracja

`FUN_0801143C` tworzy pojedynczy rekord na wywołanie.

Ustalona struktura argumentów/efektów:
- +0x08 otrzymuje indeks CAN/parameter,
- +0x0C otrzymuje drugi argument caller-a jako pointer/source,
- +0x10 otrzymuje typ,
- +0x14/+0x1C/+0x24 są zasilane przez helper `0x08014728`, który kopiuje 5-bajtowe deskryptory.

Kluczowe: rejestrator nie klonuje automatycznie jednego rekordu na cztery instancje.

## 4. HARD — instancje CO1..CO4

Dla pokazanych rodzin rejestracja występuje jako osobne indeksy:

- 0x2032..0x2035
- 0x2048..0x204B
- 0x2064..0x2067

W pętlach indeks jest rozszerzany przez `base + r7`.

Dla potwierdzonych rodzin drugi argument rejestracji pozostaje wspólny dla całej czwórki, np.:

- 0x2032..0x2035 -> 0x20020964
- 0x2048..0x204B -> 0x20020966
- 0x2064..0x2067 -> 0x2002096E

To daje twardy dowód, że rekord CAN/index może być osobny dla każdej instancji, podczas gdy lokalny working storage panelu jest współdzielony.

## 5. HARD — +0x24 jako wartość inicjalizacyjna/resetowa

Ścieżka `0x080115BC` przechodzi przez `0x294` pozycji.

Dla każdego rekordu:
1. pobierany jest deskryptor z `record+0x24`,
2. deskryptor jest przetwarzany przez `0x0801155A`,
3. wynik trafia do `0x08011812`.

To rozdziela dwie rzeczy:
- `record+0x0C` = bieżące lokalne storage/value,
- `record+0x24` = wartość używana podczas inicjalizacji/resetu.

To nie oznacza, że +0x24 jest prostym scalar-em; nadal jest strukturą/deskryptorem, którego wartość jest dekodowana przez helper.

## 6. HARD — type-aware value engine

Rodzina:
- 0x08014700 -> zapis z type 5,
- 0x08014708 -> type 2,
- 0x08014710 -> type 1,
- 0x08014718 -> type 4,
- 0x08014720 -> type 3,
- 0x08014734 -> getter wg typu,
- 0x08014728 -> kopiowanie/obsługa 5-bajtowego deskryptora.

`FUN_08011812` po lookup:
- używa +0x0C jako pointera storage,
- używa +0x10 jako type,
- zapisuje wartość zgodnie z typem,
- przy param_6=1 wykonuje dodatkową walidację związaną z polami +0x14/+0x1C.

Nie ma dowodu, że sama funkcja 0x08011812 wysyła CAN lub ustawia dirty bit.

## 7. HARD — instancja nie oznacza osobnego lokalnego RAM

Ścieżki UI/module:
`base_index + instance - 1`

Przykład:
`0x2032 + 2 - 1 = 0x2033`.

Następnie lookup trafia do rekordu odpowiadającego 0x2033.

W pokazanych rodzinach CO1..CO4 rekordy 0x2032..0x2035 wskazują ten sam lokalny storage przez +0x0C. Zatem:

`CAN PID/instance` i `local working storage` są dwiema różnymi warstwami.

To jest ważne dla emulatora: nie wolno automatycznie modelować każdego PID instancji jako osobnej zmiennej UI.

## 8. Obiektowe tablice rekordów — WAŻNA GRANICA

Starsze analizy wskazują wywołania `0x0801167A`, w których baza tablicy pochodzi z obiektu, a nie bezpośrednio z `0x20008D84`.

Potwierdzone przykładowo:
- raw 0x0D72C,
- raw 0x10138,
- raw 0x370FE,
- raw 0x37138.

Dlatego poprawny model nie brzmi:

`0x20008D84 jest jedyną możliwą tabelą rekordów`.

Poprawny model:

- istnieje główna runtime tabela zakotwiczona w `0x20008D84`,
- istnieją również ścieżki lookup działające na bazie przekazanej przez obiekt,
- `FUN_0801167A` jest mechanizmem lookup, a nie gwarancją jednej globalnej bazy.

To jest istotne dla dynamicznych instancji i późniejszego modelu emulatora.

## 9. Aktualny model platform-agnostic

```
                 +----------------------+
                 | 260-slot catalog     |
                 +----------+-----------+
                            |
                     UI/model mapper
                            |
                 568 logical positions
                            |
                    external PID/index
                            |
             +--------------+--------------+
             |                             |
      main runtime table             object-owned table
        @ 0x20008D84                  (selected paths)
             |                             |
             +--------------+--------------+
                            |
                      record 0x2C
                            |
          +-----------------+------------------+
          |        |        |        |         |
        +08      +0C      +10      +14      +1C/+24
         |        |        |        |           |
        PID     storage   type   descriptors   init/
                                                  validation
          |
       CAN/UI
```

## 10. Najważniejsze OPEN po tym pass

1. Pełny byte-by-byte layout +0x00..+0x2B.
2. Dokładna struktura 5-bajtowych deskryptorów.
3. Dokładna semantyka +0x14 vs +0x1C.
4. Pełne rozstrzygnięcie `0x0801155A/0x08014728/0x08014734`.
5. Producer/object ownership dla tablic używanych przez obiektowe wywołania 0x1167A.
6. Dokładne mapowanie 660-slot runtime universe -> 260 catalog -> 568 mapper positions.
7. Pełny CAN publication/read/write matrix.
8. Ścieżka wspólnego working storage -> rzeczywisty odczyt konkretnej instancji z CAN.

## 11. REJECTED

Nie używać bez nowego dowodu:
- +0x2C jako field status/access tego samego rekordu,
- +0x30 jako metadata tego samego rekordu,
- założenia, że 660 oznacza 660 aktywnych parametrów,
- założenia, że każdy PID instancji ma osobny lokalny storage,
- założenia, że 0x20008D84 jest jedyną możliwą bazą lookup.

## 12. Następny makro-cel

Najwyższa wartość informacyjna:

`0x0801143C -> 0x08014728 -> 0x08014734`
oraz równolegle
`0x0801155A -> 0x080117B4 -> 0x08011812`.

Celem jest odzyskanie struktury deskryptora i wszystkich semantycznych pól rekordu, a następnie automatyczne zbudowanie:
`PID -> record -> storage -> type -> descriptor -> CAN/UI consumer`.

Status po pass:
- geometria: CLOSED,
- PID/storage/type: CLOSED,
- +0x24 init/reset role: STRONG/HARD-use,
- instance/shared-storage behavior: CLOSED dla pokazanych rodzin,
- pełny descriptor model: OPEN.
