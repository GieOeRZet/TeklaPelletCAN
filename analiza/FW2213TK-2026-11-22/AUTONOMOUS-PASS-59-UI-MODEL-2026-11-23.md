# AUTONOMOUS-PASS-59 — UI-MODEL

Date: 2026-11-23

## Cel

Polaczyc inwentarz widgetow TouchGFX z PASS 58 staticzna mapa prezenterow przez
view_off = this - aktywny widok, bez zgadywania PID po pozycji lub nazwie.

## Wykonane

- Dodano tools/ui_model.py.
- Dodano tools/test_ui_model.py.
- Model przyjmuje JSON z screen_inventory_menu.py, a takze prostszy JSON z listami widgetow.
- Kazdy widget dostaje presenter_candidates.
- Jednoznaczne dopasowanie ma evidence EXACT_VIEW_OFF.
- Wieloznaczne dopasowanie pozostaje AMBIGUOUS_VIEW_OFF i zachowuje wszystkich kandydatow.
- Brak dopasowania pozostaje UNRESOLVED_VIEW_OFF.
- Dodano plaska postac CSV i raport statystyczny.

## Dowod

PASS 58 dostarcza 273 wywolania model_get w 9 klastrach oraz widget_offsets.
PASS 57/ctor_trace dostarcza this i view_off dla obiektow widgetow.
Ich wspolnym kluczem jest lokalny offset wzgledem aktywnego widoku.

To jest zamkniecie mechanicznego polaczenia widget -> presenter candidate.
Nie jest jeszcze dowodem, ze kazdy kandydat jest faktycznie wyswietlany w danym
wariancie ekranu; do tego potrzebne sa dalsze dane konstruktora/akcji.

## Weryfikacja

Dodano syntetyczny test regresyjny obejmujacy:
1. jednoznaczne EXACT_VIEW_OFF,
2. brak dopasowania,
3. wieloznaczne dopasowanie,
4. prawidlowa liczbe wierszy plaskiego eksportu.

Nie wykonano pelnego przebiegu emulatora, poniewaz lokalny firmware BIN i scratchpad
stanow UI nie sa dostepne jako pliki w tej sesji. Nie wpisano wiec zadnych
niezweryfikowanych statystyk ekranow do repo.

## Nastepny etap

Graf akcji: dla kazdego dotykalnego widgetu ustalic:
widget -> handler -> zmiana ekranu/dialogu lub PID -> ramka CAN / efekt modelu.

Priorytet: zachowac ten sam podzial FACT / STRONG / INFERENCE / OPEN / REJECTED.
