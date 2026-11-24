# BATCH — METHOD CLUSTER / Ghidra FUNCTION-GAP ANALYSIS — 2026-11-19

## Cel przebiegu

Kontynuacja dokładnie z punktu:
- dispatch FUN_0803C5B4 = OPEN,
- +0x84C / FUN_080424C4 = OPEN,
- pełny klaster Bitmap = OPEN.

Nie powtarzamy zamkniętego 370A -> +0x85C łańcucha.

---

# 1. NOWY TWARDY OBSERVATION: C5B4 NIE JEST W functions.txt

Canonical `firmware/FW2213TK-ghidra/functions.txt` zawiera:

- `0803c4c4 FUN_0803c4c4 140`
- `0803c550 FUN_0803c550 100`
- następna rozpoznana funkcja:
  `0803c8d2 FUN_0803c8d2 18`

Ponieważ:

`0x0803C550 + 100 = 0x0803C5B4`

adres `0x0803C5B4` jest **dokładnie końcem rozpoznanej przez Ghidra funkcji FUN_0803C550**.

Jednocześnie wcześniejszy raw pass niezależnie zidentyfikował `0x0803C5B4` jako początek osobnej metody/layout path.

## Status

[FW] `FUN_0803C550` kończy się dokładnie na `0x0803C5B4`.

[FW] `0x0803C5B4` nie ma własnego wpisu w functions.txt.

[FW] Raw analysis nadal dostarcza realny kod od `0x0803C5B4`, który:
- pobiera parent+0x85C,
- ustawia X=40,Y=70,
- wywołuje `FUN_0804272C`,
- przyłącza child przez parent+0x04,
- później operuje na +0x8E0.

[OPEN] Nie twierdzimy jeszcze, że sam brak wpisu w functions.txt automatycznie dowodzi vtable. Jest to jednak bardzo silny sygnał o funkcji nieuchwyconej przez automatyczną analizę Ghidry.

---

# 2. C5B4 LEŻY W ODDZIELNYM „FUNCTION GAP”

Od `0x0803C5B4` do następnej funkcji rozpoznanej przez Ghidrę `0x0803C8D2` jest:

`0x31E = 798` bajtów.

To jest wystarczająco duży obszar, aby zawierać więcej niż jeden nieoznaczony blok/metodę.

Nie wolno traktować całego zakresu jako jednego funkcjonalnego obiektu.

---

# 3. JESZCZE WAŻNIEJSZE: CB2C I CACC TEŻ NIE MAJĄ WPISÓW W functions.txt

Canonical functions.txt zawiera:
- `0803c8d2`
- `0803c8e4`
- ...
- `0803c924`

ale nie zawiera osobnych wpisów dla:
- `FUN_0803CACC`
- `FUN_0803CB2C`

Mimo że raw passes wykazały ich realne zachowanie:

### CACC
`FUN_0803CACC`
- przyjmuje Bitmap/object,
- wykonuje resource selection/update,
- prowadzi do `FUN_080307BC`.

### CB2C
`FUN_0803CB2C`
- jest realnym runtime refresh method,
- czyta model index `0x121`,
- przez `FUN_08036FF2` dociera do 370A storage,
- wywołuje `FUN_0803CACC`.

## Znaczenie

[FW] Co najmniej trzy kluczowe procedury tego fragmentu:
- C5B4,
- CACC,
- CB2C

nie występują jako normalne automatycznie rozpoznane funkcje w functions.txt.

To tworzy wspólny wzorzec: **istotne metody UI mogą znajdować się poza automatycznym function graph Ghidry**.

---

# 4. CB04 TAKŻE NALEŻY TRAKTOWAĆ JAKO PROCEDURĘ Z TEGO SAMEGO OBSZARU

`FUN_0803CB04` jest zamknięte semantycznie jako:
- constructor/wiring visual update object.

`FUN_0803CB2C`:
- runtime update.

CB04 również nie ma normalnego wpisu w functions.txt.

Nie jest jeszcze dowodem, że wszystkie te procedury należą do jednej klasy C++, ale:

[STRONG] ich adresy, sąsiedztwo i wspólny operowany layout wskazują na **gęsty, ręcznie odzyskany blok metod/handlerów UI**, którego automatyczna lista funkcji nie obejmuje poprawnie.

---

# 5. C33E MA ANALOGICZNY PROBLEM, ALE W INNYM GAPIE

Canonical functions.txt:

- `0803c284 FUN_0803c284 142`

kończy się dokładnie na:

`0x0803C284 + 142 = 0x0803C312`.

Następna rozpoznana funkcja:
- `0803c4c4`.

Tymczasem raw pass ma twardo odzyskane:
`FUN_0803C33E`.

Zatem C33E również znajduje się w obszarze, którego functions.txt nie opisuje jako osobnej funkcji.

## Wniosek

[STRONG] C33E i C5B4 nie są wyjątkami pojedynczego błędu nazewnictwa. W tej części firmware występuje większy problem automatycznego rozpoznawania granic funkcji/metod.

To jest szczególnie istotne dla obecnego pytania o dispatch.

---

# 6. NOWY MODEL DISPATCH — OSTROŻNIE

Nie możemy jeszcze napisać:

`C33E -> vtable slot -> C5B4`.

Ale obecne dowody układają się w:

```
automatyczny function graph Ghidra
        |
        +-- rozpoznane funkcje
        |
        +-- GAPS
             |
             +-- C33E
             +-- C5B4
             +-- CACC
             +-- CB04
             +-- CB2C
             +-- inne nieoznaczone metody/handlery
```

[STRONG] To przesuwa następny atak z:
„szukaj literalnego adresu C5B4”

na:

**„zidentyfikuj method-table / function-pointer region dla tego ręcznie odzyskanego klastra i dopiero wtedy połącz C5B4 z obiektem.”**

---

# 7. DLACZEGO TO PASUJE DO BRAKU BL DO C5B4

Mamy równocześnie:

1. brak bezpośredniego BL do C5B4,
2. brak literalnego `0x0803C5B5` w raw scan,
3. C5B4 nie jest funkcją w functions.txt,
4. C5B4 leży dokładnie na granicy rozpoznanej funkcji,
5. inne kluczowe metody tego obszaru też są poza functions.txt,
6. C5B4 operuje na obiekcie, którego layout jest budowany przez C33E,
7. C5B4 używa generic helperów `FUN_0804272C` i `FUN_08030380`.

[STRONG] Najbardziej produktywna hipoteza robocza:

**C5B4 jest ręcznie odzyskaną metodą/handlerem, który może być osiągany przez pośredni mechanizm obiektowy, a Ghidra nie odtworzyła go jako zwykłego call graph node.**

To nadal jest [STRONG], nie [FW] proof vtable.

---

# 8. NOWY CEL: ZNALEŹĆ GRANICE METHOD-TABLE DLA KLASTRA

Następny pass powinien badać kolejno:

### A
Adresy wszystkich nieoznaczonych procedur:
- C33E
- C5B4
- CACC
- CB04
- CB2C

### B
Dane/function-pointer tables w ich najbliższym sąsiedztwie.

### C
Wspólny zestaw metod używających:
- object +0,
- +0x04,
- +0x2C,
- +0x30,
- Bitmap +0x26,
- child attachment.

### D
Szczególnie:
- kto ma dostęp do C33E-created object,
- kto ustawia +0x85C,
- kto wywołuje CB2C,
- kto ustawia +0x8E0.

### E
Dopiero wtedy szukać exact source/class identity.

---

# 9. +0x84C — NOWA KOLEJNOŚĆ

Nie zakładamy już:
`+0x84C = container of +0x85C`.

Zamiast tego:

```
C33E
 ├─ +0x84C -> FUN_080424C4
 └─ +0x85C -> Bitmap
```

oraz osobno:

```
C5B4
 └─ +0x85C -> layout/attach
```

Następny krok dla +0x84C:
- wszystkie zapisy do +0x84C,
- wszystkie odczyty +0x84C,
- wszystkie funkcje operujące na obiekcie utworzonym przez 424C4,
- porównanie dwóch literal parameters z konstruktorami innych helperów.

Nie interpretować semantyki z samej kolejności offsetów.

---

# 10. CO ZOSTAJE ZAMKNIĘTE

Nie ruszać ponownie:

`370A -> 0x121 -> 0x20021FA6 -> 1..3 -> CB2C -> CACC -> +0x85C -> 11/12/13`

oraz:

- +0x85C = real Bitmap,
- X=40,Y=70,
- resource 11=105x126,
- resource 12=108x141,
- resource 13=82x145,
- trzy bezpośrednie C33E callers,
- +0x84C != proven parent/container,
- 0x0801AB7E = data/resource, nie callback,
- resource 14 / 469E8 = osobna gałąź.

---

# 11. NASTĘPNY PUNKT STARTOWY

**PASS 5 — HIDDEN METHOD CLUSTER**

1. odzyskać dokładne granice nieoznaczonych procedur wokół C33E/C5B4/CACC/CB04/CB2C;
2. szukać wspólnego method-table/function-pointer storage;
3. sprawdzić, czy C5B4 jest targetem pośrednim;
4. równolegle rozpracować 424C4/+0x84C;
5. wrócić do wszystkich mutacji +0x85C/+0x888/+0x8B4/+0x8E0;
6. dopiero potem identyfikować ekran 39A48/39B30/39C18.

**Nie raportować po jednym adresie. Kolejny raport dopiero po zamknięciu kilku zależnych elementów.**


# PASS 5B — +0x84C CONSTRUCTOR ALSO SITS OUTSIDE functions.txt

A further boundary check on `functions.txt`:

- `0804204a FUN_0804204a 204`
- 204 bytes ends exactly at `0x08042116`
- next listed function is `0804272c FUN_0804272c`

Yet the raw pass identifies `FUN_080424C4` as the constructor used for object +0x84C.

Therefore:

[FW] `FUN_080424C4` is another manually recovered executable procedure located inside a Ghidra function-recognition gap.

This is important because +0x84C is not merely an unexplained data slot: the constructor itself belongs to the same broader pattern of **UI procedures that Ghidra did not emit as normal functions**.

The current hidden-method evidence set is now:

- C33E — recovered inside gap between recognized functions
- C5B4 — exactly at the end boundary of FUN_0803C550, absent as its own entry
- 424C4 — inside gap after FUN_0804204A
- CACC — absent as normal entry
- CB04 — absent as normal entry
- CB2C — absent as normal entry

[STRONG] The most productive interpretation is now not "one missing C5B4 caller", but a recurring **custom UI method recovery problem** in this firmware region.

This raises the priority of recovering the underlying method-table/function-pointer structures before trying to name C++ classes.

## Updated next attack

A. Map every known manually recovered procedure to the nearest functions.txt boundaries.

B. Identify the data/function-pointer regions used by the generic object calls:
- vptr-like +0
- method slots +0x2C/+0x30
- attachment helper FUN_08030380
- Bitmap methods +0x38/+0x3C

C. Use the known generic setters as anchors to find the custom class method table.

D. From that table, test C5B4 / C33E / CB04 / CB2C / 424C4 membership or adjacency.

E. Only then decode +0x84C semantics.

[OPEN] Exact vtable address/class remains unresolved.
