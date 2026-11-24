# FW2213TK — pakiet znalezisk: warstwa BIG / instancje / konfiguracja

Data: 2026-11-19

## A. BIG jest nazwanym modułem sprzętowym
Firmware panela zawiera jawne teksty: CAN IO Big, CAN IO BIG, CAN IO 0/1/2 oraz komunikat o braku komunikacji z modułem BIG. W katalogu projektu węzeł CAN 86 jest opisany jako CAN IO BIG.

To nie dowodzi jeszcze mapowania wartości main_module_type 0/1/2 na konkretne moduły, ale potwierdza fizyczny byt BIG jako osobnego modułu I/O.

## B. +0x12B nie jest numerem obwodu CO
W runtime 0x08037D00 wartość module+0x12B wybiera typ/tryb obiektu. Wartości 1..4 bezpośrednio ustawiają +0x12C na 1..4. Wartości 5..10 i 0x10 wybierają wyspecjalizowane ścieżki.

To wzmacnia wcześniejszą korektę: +0x12B jest klasyfikacją/rodzajem obiektu, a +0x12C jest numerem instancji.

## C. +0x12C jest selektorem instancji używanym przez lookup
0x08036FF2, 0x080370C0, 0x0803716E i 0x08037212 pobierają module+0x12C. Dla grupy tabelowej wykonywane jest base + instance - 1, a wynik trafia do 0x1167A przy odczycie albo 0x11812 przy zapisie.

To daje pełny runtime bridge od obiektu modułu do właściwego rekordu parametru.

## D. Istnieje jeszcze jedna warstwa klasyfikacji obiektów
0x0803C064 najpierw czyta bajt z tabeli DAT_0803C218 indeksowanej param_2, a dopiero ta wartość wybiera zachowanie: 0, 1..4, 5..10 oraz kilka dalszych specjalizacji.

To pokazuje, że istnieje tabela opisująca typ obiektu dla pozycji param_2. Nie znaleziono jeszcze zawartości DAT_0803C218, więc nie wolno jej utożsamiać z 0x2105.

## E. 0x08036D60 wiąże obiekt z globalnym stanem instalacji
0x08036D60 zeruje pierwsze pole obiektu, odczytuje parametr CAN o indeksie 3 przez 0x080373BA i przekazuje wynik do 0x080391D6. 0x080373E6 zapisuje ten sam indeks 3 i normalizuje wartość modulo 8.

Semantyka tego parametru nie jest jeszcze pewna, dlatego nie łączymy go z liczbą obwodów.

## F. Konstruktor głównego obiektu modułu
0x08037CA4 inicjalizuje obiekt i zeruje +0x129, +0x12A, +0x12B oraz stan instancji. Konstruktor większej struktury w 0x08061098 wywołuje 0x08037CA4, 0x08036D60 i 0x08037E9C.

0x08037E9C ustawia stan domyślny: +0x128 = 1, +0x12C = 1, +0x12B = 0. Instancja 1 jest więc domyślnym stanem obiektu.

## G. 0x2105 nadal nie jest bezpośrednim sterownikiem obiektów
Mimo coraz mocniejszego połączenia warstwy modułów z CO1..CO4 nadal nie znaleziono instrukcji w rodzaju read 0x2105 -> N -> create N CH objects.

Status 0x2105: bardzo mocny kandydat na liczbę/konfigurację obwodów grzewczych, ale nadal nieudowodnione, że to właśnie ta wartość tworzy 1..4 instancji.

## Najbliższy cel
1. Odzyskać zawartość DAT_0803C218.
2. Znaleźć źródło param_2 przekazywanego do 0x0803C064.
3. Znaleźć miejsce, gdzie zestaw wybrany przez wariant 0x3500/0x3502/0x350B prowadzi do konkretnych pozycji/obiektów CH.

To powinno pozwolić przejść od modelu instancji do odpowiedzi, co dokładnie decyduje, ile instancji istnieje.