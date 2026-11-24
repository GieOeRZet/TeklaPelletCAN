# BATCH: +0x158 = poziom dostępu, nie tryb UI — 2026-11-19

## Najważniejsze odkrycie

Ponowny trace FUN_08037e74() zmienia interpretację pola obiektu +0x158.

Kod firmware:
- param_2 == 900 -> +0x158 = 1
- param_2 == 999 -> +0x158 = 2
- param_2 == 0x1BF1 -> +0x158 = 3
- param_2 == 0 -> +0x158 = 0
- inne wartości nie zmieniają pola.

W repo są niezależne, potwierdzone dane o panelu: poziom 0 = użytkownik, PIN 0900 = klucz 1, PIN 0999 = klucz 2. Zatem +0x158 nie jest zwykłym wariantem wizualnym Heating/CO. Jest polem poziomu dostępu obiektu. 0x1BF1 daje firmware'owy poziom 3; jego dokładne znaczenie funkcjonalne pozostaje do ustalenia.

## Korekta wcześniejszego modelu

Wcześniejsza interpretacja +0x158 jako UI/variant mode jest wycofana.

Prawidłowy model:
- +0x12B = klasa/typ obiektu, dla CO/Heating wartości 1..4,
- +0x12C = instancja 1..4,
- +0x158 = poziom dostępu,
- FUN_0803E714() używa +0x158 jako bramki widoczności/dostępności dodatkowych pozycji menu.

Dla klasy 1..4 FUN_0803E714(): zawsze dodaje bazowe 12 parametrów; przy +0x158 != 0 dodaje kolejne 11; następnie dla każdego ID robi FUN_08036FF2(context, id) i przekazuje wynik do UI przez FUN_0804842C().

To pasuje do mechanizmu poziomów menu: po odblokowaniu instalatorskim pojawiają się dodatkowe nastawy tej samej klasy/instancji.

## Dalszy ważny ślad

FUN_08037D00() rozdziela zachowanie przez FUN_08037DEC(), które czyta +0x12A, +0x128 oraz w klasie 3 sprawdza +0x12B dla 0x10/0x11. Nie należy mieszać +0x12A, +0x158 i +0x12B.

FUN_0803EB4A() iteruje po aktualnej liście parametrów param_1+0x20 i porównuje je z rekordami od DAT_0803F008, 188 rekordów (0xBC). Jest to osobna warstwa metadanych/formatowania wartości UI. Przy rekordzie typu 4 składa 13-bajtowy payload z parametrów 0xD4..0xD6; w pozostałych przypadkach pobiera wartość przez FUN_08036FF2() i przekazuje ją do FUN_0804842C().

## Nadal brakujące
1. zawartość DAT_0803C218 (108 bajtów),
2. zawartość DAT_0803EEC0.. — dokładne 16-bitowe ID 12+11 pozycji Heating,
3. zawartość DAT_0803F008 — 188 rekordów metadanych,
4. wejście pośrednie do FUN_0803C064() — brak bezpośredniego callsite; prawdopodobny callback/vtable/startup dispatch,
5. dokładne znaczenie poziomu 3 z PIN/klucza 0x1BF1.

## Kierunek dalszego trace
Nie łączyć na siłę 0x2105 z FUN_0803C064(). Najpierw odzyskać dane tabel z BIN/Ghidra export, prześledzić vtable wokół DAT_08038694/98/9C, znaleźć funkcję przekazującą param_2 do C064, ustalić indeksy klasyfikujące się jako 1..4, a dopiero wtedy spinać to z konfiguracją 0x2105..0x2108.

## Wniosek architektoniczny
Panel ma co najmniej trzy niezależne osie stanu:
- klasa (+0x12B) -> CO1/CO2/CO3/CO4
- instancja (+0x12C) -> który konkretny obwód 1..4
- poziom dostępu (+0x158) -> które pozycje menu tej klasy są dostępne.

To jest mocniejszy model niż wcześniejsze utożsamianie +0x158 z wariantem UI.