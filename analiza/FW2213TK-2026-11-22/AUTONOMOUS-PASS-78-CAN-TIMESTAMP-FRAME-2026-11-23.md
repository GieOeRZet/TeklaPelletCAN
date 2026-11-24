# PASS 78 — CAN producer closure for PID 0x2165 (Compatibility timestamp)

## Streszczenie

PASS 77 wykazał, że 0x20008D28 jest storage PID 0x2165 (Compatibility timestamp) i że ogólny tor CAN RX może zapisywać ten parametr.

PASS 78 domyka warstwę transportową tego zapisu statycznie:

- odbiorczy handler parametrów jest wywoływany dla StdId 0x584 w pokazanym torze;
- przed wywołaniem FUN_08062B22 handler sprawdza pole z ramki pod frame+3: po przesunięciu o 5 musi dać 2;
- FUN_08062B22 pobiera PID jako little-endian u16 z frame+4/+5;
- byte frame+6 jest kodem operacji; tylko wartość 1 prowadzi do zapisu parametru;
- dla zapisu wartości 32-bit ścieżka używa frame+7..frame+10 jako little-endian u32;
- dla PID 0x2165 katalog potwierdza typ u32 i storage 0x20008D28.

Zgodny zapis czasu ma więc logicznie postać: CAN 0x584 + PID 0x2165 + opcode 1 + u32 timestamp LE.

Nie domknięto jeszcze semantyki źródła wartości timestampu ani pełnej odpowiedzi/ACK.

## Ustalenia

| Ustalenie | Dowód | Etykieta |
|---|---|---|
| PID 0x2165 = Compatibility timestamp | data/pid_matrix_655.csv: rekord 0x2165, u32, storage 0x20008D28, class command | FACT |
| Storage PID 0x2165 = 0x20008D28 | katalog PID + PASS 77 | FACT |
| Handler RX sprawdza StdId 0x584 | PROJECT 0x08062AB2..0x08062AD8: load StdId, cmp #0x584, BL 0x08062B22 | FACT |
| Handler wymaga ((frame+3) >> 5) == 2 | PROJECT 0x08062AC8..0x08062AD2 | FACT |
| PID jest pobierany z frame+4/+5, little-endian | PROJECT 0x08062B2C..0x08062B36 | FACT |
| frame+6 == 1 jest warunkiem wejścia w zapis | PROJECT 0x08062B74..0x08062B7E | FACT |
| Dla wire type 5 dane są składane z frame+7..frame+10 jako LE u32 | PROJECT 0x08062C18..0x08062C2A | FACT |
| Decoder 0x08014720 oznacza wartość jako type=3 (u32) | PROJECT 0x08014720..0x08014726 | FACT |
| FUN_08011812 zapisuje po znalezieniu PID i zgodności type/class | PROJECT 0x08011838..0x08011894 | FACT |
| PID 0x2165 ma typ u32 i class/sidecar command | data/pid_matrix_655.csv | FACT |
| Zgodny zapis timestampu używa StdId 0x584, PID 0x2165, opcode 1, u32 LE | połączenie powyższych dowodów | STRONG |
| 0x584 oznacza węzeł 4 w sensie CANopen | sam firmware tego nie dowodzi | INFERENCE |
| Nadawcą wartości czasu jest konkretny moduł | tor statyczny tego nie identyfikuje | OPEN |

## Dokładny tor

CAN RX → handler @ 0x08062A90 → StdId 0x584 → FUN_08062B22 → PID(frame+4/5) → opcode(frame+6)==1 → decode wire type → FUN_08011812 → record+0x0C → storage 0x20008D28 (PID 0x2165)

Dla u32: frame[7] + frame[8]<<8 + frame[9]<<16 + frame[10]<<24 jest przekazywane przez decoder 0x08014720 jako typ 3, zgodny z rekordem 0x2165.

## FACT / STRONG / INFERENCE / OPEN / REJECTED

### FACT
- 0x584 jest sprawdzanym StdId w bezpośrednim callerze FUN_08062B22.
- 0x2165 jest PID-em Compatibility timestamp.
- PID jest little-endian w frame+4/+5.
- frame+6 == 1 uruchamia zapis.
- u32 jest kodowane z frame+7..frame+10 little-endian.
- docelowy storage to 0x20008D28.

### STRONG
- Pełny format transportowy zapisu 0x2165 jest zamknięty statycznie w zakresie tego handlera.

### INFERENCE
- 0x584 może być adresem CANopen węzła 4, ale nie oznaczamy tego jako FACT.

### OPEN
- Kto generuje timestamp przed wysłaniem/ustawieniem PID 0x2165.
- Czy istnieje alternatywny lokalny producent 0x20008D28.
- Czy i jak nadawca otrzymuje ACK/rezultat zapisu.
- Czy panel sam wysyła aktualny czas do 0x584, czy tylko odbiera timestamp.

### REJECTED
- Hipoteza, że potrzebna jest osobna specjalna ramka czasu niezwiązana z PID 0x2165 — w zamkniętym torze zapisu nie jest potrzebna.

## Pytania do Claude

1. W emulatorze przechwycić ruch 0x584 podczas automatycznej synchronizacji czasu i potwierdzić PID 0x2165, opcode 1 oraz u32 timestamp.
2. Ustalić, czy 0x584 jest nadawany przez moduł kotła jako źródło czasu, czy przez inną warstwę.
3. Sprawdzić ACK/odpowiedź po zapisie 0x2165.
