# AUTONOMOUS PASS 97 — ALARM RAISE / CLEAR / ACKNOWLEDGE CLOSURE

## Result
The alarm path previously marked OPEN in PASS 91 is now closed wherever the existing firmware trace provides hard evidence.

## Closed state machine
1. raise(code): 0x08025198 checks whether the same code is already active; otherwise writes code | 0x10000 | 0x20000 into the current 20-entry ring slot, writes current time, clears confirmation timestamp, and advances the ring index modulo 20.
2. active state: bit16 of the alarm register.
3. unacknowledged state: bit17 of the alarm register.
4. acknowledge: observed panel action writes the alarm register through CAN 0x584 and clears bit17; a confirmation timestamp is written to the matching 0x4038+i record.
5. clear: 0x08025104 is the clear-by-code helper. This is separate from acknowledgement.
6. reset memory: PID 0x404E is the panel-local Request reset alarm memory command; storage is 0x20021F94.

## Important correction
ACK does not clear the active condition. PASS 51 observed the alarm remaining ACTIVE after POTWIERDZ. Therefore bit17 (acknowledged/unacknowledged) and bit16 (active/inactive) are independent state bits.

## CAN proof
Observed acknowledgement publication: StdId 0x584, data 42 12 40 01 69 00 01 00, i.e. PID 0x4012 register write with value 0x00010069. The corresponding confirmation timestamp publication is PID 0x403A.

## Remaining boundary
The static alarm manager and acknowledgement path are closed. The exact individual call-site semantics for every one of the ~40 clear sites, and the full causal condition that clears each alarm code, remain separate because those are per-alarm business conditions rather than the generic alarm-manager state machine.
