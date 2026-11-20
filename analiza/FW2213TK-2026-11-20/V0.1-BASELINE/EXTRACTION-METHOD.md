# V0.1 Extraction Method

## Rule
Execute extraction tasks exactly. Do not silently reinterpret raw results. Never overwrite source handoffs; create a new artifact for every run.

## Screen record
constructor
setupScreen
tearDownScreen
vtable
base class
children + offsets + geometry
bitmap IDs
TypedText IDs
parameters read/write
visibility/editability gates
PIN/access gates
callbacks
navigation targets
transitions
animations
unknowns

## Parameter record
key, raw record, label IDs, EN/PL, unit, editor type, flags, extra/options, min/max, step, scale, signedness, storage type, read xrefs, write xrefs, CAN mapping, visibility, editability, dependencies.

## CAN record
controller, register base, init, bit timing, filters, RX/TX IRQ, message ID, DLC, payload, signal layout, cycle, timeout, request/response, special cases, parameter key, errors.

## Evidence
FACT / LIKELY / HYPOTHESIS / UNKNOWN.

## Analysis order
raw bytes -> decode -> xrefs -> caller/callee -> structures -> parameters -> assets/text -> conditions -> semantic name -> confidence.

## Final canonical databases
parameters.json
can_messages.json
can_signals.json
screens.json
widgets.json
navigation.json
typedtext.json
bitmaps.json
fonts.json
alarms.json
schedules.json
nvm.json
access.json