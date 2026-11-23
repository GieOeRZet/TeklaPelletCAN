# AUTONOMOUS-PASS-60 — UI ACTION GRAPH

Date: 2026-11-23

## Cel

Zbudowac kolejna warstwe po UI-MODEL: widget -> handler -> efekt.

## Wykonane

- tools/action_graph.py przyjmuje UI-MODEL i log akcji.
- Target widgetu jest rozwiazywany po this/addr albo node+tap.
- Kazda akcja zachowuje handler i efekty jako dane wejściowe.
- Brak targetu nie jest zgadywany: UNRESOLVED_ACTION_TARGET.
- Wieloznaczne node+tap jest jawnie oznaczane.
- tools/test_action_graph.py pokrywa EXACT_WIDGET, EXACT_NODE_TAP i UNRESOLVED_ACTION_TARGET.

## Granica dowodu

Narzedzie NIE wywnioskuje samodzielnie efektu CAN/PID z samego stukniecia.
Efekt musi pochodzić z trace/harnessu firmware. To zapobiega promowaniu
hipotez UI do FACT.

## Nastepny krok

Dopasowac rzeczywiste logi tap/handler z UiSession/ctor_trace do UI-MODEL,
a nastepnie dolaczyc zmiany PID, ekranu/dialogu i ramek CAN.
