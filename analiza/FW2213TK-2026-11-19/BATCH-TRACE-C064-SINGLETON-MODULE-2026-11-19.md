# BATCH-TRACE-C064-SINGLETON-MODULE-2026-11-19

## Cel

Kontynuacja właściwego trace:

`param_2 -> FUN_0803C064 -> DAT_0803C218 -> class 1..4 -> +0x12B/+0x12C -> lookup instancyjny -> CAN`

Bez wracania do wycofanego tropu `0x08042146 -> 0x38130`.

## 1. Nowy dowód: C064 jest operacją na jednym aktywnym obiekcie modułu

`FUN_0803C064(param_1,param_2)` nie dostaje wskaźnika modułu jako argumentu roboczego. Dla klas 1..4:

- pobiera moduł przez `FUN_080314BA()`,
- odczytuje `DAT_0803C218[param_2]`,
- dla wartości 1..4 ustawia na tym samym obiekcie:
  - `module+0x12B = class`,
  - `module+0x12C = class`.

`param_1` nie wpływa na tę gałąź. Jest używany dopiero w specjalnych klasach 0x0C i 0x0F.

To mocno zawęża rolę `param_2`: jest selektorem pozycji/klasy przekazywanym do operacji modułu, a nie wskaźnikiem modułu ani bezpośrednim indeksem CAN.

## 2. Potwierdzenie, że +0x12B/+0x12C sterują późniejszym zachowaniem tego samego modułu

`FUN_08037D00(module)` czyta `module+0x12B` i na tej podstawie wybiera wariant:

- 0 -> ścieżka domyślna,
- 1..4 -> ustawia `module+0x12C = 1..4`,
- 5..10 -> osobne funkcje wariantów,
- 0x10 -> osobna ścieżka.

Po wyborze wariantu dobiera rekord/descriptor przez `FUN_08039494` i zapisuje go do `module+0x110`, a wskaźnik do `module+0x10C`.

Wniosek: `+0x12B` jest aktywnym typem/wariantem modułu, a `+0x12C` jest numerem instancji używanym przez dalszą warstwę.

## 3. Konstrukcja modułu: jeden obiekt, nie cztery statyczne obiekty

`FUN_08061020()` tworzy obiekt modułu tylko raz:

`puVar1 = param_1 + 0x2A17`

następnie:

`FUN_08037CA4(puVar1, param_1 + 0x2A70, param_1)`

i od razu:

`FUN_08036D60(param_1 + 0x2A70)`

`FUN_08037E9C(puVar1)`

Konstruktor `FUN_08037CA4` ustawia m.in.:

- `module+0x129 = 0`,
- `module+0x12A = 0`.

`FUN_08037E9C` ustawia stan domyślny:

- `module+0x128 = 1`,
- `module+0x12B = 0`,
- `module+0x12C = 1`.

To jest istotne architektonicznie: firmware ma pojedynczy aktywny obiekt modułu, którego konfiguracja przełącza klasę/instancję. Nie znaleziono dowodu na cztery równolegle utworzone obiekty C064.

## 4. C064 i 37D00 wyglądają jak dwie warstwy tej samej klasy obiektu

Nie ma bezpośrednich call-site'ów `FUN_0803C064` ani `FUN_08037D00` w dekompilacji.

Obie funkcje mają jednak dokładnie ten sam obiektowy kontekst:

- operują na obiekcie zwracanym przez `FUN_080314BA()`,
- używają pól `+0x12A`, `+0x128`, `+0x12B`, `+0x12C`, `+0x10C`, `+0x110`,
- dobierają descriptor przez `FUN_08039494`.

Najbardziej prawdopodobny mechanizm wywołania jest więc pośredni (callback/vtable/generic dispatcher), ale nadal nie przypisujemy C064 do konkretnego slotu vtable bez danych z tablicy funkcji.

## 5. Co C064 robi z klasami 1..4 — bez interpretacji semantycznej

Twardy mapping kodowy:

| DAT_0803C218[param_2] | module+0x12B | module+0x12C |
|---:|---:|---:|
| 1 | 1 | 1 |
| 2 | 2 | 2 |
| 3 | 3 | 3 |
| 4 | 4 | 4 |

Dopiero po tym ustawieniu dalszy engine może wykonać:

`base_index + instance - 1`

Nie utożsamiamy jeszcze wartości `param_2` z `0x2105..0x2108`.

## 6. Połączenie z potwierdzonym lookupem instancji

Wcześniejszy twardy trace pozostaje ważny:

`module+0x12C -> globalny stan instancji -> base_index + instance - 1 -> FUN_0801167A -> rekord 0x2C`

Dla bazy CO:

- `0x2032 + instance - 1`,
- `0x2048 + instance - 1`,
- `0x2064 + instance - 1`,
- itd.

Czyli C064 ustawia dokładnie pole, które później determinuje wariant indeksu w lookupie.

## 7. Najważniejsza luka po tym batchu

Pozostały dwa elementy:

### A. Zawartość DAT_0803C218

Adres:

`0x0803C218`

Następna funkcja:

`0x0803C284`

Różnica:

`0x6C = 108 bajtów`

W samym decompiled.c tabela nie ma inicjalizatora, więc nie wolno wymyślać jej wartości.

### B. Źródło param_2

Bezpośredniego wywołania C064 nie ma w dekompilacji.

Następny właściwy cel to odnalezienie mechanizmu pośredniego, który wywołuje metodę z dwoma argumentami i dostarcza `param_2`. Dopiero wtedy można zmapować:

`param_2 -> pozycja w C218 -> class 1/2/3/4 -> instancja 1/2/3/4`

## 8. Granica pewności

**TWARDY DOWÓD**

- C064 czyta `DAT_0803C218[param_2]`.
- Klasy 1..4 ustawiają `+0x12B/+0x12C` na 1..4.
- `+0x12C` jest używany przez późniejszy engine instancyjny.
- Konstruktor tworzy jeden obiekt modułu.
- Domyślna instancja tego obiektu to 1.
- Brak bezpośredniego call-site C064 w decompiled.c.

**NIEUDOWODNIONE**

- wartości 108 bajtów C218,
- konkretny vtable/callback slot C064,
- konkretne wartości `param_2` dla CO1..CO4,
- bezpośrednie utożsamienie `param_2` z `0x2105..0x2108`.

## Następny trace

Nie wracamy do literalnego szukania `0x2033/0x2049` ani do wycofanego `0x38130`.

Priorytet:

`pośrednie wywołanie C064 -> param_2 -> C218 -> class/instance`

Równolegle odzyskanie surowej tablicy `0x0803C218..0x0803C283`.

