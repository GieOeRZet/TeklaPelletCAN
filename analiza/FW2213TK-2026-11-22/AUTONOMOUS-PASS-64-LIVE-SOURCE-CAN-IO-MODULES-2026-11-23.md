# PASS 64 — źródło wartości LIVE: moduły CAN IO (PDO), watchdog, mapowanie kanałów (Claude, emulator)

Kontekst: PASS 63 wykazał, że PID-y live (0x2001, 0x2277, 0x3333, 0x4000, 0x3628) nie są wstrzykiwalne przez 0x584. ChatGPT PASS 95 (statyka): tor SDO do węzłów 5/6/7. Pomiar dynamiczny poniżej koryguje i uzupełnia.

## FACT (emulator, powtarzalne)
1. Węzły 5/6/7 (SDO 0x2001:01 na 0x605..0x607) to **SLAVE 1..3 kaskady** (can_node_names.csv), a nie moduł czujników głównego kotła. Tor SDO dotyczy Kaskady.
2. Wartości live głównego kotła pochodzą z **obiektów modułów CAN IO** w RAM, odbierających **PDO CANopen-podobne**: PDO1=`0x180+node`, PDO2=`0x280+node`, PDO3=`0x380+node`, PDO4=`0x480+node` (RX handler RUNTIME 0x0801E2D2; zapis „watchdoga” 0x0801E322). Zidentyfikowane obiekty (RAM → node, pola `+8/+9`): 0x2000FF08→0x7A, 0x2000FF80→0x7B, 0x2000FFF8→0x7C, 0x20010070→0x7D, 0x20021310→0x40 (CAN IO 0), 0x20021A40→0x45 (CAN IO 5), 0x20021BB0→0x46 (CAN IO 6), 0x20023F54→0x56 i 0x57 (CAN IO BIG), 0x20024170→0x78.
3. **Układ ramki** (z listingu 0x0801E2D2..): PDO2/3/4 = 4×u16 LE (kanały analogowe 0..3, 4..7, 8..11) → sloty obiektu `+0x1C,+0x28,+0x34,+0x40`, `+0x4C..+0x70`, `+0x7C..+0xA0` (stride 0xC). PDO1: bajt0 bit0 → wejście cyfrowe (`+0xF4`); dla node≠0x56 bajt1 = NTC (przeliczenie 0x15E0·x/(0xFF−x)); bajty 6/7 → `+0xE`/`+0xF`.
4. **Watchdog:** licznik `[obj+0x168]` (u16) liczy do 300 cyklicznie (funkcja 0x0801E878, co ~500 tików); `[obj+0xA]=1` = moduł offline, wtedy slot 2 źródła (0x0801E4CC) zwraca „brak kanału”, a EstymaTask (0x08068FE4) zeruje wartość PID (źródło statusu 3). Odebranie dowolnej z ramek PDO tego węzła zeruje licznik. Skan identyfikatorów 0x100..0x7FF: zerują go 0x1D6, 0x1D7, 0x2D6, 0x2D9, 0x3D6, 0x4D6 dla obiektu CAN IO BIG.
5. **Mapowanie kanał → PID przy konfiguracji domyślnej** (jedna wartość 1000, potem jeden kanał 2000; pełne dane `data/pass64_live/modmap_default_config.json`): tylko node 0x45 kanał 8 → PID 0x2104 i kanał 9 → PID 0x3173 (691→399). Pozostałe 9 obiektów × 12 kanałów nie zmienia żadnego PID.

## OPEN
- Kanały pozostałych modułów (w tym 0x56 z 0x2001) nie dotarły do PID przy wartości 1000/2000 i domyślnej konfiguracji: prawdopodobnie przypisanie wejść zależy od konfiguracji/typu czujnika (`[r5+6]` w 0x0801EBC4 wybiera konwersję: 0 = bezpośrednio, 1 = −0xD05, 2 = ze znakiem …) lub od flag PDO1/statusu `[obj+0x1E]`. Następny krok: zrzut tabeli kanałów obiektów (pola `+0x28`, stride 0x24, 19 wpisów) i obiektów czujników (`[obj+0x18]`=moduł, `[obj+0x1C]`=kanał, `[obj+0x20]`→bramka), np. dla czujnika 0x200103F8.
- Czy to jest ten sam mechanizm, który zasila temperaturę kotła 0x2001 (obiekt czujnika 0x200103F8, źródło `[obj+0x18]`).

## Wniosek dla UI-MODEL
Wiązania live da się mierzyć PO dostarczeniu ramek PDO modułów (symulator modułu = wysyłanie 0x180/0x280/0x380/0x480+node w pętli co <300 cykli). Nie przez 0x584.
