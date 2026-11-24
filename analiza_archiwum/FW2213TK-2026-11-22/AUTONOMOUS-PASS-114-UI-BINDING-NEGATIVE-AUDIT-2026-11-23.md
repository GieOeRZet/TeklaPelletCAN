# AUTONOMOUS PASS 114 — UI BINDING NEGATIVE AUDIT — 2026-11-23

## Cel
Wykonać konserwatywny audyt par UI-key/PID w istniejącym `presenter_map.csv`, aby nie mylić braku wpisu z dowodem nieistnienia parametru.

## HARD — wynik
Źródło: `data/presenter_map.csv`.

| UI key | PID | wynik |
|---|---|---|
| 0x00F3 | 0x2114 | **BRAK pary w presenter_map** |
| 0x00F4 | 0x2115 | para obecna; setter 0x08056040 |
| 0x00F5 | 0x2280 | para obecna; setter 0x08056028 |
| 0x00B0 | 0x22A1 | para obecna |
| 0x00CD | 0x2301 | para obecna; setter 0x08054848 |

### Znaczenie
Brak `0x00F3 -> 0x2114` w presenter_map nie oznacza, że firmware nie używa tego parametru. Oznacza wyłącznie, że obecny statyczny skaner prezenterów nie wyeksportował tego callsite jako mapowania.

## Ochrona kotła
Dla 0x00B0/0x22A1 i 0x00CD/0x2301 istnieje źródłowe powiązanie z helperem 0x08054848. Nadal OPEN pozostaje przejście od jego flag A69/A95 do konkretnego widgetu `view_off=6068/6120`.

## Bufor
T2 zamyka 0xF3->0x2114, ale obecny presenter map nie zamyka widget->setter dla tego key. To wzmacnia status OPEN pola 7°C zamiast go zgadywać.

## Narzędzia
- `tools/cg_ui_binding_negative_audit.py`
- `tools/test_cg_ui_binding_negative_audit.py`
- `data/cg_ui_binding_negative_audit.csv`

## Następny krok
Nie rozwijać statycznego view_off jako samodzielnego dowodu. Przejść do CFG/XREF setterów i źródłowych callsite'ów albo wykorzystać dynamiczny PID-diff Claude'a, jeśli dostępny.
