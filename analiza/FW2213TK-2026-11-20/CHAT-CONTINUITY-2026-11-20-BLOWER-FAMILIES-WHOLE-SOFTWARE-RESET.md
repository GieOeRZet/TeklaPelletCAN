# CHAT-CONTINUITY-2026-11-20-BLOWER-FAMILIES-WHOLE-SOFTWARE-RESET

Data: 2026-11-20
Projekt: TeklaPelletCAN
Firmware: FW2213TK_kopia.bin
SHA-256 firmware: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

## 1. Cel nadrzędny projektu

Nie budujemy tylko sterownika CAN ani pojedynczego fragmentu UI.

Celem jest możliwie wierne, 1:1 odtworzenie logiki całego softu/panelu FW2213TK na podstawie samego firmware:
- UI i jego architektury,
- ekranów, menu, poziomów dostępu i gate'ów,
- parametrów i ich identyfikatorów,
- konfiguracji kotła,
- zależności między konfiguracją a widocznością/funkcją UI,
- obiektów graficznych i bitmap,
- tekstów/TypedText we wszystkich językach,
- modeli/rekordów parametrów,
- odczytu/zapisu i mapowania CAN,
- modułów rozszerzeń i ich zależności od konfiguracji kotła,
- zachowania dynamicznego host/content,
- wszystkich wariantów wynikających z wyposażenia i konfiguracji.

Stary projekt/obserwacje/rejestry z wielodniowego skanowania mogą być używane wyłącznie jako materiał pomocniczy/hipoteza lub cross-check. Nie mogą być źródłem prawdy dla rekonstrukcji. Normatywnym źródłem prawdy jest FW2213TK.bin oraz bezpośrednie dowody z jego kodu, danych, stringów, bitmap, tablic i relacji wywołań.

## 2. Zasada pracy od tego punktu

Każdy nowy wątek trzeba prowadzić do możliwie zamkniętej gałęzi, ale bez utraty mapy całego systemu.

Nie kończyć po pierwszym znalezisku.
Wykonywać wieloprzebiegowe ataki:
- xref bezpośredni,
- xref pośredni/vtable,
- konstruktor -> obiekt -> pole -> writer,
- caller/callee,
- tablice i indeksy,
- stringi/TypedText,
- bitmapy i zasoby,
- geometria,
- konfiguracja/gate,
- poziom dostępu,
- parametr/model,
- CAN,
- warianty sprzętowe,
- porównanie z dokumentacją producenta jako cross-check, nigdy jako substytut firmware.

Dla ważnych tematów preferowane są dziesiątki niezależnych przebiegów/hipotez, aż uzyskamy spójny model. Nie przerywać analizy tylko dlatego, że znaleziono pojedynczy xref.

## 3. Nowa korekta dotycząca dmuchaw/wentylatorów

Użytkownik pokazał stronę instrukcji:
„4.2.1 Moc dmuchawy modulacja”.

Oficjalna instrukcja instalatora Estyma/Tekla mówi:
- wejście w „Moc dmuchawy modulacja [%]” otwiera modyfikowalny wykres obrotów dmuchawy w funkcji mocy palnika;
- pkt 4.2.1 opisuje dokładne wartości obrotów dmuchawy przy określonej mocy palnika;
- osobno występuje „Wentylator wspomagający”;
- przy nim instrukcja mówi: „Charakterystyka jak w pkt 4.2.1”.

To jest zewnętrzny cross-check zgodny z firmware, ale nie zastępuje firmware.

## 4. Dwie rodziny wykresów potwierdzone w firmware

### A. Dmuchawa palnika

0x2261..0x2265:
- 0x2261 = punkt 20%
- 0x2262 = punkt 40%
- 0x2263 = punkt 60%
- 0x2264 = punkt 80%
- 0x2265 = punkt 100%

W obrazie dostarczonym przez użytkownika widać dokładnie pięć punktów 20/40/60/80/100 na wykresie.

### B. Druga charakterystyka wentylatora

Firmware ma osobną rodzinę:
- 0x2268 = exh. fan char. 1
- 0x226E = exh. fan char. 2
- 0x226F = exh. fan char. 3
- 0x2275 = exh. fan char. 4
- 0x227A = exh. fan char. 5

Katalog parametrów FW identyfikuje ją jako drugą pięciopunktową charakterystykę. Wartości domyślne katalogu: 20, 30, 40, 50, 60.

Nie wolno traktować tych dwóch rodzin jako jednego wykresu z dziesięcioma punktami.

## 5. Twardy ślad w FUN_0803EC18

FUN_0803EC18 ma dwie osobne gałęzie:
- resolver/index 0x4A..0x4E -> 0x2261..0x2265
- resolver/index 0x4F..0x53 -> 0x2268, 0x226E, 0x226F, 0x2275, 0x227A

Obie ścieżki korzystają z tego samego ogólnego mechanizmu komponentu wykresu.

To bardzo mocno wskazuje na reusable graph component parametryzowany różnymi rodzinami charakterystyk.

Nie wolno jednak z samego tego faktu stwierdzać, że oba wykresy zawsze są widoczne jednocześnie. UI ma warunkowanie i dynamiczny host/content.

## 6. Dlaczego użytkownik może nie widzieć drugiej charakterystyki

To jest hipoteza do zamknięcia firmware, a nie fakt już udowodniony.

Instrukcja instalatora mówi wprost:
- część parametrów jest ukrywana zależnie od wybranego poziomu menu;
- poziom zmienia się kodem serwisowym;
- po zmianach konfiguracji, szczególnie zmianie typu modułu i źródła, urządzenie wymaga restartu;
- konfiguracja obejmuje m.in. źródło CO i czujnik pokojowy.

Dlatego brak drugiego wykresu w konkretnej konfiguracji użytkownika może wynikać z:
- typu/modelu kotła,
- aktywnego modułu,
- aktywnego wentylatora/wyposażenia,
- źródła,
- innego parametru konfiguracji,
- poziomu dostępu,
- kombinacji kilku gate'ów.

Nie wolno uznać żadnego z tych wariantów za zamknięty bez xref z firmware.

## 7. Ważny szerszy wniosek o architekturze

Użytkownik słusznie zwrócił uwagę, że moduły rozszerzeń (np. videROOM, NET, GSM itd.) mogą nie być niezależnymi światami.

Instrukcja pokazuje, że:
- Igneo Touch przechowuje konfigurację systemu;
- konfiguracja obejmuje m.in. źródło CO i typ czujnika pokojowego, w tym videROOM;
- sterownik współpracuje z urządzeniami/sterownikami przez CAN;
- istnieje procedura kopiowania nastaw pomiędzy sterownikami IgneoTouch przez CAN i firmware raportuje około 570 kopiowanych parametrów.

To wspiera kierunek badania zależności między panelem głównym, konfiguracją kotła i modułami.

Ale finalna implementacja ma być odtworzeniem zależności wynikających z firmware, nie rekonstrukcją starego projektu.

## 8. Co już wiemy o graph component

Twarde ustalenia:
- bitmap 056 = normalny marker wykresu;
- bitmap 057 = wariant zaznaczony/aktywny; ma również inne firmware'owe użycie, więc nie nazywać go graph-only;
- bitmapy 056/057 są zasobami 20x20;
- graph component jest konstruowany przez FUN_08047604;
- pięć punktów ma strukturę stride 0xE4;
- punkty mają osobne poddrzewa graficzne;
- geometria komponentu obejmuje centralny obszar około X=35, Y=50, W=335, H=180;
- FUN_08047D80 ustawia bitmap 056 na punktach w ścieżce odświeżania;
- FUN_08047C1A wykonuje mapowanie wartości na geometrię punktów;
- FUN_08048520 przekazuje dane do komponentu graph przez FUN_08047A8A;
- host/content znajduje się w okolicy parent+0x84F4, a graph content jest przy parent+0x963C;
- FUN_0802EADE jest dowodem dynamicznego host/content switching.

## 9. Ważne rozdzielenie od 47290

Nie wolno mieszać:
- graph component dla pięciu punktów charakterystyki,
z
- FUN_08047290/FUN_08047334, które tworzą osobny sześciopozycyjny komponent.

47290:
- sześć slotów,
- Y = 50 + 34*slot,
- bitmapy 151/152,
- teksty są dostarczane przez osobną tablicę sześciu TypedText ID przez pole +0x08 obiektu źródłowego.

Nie ma obecnie dowodu, że 47290 wyświetla 0x2261..0x2265 lub 0x2268..0x227A.

## 10. Polska baza stringów jest już dostępna

Nie należy ponownie traktować braku bezpośrednio indeksowanego stringa jako dowodu braku funkcji.

Firmware zawiera:
- 8 tabel TypedText,
- 495 wpisów na tabelę,
- języki:
  0 ES
  1 EST
  2 EN
  3 LT
  4 PL
  5 RO
  6 SK
  7 CZ
- tabela PL jest bezpośrednio odzyskiwalna z firmware.

W kolejnych analizach, gdy trzeba ustalić semantykę elementu UI, należy obowiązkowo sprawdzić PL/EN oraz pozostałe języki, zamiast zakładać znaczenie z nazwy parametru.

## 11. PIN i poziomy

Z firmware:
- 0x180A = 6154
- 0900 -> level 1
- 0999 -> level 2
- 6154 -> level 3

Level 3 ma 17 niezależnych gate'ów UI.

Instrukcja producenta potwierdza ogólną zasadę, że poziomy dostępu ukrywają część parametrów.

## 12. Główny cel reverse engineeringu

Nie kończymy na:
„znamy rejestr X i jego wartość”.

Docelowa mapa ma być wielowarstwowa:

konfiguracja
-> gate
-> poziom dostępu
-> ekran/menu
-> host/content
-> konstruktor klasy
-> obiekt
-> parametr/model
-> wartość
-> geometria
-> bitmapa
-> TypedText
-> interakcja
-> writer
-> CAN/record
-> efekt działania

Dopiero wtedy element jest traktowany jako zamknięty.

## 13. Strategia dla modułów rozszerzeń

Nie zakładać, że videROOM/NET/GSM są osobnymi aplikacjami.

Trzeba znaleźć w firmware:
- konfigurację ich aktywacji,
- parametry powiązane z modułami,
- gate'y UI,
- identyfikatory CAN,
- sposób pobierania konfiguracji źródła/kotła,
- zależności od typu modułu,
- zachowanie przy zmianie źródła,
- restart/commit konfiguracji,
- ewentualne wspólne rekordy/struktury.

To jest część „odwzorowania całego softu”, a nie poboczny temat.

## 14. Dokumentacja zewnętrzna wykorzystana w tym przebiegu

1. Estyma — Instrukcja instalatora igneo touch, Tekla – kotły pelletowe, TKP-PL-I 20190802:
https://estyma.pl/wp-content/uploads/2020/02/InstrukcjaTeklaPelletInstalator_PL.pdf

2. Tekla Kotły — Instrukcja obsługi i instalacji kotłów serii DRACO, sierpień 2025:
https://www.teklakotly.pl/media/transfer/doc/instrukcja_kotly_automatyczne_pellety_08_25_compressed_2.pdf

3. Tekla Kotły — Tabele nastaw kotłów serii BIO, 02/2025:
https://www.teklakotly.pl/media/transfer/doc/tabele_nastaw_kotlow_serii_bio_02_2025_min_2.pdf
Uwaga: podczas bieżącego pobrania URL zwrócił błąd serwera; link zachowany jako wskazane przez użytkownika źródło.

4. Tekla Kotły — Instrukcja kotłów automatycznych ekogroszek, instalatorska:
https://www.teklakotly.pl/media/transfer/doc/instrukcja_kotly_automatyczne_ekogroszek_inst_rem_2.pdf

Dokumenty producenta są cross-checkiem i mapą terminologii. Nie mogą zastępować dowodu z firmware.

## 15. Istotne fakty z dokumentacji producenta

Instrukcja instalatora:
- pkt 4.2.1: wykres mocy dmuchawy modulacja;
- „Wentylator wspomagający” ma charakterystykę jak 4.2.1;
- część parametrów jest ukrywana zależnie od poziomu menu;
- zmiana typu modułu i źródła wymaga restartu po zapisaniu konfiguracji;
- menu konfiguracji zawiera m.in. źródło i typ czujnika pokojowego;
- videROOM jest jedną z opcji czujnika pokojowego;
- kopiowanie nastaw pomiędzy IgneoTouch odbywa się przez CAN i obejmuje około 570 parametrów.

## 16. Obecny kierunek analizy

Najbliższy duży przebieg nie powinien być ograniczony do samego wykresu.

Najpierw:
1. odzyskać z firmware polskie i angielskie TypedText związane z obiema charakterystykami;
2. znaleźć wszystkie xref 0x2268/0x226E/0x226F/0x2275/0x227A w kodzie, a nie tylko surowe wystąpienia danych;
3. znaleźć gate drugiej charakterystyki;
4. znaleźć konfigurację typu modułu/źródła/wentylatora powiązaną z gate'em;
5. ustalić parent/host/content drugiego wykresu;
6. sprawdzić, czy obie charakterystyki mają wspólną klasę, ale różne parametry, tytuły i gate'y;
7. równolegle wykonać resource-reuse matrix dla bitmap 056/057 oraz innych par selektorów;
8. potem wrócić do całego drzewa menu i konfiguracji, aby nie zgubić celu 1:1;
9. po zamknięciu gałęzi zintegrować wynik z MASTER STATE.

## 17. Ważna zasada dokumentowania rozmów

Każdy istotny chat/przebieg ma być dopisywany do repo jako osobny plik continuity/archive albo jako rozszerzenie właściwego checkpointu.

Nie deklarować, że zapisano „surowy transcript”, jeżeli zapisano tylko techniczne podsumowanie. W pliku należy jasno oznaczać:
- co użytkownik powiedział,
- co zostało znalezione,
- co jest twardym dowodem,
- co jest hipotezą,
- co zostało odrzucone,
- co pozostaje OPEN,
- następny atak.

## 18. Zasada źródła prawdy

SOURCE OF TRUTH:
1. FW2213TK.bin / FW2213TK_kopia.bin
2. bezpośrednie xref/kod/dane/zasoby firmware
3. odzyskane stringi/bitmapy/tabele z firmware
4. dokumentacja producenta jako cross-check
5. obserwacje użytkownika jako bardzo wartościowe dane testowe i korelacyjne
6. stary projekt/rejestry jako materiał pomocniczy, nie jako źródło semantyki

Jeżeli stary projekt mówi coś innego niż firmware, firmware wygrywa.

## 19. Status tego chatu

Najważniejszy rezultat:
Nie mamy jednego „wykresu dmuchawy”. Mamy co najmniej dwie pięciopunktowe rodziny parametrów obsługiwane przez wspólny mechanizm wykresu. Brak jednej rodziny w aktualnym UI użytkownika może być skutkiem konfiguracji/gate'u.

Jeszcze ważniejszy rezultat strategiczny:
Ta gałąź jest częścią większego celu. Nie wolno pozwolić, aby analiza wykresu stała się ślepą uliczką. Po zamknięciu gate/rodziny trzeba wrócić do mapy całego systemu i zintegrować wynik z architekturą konfiguracji, modułów, menu, parametrów, CAN i UI.

Checkpoint: commit zawierający ten plik ma być traktowany jako punkt wejścia do kontynuacji tego chatu.
