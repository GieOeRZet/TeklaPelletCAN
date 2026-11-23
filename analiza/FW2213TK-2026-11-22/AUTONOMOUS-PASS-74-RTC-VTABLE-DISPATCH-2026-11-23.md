# PASS 74 — FUN_08062638: domknięcie dynamic dispatch / vtable

Data: 2026-11-23

## Wynik

PASS 73 wykazał brak bezpośredniego BL do FUN_08062638. Ten PASS znajduje mechanizm wywołania przez runtime vtable/function pointer.

### FACT
- runtime address funkcji: 0x08072639 = PROJECT 0x08062639 + 0x10000 + Thumb bit.
- RAW zawiera ten runtime pointer dokładnie raz: PROJECT 0x0809446C.
- Pod runtime vptr 0x080A446C, czyli PROJECT 0x0809446C, znajduje się tablica metod.
- pierwszy slot tablicy (offset +0) zawiera 0x08072639, czyli FUN_08062638.
- w RAW nie ma bezpośredniego BL do PROJECT 0x08062638.

To zamyka wcześniejszą hipotezę: brak BL nie oznacza braku użycia funkcji; FUN_08062638 jest metodą wywoływaną przez wskaźnik.

## 1. Dowód bajtowy

RAW PROJECT 0x0809446C:

    39 26 07 08

czyli runtime pointer:

    0x08072639

Po odjęciu runtime relocation 0x10000 i wyzerowaniu Thumb bit:

    0x08072639 - 0x10000 - 1 = 0x08062638

co dokładnie odpowiada FUN_08062638.

## 2. Vptr

RAW PROJECT 0x08010456..0x08010460 zawiera konstruktorowy zapis wskaźnika do vtable.

Literal przy PROJECT 0x08010464:

    0x080A446C

Jest to runtime address vtable.

Po korekcji runtime → PROJECT:

    0x080A446C - 0x10000 = 0x0809446C

czyli dokładnie miejsce, w którym znajduje się pierwszy slot:

    0x0809446C = 0x08072639

To jest spójny, zamknięty łańcuch:

object constructor → vptr 0x080A446C → vtable PROJECT 0x0809446C → slot 0 → FUN_08062638.

## 3. Konstruktor i obiekt

Pod PROJECT 0x0801044C znajduje się kod konstruktorowy, który:

- przyjmuje r0 jako obiekt,
- wywołuje FUN_08014824 dla obiektu +0x8,
- ładuje runtime vptr 0x080A446C,
- zapisuje go do [object+0],
- ustawia [object+0x14] = 10.

Ten konstruktor jest wywoływany w startupowym/init path pod PROJECT 0x08000DC6 z:

    r0 = r8 + 0x4C

Nie nadaję jeszcze nazwy biznesowej obiektowi ani nie twierdzę, że r8 jest konkretnym globalem — wymaga to osobnego śledzenia.

## 4. Co to daje dla RTC auto-sync

Możemy teraz zapisać ścieżkę jako:

    init object
      ↓
    vptr = 0x080A446C
      ↓
    vtable PROJECT 0x0809446C
      ↓ slot 0
    FUN_08062638
      ↓
    PID 0x372F gate
      ↓
    [object+0x0C] timestamp
      ↓
    FUN_08039370
      ↓
    FUN_08018E94
      ↓
    RTC hardware

Najważniejszy następny cel nie jest już znalezienie callera FUN_08062638. Jest nim znalezienie zapisów do [object+0x0C] tego konkretnego obiektu.

## 5. Status

### FACT
- dynamic dispatch przez vtable — domknięty.
- vtable address — domknięty.
- slot 0 → FUN_08062638 — domknięty.
- brak direct BL — potwierdzony.
- konstruktorowy zapis vptr — potwierdzony.

### OPEN
- semantyka pozostałych slotów vtable.
- pełna tożsamość obiektu r8+0x4C.
- wszystkie write-sites pola +0x0C.
- źródło timestampu.

### Nie robimy
- nie nazywamy jeszcze źródła timestampu NTP/CAN bez write-site.
- nie przypisujemy całej vtable do konkretnej klasy bez dodatkowych slotów/callerów.