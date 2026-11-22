# AUTONOMOUS PASS 17 — PARAMETER MANAGER OBJECT / SCHEDULER CLOSURE — 2026-11-22

## Cel

Zamknięcie aktualnych OPEN wokół konkretnego obiektu za +0x7178/+0x7180 oraz runtime route do FUN_08010FCE.

## NEW-HARD 1 — konkretny parameter-manager object

RAW disassembly konstruktora PROJECT 0x0800DDC0 pokazuje:
- r0 = this
- r1 = provider object
- r2 = publication sink
- konstruktor najpierw wywołuje base scheduler constructor 0x08014824 z r1=1
- następnie zapisuje vptr 0x080A44F0 pod [this+0]
- zapisuje r1 pod [this+0x7178]
- zapisuje r2 pod [this+0x7180].

Startup PROJECT 0x080001AC wywołuje 0x0800DDC0 pod 0x0800024A z:
- r0 = 0x20008D84
- r1 = 0x20008D64
- r2 = 0x20008D60.

Zatem:
- parameter-manager object = 0x20008D84
- concrete +0x7178 provider object = 0x20008D64
- concrete +0x7180 publication sink = 0x20008D60
- parameter-manager vtable = 0x080A44F0.

To zamyka wcześniejsze OPEN dotyczące konkretnego obiektu za obydwoma polami.

## NEW-HARD 2 — concrete provider object

Obiekt 0x20008D64 jest konstruowany przez PROJECT 0x0800DB08.
Jego vptr = 0x080A31F0.
Nie jest scheduler-derived; konstruktor wykonuje własną inicjalizację przez 0x08014870 i 0x08014A70.

To jest konkretny obiekt implementujący provider interface używany przez +0x7178.

Pełne rozstrzygnięcie wszystkich slotów vtable 0x080A31F0 pozostaje osobnym targetem; nie zgadujemy slotów niepotwierdzonych.

## NEW-HARD 3 — concrete publication sink

Obiekt 0x20008D60 ma runtime vptr 0x080A4544.
Vtable slot 0 prowadzi do FUN_0806E59C.
FUN_0806E59C prowadzi do TX queue 0x200244EC -> xQueueGenericSend 0x08057224 -> CanTxTask -> CAN2.

Zatem +0x7180 nie jest abstrakcyjnym/nieznanym sinkiem: jest to konkretny obiekt CAN TX 0x20008D60.

## NEW-HARD 4 — scheduler route

0x0800DDC0 wywołuje base scheduler constructor 0x08014824 dla this=0x20008D84.
0x08014824 ustawia scheduler fields i rejestruje this przez 0x0801478C w singleton managerze 0x200246E8.

Scheduler main loop 0x080147C8 iteruje zarejestrowane obiekty i przy expiry wykonuje virtual slot 0.

Parameter-manager vtable 0x080A44F0 slot 0 = FUN_08010FCE (wcześniej potwierdzone vtable evidence).

Zatem pełny architektoniczny route jest:
startup 0x080001AC
-> 0x0800DDC0(0x20008D84, 0x20008D64, 0x20008D60)
-> base scheduler 0x08014824
-> scheduler registration 0x0801478C
-> scheduler loop 0x080147C8
-> vtable 0x080A44F0 slot0
-> FUN_08010FCE
-> FUN_08011368 + FUN_0801117C + periodic publication.

To zamyka wcześniejszy OPEN na poziomie statycznego/runtime architecture. Niezależny trace konkretnego ticka scheduler -> 0x08010FCE nadal jest dodatkową walidacją, ale nie jest już brakującym ogniwem architektury.

## NEW-HARD 5 — 0x7178 / 0x7180 ownership

Cały model parameter managera jest teraz:

0x20008D84
  +0x00 -> vtable 0x080A44F0 -> slot0 FUN_08010FCE
  +0x7178 -> 0x20008D64 -> vtable 0x080A31F0 -> provider interface
  +0x7180 -> 0x20008D60 -> vtable 0x080A4544 -> FUN_0806E59C -> CAN TX

To jest kluczowe rozdzielenie:
- provider = 0x20008D64
- publication/CAN sink = 0x20008D60.

## Remaining OPEN after PASS 17

1. Pełne sloty vtable 0x080A31F0 — provider GET/SET implementation bodies.
2. Niezależny runtime trace scheduler expiry -> FUN_08010FCE.
3. Pełna 260-slot PID -> storage/type/min/max/default -> provider/CAN/UI matrix.
4. Pełna lista PID-ów wybieranych przez FUN_0801117C.
5. Dokładna semantyka sidecar 1/2/3.
6. Pozostałe UI/CAN object graphs.

## Evidence discipline

Nie użyto zgadywania slotów provider vtable. Konkretne adresy obiektów wynikają z argumentów rzeczywistego konstruktora 0x0800DDC0 i startup call 0x0800024A; vptr 0x20008D60 pochodzi z niezależnego runtime evidence.

## Status

PASS 17 zamyka dwa z największych dotychczasowych OPEN-ów: concrete +0x7178/+0x7180 ownership oraz architektoniczny scheduler route.