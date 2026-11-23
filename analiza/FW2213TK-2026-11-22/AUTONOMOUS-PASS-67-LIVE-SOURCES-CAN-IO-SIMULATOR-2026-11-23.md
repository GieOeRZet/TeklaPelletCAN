# PASS 67 — źródła LIVE: moduły CAN IO, symulator i wiązania live (Claude, emulator, 2026-11-23)

## FACT (zmierzone)
- **Dlaczego wcześniej „nic nie działało”:** odbiornik CAN przyjmuje ramki POJEDYNCZO. Wstrzykiwanie kilku ramek naraz gubiło wszystkie poza ostatnią. Ramki muszą iść z odstępem ~12 tików; wartość kanału jest średnią z 8 próbek (filtr `0x08025328`), więc potrzeba ≥ 8 rund. Punkt kontrolny ekranu głównego musi być zrobiony po ≥ 4000 tików (odbiornik rusza po ~3,3 s).
- **Transport:** PDO1 `0x180+node`, PDO2 `0x280+node`, PDO3 `0x380+node`, PDO4 `0x480+node`; PDO2–4 = 4 × u16 LE = kanały analogowe 0–3, 4–7, 8–11. Kanał n leży w obiekcie modułu pod `+0x1E + 12·n` (u16, średnia), a identyfikator kanału = indeks n. PDO1 bajty 6/7 = wersja oprogramowania modułu.
- **Czujnik** (np. obiekt `0x200103F8` → moduł `0x20023F54`): surowy odczyt 12-bit (ważny 51..4000) → krzywa NTC → PID w dC. Zmierzona krzywa (raw → dC): 500→953, 1000→691, 2000→399, 3000→154, ≥3540 → ujemne (s16); max 1500 (150,0 °C). Błąd odczytu → status 2 → wartość 0 (stąd „czyszczenie” wartości live w PASS 63).
- **Mapowanie kanał → PID przy konfiguracji domyślnej** (pełne dane `data/ui_model/live_sources.json`):
  - moduł 0x56 (CAN IO BIG): kanał 0 → `0x2001` temp. kotła, 3 → `0x215F` zewnętrzna, 4 → `0x2110` CWU zmierzona, 6 → `0x226C` temp. podajnika;
  - moduł 0x45 (CAN IO 5): 0 → `0x3171` (bufor T1), 1 → `0x2112` (góra bufora), 2 → `0x2113` (dół), 4 → `0x3172` (T2), 5 → `0x2109`, 6 → `0x2102`, 7 → `0x2103`, 8 → `0x2104` (solarne 1–4), 9 → `0x3173` (T3); pochodne: `0x3174` energia bufora [%], `0x311C/0x3120` pompa/status solarny.
  - Włączenie modułu 0x56 samo zmienia 14 PID (m.in. `0x2278` pompa CWU, `0x350A`, `0x3607`, rejestr alarmów — znika „Komunikacja z modułem BIG”).
- **Stany pomp i palnika** (`0x2277`, `0x2007`) są WYLICZANE przez logikę sterownika z temperatur, nie są wejściami.
- **Narzędzia:** `tools/live_sim.py` (`LiveSim`: `set(pid, °C)`, `run(ticks)`), `tools/live_diff.py` (wiązania live metodą różnicową), wyniki `data/pass63_pilot_kociol/live_diff_*.json`, `BINDINGS_LIVE_L0.md/.csv`.
- **Wiązania live (zmierzone):** Kocioł `0x2001` → duży tekst (180,65); CWU `0x2110` → tekst (180,50) i (429,195); Solary `0x2109/0x2102/0x2103` → teksty (0,52)/(256,57)/(0,168); Bufor: góra (0,50), dół (0,135), T1 (0,80), T2 (0,120), T3 (0,160) i procent energii (75,118); Home `0x2001` → duży tekst (180,35), `0x215F` → ikona (360,7) bitmapa 181. Pierwszy żywy ekran: Kocioł „64.9” przy zadanych 65,0 °C zmierzonych (zadana kotła = 7, PID `0x2004`).
- Widżet (9,239) (bitmapy 138–142) to animacja pompy zmieniająca klatki sama — wykluczona z wiązań.

## OPEN
- `0x3333` ciśnienie, `0x4000` temp. powrotu, `0x3628` energia, lambda (węzeł 0x50), przepływomierze (0x54/0x55), SLAVE 1–3 kaskady (SDO) — poza zakresem tej mapy; wymagają innych węzłów/PDO.
- Moduły 0x40, 0x46, 0x78, 0x7A–0x7D: przy domyślnej konfiguracji tylko PID „Inside temp [C]” (`0x3627/0x3620/0x3621/0x3640`) — kanały analogowe nieprzypisane.
- Zachowanie logiki sterownika (zadana kotła, stan palnika, pompy) w funkcji temperatur — do zmierzenia (scenariusze).
