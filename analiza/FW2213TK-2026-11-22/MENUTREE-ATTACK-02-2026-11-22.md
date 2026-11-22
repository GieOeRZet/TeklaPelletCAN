# NewEstyma — MENU TREE ATTACK 02 — 2026-11-22

Firmware: FW2213TK_kopia.bin
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071
Repo: GieOeRZet/TeklaPelletCAN
Branch: ccr-be8a1bcb-5t76j0

## 0. Scope

Ten pass jest korektą i pogłębieniem MenuTree po ponownym wejściu bezpośrednio w pełny blob decompiled.c (Git blob SHA 9620d0c85259d34bb6a20d3b03b038945dfe4c1a) oraz połączeniu go z wcześniejszym RAW trace 0x42160..0x422C8.

Nie traktujemy Ghidra boundary jako źródła prawdy dla funkcji odzyskanych wcześniej z RAW.

## 1. HARD — FUN_08032F08 jest już zamknięta

Pełny decompiled.c:

    undefined1 FUN_08032f08(int param_1)
    {
      return *(undefined1 *)(param_1 + 0x2c);
    }

Wniosek:
- FUN_08032F08(x) = prosty getter bajtu x + 0x2C;
- nie jest samodzielnym callbackiem nawigacyjnym;
- nie jest resolverem selector -> screen;
- jeżeli RAW 0x422C8 wywołuje go z row pointerem, odczytuje stan bajtowy samego row objectu.

Status: FACT / CLOSED.

## 2. HARD — korekta nazwy FUN_0803C270

W functions.txt nie istnieje osobny entry-point FUN_0803C270.

Istnieje:
- FUN_0803C064, size 558 B = zakres 0x0803C064..0x0803C291;
- 0x0803C270 leży wewnątrz tego zakresu, dokładnie +0x20C od początku;
- następna funkcja zaczyna się przy 0x0803C284.

Dlatego nie wolno dalej dokumentować FUN_0803C270 jako niezależnej funkcji Ghidra.

Robocza nazwa:
FUN_0803C064+0x20C / C064_SUBENTRY_0x20C

Możliwe, że RAW wykonuje BL do środka wspólnego basic blocku/tailu. Tego nie zamykamy bez bajtowego trace.

Status: FACT — boundary correction.

## 3. HARD — czym jest FUN_0803C064

Pełny body pokazuje:

    class = *(DAT_0803C218 + param_2)

Następnie switch po klasie 0..20.

Dla klas 1..4:
- pobierany jest moduł przez FUN_080314BA();
- +0x12B dostaje klasę 1..4;
- +0x12C dostaje klasę/instancję 1..4;
- wybierany jest descriptor zależny od +0x12A;
- descriptor trafia przez FUN_08039494;
- wynik instalowany jest przy +0x10C/+0x110.

To jest warstwa klasyfikacji/instancjonowania obiektu, nie bezpośredni MenuRow resolver.

Nie wolno utożsamiać DAT_0803C218 z tabelą selectorów menu.

Status: FACT / CLOSED dla roli C064.

## 4. HARD — DAT_0803C218 pozostaje brakującą tabelą runtime

DAT_0803C218 -> 0x20005EF0.

FUN_0803C064 czyta byte[0x20005EF0 + param_2].

Znany rozmiar używanej tabeli: 108 B, do 0x20005F5B.

Brakuje nadal literalnej zawartości tej tabeli.

Konsekwencja:
- nie przypisujemy konkretnych param_2 do klas 1..4 bez dumpu;
- nie używamy tej tabeli jako zastępstwa dla MenuTree;
- nie wyciągamy z niej semantyki selectorów 90/97/100/98/95.

Status: OPEN — raw SRAM/data required.

## 5. HARD — FUN_0804BC6C: dokładna struktura dzieci

FUN_0804BC6C(row, param_2, param_3).

### Child A — row + 0x8C

Adres: row + 0x8C = param_1 + 0x23 jako int*.

Operacje:
- FUN_080313A4(row+0x8C, param_2);
- FUN_08031426(row+0x8C, RGB(255,255,255));
- geometria przez vtable +0x2C/+0x30;
- parent dodaje child przez vtable slot +0x64.

FUN_080313A4 zapisuje ID zasobu do child +0x26 i uruchamia przeliczenie rozmiaru tylko gdy obiekt nie ma jeszcze wymiarów.

Nie nazywamy tego jeszcze konkretnym TouchGFX class ani TypedText class, ponieważ vtable childa nie jest odzyskany.

### Child B — row + 0x60

Adres: row + 0x60 = param_1 + 0x18.

Gdy param_3 != 0xFFFF:
- FUN_080307BC(row+0x60, param_3);
- odczytywany jest rozmiar childa;
- ustawiany jest jego X/Y przez vtable +0x2C/+0x30.

FUN_080307BC jest potwierdzonym resource/Bitmap setterem.

To zamyka:
row + 0x60 = bitmap/resource child używany dla param_3 (B w raw row builderze).

### Child C — row + 0xF8

Adres: row + 0xF8 = param_1 + 0x3E.

Operacje:
- odczyt rozmiaru row;
- vtable +0x2C i +0x30 ustawia geometrię;
- child jest dołączany do parenta przez vtable +0x64.

### Parent

W FUN_0804BC6C parent wykonuje:
(**(code **)(*row + 0x64))(row, child)

dla wszystkich trzech dzieci.

To jest twardy dowód parent-child attachment na poziomie klasy bazowej.

Status: FACT / CLOSED dla offsetów i mechanizmu attachment.

## 6. HARD — geometria FUN_0804BC6C

Dla param_3 != 0xFFFF:
- child +0x60 otrzymuje pozycję poziomą zależną od row.width - child.width;
- pion jest ustawiany względem row.height - child.height;
- środek/offset jest skalowany przez 0x8000 >> 16, czyli połowę różnicy;
- druga część geometrii korzysta z row +0x36, +0x96, +0x08, +0x6A, +0x102 i +0x40.

Dla param_3 == 0xFFFF child bitmap nie jest ustawiany, a ścieżka geometrii jest uproszczona.

Nie zamykamy jeszcze absolutnych X/Y/W/H, bo potrzebne są runtime dimensions i konkretny row class/vtable.

Status: FACT dla wzorów / OPEN dla finalnych pikseli.

## 7. HARD — capability resolver jest osobnym etapem

Wcześniejszy RAW trace pozostaje ważny:
- po konstrukcji 21 slotów;
- baza object + 0x380;
- stride 0x274;
- caller 0x4227A;
- FUN_0803C178(model,slot);
- wynik decyduje o dalszym przetwarzaniu row.

Zamknięte gates:
- selector 1..4 -> internal 0x10E / CAN 0x2105, progi >=1..>=4;
- selector 5 -> 0x10F / 0x2106;
- selector 6 -> 0x110 / 0x2108;
- selector 7 -> 0x111 / 0x2107;
- selector 8 -> 0x11C;
- selector 9 -> 0x122.

To jest eligibility/visibility, a nie nawigacja.

Status: FACT / CLOSED dla capability layer.

## 8. HARD — 21-slot model

RAW constructor:
- records 0..14: zawsze;
- records 15..20: tylko gdy access != 0.

Następnie:
- 21 row objects;
- capability pass 0..20;
- osobny 21-iteracyjny access/update path.

Tabela @ 0x42348:

    0  0  60 83
    1 10  61 85
    2  1  62 86
    3  2  63 86
    4  3  64 86
    5  4  65 86
    6  5  66 88
    7  6  71 87
    8  7  67 84
    9  8  70 82
    10 9  69 99
    11 11  72 78
    12 13  74 89
    13 17  77 159
    14 15  76 96
    15 0  12 73
    16 90  14 75
    17 97  18 78
    18 100 16 79
    19 98 19 80
    20 95 20 81

Status: FACT / CLOSED.

## 9. Najważniejsza korekta względem ATTACK-01

Nie traktujemy już:
- FUN_08032F08 jako OPEN — jest zamknięta jako getter +0x2C;
- FUN_0803C270 jako niezależnej funkcji — jest adresem wewnątrz C064; dokładny RAW entry semantics nadal OPEN.

Poprawny model:

    row
      -> byte +0x2C
      -> FUN_08032F08

    C064 object-classification path
      -> DAT_0803C218[param_2]
      -> class/type
      -> +0x12B/+0x12C
      -> descriptor install

## 9A. NOWE HARD — odzyskany konstruktor klasy row

Pełny decompiled.c zawiera:

FUN_0804BB42(param_1)

i jest to kluczowy konstruktor klasy używanej przez FUN_0804BC6C.

Twarde cechy:
- ustawia vptr przez DAT_0804BC60;
- inicjalizuje child row+0x60 przez FUN_0802DF08;
- inicjalizuje child row+0x8C przez FUN_0802FC10;
- inicjalizuje child row+0xC4 przez FUN_0802FC10;
- inicjalizuje child row+0xF8 przez FUN_08032D7C;
- tworzy dodatkowy child row+0x2C przez FUN_08031BD4;
- ma pola/stan aż do offsetu +0x11D;
- funkcja leży bezpośrednio przed FUN_0804BC6C, które operuje dokładnie na tych samych child offsets.

To daje twardą klasę row:

    RowObject
      vptr = DAT_0804BC60
      +0x60 = Bitmap/resource child (FUN_0802DF08)
      +0x8C = resource/text-like child (FUN_0802FC10)
      +0xC4 = drugi resource/text-like child (FUN_0802FC10)
      +0xF8 = state/indicator child (FUN_08032D7C)
      +0x2C = dodatkowy child (FUN_08031BD4)

Status: FACT / CLOSED dla klasy i layoutu.

### Konsekwencja dla FUN_08032F08

FUN_08032D7C ma bezpośrednio następujące metody:
- FUN_08032E80 — zapisuje stan do child+0x2C i skaluje wartość;
- FUN_08032EB8 — aktualizuje stan child+0x2C na podstawie czasu/warunku i wywołuje callback;
- FUN_08032F08 — odczytuje child+0x2C.

Zatem FUN_08032F08 jest metodą klasy childa utworzonego przez FUN_08032D7C.

To jest ważniejsza informacja niż samo C body.

Nie nazywamy więc już FUN_08032F08 "getterem row+0x2C". Poprawny model:

    FUN_08032F08(state_child)
        -> return state_child + 0x2C

W MenuRow state_child najpewniej znajduje się pod row+0xF8.

Argument dokładnie używany w RAW 0x422C8 trzeba jeszcze potwierdzić bajtowym trace; wcześniejsze opisy skracające go do "row" nie są wystarczające.

Status:
- metoda klasy childa: FACT;
- row+0xF8 jako jej konkretny argument w 0x422C8: STRONG / wymaga RAW proof.

### Konsekwencja dla MenuTree

Mamy teraz prawdziwy mechanizm state overlay:

    row
      +0xF8
        -> state/indicator child
        -> +0x2C state byte
        -> FUN_08032E80 / FUN_08032EB8 / FUN_08032F08

To jest kandydat na warstwę state/selection/access marker, a nie selector ID.

Nie wolno utożsamiać +0x2C z selector.

## 10. Co nadal blokuje pełne MenuTree

### P0

1. RAW body/entry semantics 0x0803C270 jako sub-entry C064.
2. producer/content 0x20005F08.
3. exact row class/vtable for object+0x380+n*0x274.
4. touch/event callback row -> selector.
5. selector -> screen/page constructor.

### P1

6. exact second-stage role of selectors 0/90/97/100/98/95.
7. exact access-level visual/state effect.
8. concrete +0x12A/+0x12B/+0x12C context bridge.
9. final X/Y/W/H for row and children.
10. full child/widget tree.

## 11. Najbliższy wymagany RAW artefakt

Do zamknięcia P0 potrzebny jest jeden z:
- fizyczny FW2213TK_kopia.bin;
- Ghidra memory dump obejmujący code 0x08042100..0x08042320;
- data 0x20005EF0..0x20005F5B;
- row object runtime snapshot;
- lub równoważny raw Thumb disassembly + RAM dump.

Nie należy rekonstruować tych danych z samych opisów.

## 12. Status pass

CLOSED:
- FUN_08032F08 semantics;
- C064 vs pseudo-function 0x3C270 boundary correction;
- exact child offsets in FUN_0804BC6C;
- bitmap setter path for row+0x60;
- resource setter path for row+0x8C;
- parent attachment slot +0x64;
- 21-slot construction/capability architecture;
- first-stage and second-stage table semantics.

OPEN:
- row class/vtable;
- touch/navigation;
- runtime 0x20005F08;
- C064 sub-entry 0x3C270 exact role;
- six second-stage screen destinations;
- complete MenuTree.

## 13. Rule for next pass

Nie rozszerzać semantyki selectorów 90/97/100/98/95 na podstawie samych stringów.

Każdy selector ma dostać:

    selector
      -> row object
      -> state/capability
      -> touch callback
      -> navigation
      -> page constructor
      -> context
      -> widgets
      -> parameter/action

Dopiero po zamknięciu tej ścieżki status FACT.
