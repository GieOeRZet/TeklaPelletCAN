# AUTONOMOUS PASS 85 — CAN 0x584/0x604 ROLE + TIMESTAMP SOURCE BOUNDARY — 2026-11-23

## 1. Fixed CAN IDs around the parameter engine
RAW 0x62A90 checks incoming frame StdId 0x584 and, only when the object gates permit it, dispatches the frame to FUN_08062B22.
RAW 0x62AE4 constructs an outgoing parameter-read request with StdId 0x604, command byte 0x40, PID u16 LE and subindex 1.

Therefore the firmware contains a fixed request/response pair:
- request path: 0x604 / 0x40 / PID / sub 1;
- receive/write path: 0x584 / wire-type discriminator / PID / sub 1.

## 2. Timestamp implication
PID 0x2165 is accepted by the generic 0x584 write decoder and stored at 0x20008D28. PASS 79 proved that the panel's normal 0x584 publication builders explicitly exclude 0x2165.

The remaining static model is therefore strong:
external boiler-side/source traffic -> 0x584 write of PID 0x2165 -> parameter manager -> 0x20008D28 -> RTC auto-sync gate 0x372F.

Because 0x604 is explicitly used to poll the remote parameter endpoint associated with this pair, the remote endpoint is the boiler-side node addressed by that fixed protocol path. Static code does not prove whether PID 0x2165 arrives as a direct response to a 0x604 poll or as an unsolicited parameter write using the same 0x584 envelope.

## 3. What is CLOSED vs OPEN
CLOSED:
- exact timestamp wire PID: 0x2165;
- exact storage: 0x20008D28;
- exact write envelope: StdId 0x584, opcode 1, u32 LE;
- panel normal TX exclusion of 0x2165;
- fixed remote polling request StdId 0x604 / cmd 0x40.

OPEN:
- exact trigger/request sequence that causes the boiler-side source to emit 0x2165;
- whether the timestamp is in a normal response, unsolicited write, or another boiler-side producer path;
- ACK/response behavior specific to timestamp writes.