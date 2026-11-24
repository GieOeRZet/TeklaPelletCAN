# AUTONOMOUS PASS 45 — MENU Z PEŁNĄ KONFIGURACJĄ, DIALOG PIN, EKRAN KONFIGURACJA → PID — 2026-11-23

Firmware SHA-256 `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`. Narzędzia: `tools/ui_session.py` (`set_local`, `tap`, `swipe`, `shot`). Obrazy: `data/atlas/`. Adresy: RUNTIME, jeśli nie zaznaczono inaczej.

## Metoda
Stan „jak z pamięci nieulotnej” ustawiany wprost w storage parametrów (`UiSession.set_local`, rekord z tabeli runtime `0x20008D84`): `0x2105=4`, `0x2106=1`, `0x2107=1`, `0x2108=1`.
**Uwaga:** ramki `0x584` wstrzykiwane po CAN są ignorowane, dopóki bramka pollera (`0x2002466C+0x10`) jest zamknięta (PASS 43); ustawienie `0x3500=1` nie otwiera jej. Dlatego konfigurację ustawiono bezpośrednio w pamięci; to stan początkowy, nie zapis użytkownika (omija walidację i publikację).

## HARD (wykonanie, obraz) — widoczność wierszy menu zależna od konfiguracji
Domyślnie (`0x2105=1`, reszta 0): Kocioł, Palnik, Ogrzewanie obwód 1, Historia alarmów, Informacje o programie, Konfiguracja, Poziom menu (PIN) (`menu_top.png`/PASS 44).
Po ustawieniu konfiguracji: **Kocioł, Palnik, Ogrzewanie obwód 1, 2, 3, 4, Ciepła woda użytkowa, Solary, Bufor, Historia alarmów, Informacje o programie, Konfiguracja, Poziom menu (PIN)** (`menu_pelna_konfiguracja_*.png`).
Potwierdza to wizualnie resolwer możliwości (PASS 22/INSTANCE-CAPABILITY): `0x2105` ≥ n daje obwód n (n=1..4); CWU, Solary i Bufor pojawiają się po ustawieniu odpowiednio `0x2106`, `0x2108`, `0x2107`. Kolejność wierszy: CWU, Solary, Bufor.
Na ekranie głównym przybywa kafelków: `Ogrzewanie 2` i kran (CWU) w dolnym pasku (`home_z_konfiguracja.png`).

## HARD — dialog „Wpisz PIN” i poziom dostępu
Ekran „Wpisz PIN”: cztery cyfry z przyciskami +/− i OK (`dialog_pin.png`); cyfry zmieniane stuknięciami (wymagają `hold≥130` ticków, bo kontroler jest odpytywany co ~40 ticków; krótsze stuknięcia giną — przy `hold=60` wpisało się `1001` zamiast `6154`).
Po `6154` + OK: z kafelka palnika na ekranie głównym **znika czerwona kłódka** (przed PIN-em: kłódka) i pojawia się pomarańczowy wykrzyknik (alarm) — czyli poziom dostępu zmienia zachowanie UI (`home_po_pin_6154_z_konfiguracja.png`).
NIEROZSTRZYGNIĘTE: lista wierszy głównego menu **nie wydłuża się** po PIN-ie (nadal 13 wierszy przy pełnej konfiguracji), więc wiersze 15..20 z tablicy menu (klasy 12, 14, 18, 16, 19, 20; bitmapy 73..81 — duże ikony i pasy 440–480 px) nie są dodatkowymi pozycjami tej listy. Możliwe, że należą do osobnego ekranu/widoku (OPEN). Odczyt poziomu dostępu spod `[0x20020784+0x158]` dał 0 mimo zmiany UI — adres modelu/pola do ponownej weryfikacji.

## HARD — ekran „Konfiguracja” (wiązanie ekran → parametr po nazwie i wartości domyślnej z firmware)
| etykieta na ekranie | wartość | PID | dowód |
|---|---|---|---|
| Uśrednianie temp. zewnętrznej [h] | 12 | `0x3720` Outside temp. averaging period [h] (u8 0..48) | nazwa + default 12 |
| Temperatura przełączenia na lato [C] | 18 | `0x372A` Summer time threshold temp. [C] (u8 5..25) | nazwa + default 18 |
| Kalibracja czujnika zew. [°C] | 0.0 | `0x3747` Outside calibration [dC] (s16 −30..30, skala /10) | nazwa + default 0 |
| Rezerwa zbiornika paliwa [kg] | 40 | `0x3603` Fuel reserve [kg] (u16 0..100) | nazwa + default 40 (inny `0x3604` ma default 0) |
| Auto synchronizacja zegara | przełącznik | `0x372F` Is automatic time synchronization (u8 0/1) | nazwa |
Ekran wygląda tak samo z PIN-em i bez (`konfiguracja.png`, `konfiguracja_przewiniete.png`). Dialog „Paliwo” pokazuje `180 kg` = `0x3601` How much fuel left in tank [kg] (default 180); pojemność zbiornika `0x3600` Tank capacity [kg] (default 135).
To zamyka wcześniejsze OPEN „który ekran używa parametru” dla tych 6 PID i dostarcza etykiety PL do karty HA/ESP32.

## Ekran główny z konfiguracją
Pole wartości w prawym górnym oknie zmienia się z `0` na `7` oraz `AUTO` — dane/tryb pochodzą z parametrów (nie badane dalej). Pomarańczowy `!` to wskaźnik alarmu (źródło do ustalenia).

## OPEN
1. Źródło wierszy 15..20 (bitmapy 73..81, klasy 12/14/16/18/19/20) — gdzie są widoczne; czy po PIN-ie `0999`/`6154` pojawiają się w innym ekranie.
2. Dlaczego CAN `0x584` jest ignorowany (bramka pollera); co otwiera ją w normalnej pracy (sprawdzić klasy menu, które zapisują `+0x10`).
3. Co oznacza `!` na ekranie głównym i pole „7 AUTO”; zależność koloru tła (szary/czerwony) od stanu kotła.
4. Eksploracja pozostałych ekranów: Kocioł → ustawienia (zębatka), Palnik → ustawienia, CWU, Solary, Bufor, Informacje o programie, Historia alarmów z danymi.
