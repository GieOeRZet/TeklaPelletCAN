# AUTONOMOUS PASS 43 — RUCH CAN PANELU PO STARCIE (PUSTA MAGISTRALA), TABLICA WĘZŁÓW, BRAMKA POLLERA — 2026-11-23

Firmware SHA-256 `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`. Narzędzia: `tools/stm32_can.py` (model CAN2), `tools/can_boot_trace.py` (+ `test_can_boot_trace.py`). Dane: `data/can_tx_boot_no_partners.csv`.
Adresy: PROJECT (RUNTIME = +0x10000). Wymaga emulatora systemowego z PASS 42.

## Metoda
Pełny system (FreeRTOS + LTDC + DMA2D) + model CAN2: TX przechwytuje zapisy do `TIxR/TDTxR/TDLxR/TDHxR` (TXRQ = bit 0 `TIxR`), z ustawionymi flagami TME w `TSR` (bez nich firmware uznaje brak wolnej skrzynki i `0x08061734` zwraca 4);
RX wpisuje ramkę do FIFO0 (`RIR/RDTR/RDLR/RDHR` @ `0x40006800+0x1B0..`) i zgłasza IRQ 64. Stan: **brak jakiegokolwiek urządzenia na magistrali**.

## HARD — kiedy panel zaczyna nadawać
Scheduler obiektów okresowych `FUN_080247C8`: każdy obiekt ma `+4` = okres (reload) i `+5` = licznik; co ok. 100 ms licznik maleje, a po zerze wywoływany jest slot 0 vtable obiektu i licznik ładowany z `+4`.
Obiekt `0x2002466C` startuje z licznikiem **30** i okresem 1 (konstruktor `0x08024832/0x0802482E`), więc **pierwsze ramki pojawiają się dopiero po ok. 3,3 s od startu schedulera** (tick ≈ 3313 w emulacji).

## HARD — ramki nadawane przy pustej magistrali (106 w 6000 tikach; `data/can_tx_boot_no_partners.csv`)
| ID | DLC | dane | znaczenie (dowód) |
|---|---|---|---|
| `0x704` | 1 | `05` co ok. 1 s | **heartbeat węzła 4 = operational** (CANopen NMT; `0x700+4`, PASS 9: node ID = 4) |
| `0x605`, `0x606`, `0x607` | 8 | `20 04 30 01 00 00 00 00` (co ~1 s, najpierw) oraz `40 01 20 01 00 00 00 00` (co ~1 s) | żądania SDO do węzłów **5, 6, 7**: zapis (cmd `0x20`) parametru `0x3004:01 = 0` i cykliczny odczyt (cmd `0x40`) `0x2001:01` |
| `0x584` | 8 | `42 <pid_lo> <pid_hi> 01 <val32>` | publikacje wartości lokalnych (PASS 38): np. `0x2111=7`, `0x2166=0x46`, `0x2299=1`, `0x22AD=0x46`, `0x22FD=5`, `0x3171..0x3173=0x4E16`, `0x2101=0`, `0x2122=0x00080001`… |
| `0x250` | 8 | zera | co ok. 200 ms |
| `0x254`, `0x255` | 8 | `01 00 …` | co ok. 1 s |
| `0x26F`, `0x270`, `0x271` | 8 | zera | co ok. 1 s |
| `0x201` | 8 | `00 00 10 0e 00 …` / zera | |
| `0x240..0x247` | 4 | zera | seria co ok. 5 s |
| `0x278, 0x27A..0x27F`, `0x340..0x347`, `0x356`, `0x378, 0x37A..0x37F`, `0x440..0x447` (w tym `0x545` zamiast `0x445`), `0x456`, `0x540..0x547`, `0x556` | 8 | zera | serie ramek PDO-podobnych co ok. 5 s (rodziny `0x2xx/0x3xx/0x4xx/0x5xx` + numer 0..7) |
Wartości w ramkach PDO-podobnych są zerowe, bo magistrala jest pusta (brak danych wejściowych) — kształt i rytm ramek jest dowodem wykonania, ich zawartość nie.
Nie ma ramek `0x604` (poller pracuje innym torem, patrz niżej).

## HARD — tablica obecności węzłów i skan tożsamości
- Handler rodziny `0x0800F894` (RUNTIME `0x0801F894`): dla `StdId` w `0x701..0x77F` (heartbeat) oraz `0x581..0x5FF` (odpowiedź SDO) ustawia w obiekcie `[obj + n·4 + 0xC] = 1` (żywy) i `[obj + n·4 + 0xE] = [obj+6]` (czas); `FUN_0801F91A` zeruje flagę po **0x12C = 300** jednostkach czasu ciszy.
- `FUN_0801F8CA` wysyła `0x600+k` z `40 18 10 02 …` — **odczyt obiektu `0x1018` sub 2 (Identity/Product code wg CiA 301)** — dla `k = [obj+0x2B0]` cyklicznie `1..0x80`. To jest skanowanie węzłów i jednoznaczny dowód, że protokół jest CANopen SDO (expedited), a nie tylko „SDO-podobny” (PASS 37).
- W emulacji ten skan nie wystąpił w 6000 tikach (funkcja nie została wywołana w tym scenariuszu) — OPEN, kto ją wywołuje.

## HARD (eksperyment) — wstrzykiwanie nie włącza pollera
Heartbeaty `0x701..0x77F` (po jednym węźle na raz, `05`) oraz odpowiedzi tożsamości `0x580+k: 43 18 10 02 34 12 00 00` dla k = 1..127 **nie zmieniają** pól pollera (`0x2002466C+0x10` pozostaje 0, brak `0x604`). Odbiór ramek działa (CanRxTask budzi się), ale sama obecność węzłów nie jest bramką.

## HARD (kod) — bramka pollera ustawiana z menu
Pola sterujące pollera `0x2002466C`: `+8` (start) i `+0x10` (aktywny; wymagany do przetwarzania odpowiedzi `0x584` i generowania `0x604`, PASS 37). Zapisy do `+0x10` w kodzie klas UI:
`0x0804C24E: strb r0,[r1,#0x10]` z `r0 = (poziom dostępu +0x158 ≠ 0)` oraz `0x0804C260: strb 1,[r0,#0x10]` (oba w sąsiedztwie dispatchera klas `FUN_0803C064`). Wniosek (STRONG): **odczyt parametrów z centrali po `0x604` jest włączany przez akcje menu/ekran ustawień, nie przez wykrycie magistrali**; ekran główny korzysta z publikacji `0x584` od centrali.
Do rozstrzygnięcia: które klasy (ekrany) wywołują te zapisy i czy `+8` jest ustawiane tamże.

## Implikacje dla ESP32-C6
1. Moduł powinien nadawać heartbeat `0x700+nodeID` `05` co 1 s (nie wcześniej niż po inicjalizacji).
2. Panel aktywnie czyta węzły 5, 6, 7 obiektem `0x2001:01` co 1 s i zapisuje im `0x3004:01 = 0` — to sygnatura „modułów pokojowych”; moduł ESP32 o jednym z tych ID będzie **odpytywany** i musi odpowiadać `0x580+n: 43 01 20 01 …`.
3. Struktury `0x2xx..0x5xx` są wymieniane cyklicznie; zawartość do ustalenia przez wstrzykiwanie odpowiedzi i obserwację ekranu.

## OPEN
1. Które klasy menu ustawiają `obj+0x10` i `obj+8`; zachowanie panelu przy włączonym pollerze (ramki `0x604` w pełnym cyklu i reakcja na odpowiedzi — połączyć z PASS 37).
2. Kto wywołuje skan `0x1018:02` (`FUN_0801F8CA`) i jakie ID węzłów uznaje za centralę.
3. Semantyka ramek `0x2xx..0x5xx` (zawartość po podaniu danych) i okresy; mapowanie rodzin na węzły/obwody.
4. Odpowiedzi węzłów 5..7 (`0x585..0x587`) i ich wpływ na stan ekranu.
