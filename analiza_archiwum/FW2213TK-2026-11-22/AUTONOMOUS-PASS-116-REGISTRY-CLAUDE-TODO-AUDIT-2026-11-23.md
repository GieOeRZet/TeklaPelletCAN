# AUTONOMOUS PASS 116 — Registry 16/17/18 + Claude TODO audit — 2026-11-23

## Cel
Kontynuacja bez pauzy po PASS 115. Sprawdzono ostatnie przekazane przez Claude zadania/testy oraz ponownie prześledzono statyczny łańcuch registry dla selectorów 16/17/18.

## 1. Ostatni materiał Claude — stan
W repo nadal obowiązują dwa zadania dynamiczne Claude:
- B1: 6666 -> CAN PID 0x0005 + reakcja wskaźnika +0x210.
- B2: weryfikacja bramki pollera [0x2002466C+0x10].

Nie znaleziono w aktualnym materiale repo dowodu, że te testy dynamiczne zostały wykonane. Status pozostaje WSTRZYMANE; nie promuję ich jako zamkniętych.

## 2. Registry/menu — twardy łańcuch
Potwierdzone wcześniejszymi artefaktami:
- FUN_0807EB00 dopasowuje sender do this+0x3B4+i*0x274.
- Dopasowany indeks i trafia do FUN_0803C064(this+0x3C,i).
- źródłem selectorów jest tabela RAM 0x20005EF0.
- selector 16 -> PROJECT 0x0803856C -> +0x12B=0x11.
- selector 17 -> PROJECT 0x08038568 -> +0x12B=0x10.
- selector 18 -> PROJECT 0x08038574 -> odrębna ścieżka.

## 3. Co zostało zamknięte, a czego nie wolno dopowiadać
Zamknięte:
- indeks registry -> dispatcher,
- dispatcher -> callback dla 16/17/18,
- callback 16/17 -> wartości +0x12B,
- dalszy page-family resource switch zależny od +0x12B.

Nadal OPEN:
- dokładny semantic title rekordów 16/17/18,
- dokładny PID/presenter dla tych rekordów,
- pełny callback/resource chain dla selector 18,
- jednoznaczna identyfikacja modelu/obiektu rejestru na podstawie runtime danych.

## 4. Decyzja metodologiczna
Nie używać bitmap ID, geometrii ani samego tekstu jako dowodu semantycznego. Następny przebieg powinien szukać:
1. inicjalizacji rekordów +0x3B4+i*0x274,
2. pól descriptorów +0x60/+0x64 i callback/model binding,
3. source table 0x20005EF0 oraz wszystkich XREF,
4. połączenia z title/resource/PID dopiero po znalezieniu twardego łańcucha.

## Wynik
PASS 116 nie zamyka jeszcze S1.3, ale zawęża go do source/runtime initialization i descriptor binding. Praca statyczna trwa bez przejęcia zadań dynamicznych Claude.
