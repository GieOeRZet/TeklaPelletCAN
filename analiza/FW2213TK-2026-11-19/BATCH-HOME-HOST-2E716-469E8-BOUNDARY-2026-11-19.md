# BATCH — HOME HOST / 2E716 / 469E8 BOUNDARY — 2026-11-19

## Cel
Kontynuacja reverse-engineering oryginalnego FW2213TK TouchGFX. Najważniejszy nierozwiązany problem: skąd rzeczywiście bierze się wybór bitmapy kotła 011..014 i jak łączy się z parametrem 0x370A.

## 1. FUN_0802E716 — ROZSTRZYGNIĘTE: NIE JEST GRAFIKĄ KOTŁA
FUN_0802E716 ma 648 B i tworzy kontener/host treści:
- inicjalizuje obiekty tekstowe/sterujące (FUN_08034866, FUN_080349F4, FUN_08034784, callbacki FUN_08034A2C..08034A68);
- tworzy prostokąt 480x300 przez vtable +0x34/+0x38/+0x3c;
- tworzy element o rozmiarze 1000x1000;
- nie wykonuje bezpośredniego FUN_080307BC z ID bitmapy 0x0B..0x0E;
- jest instancjonowany w wielu ekranach, nie tylko Home.

Kluczowe: Home root FUN_0803E5AC tworzy FUN_0802E716(param_1 + 0x213d), a następnie osobno: FUN_08047244, FUN_08047290, FUN_08047604, FUN_08047E54. To pokazuje architekturę: 2E716 jest hostem/obszarem zawartości, a nie samą grafiką kotła.

## 2. FUN_0802EADE — mechanizm podmiany zawartości hosta
FUN_0802EADE dostaje wskaźnik hosta i wskaźnik aktualnego contentu. Jest wywoływany z:
- FUN_08048468 -> FUN_0802EADE(param_1 + 0x84F4, iVar1)
- FUN_080484B0 -> FUN_0802EADE(param_1 + 0x84F4, iVar1)
- FUN_080484F0 -> FUN_0802EADE(param_1 + 0x84F4, iVar1)
- FUN_08048520 -> FUN_0802EADE(param_1 + 0x84F4, param_1 + 0x963C)

Wniosek: Home +0x84F4 jest dynamicznym content hostem. To pozwala rozdzielić analizę layoutu od konkretnego widgetu.

## 3. FUN_08047244 / 08034A90 — NIE JEST BOILER GRAPHIC
FUN_08047244 tworzy FUN_08034A90(param_1+0x18) i ustawia X=0x32, Y=0x37. 08034A90 nie zawiera twardego ID bitmapy 11..14; buduje serię elementów tekstowych/sterujących.

## 4. FUN_08047290 / 08047334 — NIE JEST GRAFIKĄ KOTŁA
08047290 tworzy sześć elementów przez FUN_0800DCD4; 08047334 układa je pionowo i wypełnia tekstem. To lista/sekcja, nie centralny boiler bitmap.

## 5. FUN_08047E54 -> FUN_0802DF80 — NIE JEST BOILER GRAPHIC
08047E54 zawiera 0802DF80(param_1+0x18). 0802DF80 ma cztery elementy FUN_080347DC z ID 0x1B6, 0x1B7, 0x1B8, 0x1B9. Są to inne zasoby niż bitmapy kotłów 011..014. Ten trop odpada.

## 6. FUN_080469E8 — NADAL NAJMOCNIEJSZY KANDYDAT NA WIZUALNY KOMPONENT KOTŁA
Twarde fakty:
- parent W=70 (0x46), H=150 (0x96);
- bitmap child ma ID 0x0E = 14;
- bitmap jest ustawiana przez FUN_080307BC(param_1+0x4F, ...);
- Y bitmapy = 20;
- resource dimensions są pobierane przez vtable +0x38/+0x3C;
- cztery child widgets są instancjonowane w FUN_0803E34C: +0x251, +0x2B8, +0x31F, +0x386;
- stride między instancjami = 0x19C B;
- FUN_080469D4 tworzy obiekt pomocniczy przy +0x213.

## 7. Ważna korekta interpretacyjna
Samo istnienie FUN_080469E8 NIE dowodzi jeszcze, że 0x370A=1/2/3 mapuje się na bitmapy 011/012/013, ani że 0x370A=3 oznacza bitmapę 014. W kodzie 469E8 ID 14 jest hard-coded. W całym decompiled.c nie znaleziono bezpośredniego call-site'u, który później zmienia te cztery dzieci przez FUN_080307BC na 11/12/13. Trzeba szukać mechanizmu pośredniego: vtable, callback, visibility/instance selection albo osobny obiekt nadrzędny.

## 8. Parametr 0x370A
Potwierdzony z wcześniejszej analizy:
- nazwa: Boiler image selector;
- typ: u8;
- zakres: 1..3;
- default: 1;
- RAM: 0x20021FA6;
- snapshot: 3;
- rejestracja/callback boundary: 0x0801AB7E.

0x0801AB7E nie występuje jako normalna funkcja w functions.txt; adres leży w luce między rozpoznanymi funkcjami, więc nie wolno zakładać, że jest to zwykły entrypoint funkcji. Trzeba traktować go jako potencjalny wpis/tabelę/handler boundary do czasu odzyskania surowego obrazu.

## 9. Nowa architektura Home
FUN_0803E5AC tworzy: content host 2E716 @ +0x213D; 47244 @ +0x23DC; 47290 @ +0x24B7; 47604 @ +0x258F; 47E54 @ +0x289B.
Natomiast FUN_0803E34C jest osobnym komponentem z czterema instancjami 469E8. Nie znaleziono nazwanego caller'a 0803E34C w decompiled.c, więc jego instancjonowanie prawdopodobnie idzie przez warstwę obiektową/vtable/factory.

## 10. Następny priorytet
1. rozgryźć klasę/rodzica FUN_0803E34C;
2. znaleźć vtable DAT_0803E424 i metody klasy;
3. znaleźć wszystkie operacje na obszarach +0x251/+0x2B8/+0x31F/+0x386 po konstrukcji;
4. prześledzić FUN_080469D4 i obiekt przy +0x213;
5. znaleźć źródło wartości/wyboru powiązanego z 0x370A;
6. dopiero potem przypisać 011/012/013/014 do konkretnych wartości.

## Zakaz nadinterpretacji
Nie wpisywać do dokumentacji jako faktu żadnego mapowania 370A -> bitmap 11/12/13/14, dopóki nie ma bezpośredniego łańcucha danych/kodu.