# BATCH — BOILER IMAGE TRACE: NEGATIVE-CALLSITE + CALLBACK BOUNDARY — 2026-11-19

## 1. Najważniejszy wynik
Pełny przegląd wszystkich jawnych wywołań FUN_080307BC w eksportowanym decompiled.c nie wykazał żadnego drugiego miejsca, w którym writer dostaje hard-coded ID 0x0B, 0x0C albo 0x0D. Jedyny jawny przypadek z tej rodziny to FUN_080469E8 -> ID 0x0E.

To jest istotne, bo eliminuje prostą architekturę: osobny konstruktor 011 + osobny konstruktor 012 + osobny konstruktor 013 + 014 jako cztery jawne klasy w tym eksporcie.

## 2. FUN_0803E34C — architektura slotów
FUN_0803E34C:
- najpierw wywołuje FUN_080468F0() — wspólny/base constructor;
- ustawia vptr DAT_0803E424;
- tworzy kilka childów/zasobów;
- tworzy pomocniczy obiekt FUN_080469D4 @ +0x213;
- następnie przełącza vptr na DAT_0803E430;
- tworzy cztery identyczne instancje FUN_080469E8 @ +0x251/+0x2B8/+0x31F/+0x386.

To potwierdza model: 3E34C jest kontenerem/rekordem z czterema slotami tego samego typu, a 469E8 jest konkretnym child widgetem.

## 3. FUN_080469D4 — nie jest setterem bitmapy
469D4 zapisuje wyłącznie cztery pola:
- vptr DAT_080469E4
- parent = param_2
- object/model pointer = param_3
- metadata = param_4.

Nie ma tu żadnego zapisu Bitmap ID. Jest to cienki obiekt-binding/bridge, który trzeba śledzić jako osobną klasę.

## 4. 469E8 — twardy stan początkowy
469E8 ustawia:
- parent W=70, H=150;
- child Bitmap @ +0x4F;
- Bitmap ID = 14;
- X centrowany względem 70 px przez vtable +0x2C;
- Y=20 przez vtable +0x30;
- cztery elementy TypedText/style wokół bitmapy;
- na końcu FUN_080318B4(FUN_080314BA(), param_1), czyli binding komponentu do aktywnego modelu.

Nie ma w samym konstruktorze odczytu 370A.

## 5. 0x370A / 0x0801AB7E — ważna korekta
Adres callbacku/rejestracji 0x0801AB7E pochodzi z tabeli parametrów. functions.txt ma funkcje do 0x08019462, a następny rozpoznany entrypoint jest dopiero 0x0802BDF0. Zatem 0x0801AB7E nie jest nazwanym entrypointem w wyeksportowanym zestawie funkcji.

To nie dowodzi, że adres jest 'nie-kodem'. Może być wskaźnikiem do podfunkcji, handlerem w tabeli, adresem wewnątrz większego bloku albo elementem metadanych. Ale nie wolno nazywać go normalną funkcją bez odzyskania surowego obrazu.

## 6. Sąsiedztwo 370A
Z katalogu parametrów:
- 0x3709 -> callback 0x0801425C;
- 0x370A -> 0x0801AB7E;
- 0x370B -> 0x08015CCC;
- 0x370C -> 0x0801659E;
- 0x370D -> 0x08016614.

Co ciekawe, część tych adresów leży wewnątrz większych funkcji rozpoznanych przez Ghidrę. To wzmacnia interpretację, że pole 'callback' w tabeli nie musi oznaczać klasycznego początku funkcji C.

## 7. 0801417C — ważny kontekst modelowy, ale nie bezpośredni 370A
FUN_0801417C buduje tabelę/model danych zawierającą jawne nazwy wielu kotłów, m.in. Bio Compact 10/18 kW, Draco Bio Compact FBII, Draco Bio, Tytan Bio itd.
To jest mocny dowód, że firmware posiada osobną warstwę danych identyfikujących warianty/model kotła. Jednak w eksportowanym kodzie nie ma jeszcze dowodu, że 370A jest obliczane z tej tabeli.

## 8. Najważniejsza granica dowodowa
Obecny dowodowy łańcuch to:
0x370A = Boiler image selector (1..3)
    [BRAK BEZPOŚREDNIEGO CALL-CHAINU W EKSPORCIE]
    ↓
3E34C / 469D4 / 469E8
    ↓
Bitmap ID 14
    ↓
014.png = 54x100

Nie wpisujemy jeszcze 1->011, 2->012, 3->013 jako faktu firmware. Taki mapping jest zgodny z zakresem i z późniejszą repliką WWW, ale to nie jest dowód z FW.

## 9. Nowy kierunek ataku
Najbardziej opłacalny następny krok nie polega już na szukaniu kolejnego konstruktora bitmapy.
Trzeba odzyskać jedną z dwóch rzeczy:
1. vtable DAT_08046CC4 i metody klasy 469E8, szczególnie metodę odświeżania/visibility/binding;
2. surowy obraz binarny/data region wokół 0x0801AB7E oraz tablicę parametrów, żeby rozstrzygnąć, czym faktycznie jest pole callback dla 370A.

Jeżeli uda się odzyskać metodę 469E8, można zamknąć: model binding -> parametr -> Bitmap ID. Jeżeli uda się odzyskać tabelę 370A, można zamknąć źródło parametru i jego handler.

## 10. Korekta handoffu
Usunięto ze START-HERE błędny/stary wpis sugerujący jako fakt '370A 1/2/3 = bitmapy 011/012/013'. Obecny handoff wymaga bezpośredniego call-chainu.