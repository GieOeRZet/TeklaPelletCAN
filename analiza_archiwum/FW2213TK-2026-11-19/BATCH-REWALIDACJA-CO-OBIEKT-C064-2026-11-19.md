# BATCH-REWALIDACJA-CO-OBIEKT-C064-2026-11-19

## Krytyczna rewalidacja bieżącej dekompilacji

W aktualnym decompiled.c trzeba odrzucić wcześniejszą hipotezę, że raw 0x32146 / 0x08042146 jest twardym dowodem na 0x10E -> 0x38130.

functions.txt pokazuje: 0x0804204A = FUN_0804204a, rozmiar 204 B, koniec 0x08042116. Adres 0x08042146 leży już poza rozpoznaną funkcją. Sama bieżąca FUN_0804204a nie zawiera odczytu 0x10E ani wywołania mechanizmu instancji.

To świadome wycofanie wcześniejszego wniosku. Źródłem prawdy jest bieżąca dekompilacja.

## 1. Twardy mechanizm instancji: FUN_0803C064

Funkcja wykonuje class = DAT_0803C218[param_2].

Dla klas 1..4:
- class 1 -> bVar4=1
- class 2 -> bVar4=2
- class 3 -> bVar4=3
- class 4 -> bVar4=4

Następnie ustawia bezpośrednio:
- object+0x12B = class 1..4
- object+0x12C = instance 1..4

To jest bezpośredni, kodowy dowód powiązania tabeli klasyfikacji z instancją.

## 2. +0x12B i +0x12C

+0x12B jest klasą/typem wybranym z DAT_0803C218.
+0x12C jest numerem instancji.

Po tym wybierany jest wariant struktury przez FUN_08039494, a wynik trafia do object+0x110; wskaźnik jest zapisywany do object+0x10C.

## 3. DAT_0803C218

Adres tabeli: 0x0803C218.
Następna funkcja: 0x0803C284.
Różnica: 0x6C = 108 bajtów.

Ponieważ kod czyta bajt DAT_0803C218[param_2], najbardziej naturalny model to 108-bajtowa tabela klasyfikacyjna.
Nie mamy jeszcze jej surowych wartości, więc nie przypisujemy ich na siłę do CAN.

## 4. Instance-aware parameter engine

FUN_08036FF2(param_1,param_2) szuka param_2 najpierw w tabeli DAT_08037B4C (31 pozycji), a następnie w DAT_08037578 (174 pozycji).

Dla pierwszej tabeli wynik jest modyfikowany numerem instancji przechowywanym w obiekcie: wpis + object+0x12C - 1.

FUN_08037212 wykonuje analogiczny zapis przez FUN_08011812, również używając numeru instancji przy pierwszej tabeli.

To daje dwie klasy parametrów: instancjonowane oraz globalne/specjalne.

## 5. Globalny stan obiektu

FUN_08061020 tworzy obiekt przez FUN_08037CA4, następnie wykonuje FUN_08036D60(param+0x2A70) i FUN_08037E9C.

FUN_08036D60 zeruje pole, odczytuje parametr store o indeksie 3 przez FUN_080373BA, normalizuje wynik modulo 8 i przekazuje go do FUN_080391D6.

To pokazuje, że obiekt ma globalną konfigurację pobieraną przed logiką klas/instancji.

## 6. Konstruktor i default

FUN_08037CA4 ustawia m.in. +0x129=0 oraz +0x12A=0.
FUN_08037E9C ustawia jako default:
- +0x128 = 1
- +0x12C = 1
- +0x12B = 0

Czyli obiekt startuje z instancją 1, ale bez wybranego typu klasy.

## 7. 0x10E i 0x10F po rewalidacji

W FUN_08031CCC 0x10E jest używany do sterowania elementami UI:
- 0x10E > 0 -> element 1 aktywny
- 0x10E > 1 -> element 2 aktywny

0x10F jest przekazywany do FUN_0802D3E0 oraz FUN_0802D91C, czyli do stanu/grafiki konfiguracji ogrzewania.

W bieżącym decompiled.c nie ma literalnego przejścia 0x2105 -> FUN_0803C064.

## 8. Nowy model

param_2 -> DAT_0803C218[param_2] -> class 1..4 -> object+0x12B/+0x12C -> instance-aware lookup -> DAT_08037B48/DAT_08037578 -> FUN_0801167A/FUN_08011812 -> parameter store/CAN mapping.

Warstwa 0x10E/0x10F pozostaje obecnie osobną warstwą konfiguracji/UI. Nie zakładamy jeszcze bezpośredniego związku z tworzeniem obiektów.

## Następny cel

1. znaleźć wejście do FUN_0803C064 przez vtable/callback,
2. odzyskać param_2,
3. odzyskać 108 bajtów DAT_0803C218,
4. wskazać wpisy prowadzące do klas 1..4,
5. połączyć je z DAT_08037B48/DAT_08037578,
6. dopiero wtedy spiąć wynik z 0x2105..0x2108.

To jest obecnie najczystsza ścieżka do pełnego modelu CO1..CO4.