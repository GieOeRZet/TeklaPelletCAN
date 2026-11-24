# BATCH — C064 / 4107C / DATA boundary — 2026-11-19

## Wykonany trace

### 1. C064 pozostaje najtwardszym punktem klasyfikacji
FUN_0803C064(param_1,param_2) wykonuje:
class = DAT_0803C218[param_2].

Dla class 1..4 zapisuje jednocześnie:
- object+0x12B = class
- object+0x12C = class
oraz dobiera descriptor przez FUN_08039494.

FUN_08037D00 stanowi niezależną ścieżkę normalizacji type -> instance: dla type 1..4 ustawia +0x12C = type i ponownie dobiera descriptor.

### 2. C064 nie ma bezpośredniego call-site w obecnym decompiled.c
Literal search całego blobu nadal daje definicję FUN_0803C064, ale nie normalne BL do tej funkcji. Granica pozostaje pośrednia: callback/function-pointer/vtable/tabela startowa albo dane nieodtworzone przez Ghidrę.

functions.txt potwierdza zakres funkcji 0x0803C064..0x0803C282 (558 B), z sąsiednimi funkcjami 0x0803BC3C i 0x0803C284.

### 3. 0x12C jest rzeczywistym selektorem instancji
FUN_08036FF2 / FUN_080370C0 / FUN_0803716E / FUN_08037212 korzystają z +0x12C. W rodzinach count=4 obowiązuje base + instance - 1.

Twarde przykłady rodzin:
- 0x2032..0x2035
- 0x2048..0x204B
- 0x2064..0x2067

Mechanizm instancji jest więc udowodniony niezależnie od nazwy UI.

### 4. 4107C nie jest głównym źródłem CO
FUN_08040FC2 iteruje 22 wpisy DAT_0804107C. Pierwsze pole wpisu jest używane jako indeks parametru do FUN_08036FF2, a trzecie pole może zostać zapisane do object+0x12C. FUN_08041020 analogicznie korzysta z DAT_08041080 i zapisuje +0x12C przed FUN_08037212.

To jest realny mechanizm konfiguracji/test I/O z 22 wpisami, ale obecne dowody nie pokazują, że jest to źródło liczby aktywnych obwodów CO. Traktujemy go jako osobną ścieżkę instancji/Test I/O.

### 5. Krytyczna korekta adresowa
Nie używamy wcześniejszego tropu raw 0x32146 -> runtime 0x08042146 ani raw 0x38130 -> runtime 0x08048130 jako dowodu źródła instancji. README projektu określa dla funkcji runtime = 0x08000000 + raw. 0x08038130 leży w luce pomiędzy rozpoznanymi funkcjami, a 0x08048130 należy do FUN_080480C0.

W szczególności nie twierdzimy już: 0x10E -> 0x38130 -> +0x12C.

### 6. 0x10E i 0x10F są rozdzielone
FUN_08031CCC realnie odczytuje panel index 0x10E i używa wartości jako progów UI: value > 0 dla pierwszego elementu oraz value > 1 dla drugiego. To jest twardy fan-out UI, ale nie dowód liczby instancji CO.

Ten sam caller odczytuje 0x10F -> CAN 0x2105 i przekazuje wartość do FUN_0802D3E0 oraz FUN_0802D91C, gdzie jest traktowana jako stan/grafika konfiguracji ogrzewania. 0x2105 nie ma potwierdzonego bezpośredniego połączenia z C064.

### 7. Repo nie zawiera surowego BIN/HEX potrzebnego do odzyskania danych
Przeszukano pełne drzewo Git na canonical commit 9a0411a... oraz katalog firmware. Nie ma pliku .bin ani .hex z FW2213TK. W firmware/FW2213TK-ghidra są decompiled.c, functions.txt i strings.txt, ale nie ma eksportu surowej pamięci.

W konsekwencji nie wolno rekonstruować wartości:
- DAT_0803C218 (0x0803C218..0x0803C283)
- DAT_0803EEC0 (+0x62/+0x6E)
- DAT_0803F008
- DAT_0804107C / DAT_08041080
z samych nazw/rozmiarów.

### 8. Najkrótszy aktualny łańcuch
C064:
param_2 -> DAT_0803C218[param_2] -> class 1..4 -> +0x12B/+0x12C -> instance-aware parameter engine -> base + instance - 1 -> rekord CAN.

Brakujące dwa kluczowe ogniwa:
1. kto przekazuje param_2 do C064,
2. jakie konkretnie bajty znajdują się w C218.

### 9. Kolejny target
Priorytetowo analizować zakres kodu około 0x08037C00..0x080386xx pod kątem rzeczywistych tabel function-pointer/vtable i konstruktorów instalujących callbacki, a następnie wszystkie pośrednie wywołania/indirect calls z funkcjami sąsiadującymi z C064.

Równolegle śledzić wejścia do FUN_0803C064 od strony konstruktorów/dispatcherów, zamiast szukać literalnego BL.

Dopiero po odzyskaniu param_2 i C218 scalać ten wynik z 0x10E/0x10F i konfiguracją wariantów 0x3500/0x3502/0x350B.
