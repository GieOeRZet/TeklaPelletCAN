# AUTONOMOUS PASS 113 — A69/A95 + BUFFER 7C BINDING — 2026-11-23

## HARD — Ochrona kotła
Źródło: `data/widgets_invm2_L2_partial.json`.

Ekran: `OGRZEWANIE 1`.
- Label: `this=0x200177ec`, `view_off=6068`, `text_id=30`, tekst „Ochrona kotła”, visible=1.
- Sąsiedni obraz: `this=0x20017820`, `view_off=6120`, bitmap=130, visible=1.
- Poniżej grupa wskaźnika zaczyna się od `view_off=6164`.

Źródło warunku:
- helper PROJECT `0x08054848`;
- inputs: PID `0x22A1` (UI key 0xB0) oraz PID `0x2301` (UI key 0xCD);
- A95 = (0x22A1 != 4);
- A69 = (0x22A1 == 4 && 0x2301 == 1).

### Granica
Mamy twardą lokalizację widgetu, ale nie mamy jeszcze statycznego dowodu, że pole visibility `view_off=6068) lub bitmapa `view_off=6120) jest ustawiana bezpośrednio przez A69 albo A95. Nie promuję tego mapowania.

## HARD — Buffer
Resolver T2:
- UI key 0xF3 -> PID 0x2114 Buffer top set temperature;
- UI key 0xF4 -> PID 0x2115 Buffer bottom set temperature;
- UI key 0xF5 -> PID 0x2280 Buffer top set temperature (osobny parametr).

Parametry:
- 0x2114: min 7, max 80, setting;
- 0x2115: min 7, max 80, setting;
- 0x2280: min 25, max 80, osobny parametr live/read-only w macierzy runtime.

Presenter map:
- 0xF4 -> 0x2115 -> setter 0x08056040;
- 0xF5 -> 0x2280 -> setter 0x08056028;
- brak obecnego wpisu 0xF3 -> 0x2114.

### Wniosek
„7°C” nie może być jeszcze uczciwie przypisane do 0x2114 tylko na podstawie min=7. Dokładny widget/setter binding jest OPEN.

## Następny krok
CFG/XREF:
1. `0x08054848` -> zapis A69/A95 -> konstruktor/visibility widgetu 6068/6120.
2. Brakujący setter UI key 0xF3/PID 0x2114.
3. Po zamknięciu tych dwóch ścieżek rozszerzyć tę samą metodę na pozostałe ekrany.
