# REWALIDACJA ADRESÓW 0x38130 / 0x3212C — 2026-11-19

## Krytyczna korekta

Wcześniejsze notatki używały przesunięcia +0x10000 przy interpretacji adresów funkcji. To jest błędne dla kodu.

README projektu definiuje: kod/funkcje = 0x08000000 + raw_offset; +0x10000 dotyczy części danych/tekstów i nie wolno stosować tego przesunięcia do adresów funkcji.

Dlatego:
- raw 0x38130 -> runtime 0x08038130, NIE 0x08048130.
- raw 0x3212C -> runtime 0x0803212C, NIE 0x0804212C.
- raw 0x32146 -> runtime 0x08032146, NIE 0x08042146.
- raw 0x3C0B6 -> runtime 0x0803C0B6, a adres ten leży wewnątrz FUN_0803C064.
- runtime 0x08048130 należy do FUN_080480C0, a nie jest funkcją 0x38130.

## 1. 0x08038130 nie jest funkcją setter

functions.txt: FUN_0803809C ma 46 B i kończy się na 0x080380CA; następna rozpoznana funkcja to FUN_080381E4. Adres 0x08038130 leży w luce, więc nie ma podstaw do traktowania go jako rozpoznanej funkcji ustawiającej instancję.

## 2. 0x0803212C również nie jest rozpoznaną funkcją

FUN_080320C2 ma 50 B i kończy się na 0x080320F4. Adres 0x0803212C nie jest początkiem ani wnętrzem tej funkcji. Wcześniejszy zapis o ścieżce 0x10E -> 0x38130 zostaje wycofany jako dowód.

## 3. 0x08048130 to inny kod

FUN_080480C0 ma 866 B i obejmuje runtime 0x080480C0..0x08048422. Kod tego obszaru dotyczy budowy/układu dużego obiektu TouchGFX i nie jest potwierdzonym setterem +0x12C.

## 4. Co pozostaje twarde

FUN_0803C064 wykonuje class = DAT_0803C218[param_2]. Dla klas 1..4 bezpośrednio ustawia module+0x12B oraz module+0x12C na wartości 1..4.

To jest obecnie najpewniejszy kodowy punkt konfiguracji numeru instancji.

## 5. Dynamiczne indeksowanie pozostaje potwierdzone

FUN_080370C0 / FUN_0803716E / FUN_08037212 pobierają numer instancji z obiektu modułu i dla pierwszej tabeli wykonują base_index + instance - 1.

## 6. 0x10E

FUN_08031CCC bezpośrednio pobiera panelowy parametr 0x10E przez FUN_08036FF2 i używa go jako wartości licznikowej: 0x10E > 0 aktywuje pierwszy element, a 0x10E > 1 drugi.

Mapa panela nadal potwierdza: panel 0x10E -> CAN 0x3505 oraz panel 0x10F -> CAN 0x2105.

Nie mamy już jednak prawa twierdzić na podstawie adresów 0x3212C/0x38130, że 0x10E bezpośrednio wywołuje setter instancji.

## 7. Następny cel

Trzeba odnaleźć rzeczywiste wejście do FUN_0803C064. Ponieważ decompiled.c pokazuje tylko definicję, należy sprawdzić vtable, callbacki, tabele funkcji i wywołania pośrednie oraz konstruktor obiektu instalujący tę metodę.

Dopiero ten call path pozwoli ustalić, które param_2 prowadzą do klas 1..4 i czy 0x10E/0x3505 wpływa na wybór instancji.

## Status

Wycofane: 0x08048130 = setter instance; 0x08032146 = ścieżka 0x10E -> setter; 0x0803C0B6 = niezależny wybór 1..4 jako dowód wcześniejszego modelu.

Potwierdzone: FUN_0803C064 ustawia +0x12B/+0x12C dla klas 1..4; +0x12C jest używane przez dynamiczne indeksowanie parametrów; 0x10E jest realnym parametrem używanym do aktywacji elementów UI; 0x10F/0x2105 pozostaje odrębnym parametrem konfiguracji ogrzewania.