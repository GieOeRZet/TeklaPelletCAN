# CO2 — pełny zestaw parametrów względem CO1 (2026-11-18)

## Najważniejsze odkrycie

W `panel-fw-parametry-FW2213TK.csv` kolumna `count=4` nie oznacza czterech bajtów parametru. Oznacza cztery instancje tego samego parametru dla obiegów. Potwierdza to jednocześnie:

- wspólny RAM bazowy dla parametrów CO i kolejne adresy SDO,
- katalog `katalog-rejestrow.csv`, gdzie po nazwanym CO1 występują kolejne adresy `+1,+2,+3`,
- identyczny wzorzec dla temperatur, trybów i harmonogramów,
- firmware ma cztery elementy w pamięci dla pól oznaczonych `count=4`.

Przykład:
`0x2032` = CH comfort set, count=4, RAM `0x20020964`.
Katalog ma następnie `0x2033`, `0x2034`, `0x2035` z tym samym zakresem.
Analogicznie `0x2142` ma count=4, więc instancje to `0x2142..0x2145`.

**Wniosek:** dla parametrów rzeczywiście zarejestrowanych jako `count=4`, CO2 jest instancją **CO1 + 1**. To jest znacznie mocniejszy dowód niż wcześniejsze założenie, że tylko siedem prostych rejestrów ma odpowiednik CO2.

## CO1 → CO2

| CO1 | CO2 | Parametr z FW panela | Typ | Zakres | Pewność |
|---|---|---|---|---|---|
| 0x2032 | 0x2033 | Temperatura komfortowa CO | u16 | 150..300 | **wysoka** — count=4 |
| 0x2048 | 0x2049 | Temperatura ekonomiczna CO | u16 | 100..300 | **wysoka** — count=4 |
| 0x2064 | 0x2065 | Tryb/program CO | u8 | 0..3 | **wysoka** — count=4 + osobne nazwanie CO2 |
| 0x2126 | 0x2127 | Harmonogram poniedziałek | u32 | 0..16777215 | **wysoka** — count=4 |
| 0x212A | 0x212B | Harmonogram wtorek | u32 | 0..16777215 | **wysoka** — count=4 |
| 0x212E | 0x212F | Harmonogram środa | u32 | 0..16777215 | **wysoka** — count=4 |
| 0x2132 | 0x2133 | Harmonogram czwartek | u32 | 0..16777215 | **wysoka** — count=4 |
| 0x2136 | 0x2137 | Harmonogram piątek | u32 | 0..16777215 | **wysoka** — count=4 |
| 0x213A | 0x213B | Harmonogram sobota | u32 | 0..16777215 | **wysoka** — count=4 |
| 0x213E | 0x213F | Harmonogram niedziela | u32 | 0..16777215 | **wysoka** — count=4 |
| 0x2142 | 0x2143 | Tryb pracy CO: ręczny/pogodowy | u8 | 0..1 | **wysoka** — count=4 |
| 0x2146 | 0x2147 | Temperatura zadana ręczna | u8 | 20..80 | **wysoka** — count=4 + osobny wpis CO2 |
| 0x214A | 0x214B | Test mieszacza | u8 | 0..2 | **wysoka** — count=4 + osobny wpis CO2 |
| 0x2166 | 0x2167 | CH result/res | s16 | 0..500 | **wysoka** — count=4 |
| 0x2299 | 0x229A | Stan pompy CO | u8 | 0..1 | **wysoka** — count=4 + osobny wpis CO2 |
| 0x229D | 0x229E | Test pompy CO | u8 | 0..2 | **wysoka** — osobny wpis CO2; wzorzec +1 |
| 0x22A1 | 0x22A2 | Typ czujnika pokojowego | u8 | 0..5 | **wysoka** — count=4 |
| 0x22A5 | 0x22A6 | Użycie czujnika CO | u8 | 0..1 | **wysoka** — count=4 |
| 0x22AD | 0x22AE | Temperatura zadana wynikowa | s16 | 10..90 | **wysoka** — count=4 + osobny wpis CO2 |
| 0x22B1 | 0x22B2 | Zwiększenie temperatury źródła | u8 | 0..30 | **wysoka** — count=4 |
| 0x22B5 | 0x22B6 | Czas mieszacza | u16 | 60..360 s | **wysoka** — count=4 |
| 0x22B9 | 0x22BA | Stan mieszacza | u8 | 0..2 | **wysoka** — count=4 |
| 0x22BD | 0x22BE | Histereza obiegu | u8 | 0..50 | **wysoka** — count=4 |
| 0x22C1 | 0x22C2 | Kalibracja czujnika pokojowego | s16 | -30..30 | **wysoka** — count=4 |
| 0x22C5 | 0x22C6 | Krzywa pogodowa dla -20°C | u8 | 20..80 | **wysoka** — count=4 |
| 0x22C9 | 0x22CA | Krzywa pogodowa dla 0°C | u8 | 20..80 | **wysoka** — count=4 |
| 0x22CD | 0x22CE | Krzywa pogodowa dla +10°C | u8 | 20..80 | **wysoka** — count=4 |
| 0x22D1 | 0x22D2 | Źródło CO: kocioł/bufor | u8 | 0..1 | **wysoka** — count=4 |
| 0x22D5 | 0x22D6 | Temperatura maksymalna CO | u8 | 30..80 | **wysoka** — count=4 |
| 0x22D9 | 0x22DA | Współczynnik korekcji temperatury CO | u8 | 0..20 | **wysoka** — count=4 |
| 0x22E5 | 0x22E6 | Obniżenie temperatury CO | u8 | 0..40 | **wysoka** — count=4 |
| 0x22E9 | 0x22EA | Minimalna temperatura CO dla pomp | u8 | 20..60 | **wysoka** — count=4 |
| 0x22F1 | 0x22F2 | Stała pompa | u8 | 0..1 | **wysoka** — count=4 |
| 0x22F5 | 0x22F6 | Temperatura wymagana CO | u16 | 0..150 | **wysoka** — count=4 |
| 0x22F9 | 0x22FA | Obniżenie Tco dla ochrony powrotu | u8 | 0..1 | **wysoka** — count=4 |
| 0x22FD | 0x22FE | Status CO | u8 | 0..255 | **wysoka** — count=4 |
| 0x2301 | 0x2302 | Stan termostatu CO | u8 | 0..1 | **wysoka** — count=4 |
| 0x2305 | 0x2306 | Korekta zadanej temperatury pokojowej | s16 | -110..40 dC | **wysoka** — count=4 |
| 0x2309 | 0x230A | Napięcie baterii radiowego czujnika pokojowego | u16 | 0..65535 mV | **wysoka** — count=4 |
| 0x230D | 0x230E | Sygnał radiowego czujnika pokojowego | u8 | 0..255 | **wysoka** — count=4 |
| 0x2311 | 0x2312 | Czas od ostatniego odbioru czujnika radiowego | u16 | 0..65535 | **wysoka** — count=4 |
| 0x2315 | 0x2316 | Automatyczne rozpoznanie lata | u8 | 0..1 | **wysoka** — count=4 |
| 0x2319 | 0x231A | Wersja software czujnika radiowego — przed kropką | u8 | 0..255 | **wysoka** — count=4 |
| 0x2321 | 0x2322 | Nazwa obwodu — część 1 | u32 | 0..0xFFFFFFFF | **wysoka** — count=4 |
| 0x2325 | 0x2326 | Nazwa obwodu — część 2 | u32 | 0..0xFFFFFFFF | **wysoka** — count=4 |
| 0x2329 | 0x232A | Nazwa obwodu — część 3 | u32 | 0..0xFFFFFFFF | **wysoka** — count=4 |
| 0x4001 | 0x4002 | Temperatura zmierzona CO | s16 | -100..1500 | **wysoka** — count=4 + osobny wpis CO2 |
| 0x400C | 0x400D | Punkt krzywej dla -10°C | u8 | 20..80 | **wysoka** — count=4 |

## Ważne wyjątki

Nie wolno automatycznie dopisywać `+1` do każdego adresu występującego w naszej aplikacji.

Szczególnie:

- `0x22DD` — CO1 MAX Tzew pomp komfort
- `0x22E1` — CO1 MAX Tzew pomp ekonomiczny

są obecne w naszym katalogu/warstwie aplikacyjnej i są potwierdzone jako parametry CO1, ale **nie występują w tabeli rejestracji FW panela z `count=4`**. Dla nich nie mamy jeszcze tak mocnego dowodu, że `0x22DE` i `0x22E2` są CO2. W katalogu sąsiadujące adresy istnieją, ale ich semantyka nie została jeszcze potwierdzona z firmware panela.

To samo dotyczy każdego parametru, którego nie ma w `panel-fw-parametry-FW2213TK.csv` jako `count=4`.

## Co to zmienia względem wcześniejszej analizy

Wcześniejszy dokument `GHIDRA-FW2213TK-PRZEWODNIK.md` mówił, że tylko 7 prostych parametrów ma potwierdzony odpowiednik CO2. Ta teza jest teraz **nieaktualna** dla parametrów z `count=4`.

Nowy dowód z firmware panela pokazuje pełne rodziny czterech instancji. Dla nich CO2 nie jest „brakującym rejestrem”, tylko kolejną instancją tego samego parametru.

Następny etap: odnaleźć w kodzie TouchGFX, gdzie wybierany jest numer instancji obiegu. Wtedy będziemy mogli powiązać:
**ekran CO1/CO2 → TypedText → widget → numer instancji → indeks SDO → adres CO2**,
a następnie odtworzyć ekran 1:1.


## Nowe potwierdzenie z kodu UI — osobne komponenty dla „Ogrzewanie 2” i „Ogrzewanie 1”

W kolejnym przebiegu znaleziono dwa bardzo podobne konstruktory, których Ghidra nie wpisał do `functions.txt` jako osobnych funkcji, ale kod jest jednoznaczny:

### Komponent CO2 / „Ogrzewanie 2”

**Ghidra:** `0x08046D2C`

Najważniejszy fragment:
- `movs r0,#0x3A`
- zapis ID na stos,
- `r5 = r4 + 0xA4`,
- `FUN_080313A4(r5, 0x3A)`.

TypedText ID `58 = Ogrzewanie 2`.

Dodatkowo:
- `[r4+0x12A] = 2`,
- `[r4+0xAC] = *0x200247C8`,
- dalsza część konstruktora tworzy/konfiguruje kolejne obiekty pod offsetami `+0x8B4`, `+0x8E8`, `+0x8EC`, `+0x924`, `+0x930` itd.

### Komponent CO1 / „Ogrzewanie 1”

**Ghidra:** `0x0804B618`

Najważniejszy fragment:
- `movs r0,#0x39`
- zapis ID na stos,
- `r5 = r4 + 0xA4`,
- `FUN_080313A4(r5, 0x39)`.

TypedText ID `57 = Ogrzewanie 1`.

Dodatkowo:
- `[r4+0x12A] = 2`,
- `[r4+0xAC] = *0x200247C8`,
- dalsza struktura jest bardzo podobna do komponentu 0x08046D2C.

### Wniosek

To jest znacznie mocniejszy dowód niż samo występowanie tekstów w bazie.

**[FW]** Firmware zawiera dwa osobne, bardzo podobne komponenty UI:
- `0x08046D2C` → TypedText 58 → **Ogrzewanie 2**,
- `0x0804B618` → TypedText 57 → **Ogrzewanie 1**.

**[SILNA INFERENCJA]** Są to komponenty odpowiadające dwóm pozycjom/elementom UI związanym z obwodami ogrzewania. Ich dokładne miejsce na Home Screen (np. dolny pasek) wymaga jeszcze prześledzenia referencji do konstruktorów/vtable, więc nie przypisujemy im jeszcze współrzędnych ekranu.

Istotne: oba komponenty korzystają z tego samego RAM `0x200247C8` w pokazanym fragmencie. Nie oznacza to, że CO1 i CO2 mają ten sam zestaw parametrów; ten adres może być wspólną wartością prezentacyjną.


## Dalszy ślad UI parametrów CO

Znaleziono także konstruktor/fragment UI przy **Ghidra 0x08046164** (Ghidra nie wydzielił go jako osobnej funkcji w functions.txt), który bezpośrednio ustawia:

- TypedText **172** = „Wsp. korekcji t. CO [°C/°C]”
- TypedText **179** = „Stała pompa”

W tym samym komponencie występują również kolejne pola tekstowe i obiekty wartościowe. Konstrukcja jest analogiczna do innych ekranów/komponentów parametrów.

W innym dużym konstruktorze **FUN_0804C410** występują bezpośrednie settery dla:
- TypedText **159** = „Temp. maksymalna [°C]”
- TypedText **170** = „Temperatura CO dla 0°C [°C]”
- TypedText **171** = „Temperatura CO dla 10°C [°C]”

oraz inne pola z tego samego zestawu.

**[FW]** Teksty CO są więc rzeczywiście podpinane do obiektów UI przez kod wykonawczy, a nie tylko przechowywane w bazie TypedText.

**[WAŻNE]** Nie traktujemy jednak jeszcze adresu tych konstruktorów jako „ekranu CO2”. Są to komponenty/reużywalne fragmenty UI. Dopiero znalezienie instancji/indeksu obwodu oraz ścieżki wejścia z Home Screen pozwoli przypisać konkretny obiekt do CO1 albo CO2.

## Korekta adresów: raw-disassembly vs Ghidra/runtime

Wcześniejsze wpisy tego dokumentu używające adresów `0x08046D2C`, `0x0804B618`, `0x0804D948` itd. odnosiły się do **syntetycznych adresów pomocniczego ELF z bazą 0x08000000**.

Po zestawieniu z rzeczywistymi wskaźnikami w BIN właściwa przestrzeń Ghidra/runtime jest przesunięta o `0x10000`:

`Ghidra/runtime = 0x08010000 + raw_offset`

Przykład:
- raw `0x46D2C` → runtime/Ghidra `0x08056D2C`;
- raw `0x4B618` → runtime/Ghidra `0x0805B618`;
- raw `0x4D948` → runtime/Ghidra `0x0805D948`.

W dalszej analizie adresy będą oznaczane jako **raw** i **Ghidra/runtime** osobno. Nie zmienia to samych instrukcji ani wniosków o strukturze kodu; zmienia jedynie ich prawidłową numerację w przestrzeni Ghidra.


## 13. CO2 — granica pewności po ponownym zestawieniu rejestrów

POTWIERDZONE z mapy panel-ID: 0x2065 = ID 168 = Tryb CO 2; 0x2032 = ID 170 = CO temperatura komfort; 0x2048 = ID 171 = CO temperatura eko; 0x2166 = ID 172; 0x2064 = ID 191 = Tryb CO 1; 0x2126 = ID 192 = Harmonogram CO1 poniedziałek.

POTWIERDZONE z rejestru FW: duża grupa parametrów CH ma count=4, m.in. 0x2032, 0x2048, 0x2064, 0x2126..0x213E, 0x2142, 0x2146, 0x214A, 0x2166, 0x22A5..0x22F9, 0x4001 i 0x400C.

WAŻNE: count=4 oznacza cztery instancje w mechanizmie firmware. Nie będę sztucznie tworzył osobnych CAN-ID dla CO2. Dla emulatora trzeba odtworzyć index + instancję.

NIEPOTWIERDZONE: że wszystkie te parametry mają instancję CO2 dokładnie jako +1 względem CO1; że osiem podobnych konstruktorów UI oznacza osiem obwodów; że komponent Ogrzewanie 2 jest pełnym ekranem parametrów. Te punkty wymagają dalszego śledzenia kodu.
