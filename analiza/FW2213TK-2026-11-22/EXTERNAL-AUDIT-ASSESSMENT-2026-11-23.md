# OCENA AUDYTU ODKRYWCZEGO (zewnętrzny agent) WZGLĘDEM STANU WIEDZY — 2026-11-23

Dokument oceniany: `EXTERNAL-AUDIT-DISCOVERY-FW2213TK-2026-11-23.md` (wnioski dostarczone przez właściciela projektu). Weryfikacja na danych z emulacji (`data/runtime_param_table_655.csv`, `data/panel_lists_by_level.md`, `data/ram_clusters.csv`).

## Zgodność z głównym wnioskiem
Zgoda: reverse engineering nie jest kompletny (szacunek własny ~70%, ESP32/HA 0%). Audyt trafnie wskazuje kierunki, ale część „drugiej warstwy” **istnieje już w tabeli 655 rekordów jako zwykłe PID-y**; otwarta jest **logika wokół nich**, nie ich istnienie.

## Punkt po punkcie
| # | Twierdzenie audytu | Weryfikacja | Status |
|---|---|---|---|
| 1 | Pamięć alarmów (`Alarm date timestamp`, `Alarm register`, `Alarm confirm timestamp`, `Alarm next index`, `Number of alarms`, `Request reset alarm memory`) | HARD: **66 rekordów z „Alarm”** w tabeli: `0x4010..` Alarm register (klasa 3), `0x4024..` Alarm date timestamp i `0x4038..` Alarm confirm timestamp (klasa 2 = lustro z centrali, ~20+20 wpisów), `0x404C` next index, `0x404D` number of alarms, **`0x404E` Request reset alarm memory (klasa 1 = komenda)**, `0x3728` Is reset required. Komenda resetu jest **widoczna w ekranie Konfiguracja od poziomu 2** (PASS 46). Ekran „Historia alarmów” istnieje (pusty bez danych) | **Zgoda co do priorytetu**; „poza macierzą PID” — nie, ale mechanizm (zapis wpisów, potwierdzanie, kolejność, wskaźnik „!” na ekranie głównym) nie jest zbadany; wymaga modelu RTC (znaczniki czasu) |
| 2 | `Default settings request` | HARD: PID `0x0005` (u8 0..1, default 1, klasa 3), storage `0x20021FA7` (+0x16BB) leży w tym samym klastrze co `Boiler image selector 0x370A`, `Is reset required 0x3728`, `Autoconfig activation 0x3501`. **Nie występuje na żadnej liście ekranu USTAWIEŃ** (sprawdzone dla klas 0..0x11 × poziomy 0..3) | **Zgoda — prawdziwa luka**: nie wiadomo, gdzie i jak jest wywoływane (CAN/serwis/ukryty dialog?) |
| 3 | Konfiguracja modułów (`Main module type`, `CH expansion module type`, `Profile number`, wersje Vide room, `boiler short name`) | HARD: `0x3500`, `0x3502` edytowalne w **Konfiguracji od poziomu 1**; `0x350B Profile number` (u8 1..3, default 2, klasa 3, +0x16CC); wersje `0x365C..0x3663` (Vide room 1..4 przed/po kropce, klasa 0 = live), `0x3665 igneTouch boiler short name`. Panel cyklicznie odpytuje **węzły 5, 6, 7** (`0x605..0x607`, obiekt `0x2001`) — **hipoteza (INFERENCE): to Vide Room 2..4** | **Częściowo zamknięte** po stronie UI; otwarte: co zmienia Profile number (1..3) i jak wersje trafiają do ekranu „Informacje o programie” |
| 4 | Niezamknięta mapa peryferiów (`0x40000000..0x40002800`) | HARD (wykonanie): to **TIM2..TIM7 i RTC (`0x40002800`)**; timery pełnią rolę podstawy opóźnień, **RTC nie jest zamodelowany** (stąd czas `0:00`, a znaczniki alarmów zależą od czasu). Zamodelowane i potwierdzone: LTDC, DMA2D, CAN2, I2C1 (FT5x06 dotyk + zapis na `0x38`), SysTick | **Zgoda (RTC realna luka)**; reszta to infrastruktura |
| 5 | Klastry RAM poza modelem PID (`0x200247C8` 60 ref., `0x20021FA0` 39, `0x200243E4` 22, …) | Własny skan (`tools/ram_clusters.py`, literały wyrównane): 1169 adresów SRAM z literałami; **1071 „other”**, 29 = storage parametrów, 6 = znane obiekty, **63 = „config-gap”** (wewnątrz bloku ustawień, poza storage'em jakiegokolwiek rekordu). `0x200247C8..0x20024818` leży obok **struktury dotyku `0x200247E4` (HARD: cache sampleTouch)** → najpewniej stan HAL/GUI, nie PID. **`0x20021FA0` (39 literałów, +0x16B4) i `0x200243E4` (19) to nierejestrowane pola w bloku ustawień** | **Zgoda w części**: dwa realne tropy (config-gap `0x20021FA0`, `0x200243E4`); reszta to infrastruktura sterowników/RTOS/UI |
| — | „260 parametrów = konfiguracja” zbyt wąskie | Zgoda; od PASS 35 pracujemy na **655 rekordach runtime** (448 w katalogu panelu); 260 slotów z wcześniejszych passów nie jest katalogiem PID | Już uwzględnione |

## Przyjęta kolejność (decyzja głównego programisty)
1. **Inwentarz tego, co firmware ma, a nie było wykonane/widziane:** pokrycie wykonania funkcji (z 2810 celów BL) i pokrycie zasobów (bitmapy/teksty/PID) w eksploracji UI — dowód zamiast domysłów.
2. **Klaster ustawień `0x20021FA0` i `0x200243E4`** (kto czyta/zapisuje, jakie pola).
3. **Alarmy end-to-end** (RTC, zapis wpisów, potwierdzanie, ekran, wskaźnik „!”, komenda resetu `0x404E`).
4. **Default settings / reset / autoconfig** (`0x0005`, `0x3728`, `0x3501`).
5. **Profil i moduły** (`0x350B`, `0x3500`, `0x3502`; węzły 5–7 ↔ Vide Room).
6. Dalsze CAN „PDO-podobne” i peryferia.
