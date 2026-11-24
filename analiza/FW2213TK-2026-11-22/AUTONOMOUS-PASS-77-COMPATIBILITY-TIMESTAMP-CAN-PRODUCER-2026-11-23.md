# PASS 77 — Compatibility timestamp 0x2165: CAN RX producer closure

Data: 2026-11-23

## Wynik

Najważniejsze nowe ustalenie A3:

0x20008D28 jest storage PID 0x2165 = Compatibility timestamp.

Zamknięty tor statyczny:

CAN RX frame → parameter index → FUN_080115F6 lookup → PID 0x2165 record → FUN_08011812 → record+0x0C → 0x20008D28 → FUN_08062638 → 0x372F gate → FUN_08018E94 → hardware RTC

## 1. Twarde przypisanie adresu

- PID 0x2165
- nazwa: Compatibility timestamp
- typ: u32
- storage: 0x20008D28
- runtime table entry: 518
- 0x20008D28 = 0x20008CD0 + 0x58
- dla obiektu auto-sync base 0x20008D1C jest to object+0x0C

## 2. CAN RX write path

Wcześniej zamknięty tor CAN RX:

CAN frame → FUN_08062AE4/handler → FUN_08062B22 → parameter index z frame+4/+5 → FUN_080115F6 → type → FUN_08011812 → record+0x0C

jest ogólnym mechanizmem zapisu parametrów z CAN.

Dla PID 0x2165 record lookup zwraca storage 0x20008D28.

Dlatego dla tej konkretnej wartości otrzymujemy:

CAN write PID 0x2165 → write 0x20008D28

To jest twardy statyczny dowód istnienia CAN jako producenta timestampu.

Nie oznacza jeszcze, że CAN jest jedynym producentem.

## 3. Dlaczego 0x372F nie jest czasem

FUN_08062638:
- porównuje object+0x10 z object+0x0C;
- pobiera PID 0x372F;
- jeżeli PID jest niezerowy, bierze timestamp z object+0x0C;
- rozkłada go przez FUN_08039370;
- zapisuje RTC przez FUN_08018E94;
- następnie synchronizuje shadow object+0x10.

Zatem:

0x2165 = dane czasu
0x372F = zezwolenie na automatyczne zastosowanie tego czasu

## 4. Korekta wcześniejszego PASS 75

Wcześniej 0x20008D28 zostało opisane jako ogólny object+0x0C timestamp producer input.

Teraz mamy silniejszą identyfikację:

object+0x0C jest jednocześnie storage parametru 0x2165 Compatibility timestamp.

Nie należy traktować tego pola jako anonimowego prywatnego timestampu klasy.

## 5. Co pozostaje OPEN

1. Dokładny CAN command/frame wariant, który zapisuje 0x2165 w praktyce.
2. Źródłowe urządzenie po drugiej stronie CAN.
3. Czy UI/local path również zapisuje 0x2165.
4. Czy istnieje drugi producer lokalny.
5. Dynamiczne potwierdzenie kolejności RX → write 2165 → kolejny tick FUN_08062638 → RTC.

## 6. Status A3

### CLOSED
- RTC hardware.
- auto-sync method.
- scheduler execution.
- PID 0x372F jako enable gate.
- PID 0x2165 jako Compatibility timestamp.
- storage 0x20008D28.
- standardowy CAN RX parameter-write engine może zapisać PID 0x2165.

### OPEN
- dokładny producent po drugiej stronie CAN.
- konkretny command/SDO/PDO, który niesie timestamp.
- czy istnieje drugi producer lokalny.