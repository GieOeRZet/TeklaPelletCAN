# PASS 76 — scheduler closure: kto uruchamia FUN_08062638

Data: 2026-11-23

## Wynik

To jest najważniejsze domknięcie A3 od strony wykonawczej.

FUN_08062638 nie jest tylko funkcją wskazywaną przez vtable. Jest **metodą slot 0 obiektu zarejestrowanego w globalnym schedulerze**, a scheduler iteruje listę obiektów i wykonuje ich slot 0.

### Zamknięty łańcuch

    startup r8 = 0x20008CD0
        ↓
    object = r8 + 0x4C = 0x20008D1C
        ↓
    constructor 0x0801044C
        ↓
    base constructor FUN_08014824
        ↓
    scheduler registration FUN_0801478C
        ↓
    scheduler list
        ↓
    scheduler tick FUN_080147C8
        ↓
    object vptr
        ↓
    vtable slot 0
        ↓
    FUN_08062638

## 1. Base constructor / rejestracja

FUN_08014824:

- przyjmuje obiekt w r0,
- ustawia bazowy vptr `0x080A458C`,
- ustawia `[object+0x05] = r1`,
- ustawia `[object+0x04] = 1`,
- wywołuje FUN_08014764,
- następnie FUN_0801478C z obiektem.

FUN_0801478C dodaje obiekt do dynamicznej listy scheduler'a.

Dokładna ścieżka:

    FUN_0801478C
      → FUN_08017DCE  (liczba elementów)
      → FUN_08017DD8  (wolne miejsce / zakres)
      → FUN_08017DE8  (wstawienie elementu)

## 2. Scheduler

Global scheduler state znajduje się pod `0x200246E8`.

FUN_08014764 inicjalizuje jego pola:

- `[scheduler+0x04]` — początek listy,
- `[scheduler+0x08]` — koniec/aktualny koniec,
- `[scheduler+0x0C]` — dodatkowy stan.

FUN_080147C8 wykonuje iterację:

1. pobiera obiekt z listy,
2. zmniejsza jego licznik `[object+0x05]`,
3. gdy licznik dochodzi do zera, pobiera obiekt z listy ponownie,
4. wykonuje:

       r0 = object
       r1 = [object]
       r1 = [r1]
       blx r1

czyli **slot 0 vtable**.

Po wywołaniu przywraca licznik z `[object+0x04]` do `[object+0x05]`.

To dokładnie odpowiada klasie obiektu RTC, którego konstruktor ustawia `[object+0x14] = 10` — ten licznik nie jest jednak tym samym polem co schedulerowe `+0x05`; trzeba rozdzielać warstwę bazowego scheduler object od pól klasy RTC.

## 3. RTC obiekt

Dla obiektu `0x20008D1C`:

- vptr runtime `0x080A446C`,
- vtable PROJECT `0x0809446C`,
- slot 0 = runtime `0x08072639`,
- slot 0 po korekcji Thumb/runtime = `FUN_08062638`.

Zatem scheduler nie musi mieć żadnej wiedzy o RTC. Widzi tylko obiekt i wywołuje jego slot 0.

## 4. Co to znaczy dla 0x372F

0x372F jest sprawdzany dopiero wewnątrz metody schedulerowej `FUN_08062638`.

Nie jest to globalny warunek scheduler'a.

Scheduler robi:

    call object->slot0()

a dopiero metoda RTC robi:

    compare timestamp
    → read PID 0x372F
    → optional RTC setter

To jest ważne dla implementacji 1:1: **auto-sync jest własnością obiektu/metody czasu, nie scheduler'a.**

## 5. Nadal OPEN

- dokładny producent wartości `0x20008D28` (object+0x0C),
- dokładna wartość `object+0x04` i `+0x05` dla tego konkretnego obiektu po konstrukcji bazowej,
- kto/który task wywołuje `FUN_080147C8` — brak direct BL, prawdopodobnie kolejny poziom scheduler/timer dispatch.

Najważniejsze: znalezienie producenta `0x20008D28` jest teraz jedynym brakującym elementem źródła czasu.