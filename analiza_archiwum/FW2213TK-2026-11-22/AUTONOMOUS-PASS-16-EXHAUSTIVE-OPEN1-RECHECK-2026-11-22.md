# AUTONOMOUS PASS 16 — EXHAUSTIVE OPEN-1 RECHECK — 2026-11-22

## Cel

Kolejny pełny przebieg po aktualnym repo pod kątem wszystkich aktywnych OPEN związanych z:
- +0x7178
- +0x7180
- FUN_08010FCE
- scheduler/framework
- lokalny WRITE -> publikacja CAN
- 260 catalog -> CAN matrix.

## Wyniki

### D60 / READ/TX boundary

Wcześniejszy runtime artifact PASS 09 daje twarde potwierdzenie:
- [0x20008D60] = 0x080A4544
- vtable slot 0 -> 0x0806E59C
- poller+0x14 = 0x20008D60
- poller+0x18 = 0x20008D84
- node4[0] = 0x20008D60.

Pełny READ/TX chain jest więc CLOSED/HARD.

### +0x7178

W aktualnym materiale nadal brak bezpośredniego store/assignment konkretnego obiektu do pola.

Zamknięty jest wyłącznie kontrakt:
- slot 0 = GET(PID, 5-byte typed descriptor) -> status
- slot +4 = SET(PID, value, type).

Użycie:
- registration
- periodic provider synchronization
- sidecar 2/3.

STATUS: OPEN — concrete object/vtable.

### +0x7180

Zamknięty jest kontrakt:
- vtable slot 0
- outbound publication sink
- używany zarówno przez local-change publication, jak i round-robin publication
- wire: StdId 0x0584, DLC 8, command 0x42.

Brak niezależnego dowodu konkretnego obiektu/vtable.

STATUS: OPEN — concrete object/vtable.

### FUN_08010FCE

Zamknięte:
- vtable 0x080A44F0 slot 0 -> FUN_08010FCE
- konstruktor 0x0800DDE4
- startup object family
- callback group
- body: provider sync -> tracked publication -> periodic publication.

Brak niezależnego runtime trace pokazującego dokładny caller/dispatcher -> FUN_08010FCE.

STATUS: OPEN — scheduler invocation edge.

### 260-slot matrix

Nadal nie ma kompletnego, mechanicznie potwierdzonego mapowania:
260 catalog -> runtime record -> PID -> CAN READ/WRITE/PUBLISH.

STATUS: OPEN.

## Ważna kontrola jakości

Nie znaleziono nowego dowodu, który pozwalałby uczciwie podnieść trzy główne OPEN-y do HARD. Nie wykonano sztucznego promotion.

## Toolchain

Nowe narzędzia z PASS 15 są przygotowane do:
re_scan -> vtable_scan -> runtime_trace_analyzer.

Próba uruchomienia testów w bieżącym środowisku wykonawczym została zablokowana przez brak dostępu sieciowego do GitHub, więc nie traktujemy lokalnego uruchomienia jako wykonanego dowodu.

## Następny atak

Priorytet 1:
- odzyskać/wykorzystać istniejący runtime trace z callback group
- wyłapać pierwszy INDIRECT_CALL prowadzący do 0x08010FCE
- równolegle śledzić wartości pól this+0x7178 i this+0x7180.

Priorytet 2:
- korelacja konkretnego vptr z obiektem parameter-managera.

Priorytet 3:
- automatyczna enumeracja PID -> CAN publication.

## Status

PASS 16 nie zmienia procentów. Zawęża natomiast granicę dowodową: nie ma podstaw do uznania +0x7178/+0x7180 ani scheduler route za HARD.