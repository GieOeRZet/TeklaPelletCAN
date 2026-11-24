# BATCH — TOUCH 1:1: UI → parametr → obiekt → CAN — 2026-11-19

## Cel
Celem jest odtworzenie zachowania FW2213TK 1:1. Model roboczy: IGNEO Touch jest warstwą nadrzędną UI/regulatora/logiki parametrów, a CAN I/O BIG i pozostałe moduły są warstwą wykonawczą/I/O.

## 1. 0x2105 jest rzeczywiście używane przez UI
Panel index 0x10F (271) przechodzi przez FUN_08036FF2(context, 0x10F) do CAN 0x2105 — Heating configuration. FUN_08031CCC pobiera tę wartość i przekazuje ją do FUN_0802D3E0 oraz FUN_0802D91C.
Dowód: 0x2105 wpływa na stan/aktywność UI. Nie znaleziono natomiast dowodu 0x2105 -> utworzenie obiektów CO.

## 2. FUN_08036FF2 jest kluczowym mapperem panela
Funkcja mapuje panelowy indeks parametru na slot/ID zależny od kontekstu. Korzysta również z numeru instancji +0x12C, a wynik trafia dalej do obiektu panelowego.
To jest ważne dla repliki 1:1: UI może operować na indeksie panelowym, podczas gdy wspólny engine rozwiązuje właściwy rekord, storage i później CAN.

## 3. Trzy warstwy konfiguracji
A: 0x3500 Main module type + 0x3502 CH expansion module type + 0x350B Profile number -> wariant sprzętowy 2..7 -> zestaw struktur/tabel.
B: 0x2105..0x2108 -> konfiguracja funkcjonalna -> aktywność/widoczność UI i logika regulatora.
C: warstwa obiektów +0x12B/+0x12C -> typ/rodzaj obiektu oraz instancja -> dynamiczne indeksowanie parametrów CO.
Nie wolno utożsamiać profilu BIG z liczbą obiegów CO.

## 4. CO1..CO4 mają prawdziwy mechanizm instancji
Rodziny parametrów 0x2032..0x2035, 0x2048..0x204B i 0x2064..0x2067 mają count=4. FUN_08036FF2/FUN_080370C0/FUN_08037212 budują indeks base + instance - 1.
FUN_0803C064 wykonuje class = DAT_0803C218[param_2] i dla klas 1..4 ustawia +0x12B oraz +0x12C na 1..4. C064 nie jest jednak uznane za jedyne źródło +0x12C.

## 5. Korekta znaczenia +0x12B
+0x12B nie jest numerem obwodu CO. Switch w 0x0805D948 wybiera na podstawie tego pola typy/teksty obejmujące BIG, STD, MINI oraz Test pompy.
+0x12C pozostaje numerem instancji w mechanizmie dynamicznego indeksowania.

## 6. Twardy ślad UI CO1..CO4
Firmware ma osobne TypedText: 119 = Ogrzewanie obwód 1, 120 = Ogrzewanie obwód 2, 121 = Ogrzewanie obwód 3, 122 = Ogrzewanie obwód 4.
Komponent CO2 ma własny kod i własny wariant vtable, więc nie jest tylko zmianą napisu w jednym wspólnym widgetcie.
W jednym z komponentów CO2 potwierdzono geometrię: Błąd wygaszania X=205 Y=195 W=200 H=70; Liczba kotłów slave X=320 Y=195 W=200 H=70.

## 7. Geometria UI jest już możliwa do odtworzenia z firmware
Helper 0x08030358 ustawia geometrię X,Y,W,H. W 0x080612E0 potwierdzono pełny obszar 480x272.
Możemy więc budować tabelę: rodzic -> dziecko -> TypedText/bitmap -> X/Y/W/H -> stan -> callback -> parametr.

## 8. Ważna uwaga o Ghidrze
Raw BIN zawiera rzeczywisty BL do 0x0805D948, mimo że Ghidra nie oznaczyła tego wejścia jako osobnej funkcji. functions.txt nie jest więc kompletną listą osiągalnych wejść kodu.

## 9. Aktualny model pełnego przepływu
TOUCH event / UI -> panelowy indeks parametru -> FUN_08036FF2 -> slot/rekord -> descriptor/storage -> logika regulatora -> CAN parameter/SDO -> moduł wykonawczy BIG -> odpowiedź CAN -> aktualizacja obiektu panelowego -> widget/bitmapa/TypedText.
Równolegle konfiguracja 0x3500/0x3502/0x350B wybiera wariant sprzętowy, a 0x2105..0x2108 konfigurację funkcjonalną.

## 10. Następne cele
1. Odzyskać DAT_0803C218.
2. Znaleźć pośrednie wejścia do FUN_0803C064 przez vtable/callback.
3. Prześledzić źródła param_2 dla komponentów CO1..CO4.
4. Rozwiązać rodziców/vptr komponentów CO1/CO2.
5. Zmapować widget -> panel index -> FUN_08036FF2 -> CAN.
6. Dopiero potem spiąć 0x2105 z warunkiem aktywacji CO1..CO4.
7. DAT_0804107C traktować jako prawdopodobną warstwę Test I/O, nie główny mechanizm CO.

## Granice pewności
[FW] = bezpośredni kod/tabela/BIN. [STRONG INFERENCE] = kilka zgodnych śladów bez jednego rozstrzygającego call-site. [HIPOTEZA] = nie wdrażać do repliki 1:1 bez kolejnego dowodu.
Nie wracać do wycofanego tropu 0x08042146 -> 0x38130.