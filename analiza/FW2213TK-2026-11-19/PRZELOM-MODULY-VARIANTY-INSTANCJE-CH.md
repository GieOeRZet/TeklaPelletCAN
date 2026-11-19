# FW2213TK — nowy trace: konfiguracja modułów → obiekty instancji CH

Data: 2026-11-19

## 1. Twardy punkt wejścia konfiguracji modułów

Runtime 0x08001AE4 / raw 0x1AE4 rejestruje trzy pola obiektu konfiguracyjnego:

- object + 0x16BF → 0x3500 Main module type
- object + 0x16C0 → 0x3502 CH expansion module type
- object + 0x16CC → 0x350B Profile number

Rejestracja odbywa się przez 0x0801143C.

## 2. Wybór wariantu jest rzeczywisty i globalny

Runtime 0x08000E34 używa:

- +0x16BF jako main_module_type,
- +0x16C0 jako expansion,
- +0x16CC jako profile.

Dla main_module_type == 0:

- expansion 0: profile 1/2/3 → wariant 2/3/4
- expansion 1: profile 1/2/3 → wariant 5/6/7

Wybrany indeks iVar14 wybiera równolegle elementy wielu tablic (local_48 ... local_328), a następnie kopiuje je do wielu pól obiektu. To nie jest wybór pojedynczego parametru, lecz całego zestawu struktur konfiguracyjnych.

## 3. Ważne połączenie z instancjami CH

W module obiektu:

- +0x12B (offset 299) = klasyfikacja/typ obiektu,
- +0x12C (offset 300) = numer instancji 1..4.

Runtime 0x08037D00 dla klasyfikacji 1..4 zapisuje bezpośrednio:

    module + 0x12C = 1..4

Funkcja 0x080370C0 następnie pobiera:

    module = FUN_080314BA()
    instance = module + 0x12C

i dla wpisów tabeli instancji wykonuje:

    base_index + instance - 1
        → FUN_0801167A(...)
        → lookup rekordu parametru

To jest twarde połączenie warstwy obiektu modułu z dynamicznym wyborem instancji parametrów CO.

## 4. Dodatkowy ślad: inicjalizacja 22 pozycji

Runtime 0x08040FC2 iteruje 22 wpisy tabeli DAT_0804107C.

Dla każdego wpisu:

1. opcjonalnie ustawia module +0x12C z trzeciego pola wpisu,
2. pobiera parametr przez 0x08036FF2,
3. wynik przekazuje do 0x08040E46,
4. 0x08041020 wykonuje analogicznie zapis przez 0x08037212.

To pokazuje, że +0x12C nie jest wyłącznie polem pomocniczym UI. Jest używane jako selektor instancji zarówno przy odczycie, jak i przy zapisie parametrów.

## 5. Co z tego wynika

Mamy teraz dwie warstwy połączone na poziomie kodu:

    0x3500 / 0x3502 / 0x350B
                |
                v
        wybór wariantu sprzętowego
                |
                v
       zestaw struktur obiektu
                |
                v
       obiekty modułów CH
                |
          +0x12C = 1..4
                |
                v
       base + instance - 1
                |
                v
       0x1167A / 0x11812
                |
                v
       rekord parametru CO1..CO4

Warstwa 0x2105 (Heating configuration) nadal nie jest bezpośrednio znaleziona jako odczyt w dekompilacji. Nie należy jeszcze twierdzić, że 0x2105 tworzy obiekty CH. Jest natomiast silnym kandydatem na funkcjonalną liczbę/konfigurację obwodów.

## 6. Korekta ważnej interpretacji

Wcześniejsze określenie +0x12C jako „pole instancji” pozostaje prawidłowe, ale obecnie mamy mocniejszy dowód:

- +0x12C jest faktycznie ustawiane na 1..4,
- następnie jest czytane przez 0x370C0/0x3716E/0x37212,
- wpływa bezpośrednio na indeks parametru przekazywany do lookup/write.

Nie jest to tylko numer wizualnego slotu panela.

## Status

UDOWODNIONE:
- konfiguracja modułów → wybór wariantu,
- +0x12C → numer instancji 1..4,
- +0x12C → dynamiczny indeks parametru.

NADAL DO UDOWODNIENIA:
- dokładna semantyka wartości 0..4 rejestru 0x2105,
- moment, w którym 0x2105 wpływa na liczbę utworzonych obiektów CH,
- mapowanie wariantów 1..7 na konkretne fizyczne konfiguracje BIG I/O / expansion.

Najbliższy cel: odtworzyć tabelę DAT_0804107C i znaleźć funkcję, która tworzy/aktywuje kolejne obiekty CH na podstawie konfiguracji instalacji.
