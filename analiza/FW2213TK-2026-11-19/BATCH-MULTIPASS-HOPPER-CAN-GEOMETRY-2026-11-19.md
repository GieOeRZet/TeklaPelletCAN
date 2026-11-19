# TeklaPelletCAN — MULTIPASS HOPPER / CAN / GEOMETRY / PARAMETER PASS
Data: 2026-11-19

## 0. Zakres

Wielotorowy raw-BIN pass wykonany na `FW2213TK_kopia.bin` (0x1F0000 B).
Nie wracamy do ekstrakcji bitmap; inventory 000..187 i baza 0x08010000 są zamknięte.

Status:
- [FW] = bezpośredni dowód z kodu/binarki
- [DATA] = surowa tabela/asset
- [STRONG] = silny wniosek
- [HYPOTHESIS] = hipoteza wymagająca dalszego mostu

---

# 1. TWARDY ŁAŃCUCH ZASOBNIKA

## 1.1 FUN_08031CCC

W okolicy file 0x31CCC:

```
internal 0x147 -> resolver -> CAN 0x3601
internal 0x148 -> resolver -> CAN 0x3600
internal 0x14A -> resolver -> CAN 0x3602

percentage = 100 * value(0x147) / value(0x148)

FUN_0802DA54(context, percentage, (uint8)value(0x14A))
```

[FW] To jest bezpośredni raw-BIN proof.

Semantyka nazw z firmware:
- CAN 0x3600 = Tank capacity [kg]
- CAN 0x3601 = How much fuel left in tank [kg]
- CAN 0x3602 = Is fuel reserve
- CAN 0x3603 = Fuel reserve [kg]

Mapowanie panel-index -> CAN wynika z tabeli w file 0x37980+.

## 1.2 Korekta starego mapowania

Stare notatki miały przesunięcie:
- 328 -> 0x3601
- 329 -> 0x3600
- 330 -> 0x3603

To jest NIEAKTUALNE.

Raw mapping table:
```
0x147 -> 0x3601
0x148 -> 0x3600
0x149 -> 0x3603
0x14A -> 0x3602
0x14B -> 0x3604
0x14C -> 0x3607
```

---

# 2. FUN_0802DA54 — PEŁNY MECHANIZM HOPPERA

File offset: 0x2DA54.

Parametry:
- r0 = parent/context object
- r1 = percentage
- r2 = reserve flag

## reserve == 0

```
Bitmap child = parent + 0x5A8
resource = 0x33 = bitmap ID 051
parent+0x5F9 = 1
```

## reserve != 0

```
Bitmap child = parent + 0x5A8
resource = 0x35 = bitmap ID 053
parent+0x5F9 = 0
```

Następnie w obu gałęziach:
```
refresh(+0x5A8)
refresh(+0x5D4)
refresh(+0x5360)
```

[FW] 051/053 są wybierane dynamicznie przez flagę reserve.
[FW] Percentage NIE wybiera 051/053.

---

# 3. PROGRESS ARITHMETIC W FUN_0802DA54

Literal:
```
0x51EB851F
```

jest używany jako fixed-point multiplier realizujący dzielenie przez 100.

Dla reserve==0:
```
r1 = parent + 0x5AE
r2 = signed16(parent + 0x5DE)
r2 = percentage * r2
fill = fixed_point_div100(r2)
store parent+0x966/+0x96A

bottom/top arithmetic:
parent+0x966 = (parent+0x5AE) + (parent+0x5B2) - fill
parent+0x96A = fill
parent+0x5DA = fill - (parent+0x5B2)
```

[FW] Percentage zapisuje wartości do pól `+0x966`, `+0x96A`, `+0x5DA`.
[STRONG] To jest mechanizm progress/fill geometry, nie tylko wybór bitmapy.
[OPEN] Dokładna rola +0x5DE i późniejszego użycia +0x5DA wymaga znalezienia metody rysującej/clippingowej.

---

# 4. KONSTRUKTOR I DWA BITMAP CHILDREN

Konstruktor: FUN_0802BDF0.
Setup zaczyna się w okolicy file 0x2C294.

[FW]
- `parent+0x5A8` = Bitmap object, początkowo resource 0xFFFF
- `parent+0x5D4` = Bitmap object, początkowo resource 0xFFFF

W setup:
```
parent+0x5A8 -> resource 0x33 (051)
parent+0x5D4 -> resource 0x34 (052)
```

Dlatego:
- 051 = dynamic layer/state
- 052 = druga, osobna Bitmap layer
- 053 = alternatywny dynamic resource tej samej pierwszej warstwy

[STRONG] Hopper jest co najmniej dwuwarstwowym komponentem.

---

# 5. TOUCHGFX GEOMETRY — TWARDY DOWÓD

Dla Bitmap child `+0x5A8` setup robi:

```
parent geometry source = r6

x = parentX + (parentW - bitmapW) / 2
y = parentY + 0x20
```

Kod:
```
ldrsh r0,[r6,#0x44]    ; parent width
ldrsh r1,[r10,#0x08]   ; bitmap width
sub   r0,r0,r1
...
ldrh  r1,[r6,#0x40]    ; parent X
add   r1,r1,(delta/2)
...
vtable+0x2C(object)     ; set X
...
ldrh  r11,[r6,#0x42]   ; parent Y
add   r1,r11,#0x20
vtable+0x30(object)     ; set Y
```

[FW] To jest realna centrowana geometria, nie zgadywanie.

Dla child `+0x5A8` resource 051/053 ma W=34, H=29.

---

# 6. +0x960 — CLIPPING/CONTAINER CANDIDATE

Setup tworzy `parent+0x960` jako osobny widget/container-like object.

Jego geometry jest ustawiana z parametrów `+0x5A8`:
```
x = x(5A8)
y = y(5A8)
w = w(5A8)
h = h(5A8)
```

Następnie:
```
parent+0x5D4
resource = 052
add child -> parent+0x960
```

[FW] +0x960 ma geometrię zgodną z obszarem 5A8 i otrzymuje 5D4 jako child.
[STRONG] +0x960 jest bardzo mocnym kandydatem na obszar clippingu/kompozycji dla warstwy 052.
[OPEN] Nie nadawać mu jeszcze konkretnej klasy C++ bez vtable/class proof.

---

# 7. DOWÓD NA ADD/REMOVE CHILD

File/runtime helper:
- `FUN_08030380` = add child / linked-list insertion
- `FUN_080303F0` = remove child / linked-list removal

`FUN_08030380(parent, child)` zapisuje:
- child+0x14 = parent
- child+0x18 = next
- parent+0x28 / linked list

[FW] W setupie hoppera `+0x5A8`, `+0x960`, `+0x5D4` uczestniczą w prawdziwym parent-child tree.

---

# 8. FUN_080307BC — PRAWDZIWY BITMAP RESOURCE SETTER

File offset: 0x307BC.

Działanie:
```
resource ID -> Bitmap +0x26
derive width
 -> vtable +0x38
derive height
 -> vtable +0x3C
recompute clipping/visibility bounds
```

[FW] Nie jest to zwykły zapis numeru resource; aktualizuje rozmiar i stan geometryczny Bitmap.

To potwierdza, że:
```
resource 051/052/053
 -> real TouchGFX Bitmap
 -> real W/H
 -> real widget tree
```

---

# 9. DRUGI TOR: AGREGATOR PALIWA 0x32188

File offset: 0x32188.

Funkcja pobiera:
```
internal 0x116
internal 0x149
internal 0x148
internal 0x147
```

i przekazuje je do callbacku:
```
arg0 = value(0x116)
arg1 = value(0x147)
arg2 = value(0x148)
arg3 = value(0x149)
stack = u8(value(0x116))
```

[FW] To jest niezależny od FUN_08031CCC dowód, że wartości 0x147/148/149 są grupowane razem w jednym torze UI/model.

Tabela:
```
0x116 -> CAN 0x3606
0x147 -> CAN 0x3601
0x148 -> CAN 0x3600
0x149 -> CAN 0x3603
```

Target callback z BL w tej funkcji:
```
0x0802D828
```

[OPEN] Semantyka 0x3606 nie jest jeszcze zamknięta nazwą parametru.

---

# 10. STRING TABLE — TWARDY KONTEKST SEMANTYCZNY

W firmware:
```
0x26F14  Tank capacity [kg]
0x26F28  How much fuel left in tank [kg]
0x26F48  Fuel reserve [kg]
0x26F5C  Is fuel reserve
0x26F6C  Input IN17 config
0x26F80  Reserve sensor state
0x26F98  Total fuel counter[kg]
```

[STRONG] Sekwencja nazw jest zgodna z blokiem panel-index/CAN:
```
148 -> Tank capacity
147 -> Fuel left
149 -> Fuel reserve
14A -> Is fuel reserve
14B -> Input IN17 config
14C -> Reserve sensor state
```

To jest bardzo silna korelacja tabeli indeksów z tekstami, ale bez bezpośredniego xref string->record nadal oznaczamy jako [STRONG], nie [FW].

---

# 11. 0x160/0x161 — NOWA TWARDa MAPA CAN

W raw mapping table:
```
0x160 -> CAN 0x3521
0x161 -> CAN 0x3529
0x162 -> CAN 0x352A
0x163 -> CAN 0x3527
0x164 -> CAN 0x3528
0x165 -> CAN 0x352B
```

Dodatkowo:
```
0x151 -> 0x3515
0x152 -> 0x3516
0x153 -> 0x3517
0x154 -> 0x3518
0x155 -> 0x351B
0x156 -> 0x351C
0x157 -> 0x3519
0x158 -> 0x351A
```

[DATA/ FW] Mapowanie jest bezpośrednio w tabeli.

[OPEN] Nadal trzeba znaleźć call-site, parent, geometrię i callback dla 160/161.

---

# 12. 130..137 — NOWA TWARDa MAPA CAN

W raw mapping table:
```
0x130 -> 0x3739
0x131 -> 0x373A
0x132 -> 0x373B
0x133 -> 0x3722
0x134 -> 0x3723
0x135 -> 0x3728
0x136 -> 0x373C
0x137 -> 0x373D
```

User-confirmed visual semantics:
- 130..137 = cztery pozycje ikon trybu nad sliderem,
- każda pozycja ma state inactive/active,
- 4x2 = 8 bitmapów.

[FW] CAN mapping jest zamknięty.
[OPEN] Dokładne przypisanie ID -> pozycja 1..4 -> active/inactive wymaga call-site/resource assignment.

---

# 13. 151/152 — MAPA CAN

Raw:
```
0x151 -> 0x3515
0x152 -> 0x3516
```

User/asset evidence:
- 151/152 = 30x31 vertical selector state pair związany z FUN_08047290.

[OPEN] Potrzebny jest pełny call-site -> model -> geometry.

---

# 14. NAJWAŻNIEJSZY NOWY MODEL HOPPERA

Najbardziej prawdopodobny obecnie układ:

```
CAN
 ├─ 0x3600 capacity
 ├─ 0x3601 remaining
 ├─ 0x3602 reserve flag
 └─ 0x3603 reserve threshold
       |
       v
FUN_08031CCC
       |
       +-- percentage = 100*remaining/capacity
       +-- reserve flag
       v
FUN_0802DA54
       |
       +-- Bitmap +5A8 = 051 or 053
       +-- progress fields +966/+96A/+5DA
       |
       +-- refresh +5A8
       +-- refresh +5D4
       |
       +-- +960 clipping/composition area
              |
              +-- Bitmap +5D4 = 052
```

[STRONG] To jest obecnie najpełniejszy dowodowy pionowy łańcuch dla zasobnika.

[OPEN] Nadal trzeba odnaleźć metodę, która konsumuje +5DA/+966/+96A i przez to zamknąć dokładny mechanizm wizualnego fill/clippingu.

---

# 15. NEXT ATTACK — PRIORYTET

1. **+0x5DA / +0x966 / +0x96A**
   - znaleźć wszystkie funkcje/metody konsumujące te pola;
   - zidentyfikować draw/paint/clip callback.

2. **+0x960**
   - odzyskać vptr/class pattern;
   - ustalić czy to ClippedContainer/Container lub custom wrapper.

3. **FUN_0802D828**
   - prześledzić caller/callback;
   - ustalić rolę 0x116/0x3606.

4. **0x3602 / 0x3607**
   - znaleźć runtime consumers i potwierdzić reserve semantics.

5. **160/161**
   - wszystkie call-site'y;
   - parent;
   - X/Y/W/H;
   - callback.

6. **130..137**
   - resource setter call-sites;
   - exact 4x2 state map.

7. **151/152**
   - 47290 vertical selector;
   - exact model parameter(s).

8. **parameter -> callback -> model -> widget**
   - wrócić do 3E714 / 36FF2 / 4842C / 4E5BC / 32316 po zamknięciu powyższych torów.

---

# 16. ZASADA KONSOLIDACJI

Nie traktować pojedynczego BL jako końca toru.
Każdy kolejny wynik ma być prowadzony:
```
parameter/index
 -> mapping
 -> model/record
 -> callback
 -> object
 -> widget
 -> resource
 -> geometry
 -> visibility/clipping
 -> render
```

Kolejny duży checkpoint ma zamknąć przynajmniej jeden taki pionowy łańcuch.


---

# 17. NOWY PASS — KOREKTA SEMANTYKI +0x5DA/+0x5DE

To jest ważna korekta poprzedniej interpretacji.

## [FW] +0x5DA i +0x5DE są wewnątrz obiektu +0x5A8

`r1 = parent + 0x5AE` w `FUN_0802DA54`, więc:
- `[r1]` = parent+0x5AE = child+0x06
- `[r1,#4]` = parent+0x5B2 = child+0x0A
- `[r1,#0x2C]` = parent+0x5DA = child+0x32
- `[r1,#0x30]` = parent+0x5DE = child+0x36

Czyli poprzednie określenie ich jako „zewnętrzne pola progress” było zbyt luźne.

## [FW] Standardowy Bitmap constructor

`FUN_0802DF08`:
- ustawia vptr Bitmap,
- resource ID -> +0x26,
- width -> +0x08,
- height -> +0x0A,
- status/flags -> +0x28.

Bitmap vtable dla tego obiektu zaczyna się pod runtime `0x0807F1E0`.

## [FW] Resource setter

`FUN_080307BC`:
- resource -> Bitmap+0x26,
- wywołuje vtable+0x38 z szerokością z BitmapData,
- vtable+0x3C z wysokością,
- następnie aktualizuje stan geometryczny.

To zamyka, że +0x08/+0x0A są standardowym W/H Bitmap.

## [STRONG] Co wynika z +0x30/+0x32/+0x36

W firmware istnieje osobny kod pod `0x0803008C` i `0x08030640`, który operuje na polach +0x30/+0x32/+0x34/+0x36/+0x37 oraz na resource ID +0x26. Nie ma jeszcze bezpośredniego dowodu, że jest to dokładnie klasa Bitmap z hoppera, więc nie utożsamiać automatycznie.

Natomiast w samym hopperze:
```
+0x5DA = child(+0x32)
+0x5DE = child(+0x36)
```

i `FUN_0802DA54` robi:
```
value = percentage * signed16(child+0x36)
fill = fixed_point_div100(value)

child+0x32 = fill - child+0x0A
+0x966/+0x96A = pochodne fill/geometry
```

## [OPEN] Najważniejszy następny test

Nie nazywać jeszcze +0x5DA „crop Y” ani „progress field”.

Trzeba teraz:
1. ustalić, kto ustawia child+0x36 przed pierwszym wywołaniem `FUN_0802DA54`,
2. znaleźć funkcje czytające/ustawiające +0x32/+0x36 w tej samej klasie/vtable,
3. porównać je z kodem `0x0803008C/0x08030640`,
4. dopiero wtedy nazwać mechanizm jako crop/animation/clip.

## [FW] +0x960 nadal jest osobnym obiektem geometry/container-like

Setup:
```
+0x960 geometry = geometry +0x5A8
add +0x960 to parent
add +0x5D4 to +0x960
```

`FUN_0802BDF0` nie wykonuje prostego `+0x960 -> Bitmap constructor`; `+0x960` przechodzi przez osobny initializer `FUN_0802DD4C` w setupie. To wzmacnia rozdział:
- +0x5A8 = Bitmap,
- +0x960 = inny widget/container-like object,
- +0x5D4 = Bitmap child.

Nie przypisywać jeszcze konkretnej klasy TouchGFX bez vptr proof.

---

# 18. NOWY WNIOSEK O STRUKTURZE

Najbardziej bezpieczny model na tym etapie:

```
HOPPER ROOT
  |
  +-- Bitmap @ +0x5A8
  |      |
  |      +-- resource 051/053
  |      +-- standard W/H @ +0x08/+0x0A
  |      +-- custom/extended fields around +0x30..+0x37 [OPEN]
  |
  +-- object @ +0x960
         |
         +-- Bitmap @ +0x5D4
                |
                +-- resource 052
```

[FW] Ten model jest zgodny z kolejnością konstrukcji, resource assignment, geometry i add-child.

[OPEN] Nadal brakuje jednego mostu: dokładnej klasy +0x960 oraz funkcji konsumującej wynik procentu.
