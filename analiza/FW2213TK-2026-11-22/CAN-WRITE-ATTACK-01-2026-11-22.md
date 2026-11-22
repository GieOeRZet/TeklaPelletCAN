# NewEstyma — CAN WRITE/TX ATTACK 01 — 2026-11-22

Firmware: FW2213TK_kopia.bin
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

## Cel

Oddzielić twardo potwierdzony transport CAN TX od nieudowodnionego jeszcze mostu UI WRITE -> CAN.

## CLOSED / HARD

### 1. TX queue transport

0x08057224 jest FreeRTOS-style queue-send primitive.

Potwierdzony direct caller w obszarze CAN:
0x0806E604 -> 0x08057224.

0x08057224 przekazuje rekord do mechanizmu kolejki, a 0x080574E4 realizuje kopiowanie do kolejki / aktualizację count.

Kolejka TX:
0x200244EC = CanMessagesToTransmit.

### 2. Hardware TX

CanTxTask:
0x080654A8

Ścieżka konsumenta:
CanMessagesToTransmit -> CanTxTask -> 0x08061734 -> CAN2 0x40006800.

0x08061734 bezpośrednio programuje mailbox CAN TX.

### 3. 0x0806E59C

Funkcja buduje lokalny rekord 0x14 B z wejścia r1:
- +0 = StdId
- +2..+0xA = payload/metadata copied from source.

Kontrola:
- obiekt 0x2002466C;
- jeśli byte +9 == 0 i byte +10 == 1, wysyłka jest blokowana;
- poza tym wejściowy StdId musi być 0x0604;
- handle kolejki pobierany z 0x200244EC;
- wywołanie 0x08057224 z queue handle, lokalnym rekordem, wait=1, copy-position=0.

Wniosek:
0x0806E59C jest wyspecjalizowanym adapterem TX dla ścieżki 0x0604, nie ogólnym CanSendMessage().

### 4. Dispatch/vtable

Fizyczna tabela dispatch:
0x08094508

Slot 5:
0x08094544 -> 0x0807E59D -> physical 0x0806E59C.

Slot 8:
0x08094568 -> 0x080729FD -> physical 0x080629FC.

Konstruktor 0x080157A0 zapisuje high-space form 0x080A4508 jako vptr obiektu.

To dowodzi istnienia wspólnej class/dispatch table zawierającej zarówno TX adapter, jak i poller.

Nie dowodzi jeszcze, że [0x2002466C+0x14] wskazuje konkretnie na instancję z tym vptr.

## PARAMETER READ — CLOSED

0x080629FC:
- pobiera parametr z runtime table:
  base = *(obj+0x18)
  index = *(u16*)(base + counter*0x2C + 0x08)
- zapisuje index do obj+0x0E;
- przy index != 0 wywołuje 0x08062AE4.

0x08062AE4:
- buduje CAN frame StdId 0x0604;
- command byte 0x40;
- następnie wykonuje BLX przez [obj+0x14].

Wspólny dispatch table daje silny związek:
poller -> 0604 request -> dispatch -> TX adapter -> TX queue.

## PARAMETER WRITE — nadal OPEN

Potwierdzona ścieżka RX WRITE:
CAN2 RX
-> 0x080617DC
-> ReceivedCanMessages
-> CanRxTask
-> 0x08063B80
-> 0x08062A90
-> StdId 0x0584
-> 0x08062B22
-> 0x08011812
-> parameter record +0x0C / local RAM.

Potwierdzona ścieżka UI WRITE:
UI
-> 0x08037212
-> 0x08011812
-> parameter record +0x0C
-> local RAM.

0x08011812 NIE jest potwierdzonym dirty-bit/TX setterem:
- nie wywołuje 0x0806E59C;
- nie wywołuje 0x08057224;
- nie ma potwierdzonego post-write CAN callbacku.

Zatem obecnie:
UI WRITE -> local parameter RAM = HARD.
local parameter RAM -> CAN TX = OPEN.

## WAŻNA KOREKTA

Nie należy pisać jako HARD:
UI -> 0x08037212 -> 0x08011812 -> 0x0806E59C.

Tego połączenia nie ma w aktualnym RAW proof.

## NEXT

1. Ustalić inicjalizację [obj+0x14] w 0x2002466C.
2. Ustalić slot/callback wykonywany po zmianie lokalnego parametru.
3. Prześledzić 0x08056A1C / 0x08056A44, ponieważ są dodatkowymi direct callers 0x08057224.
4. Połączyć record+0x0C consumer z TX frame construction.
5. Dopiero wtedy zamknąć UI WRITE -> CAN.

## Status

TX transport: CLOSED.
0x0604 parameter READ request path: CLOSED/STRONG, z jednym otwartym przypisaniem instancji vtable.
RX parameter WRITE: CLOSED.
UI local WRITE: CLOSED.
UI WRITE -> CAN TX bridge: OPEN.
