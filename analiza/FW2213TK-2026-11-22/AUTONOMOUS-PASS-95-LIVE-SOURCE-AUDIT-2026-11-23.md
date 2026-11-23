# PASS 95 — LIVE source audit (S9) — 2026-11-23

## Domknięte statycznie
- Panel ma osobny tor danych LIVE. `EstymaTask` odświeża obiekt czujnika z producenta źródłowego, więc zwykły zapis PID przez `0x584` nie jest trwałym źródłem wartości LIVE.
- Węzły 5, 6 i 7 są cyklicznie odpyt ywane przez panel przez CANopen SDO: `0x605..0x607`, odczyt `0x2001:01`; odpowiedzi mają standardowy zakres `0x585..0x587`.
- Panel posiada równoległe rodziny ramek PDO-podobnych `0x2xx/0x3xx/0x4xx/0x5xx`, których zawartość zasila modułowy tor LIVE. Statycznie można potwierdzić ich istnienie i rytm, ale nie można uczciwie przypisać konkretnego PID `0x2001/0x2277/0x3333/0x4000/0x3628` do konkretnego ID/slotu PDO bez obserwacji odpowiedzi modułu.

## PID-e
`0x2001` = Boiler temperature; `0x2277` = Boiler pump state; `0x3333` = Boiler pressure; `0x4000` = Boiler return temperature; `0x3628` = Statistics total energy produced.

## Granica statycznego RE
**OPEN:** dokładne `node/channel -> PDO frame -> PID` dla tych pięciu LIVE PID-ów. Istniejący materiał potwierdza, że źródłem jest modułowy tor CAN, ale nie zawiera wystarczającego dowodu, aby przypisać kanały bez eksperymentu dynamicznego. Nie zgaduję mapowania.

## Wniosek dla emulatora
Emulator powinien modelować odpowiedzi CAN modułów (w szczególności węzłów 5..7) oraz tor ramek PDO-podobnych, zamiast próbować utrzymywać wartości LIVE przez `0x584`.
