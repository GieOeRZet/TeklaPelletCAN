# FW2213TK — MASTER STATE / HANDOFF
## Stan po pełnym przeglądzie researchu od początku analizy binarki
Data: 2026-11-19
Repo: GieOeRZet/TeklaPelletCAN
Bazowy HEAD researchu: 4c62108bda512ac6dde84186b9882fa91164355b
NIE zaczynać analizy od zera.

---

# 0. POCHODZENIE DANYCH — CO FAKTYCZNIE ANALIZUJEMY

Badamy firmware panela **IGNEO Touch**, plik **FW2213TK.bin**.

Surowy materiał Ghidra zapisany w repo:
- `firmware/FW2213TK-ghidra/decompiled.c` — dekompilacja 1157 wykrytych funkcji,
- `functions.txt` — lista funkcji,
- `strings.txt` — stringi,
- `firmware/FW2213TK-ghidra/README.md`.

Hash BIN z README Ghidra:
`sha256 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`
Rozmiar: **2 031 616 B**.

To jest **binarka panela**, a nie firmware ESP32-C6 z katalogu `firmware/`.
Nie mieszać:
- FW2213TK = panel / TouchGFX / CANopen / UI / lokalny storage,
- `firmware/` = nasz ESP32-C6 + MCP2515 + API.

Dla kodu i klasycznych danych obowiązuje:
`runtime/Ghidra = 0x08000000 + raw_offset`.

Osobna przestrzeń +0x10000 dotyczy wskaźników części tekstów/assetów. **Nie stosować +0x10000 do funkcji.**

---

# 1. CEL RESEARCHU

Pierwotny cel: zrozumieć prawdziwe działanie FW panela, szczególnie:
1. pełny mechanizm CO1..CO4,
2. jak panel wybiera konkretny obieg,
3. jak wybór UI trafia do parametru CANopen,
4. jak parametr trafia do lokalnego rekordu/storage,
5. jak działa UI/TouchGFX dla Ogrzewanie 1..4,
6. gdzie i jak liczba aktywnych obiegów ogranicza widoczność/funkcjonalność.

Końcowy model ma być wystarczająco dokładny do repliki 1:1, a nie tylko do „ładnego podobieństwa”.

---

# 2. NAJWAŻNIEJSZE ODKRYCIE: COUNT=4

`count=4` w katalogu FW **nie oznacza czterech bajtów parametru**.
Oznacza rodzinę czterech instancji.

Twarde przykłady:
- `0x2032..0x2035` — CH comfort temperature,
- `0x2048..0x204B` — CH eco temperature,
- `0x2064..0x2067` — CH program/mode,
- `0x2126..0x2139...` — harmonogramy,
- `0x2142..0x2145`,
- `0x2166..0x2169`,
- duża grupa `0x22xx`,
- `0x4001..0x4004`,
- `0x400C..0x400F`,
- nazwy obwodów `0x2321/2325/2329` jako rodziny count=4.

Najważniejszy przykład:
`0x2032 -> 0x2033 -> 0x2034 -> 0x2035`
czyli CO1..CO4 dla tego samego parametru.

Potwierdzenie niezależne od samego CSV znajduje się w **kodzie wykonawczym** — patrz §5.

---

# 3. CO2 — POTWIERDZONY ZESTAW INDEKSÓW

Dla rodzin count=4 drugi element jest instancją CO2.

Najważniejsze:
- `0x2033` — CO2 comfort,
- `0x2049` — CO2 eco,
- `0x2065` — CO2 mode, dodatkowo jawnie nazwany w mapie panela jako **Tryb CO 2**,
- `0x2127..0x213F` — CO2 harmonogramy,
- `0x2143`,
- `0x2147`,
- `0x214B`,
- `0x2167`,
- `0x229A`,
- `0x229E`,
- `0x22A2`,
- `0x22A6`,
- `0x22AE`,
- `0x22B2`,
- `0x22B6`,
- `0x22BA`,
- `0x22BE`,
- `0x22C2`,
- `0x22C6/0x22CA/0x22CE`,
- `0x22D2`,
- `0x22D6`,
- `0x22DA`,
- `0x22E6`,
- `0x22EA`,
- `0x22F2`,
- `0x22F6`,
- `0x22FA`,
- `0x22FE`,
- `0x2302/2306/230A/230E/2312/2316/231A`,
- `0x2322/2326/232A`,
- `0x4002`,
- `0x400D`.

To jest twarde na poziomie **indeksu CAN/SDO** dla rodzin count=4.
Nie wolno z tego automatycznie wyliczać adresu RAM CO2 bez ścieżki instancji.

---

# 4. UI TOUCHGFX — CO ZOSTAŁO POTWIERDZONE

Polska baza TypedText zawiera m.in.:
- 57 = Ogrzewanie 1,
- 58 = Ogrzewanie 2,
- 99 = OGRZEWANIE 1,
- 100 = OGRZEWANIE 2,
- 101 = OGRZEWANIE 3,
- 102 = OGRZEWANIE 4,
- 119 = Ogrzewanie obwód 1,
- 120 = Ogrzewanie obwód 2,
- 121 = Ogrzewanie obwód 3,
- 122 = Ogrzewanie obwód 4.

Firmware ma osobne komponenty UI dla co najmniej CO1/CO2:
- komponent „Ogrzewanie 2” — kod wcześniej zlokalizowany w okolicy raw `0x46D2C` / odpowiednia przestrzeń UI,
- komponent „Ogrzewanie 1” — okolice raw `0x4B618`.

W pokazanych fragmentach oba używają wspólnego RAM-u prezentacyjnego `0x200247C8`, ale to **nie oznacza wspólnego zestawu parametrów**.

W firmware są też konstrukcje ustawiające teksty parametrów CO:
- TypedText 172 — współczynnik korekcji t. CO,
- TypedText 179 — stała pompa,
- TypedText 159 — temperatura maksymalna,
- TypedText 170 — temperatura CO dla 0°C,
- TypedText 171 — temperatura CO dla 10°C.

Nie utożsamiać pojedynczego konstruktora/reużywalnego komponentu z pełnym ekranem CO.

---

# 5. KLUCZOWY DOWÓD: PRAWDZIWY MECHANIZM INSTANCJI W KODZIE

To jest obecnie najważniejszy fragment całej analizy.

## 5.1 Globalny bieżący obiekt

`FUN_080314ba()` zwraca:
`*DAT_08031a8c`.

`FUN_08031478()` zeruje `DAT_08031a8c` i jego pola pomocnicze.

Czyli wiele funkcji obiektowych pobiera **aktualny obiekt modułu** przez `FUN_080314ba()`.

## 5.2 Pole instancji

W aktualnym decompiled.c:
- offset **+0x12B = +299** — klasyfikacja/typ obiektu,
- offset **+0x12C = +300** — **konkretny numer instancji**.

Nie mieszać ich.

## 5.3 C064 — klasyfikacja i materializacja instancji

`FUN_0803C064(param_1,param_2)` robi:

`class = DAT_0803C218[param_2]`

Dla klas 1..4:
- class 1 -> `+0x12B = 1`, `+0x12C = 1`
- class 2 -> `+0x12B = 2`, `+0x12C = 2`
- class 3 -> `+0x12B = 3`, `+0x12C = 3`
- class 4 -> `+0x12B = 4`, `+0x12C = 4`.

Dla innych klas wywołuje inne przygotowanie/deskryptory.

C064 jest więc **dispatcherem klasyfikującym obiekt i ustawiającym jego typ + instancję**.

Nie ma bezpośredniego, literalnego call-site C064 w decompiled.c. Prawdopodobnie wejście jest pośrednie (vtable/callback/data dispatch).

## 5.4 Druga niezależna ścieżka +0x12C

`FUN_08037D00(param_1)` ma własny switch i dla przypadków 1..4 ustawia:
`*(param_1 + 0x12C) = 1..4`.

To jest niezależny dowód, że C064 nie jest jedynym źródłem instancji.

Model:
`klasyfikacja/setup -> +0x12B -> +0x12C -> lookup`.

## 5.5 Konstruktor / singleton

`FUN_08061020()` tworzy obiekt pod `param_1 + 0x2A17`, wywołuje:
- `FUN_08037CA4()`,
- `FUN_08036D60()`,
- `FUN_08037E9C()`.

`FUN_08037CA4()` ustawia vtable-ish pointers i zeruje:
- `+0x129`,
- `+0x12A`,
- `+0x12B`.

`FUN_08037E9C()` ustawia:
- `+0x128 = 1`,
- `+0x12B = 0`,
- `+0x12C = 1`.

To mocno wspiera model **jednego aktualnego obiektu z przełączanym typem/instancją**, a nie czterech niezależnych obiektów UI stale istniejących naraz.

---

# 6. NAJNOWSZE, BARDZO WAŻNE ODKRYCIE: MAPPER MA FIZYCZNIE ZAKODOWANE RODZINY 4-ELEMENTOWE

`FUN_08036FF2(context,param_2)` jest kluczowym mapperem panelowego indeksu.

Kod robi:
1. pobiera aktualny obiekt przez `FUN_080314ba()`,
2. dla pierwszej części tabeli szuka `param_2` w **grupach po 4 wpisy**,
3. po znalezieniu wylicza:
   `base = group_number * 4`,
4. następnie:
   `resolved = base + object[+0x12C] - 1`,
5. przekazuje wynik dalej do `FUN_08037094()`.

Konkretnie w kodzie:
`sVar3 = table_base + (group_index << 2) + (byte)(object+0x12C) - 1`.

To jest **bezpośredni kod implementujący count=4 / instance 1..4**. Uwaga korekcyjna: starsza notatka C064 podawała 31 pozycji dla tej tabeli; bieżący `decompiled.c` ma literalnie `iVar2 = 0x31` w `FUN_080370C0/0803716E`, czyli **49** pozycji. Aktualny decompiled.c ma pierwszeństwo.

Dalsza część mappera ma osobny obszar singletonów:
- pierwsza część: **49 grup po 4**,
- druga część: **0x174 = 372 pojedyncze wpisy**.

Czyli architektura mappera jest faktycznie rozdzielona na:
`4-way families` + `singletons`.

To jest znacznie mocniejsze niż samo oznaczenie `count=4` w CSV.

---

# 7. PEŁNY ŁAŃCUCH: PANEL INDEX -> INSTANCJA -> REKORD PARAMETRU

To jest aktualnie najbardziej konkretny przepływ.

### A. Panelowy indeks
`FUN_08036FF2(context, panel_index)`

### B. Rodzina
Pierwsza część tabeli `DAT_08037B4C...` zawiera rodziny po 4 panelowe wpisy.

### C. Instancja
`object + 0x12C`:
- 1 -> +0,
- 2 -> +1,
- 3 -> +2,
- 4 -> +3.

### D. Rozwiązany indeks wewnętrzny
Mapper przekazuje `sVar3` do `FUN_08037094()`.

### E. Record table
`FUN_08037094()` wywołuje:
`FUN_080115F6(&local, DAT_0803754C, resolved_index)`.

`FUN_080115F6()` przeszukuje rekordy:
- rekord stride = **0x2C bajta**,
- pierwszy CAN/index field = `record+0x08`,
- następny = `record+0x2C),
- kolejny = `record+0x58), itd. (grupowanie po 4 rekordy),
- `record+0x0C` = wskaźnik źródła/storage,
- `record+0x10` = typ,
- `record+0x14` = wartość/deskryptor używany przez accessor,
- `record+0x1C` i `+0x24` = kolejne wartości/metadata.

### F. Odczyt wartości
`FUN_0801167A()` znajduje rekord po resolved index i czyta:
`record + 0x14`.

`FUN_080116E6()` analogicznie czyta:
`record + 0x1C`.

### G. Zapis wartości
`FUN_08037212(context,param_2,value)` wykonuje ten sam mechanizm rodziny 4:
- pobiera bieżące `object+0x12C`,
- dla pierwszej tabeli wylicza `base + instance - 1`,
- następnie wywołuje `FUN_08011812()` na rozstrzygniętym rekordzie/indexie.

To oznacza, że `+0x12C` nie jest tylko selektorem odczytu UI. Ten sam selektor uczestniczy również w **zapisie parametru**. To jest twardy dowód dwukierunkowego mechanizmu instancji.

To daje konkretny most:
**panelowy indeks -> grupa 4 -> +0x12C -> resolved index -> rekord 0x2C -> wartość**.

To jest obecnie jeden z najważniejszych dowodów całego researchu.

---

# 8. REJESTRACJA REKORDÓW — POPRAWNE ADRESY

Wcześniejsze notatki używały omyłkowo adresów `0x0802167A/0x0802143C`.
W aktualnym `decompiled.c` prawidłowe funkcje to:

- **`FUN_0801143C`** — rejestracja rekordu,
- **`FUN_080115F6`** — lookup rekordu / metadata,
- **`FUN_0801167A`** — accessor wartości z `+0x14`,
- **`FUN_080116E6`** — accessor wartości z `+0x1C`.

`FUN_0801143C()`:
- wyszukuje wolny rekord co 4 pozycje,
- zapisuje `record+0x08 = param_2`,
- `record+0x0C = param_3`,
- zapisuje metadata pod +0x14/+0x1C/+0x24,
- `record+0x10 = param_4`.

Nie wolno wracać do `0x0802143C/2167A` jako adresów funkcji.

---

# 9. PANEL HEATING UI — 12 PARAMETRÓW

`FUN_0803E714()` dla klas/typów 1..4 wspólnie dodaje:
`FUN_0803EFDA(param_1, DAT_0803EEC0 + 0x62, 0x0C)`.

`FUN_0803EFDA()` kopiuje 12 kolejnych 16-bitowych ID do listy UI pod `param_1+0x20`, zwiększając licznik `+0xE8`.

Wszystkie te ID przechodzą dalej przez mechanizm `FUN_08036FF2()`, więc aktywna instancja obiektu może zmieniać właściwy parametr.

Dodatkowa lista 11 parametrów jest dołączana, gdy `+0x158 != 0`.

`+0x158` NIE jest numerem obwodu.
`FUN_08037E74(param_1,param_2)` mapuje:
- 0 -> +0x158 = 0,
- 900 -> 1,
- 999 -> 2,
- 0x1BF1 -> 3.

To jest osobna bramka trybu/poziomu UI.

---

# 10. 0x2105 — CO WIEMY, A CZEGO NIE WIEMY

Panel index:
- `0x10F` -> CAN `0x2105`,
- nazwa: **Heating configuration**,
- u8,
- zakres 0..4,
- default 1,
- storage panela: `0x20021FAF`.

`FUN_08031CCC()` pobiera 0x10F przez `FUN_08036FF2()` i używa wartości do:
- `FUN_0802D3E0()`,
- `FUN_0802D91C()`.

Czyli **0x2105 realnie steruje UI**. W `FUN_08031CCC` dokładnie ten sam mapper `FUN_08036FF2()` pobiera `0x10E` i `0x10F`: `0x10E` steruje dwoma warunkami widoczności (`>0`, `>1`), a `0x10F` jest przekazywane do `FUN_0802D3E0()` i `FUN_0802D91C()`.

Jednocześnie nie znaleziono dowodu:
`0x2105 -> create N CO objects`.

Aktualny model:
- `count=4` = pojemność mechanizmu,
- `+0x12C` = konkretny numer instancji,
- `0x2105` = funkcjonalna konfiguracja Heating,
- liczba aktywnych obwodów jest nadrzędnym stanem/warunkiem, którego dokładny most do obiektów CO nadal szukamy.

**BARDZO PRAWDOPODOBNE**, ale jeszcze nie [FW]:
0x2105 odpowiada liczbie/konfiguracji aktywnych obwodów CO 0..4.

Nie wolno tego jeszcze przedstawiać jako twardego faktu implementacyjnego.

---

# 11. WARSTWA SPRZĘTOWA: 3500 / 3502 / 350B / 16C1 / 16D5

Twardo potwierdzone:
- `0x3500` Main module type,
- `0x3502` CH expansion module type,
- `0x350B` Profile number.

Są przechowywane w głównym obiekcie:
- `+0x16BF`,
- `+0x16C0`,
- `+0x16CC`.

Te trzy wartości realnie budują indeks wariantu sprzętowego.

Dla Main=0:
- expansion=0: profile 1/2/3 -> wariant 2/3/4,
- expansion=1: profile 1/2/3 -> wariant 5/6/7.

Dodatkowo:
- `+0x16C1` jest kolejnym polem konfiguracji wpływającym na wybór struktur,
- `+0x16D5` jest innym warunkiem i nie wolno go utożsamiać z 16C1.

Wniosek:
**profil sprzętowy != liczba obiegów CO**.
Warstwa sprzętowa i funkcjonalna muszą być analizowane osobno.

---

# 12. MODEL CO1..CO4 — AKTUALNY

Najlepszy obecnie model:

```
Panel UI
  |
  | panel index
  v
FUN_08036FF2()
  |
  | rodzina 4-elementowa
  v
object + 0x12C
  | 1 / 2 / 3 / 4
  v
resolved internal index
  |
  v
FUN_08037094()
  |
  v
FUN_080115F6()
  |
  v
record table (0x2C stride)
  |
  +--> record+0x08 = CAN/index
  +--> record+0x0C = storage/source
  +--> record+0x10 = type
  +--> record+0x14 = value/descriptor
  +--> record+0x1C = alternate value
  |
  v
FUN_0801167A / FUN_080116E6
  |
  v
wartość / aktualizacja UI
```

Równolegle:
```
classification / dispatch
       |
       v
+0x12B = type/class
+0x12C = instance 1..4
       |
       v
Heating UI / descriptor
```

A osobno:
```
0x3500/3502/350B + 16C1/16D5
       |
       v
wariant sprzętowy / zestaw struktur
```

I jeszcze osobno:
```
0x2105..0x2108
       |
       v
konfiguracja funkcjonalna / widoczność / aktywacja
```

---

# 13. DAT_0803C218 — NADAL OTWARTE

`DAT_0803C218` ma 108 bajtów:
`0x0803C218..0x0803C283`.

C064 używa:
`DAT_0803C218[param_2]`.

Znamy funkcję tablicy:
- wartości 1..4 prowadzą do instancji 1..4,
- dalsze wartości wybierają inne typy obiektów.

Nie mamy jeszcze surowych bajtów tej tablicy w repo.
Nie wolno ich zgadywać.

---

# 14. VTABLE / POŚREDNIE WEJŚCIE DO C064

`FUN_08037CA4()`:
- `*param_1 = DAT_08038694`,
- `*DAT_08038698 = param_1`,
- następnie `*param_1 = DAT_0803869C`.

`FUN_08037C1E()` i `FUN_08037C70()` wykonują wiele wywołań przez vtable slots:
- +0x04,
- +0x08,
- +0x0C,
- +0x10,
- +0x14,
- +0x28.

C064 nie ma bezpośredniego call-site w decompiled.c.
Priorytetem jest więc odzyskanie danych/vtable i znalezienie slotu wskazującego na C064.

Nie wolno zakładać, że brak literalnego call-site oznacza brak użycia.

---

# 15. DAT_0804107C — ODDZIELIĆ OD NORMALNEGO CO

`FUN_08040FC2()` iteruje **22 wpisy**:
- pobiera indeks parametru,
- pobiera konfigurację,
- używa `FUN_08036FF2()`,
- wywołuje `FUN_08040E46()`.

`FUN_08041020()` zapisuje przez:
`FUN_08037212(..., table[param_2*3], ...)`.

To jest realny mechanizm parametrowy, ale obecnie dowody wskazują na **Test I/O / konfigurację testów wyjść**:
- CO1..CO4 pompy,
- CO1..CO4 mieszacze,
- boiler pump,
- blower,
- igniter,
- solar itd.

Nie traktować tego jako źródła normalnego wyboru CO1..CO4 bez dodatkowego połączenia.

---

# 16. REWALIDACJE / TROPY WYCOFANE

## WYCOFANE: 0x38130 / 0x3212C / 0x32146 jako setter instancji
Adresy funkcji kodu są bez +0x10000.

- raw 0x38130 -> runtime 0x08038130,
- raw 0x3212C -> 0x0803212C,
- raw 0x32146 -> 0x08032146.

Nie są one potwierdzonym setterem instancji.

W szczególności stary trop `0x08042146 -> 0x38130` jest wycofany.

## WYCOFANE: 0x10E -> 0x38130
Nie używać.
`0x10E` to panel index -> `0x3505`, ale nie mamy dowodu, że jego setter jest przy 0x38130.

## WYCOFANE: 0x2105 bezpośrednio tworzy +0x12C
Nie znaleziono literalnego kodu implementującego ten most.

## WYCOFANE: count=4 = wszystkie 4 obwody zawsze aktywne
Nie.
count=4 = pojemność/rodzina instancji.
Aktywność musi być osobnym stanem.

---

# 17. WAŻNA KOREKTA STAREGO DOKUMENTU CO2

`rejestry/GHIDRA-FW2213TK-PRZEWODNIK.md` zawiera wcześniejszy, częściowo przestarzały wniosek:
„tylko 7 prostych parametrów ma potwierdzony CO2”.

Ten wniosek jest **NIEAKTUALNY** po odkryciu count=4 i implementacji mappera 4-way.

Aktualny stan:
- dla rodzin count=4 mamy pełne rodziny indeksów CAN/SDO,
- mechanizm +0x12C jest bezpośrednio używany w kodzie mappera,
- nadal nie mamy kompletnej mapy RAM dla każdego CO2.

Stary dokument nie powinien być traktowany jako aktualny stan researchu.

---

# 18. WNIOSKI ARCHITEKTONICZNE

1. Panel nie przechowuje CO1..CO4 jako czterech niezależnych kopii UI.
2. Ma **wspólny mechanizm obiektu + selector instancji**.
3. Parametry wieloinstancyjne są rozwiązywane dynamicznie.
4. Rodziny 4-way są zakodowane w tabeli mappera, nie tylko opisane w CSV.
5. Rekordy parametrów mają stride 0x2C.
6. Instancja jest dodawana **przed** lookupiem rekordu.
7. To tłumaczy, dlaczego CO2/3/4 mogą mieć kolejne CAN-ID bez konieczności czterech osobnych konstruktorów parametru.
8. UI może mieć osobne komponenty „Ogrzewanie 1/2/3/4”, ale ich parametry mogą korzystać ze wspólnego silnika instancji.
9. Warstwa sprzętowa (Main/Expansion/Profile) i warstwa funkcjonalna (Heating configuration) nie są tym samym.
10. 0x2105 jest realnym wejściem UI, ale dokładny most do aktywnych instancji pozostaje otwarty.

---

# 19. NASTĘPNE CELE — KOLEJNOŚĆ, BEZ WRACANIA DO ZAMKNIĘTYCH TEMATÓW

### PRIORYTET 1 — odzyskać DAT_08037B48 / DAT_08037B4C
To da możliwość powiązania:
panel index -> grupa 4 -> base index.

Jeżeli odzyskamy surową tabelę, można wyliczyć dokładny resolved index dla każdego CO1..CO4.

### PRIORYTET 2 — odzyskać DAT_0803C218
Potrzebne do mapowania:
param_2 -> class 1/2/3/4 -> instancja.

### PRIORYTET 3 — znaleźć pośrednie wejście do C064
Przejrzeć vtable/data przy:
- 0x08038694,
- 0x08038698,
- 0x0803869C,
- region 0x08037C00..0x080386xx.

### PRIORYTET 4 — odzyskać DAT_0803EEC0
Potrzebne są rzeczywiste 12 ID z:
`DAT_0803EEC0 + 0x62`
oraz 11 ID z:
`+0x6E`.

### PRIORYTET 5 — 0x2105
Po rozwiązaniu mappera i C064 wrócić do:
- kto ustawia wartość 0x2105,
- czy 0/1/2/3/4 ogranicza widoczność CO1..CO4,
- czy 3502/16C1/16D5 dodatkowo ograniczają aktywność.

### PRIORYTET 6 — UI 1:1
Dla każdego CO:
parent -> child -> vptr -> TypedText/bitmap -> X/Y/W/H -> callback -> panel index -> instance -> CAN.

---

# 20. INSTRUKCJA DLA KOLEJNEGO CHATA / AGENTA

**Nie zaczynać od ponownego odkrywania count=4, 0x12B/0x12C ani podstawowego UI.**
Są zamknięte.

**Nie wracać do wycofanych adresów 0x38130/0x3212C/0x32146 ani starego 0x42146.**

Najbardziej wartościowy aktualnie łańcuch do kontynuacji:
```
panel index
 -> FUN_08036FF2
 -> DAT_08037B4C family-of-4
 -> +0x12C - 1
 -> FUN_08037094
 -> FUN_080115F6
 -> 0x2C record
 -> FUN_0801167A / 080116E6
 -> value
```

Równoległy:
```
param_2
 -> DAT_0803C218[param_2]
 -> class 1..4
 -> +0x12B/+0x12C
```

I:
```
3500/3502/350B/16C1/16D5
 -> hardware variant
```

oraz:
```
2105
 -> UI/configuration
 -> ? active CO count
```

Każdy kolejny większy commit/notatka ma zawierać:
1. stan już potwierdzony,
2. wszystkie istotne korekty/wycofania,
3. nowe dowody,
4. wnioski,
5. dokładny punkt zatrzymania,
6. następne konkretne adresy/funkcje,
7. wyraźne oddzielenie [FW] / [STRONG INFERENCE] / [HYPOTHESIS].

Nie tworzyć małych notatek typu „znaleziono jeden adres”. Konsolidować kilka sukcesów w jeden większy handoff.


# 21. NADRZĘDNY CEL PROJEKTU — PANEL 1:1 / REIMPLEMENTACJA ESP

Cel projektu został doprecyzowany i ma pierwszeństwo przed pojedynczymi tropami reverse-engineeringu:

**Odtworzyć działanie całego panelu FW2213TK we własnym sofcie na ESP, możliwie 1:1.**

„1:1” oznacza nie tylko wygląd. Docelowo trzeba odtworzyć:
- ekrany, bitmapy, teksty, fonty, pozycje X/Y, W/H, kolejność warstw i stany widoczności,
- nawigację, callbacki, przyciski, gesty/touch i przejścia między ekranami,
- konfigurację i warunki pojawiania się elementów,
- inicjalizację/startup, boot, błędy i stany pośrednie,
- parametry CAN, indeksy, rejestry, typy, zakresy, wartości domyślne, zapis/odczyt,
- zależności między parametrami,
- CO1..CO4 i wszystkie mechanizmy instancjonowania,
- warianty sprzętowe i konfiguracje funkcjonalne,
- tryby pracy, menu serwisowe/testowe, wejścia/wyjścia,
- alarmy, statusy, timery i automaty stanu,
- komunikację CAN/CANopen i mapowanie danych,
- persistent storage / konfigurację lokalną,
- logikę ograniczania/opcji dostępnych w UI,
- zachowanie po braku/obecności modułów i różnych konfiguracjach,
- pełne zależności między warstwą UI, logiką aplikacji i CAN.

### Zasada prowadzenia reverse-engineeringu

Nie optymalizować pracy pod „najbliższy mały wynik”. Priorytetem jest **zrozumienie całego softu**.

Kolejność śledztwa może być zmieniana dynamicznie. Jeżeli jakiś inny obszar daje szybciej twarde zależności potrzebne do repliki panelu, należy go analizować przed obecnym lokalnym tropem.

Jednocześnie nie porzucać głównego celu CO/instancji — jest on jednym z fundamentów repliki.

### Docelowa mapa systemu

Reverse engineering ma doprowadzić do mapy:

```
BOOT / INIT
  ↓
HW / MODULE DISCOVERY
  ↓
CONFIG / PERSISTENT STATE
  ↓
CAN / PARAMETER ENGINE
  ↓
APPLICATION STATE MACHINE
  ↓
SCREEN / MENU DISPATCH
  ↓
WIDGET TREE
  ↓
BITMAP / TEXT / GEOMETRY
  ↓
TOUCH / CALLBACK
  ↓
PARAMETER READ/WRITE
  ↓
CAN / STORAGE / SIDE EFFECTS
```

Każdy ważny element powinien być docelowo opisany w kategoriach:
**wejście → warunek → funkcja → stan → wyjście → efekt uboczny → zależności.**

### Status oznaczeń

- **[FW]** — bezpośrednio potwierdzone w binarce/dekompilacji.
- **[DATA]** — bezpośrednio potwierdzone w surowych danych/tabeli/assetach.
- **[STRONG]** — bardzo mocny wniosek z kilku niezależnych dowodów.
- **[HYPOTHESIS]** — hipoteza wymagająca potwierdzenia.

Hipotez nie mieszać z faktami w dokumentacji.

### Strategia

Nie trzeba rozpracowywać każdego bajtu liniowo. Najpierw budować „kręgosłup” systemu:
1. startup i inicjalizacja,
2. globalny model obiektów,
3. parameter engine / CAN,
4. UI dispatcher i ekrany,
5. widget/bitmap/text geometry,
6. callbacki/touch,
7. zależności i konfiguracja,
8. moduły serwisowe/testowe,
9. dopiero potem drobne funkcje i edge cases.

Każdy kolejny duży commit ma zachowywać pełny stan projektu, a następnie dodawać nowe dowody i instrukcję kontynuacji. Nie tworzyć izolowanych notatek, które zmuszają kolejnego agenta do odtwarzania kontekstu.


# 22. NOWY PUNKT KRYTYCZNY — STARTUP / UTWORZENIE GŁÓWNEGO OBIEKTU PANELU

W dalszym trace po całym firmware znaleziono konkretny łańcuch tworzenia warstwy aplikacyjnej panelu.

## 22.1 FUN_0805fd2a — utworzenie głównego obiektu UI/aplikacji

FUN_0805fd2a() wywołuje:

    FUN_0806024c(
        DAT_0805ff38 + 8,
        DAT_0805ff38 + 0xAB4,
        DAT_0805ff38 + 0xAB0,
        0x1E0,
        0x110,
        0, 0, 0
    )

Twarde:
- 0x1E0 = 480,
- 0x110 = 272.

Czyli firmware ma jawnie zakodowaną rozdzielczość/obszar panelu 480×272 w ścieżce tworzenia obiektu.

Po utworzeniu obiektu:
- wywoływany jest vtable slot +0x6C z argumentami 0xC0000000, 0x10, 1, 1,
- object+0x14 = 2,
- object+0x10 = 10.

## 22.2 FUN_0806024c — wejście aplikacji

FUN_0806024c():
1. tworzy/pobiera obiekt przez FUN_08060fd4(),
2. wykonuje FUN_080561B0(),
3. pobiera dwa obiekty przez FUN_0805444A() / FUN_08054444(),
4. przekazuje je do FUN_080342B4(),
5. wykonuje FUN_080391D6(0),
6. zapisuje DAT_080602B4 do DAT_080602B8 (+4),
7. ustawia globalny kontekst przez FUN_08061014(iVar1),
8. jednorazowo tworzy główny obiekt aplikacyjny przez FUN_08061020(DAT_080602C0),
9. przekazuje wynik do FUN_0800DD22(...),
10. pobiera aktualny obiekt przez FUN_080314BA(),
11. wywołuje na obiekcie vtable slot +0x4C.

To pokazuje, że FUN_08061020 jest częścią jednorazowej inicjalizacji głównego obiektu aplikacyjnego.

## 22.3 FUN_08061020 — skład głównego obiektu

FUN_08061020(param_1) buduje strukturę obejmującą:
- param_1,
- pod-obiekty przy +0x14, +0x108, +0xA7FC,
- główny obiekt modułu przy param_1 + 0x2A17.

Następnie:
- FUN_08037CA4(puVar1, param_1+0x2A70, param_1),
- FUN_08036D60(param_1+0x2A70),
- FUN_08037E9C(puVar1).

Czyli wcześniej zidentyfikowany obiekt z +0x12B/+0x12C jest rzeczywiście tworzony w głównym obiekcie aplikacyjnym podczas inicjalizacji.

## 22.4 Startup/UI hardware — FUN_0805fd78

FUN_0805fd78() wykonuje m.in.:
- FUN_080602CC() — konfiguracja,
- FUN_0805FBB2() — konfiguracja kontrolera/display,
- FUN_0806075E(...,1),
- FUN_08060770(1),
- FUN_0806069C(1),
- FUN_08056B0C(),
- FUN_0806089E(),
- FUN_08060A14(),
- FUN_08060A60(),
- FUN_08060AFC(),
- FUN_08060B6C(0x7D),
- FUN_08060CB0(),
- FUN_08018A9C(0x100,1).

To jest mocny kandydat na łańcuch inicjalizacji sprzętu/display/TouchGFX, a nie logikę menu.

## 22.5 FUN_0805FBB2 — ustawienia sprzętowe panelu

W FUN_0805FBB2() występują jawne wartości związane z konfiguracją wyświetlania:
- 0x3C3,
- 0x3C0,
- 0x110,
- 0x11B,
- 0x20A/20B,
- 0x21C,
- 0x120,
- 0x28,
- 0x2B.

Nie przypisywać im jeszcze znaczeń X/Y/W/H bez rozpoznania struktur FUN_08060604 / FUN_080606C8. To jest następny trop do geometrycznej rekonstrukcji panelu.

## 22.6 Wniosek dla repliki ESP

Mamy teraz trzy rozdzielone warstwy:

    FUN_0805fd78
       ↓
    hardware/display/TouchGFX init
       ↓
    FUN_0805fd2a
       ↓
    FUN_0806024c
       ↓
    FUN_08061020
       ↓
    główny obiekt aplikacyjny
       ↓
    FUN_08037CA4 / FUN_08037E9C
       ↓
    obiekt +0x12B/+0x12C
       ↓
    parameter engine / CAN / UI

Dla własnego ESP trzeba odtworzyć te warstwy osobno:
1. display geometry,
2. root/application object,
3. state/config,
4. parameter engine,
5. screen/widget tree.

Nie kopiować architektury binarki mechanicznie — odtwarzamy zachowanie, ale te granice są ważne dla poprawnej repliki.

## 22.7 Następne priorytety po tym odkryciu

1. FUN_08060604 — ustalić strukturę parametrów geometrycznych.
2. FUN_080606C8 — ustalić pola descriptorów display/widget.
3. FUN_0805fd2a / FUN_0806024c — odzyskać root object i pierwszą warstwę ekranów.
4. Trace vtable slot +0x4C po FUN_080314BA().
5. Trace FUN_080561B0, FUN_080342B4, FUN_0805444A, FUN_08054444.
6. Równolegle kontynuować DAT_08037B4C, DAT_0803C218, C064.
7. Odnalezione geometrie łączyć z bitmapami web/img/panel/*.png tylko po potwierdzeniu źródła bitmapy.

Nie traktować 0x3C0/0x3C3/0x20A/0x20B jako wymiarów widgetów bez dalszego trace.
