# Analiza UI głównego panelu — 2026-11-18

## 1. Korekta mapowania adresów

W firmware występują **co najmniej dwa istotne układy adresowe** i nie wolno ich mieszać.

### Kod i klasyczny obszar danych

Dla adresów funkcji z `functions.txt` oraz dla tabel takich jak mapa CANopen↔panel-ID praktyczne mapowanie jest bezpośrednie:

`Ghidra address = 0x08000000 + raw_offset`

Przykład:
- `FUN_0801143c` znajduje się w pliku przy raw `0x1143C`;
- raw `0x37576` odpowiada adresowi `0x08037576`.

### Obszar tekstów/assetów

Wskaźniki zapisane w tablicach TypedText wskazują natomiast adresy przesunięte o `0x10000` względem surowego offsetu tekstu.

Dowód:
- tablica PL jest w pliku przy raw `0x5BD80`;
- wpis ID 120 zawiera wskaźnik `0x08098B58`;
- tekst `Ogrzewanie obwód 2` znajduje się w pliku przy raw `0x88B58`;
- `0x08098B58 - 0x08010000 = 0x88B58`.

To nie jest powód do przesuwania adresów funkcji. Oznacza to, że **tekst/asset pointer space ma własne przesunięcie**. W dalszej analizie będę jawnie podawał `raw`, `Ghidra/code address` i — gdy potrzebne — `asset pointer address`.

To wyjaśnia wcześniejsze pozorne rozbieżności między adresami kodu i wskaźnikami tekstów.

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

## 8. Dokładniejszy rozkład kandydata na Home/Main UI

FUN_0803E5AC nie jest pojedynczym widgetem. Konstruktor składa duży obiekt z wielu podkomponentów. Potwierdzone wywołania:

| offset obiektu | konstruktor | obserwacja |
|---:|---|---|
| +0x041C | FUN_08047230 | mały komponent |
| +0x042C | FUN_0800DCD4 | inicjalizacja tablicy/serii obiektów |
| +0x84F4 | FUN_0802E716 | osobny komponent |
| +0x8F70 | FUN_08047244 | komponent tekstowo-graficzny |
| +0x92DC | FUN_08047290 | seria dokładnie 6 elementów |
| +0x963C | FUN_08047604 | duży komponent z wieloma podelementami |
| +0xA26C | FUN_08047E54 | mały komponent |
| +0xA5FC | FUN_08038ED0 | komponent |
| +0xA628 | FUN_08038ED0 | komponent |
| +0xA654 | FUN_0802DF08 | komponent z wartością początkową 0xFFFF |
| +0xA680 | FUN_0802DF08 | drugi taki komponent |
| +0xA6AC | FUN_08047FD4 | komponent |
| +0xA6BC | FUN_08047FE8 | komponent |
| +0xA6CC | FUN_08047FFC | komponent |
| +0xA6DC | FUN_08047FE8 | komponent |

### Sześciokrotny komponent

FUN_08047290 wywołuje ogólny konstruktor tablicy FUN_0800DCD4 z:
- stride = 0x40,
- liczba elementów = 6.

Następnie w pętli 0..5 zapisuje kolejne elementy do tablicy.

**[FW]** liczba elementów = 6.

**[SILNA INFERENCJA]** To jest bardzo dobry kandydat na sześć powtarzalnych elementów dolnego paska ze zrzutu, ale nadal nie przypisujemy bez dowodu: MENU, paliwo, palnik, CO1, CWU/CO2, power.

### Komponent 0x963C

FUN_08047604 jest znacznie większy (1158 B) i zawiera:
- kilka tablic obiektów tworzonych przez FUN_0800DCD4,
- serie po 5 elementów,
- ustawianie pozycji/wymiarów,
- tekst TypedText ID 0x1D4 (468) w jednym z podkomponentów,
- kolejne elementy powtarzane po stałych krokach.

To wygląda jak duża część UI, ale bez mapy vtable nie przypisujemy jej jeszcze do konkretnego fragmentu zrzutu.

### Komponent 0xA26C

FUN_08047E54 jest mały i zapisuje obiekt pod +0x328; nie zawiera bezpośredniego TypedText w pokazanym konstruktorze. Może odpowiadać za wartość/element liczbowy, ale to na razie tylko hipoteza.
