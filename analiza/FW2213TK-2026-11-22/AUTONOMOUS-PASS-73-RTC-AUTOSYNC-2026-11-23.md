# PASS 73 — RTC auto-sync: domknięcie statycznego mechanizmu 0x372F → timestamp → RTC

Data: 2026-11-23

## Wynik

Ten PASS znajduje w pełnym zdekompilowanym kodzie bezpośrednią ścieżkę użycia PID 0x372F do ustawienia sprzętowego RTC.

Kluczowa funkcja: FUN_08062638 (718 B). Powiązane funkcje: FUN_08018E94 (RTC setter), FUN_08018F18 (RTC reader), FUN_08018FF8 (odczyt/konwersja RTC).

Najważniejszy wniosek:

> 0x372F nie jest czasem. Jest bramką, która zezwala funkcji synchronizacji na zastosowanie zewnętrznego timestampu przechowywanego w obiekcie synchronizacji do sprzętowego RTC.

Nie znaleziono w tej funkcji żadnego odczytu czasu z CAN. Źródło timestampu pozostaje osobnym OPEN.

## 1. Twardy dowód z FUN_08062638

Funkcja najpierw porównuje [param+0x10] z [param+0x0C]. Gdy są różne, pobiera PID 0x372F przez FUN_080115F6(...,0x372F), następnie FUN_08014728/FUN_08014734. Jeżeli wartość jest niezerowa, przechodzi do synchronizacji.

Jako źródło czasu wykorzystuje [param+0x0C], a nie wartość PID 0x372F. Następnie FUN_08039370 rozbija timestamp na pola daty/czasu, po czym FUN_08018E94(0,&local_time) wykonuje rzeczywisty zapis sprzętowego RTC.

Po synchronizacji [param+0x10] zostaje ustawione na [param+0x0C], czyli timestamp zostaje oznaczony jako już zastosowany.

## 2. Adresy instrukcji

| Projekt | Znaczenie |
|---|---|
| 0x080627AE | movw r2,#0x372F |
| 0x080627E2 | bl FUN_08018F18 |
| 0x08062808 | bl FUN_08018FF8 |
| 0x080628A8 | bl FUN_08039370 |
| 0x080628E6 | bl FUN_08018E94 |
| 0x08062920 | FUN_08062920, konwersja/normalizacja timestampu |

Scanner tools/cg_rtc_autosync_scan.py potwierdza te sygnatury oraz obecność runtime pointera 0x08072639 w kanonicznym BIN.

## 3. Znaczenie pól obiektu

| Pole | Rola |
|---|---|
| param+0x0C | timestamp do zastosowania / nowy czas synchronizacji |
| param+0x10 | poprzednio zastosowany timestamp / znacznik ostatniej synchronizacji |
| param+0x08 | stan/licznik związany z generowaniem czasu; używany w ścieżce normalnego odczytu |
| param+0x16..0x1E | rozłożone pola czasu/datym używane przez obiekt |

Mechanizm jest więc: zewnętrzny timestamp → konwersja → RTC hardware.

## 4. Status A3

### Zamknięte
- RTC hardware panelu — FACT.
- 0x372F — FACT: enable/disable automatic time synchronization.
- 0x372F nie zawiera czasu — FACT.
- Automatyczna synchronizacja rzeczywiście wywołuje RTC setter — FACT.
- Synchronizacja korzysta z timestampu przechowywanego w obiekcie — FACT.
- Po zastosowaniu timestamp jest kopiowany z +0x0C do +0x10 — FACT.

### Nadal OPEN
1. Kto zapisuje [param+0x0C].
2. Skąd pochodzi timestamp: CAN, NTP/Internet/Wi-Fi albo inny mechanizm panelu.
3. Kto wywołuje FUN_08062638. Nie ma bezpośredniego BL do PROJECT 0x08062638, ale RAW zawiera runtime pointer 0x08072639 dokładnie raz, pod PROJECT 0x0809446C. To jest twardy dowód, że funkcja jest używana przez mechanizm wskaźnikowy/dynamic-dispatch; nie zamyka jeszcze konkretnego caller object.
4. Dokładny format wszystkich pól daty przekazywanych do FUN_08018E94.
5. Czy ustawienie czasu z UI korzysta z tej samej funkcji, czy bezpośrednio z RTC setterem.

## 5. Najważniejsze rozróżnienie

Nie wolno zapisywać w dokumentacji: 0x372F → CAN time.

Dowód mówi: 0x372F → enable gate; param+0x0C → timestamp source; FUN_08039370 → date/time decomposition; FUN_08018E94 → RTC hardware.

Najważniejszym brakującym ogniwem są wszystkie zapisy do pola +0x0C obiektu używanego przez FUN_08062638.

## 6. FUN_08062920

FUN_08062920 pracuje na strukturze pól sekundy/minuty/godziny/dzień/miesiąc/rok i wykonuje arytmetykę epokową oraz odejmuje wynik FUN_0803BB58(). Jest to spójne z wcześniejszym rozpoznaniem Unix epoch seconds, ale nie stanowi dowodu źródła timestampu.

## 7. Test regresyjny

Dodano tools/cg_rtc_autosync_scan.py oraz tools/test_cg_rtc_autosync_scan.py.

Scanner potwierdza: PID 0x372F @ 0x080627AE; RTC read @ 0x080627E2; RTC helper @ 0x08062808; timestamp decomposition @ 0x080628A8; RTC write @ 0x080628E6.

