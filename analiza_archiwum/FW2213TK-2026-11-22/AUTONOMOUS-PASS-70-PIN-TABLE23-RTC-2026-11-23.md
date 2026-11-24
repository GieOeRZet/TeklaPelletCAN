# PASS 70 — PIN / tabela 23 / RTC (statyczne domknięcie zakresu A1-A3)

## Streszczenie

Zweryfikowano ponownie na kanonicznym BIN SHA-256 `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`, 2,031,616 B.

Najważniejsze wyniki:

1. **A1 — ukryte kody PIN:** w dokładnym handlerze specjalnym `FUN_08018634` pozostają trzy stałe bezpośrednie: **1992**, **6666** i **0**, plus osobny lookup przez `FUN_080144B4`. Nie znaleziono drugiej niezależnej gałęzi stałej w tym handlerze. 1992 zwiększa licznik o `0x01E13380` s; 6666 ustawia flagę `obj+7`; 0 ją kasuje. Lookup 23 rekordów również ustawia tę samą flagę.
2. **A2 — tabela 23:** `FUN_080144B4` rzeczywiście iteruje **23** rekordy (`cmp #0x17`), czytając `u16 [record+8]`. Adres katalogu to SRAM `0x20008C50`, więc 23. wartości nie można uczciwie odczytać z surowego BIN bez odtworzenia stanu zdekompresowanego RAM. **23. wartość = OPEN.** `FUN_080144E4` jest wywołana statycznie z jednym znanym callerem i dostaje u16 z pola obiektu `[r10+0x1A]`; semantyka tego pola nadal OPEN.
3. **A3 — RTC:** firmware ma rzeczywisty sprzętowy zapis/odczyt RTC. `FUN_08018E94` zapisuje spakowany czas do rejestrów peryferium `0x40002800/08/0C`; `FUN_08018F18` odczytuje z `0x40002800`; `FUN_08018FF8` odczytuje z `0x40002804` i rozpakowuje pola BCD. Nie znaleziono w katalogu 655 PID-u oznaczonego jako bieżący czas/zegar. Istnieje natomiast panelowy PID **0x372F "Is automatic time synchronization"**, klasa 3, storage `0x20021FD0`; dokumentacja repo potwierdza, że **nie odpowiada na kotle** i jest "TYLKO W FW PANELA". Zatem nie jest to PID czasu przesyłany do sterownika.
4. Alarmy mają już zamkniętą konwersję timestamp -> UTC przez `FUN_08049370`; timestamp jest Unix epoch seconds UTC. To potwierdza format używany przez panel lokalnie, ale **nie dowodzi istnienia ramki CAN z bieżącym czasem**.

## Ustalenia

| Temat | Dowód | Status |
|---|---|---|
| 1992 w handlerze PIN | PROJECT `0x08018638`: `cmp.w r5,#0x7c8`; `0x08018760` = `0x01E13380`; zapis `[obj+0x24]` | FACT |
| 6666 w handlerze PIN | PROJECT `0x08018668`: `movw r0,#0x1a0a`; przy trafieniu `strb r0,[obj,#7]` z wartością 1 | FACT |
| 0 w handlerze PIN | PROJECT `0x08018676..0x0801867E`: `cbnz r5`; dla 0 `strb #0,[obj,#7]` | FACT |
| Lookup tabeli 23 | PROJECT `0x080144B4..0x080144E2`: `[ptr]`, `[record+8]`, pętla do `0x17` | FACT |
| Baza lookup | PROJECT `0x0801452C` zawiera `0x20008C50` | FACT |
| 23. rekord | SRAM jest inicjalizowany/dekompresowany poza prostym odczytem RAW | OPEN |
| `FUN_080144E4` | Jedyny znaleziony statyczny caller: PROJECT `0x0805F612`; argument = `u16 [r10+0x1A]`; wynik trafia dalej do budowy obiektu | FACT; semantyka OPEN |
| RTC write | PROJECT `0x08018E98` ładuje `0x40002800`; `0x08018EE0` zapisuje rejestr bazowy, `0x08018EE2..0x08018EE8` modyfikuje +0x0C, `0x08018EEC` czyta +0x08 | FACT |
| RTC read | PROJECT `0x08018F18..0x08018F3C` czyta `0x40002800` i rozbija pola do bufora | FACT |
| RTC conversion/read helper | PROJECT `0x08018FF8`: czyta `0x40002804`, maskuje i rozbija pola; przy trybie 0 wykonuje BCD->bin | FACT |
| RTC field conversion | PROJECT `0x0801906E` wykonuje konwersję pola używaną przez ścieżki RTC | FACT |
| Auto-sync setting | PID `0x372F`, u8 0..1, class 3, storage `0x20021FD0` | FACT |
| 0x372F jako PID kotła | Repo: "TYLKO W FW PANELA", na kotle nie odpowiada | FACT |
| Bieżący czas jako PID CAN | brak takiego rekordu w runtime catalog 655 | STRONG negative; nie zamyka ramek PDO/SDO poza katalogiem |
| Timestamp alarmów | `FUN_08049370` = Unix epoch seconds / UTC, potwierdzone PASS 51 | FACT |

## A1 — specjalny handler PIN

Łańcuch jest:

`PIN -> FUN_0803C21C -> FUN_08018634 + FUN_08037E74`.

`FUN_08037E74` jest osobnym mapperem poziomu i rozpoznaje tylko `0/900/999/6154`; nie znaleziono w nim dodatkowych kodów.

W `FUN_08018634`:

- **1992**: dodaje `0x01E13380 = 31,536,000 s = 365 dni` do wartości bazowej z `[obj+0xE0]+0x0C` i zapisuje wynik do `[obj+0x24]`.
- **lookup 23**: `FUN_080144B4(code)`; jeśli zwróci 1, `[obj+7]=1`.
- **6666**: `[obj+7]=1`.
- **0**: `[obj+7]=0`.
- po tych gałęziach nie ma kolejnej stałej specjalnej w tym handlerze.

Wniosek: **nie ma podstaw, aby dopisywać kolejne stałe PIN-y tylko na podstawie tego handlera.** Jedyną realną nierozstrzygniętą klasą są wartości z rejestru 23 rekordów.

## A2 — tabela 23

`FUN_080144B4` ma bardzo mocny, mechaniczny dowód:

- baza: `[0x0801452C] = 0x20008C50`;
- rekord: wskaźnik z tablicy;
- klucz: `u16 [record+8]`;
- krok tablicy: 4 bajty;
- licznik: start 0, zwiększany o 2, kończy gdy `counter >= 0x17`.

To daje dokładnie **23 wpisy**.

Znanych 22 wartości nie podnoszę ponownie do FACT z samego RAW BIN, bo pochodzą ze zdekompresowanego RAM/emulatora Claude'a. W tym passie ich rola jest traktowana jako dane przekazane z toru dynamicznego.

**23. wartość pozostaje OPEN.**

Nie wolno jej zgadywać jako mocy kotła, mocy palnika ani innego modelu tylko dlatego, że 22 znane liczby wyglądają jak katalog mocy. To jest obecnie wyłącznie INFERENCE.

Dodatkowo `FUN_080144E4` korzysta z tej samej tablicy i zwraca pole `+0x0C` znalezionego rekordu. Jej jedyny znaleziony statyczny caller używa jako klucza `u16 [r10+0x1A]`. To jest ważny trop do znaczenia obiektów, ale nie jest dowodem semantyki "moc kotła".

## A3 — RTC i czas

### Zapis

`FUN_08018E94`:

- pobiera bazę `0x40002800`;
- pola wejściowe są konwertowane przez `FUN_0801906E`;
- składają się w wartość 32-bit;
- zapisuje do `0x40002800`;
- modyfikuje `0x4000280C` i odczytuje `0x40002808`.

To jest rzeczywista ścieżka ustawiania sprzętowego RTC, nie tylko formatowanie danych.

### Odczyt

`FUN_08018F18` czyta `0x40002800` i rozdziela pola do bufora.

`FUN_08018FF8` czyta `0x40002804`, maskuje wartość i rozdziela pola; w trybie 0 wykonuje konwersję BCD do wartości binarnych. To odpowiada ścieżce pobierania czasu z RTC.

### CAN

W katalogu 655 nie ma rekordu odpowiadającego "current time", "current date", "clock" itp. Są timestampy historii alarmów oraz timestampy serwisowe, ale są to dane pamięci/zdarzeń, nie bieżący zegar.

PID `0x372F` jest nazwany **Is automatic time synchronization**. Jest ustawieniem panelu, nie czasem. Repo ma dodatkowo niezależny dowód, że `0x372F` nie odpowiada na kotle i jest tylko w firmware panela.

Dlatego obecny status:

- **RTC panelu = FACT**
- **lokalny format czasu = FACT**
- **PID 0x372F = FACT, ale nie jest czasem**
- **ramka CAN z bieżącym czasem = OPEN**
- **zapis czasu przychodzącego z CAN = OPEN**

## FACT / STRONG / INFERENCE / OPEN / REJECTED

### FACT
- 1992, 6666 i 0 są bezpośrednimi gałęziami `FUN_08018634`.
- Lookup 23 wpisów jest mechanicznie potwierdzony.
- RTC jest obsługiwany bezpośrednio przez peryferium `0x40002800...`.
- PID 0x372F jest ustawieniem automatycznej synchronizacji czasu i należy do panela.

### STRONG
- W katalogu 655 nie ma osobnego PID-u bieżącego zegara.
- Najbardziej prawdopodobne jest, że synchronizacja automatyczna korzysta z lokalnej funkcji panelu/warstwy Internet/WiFi, a nie z klasycznego PID-u sterownika. To nadal wymaga śledzenia wywołań.

### INFERENCE
- 23 rekordy mogą reprezentować katalog wariantów/mocy/modeli. Nie traktować tego jako zamknięte.
- `FUN_080144E4` może być ogólnym "find object by value", ale semantyka obiektów wymaga dalszego śledzenia.

### OPEN
1. 23. wartość `0x20008C50`.
2. Pełne znaczenie 23 obiektów.
3. Kto wywołuje RTC setter w rzeczywistym przepływie "Ustaw czas".
4. Czy istnieje CAN/PDO poza katalogiem 655, który przenosi bieżący czas.
5. Czy PID 0x372F włącza synchronizację z Internetu/NTP lub innym źródłem.
6. Czy istnieje ścieżka CAN RX -> RTC setter.

### REJECTED
- Hipoteza, że 0x372F jest PID-em czasu kotła — odrzucona.
- Hipoteza, że można dopisać dowolne "ukryte PIN-y" na podstawie samych 16-bitowych literalów 1992/6666 znalezionych w innych miejscach BIN — odrzucona; liczy się kontrola przepływu w handlerze.

## Pytania do Claude (dynamika/emulator)

1. Prześledź w emulatorze dialog "Ustaw czas" aż do wywołania `FUN_08018E94`/powiązanego wrappera i zapisz format wejścia (rok/miesiąc/dzień/godzina/minuta) oraz moment zapisu RTC.
2. Włącz trace CAN + wywołania funkcji podczas ustawiania czasu. Szukamy **jakiejkolwiek ramki po CAN bezpośrednio związanej z ustawieniem zegara**.
3. Przetestuj zmianę PID 0x372F w panelu: czy powoduje jakąkolwiek aktywność sieciową/CAN lub tylko zmianę konfiguracji UI.
4. Dla tabeli 23: z RAM po boot/inicjalizacji podaj **23. wpis** oraz wartość `[entry+8]`; nie potrzebujemy ponownej emulacji całej ścieżki PIN.
5. Jeśli to możliwe, sprawdź caller `FUN_080144E4` z `[r10+0x1A]`: jaki obiekt/parametr jest w `r10` i czy jego wartości pokrywają się z katalogiem 23.
