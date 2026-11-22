# AUTONOMOUS PASS 21 — MENU RAW MATRIX / RUNTIME-ANCHOR AUDIT — 2026-11-22

Firmware: `FW2213TK_kopia.bin`
SHA-256: `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`
Size: `0x1F0000`

## Cel

Po uzyskaniu fizycznego canonical BIN ponownie sprawdzić MenuTree bez polegania na wcześniejszych opisach:
- dokładną tabelę 21 × 6 B,
- adresację RAW/PROJECT/RUNTIME,
- bezpośrednie literalne odwołania do runtime class table,
- bezpośrednie odwołanie do access/update table,
- literalne kotwice konstruktora row i resolverów selekcji.

Do automatyzacji dodano:
- `tools/menu_matrix_scan.py`
- `tools/test_menu_matrix_scan.py`

Skaner jest evidence-only: nie nadaje semantyki selectorom i nie zgaduje zawartości RAM.

## 1. HARD — canonical BIN ponownie potwierdzony

Skaner odczytał:

- SHA-256 = `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`
- size = `0x1F0000`
- PROJECT = RAW + `0x08000000`
- RUNTIME = PROJECT + `0x10000`

Status: **HARD**.

## 2. HARD — 21 × 6 B MenuTree table

Tabela zaczyna się pod:
- RAW `0x42348`
- PROJECT `0x08042348`

Stride = 6 B.

Odczyt z canonical BIN:

| idx | selector | TypedText | Bitmap |
|---:|---:|---:|---:|
| 0 | 0 | 60 | 83 |
| 1 | 10 | 61 | 85 |
| 2 | 1 | 62 | 86 |
| 3 | 2 | 63 | 86 |
| 4 | 3 | 64 | 86 |
| 5 | 4 | 65 | 86 |
| 6 | 5 | 66 | 88 |
| 7 | 6 | 71 | 87 |
| 8 | 7 | 67 | 84 |
| 9 | 8 | 70 | 82 |
| 10 | 9 | 69 | 99 |
| 11 | 11 | 72 | 78 |
| 12 | 13 | 74 | 89 |
| 13 | 17 | 77 | 159 |
| 14 | 15 | 76 | 96 |
| 15 | 0 | 12 | 73 |
| 16 | 90 | 14 | 75 |
| 17 | 97 | 18 | 78 |
| 18 | 100 | 16 | 79 |
| 19 | 98 | 19 | 80 |
| 20 | 95 | 20 | 81 |

To jest bezpośredni odczyt BIN, niezależny od dekompilacji.

Status: **HARD**.

## 3. HARD — runtime class table ma dokładnie jedną bezpośrednią literalną kotwicę

Szukano little-endian `0x20005EF0` w całym BIN.

Wynik:
- 1 trafienie,
- RAW `0x3C218`.

To jest dokładnie okolica formalnej funkcji `FUN_0803C064), która korzysta z tej tabeli jako:
`class = [0x20005EF0 + row_index]`.

Wniosek:
- nie ma drugiego statycznego literalnego producenta/źródła tej RAM tabeli w canonical BIN;
- jej **zawartość nadal jest runtime state**, nie stałą flashową;
- nie wolno rekonstruować 21 klas z samego root-table selector.

Status: **HARD dla pojedynczej statycznej kotwicy; OPEN dla producenta/zawartości RAM**.

## 4. HARD — access/update table 0x20005F08 ma dokładnie jedną literalną kotwicę

Szukano little-endian `0x20005F08`.

Wynik:
- 1 trafienie,
- RAW `0x42314`.

To potwierdza wcześniejszy model:
- `0x20005F08` jest zewnętrzną/runtime tablicą używaną przez 21-iteracyjny access/update pass;
- BIN nie zawiera jej statycznej zawartości;
- punkt literalnego pobrania leży bezpośrednio przy końcu MenuTree code/data window.

Status: **HARD** dla jedynej literalnej kotwicy; **OPEN** dla runtime producer i zawartości.

## 5. HARD — literalne kotwice row/navigation family

Whole-BIN little-endian scan znalazł dokładnie po jednym wystąpieniu:

- `0x0805BB43` → RAW `0x3C030`
  - row constructor pointer / Thumb pointer używany przez wcześniejszy closure;
- `0x0808EB01` → RAW `0x63AB8`
  - główny row-selection resolver;
- `0x0808EB37` → RAW `0x63AC0`
  - sibling selection/state resolver.

Brak dodatkowych literalnych wystąpień tych wskaźników w canonical BIN.

To wzmacnia rozdzielenie:
1. row construction,
2. main row-selection resolver,
3. sibling/state resolver.

Nie utożsamiamy sibling resolvera z główną nawigacją.

Status: **HARD jako literal anchor audit**.

## 6. HARD — selector nie jest wystarczającym kluczem nawigacji

Canonical BIN potwierdza jednocześnie:

- root table zawiera selector values,
- runtime class table jest osobną RAM strukturą,
- row-selection resolver wskazuje konkretny row object,
- następnie row index trafia do `FUN_0803C064`,
- `FUN_0803C064` wybiera destination na podstawie runtime class byte.

Dlatego poprawny model pozostaje:

`root table selector -> MenuRow object -> row index -> runtime class -> page-family dispatch`

a nie:

`selector -> page`.

To jest kluczowe dla późniejszego ESP32 implementation.

Status: **HARD mechanizm; semantic labels of runtime classes remain OPEN where not independently proven**.

## 7. Korekta statusu względem wcześniejszych raportów

Ten pass nie zmienia wcześniejszego closure dotyczącego:
- 21-slot row family,
- access-dependent construction 15 + 6,
- capability resolver,
- row selection -> index,
- class dispatcher.

Natomiast podnosi jakość dowodową, ponieważ wszystkie główne adresy zostały ponownie zakotwiczone bezpośrednio w fizycznym canonical BIN.

Nie cofamy wcześniejszych korekt.

## 8. Najważniejsze OPEN po tym pass

P0:

1. runtime producer/writer dla `0x20005EF0`;
2. runtime producer/writer dla `0x20005F08`;
3. exact runtime contents of both 21-byte tables;
4. semantic mapping:
   `class byte -> destination -> screen/widget family`;
5. exact vtable/class identity of the row object;
6. touch callback producer for `row+0x26C`;
7. state-child callback producer at `row+0xF8 + 0x150`.

P1:

8. exact widget tree per destination;
9. configuration/access matrix per screen family;
10. full PID -> screen -> widget -> CAN matrix.

## 9. Narzędzie

Nowy scanner:
`tools/menu_matrix_scan.py`

Test:
`tools/test_menu_matrix_scan.py`

Zasada:
- parser danych nie nadaje znaczeń,
- adresy są emitowane w RAW/PROJECT/RUNTIME,
- literal anchors są liczone w całym BIN,
- wynik jest deterministyczny.

## 10. Następny atak

Priorytet zostaje ustawiony na **runtime class/access table producers**, ponieważ bez ich zawartości nie da się zamknąć 1:1 mapy:
`row index -> actual page/screen family`.

Dopiero potem schodzimy z page-family do:
`screen -> widgets -> visibility -> PID -> CAN`.

Status końcowy PASS 21:
- MenuTree physical table: **HARD**
- 21-slot architecture: **HARD**
- access-dependent 15+6 construction: **HARD**
- class-table literal anchor: **HARD**
- access/update-table literal anchor: **HARD**
- selector != direct navigation key: **HARD**
- runtime class table contents: **OPEN**
- runtime access/update table contents: **OPEN**
- full screen/widget semantics: **OPEN**
