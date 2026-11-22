# SOFTWARE-FIRST REVERSE ENGINEERING TARGET — 2026-11-22

## Cel nadrzędny

Projekt NIE jest obecnie projektem ESP32. Najpierw należy możliwie kompletnie odtworzyć zachowanie i model software'u Estymy tak, aby później można było wykorzystać go niezależnie od platformy.

Docelowe zastosowania wynikające z tego samego odzyskanego modelu:

1. pełny emulator firmware/modelu,
2. emulator urządzenia po CAN,
3. emulacja/udawanie odpowiedniego węzła lub panelu na CAN,
4. własny sterownik zastępujący funkcjonalność oryginału,
5. klon panelu/ekranu z zachowaniem jego logiki,
6. zewnętrzny panel sterujący,
7. integracja Home Assistant,
8. Web/Android/desktop,
9. dopiero na końcu dobór MCU/platformy: ESP32-C6 lub inny mikrokontroler.

Platforma sprzętowa nie może ograniczać modelu odzyskanego z firmware.

## Zasada architektoniczna

Najpierw odzyskujemy:

FW behavior
-> object model
-> parameter/state model
-> CAN protocol
-> UI model
-> state transitions
-> validation/access/capability
-> persistence/publication
-> timing/tasks

Dopiero potem projektujemy implementacje:

canonical software model
-> emulator
-> CAN node
-> panel clone
-> controller
-> HA/Web/Android adapters
-> MCU backend

## Aktualny makro-P0

### A. Runtime parameter/object engine

Domknąć:

- pełny rekord 0x2C,
- ownership 0x20008D84,
- wszystkie pola +0x00..+0x2B,
- FUN_0801143C registration,
- FUN_080115F6 lookup,
- FUN_0801167A,
- FUN_080116E6,
- FUN_080117B4,
- FUN_08011812,
- obiektowe tablice rekordów,
- dynamiczne instancje CO1..CO4,
- storage pointers,
- type semantics,
- validation/range semantics,
- commit/update semantics.

Ważna granica: wcześniejsze interpretacje +0x2C/+0x30 jako pól tego samego rekordu są odrzucone.

### B. Parameter graph

Zbudować jeden dowiedziony graf:

catalog
-> mapper
-> external PID
-> runtime record
-> storage
-> type
-> getter
-> setter
-> validation
-> CAN request
-> CAN response/publication
-> UI binding
-> persistence

Nie zakładać, że 260 catalog entries = wszystkie runtime/CAN parameters.

### C. Full GUI

Celem nie jest samo menu root.

Odtworzyć:

menu
-> screen
-> submenu
-> child/widget
-> constructor
-> parent/child relation
-> visibility/capability
-> access level
-> parameter binding
-> text
-> bitmap/resource
-> handler
-> state transition
-> touch/navigation
-> resulting parameter/state change.

Dopiero wtedy mamy podstawę do prawdziwego klonu ekranu.

### D. Runtime behavior

Po zamknięciu modelu statycznego odzyskać:

- taski,
- kolejki,
- timery,
- periodic polling,
- heartbeat/presence,
- CAN publication,
- state machines,
- event dispatch,
- startup state,
- error handling,
- persistence,
- watchdog-related behavior.

### E. Emulator as verification target

Emulator nie ma być celem końcowym, lecz narzędziem dowodowym.

Powinien umożliwić:

- startup,
- odtworzenie obiektów,
- runtime parameter state,
- CAN RX/TX,
- UI state,
- wykonywanie akcji,
- obserwację zmian RAM/state,
- porównanie zachowania z firmware.

## Priorytet kolejnego makro-passa

1. Exhaustive record-engine closure.
2. Dynamic instance/object-record closure.
3. 568 mapper -> PID -> record mapping.
4. Full parameter getter/setter/validation matrix.
5. Full CAN parameter graph.
6. Full GUI screen/widget graph.
7. Runtime state/event/task graph.
8. Emulator extension and differential verification.

Nie wykonywać teraz prac projektowych zależnych od ESP32.

## FACT / INFERENCE boundary

Każdy odzyskany element ma mieć status:

- HARD/FACT — bezpośredni dowód RAW/dekompilacji/runtime,
- STRONG — wielokrotnie potwierdzony przepływ,
- INFERENCE — model wynikający z kilku faktów,
- OPEN — brak dowodu,
- REJECTED — wcześniejsza interpretacja sprzeczna z aktualnym dowodem.

Nigdy nie podnosić INFERENCE do FACT bez nowego dowodu.

## Aktualny stan

CAN2 runtime: mocno zamknięty.
Parameter catalog: mocno zamknięty jako osobna warstwa.
Mapper 568: zamknięty mechanizm.
Runtime record geometry: zamknięta baza/stride/kluczowe pola, pełny layout nadal OPEN.
MenuTree mechanism: zamknięty.
Pełne GUI semantics: OPEN.
Pełny runtime behavior: OPEN.
Pełny CAN catalog/behavior: OPEN.

## Docelowy rezultat RE

Rezultatem reverse engineeringu ma być nie tylko dokumentacja adresów firmware, lecz platform-agnostic behavioral specification:

- objects,
- records,
- parameters,
- instances,
- states,
- events,
- screens,
- widgets,
- resources,
- permissions,
- CAN frames,
- timing,
- persistence,
- transitions.

Dopiero ten model będzie podstawą implementacji na dowolnej platformie.
