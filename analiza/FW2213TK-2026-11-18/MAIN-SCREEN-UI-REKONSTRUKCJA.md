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

## 9. Nowe ustalenia z bezpośredniej disassemblacji konstruktorów

Przeanalizowano surowy Thumb-2 dla fragmentów, których Ghidra nie wydzielił poprawnie jako funkcje.

### CO2 tile / komponent „Ogrzewanie 2”

Adres **0x08046D2C**:

- zapisuje `[r4+0x12A] = 2`;
- ustawia TypedText **58 = „Ogrzewanie 2”**;
- następnie tworzy kilka niezależnych obiektów UI;
- wywołuje osobny konstruktor **0x0804D948**;
- ustawia TypedText **348 = „Błąd wygaszania”** na obiekcie `r4+0x8B4`;
- dla tego obiektu przekazuje do helpera geometrii cztery stałe: `0xCD, 0xC3, 0xC8, 0x46`;
- ustawia TypedText **460 = „Liczba kotłów slave”** na obiekcie `r4+0x8EC`;
- drugi obiekt dostaje parametry geometrii `0x140, 0xC3, 0xC8, 0x46`;
- później ustawia TypedText **68 = „Moc 2”** na obiekcie `r4+0x85C`.

To jest bardzo mocny dowód, że komponent „Ogrzewanie 2” jest złożonym widgetem, a nie samym napisem.

### CO1

Adres **0x0804B618** analogicznie:

- `[r4+0x12A] = 2`;
- TypedText **57 = „Ogrzewanie 1”**;
- tworzy serię powtarzalnych podkomponentów;
- ma strukturę bardzo podobną do CO2.

### Ważne: to nadal nie jest cały ekran CO2

0x08046D2C wygląda na **komponent/element „Ogrzewanie 2”**, prawdopodobnie element większego UI. Nie utożsamiamy go jeszcze z pełnoekranowym widokiem parametrów CO2.

### Odkrycie 8 powtarzalnych konstruktorów

W firmware znajduje się osiem bardzo podobnych konstruktorów:

- `0x0804C410`
- `0x0804C78C`
- `0x0804CA94`
- `0x0804CD9C`
- `0x0804D00C`
- `0x0804D320`
- `0x0804D634`
- `0x0804D948`

Każdy ma tę samą charakterystyczną strukturę:
- wybór jednego z TypedText ID **40–49** zależnie od bajtu `[+0x12B]`;
- TypedText **159 = „Temp. maksymalna [°C]”**;
- TypedText **170 = „Temperatura CO dla 0°C [°C]”**;
- TypedText **171 = „Temperatura CO dla 10°C [°C]”**;
- kilka tych samych widgetów wartościowych.

Każdy z ośmiu konstruktorów jest wywoływany z innego dużego komponentu. Przykładowo:
- `0x08046D2C -> 0x0804D948`.

**[FW]** osiem kopii istnieje fizycznie w firmware.

**[HIPOTEZA]** Nie zakładamy jeszcze, że oznacza to osiem obwodów CO. To może być osiem instancji/reużywalnych ekranów lub komponentów innych funkcji.

### Helper geometrii

Funkcja **0x08030358** pobiera cztery wartości przekazane przez caller i przekazuje je do trzech metod vtable obiektu. Jest więc ewidentnie częścią ustawiania geometrii/layoutu widgetu.

Na tym etapie nie przypisujemy jeszcze nazw tych czterech argumentów do `x/y/width/height`, dopóki nie rozwiążemy metod vtable `+0x34/+0x38/+0x3C`.

To jest celowo zachowane jako [FW]/[HIPOTEZA], a nie zgadywane.

### Wniosek dla dalszej rekonstrukcji

Najbliższy cel to:
1. rozwiązać vtable używane przez 0x08030358;
2. ustalić dokładne znaczenie czterech parametrów geometrii;
3. znaleźć instancję/rodzica odpowiadającego pełnemu widokowi CO2;
4. dopiero wtedy narysować layout 1:1.

## 10. Przełom: 0x08030358 = ustawienie geometrii X/Y/W/H

Bezpośrednia analiza funkcji **0x08030358** pozwala już rozstrzygnąć znaczenie czterech argumentów.

Kod:
- zachowuje `r3`,
- wywołuje metodę vtable `+0x34` z `r0=this, r1, r2`,
- wywołuje metodę vtable `+0x38` z `r0=this, r1=r3`,
- wywołuje metodę vtable `+0x3C` z `r0=this, r1=[sp+0x10]`.

Czyli caller przekazuje:

`setGeometry(object, X, Y, W, H)`

jako:
- r1 = X
- r2 = Y
- r3 = W
- [sp] = H

### Niezależne potwierdzenie

W funkcji **0x0805F87C** wywołanie ma:
- X = 0
- Y = 0
- W = 0x1E0 = **480**
- H = 0x110 = **272**

To jest pełny obszar wyświetlacza **480×272**.

### Konkretny przypadek CO2-komponentu 0x08046D2C

Dwa obiekty:

1. `r4 + 0x8B4`
   - TypedText **348 = „Błąd wygaszania”**
   - geometry:
     - X = **0xCD = 205**
     - Y = **0xC3 = 195**
     - W = **0xC8 = 200**
     - H = **0x46 = 70**

2. `r4 + 0x8EC`
   - TypedText **460 = „Liczba kotłów slave”**
   - geometry:
     - X = **0x140 = 320**
     - Y = **0xC3 = 195**
     - W = **0xC8 = 200**
     - H = **0x46 = 70**

To są **rzeczywiste współrzędne z firmware**, nie rekonstrukcja wizualna.

### Ważna interpretacja

Te dwa prostokąty częściowo się nakładają, więc nie należy ich traktować jako dwóch jednocześnie widocznych pól na ekranie. Są to najpewniej alternatywne/warunkowe elementy tego komponentu albo obiekty obsługujące różne stany. Sam kod nie daje jeszcze prawa do stwierdzenia, który jest widoczny w danej konfiguracji.

To jednak pierwszy twardy punkt, w którym mamy **rzeczywistą geometrię UI z firmware**.

### Co z tego wynika

Od teraz możemy dla każdego znalezionego komponentu budować tabelę:

`obiekt -> TypedText/Bitmap -> X,Y,W,H -> rodzic -> akcja`

To jest dokładnie format potrzebny później do odtworzenia panelu 1:1.

## 11. Korekta numeracji adresów po zestawieniu z rzeczywistymi wskaźnikami

**Bardzo ważne:** w poprzednich sekcjach używałem adresów z pomocniczego ELF/disassembly, który został zlinkowany z bazą `0x08000000`. Są to **adresy syntetyczne do czytania raw BIN**, a nie zawsze adresy Ghidra.

Bezpośredni dowód z BIN:
- raw offset `0x46D2C` zawiera kod zaczynający się od fragmentu `b5 f8 04 46...`;
- w firmware istnieje wskaźnik `0x08056D2D` do tego samego obszaru kodu (Thumb bit = 1);
- `0x08056D2D - 0x08010000 = 0x46D2D`.

Dlatego dla dalszej pracy stosujemy:
- **raw offset** = pozycja bajtowa w BIN,
- **Ghidra/runtime address** = `0x08010000 + raw_offset`,
- **syntetyczny adres z naszego ELF** = `0x08000000 + raw_offset`.

Przykład:
- syntetyczne `0x08046D2C` = raw `0x46D2C`,
- właściwy adres runtime/Ghidra dla tego raw = **`0x08056D2C`**.

Wcześniejsze nazwy typu „konstruktor 0x08046D2C” należy więc czytać jako **raw-disassembly @ raw 0x46D2C**, a nie jako potwierdzony adres funkcji Ghidra.

Dodatkowo `functions.txt` pokazuje funkcję `FUN_08056D04`, co potwierdza, że właściwa przestrzeń adresowa Ghidra jest przesunięta o `0x10000` względem pomocniczego ELF.

Od teraz w dokumentacji będę podawał przede wszystkim **raw + Ghidra/runtime**, żeby nie było już dwuznaczności.

## 12. Vtable potwierdza dwa różne typy komponentów CO1/CO2

W surowym BIN znaleziono tablice metod w obszarze około raw `0x7EE20` i `0x7F778`.

Pierwsza zawiera m.in. wskaźnik:
- `0x08056D2D` (Thumb) → kod znajdujący się przy raw `0x46D2C`.

Druga zawiera:
- `0x0805B619` (Thumb) → kod znajdujący się przy raw `0x4B618`.

Obie tablice mają bardzo podobny układ pozostałych wpisów:
- wspólny pierwszy zestaw metod,
- różny wpis odpowiadający implementacji komponentu CO1/CO2,
- wspólne kolejne metody.

**[FW]** nie są to tylko dwa wywołania tego samego tekstu. Firmware posiada **dwa warianty klasy/obiektu UI**, których implementacje różnią się właśnie w metodzie wskazywanej przez te wpisy.

To jest kolejny mocny dowód na odrębność komponentów „Ogrzewanie 1” i „Ogrzewanie 2”.

### Następny krok

Trzeba teraz:
1. zidentyfikować rodzicielski obiekt, który posiada każdą z tych tablic metod;
2. prześledzić, kto dodaje ten obiekt do ekranu;
3. znaleźć metody odpowiedzialne za rysowanie/aktualizację;
4. połączyć je z bitmapami i wartościami dynamicznymi.

To powinno dać pełny łańcuch:
`Home -> element CO2 -> vtable -> widgety -> bitmapy/teksty -> dane`.

## 14. Vtable i rzeczywiste odwołanie do komponentu CO2

Dalsze przeszukanie surowego BIN potwierdziło konkretne tablice metod.

### Vtable komponentu CO2

RAW 0x7EE20 zawiera m.in.:
- +0x00 -> 0x08043A33
- +0x04 -> 0x08056D2D — metoda związana z komponentem CO2
- +0x08 -> 0x080A60EB
- +0x0C -> 0x080570F5
- +0x10 -> 0x08043C73
- +0x14 -> 0x08043E3B
- +0x18 -> 0x08043F39
- +0x1C -> 0x080570F7
- +0x20 -> 0x080A60ED
- +0x2C -> 0x0809DE09
- +0x34 -> 0x08043A33
- +0x38 -> 0x0805B33D
- +0x3C -> 0x080A60EB
- +0x40 -> 0x0805B4D1

### Vtable komponentu CO1

RAW 0x7F778 zawiera analogiczny układ, ale inny zestaw metod:
- +0x00 -> 0x08043A33
- +0x04 -> 0x0805B619
- +0x08 -> 0x080A60EB
- +0x0C -> 0x0808447F
- +0x10 -> 0x08043C73
- +0x14 -> 0x08043E3B
- +0x18 -> 0x08043F39
- +0x1C -> 0x0807ED61
- +0x20 -> 0x080A60ED
- +0x2C -> 0x0808B75B
- +0x34 -> 0x08043A33
- +0x38 -> 0x080A60C9
- +0x3C -> 0x080A60EB
- +0x40 -> 0x080A60CB

**[FW]** Obie vtable są rzeczywiście różne, mimo wspólnego szkieletu metod.

### Bezpośredni call znaleziony w kodzie

Skan Thumb-2 dla BL wykazał:

raw 0x46D3C -> 0x0805D948

czyli fragment komponentu CO2 wykonuje bezpośrednie wywołanie konstruktora znajdującego się przy runtime 0x0805D948.

To jest niezależne potwierdzenie relacji:

komponent CO2 -> jeden z powtarzalnych konstruktorów parametrów/UI.

Nie znaleziono jeszcze bezpośredniego BL do samego konstruktora komponentu CO2 z innych funkcji. Jest to zgodne z tym, że obiekt może być tworzony przez mechanizm klasy bazowej/virtual dispatch lub przez kod, którego Ghidra nie rozpoznał jako funkcji.

### Ważne

Vtable nie daje jeszcze prawa do powiedzenia, który wpis odpowiada draw() albo handleClick(). Najpierw trzeba rozwiązać wspólną klasę bazową i znaczenie offsetów vtable. W dokumencie nie przypisujemy więc tych metod do nazw z TouchGFX bez dowodu.
## 15. Nowy punkt: BL do 0x0805D948 jest rzeczywisty, ale Ghidra nie utworzył tam funkcji

Ponownie zweryfikowano instrukcję BL w komponencie CO2.

- RAW `0x46D3C` zawiera `06 F0 04 FE`.
- Dekoder Thumb-2 daje cel **`0x0805D948`**.
- `0x0805D948` odpowiada RAW `0x4D948`, czyli dokładnie początkowi kodu wcześniej wytypowanego jako jeden z powtarzalnych konstruktorów.
- `functions.txt` nie ma funkcji rozpoczynającej się pod `0x0805D948`.

**[FW]** Nie wolno więc utożsamiać listy funkcji Ghidra z pełnym zbiorem funkcji wykonywalnych. Ten konkretny adres jest osiągalny rzeczywistym BL, mimo że automatyczna analiza nie oznaczyła go jako osobnej funkcji.

To jest istotne dla dalszego reverse engineeringu: będziemy szukać również **wejść do kodu osiągalnych przez BL, których Ghidra nie zarejestrował jako funkcje**, szczególnie w obszarach UI.

### Korekta metodologiczna

Nie znaleziono w surowym BIN prostego 32-bitowego wskaźnika do adresów vtable `0x0807EE20` / `0x0807F778`. Nie traktujemy więc samej lokalizacji tych tablic jako dowodu sposobu ich przypisania do instancji. Kolejny krok to identyfikacja zapisów vptr przez analizę konstruktorów i instrukcji PC-relative, a nie zgadywanie na podstawie samego adresu tablicy.
## 16. Korekta i konkretny łańcuch CO2: 0x08056D2C -> globalny obiekt -> 0x0805D948

Bezpośrednia disassembly z surowego BIN pozwoliła rozstrzygnąć rzecz, której wcześniej nie wolno było zgadywać.

### 0x080414BA nie jest konstruktorem bazowym

Instrukcja `BL` z początku komponentu CO2 prowadzi do `0x080414BA`.
Ten adres leży wewnątrz funkcji `FUN_0804148A`, a sam fragment pod `0x080414BA` wykonuje:

`LDR.W r0, [PC,#...]` -> odczyt adresu `0x20024814` -> `LDR r0,[r0]` -> `BX LR`.

**[FW]** `0x080414BA` jest więc accessor-em zwracającym wskaźnik przechowywany w globalnej zmiennej RAM `0x20024814`. Nie jest to „base constructor”.

### Początek komponentu CO2

RAW `0x46D2C` / runtime `0x08056D2C`:

- `BL 0x080414BA`
- `r1 = 2`
- zapis bajtu `+0x12A` w obiekcie zwróconym przez accessor
- `BL 0x0805D948`

To oznacza, że przed wejściem do dalszej konfiguracji UI kod ustawia wartość `2` w polu `+0x12A` obiektu wskazywanego przez global `0x20024814`.

### 0x0805D948 — konstruktor/konfigurator wywoływany przez CO2

RAW `0x4D948` / runtime `0x0805D948` zaczyna się od:

- `BL 0x080414BA`
- zapis `2` do `+0x12A` zwróconego obiektu
- `BL 0x080612E0` z `r0 = r4`
- ponownie `BL 0x080414BA`
- odczyt bajtu `+0x12B`
- switch dla wartości `0..10`.

Funkcja `0x080612E0` istnieje w `functions.txt` jako `FUN_080612E0`, rozmiar 224 B.

### Twardo odczytana mapa switcha +0x12B

Dla wartości `+0x12B` kod wybiera TypedText:

| wartość +0x12B | TypedText ID |
|---:|---:|
| 0 | 40 |
| 1 | 42 |
| 2 | 43 |
| 3 | 44 |
| 4 | 45 |
| 5 | 46 |
| 6 | 49 |
| 7 | 47 |
| 8 | 48 |
| pozostałe / default | 41 |

**[FW]** To jest bezpośrednio z instrukcji switcha w BIN, a nie interpretacja z nazw.

Jest to szczególnie ważne dla późniejszej rekonstrukcji UI: `+0x12B` jest używane jako indeks wyboru tekstu w tym komponencie.

### Wniosek

Mamy już konkretny łańcuch:

`CO2 @ 0x08056D2C`
` -> accessor 0x080414BA`
` -> globalny obiekt *0x20024814`
` -> ustawienie pola +0x12A = 2`
` -> BL 0x0805D948`
` -> kolejny komponent konfiguracyjny`
` -> odczyt +0x12B`
` -> wybór TypedText 40..49`.

To jest znacznie bardziej użyteczne niż samo znalezienie vtable, bo mamy już **realne pola obiektu i warunkowy wybór tekstu**.

### Granica dowodu

Nie twierdzę jeszcze, że global `0x20024814` jest całym ekranem głównym ani że `+0x12B` oznacza numer obwodu. To wymaga znalezienia miejsc, które zapisują te pola i miejsca, z których globalny obiekt jest dodawany do hierarchii UI.
## 17. Ważna korekta: switch +0x12B nie wybiera obwodu CO

Po ponownym odczytaniu tabeli TBB w `0x0805D948` wcześniejsza mapa była częściowo błędna.

### Dokładna mapa TBB

`[object + 0x12B]` jest porównywane z `10`, a następnie wykonywane jest `TBB`.

| wartość +0x12B | TypedText ID | tekst PL |
|---:|---:|---|
| 0 | 40 | BIG |
| 1 | 42 | STD |
| 2 | 43 | $ |
| 3 | 44 | $ |
| 4 | 45 | $ |
| 5 | 46 | $ |
| 6 | 49 | $ |
| 7 | 47 | $ |
| 8 | 161 | Test pompy |
| 9 | 48 | $ |
| 10 | 41 | MINI |
| >10 | 161 | Test pompy |

Teksty są odczytane z rzeczywistej polskiej tablicy TypedText w firmware.

**[FW]** Wartość `+0x12B` nie może być obecnie interpretowana jako numer obwodu CO. Wręcz przeciwnie: wartości `0/1/10` wybierają teksty `BIG/STD/MINI`, więc pole wygląda raczej na typ/tryb obiektu lub rodzaj urządzenia/modułu.

To usuwa wcześniejsze ryzyko błędnej interpretacji tego pola jako „numeru obwodu”.

## 18. 0x080612E0 jako konstruktor wspólnego elementu UI

`0x0805D948` wykonuje:

`BL 0x080612E0`

a `0x080612E0` ma rozmiar 224 B i wykonuje m.in.:

- tworzenie/konfigurację elementu pod `this + 0x48`;
- geometrię `X=0, Y=0, W=480, H=272` dla `this + 0x48`;
- konfigurację kolejnych pól obiektu;
- ustawia TypedText ID **436** = `Uszkodzenie czujnika temp. zewnętrznej` na obiekcie `this + 0x11C`;
- ustawia TypedText ID **454** = `Próg zmniejszania stopnia mocy [%]` na obiekcie `this + 0x23C`.

**[FW]** 480×272 nie jest tutaj wnioskiem z fotografii — wartości są literalami przekazywanymi do helpera geometrii.

### Co to oznacza dla architektury

Najbardziej prawdopodobny, ale jeszcze nieudowodniony model C++ jest:

`0x0805D948` -> konstruktor większego komponentu
`    -> 0x080612E0 -> konstruktor/konfiguracja wspólnego elementu bazowego`
`    -> kolejne widgety i pola stanu

To jest **[STRONG INFERENCE]**, a nie [FW], dopóki nie znajdziemy zapisu vptr/wywołania zewnętrznego tworzącego obiekt.

### Co teraz ma największą wartość

Nie będziemy już śledzić `+0x12B` jako numeru CO2. Następny konkretny cel to:

1. rozpracować `0x0805D948` od `+0x12B` dalej;
2. zidentyfikować wszystkie `BL 0x080313A4` i odpowiadające im TypedText IDs;
3. dla każdego znaleźć `setGeometry` i rodzica;
4. osobno znaleźć miejsce, gdzie `0x08056D2C`/CO2 jest dodawany do hierarchii ekranu;
5. dopiero wtedy połączyć CO2 z konkretnymi wartościami CAN.