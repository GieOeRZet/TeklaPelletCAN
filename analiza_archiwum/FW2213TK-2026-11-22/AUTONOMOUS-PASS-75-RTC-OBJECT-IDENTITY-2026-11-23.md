# PASS 75 — identyfikacja obiektu RTC auto-sync w głównym anchorze SRAM

Data: 2026-11-23

## Wynik

Udało się zejść o jeden poziom niżej: obiekt, którego metodą slot 0 jest FUN_08062638, ma znany adres SRAM.

### Twardy łańcuch

1. Startup/init ładuje `r8 = 0x20008CD0` z literal pool.
2. Pod PROJECT 0x08000DC6 wywołuje konstruktor-like `0x0801044C` z:

       r0 = r8 + 0x4C

3. Zatem obiekt ma adres:

       0x20008CD0 + 0x4C = 0x20008D1C

4. Konstruktor `0x0801044C` zapisuje runtime vptr `0x080A446C` do `[object+0]`.
5. `0x080A446C - 0x10000 = PROJECT 0x0809446C`.
6. Slot 0 pod `PROJECT 0x0809446C` zawiera runtime pointer `0x08072639`.
7. `0x08072639 - 0x10000 - Thumb = PROJECT 0x08062638 = FUN_08062638`.

### Wniosek

**Obiekt auto-sync RTC = `0x20008D1C`** (na podstawie kompletnego łańcucha startup → konstruktor → vptr → vtable slot 0).

To jest istotne, ponieważ od teraz można szukać producenta timestampu bez abstrakcyjnego `param+0x0C`.

## 1. Layout obiektu używany przez FUN_08062638

| Adres | Offset | Znaczenie |
|---|---:|---|
| 0x20008D1C | +0x00 | vptr = runtime 0x080A446C |
| 0x20008D24 | +0x08 | poprzednia wartość czasu / stan porównania |
| 0x20008D28 | +0x0C | **timestamp producer input / bieżąca wartość czasu** |
| 0x20008D2C | +0x10 | poprzednio zapamiętana wartość do compare |
| 0x20008D30 | +0x14 | licznik wywołań, resetowany co 10 |
| 0x20008D3A..0x20008D44 | +0x1E..+0x28 | rozłożone pola daty/czasu używane przez metodę |

Uwaga: pola +0x1E..+0x28 są wypełniane przez FUN_08039370 przed RTC write; nie należy traktować ich jako trwałego wejścia.

## 2. Co robi FUN_08062638 z tym obiektem

- `[0x20008D30]` jest inkrementowane jako bajt.
- przy wartości 10 jest zerowane i wykonywana jest cięższa ścieżka.
- `[0x20008D2C]` jest porównywane z `[0x20008D28]`.
- gdy są różne, PID `0x372F` decyduje, czy synchronizacja ma wykonać zapis RTC.
- po odczycie/normalizacji bieżącego RTC `FUN_08062920` daje wartość epoch, która trafia do `[object+0x0C] = 0x20008D28`, a następnie `[object+0x10] = 0x20008D2C`.

Najważniejsze dla dalszego skanu pozostaje:

    WRITE 0x20008D28

To jest obecnie **najbardziej precyzyjny cel statycznego RE** dla znalezienia źródła czasu.

## 3. FUN_08062920 — potwierdzenie epoch

FUN_08062920 przyjmuje strukturę z polami:

- +0x00 sekundy,
- +0x04 minuty,
- +0x08 godziny,
- +0x0C dzień,
- +0x10 miesiąc,
- +0x14 rok.

Funkcja wykonuje arytmetykę kalendarzową i korzysta z `FUN_0803BB58()` jako punktu odniesienia czasu. Wynik jest 64-bitową arytmetyką epokową, a w FUN_08062638 używana jest część niskiego słowa.

To zamyka model: `0x20008D28` jest wartością timestampową, a nie dowolnym parametrem.

## 4. Następny skan

Nie należy już szukać ogólnie `param+0x0C`.

Priorytet:

1. wszystkie sposoby wyliczenia adresu `0x20008D28`;
2. wszystkie STR/STR.W do tego pola;
3. funkcje wywołujące te write-sites;
4. sprawdzenie, czy zapis pochodzi z CAN RX, synchronizacji sieciowej, UI czy innego timera.

Jeżeli znajdziemy write-site, A3 może zostać zamknięte do poziomu źródła timestampu.