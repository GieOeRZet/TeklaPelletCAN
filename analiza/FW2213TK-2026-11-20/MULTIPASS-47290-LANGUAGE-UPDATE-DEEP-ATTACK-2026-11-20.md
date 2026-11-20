# MULTIPASS — 47290 / LANGUAGE / UPDATE-SCREEN DEEP ATTACK — 2026-11-20

## 0. Cel

Ten batch ma odpowiedzieć na aktualne pytanie:

> Czy pionowy sześciopozycyjny komponent `FUN_08047290` może być ekranem wyboru języka / ekranem związanym z aktualizatorem firmware?

Użytkownik wykluczył go wizualnie jako element Home. Instrukcja urządzenia mówi, że aktualizacja z karty odbywa się automatycznie po włączeniu zasilania, a po pojawieniu się ekranu głównego urządzenie należy wyłączyć i wyjąć kartę.

Zasada: żadnego dopasowywania na siłę. Oddzielamy:
- HARD — bezpośrednio z BIN / disassembly / xref / tabel,
- CORRELATION — obserwacja użytkownika,
- OPEN — brak zamknięcia.

Źródło binarne:
`FW2213TK_kopia.bin`
SHA-256:
`1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`
Rozmiar: 2,031,616 B
Baza runtime używana w analizie: `0x08010000`.

---

# 1. PROTOKÓŁ MULTIPASS

Wykonano szeroki atak wielotorowy zamiast jednego grep-a:

1. raw binary — adresy funkcji 47290/47334/484B0/3E714/3E5AC,
2. xref 47290 -> 47334,
3. xref 484B0 -> 47334,
4. xref 3EE30 -> 484B0,
5. provenance `record+0x08`,
6. analiza param_7,
7. geometria sześciu slotów,
8. resource IDs 151/152,
9. bitmap descriptor table,
10. TypedText table architecture,
11. osiem tabel językowych,
12. wyszukiwanie nazw języków w BIN jako UTF-16LE,
13. wyszukiwanie stringu "Language",
14. parametr FW ID=3 Language,
15. RAM address parametru Language,
16. kod obsługi parametru Language,
17. menu selector 90,
18. korelacja selector 90 -> Language,
19. korelacja selector 15 -> PIN,
20. pełna kolejność 21 selectorów menu,
21. rozdzielenie 15 rekordów bazowych od 6 rekordów access-dependent,
22. wyszukiwanie resource 115,
23. wyszukiwanie resource 144,
24. wyszukiwanie resource 174,
25. wyszukiwanie resource 160/161/170/171,
26. analiza obszarów tabel resource IDs w BIN,
27. wyszukiwanie słów związanych z update/bootloader/SD,
28. sprawdzenie, czy repo ma już zamkniętą semantykę 47290,
29. kontradykcja hipotezy "47290 = Home",
30. kontradykcja hipotezy "47290 = prosty sześciopunktowy wybór języka".

Nie traktować liczby przebiegów jako dowodu jakości; istotne są niezależne ścieżki i zgodność wyników.

---

# 2. 47290 — TWARDY MODEL

`FUN_0803E5AC` ma bezpośrednie połączenie:

`root + 0x92DC -> FUN_08047290`

`FUN_08047290` tworzy sześć rekordów:
- pierwszy: `+0xA8`,
- stride: `0x40`,
- count: 6.

`FUN_08047334` ustawia:

| slot | X | Y |
|---:|---:|---:|
| 0 | 100 | 50 |
| 1 | 100 | 84 |
| 2 | 100 | 118 |
| 3 | 100 | 152 |
| 4 | 100 | 186 |
| 5 | 100 | 220 |

To jest HARD.

Obserwacja użytkownika:
- takiego pionowego sześciopozycyjnego elementu nie ma na widocznym Home.

Wniosek:
- 47290 NIE wolno dalej używać jako elementu widocznego Home,
- geometria nie może być wciskana do Home,
- pozostaje komponentem innego ekranu/overlayu/sekcji.

Nie znaleziono dowodu na późniejszy obrót o 90°. Hipoteza rotacji pozostaje odrzucona do czasu znalezienia konkretnego transform/geometry call.

---

# 3. 151/152 — ZAMKNIĘTE

Tabela bitmap:
- runtime `0x08054450`,
- rekord bitmap: 20 B.

Bitmap 151:
- 30x31,
- RGB pointer `0x081C5638`.

Bitmap 152:
- 30x31,
- RGB pointer `0x081C5D7C`.

Różnica:
`0x744 = 30 * 31 * 2`.

Raw call-site w `FUN_08047334` potwierdza parę:
- 151 normal,
- 152 selected.

Zatem 47290 jest kompozytem:
- sześć slotów,
- bitmap state,
- TypedText,
- runtime update/touch.

To nie jest zwykła lista tekstów.

---

# 4. NAJWAŻNIEJSZY MOST — SKĄD BIERZE SIĘ TEKST

Jedyny bezpośredni BL do `FUN_08047334`:
`0x080484D4`, wewnątrz `FUN_080484B0`.

`FUN_080484B0` dostaje argumenty od `FUN_0803EE30`.

W `0803EE30`:
- argument z `record+0x08` jest przekazywany dalej,
- `FUN_080484B0` kopiuje go do argumentu 7 `FUN_08047334`.

Dlatego:

`param_7 = *(record + 0x08)`

a w `FUN_08047334`:

`TypedTextID(slot) = param_7[slot]`

To jest HARD.

### Konsekwencja

Sześć nazw NIE jest wpisanych bezpośrednio w `FUN_08047290`.

47290 jest rendererem wielokrotnego użytku.

Semantyka sześciu pozycji jest dostarczana z zewnątrz przez aktywny runtime record/configuration path.

To bardzo mocno osłabia prostą interpretację:
`47290 = stały ekran wyboru sześciu języków`.

---

# 5. 3E714 / 3E7xx–3EBxx — KONFIGURACYJNY CHARAKTER

`FUN_0803E714` i okolice budują runtime listy TypedText / parametrów.

W znanej ścieżce Heating:
`FUN_0803E714`
-> `FUN_0803EFDA`
-> kolejne 16-bitowe ID
-> `FUN_08036FF2(context,id)`
-> UI.

`FUN_0803EFDA` kopiuje kolejne 16-bitowe ID do runtime listy.

To pokazuje architekturę:
- builder wybiera zestaw ID,
- renderer otrzymuje wskaźnik do tablicy,
- komponent może być użyty ponownie dla różnych zestawów.

Nie ma dowodu, że sześć ID 47290 jest tym samym zestawem co 12/11 parametrów Heating. Jest natomiast dowód na ten sam typ architektury: dane tekstowe są dostarczane dynamicznie.

---

# 6. JĘZYKI — CO NAPRAWDĘ MAMY W BIN

W BIN są 8 równoległych tabel TypedText:
- ES
- EST
- EN
- LT
- PL
- RO
- SK
- CZ

Każda:
- 495 wpisów,
- 4 B na wskaźnik,
- stride między tabelami `0x7BC`.

Początki:
- `0x59E90`
- `0x5A64C`
- `0x5AE08`
- `0x5B5C4`
- `0x5BD80`
- `0x5C53C`
- `0x5CCF8`
- `0x5D4B4`

Wspólne ID TypedText działają między językami.

Przykładowo:
- 57 = Ogrzewanie 1,
- 58 = Ogrzewanie 2,
- 99..102 = OGRZEWANIE 1..4,
- 119..122 = Ogrzewanie obwód 1..4.

---

# 7. NOWY TWARDY PUNKT: PARAMETR "LANGUAGE"

W rejestracji parametrów firmware istnieje:

- parameter ID = `3`,
- hex = `0x0003`,
- name = `Language`,
- type = u8,
- min = 0,
- max = 30,
- default = 0,
- access = 3,
- RAM = `0x20021FAA`,
- kod / funkcja powiązana = `0x08011D6C`.

To jest niezależny HARD dowód, że firmware ma osobny parametr konfiguracyjny Language.

Bardzo ważne:
- zakres 0..30 nie oznacza 8 języków,
- nie wolno utożsamiać wartości parametru z indeksem tabeli językowej bez znalezienia mappera,
- sam fakt istnienia parametru nie dowodzi, że 47290 jest jego UI.

---

# 8. CZY W BIN SĄ NAZWY JĘZYKÓW JAKO STRINGI?

Wykonano niezależny raw scan BIN dla nazw:
- Polski,
- English,
- Eesti,
- Lietuvių,
- Română,
- Slovenčina,
- Čeština,
- Español.

Nie znaleziono tych nazw jako prostych UTF-16LE/ascii/UTF-8 stringów w BIN.

Znaleziono natomiast string:
`Language`

To jest istotne.

Nie oznacza:
"firmware nie ma nazw języków".

Możliwe mechanizmy:
- nazwy są budowane z innych danych,
- używane są skróty / symbole,
- UI korzysta z TypedText IDs,
- nazwy mogą być zaszyte w innej strukturze,
- wyświetlane są wartości pośrednie.

Ale na tym etapie nie mamy dowodu:
`slot 0..5 -> nazwa języka`.

---

# 9. MENU SELECTOR 90 — WAŻNE ROZDZIELENIE

Zamknięto wcześniej:

`selector 90 -> Language / Język`.

Jednocześnie główny menu selector table ma kolejność:

`0, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 13, 17, 15, 0, 90, 97, 100, 98, 95`

Czyli 90 jest jednym z rekordów menu zależnych od access/configuration.

To daje bardzo mocny model:

Home/Menu
-> Konfiguracja / ustawienia
-> pozycja selector 90
-> Language.

Ale to NIE jest jeszcze dowód:
`selector 90 -> FUN_08047290`.

To są dwa osobne fakty, które dopiero trzeba połączyć przez constructor/callback/navigation path.

---

# 10. SZEŚĆ POZYCJI VS 8 JĘZYKÓW — KONTRADYKCJA

Na pierwszy rzut oka:

47290 = 6 slotów

BIN language tables = 8 języków

To nie pasuje do prostego modelu:
`6 slotów = 6 języków`.

Możliwe są jednak warianty:
1. 8 języków skompilowanych, ale tylko 6 dostępnych w UI,
2. sześć slotów jest stroną/fragmentem większej listy,
3. 47290 nie jest language selector,
4. sloty pokazują inne wartości,
5. jedna lub więcej pozycji jest dynamicznie zmieniana zależnie od konfiguracji.

Na razie brak podstaw do wyboru jednego z nich.

Najbardziej konserwatywny status:
**47290 = reusable six-slot vertical selector/list, semantics OPEN.**

---

# 11. UPDATE SCREEN — WERYFIKACJA HIPOTEZY

W repo/BIN search nie zamknięto osobnego ekranu z jednoznacznymi tekstami typu:
- "Updating",
- "Update successful",
- "Please wait",
- "Bootloader",
- "SD card update".

Nie znaleziono też w obecnym korpusie analizy twardej factory/navigation edge:
`power-on updater -> 47290`.

Dlatego hipoteza:
`47290 = wybór języka aktualizatora`

pozostaje OPEN i nie ma jeszcze statusu STRONG.

Instrukcja użytkownika dodatkowo osłabia tę hipotezę, ponieważ opisuje aktualizację jako automatyczną:
- włączenie zasilania,
- automatyczny start update,
- czerwone/zielone LED,
- pojawienie się Home,
- wyłączenie,
- wyjęcie karty.

To nie opisuje interaktywnego wyboru języka podczas update.

---

# 12. 115 / 144 / 174 — REALNE ANCHORY HOME

Niezależna korelacja z fizycznym Home:
- 115 = dolny prawy przycisk ustawień/menu/zasilania,
- 144 = ikona CO1,
- 174 = ikona CWU.

To jest CORRELATION użytkownika, ale bardzo silna i konkretna.

Firmware-only search nie znalazł jeszcze prostego bezpośredniego writer call-site dla wszystkich trzech.

Ważna korekta:
brak prostego immediate `#115/#144/#174` w pojedynczym miejscu nie oznacza braku na Home.
Resource IDs mogą przechodzić przez:
- tablice,
- registry,
- konfigurację,
- constructor,
- vtable,
- runtime record.

---

# 13. RESOURCE-TABLE FORENSICS

Raw scan pokazuje wiele wystąpień 0x73 / 0x90 / 0xAE:
- 115 = 0x73,
- 144 = 0x90,
- 174 = 0xAE.

W obszarze około `0x0804Fxxx` występują regularne struktury zawierające m.in.:
- 0x73,
- 0x90,
- 0xAE,
- 0xA0,
- 0xA1,
- 0xAA,
- 0xAB,
- 0xAC,
- 0xAD,
- 0xAF,
- 0xB8,
- 0xBA,
- 0xBD.

To wygląda jak obszar danych/descriptorów/resource mappings, a nie prosty zestaw pojedynczych immediate writerów.

To jest nowy kierunek:
**zamiast szukać tylko literalnego `movs #resource`, trzeba zamknąć format tych rekordów i znaleźć konsumenta tabeli.**

---

# 14. HOME — CO JEST JUŻ NAPRAWDĘ ZAMKNIĘTE

Twarde / bardzo mocne:

- ekranowa przestrzeń ma 480x272,
- 115 jest realnym Home assetem,
- 144 jest realnym Home assetem,
- 174 jest realnym Home assetem,
- 47290 ma sześć pionowych slotów,
- 47290 nie jest widocznym pionowym menu Home,
- 47290 używa 151/152,
- teksty 47290 są dynamiczne,
- menu ma 21 selector records,
- access != 0 odblokowuje rekordy 15..20,
- selector 90 = Language,
- firmware ma parametr Language ID 3,
- firmware ma 8 tabel językowych.

Nie jest zamknięte:

- exact Home tile factory,
- X/Y/W/H wszystkich Home tiles,
- parent chain 115,
- parent chain 144,
- parent chain 174,
- połączenie selector 90 -> konkretny screen class,
- połączenie selector 90 -> 47290,
- sześć TypedText IDs 47290,
- semantyka slotów 47290,
- updater factory/navigation,
- mapper Language value 0..30 -> language table.

---

# 15. KONTRADYKCJA STARYCH HIPOTEZ

### Odrzucone

1. 47290 = dolny pasek Home.
   - ODRZUCONE geometrycznie i przez obserwację użytkownika.

2. 47290 = sześć poziomych kafelków.
   - ODRZUCONE: Y rośnie 50,84,118,152,186,220.

3. 47290 = wykres.
   - ODRZUCONE resource pair: 151/152, nie 056/057.

4. 47290 = na pewno language selector.
   - NIEZAMKNIĘTE.

5. 47290 = na pewno updater language screen.
   - NIEZAMKNIĘTE, obecnie słabe.

6. 0803E5AC = wyłącznie prosty Home renderer.
   - ODRZUCONE jako zbyt mocne. To duży runtime screen/model host.

---

# 16. NAJWAŻNIEJSZY NASTĘPNY ATAK

Nie robić kolejnego przebiegu geometrii 47290 — geometria jest zamknięta.

Priorytet A:
`0803EC18 -> 0803EE30 -> record`

Trzeba zidentyfikować:
- gdzie powstaje record,
- dokładny typ record,
- źródło `record+0x08`,
- wszystkie writer-y tego pola,
- wszystkie warianty sześciu u16 ID.

Priorytet B:
odtworzyć sześć rzeczywistych TypedText IDs:
`param_7[0..5]`.

Dopiero wtedy:
`ID -> 8 language tables -> konkretne słowa`.

Jeżeli otrzymamy:
- nazwy języków -> language selector zostaje praktycznie zamknięty;
- parametry/error/config -> hipoteza językowa odpada.

Priorytet C:
zamknąć selector 90:
`menu row -> touch -> navigation callback -> screen constructor`.

Priorytet D:
szukać osobnej updater factory po:
- SD/card,
- boot/start path,
- LED state,
- firmware version,
- reset/update request,
- resource 151/152.

Priorytet E:
równolegle zamknąć Home:
`115 / 144 / 174 -> table/registry -> constructor -> parent -> geometry`.

---

# 17. MACIERZ HIPOTEZ PO TYM BATCHU

| Hipoteza | Status | Dlaczego |
|---|---|---|
| 47290 jest pionowym selektorem/listą | HARD | konstruktor + geometria |
| 47290 jest na Home | ODRZUCONE | użytkownik + geometria |
| 47290 jest dolnym paskiem | ODRZUCONE | geometria |
| 47290 jest language selector | OPEN | 6 slotów vs 8 tabel, brak ID |
| 47290 jest updater language selector | WEAK/OPEN | brak factory/navigation proof |
| selector 90 = Language | HARD/STRONG | menu resolver |
| FW parametr 3 = Language | HARD | parametr table + RAM/code |
| FW ma 8 języków | HARD | 8 TypedText tables |
| 115 = Home quick/settings tile | CORRELATION STRONG | obserwacja użytkownika |
| 144 = Home CO1 | CORRELATION STRONG | obserwacja użytkownika |
| 174 = Home CWU | CORRELATION STRONG | obserwacja użytkownika |
| 47290 labels są stałe w konstruktorze | ODRZUCONE | param_7 dynamic |
| 47290 labels pochodzą z runtime record | HARD | record+0x08 -> param_7 |

---

# 18. CONTINUITY — DLA NASTĘPNEGO AGENTA

Nie zaczynać od:
- ponownego dowodzenia geometrii 47290,
- ponownego dowodzenia 151/152,
- ponownego dowodzenia 8 tabel językowych,
- ponownego dowodzenia selector 90 = Language.

Startować tutaj:

`0803EC18
 -> 0803EE30
 -> record
 -> record+0x08
 -> param_7
 -> 47290[0..5]
 -> TypedText IDs
 -> 8 language tables
`

Drugie ramię:

`selector 90
 -> row/callback
 -> navigation
 -> concrete screen/factory
`

Trzecie:

`Home asset 115/144/174
 -> indirect resource resolver
 -> parent constructor
 -> X/Y/W/H
`

Zasada:
**OPEN pozostaje OPEN aż do twardego call/data-flow proof.**

