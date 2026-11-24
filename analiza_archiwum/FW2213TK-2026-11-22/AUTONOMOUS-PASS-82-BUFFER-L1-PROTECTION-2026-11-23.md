# AUTONOMOUS PASS 82 — BUFFER L>=1 + OGRZEWANIE PROTECTION CONDITION — 2026-11-23

## 1. Bufor L>=1 — CLOSED

Menu/list builder `FUN_0804E714` dispatchuje po `model+0x12B` (klasa). Klasa `0x07` to Bufor.

Dla klasy `0x07` ścieżka zaczyna się RAW `0x3E7DA` (artifact `0x0804E7DA`). Najpierw tworzony jest pierwszy element klasy. Następnie firmware pobiera `model+0x158` i wykonuje:

- RAW `0x3E7F2`: `ldrb r0,[model,#0x158]`
- `cmp r0,#0`
- RAW `0x3E7F8`: `beq 0x3EB0A`

Czyli drugi element Bufora jest dodawany dokładnie dla `level != 0`.

Następnie RAW `0x3E7FC..0x3E808` dodaje drugi wpis przez wspólny helper `FUN_0803EFDA`, z parametrami `r5/r2 = 5` i offsetem/resource `0x110`.

To jest twarde zamknięcie B3 dla bramki Bufora: **Bufor ma dodatkowy element UI od poziomu L1, warunek jest dokładnie `model+0x158 != 0`.** Nie jest to L2 ani L3.

## 2. Źródła danych ekranu Bufor

Prezenter Bufora znajduje się RAW `0x3DF78` (artifact `0x0804DF78`). Kolejno pobiera klucze UI:

- `0xF1` -> PID `0x2112` Buffer top measured temperature
- `0xF2` -> PID `0x2113` Buffer bottom measured temperature
- `0xF5` -> PID `0x2280` Buffer top set temperature
- `0xF4` -> PID `0x2115` Buffer bottom set temperature
- `0xF8` -> PID `0x3171` Buffer T1 measured temperature
- `0xF9` -> PID `0x3172` Buffer T2 measured temperature
- `0xFA` -> PID `0x3173` Buffer T3 measured temperature
- `0xFB` -> PID `0x3174` Buffer internal energy [%].

Zatem wildcard `0%` na ekranie Bufora jest powiązany z **PID `0x3174` Buffer internal energy [%]**, a nie z procentowym stanem pompy.

Konfiguracja Bufora to PID `0x2107` (u8 0/1), ale nie jest ona używana jako bramka L1 w samym konstruktorze ekranu; konstruktor/list builder używa bezpośrednio `model+0x158`.

## 3. `7°C` na Buforze

Firmware ma zakres minimalny `7°C` dla PID-ów ustawień Bufora:
- `0x2114` Buffer top set temperature: min 7, max 80, default 45
- `0x2115` Buffer bottom set temperature: min 7, max 80, default 65.

Sam prezenter ekranu nie pozwala jednak statycznie przypisać wildcardu `7°C` do jednego z tych dwóch pól wyłącznie na podstawie kolejności getterów. W szczególności `0xF3 -> 0x2114` nie występuje jako osobny getter w tym prezenterze, podczas gdy `0xF4 -> 0x2115` i `0xF5 -> 0x2280` występują. Dlatego **nie wpisuję arbitralnego PID dla `7°C`**.

## 4. `Ochrona kotła` — dalsza analiza

Prezenter ekranu Ogrzewanie 1 jest RAW `0x3D37C` (artifact `0x0804D37C`). Czyta m.in. klucze:
- `0xA8`
- `0xB2`
- `0xB0`
- `0xC6`
- `0xAB`
- `0xCB`
- `0xAC`.

Wcześniejsza hipoteza łączyła `Ochrona kotła` z `CH status` PID `0x22FD`, ale w tej funkcji nie ma bezpośredniego getter-a `0xA8 -> 0x22FD` użytego jako prosty warunek widoczności tekstu. Jest natomiast warunek na wartości klucza `0xB0` oraz ścieżki zależne od `0xC6`. To oznacza, że hipoteza `CH status == ...` nie jest jeszcze dowodem.

**Status:** Bufor L>=1 CLOSED; źródło `0%` CLOSED; dokładny PID dla `7°C` OPEN; warunek widoczności `Ochrona kotła` OPEN.

## 5. Następny krok

Zostaje prześledzić setter/widget group dla `Ochrona kotła` i dokładnie związać jego widoczność z getterami `0xB0/0xC6/0xA8`, a następnie domknąć `7°C` przez widget->setter->model_get.