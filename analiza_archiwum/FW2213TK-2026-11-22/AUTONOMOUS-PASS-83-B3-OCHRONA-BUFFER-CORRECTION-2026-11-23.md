# AUTONOMOUS PASS 83 — B3 OCHRONA KOTŁA + KOREKTA BUFFER PID — 2026-11-23

## Cel
Domknąć statycznie warunek pola „Ochrona kotła” oraz skorygować mapowanie parametrów Bufora.

## 1. Ochrona kotła — twardy warunek danych

Prezenter Ogrzewanie PROJECT 0x0804D37C (RAW 0x3D37C) wykonuje:
- model_get(0xB0) = PID 0x22A1 „Room temp sensor type”;
- model_get(0xCD) = PID 0x2301 „CH thermostat state”;
- następnie przekazuje te dwie wartości do helpera PROJECT 0x08054848 (RAW 0x44848).

RAW 0x44848:
- jeśli sensor type (0x22A1) != 4: ustawia obiektowi +0xA69 = 0 oraz +0xA95 = 1;
- jeśli sensor type == 4: ustawia +0xA95 = 0 oraz +0xA69 = 1 tylko gdy CH thermostat state (0x2301) == 1, w przeciwnym razie +0xA69 = 0.

To jest HARD dowód warunku wejściowego dla dwóch flag widoku:
A95 = (Room temp sensor type != 4) ? 1 : 0
A69 = (Room temp sensor type == 4 && CH thermostat state == 1) ? 1 : 0.

Wniosek: wcześniejsza hipoteza, że napis „Ochrona kotła” jest bezpośrednio sterowany przez CH status 0x22FD, jest ODRZUCONA. W tej konkretnej ścieżce warunek opiera się na 0x22A1 + 0x2301. Nadal nie przypisuję arbitralnie, czy TypedText 87 jest związany z A69 czy A95 bez dodatkowego śledzenia konstrukcji widgetu.

## 2. Korekta mapowania Bufora

Wcześniejsze materiały mieszały 0x2114 i 0x2280. Dane firmware potwierdzają:
- UI key 0xF3 -> PID 0x2114 „Buffer top set temperature”, min 7°C, setting;
- UI key 0xF4 -> PID 0x2115 „Buffer bottom set temperature”, min 7°C, setting;
- UI key 0xF5 -> PID 0x2280 „Buffer top set temperature”, ale jest to osobny parametr live/read-only w macierzy 655, storage 0x2002213A, zakres 25..80;
- prezenter Bufora używa 0xF5 i 0xF4, więc nie wolno utożsamiać 0x2280 z nastawą 0x2114 tylko na podstawie nazwy.

0% pozostaje HARD jako UI key 0xFB -> PID 0x3174 „Buffer internal energy [%]”.

Źródło obserwowanego „7°C” nadal nie jest statycznie przypisane do konkretnego widgetu w prezenterze; min=7 dla 0x2114/0x2115 jest tylko ograniczeniem parametrów nastaw, nie dowodem renderowania konkretnego pola.

## 3. Istotna korekta PASS 81

PASS 81 błędnie opisał 0x20008D84 jako tablicę 23 rekordów po 0x14. To adres parameter managera, którego runtime table ma stride 0x2C.

Funkcje FUN_080143DE/FUN_08014416/FUN_0801443E przyjmują bazę rekordów przez argument, a katalog 0x20008C50 zawiera wskaźniki do tych runtime tablic. Literal 0x20008D84 występuje w kodzie jako manager, nie dowodzi, że jest bazą 23-elementowej tablicy.

Status A2 pozostaje:
- katalog 23 wpisów: CLOSED;
- record+0x08 = Parameters set Number: CLOSED;
- dokładny adres runtime source array: OPEN;
- 23. wartość record#23+0x0C: OPEN.

## 4. Następne cele
1. Zidentyfikować, czy A69 czy A95 steruje TypedText 87 / bitmapami ochrony.
2. Prześledzić widget „7°C” Bufora do setter-a i dokładnego PID.
3. Odnaleźć rzeczywistą bazę 23 rekordów wskazywaną przez wpisy 0x20008C50.
4. Domknąć konteksty czterech wrapperów L>=3.