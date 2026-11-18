# Analiza UI głównego panelu — 2026-11-18

## 1. Korekta mapowania adresów

Wcześniejsze notatki mieszały dwa układy adresów. W tej analizie rozdzielamy:

- **offset surowego FW2213TK.bin** — indeks bajtowy w pliku,
- **adres używany przez Ghidra** — adres kodu/danych widoczny w `functions.txt` i `strings.txt`.

Dla analizowanej części obrazu firmware działa praktyczna zależność:

`Ghidra = raw_offset + 0x08010000`

czyli:

`raw_offset = Ghidra_address - 0x08010000`

Dowód bezpośredni:
- tablica TypedText PL znajduje się w pliku przy raw `0x5BD80`;
- odpowiada jej adres Ghidra `0x0806BD80`;
- wpis ID 120 zawiera wskaźnik `0x08098B58`;
- w pliku przy raw `0x88B58` znajduje się dokładnie `Ogrzewanie obwód 2`;
- `0x08098B58 - 0x08010000 = 0x88B58`.

To mapowanie należy stosować przy łączeniu wyników Ghidra z offsetami z surowego BIN.

## 2. Baza tekstów TouchGFX — potwierdzone ID

Polska tablica TypedText ma 495 wpisów i zaczyna się przy raw `0x5BD80`.

Potwierdzone wpisy użyteczne dla rekonstrukcji UI:

| TypedText ID | Tekst PL | raw string |
|---:|---|---:|
| 57 | Ogrzewanie 1 | 0x8EF50 |
| 58 | Ogrzewanie 2 | 0x8EF6C |
| 63 | Wyłączony | 0x92AA8 |
| 96 | MENU | 0x94C38 |
| 99 | OGRZEWANIE 1 | 0x8EFDC |
| 100 | OGRZEWANIE 2 | 0x8EFF8 |
| 101 | OGRZEWANIE 3 | 0x8F014 |
| 102 | OGRZEWANIE 4 | 0x8F030 |
| 119 | Ogrzewanie obwód 1 | 0x88B30 |
| 120 | Ogrzewanie obwód 2 | 0x88B58 |
| 121 | Ogrzewanie obwód 3 | 0x88B80 |
| 122 | Ogrzewanie obwód 4 | 0x88BA8 |
| 150 | Temperatura komfortowa [°C] | 0x7A... |
| 164 | Tryb pracy | 0x... |
| 168 | Temperatura CO dla -20°C [°C] | 0x... |
| 169 | Temperatura CO dla -10°C [°C] | 0x... |
| 170 | Temperatura CO dla 0°C [°C] | 0x... |
| 171 | Temperatura CO dla 10°C [°C] | 0x... |
| 174 | Czas mieszacza [s] | 0x... |
| 175 | Temperatura CO zadana ręcznie [°C] | 0x... |
| 270 | Poniedziałek | 0x... |
| 271 | Wtorek | 0x... |
| 272 | Środa | 0x94CBC |
| 273 | Czwartek | 0x... |
| 274 | Piątek | 0x... |
| 275 | Sobota | 0x... |
| 276 | Niedziela | 0x... |

Najważniejsze dla załączonego ekranu:
- `MENU` = TypedText 96,
- `Wyłączony` = TypedText 63,
- `Środa` = TypedText 272.

Są to **ID wynikające z binarnej tablicy tekstów**, a nie domysły na podstawie wyglądu.

## 3. Zrzut ekranu a struktura firmware

Załączony obraz traktujemy jako **Home/Main Screen całego panelu**, a nie jako ekran CO1/CO2.

W firmware znaleziono dużą strukturę UI, która jest silnym kandydatem na główny root ekranu:

- `FUN_0803e5ac`, 292 B — konstruktor/kompozycja dużego obiektu UI;
- jest wywoływany przez `FUN_0803afc0`;
- w `FUN_0803e5ac` tworzonych jest wiele dużych podkomponentów pod stałymi offsetami od obiektu:
  - `+0x41C`
  - `+0x42C`
  - `+0x84F4`
  - `+0x8F70`
  - `+0x92DC`
  - `+0x963C`
  - `+0xA26C`
  - `+0xA5FC`
  - `+0xA628`
  - `+0xA654`
  - `+0xA680`
  - `+0xA6AC`

Szczególnie interesujący jest komponent pod `+0x92DC`, ponieważ `FUN_08047290` tworzy w nim **dokładnie sześć powtarzalnych elementów**, w pętli:

- licznik 0..5,
- krok obiektu `0x40`,
- zapis kolejnych elementów do tablicy,
- dwa wspólne komponenty przekazywane każdemu elementowi.

To bardzo dobrze pasuje strukturalnie do sześciu elementów dolnego paska widocznego na zrzucie:

`MENU | paliwo | palnik | CO1 | CWU/CO2 | zasilanie`

Na tym etapie oznaczamy to jako **[SILNA INFERENCJA]**. Liczba 6 wynika bezpośrednio z kodu; przypisanie konkretnych sześciu pozycji do ikon ze zrzutu wymaga jeszcze prześledzenia bitmap/akcji dotyku.

## 4. Potwierdzenie tekstu „Wyłączony” w kodzie UI

`FUN_0802fc40` zawiera bezpośrednie ustawienie TypedText:

- `movs r0,#0x3F`
- zapis ID na stos,
- wywołanie `FUN_080307bc`.

TypedText 63 = `Wyłączony`.

`FUN_0802fc40` jest wywoływany z `FUN_0802ffec`.

To daje bezpośredni łańcuch:

`FUN_0802ffec -> FUN_0802fc40 -> TypedText 63 -> "Wyłączony"`

Jest to **[FW]**, nie domysł.

`FUN_0802ffec` dodatkowo używa TypedText:
- 158 = `Zwiększenie temperatury źródła [°C]`,
- 157 = `Źródło`

co wskazuje, że `FUN_0802fc40` nie jest jeszcze całym Home Screenem; jest raczej komponentem/fragmentem większej logiki UI. Dlatego nie należy utożsamiać go automatycznie z całym ekranem głównym.

## 5. Bezpośrednie ustawianie tekstów związanych z ogrzewaniem

W kodzie znaleziono wywołania `FUN_080307bc` z:

- ID 57 = `Ogrzewanie 1`:
  - Ghidra `0x08047558`, wewnątrz `FUN_0804752c`;
  - Ghidra `0x080475C2`, wewnątrz `FUN_080475A4`.

To jest bezpośredni dowód, że ID 57 jest faktycznie używane przez kod UI, a nie tylko obecne w bazie tekstów.

Wartość ID 58 = `Ogrzewanie 2` jest potwierdzona w bazie TypedText, ale jego bezpośredni setter nie został jeszcze jednoznacznie znaleziony w tym przebiegu. Nie wolno więc twierdzić, że konkretna funkcja X ustawia ID 58 bez dalszego śladu.

## 6. Co z tego wynika dla rekonstrukcji 1:1

Mamy już trzy niezależne warstwy:

1. **TypedText database**
   - 8 języków,
   - 495 ID,
   - stałe ID tekstów.

2. **Komponenty UI**
   - obiekty tworzone przez konstruktory `FUN_...`,
   - podkomponenty pod stałymi offsetami,
   - komponent sześciu powtarzalnych elementów dolnego paska.

3. **Kod ustawiający TypedText**
   - `FUN_080307bc` przyjmuje ID tekstu i zapisuje je do obiektu tekstowego;
   - znaleziono rzeczywiste wywołania z ID 57 i 63.

Dalsza rekonstrukcja powinna iść od rootu `FUN_0803e5ac` w dół:
`root -> komponent +0x92DC -> 6 elementów -> bitmapy -> akcje dotyku`

oraz równolegle:
`root -> komponenty górnej części -> TypedText 272/96/63 -> wartości dynamiczne`.

## 7. Zasada oznaczania pewności

- **[FW]** — bezpośrednio odczytane z BIN / kodu / tabeli.
- **[SILNA INFERENCJA]** — wynika ze struktury kodu i zgodności z ekranem, ale nie ma jeszcze pojedynczego dowodu semantycznego.
- **[HIPOTEZA]** — wymaga dalszego potwierdzenia.

Nie będziemy wpisywać do mapy 1:1 rzeczy tylko dlatego, że „pasują wizualnie”.
