# NewEstyma — RE Harness Progress — 2026-11-22

## Wykonane

Powstal platform-independent runtime evidence harness w `software/re_harness/`.

### Instrumentacja

- TraceEvent / TraceLog z typami CALL, RETURN, READ, WRITE, INDIRECT_CALL, CAN_RX, CAN_TX, SNAPSHOT.
- WatchpointSet dla krytycznych obszarow RAM.
- DEFAULT_TARGETS obejmuje:
  - 0x20008D60 — parameter-table-object
  - 0x20008D84 — parameter-record-table
  - 0x200114C0 — node4-object-record
  - 0x2002466C — CAN-poller-object
  - 0x200244EC — CAN-TX-queue
  - 0x200244DC — CAN-RX-queue
- self-checki w `software/re_harness/test_harness.py`.

## Najwazniejsza zmiana

Emulator nie ma juz byc tylko backendem wykonawczym. Adapter ARM ma produkowac
dowody runtime, ktore mozna laczyc z obecna baza statycznego RE.

Pierwsze automatyczne closure targets:
1. pierwszy writer 0x20008D60,
2. obiekt 0x2002466C,
3. [0x2002466C+0x14] -> vptr -> slot0,
4. implementacje +0x7178/+0x7180,
5. CAN replay + snapshot diff.

## Status

Instrumentacja: 1. etap wykonany.
Adapter konkretnego backendu ARM: jeszcze OPEN.

Nie podnosze sztucznie procentu calosci tylko za utworzenie harnessu. To jest
narzedzie przyspieszajace nastepne closure. Metryka pozostaje rozdzielona na:
static RE, runtime RE, software model i 1:1 reproduction.
