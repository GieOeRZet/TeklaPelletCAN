# AUTONOMOUS PASS 112 — UI MODEL HOME BINDING — 2026-11-23

## Cel
Wykonać pierwszy etap S1: połączyć inwentarz widgetów z presenter map przez `view_off`, bez utożsamiania geometrii/bitmapy z PID.

## HARD
- `data/widgets_home_with_view_off.json` zawiera rzeczywiste adresy widgetów, `view_off`, geometrię, parent i touch.
- Root Home: `this=0x2001603c`, `view_off=4).
- Dzieci Home są reprezentowane jako obiekty z własnymi offsetami `view_off`.
- `data/presenter_map.csv` zawiera niezależne, źródłowe powiązania UI key -> PID -> setter -> widget_offsets.
- Potwierdzone Home PID bindings z presenter map:
  - 0x2001 = Boiler temperature, format %d.%d, div10;
  - 0x2004 = Boiler set result temperature;
  - 0x2005 = Boiler on/off;
  - 0x2007 = Burner state;
  - 0x2105 = Heating configuration;
  - 0x2014 = Hot water 1 program;
  - 0x3728 = Is reset required.
- Kocioł helper `0x08054848` ma HARD wejścia PID 0x22A1 + 0x2301 i zapisuje flagi A69/A95. Nie przypisano jeszcze TypedText 87 do jednej z flag.
- Bufor presenter map ma HARD bindings:
  - 0x2280,
  - 0x2115,
  - 0x3174.
  Pole 7°C nie ma jeszcze twardego widget->setter proof.

## Wniosek
Model UI powinien być reprezentowany jako:
`screen/view -> widget object -> view_off -> presenter setter(s) -> UI key -> resolver -> PID`.

Nie wolno używać samej geometrii, bitmap ID ani kolejności widgetu jako dowodu PID.

## OPEN po PASS 112
1. Pełne CFG-aware przypisanie widgetów Home/Kocioł/Bufor do setterów.
2. A69 vs A95 -> konkretny widget/TypedText.
3. Bufor 7°C -> konkretny widget/setter/PID.
4. Pozostałe ekrany wymagają analogicznego połączenia.

## Status
PASS 112 jest etapem statycznego UI-model closure. Nie przejmuje zadań dynamicznych Claude.
