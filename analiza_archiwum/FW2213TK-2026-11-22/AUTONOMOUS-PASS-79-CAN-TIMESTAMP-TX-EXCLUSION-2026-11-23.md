# AUTONOMOUS PASS 79 — CAN TIMESTAMP TX EXCLUSION / PRODUCER BOUNDARY — 2026-11-23

## Cel
Domknąć statycznie otwarty punkt z PASS 78: czy panel sam produkuje CAN dla PID 0x2165 (Compatibility timestamp), czy 0x2165 jest wyłącznie wartością przyjmowaną z magistrali.

## FACT

### 1. 0x2165 jest jawnie wykluczony z dwóch ścieżek publikacji parametrów
W funkcji PROJECT `0x0802117C` (RAW `0x1117C`) firmware iteruje po tabeli runtime i przed zbudowaniem publikacji `0x584/0x42` porównuje PID z:
- `0x2165` — Compatibility timestamp,
- `0x3726`,
- `0x2311..0x2314`.

Dla tych PID-ów wykonywany jest skok do końca iteracji bez publikacji.

Dowód RAW:
- `0x080211EE`: `movw r3,#0x2165`
- `0x080211F6`: porównanie z PID z rekordu
- `0x080211FC..0x08021200`: skok pomijający budowę ramki.

### 2. Specjalna ścieżka publikacji również jawnie pomija 0x2165
Funkcja PROJECT `0x080212A6` (RAW `0x112A6`) wykonuje analogiczny wybór bieżącego rekordu i ponownie odrzuca:
- `0x2165`,
- `0x3726`,
- `0x2311..0x2314`.

Dowód RAW:
- `0x080212B8`: `movw r3,#0x2165`
- `0x080212C0`: porównanie
- `0x080212CA`: skok do końca iteracji.

Ta funkcja jest rzeczywistą ścieżką wywoływaną z callbacku przez wcześniejszy branch z `0x08021100`.

### 3. Normalna publikacja 0x584/0x42 ma dokładnie znany format
W `0x0802117C`:
- StdId = `0x0584`,
- DLC = 8,
- cmd = `0x42`,
- PID = rekord+8,
- sub = 1,
- wartość = zdekodowana wartość parametru.

Wniosek: PID 0x2165 nie trafia do tej publikacji, mimo że jest obecny w runtime table.

### 4. Jedyny potwierdzony wejściowy zapis 0x2165 pozostaje ścieżką RX
PASS 78 zamknął:
`CAN RX StdId 0x0584 -> frame PID 0x2165 -> type u32 -> FUN_08011812 -> record+0x0C -> storage 0x20008D28`.

Dla wire type 5 wartość jest składana little-endian z frame+7..+10.

### 5. Pozostałe wystąpienia kodowe 0x2165 nie tworzą ramki CAN czasu
Wystąpienia związane z kodem kompatybilności w okolicach RAW `0xE994` i `0xEA02` są częścią mapowania lokalnych identyfikatorów `0x40..0x47/0x56 -> 0x2164..0x216E` i wywołują `FUN_08015198` / `FUN_08015104`.

Te funkcje operują na wewnętrznej tabeli 20 rekordów/flag i nie są generic CAN TX builderem ani ścieżką zapisu `0x20008D28`.

Dodatkowo wystąpienie przy RAW `0x4A48` jest częścią instrukcji `movw r1,#0x2265`, więc nie jest literalnym PID `0x2165`.

## STRONG

Statycznie bardzo mocny jest wniosek, że panel **nie publikuje PID 0x2165 przez standardowy mechanizm publikacji parametrów 0x584/0x42**. Firmware ma świadome wyjątki, a `0x2165` jest jednym z nich.

Najbardziej spójny model po PASS 78+79:
`zewnętrzny producent czasu -> CAN 0x0584/WRITE PID 0x2165 -> parameter manager -> 0x20008D28 -> RTC auto-sync gated by PID 0x372F`.

## INFERENCE

Najbardziej prawdopodobnym producentem `0x2165` jest sterownik/centrala na CAN, a nie panel. Nie wolno jednak nazwać konkretnego węzła producentem bez dynamicznego trace'u.

Nie należy też automatycznie utożsamiać `0x0584` z konkretnym numerem węzła tylko na podstawie numeracji CANopen.

## OPEN

1. Dynamicznie potwierdzić, czy przy aktywnym auto-sync (`0x372F=1`) pojawia się `0x0584` z PID `0x2165`.
2. Ustalić nadawcę tego frame (konkretny node).
3. Sprawdzić, czy po odebraniu timestampu panel wysyła ACK/response.
4. Sprawdzić, czy panel kiedykolwiek wysyła czas innym, niestandardowym formatem niezwiązanym z PID `0x2165`.

## REJECTED

- Hipoteza o osobnej, ukrytej ramce „time frame” w standardowej publikacji parametrów — brak potwierdzenia; 0x2165 jest celowo wykluczony z obu publisherów.
- Hipoteza, że mapowanie `0x2164..0x216E` z RAW `0xE994/0xEA02` jest bezpośrednim TX timestamp — brak ścieżki do CAN TX i brak zapisu do `0x20008D28`.

## Werdykt PASS 79

**HARD:** panelowy publisher `0x584/0x42` celowo wyklucza PID `0x2165` w dwóch ścieżkach publikacji.

**STRONG:** statyczny rewers nie pokazuje panelowego producenta CAN dla PID `0x2165`; obecny dowód wskazuje na wejście z CAN.

**OPEN:** wyłącznie identyfikacja zewnętrznego producenta i dynamiczne potwierdzenie frame/ACK.
