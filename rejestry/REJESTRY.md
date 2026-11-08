# Rejestry kotła i firmware panela – pełna dokumentacja

Plik **generowany** (`tools/gen_rejestry_md.py`) z `katalog-rejestrow.csv`, `panel-fw-parametry-FW2213TK.csv` i `panel-fw-mapa-indeks-id.csv`. Nie edytuj ręcznie – popraw CSV i uruchom skrypty (sekcja 7). Stan: 2026-11-08, firmware PelletCAN 1.4.23.

## 1. Liczby

| Co | Ile |
|---|---|
| Parametry zarejestrowane w kodzie firmware panela FW2213TK (funkcja `0x0802143C`, ID parametru = indeks SDO) | **448** |
| …z tego wykorzystane w naszym firmware ESPHome | 179 |
| …z tego jeszcze niewykorzystane | 269 |
| Pary (indeks CANopen, ID panela) w tablicy @0x37576 | 420 wierszy, 419 unikalnych indeksów (odpowiada na kotle: 299, nie: 120) |
| Rejestry węzła 4 (kocioł) w katalogu | 669 (w tym 593 odpowiada na skan, reszta to parametry znane tylko z firmware panela) |
| Rejestry węzła 4 wykorzystane w naszym firmware (łącznie z niepanelowymi, np. alarmy 0x4010+) | 243 |
| Wiersze węzła 86 (CAN IO BIG) | 18 |

Rodzaje parametrów panela: u8: 234, u16: 112, s16: 45, u32: 56, s32: 1. Dostęp wg panela: 0 = odczyt na żywo, 1 = komenda, 2/3 = nastawa (3 – edytowalna z menu).

## 2. Jak czytać wartości

- Węzeł 4 = sterownik kotła, CANopen SDO, 125 kbit/s, **sub 1** (sub 0/2 nic nie zwracają). Węzeł 86 = CAN IO BIG. ESP = węzeł 90.
- **flaga + bajt:** wiele parametrów jest zwracanych jako `256 + wartość` (np. surowe 276 = 20). W tabelach „kodowanie” opisuje przeliczenie.
- **Temperatury** to zwykle `raw / 10 °C`; niektóre nastawy są w °C bez dzielenia.
- **Poziom menu (PIN):** 0 = bez PIN-u, klucz 1 = PIN instalatora 0900, klucz 2 = PIN 0999 (wymagany m.in. do Testu wyjść).
- **Status:** POTWIERDZONY = znaczenie sprawdzone na kotle; ODNALEZIONY – … = nazwa z firmware panela lub skan, nieprzetestowane; NIEZNANY = brak nazwy.

## 3. Rejestry wykorzystywane w firmware / karcie (243)

Opis każdego: co to jest, kodowanie, dostęp i **gdzie w firmware** (akcja `set_param` N, encja, ekran karty). Kolumna „Nazwa panela” to oryginalna angielska nazwa z firmware panela.

### Ustawienia podstawowe kotła / CO / CWU / tryby

| Rejestr | Nazwa | Nazwa panela | Typ | Zakres | Kodowanie / jednostka | Dostęp | PIN | Gdzie w firmware / karcie | Uwagi |
|---|---|---|---|---|---|---|---|---|---|
| `0x2001` | Temperatura kotła | Boiler temp[dC] | U16 | 0…1500 | raw/10 °C | R |  | odczyt fw v2.15: boiler_temp; karta: boiler_temp | Pomiar; zakres 0–150 °C |
| `0x2002` | Tryb zadawania temperatury kotła | Boiler program | U16 | 0…3 | 0 czasowy auto, 1 czasowy ręczny, 2 auto, 3 ręczny | R/W (przetestowane) |  | zapis: set_boiler_mode, odczyt fw: set_boiler_mode; karta: okno trybu kotła | Zapis działał (mirror go blokuje) |
| `0x2003` | Temperatura zadana kotła (ręczna) | Boiler set manual temp[C] | U16 | 60…80 | °C (bez dzielenia), 60–80 | R/W (przetestowane) |  | zapis: set_setpoint, odczyt fw: set_setpoint which=4; karta: okno kotła | Zapis działał |
| `0x2004` | Temperatura zadana kotła (wynikowa) | Boiler set result temp[C] | U16 | 60…150 | °C (bez dzielenia), 60–150 | R/W (zapis w firmware, nietestowany osobno) |  | odczyt fw: boiler_set_result | Odczyt |
| `0x2005` | Włącz / wyłącz kocioł | Boiler on/off | U16 | 256…257 | młodszy bajt 0/1; 256+n (flaga) | R/W (przetestowane) |  | zapis: power_switch, odczyt fw: power_switch; karta: przełącznik w oknie szybkich ustawień | Typ U16; zapis działał |
| `0x2006` | Wejście: zakaz rozpalenia (IN16) | Burner external permission | U16 | 256…257 | 257 = brak zakazu, 256 = zakaz | R |  | odczyt fw: in_zakaz | Test zworką; tylko odczyt |
| `0x2007` | Stan palnika | Burner state | U16 | 256…356 | młodszy bajt: 0 wył., 1 rozpalanie, 2 żarzenie, 5 modulacja, 6 wygaszanie, 7 czyszczenie, 8 pauza, 9 stop, 10 alarm | R |  | odczyt fw: burner_state_code/text; karta: nagłówek, diody | Odczyt |
| `0x2010` | CWU – temperatura komfort (zadana) | Hot water 1 comfort temperature | U16 | 20…70 | °C, 20–70 | R/W (przetestowane) |  | zapis: set_setpoint, odczyt fw: set_setpoint which=0; karta: okno CWU | Zapis działał |
| `0x2012` | CWU – temperatura eko (zadana) | Hot water 1 economical temperature | U16 | 20…70 | °C, 20–70 | R/W (przetestowane) |  | zapis: set_setpoint, odczyt fw: set_setpoint which=1 | Zapis działał |
| `0x2014` | Tryb CWU | Hot water 1 program | U16 | 256…259 | 256 Off, 257 Eko, 258 Harmonogram, 259 Komfort (młodszy bajt 0–3) | R/W (przetestowane) |  | zapis: tryb CWU, odczyt fw: cwu_mode | Zapis działał |
| `0x201A` | CWU – temperatura zadana (wynikowa) | Hot water 1 result temperature | U16 | 0…500 | °C (bez dzielenia), 0–500 raw | R/W (zapis w firmware, nietestowany osobno) |  | odczyt fw: hw_set_result | Odczyt |
| `0x201C` | Hot water 1 temperature max (FW panela) | Hot water 1 temperature max | U16 | …336 |  | R (zapis nieprzetestowany) |  | zapis: set_param 66, odczyt | (auto) flaga+bajt: wartość 60 (raw 316); zakres ?..336; sąsiedztwo: po: CWU – temperatura zadana (wynikowa) (0x201A) / FW panela: Hot water 1 temperature max; typ u8, zakres 40…80, domyslna 70, dostep: nastawa |
| `0x2032` | CO – temperatura komfort (zadana) | CH comf temp set [dC] | U16 | 150…300 | raw/10 °C, 15–30 °C | R/W (przetestowane) |  | zapis: set_setpoint, odczyt fw: set_setpoint which=2; karta: okno CO | Zapis działał |
| `0x2048` | CO – temperatura eko (zadana) | CH eco temp set [dC] | U16 | 100…300 | raw/10 °C, 10–30 °C | R/W (przetestowane) |  | zapis: set_setpoint, odczyt fw: set_setpoint which=3 | Zapis działał |
| `0x2064` | Tryb CO 1 | CH program | U16 | 256…259 | 256 Off, 257 Eko, 258 Harmonogram, 259 Komfort | R/W (przetestowane) |  | zapis: tryb CO, odczyt fw: co_mode | Zapis działał |
| `0x2065` | Tryb CO 2 | - | U16 | 256…259 | jak 0x2064 | R (zapis nieprzetestowany) |  | odczyt fw: czytany tylko przy dwa_obiegi_co | Niezweryfikowany (brak drugiego obiegu CO) / w firmware wyłączone (dwa_obiegi_co: false) |

### Harmonogram CO i sloty

| Rejestr | Nazwa | Nazwa panela | Typ | Zakres | Kodowanie / jednostka | Dostęp | PIN | Gdzie w firmware / karcie | Uwagi |
|---|---|---|---|---|---|---|---|---|---|
| `0x2106` | Hot water configuration (FW panela) | Hot water configuration | U16 | 256…257 | flaga 0x01 + bajt: raw − 256 (zakres wartości 0…1; jeśli x10: 0…0.1) | R (zapis nieprzetestowany) |  | odczyt | (auto) flaga 0/1 (raw 257=1); zakres 256..257 / FW panela: Hot water configuration; typ u8, zakres 0…1, domyslna 0, dostep: nastawa |
| `0x2107` | Buffer configuration (FW panela) | Buffer configuration | U16 | 256…257 | flaga 0x01 + bajt: raw − 256 (zakres wartości 0…1; jeśli x10: 0…0.1) | R (zapis nieprzetestowany) |  | odczyt | (auto) flaga 0/1 (raw 256=0); zakres 256..257 / FW panela: Buffer configuration; typ u8, zakres 0…1, domyslna 0, dostep: nastawa |
| `0x2108` | Solar configuration (FW panela) | Solar configuration | U16 | 256…257 | flaga 0x01 + bajt: raw − 256 (zakres wartości 0…1; jeśli x10: 0…0.1) | R (zapis nieprzetestowany) |  | odczyt | (auto) flaga 0/1 (raw 256=0); zakres 256..257 / FW panela: Solar configuration; typ u8, zakres 0…1, domyslna 0, dostep: nastawa |
| `0x2110` | CWU – temperatura (pomiar) | Hot water 1 measured temperature | U16 | -100…1500 | raw/10 °C | R |  | odczyt fw: hw_temp | Odczyt |
| `0x2123` | Lambda module presence (FW panela) | Lambda module presence | U16 | 256…257 | flaga 0x01 + bajt: raw − 256 (zakres wartości 0…1; jeśli x10: 0…0.1) | R (zapis nieprzetestowany) |  | odczyt | (auto) flaga 0/1 (raw 256=0); zakres 256..257; sąsiedztwo: przed: Harmonogram CO 1 – poniedziałek (maska 24 bit) (0x2126) / FW panela: Lambda module presence; typ u8, zakres 0…1, domyslna 0, dostep: nastawa |
| `0x2126` | Harmonogram CO 1 – poniedziałek (maska 24 bit) | CH schedule monday | U16 | 0…16777215 | bit i = godzina i, 1 = komfort | R/W (zapis w firmware: action set_schedule; skuteczność zapisu na kotle niepotwierdzona w dokumentach) |  | zapis: set_schedule CO fw: sch_co; karta: ekran PROGRAM (CO). Dalej: +4 na dzień (0x212A, 0x212E, 0x2132, 0x2136, 0x213A, 0x213E) | Wartość 0x0781FC = godz. 2–9 i 15–19 (zgodne ze zdjęciem panelu OGRZEWANIE 1 → PROGRAM). Odczyt i zapis działały |
| `0x212A` | Harmonogram CO 1 – wtorek (maska 24 bit) | CH schedule tuesday | U16 | 0…16777215 | bit i = godzina i, 1 = komfort | R/W (zapis w firmware: action set_schedule; skuteczność zapisu na kotle niepotwierdzona w dokumentach) |  | zapis: set_schedule CO fw: sch_co | Wartość 0x0781FC = godz. 2–9 i 15–19 (zgodne ze zdjęciem panelu OGRZEWANIE 1 → PROGRAM). Odczyt i zapis działały |
| `0x212E` | Harmonogram CO 1 – środa (maska 24 bit) | CH schedule wednesday | U16 | 0…16777215 | bit i = godzina i, 1 = komfort | R/W (zapis w firmware: action set_schedule; skuteczność zapisu na kotle niepotwierdzona w dokumentach) |  | zapis: set_schedule CO fw: sch_co | Wartość 0x0781FC = godz. 2–9 i 15–19 (zgodne ze zdjęciem panelu OGRZEWANIE 1 → PROGRAM). Odczyt i zapis działały |
| `0x2132` | Harmonogram CO 1 – czwartek (maska 24 bit) | CH schedule thursday | U16 | 0…16777215 | bit i = godzina i, 1 = komfort | R/W (zapis w firmware: action set_schedule; skuteczność zapisu na kotle niepotwierdzona w dokumentach) |  | zapis: set_schedule CO fw: sch_co | Wartość 0x0781FC = godz. 2–9 i 15–19 (zgodne ze zdjęciem panelu OGRZEWANIE 1 → PROGRAM). Odczyt i zapis działały |
| `0x2136` | Harmonogram CO 1 – piątek (maska 24 bit) | CH schedule friday | U16 | 0…16777215 | bit i = godzina i, 1 = komfort | R/W (zapis w firmware: action set_schedule; skuteczność zapisu na kotle niepotwierdzona w dokumentach) |  | zapis: set_schedule CO fw: sch_co | Wartość 0x0781FC = godz. 2–9 i 15–19 (zgodne ze zdjęciem panelu OGRZEWANIE 1 → PROGRAM). Odczyt i zapis działały |
| `0x213A` | Harmonogram CO 1 – sobota (maska 24 bit) | CH schedule saturday | U16 | 0…16777215 | bit i = godzina i, 1 = komfort | R/W (zapis w firmware: action set_schedule; skuteczność zapisu na kotle niepotwierdzona w dokumentach) |  | zapis: set_schedule CO fw: sch_co | Wartość 0x0781FC = godz. 2–9 i 15–19 (zgodne ze zdjęciem panelu OGRZEWANIE 1 → PROGRAM). Odczyt i zapis działały |
| `0x213E` | Harmonogram CO 1 – niedziela (maska 24 bit) | CH schedule sunday | U16 | 0…16777215 | bit i = godzina i, 1 = komfort | R/W (zapis w firmware: action set_schedule; skuteczność zapisu na kotle niepotwierdzona w dokumentach) |  | zapis: set_schedule CO fw: sch_co | Wartość 0x0781FC = godz. 2–9 i 15–19 (zgodne ze zdjęciem panelu OGRZEWANIE 1 → PROGRAM). Odczyt i zapis działały |

### Ustawienia CO/CWU, harmonogram CWU

| Rejestr | Nazwa | Nazwa panela | Typ | Zakres | Kodowanie / jednostka | Dostęp | PIN | Gdzie w firmware / karcie | Uwagi |
|---|---|---|---|---|---|---|---|---|---|
| `0x2142` | CO 1 – tryb pracy (ręczny/pogodowy) | CH mode | U16 | 256…257 | 256 = ręczny, 257 = pogodowy (górne bajty ramki bywają śmieciami) | R (zapis nieprzetestowany) |  | zapis: set_param 14, odczyt fw v2.18: ch1_mode | Potwierdzone zmianami na panelu; zapis set_param key 14 |
| `0x2146` | CO 1 – temperatura zadana ręczna [°C] | Tch set manual [C] | U16 | 276…336 | flaga + bajt: raw − 256 = °C (20..80) – NIE raw/10 | R/W (zapis w firmware, nietestowany osobno) |  | zapis: set_param 15, odczyt fw v2.18: ch1_set_manual | POPRAWKA w v2.18 (wcześniej raw/10); zapis set_param key 15 |
| `0x2147` | CO 2 – temperatura zadana (ręczna) | - | U16 | 276…336 | raw/10 °C | R/W (zapis w firmware, nietestowany osobno) |  | odczyt fw: ch2_set_manual | Brak drugiego obiegu / w firmware wyłączone (dwa_obiegi_co: false) |
| `0x214E` | Tlen dla mocy 30 % [%] | Oxygen for 30% of power [%] | U16 | 306…406 | raw/10 (zakres 306–406 = 5,0–15,0); 376 = 12,0 | R (zapis nieprzetestowany) | klucz 1 | zapis: set_param 32, odczyt fw v2.20 (menu palnika) | (auto) flaga+bajt: wartość 120 (raw 376); zakres 306..406 zmiana 12,0→12,2 (376→378), 19.10 23:00; poziom menu: klucz 1 (PIN 0900) |
| `0x2152` | Tlen dla mocy 100 % [%] | Oxygen for 100% of power [%] | U16 | 306…406 | raw/10 (306–406 = 5,0–15,0); 336 = 8,0 | R (zapis nieprzetestowany) | klucz 1 | zapis: set_param 33, odczyt fw v2.20 (menu palnika) | (auto) flaga+bajt: wartość 80 (raw 336); zakres 306..406; sąsiedztwo: przed: Harmonogram CWU – poniedziałek (maska 24 bit) (0x2154) zmiana 8,0→8,2 (336→338); poziom menu: klucz 1 (PIN 0900) |
| `0x2153` | Bezwładność palnika [min] | Burner inertia [min] | U16 | 257…316 | flaga+bajt: raw−256 (257–316) | R (zapis nieprzetestowany) | klucz 2 | zapis: set_param 39, odczyt fw v2.20 (menu palnika) | (auto) flaga+bajt: wartość 5 (raw 261); zakres 257..316; sąsiedztwo: przed: Harmonogram CWU – poniedziałek (maska 24 bit) (0x2154) zmiana 5→7 (261→263); poziom menu: klucz 2 (PIN 0999) |
| `0x2154` | Harmonogram CWU – poniedziałek (maska 24 bit) | Hot water 1 schedule monday | U16 | 0…16777215 | bit i = godzina i, 1 = komfort | R/W (zapis w firmware: action set_schedule; skuteczność zapisu na kotle niepotwierdzona w dokumentach) |  | zapis: set_schedule CWU fw: sch_cwu | Odczyt i zapis działały |
| `0x2155` | Harmonogram CWU – wtorek (maska 24 bit) | Hot water 1 schedule tuesday | U16 | 0…16777215 | bit i = godzina i, 1 = komfort | R/W (zapis w firmware: action set_schedule; skuteczność zapisu na kotle niepotwierdzona w dokumentach) |  | zapis: set_schedule CWU fw: sch_cwu | Odczyt i zapis działały |
| `0x2156` | Harmonogram CWU – środa (maska 24 bit) | Hot water 1 schedule wednesday | U16 | 0…16777215 | bit i = godzina i, 1 = komfort | R/W (zapis w firmware: action set_schedule; skuteczność zapisu na kotle niepotwierdzona w dokumentach) |  | zapis: set_schedule CWU fw: sch_cwu | Odczyt i zapis działały |
| `0x2157` | Harmonogram CWU – czwartek (maska 24 bit) | Hot water 1 schedule thursday | U16 | 0…16777215 | bit i = godzina i, 1 = komfort | R/W (zapis w firmware: action set_schedule; skuteczność zapisu na kotle niepotwierdzona w dokumentach) |  | zapis: set_schedule CWU fw: sch_cwu | Odczyt i zapis działały |
| `0x2158` | Harmonogram CWU – piątek (maska 24 bit) | Hot water 1 schedule friday | U16 | 0…16777215 | bit i = godzina i, 1 = komfort | R/W (zapis w firmware: action set_schedule; skuteczność zapisu na kotle niepotwierdzona w dokumentach) |  | zapis: set_schedule CWU fw: sch_cwu | Odczyt i zapis działały |
| `0x2159` | Harmonogram CWU – sobota (maska 24 bit) | Hot water 1 schedule saturday | U16 | 0…16777215 | bit i = godzina i, 1 = komfort | R/W (zapis w firmware: action set_schedule; skuteczność zapisu na kotle niepotwierdzona w dokumentach) |  | zapis: set_schedule CWU fw: sch_cwu | Odczyt i zapis działały |
| `0x215F` | Temperatura zewnętrzna | Outside temperature | U16 | -500…1000 | raw/10 °C | R |  | odczyt fw: outside_temp | Odczyt |
| `0x216C` | Kociol – minimalna temperatura powrotu [°C] | Boiler minimal return temperature | U16 | 35…75 | liczba całkowita °C (bez flagi) | R/W (potwierdzone zmiana na panelu i zapisem z ESP) | klucz 1 | zapis: set_param 49, odczyt | Menu → Kocioł → NASTAWY Zmiana na panelu + skan 22.10; set_param 49 |
| `0x216D` | Mieszacz powrotu – tryb testowy (A/CLOSE/OPEN) | Boiler return mixer test | U16 | 256…258 | 256 = A (automat), 257 = OFF/CLOSE, 258 = ON/OPEN (+flaga 0x0100) | R/W (potwierdzone zapisem) |  | odczyt | Polecenie trybu testowego wyjścia (Menu → Test wyjść, wymaga PIN poziom 2). Zapis zmienia tryb, stan fizyczny wyjścia zależy od sterownika. Potwierdzone 21.10. OPEN → 258. Po próbie zawsze wracać na A (256). fw: akcja set_output |
| `0x216E` | Kociol – czas mieszacza [s] | Boiler mixer opening time [s] | U16 | 60…360 | liczba s (bez flagi) | R/W (potwierdzone zmiana na panelu i zapisem z ESP) | klucz 1 | zapis: set_param 50, odczyt | Menu → Kocioł → NASTAWY Zmiana na panelu + skan 22.10; set_param 50 |

### Inne

| Rejestr | Nazwa | Nazwa panela | Typ | Zakres | Kodowanie / jednostka | Dostęp | PIN | Gdzie w firmware / karcie | Uwagi |
|---|---|---|---|---|---|---|---|---|---|
| `0x215A` | Airflow speed for 30% of power [m/s] (FW panela) | Airflow speed for 30% of power [m/s] | U16 |  |  |  |  | zapis: set_schedule CWU | FW panela: Airflow speed for 30% of power [m/s]; typ u16, zakres 5…500, domyslna 50, dostep: nastawa; na kotle: nie odpowiada (inna konfiguracja?) |

### Zakresy, harmonogram kotła

| Rejestr | Nazwa | Nazwa panela | Typ | Zakres | Kodowanie / jednostka | Dostęp | PIN | Gdzie w firmware / karcie | Uwagi |
|---|---|---|---|---|---|---|---|---|---|
| `0x2207` | Kociol – minimalna temperatura pomp [°C] | Boiler minimal pump temperature | U16 | 20…70 | liczba całkowita °C (bez flagi) | R/W (potwierdzone zmiana na panelu i zapisem z ESP) | klucz 1 | zapis: set_param 48, odczyt | Menu → Kocioł → NASTAWY Zmiana na panelu + skan 22.10; zapis z ESP (set_param 48) |
| `0x2208` | Histereza załączenia kotła [°C] | Boiler on histeresis | U16 | 0…20 | °C, liczba całkowita 0..20 | R (zapis nieprzetestowany) |  | zapis: set_param 10, odczyt fw v2.17 | Potwierdzone zmianą na panelu 15 → 16; zapis set_param key 10 |
| `0x2209` | Harmonogram kotła – poniedziałek (maska 24 bit) | Boiler schedule monday | U16 | 0…16777215 | bit i = godzina i, 1 = komfort | R/W (zapis w firmware: action set_schedule; skuteczność zapisu na kotle niepotwierdzona w dokumentach) |  | zapis: set_schedule kociol fw: sch_boil; karta: ekran PROGRAM (kocioł) | OTWARTE (2026-10-19): skan = 0x1FFFE0 (godz. 5–21, zgodne z panelem), ale odczyt dziś = FFFFFF (cały dzień). Do wyjaśnienia surowymi bajtami (fw v2.19). Odczyt i zapis działały |
| `0x220A` | Harmonogram kotła – wtorek (maska 24 bit) | Boiler schedule tuesday | U16 | 0…16777215 | bit i = godzina i, 1 = komfort | R/W (zapis w firmware: action set_schedule; skuteczność zapisu na kotle niepotwierdzona w dokumentach) |  | zapis: set_schedule kociol fw: sch_boil; karta: ekran PROGRAM (kocioł) | OTWARTE (2026-10-19): skan = 0x1FFFE0 (godz. 5–21, zgodne z panelem), ale odczyt dziś = FFFFFF (cały dzień). Do wyjaśnienia surowymi bajtami (fw v2.19). Odczyt i zapis działały |
| `0x220B` | Harmonogram kotła – środa (maska 24 bit) | Boiler schedule wednesday | U16 | 0…16777215 | bit i = godzina i, 1 = komfort | R/W (zapis w firmware: action set_schedule; skuteczność zapisu na kotle niepotwierdzona w dokumentach) |  | zapis: set_schedule kociol fw: sch_boil; karta: ekran PROGRAM (kocioł) | OTWARTE (2026-10-19): skan = 0x1FFFE0 (godz. 5–21, zgodne z panelem), ale odczyt dziś = FFFFFF (cały dzień). Do wyjaśnienia surowymi bajtami (fw v2.19). Odczyt i zapis działały |
| `0x220C` | Harmonogram kotła – czwartek (maska 24 bit) | Boiler schedule thursday | U16 | 0…16777215 | bit i = godzina i, 1 = komfort | R/W (zapis w firmware: action set_schedule; skuteczność zapisu na kotle niepotwierdzona w dokumentach) |  | zapis: set_schedule kociol fw: sch_boil; karta: ekran PROGRAM (kocioł) | OTWARTE (2026-10-19): skan = 0x1FFFE0 (godz. 5–21, zgodne z panelem), ale odczyt dziś = FFFFFF (cały dzień). Do wyjaśnienia surowymi bajtami (fw v2.19). Odczyt i zapis działały |
| `0x220D` | Harmonogram kotła – piątek (maska 24 bit) | Boiler schedule friday | U16 | 0…16777215 | bit i = godzina i, 1 = komfort | R/W (zapis w firmware: action set_schedule; skuteczność zapisu na kotle niepotwierdzona w dokumentach) |  | zapis: set_schedule kociol fw: sch_boil; karta: ekran PROGRAM (kocioł) | OTWARTE (2026-10-19): skan = 0x1FFFE0 (godz. 5–21, zgodne z panelem), ale odczyt dziś = FFFFFF (cały dzień). Do wyjaśnienia surowymi bajtami (fw v2.19). Odczyt i zapis działały |
| `0x220E` | Harmonogram kotła – sobota (maska 24 bit) | Boiler schedule saturday | U16 | 0…16777215 | bit i = godzina i, 1 = komfort | R/W (zapis w firmware: action set_schedule; skuteczność zapisu na kotle niepotwierdzona w dokumentach) |  | zapis: set_schedule kociol fw: sch_boil; karta: ekran PROGRAM (kocioł) | OTWARTE (2026-10-19): skan = 0x1FFFE0 (godz. 5–21, zgodne z panelem), ale odczyt dziś = FFFFFF (cały dzień). Do wyjaśnienia surowymi bajtami (fw v2.19). Odczyt i zapis działały |
| `0x220F` | Harmonogram kotła – niedziela (maska 24 bit) | Boiler schedule sunday | U16 | 0…16777215 | bit i = godzina i, 1 = komfort | R/W (zapis w firmware: action set_schedule; skuteczność zapisu na kotle niepotwierdzona w dokumentach) |  | zapis: set_schedule kociol fw: sch_boil; karta: ekran PROGRAM (kocioł) | OTWARTE (2026-10-19): skan = 0x1FFFE0 (godz. 5–21, zgodne z panelem), ale odczyt dziś = FFFFFF (cały dzień). Do wyjaśnienia surowymi bajtami (fw v2.19). Odczyt i zapis działały |

### Palnik, dmuchawa, pompy, parametry serwisowe

| Rejestr | Nazwa | Nazwa panela | Typ | Zakres | Kodowanie / jednostka | Dostęp | PIN | Gdzie w firmware / karcie | Uwagi |
|---|---|---|---|---|---|---|---|---|---|
| `0x2210` | CWU – zagrzej teraz | Hot water 1 heat now | U16 | 256…257 | 256 = wył., 257 = wł. (przełącznik) | R (zapis nieprzetestowany) |  | zapis: set_param 20, odczyt fw v2.18: hw_boost | Potwierdzone zmianami na panelu; zapis set_param key 20 |
| `0x2212` | CWU – histereza [°C] | Hot water 1 histeresis | U16 | 0…20 | °C, liczba całkowita 0..20 (karta: 5,0) | R (zapis nieprzetestowany) |  | zapis: set_param 19, odczyt fw v2.18: hw_hyst | Potwierdzone zmianami na panelu; zapis set_param key 19 |
| `0x2214` | CWU – źródło ciepła | Hot water 1 source | U16 | 256…257 | 256 = Kocioł, 257 = Bufor | R/W (potwierdzone zmianą na panelu) | klucz 1 | zapis: set_param 44, odczyt | Źródło ciepła CWU (Menu → Ciepła woda → NASTAWY, klucz 1). Potwierdzone w obie strony 21.10. fw: CWU Źródło |
| `0x2218` | CWU – delta załączenia pompy | Hot water 1 delta min temperature | ? | 258…276 | 256 + wartość [°C] | R/W (potwierdzone zmianą na panelu) | klucz 1 | zapis: set_param 46, odczyt | Różnica temperatur załączenia pompy CWU (zakres 2–20 °C). 10 → 266, 6 → 262. fw: CWU Delta |
| `0x2250` | Jasność płomienia (ekran Palnik: jasność=) | Burner brightness | U16 | 0…100 | 0..100, bez skali; 0 przy zimnym palniku, 100 przy płomieniu (odczyt 22:12 = 100, panel jasność=100) | R (zapis nieprzetestowany) |  | odczyt fw v2.20: "Palnik jasnosc plomienia", poll | Zgodne z panelem: palnik wyłączony jasność=0, pracujący 100 |
| `0x2253` | Burner igniter (FW panela) | Burner igniter | U16 | 0…100 |  | R (zapis nieprzetestowany) |  | odczyt | (auto) zero; zakres 0..100; sąsiedztwo: przed: Dmuchawa – obroty [%] (0x2254) / FW panela: Burner igniter; typ u16, zakres 0…100, domyslna 0, dostep: odczyt na zywo |
| `0x2254` | Dmuchawa – obroty [%] | Burner blower | U16 | 256…356 | młodszy bajt = % | R |  | odczyt fw: blower_pct; karta: dmuchawa % przy palniku | Odczyt |
| `0x2256` | Wstępna dawka paliwa [s] | Pellet predose [s] | U16 | 0…200 | liczba, 0..200 s | R (zapis nieprzetestowany) | klucz 1 | zapis: set_param 22, odczyt fw v2.20 (menu palnika) | (auto) liczba 20; zakres 0..200; sąsiedztwo: po: Dmuchawa – obroty [%] (0x2254) / przed: Podajnik – tryb (0x2259) zmiana 20→21 na panelu (19.10 22:45); poziom menu: klucz 1 (PIN 0900) |
| `0x2257` | Podawanie max [s] | Max Feeding [s] | U16 | 10…150 | raw/10 s (10..150 = 1,0..15,0 s); wyliczane z testu paliwa | R (zapis nieprzetestowany) | klucz 1 | zapis: set_param 23, odczyt fw v2.20 (menu palnika) | (auto) liczba 56 (jeśli /10: 5.6); zakres 10..150; sąsiedztwo: po: Dmuchawa – obroty [%] (0x2254) / przed: Podajnik – tryb (0x2259) skan 56 → 59 → 61 (panel 5,9 → 6,0); zmiana na panelu 22:45; poziom menu: klucz 1 (PIN 0900) |
| `0x2258` | Liczba czyszczeń rusztu | Grate cleaning number | U16 | 256…266 | flaga+bajt: raw−256 (0..10) | R (zapis nieprzetestowany) | klucz 1 | zapis: set_param 34, odczyt fw v2.20 (menu palnika) | (auto) flaga 0/1 (raw 257=1); zakres 256..266; sąsiedztwo: po: Dmuchawa – obroty [%] (0x2254) / przed: Podajnik – tryb (0x2259) zmiana 1→2 (257→258); poziom menu: klucz 1 (PIN 0900) |
| `0x2259` | Podajnik – tryb testowy | Burner storage feeder test | U16 | 256…258 | 256 = A (automat), 257 = OFF/CLOSE, 258 = ON/OPEN (+flaga 0x0100) | R/W (potwierdzone zapisem) |  | zapis: Test wyjsc / Podajnik, odczyt fw: feeder_* | Polecenie trybu testowego wyjścia (Menu → Test wyjść, wymaga PIN poziom 2). Zapis zmienia tryb, stan fizyczny wyjścia zależy od sterownika. Potwierdzone wcześniej. Po próbie zawsze wracać na A (256). fw: akcja set_output |
| `0x2261` | Krzywa dmuchawy – obroty dmuchawy [%] przy mocy kotła 20 % | blower char. 1 | U16 | 0…100 | 0–100 % obrotów dmuchawy | R (zapis nieprzetestowany) |  | zapis: set_param 5, odczyt fw v2.16: dmuchawa modulacja 20 %; karta: Moc dmuchawy (modulacja); fw v2.20 (menu palnika) | ZNALEZIONA (estyma-otwarte-punkty §1): punkty krzywej idą z kotła (skan 30/38/48/55/61; HA 2026-10-19: 30/38/48/54/61). Nie zmieniamy ich z karty poza ekranem serwisowym (zapis set_param key 5). 0 % przy mocy 20 % = wyłączona dmuchawa – ostrożnie; poziom menu: klucz 1 (PIN 0900) |
| `0x2262` | Krzywa dmuchawy – obroty dmuchawy [%] przy mocy kotła 40 % | blower char. 2 | U16 | 0…100 | 0–100 % obrotów dmuchawy | R (zapis nieprzetestowany) |  | zapis: set_param 6, odczyt fw v2.16: dmuchawa modulacja 40 %; karta: Moc dmuchawy (modulacja); fw v2.20 (menu palnika) | ZNALEZIONA (estyma-otwarte-punkty §1): punkty krzywej idą z kotła (skan 30/38/48/55/61; HA 2026-10-19: 30/38/48/54/61). Nie zmieniamy ich z karty poza ekranem serwisowym (zapis set_param key 6). 0 % przy mocy 20 % = wyłączona dmuchawa – ostrożnie; poziom menu: klucz 1 (PIN 0900) |
| `0x2263` | Krzywa dmuchawy – obroty dmuchawy [%] przy mocy kotła 60 % | blower char. 3 | U16 | 0…100 | 0–100 % obrotów dmuchawy | R (zapis nieprzetestowany) |  | zapis: set_param 7, odczyt fw v2.16: dmuchawa modulacja 60 %; karta: Moc dmuchawy (modulacja); fw v2.20 (menu palnika) | ZNALEZIONA (estyma-otwarte-punkty §1): punkty krzywej idą z kotła (skan 30/38/48/55/61; HA 2026-10-19: 30/38/48/54/61). Nie zmieniamy ich z karty poza ekranem serwisowym (zapis set_param key 7). 0 % przy mocy 20 % = wyłączona dmuchawa – ostrożnie; poziom menu: klucz 1 (PIN 0900) |
| `0x2264` | Krzywa dmuchawy – obroty dmuchawy [%] przy mocy kotła 80 % | blower char. 4 | U16 | 0…100 | 0–100 % obrotów dmuchawy | R (zapis nieprzetestowany) |  | zapis: set_param 8, odczyt fw v2.16: dmuchawa modulacja 80 %; karta: Moc dmuchawy (modulacja); fw v2.20 (menu palnika) | ZNALEZIONA (estyma-otwarte-punkty §1): punkty krzywej idą z kotła (skan 30/38/48/55/61; HA 2026-10-19: 30/38/48/54/61). Nie zmieniamy ich z karty poza ekranem serwisowym (zapis set_param key 8). 0 % przy mocy 20 % = wyłączona dmuchawa – ostrożnie; poziom menu: klucz 1 (PIN 0900) |
| `0x2265` | Krzywa dmuchawy – obroty dmuchawy [%] przy mocy kotła 100 % | blower char. 5 | U16 | 0…100 | 0–100 % obrotów dmuchawy | R (zapis nieprzetestowany) |  | zapis: set_param 9, odczyt fw v2.16: dmuchawa modulacja 100 %; karta: Moc dmuchawy (modulacja); fw v2.20 (menu palnika) | ZNALEZIONA (estyma-otwarte-punkty §1): punkty krzywej idą z kotła (skan 30/38/48/55/61; HA 2026-10-19: 30/38/48/54/61). Nie zmieniamy ich z karty poza ekranem serwisowym (zapis set_param key 9). 0 % przy mocy 20 % = wyłączona dmuchawa – ostrożnie; poziom menu: klucz 1 (PIN 0900) |
| `0x2267` | Podawanie ręczne – licznik | Burner storage feeder left time during refuling [s] | U16 | 0…3600 | sekundy, 0–3600; maleje podczas podawania | R (zapis nieprzetestowany) |  | odczyt fw: feed_manual_off; karta: czas w oknie paliwa | Do weryfikacji |
| `0x2268` | Wartość 20 (kandydat: moc min?) | exh. fan char. 1 | U16 | 0…100 | 0–100 | R (zapis nieprzetestowany) |  | zapis: set_param 68, odczyt — | Do porównania z Moc min z panelu |
| `0x226A` | Próg foto | Brightness threshold | U16 | 261…356 | flaga+bajt: raw−256 (5..100) | R (zapis nieprzetestowany) | klucz 1 | zapis: set_param 24, odczyt fw v2.20 (menu palnika) | (auto) flaga+bajt: wartość 30 (raw 286); zakres 261..356; sąsiedztwo: po: Wartość 20 (kandydat: moc min?) (0x2268) / przed: Temperatura palnika (0x226C) zmiana 30→31 (286→287); 0x2260 to NIE próg foto; poziom menu: klucz 1 (PIN 0900) |
| `0x226B` | Czas wygaszania [min] | Burning off time [min] | U16 | 257…271 | flaga+bajt: raw−256 (1..15) | R (zapis nieprzetestowany) | klucz 1 | zapis: set_param 30, odczyt fw v2.20 (menu palnika) | (auto) flaga+bajt: wartość 3 (raw 259); zakres 257..271; sąsiedztwo: po: Wartość 20 (kandydat: moc min?) (0x2268) / przed: Temperatura palnika (0x226C) zmiana 3→4 (259→260); poziom menu: klucz 1 (PIN 0900) |
| `0x226C` | Temperatura palnika | Burner feeder temperature [dC] | U16 | 0…1500 | raw/10 °C | R (zapis nieprzetestowany) |  | odczyt fw: burner_temp | Potwierdzić na panelu |
| `0x226D` | Czas podawania paliwa – bieżący [s×10] | Burner storage feeding time [dS] | U16 | 0…1000 | raw/10 s; 0 gdy podajnik nie pracuje | R (zapis nieprzetestowany) |  | odczyt fw v2.20: "Palnik czas podawania paliwa" (raw/10), poll | potwierdzone z panelem (3,8 s); na ekranie Palnik pod ikoną podajnika paliwa |
| `0x2270` | Moc min [%] | Min power | u8 | 30…100 | flaga 0x01 + bajt: młodszy bajt = % | R (zapis nieprzetestowany) | poziom 0 | zapis: set_param 0, odczyt fw v2.16: power_min; karta: okno Moc min; fw v2.20 (menu palnika) | Potwierdzone zdjęciami panelu; zapis przez set_param key 0; poziom menu: użytkownik |
| `0x2271` | Moc max [%] | Max power | u8 | 30…100 | flaga 0x01 + bajt: młodszy bajt = % (>= Moc min) | R (zapis nieprzetestowany) | poziom 0 | zapis: set_param 1, odczyt fw v2.16: power_max; karta: okno Moc max; fw v2.20 (menu palnika) | Potwierdzone zdjęciami panelu; zapis przez set_param key 1; poziom menu: użytkownik |
| `0x2272` | Ilość paliwa test [kg/h] | Feeder rate [dkg/h] | ? | 50…1000 | raw/10, 5–100 | R |  | zapis: set_param 4, odczyt fw: fuel_test; fw v2.20 (menu palnika) | Skan 152 = stara wartość; teraz 140 (14,0 kg/h, panel 19.10 22:30); odczyt w HA: sensor ilosc_paliwa_test; poziom menu: użytkownik |
| `0x2273` | Korekta powietrza [%] | Burner blower corretion | U16 | -10…40 | −10…40 % | R (zapis nieprzetestowany) |  | zapis: set_param 3, odczyt fw: air_corr; fw v2.20 (menu palnika) | Zapis przez set_param key 3 (-10..40 %); okno edycji do zrobienia Korekta powietrza = 18 zgodna z panelem; poziom menu: użytkownik |
| `0x2275` | Wartość 50 (kandydat: moc?) | exh. fan char. 4 | U16 | 0…100 | 0–100 | R (zapis nieprzetestowany) |  | zapis: set_param 71, odczyt — | Do porównania z panelem |
| `0x2278` | Pompa CWU – stan pracy | Hot water pump state | U16 | 256…257 | młodszy bajt ≠0 = pracuje | R |  | odczyt fw: hw_pump | Stan pompy CWU (257 po wymuszeniu ON w teście). Odczyt. Rejestr POLECENIA pompy CWU nieznany (węzeł 86?) |
| `0x227A` | Wartość 60 (kandydat: moc?) | exh. fan char. 5 | U16 | 0…100 | 0–100 | R (zapis nieprzetestowany) |  | zapis: set_param 72, odczyt — | Do porównania z panelem |
| `0x2283` | Dmuchawa – tryb testowy | Blower test | U16 | 256…258 | 256 = A (automat), 257 = OFF/CLOSE, 258 = ON/OPEN (+flaga 0x0100) | R/W (potwierdzone zapisem) |  | zapis: Test wyjsc / Dmuchawa, odczyt fw: blower_* | Polecenie trybu testowego wyjścia (Menu → Test wyjść, wymaga PIN poziom 2). Zapis zmienia tryb, stan fizyczny wyjścia zależy od sterownika. Potwierdzone wcześniej. Po próbie zawsze wracać na A (256). fw: akcja set_output |
| `0x2284` | Zapalarka – tryb testowy | Igniter test | U16 | 256…258 | 256 = A (automat), 257 = OFF/CLOSE, 258 = ON/OPEN (+flaga 0x0100) | R/W (potwierdzone zapisem) |  | zapis: Test wyjsc / Zapalarka | Polecenie trybu testowego wyjścia (Menu → Test wyjść, wymaga PIN poziom 2). Zapis zmienia tryb, stan fizyczny wyjścia zależy od sterownika. Potwierdzone 19.10. Po próbie zawsze wracać na A (256). fw: akcja set_output |
| `0x2289` | Moc dmuchawy rozpalanie [%] | Blower power during fire up | U16 | 276…356 | flaga+bajt: raw−256 (0..100 %); 302 = 46 %, 301 = 45 % | R (zapis nieprzetestowany) | klucz 1 | zapis: set_param 25, odczyt —; fw v2.20 (menu palnika) | Zmiana 46→45 na panelu (19.10 22:52): 302→301. Wcześniejszy opis „kopia wartości opałowej" był błędny – zbieżność 46 = 4,6 kWh/kg ×10 (wartość opałowa to 0x2292); poziom menu: klucz 1 (PIN 0900) |
| `0x228C` | Exhaust fan power (FW panela) | Exhaust fan power | U16 | 256…356 | flaga 0x01 + bajt: raw − 256 (zakres wartości 0…100; jeśli x10: 0…10) | R (zapis nieprzetestowany) |  | odczyt | (auto) flaga 0/1 (raw 256=0); zakres 256..356; sąsiedztwo: po: (kopia wartości opałowej – nie zmienia się) (0x2289) / FW panela: Exhaust fan power; typ u8, zakres 0…100, domyslna 0, dostep: odczyt na zywo |
| `0x2290` | Czas rozżarzania [min] | Incandescing time [min] | U16 | 256…276 | flaga+bajt: raw−256 [min], zakres 0..20 (poziom 1) | R/W (zapis w firmware, nietestowany osobno) | klucz 1 | zapis: set_param 28, odczyt fw v2.20: "Palnik czas rozzarzania", set_param key 28 (0..20) | (auto) flaga+bajt: wartość 2 (raw 258); zakres 256..?; sąsiedztwo: przed: Histereza wyłączenia kotła [°C] (0x2291) zmiana 2→7 (258→263) 19.10 23:40; zakres 0–20 min z panelu; poziom menu: klucz 1 (PIN 0900) |
| `0x2291` | Histereza wyłączenia kotła [°C] | Boiler off histeresis | ? | 0…20 | °C, liczba całkowita 0..20 | R (zapis nieprzetestowany) |  | zapis: set_param 11, odczyt fw v2.17 | Potwierdzone zmianą na panelu 5 → 6; zapis set_param key 11 |
| `0x2292` | Wartość opałowa [kWh/kg] | Fuel calorific [kWh/kg] | U16 | 276…356 | jak 0x2289 (302 → 4,6 kWh/kg) | R (zapis nieprzetestowany) | poziom 0 | zapis: set_param 2, odczyt fw v2.16: fuel_cv; karta: okno wartości opałowej; fw v2.20 (menu palnika) | Potwierdzone testem zmiany na panelu 4,6 → 4,7; zapis set_param key 2 (2,0..10,0); poziom menu: użytkownik |
| `0x2295` | Podajnik palnika – tryb testowy | Burner feeder test | U16 | 256…258 | 256 = A (automat), 257 = OFF/CLOSE, 258 = ON/OPEN (+flaga 0x0100) | R/W (potwierdzone zapisem) |  | zapis: Test wyjsc / Podajnik palnika | Polecenie trybu testowego podajnika palnika (Test wyjść). Rejestr polecenia znaleziony; NIEPOTWIERDZONY jest bit stanu „podajnik palnika pracuje” (PDO 0x456 bajt0 bit1 nie zmienia się). fw: set_output out=19 |
| `0x2297` | HW1 anti legionella (FW panela) | HW1 anti legionella | U16 | 256…257 | flaga 0x01 + bajt: raw − 256 (zakres wartości 0…1; jeśli x10: 0…0.1) | R (zapis nieprzetestowany) |  | zapis: set_param 67, odczyt | (auto) flaga 0/1 (raw 256=0); zakres 256..257; sąsiedztwo: przed: Pompa CO 1 (0x2299) / FW panela: HW1 anti legionella; typ u8, zakres 0…1, domyslna 0, dostep: nastawa |
| `0x2299` | Pompa CO1 – stan pracy | CH pump state | U16 | 256…257 | młodszy bajt ≠0 = pracuje | R |  | odczyt fw: ch1_pump | Stan pompy obiegu CO1. Odczyt; potwierdzone testem 21.10 |
| `0x229A` | Pompa CO2 – stan pracy | - | U16 | 256…257 | młodszy bajt ≠0 = pracuje | R |  | odczyt fw: ch2_pump | Stan pompy obiegu CO2 (kocioł ma jeden obieg – używane tylko z dwa_obiegi_co). Odczyt; reaguje na test CO2 (21.10) |
| `0x22A1` | CO1 – czujnik pokojowy | Room temp sensor type | U16 | 256…261 | flaga+bajt: 0 brak, 1 CTP1, 2 CTP2, 3 videROOM, 4 termostat, 5 CAN | R/W (potwierdzone zmiana na panelu i zapisem z ESP) | klucz 1 | zapis: set_param 63, odczyt | Menu → Ogrzewanie 1 → NASTAWY Zmiana termostat→brak: 260→256; set_param 63 |
| `0x22A5` | CO1 – czujnik CO (0/1) | CH sensor use | U16 | 256…257 | flaga: 256 = wył., 257 = wł. | R/W (potwierdzone zmiana na panelu i zapisem z ESP) | klucz 1 | zapis: set_param 62, odczyt | Menu → Ogrzewanie 1 → NASTAWY Zmiana na panelu wł.→wył.: 257→256; set_param 62 |
| `0x22AD` | CO 1 – temperatura zadana (wynikowa) | CH temp calc | U16 | 10…90 | °C (bez dzielenia), 10–90 | R/W (zapis w firmware, nietestowany osobno) |  | odczyt fw: ch1_set_result; karta: liczba przy temperaturze CO | Odczyt |
| `0x22AE` | CO 2 – temperatura zadana (wynikowa) | - | U16 | 0…90 | °C | R/W (zapis w firmware, nietestowany osobno) |  | odczyt fw: ch2_set_result | Brak drugiego obiegu / w firmware wyłączone (dwa_obiegi_co: false) |
| `0x22B1` | CO1 – zwiekszenie temperatury zrodla [°C] | CH delta source [C] | U16 | 256…286 | flaga+bajt: raw = 256 + °C (0..30) | R/W (potwierdzone zmiana na panelu i zapisem z ESP) | klucz 1 | zapis: set_param 51, odczyt | Menu → Ogrzewanie 1 → NASTAWY Zmiana na panelu 22.10; set_param 51 |
| `0x22B5` | CO1 – czas mieszacza [s] | CH mixer opening time [s] | U16 | 60…360 | liczba s (bez flagi), 60..360 | R/W (potwierdzone zmiana na panelu i zapisem z ESP) | klucz 1 | zapis: set_param 58, odczyt | Menu → Ogrzewanie 1 → NASTAWY Zmiana na panelu 22.10; set_param 58 |
| `0x22B9` | Mieszacz CO1 – tryb testowy (A/CLOSE/OPEN) | CH mixer state | U16 | 256…258 | 256 = A (automat), 257 = OFF/CLOSE, 258 = ON/OPEN (+flaga 0x0100) | R/W (potwierdzone zapisem) |  | odczyt | Polecenie trybu testowego wyjścia (Menu → Test wyjść, wymaga PIN poziom 2). Zapis zmienia tryb, stan fizyczny wyjścia zależy od sterownika. Potwierdzone 21.10. OPEN → 258. Po próbie zawsze wracać na A (256). fw: akcja set_output |
| `0x22BD` | CO 1 – histereza [°C] | Room temp hysteresis [C] | U16 | 256…306 | flaga + bajt: raw − 256 = 10 × °C (0..5 °C) | R (zapis nieprzetestowany) |  | zapis: set_param 12, odczyt fw v2.18: ch1_hyst | Potwierdzone zmianami na panelu; zapis set_param key 12 |
| `0x22C1` | CO 1 – kalibracja czujnika [°C] | Room sensor cal [C] | U16 | -30…30 | int16 / 10 °C (−3..+3) | R (zapis nieprzetestowany) |  | zapis: set_param 13, odczyt fw v2.18: ch1_calib | Potwierdzone zmianami na panelu; zapis set_param key 13 |
| `0x22C5` | CO 1 – krzywa pogodowa, temperatura zewnętrzna −20 °C [°C zasilania] | CH temp for -20C [C] | U16 | 276…336 | flaga + bajt: raw − 256 = °C (20..80) | R |  | zapis: set_param 16, odczyt fw v2.18: ch1_curve | Potwierdzone zmianami na panelu; punkty krzywej odczyt/zapis (set_param key 16) |
| `0x22C9` | CO 1 – krzywa pogodowa, temperatura zewnętrzna 0 °C [°C zasilania] | CH temp for 0C [C] | U16 | 276…336 | flaga + bajt: raw − 256 = °C (20..80) | R |  | zapis: set_param 17, odczyt fw v2.18: ch1_curve | Potwierdzone zmianami na panelu; punkty krzywej odczyt/zapis (set_param key 17) |
| `0x22CD` | CO 1 – krzywa pogodowa, temperatura zewnętrzna +10 °C [°C zasilania] | CH temp for -20C [C] | U16 | 276…336 | flaga + bajt: raw − 256 = °C (20..80) | R |  | zapis: set_param 18, odczyt fw v2.18: ch1_curve | Potwierdzone zmianami na panelu; punkty krzywej odczyt/zapis (set_param key 18) |
| `0x22D5` | CO1 – temperatura maksymalna [°C] | CH max temp [C] | U16 | 286…336 | flaga+bajt: raw = 256 + °C (30..80) | R/W (potwierdzone zmiana na panelu i zapisem z ESP) | klucz 1 | zapis: set_param 52, odczyt | Menu → Ogrzewanie 1 → NASTAWY Zmiana na panelu 22.10; set_param 52 |
| `0x22D9` | CO1 – wspolczynnik korekcji t. CO | CH correction factor [C] | U16 | 256…276 | flaga+bajt: raw = 256 + wartosc (0..20) | R/W (potwierdzone zmiana na panelu i zapisem z ESP) | klucz 1 | zapis: set_param 53, odczyt | Menu → Ogrzewanie 1 → NASTAWY Zmiana na panelu 22.10; set_param 53 |
| `0x22DD` | CO1 – MAX Tzew pomp komfort [°C] | - | U16 | 256…286 | flaga+bajt: raw = 256 + °C (0..30) | R/W (potwierdzone zmiana na panelu i zapisem z ESP) | klucz 1 | zapis: set_param 54, odczyt | Menu → Ogrzewanie 1 → NASTAWY Zmiana na panelu 22.10; set_param 54 |
| `0x22E1` | CO1 – MAX Tzew pomp ekonomiczny [°C] | - | U16 | 256…286 | flaga+bajt: raw = 256 + °C (0..30) | R/W (potwierdzone zmiana na panelu i zapisem z ESP) | klucz 1 | zapis: set_param 55, odczyt | Menu → Ogrzewanie 1 → NASTAWY Zmiana na panelu 22.10; set_param 55 |
| `0x22E5` | CO1 – obnizenie temperatury CO [°C] | CH temp lowering [C] | U16 | 256…296 | flaga+bajt: raw = 256 + °C (0..40) | R/W (potwierdzone zmiana na panelu i zapisem z ESP) | klucz 1 | zapis: set_param 56, odczyt | Menu → Ogrzewanie 1 → NASTAWY Panel 5→7 (skan 261→263); set_param 56 |
| `0x22E9` | CO1 – MIN temperatura CO pomp [°C] | Min CH temp for pump [C] | U16 | 276…316 | flaga+bajt: raw = 256 + °C (20..60) | R/W (potwierdzone zmiana na panelu i zapisem z ESP) | klucz 1 | zapis: set_param 57, odczyt | Menu → Ogrzewanie 1 → NASTAWY Zmiana na panelu 22.10; set_param 57 |
| `0x22F1` | CO1 – stala pompa (0/1) | Permament pump | U16 | 256…257 | flaga: 256 = wył., 257 = wł. | R/W (potwierdzone zmiana na panelu i zapisem z ESP) | klucz 1 | zapis: set_param 59, odczyt | Menu → Ogrzewanie 1 → NASTAWY Przełączenie na panelu 257→256; set_param 59 |
| `0x22F9` | CO1 – obnizenie Tco dla ochrony powrotu (0/1) | Tch lowering for energ. consumption reduction | U16 | 256…257 | flaga: 256 = wył., 257 = wł. | R/W (potwierdzone zmiana na panelu i zapisem z ESP) | klucz 1 | zapis: set_param 60, odczyt | Menu → Ogrzewanie 1 → NASTAWY Przełączenie na panelu 256→257; set_param 60 |

### Odczyt ręczny / luka w skanie

| Rejestr | Nazwa | Nazwa panela | Typ | Zakres | Kodowanie / jednostka | Dostęp | PIN | Gdzie w firmware / karcie | Uwagi |
|---|---|---|---|---|---|---|---|---|---|
| `0x2216` | CWU – zwiększenie temperatury źródła | Hot water 1 delta source | u8 | 261…276 | 256 + wartość [°C] | R/W (potwierdzone zmianą na panelu) | klucz 1 | zapis: set_param 45, odczyt | Zwiększenie temp. źródła względem zadanej CWU (zakres 5–20 °C). 8 → 264, 5 → 261. fw: CWU Zwiększenie |
| `0x226E` | exh. fan char. 2 (FW panela) | exh. fan char. 2 | u16 |  |  | R (zapis nieprzetestowany) |  | zapis: set_param 69, odczyt | (auto) liczba 30; brak subów 2-4 (rejestr tylko do odczytu lub sub nie istnieje); sąsiedztwo: po: Temperatura palnika (0x226C) / przed: Moc min [%] (0x2270) / FW panela: exh. fan char. 2; typ u16, zakres 0…100, domyslna 30, dostep: nastawa Odczytany ręcznie (brak w skanie katalogowym) |
| `0x226F` | exh. fan char. 3 (FW panela) | exh. fan char. 3 | u16 |  |  | R (zapis nieprzetestowany) |  | zapis: set_param 70, odczyt | (auto) liczba 40; brak subów 2-4 (rejestr tylko do odczytu lub sub nie istnieje); sąsiedztwo: po: Temperatura palnika (0x226C) / przed: Moc min [%] (0x2270) / FW panela: exh. fan char. 3; typ u16, zakres 0…100, domyslna 40, dostep: nastawa Odczytany ręcznie (brak w skanie katalogowym) |
| `0x2296` | Test wyjsc – Pompa CWU | HW1 pump test | u8 | 256…257 | 256 = A (auto), 257 = OFF, 258 = ON | R/W (poziom 2) | klucz 2 | zapis: Test wyjsc / Pompa CWU | Menu → Test wyjść → Pompa CWU Różnica migawek 22.10 (ON = 258, A = 256); poprawia wcześniejszy opis „stan wentylatora” |
| `0x22D1` | CO1 – zrodlo (0 Kociol / 1 Bufor) | CH source | U16 | 256…257 | flaga: 256 = Kocioł, 257 = Bufor | R/W (potwierdzone zmiana na panelu i zapisem z ESP) | klucz 1 | zapis: set_param 61, odczyt | Menu → Ogrzewanie 1 → NASTAWY Zmiana na panelu Kocioł→Bufor: 256→257; set_param 61 |
| `0x2999` | Odstęp czyszczenia [h] | Burner max continuous work time [h] | u16 | 1…12 | liczba h (zakres 1..12), bez flagi | R | klucz 1 | zapis: set_param 35, odczyt fw v2.20 (menu palnika) | (auto) liczba 3; brak subów 2-4 (rejestr tylko do odczytu lub sub nie istnieje) Skan 3 → odczyt 12 po zmianie na panelu 3→12 (19.10 23:15). Nie pojawia się w migawkach (rejestr z listy odpytywania), odczyt tylko pojedynczy sdo_read; poziom menu: klucz 1 (PIN 0900) |
| `0x3525` | Additional fuel storage (FW panela) | Additional fuel storage | u8 |  |  | R (zapis nieprzetestowany) |  | odczyt | (auto) flaga 0/1 (raw 256=0); brak subów 2-4 (rejestr tylko do odczytu lub sub nie istnieje) / FW panela: Additional fuel storage; typ u8, zakres 0…1, domyslna 0, dostep: nastawa Odczytany ręcznie (brak w skanie katalogowym) |
| `0x3614` | Average oxygen for 50% pwr [%] (FW panela) | Average oxygen for 50% pwr [%] | u8 |  |  | R (zapis nieprzetestowany) |  | odczyt | (auto) flaga 0/1 (raw 256=0); brak subów 2-4 (rejestr tylko do odczytu lub sub nie istnieje); sąsiedztwo: po: Statystyki: czas pracy podajnika 2 [h] (0x3612) / przed: Statystyki: liczba czyszczeń wymiennika (0x3618) / FW panela: Average oxygen for 50% pwr [%]; typ u8, zakres 0…255, dostep: odczyt na zywo Odczytany ręcznie (brak w skanie katalogowym) |
| `0x3701` | Min EGT required [C] (FW panela) | Min EGT required [C] | u16 |  |  | R (zapis nieprzetestowany) |  | zapis: set_param 78, odczyt | (auto) liczba 90 (jeśli /10: 9.0); brak subów 2-4 (rejestr tylko do odczytu lub sub nie istnieje) / FW panela: Min EGT required [C]; typ u16, zakres 70…120, domyslna 90, dostep: nastawa Odczytany ręcznie (brak w skanie katalogowym) |

### Parametry 0x2300–0x2FFF

| Rejestr | Nazwa | Nazwa panela | Typ | Zakres | Kodowanie / jednostka | Dostęp | PIN | Gdzie w firmware / karcie | Uwagi |
|---|---|---|---|---|---|---|---|---|---|
| `0x2301` | Wejście: zgoda regulatora (IN3) | CH thermostat state | U16 | 256…257 | 257 = pozwala grzać, 256 = nie | R |  | odczyt fw: in_regulator | Test; tylko odczyt |
| `0x299A` | Rozżarzanie paliwo [%] | Incandenscing fuel [%] | U16 | 276…356 | flaga+bajt: raw−256 [%], zakres 20..100 (poziom 1) | R/W (zapis w firmware, nietestowany osobno) | klucz 1 | zapis: set_param 29, odczyt fw v2.20: "Palnik rozzarzanie paliwo", set_param key 29 | (auto) flaga+bajt: wartość 20 (raw 276); zakres 276..356 zmiana 20→22 (276→278) 19.10 23:40; poziom menu: klucz 1 (PIN 0900) |
| `0x299D` | HALL Activated (FW panela) | HALL Activated | U16 | 256…257 | flaga 0x01 + bajt: raw − 256 (zakres wartości 0…1; jeśli x10: 0…0.1) | R (zapis nieprzetestowany) |  | odczyt | (auto) flaga 0/1 (raw 256=0); zakres 256..257 / FW panela: HALL Activated; typ u8, zakres 0…1, domyslna 0, dostep: nastawa |
| `0x299E` | Boiler pump work mode (FW panela) | Boiler pump work mode | U16 | 256…257 | flaga 0x01 + bajt: raw − 256 (zakres wartości 0…1; jeśli x10: 0…0.1) | R (zapis nieprzetestowany) |  | odczyt | (auto) flaga 0/1 (raw 256=0); zakres 256..257 / FW panela: Boiler pump work mode; typ u8, zakres 0…2, domyslna 0, dostep: nastawa |

### Parametry serwisowe 0x3000

| Rejestr | Nazwa | Nazwa panela | Typ | Zakres | Kodowanie / jednostka | Dostęp | PIN | Gdzie w firmware / karcie | Uwagi |
|---|---|---|---|---|---|---|---|---|---|
| `0x3003` | Czas ruchu rusztu [s] | Grate move in modulation [0.1s] | U16 | 0…600 | raw/10 s (0..600 = 0..60,0) | R (zapis nieprzetestowany) | klucz 2 | zapis: set_param 40, odczyt fw v2.20 (menu palnika) | (auto) liczba 200 (jeśli /10: 20.0); zakres 0..600 zmiana 20,0→20,2 (200→202); poziom menu: klucz 2 (PIN 0999) |
| `0x300C` | Moc dmuchawy wygaszanie [%] | Blower power in burning off [%] | U16 | 257…356 | flaga+bajt: raw−256 (0..100) | R (zapis nieprzetestowany) | klucz 1 | zapis: set_param 27, odczyt fw v2.20 (menu palnika) | (auto) flaga+bajt: wartość 60 (raw 316); zakres 257..356; sąsiedztwo: przed: CWU – priorytet (0x300D) zmiana 60→62 (316→318); poziom menu: klucz 1 (PIN 0900) |
| `0x300D` | CWU – priorytet | Hot water priority | U16 | 256…257 | 256 = wył., 257 = wł. (przełącznik) | R (zapis nieprzetestowany) |  | zapis: set_param 21, odczyt fw v2.18: hw_prio | Potwierdzone zmianami na panelu; zapis set_param key 21 |
| `0x300E` | Minimalne obroty dmuchawy [*100] | Burner blower minimal RPM [*100] | U16 | 0…5 | liczba 0..5 | R (zapis nieprzetestowany) | klucz 2 | zapis: set_param 43, odczyt fw v2.20 (menu palnika) | (auto) liczba 5; zakres 0..5; sąsiedztwo: po: CWU – priorytet (0x300D) zmiana 5→3; poziom menu: klucz 2 (PIN 0999) |
| `0x3122` | Exchanger cleaning interval [min] (FW panela) | Exchanger cleaning interval [min] | U16 | 10…600 |  | R (zapis nieprzetestowany) |  | zapis: set_param 80, odczyt | (auto) liczba 180 (jeśli /10: 18.0); zakres 10..600 / FW panela: Exchanger cleaning interval [min]; typ u16, zakres 10…600, domyslna 180, dostep: nastawa |

### Zbiornik, statystyki, liczniki

| Rejestr | Nazwa | Nazwa panela | Typ | Zakres | Kodowanie / jednostka | Dostęp | PIN | Gdzie w firmware / karcie | Uwagi |
|---|---|---|---|---|---|---|---|---|---|
| `0x3500` | Main module type (FW panela) | Main module type | U16 | 256…257 | flaga 0x01 + bajt: raw − 256 (zakres wartości 0…1; jeśli x10: 0…0.1) | R (zapis nieprzetestowany) |  | odczyt | (auto) flaga 0/1 (raw 256=0); zakres 256..257 / FW panela: Main module type; typ u8, zakres 0…1, domyslna 0, dostep: nastawa |
| `0x3501` | Autoconfig activation (FW panela) | Autoconfig activation | ? | 256…257 | flaga 0x01 + bajt: raw − 256 (zakres wartości 0…1; jeśli x10: 0…0.1) | R (zapis nieprzetestowany) |  | odczyt | (auto) flaga 0/1 (raw 256=0); zakres 256..257 / FW panela: Autoconfig activation; typ u8, zakres 0…1, domyslna 1, dostep: nastawa |
| `0x3505` | Outside temperature sensor configuration (FW panela) | Outside temperature sensor configuration | U16 | 256…258 | flaga 0x01 + bajt: raw − 256 (zakres wartości 0…2; jeśli x10: 0…0.2) | R (zapis nieprzetestowany) |  | odczyt | (auto) flaga 0/1 (raw 257=1); zakres 256..258; sąsiedztwo: przed: Statystyki: całkowite zużycie paliwa [kg] (0x3507) / FW panela: Outside temperature sensor configuration; typ u8, zakres 0…2, domyslna 0, dostep: nastawa |
| `0x3506` | Sound alarm activation (FW panela) | Sound alarm activation | U16 | 256…257 | flaga 0x01 + bajt: raw − 256 (zakres wartości 0…1; jeśli x10: 0…0.1) | R (zapis nieprzetestowany) |  | zapis: set_param 73, odczyt | (auto) flaga 0/1 (raw 257=1); zakres 256..257; sąsiedztwo: przed: Statystyki: całkowite zużycie paliwa [kg] (0x3507) / FW panela: Sound alarm activation; typ u8, zakres 0…1, domyslna 1, dostep: nastawa |
| `0x3507` | Statystyki: całkowite zużycie paliwa [kg] | Total fuel counter[kg] | U16 | 0…4294967295 | kg (16706; to samo w 0x2294 i 0x3507) | R (zapis nieprzetestowany) |  | odczyt karta: Statystyki | Mapowanie z fw v2.14 |
| `0x3508` | Silence hours from (FW panela) | Silence hours from | U16 | 256…280 | flaga 0x01 + bajt: raw − 256 (zakres wartości 0…24; jeśli x10: 0…2.4) | R (zapis nieprzetestowany) |  | zapis: set_param 74, odczyt | (auto) flaga+bajt: wartość 22 (raw 278); zakres 256..280; sąsiedztwo: po: Statystyki: całkowite zużycie paliwa [kg] (0x3507) / FW panela: Silence hours from; typ u8, zakres 0…24, domyslna 22, dostep: nastawa |
| `0x3509` | Silence hours to (FW panela) | Silence hours to | U16 | 256…280 | flaga 0x01 + bajt: raw − 256 (zakres wartości 0…24; jeśli x10: 0…2.4) | R (zapis nieprzetestowany) |  | zapis: set_param 75, odczyt | (auto) flaga+bajt: wartość 6 (raw 262); zakres 256..280; sąsiedztwo: po: Statystyki: całkowite zużycie paliwa [kg] (0x3507) / FW panela: Silence hours to; typ u8, zakres 0…24, domyslna 6, dostep: nastawa |
| `0x350A` | Return to boiler temperature sensor (FW panela) | Return to boiler temperature sensor | U16 | 256…257 | flaga 0x01 + bajt: raw − 256 (zakres wartości 0…1; jeśli x10: 0…0.1) | R (zapis nieprzetestowany) |  | odczyt | (auto) flaga 0/1 (raw 257=1); zakres 256..257; sąsiedztwo: po: Statystyki: całkowite zużycie paliwa [kg] (0x3507) / FW panela: Return to boiler temperature sensor; typ u8, zakres 0…1, domyslna 0, dostep: nastawa |
| `0x350B` | Profile number (FW panela) | Profile number | U16 | 257…259 | flaga 0x01 + bajt: raw − 256 (zakres wartości 1…3; jeśli x10: 0.1…0.3) | R (zapis nieprzetestowany) |  | odczyt | (auto) flaga+bajt: wartość 2 (raw 258); zakres 257..259; sąsiedztwo: po: Statystyki: całkowite zużycie paliwa [kg] (0x3507) / FW panela: Profile number; typ u8, zakres 1…3, domyslna 1, dostep: nastawa |
| `0x350C` | Is this device cascade master (FW panela) | Is this device cascade master | U16 | 256…257 | flaga 0x01 + bajt: raw − 256 (zakres wartości 0…1; jeśli x10: 0…0.1) | R (zapis nieprzetestowany) |  | odczyt | (auto) flaga 0/1 (raw 256=0); zakres 256..257 / FW panela: Is this device cascade master; typ u8, zakres 0…1, domyslna 0, dostep: nastawa |
| `0x350D` | Pressure sensor (FW panela) | Pressure sensor | U16 | 256…257 | flaga 0x01 + bajt: raw − 256 (zakres wartości 0…1; jeśli x10: 0…0.1) | R (zapis nieprzetestowany) |  | odczyt | (auto) flaga 0/1 (raw 256=0); zakres 256..257 / FW panela: Pressure sensor; typ u8, zakres 0…1, domyslna 0, dostep: nastawa |
| `0x3600` | Zbiornik – pojemność [kg] | Tank capacity [kg] | U16 | 10…1500 | kg, 10–1500 | R (zapis nieprzetestowany) |  | odczyt fw: tank_cap | Potwierdzone działaniem karty |
| `0x3601` | Zbiornik – ilość paliwa [kg] | How much fuel left in tank [kg] | U16 | 0…4294967295 | kg | R (zapis nieprzetestowany) |  | zapis: set_param 47, odczyt fw: tank_kg | Potwierdzone działaniem karty |
| `0x3602` | Is fuel reserve (FW panela) | Is fuel reserve | U16 | 256…257 | flaga 0x01 + bajt: raw − 256 (zakres wartości 0…1; jeśli x10: 0…0.1) | R (zapis nieprzetestowany) |  | odczyt | (auto) flaga 0/1 (raw 256=0); zakres 256..257; sąsiedztwo: po: Zbiornik – ilość paliwa [kg] (0x3601) / FW panela: Is fuel reserve; typ u8, zakres 0…1, dostep: odczyt na zywo |
| `0x3603` | Fuel reserve [kg] (FW panela) | Fuel reserve [kg] | U16 | -2816…100 |  | R (zapis nieprzetestowany) |  | odczyt | (auto) zero; zakres -2816..100; sąsiedztwo: po: Zbiornik – ilość paliwa [kg] (0x3601) / FW panela: Fuel reserve [kg]; typ u16, zakres 0…100, domyslna 40, dostep: nastawa |
| `0x3604` | Kociol – rezerwa paliwa stop [kg] | Fuel reserve [kg] | U16 | 0…100 | liczba kg (bez flagi), 0..100 | R/W (potwierdzone zmiana na panelu i zapisem z ESP) | klucz 1 | zapis: set_param 65, odczyt | Menu → Kocioł → NASTAWY Panel 0→17: skan 0→17 (22.10 23:49); set_param 65 |
| `0x3605` | Sterowanie Lambda (0/1) | Lambda oxygen control | U16 | 256…257 | flaga: 256 = wył., 257 = wł. | R (zapis nieprzetestowany) | klucz 1 | zapis: set_param 31, odczyt fw v2.20 (menu palnika) | (auto) flaga 0/1 (raw 256=0); zakres 256..257; sąsiedztwo: po: Zbiornik – ilość paliwa [kg] (0x3601) / przed: Statystyki: licznik rozpaleń (0x3608) zmiana wył.→wł. (256→257); czujnik fizycznie niezamontowany; poziom menu: klucz 1 (PIN 0900) |
| `0x3608` | Statystyki: licznik rozpaleń | Statistics - Ignition cnt | U16 | 0…4294967295 | liczba | R (zapis nieprzetestowany) |  | odczyt karta: Statystyki | Mapowanie z fw v2.14, wartość 12894 |
| `0x3609` | Statystyki: średni czas rozpalania [s] | Statistics - Avg ignition time [s] | U16 | 0…4294967295 (licznik, bez limitu) | sekundy | R (zapis nieprzetestowany) |  | odczyt karta: Statystyki | Mapowanie z fw v2.14 |
| `0x3610` | Statistics - Avg burner power [%] (FW panela) | Statistics - Avg burner power [%] | U16 | 256…356 | flaga 0x01 + bajt: raw − 256 (zakres wartości 0…100; jeśli x10: 0…10) | R (zapis nieprzetestowany) |  | odczyt | (auto) flaga+bajt: wartość 44 (raw 300); zakres 256..356; sąsiedztwo: przed: Statystyki: czas pracy podajnika 1 [h] (0x3611) / FW panela: Statistics - Avg burner power [%]; typ u8, zakres 0…100, dostep: odczyt na zywo |
| `0x3611` | Statystyki: czas pracy podajnika 1 [h] | Feeder 1 total work time [h] | U16 | 0…4294967295 | godziny | R (zapis nieprzetestowany) |  | odczyt karta: Statystyki | Mapowanie z fw v2.14 |
| `0x3612` | Statystyki: czas pracy podajnika 2 [h] | Feeder 2 total work time [h] | U16 | 0…4294967295 | godziny | R (zapis nieprzetestowany) |  | odczyt karta: Statystyki | Mapowanie z fw v2.14 |
| `0x3613` | Average oxygen for 30% pwr [%] (FW panela) | Average oxygen for 30% pwr [%] | U16 | 256…511 | flaga 0x01 + bajt: raw − 256 (zakres wartości 0…255; jeśli x10: 0…25.5) | R (zapis nieprzetestowany) |  | odczyt | (auto) flaga 0/1 (raw 256=0); zakres 256..511; sąsiedztwo: po: Statystyki: czas pracy podajnika 2 [h] (0x3612) / FW panela: Average oxygen for 30% pwr [%]; typ u8, zakres 0…255, dostep: odczyt na zywo |
| `0x3615` | Average oxygen for 70% pwr [%] (FW panela) | Average oxygen for 70% pwr [%] | U16 | …511 |  | R (zapis nieprzetestowany) |  | odczyt | (auto) flaga 0/1 (raw 256=0); zakres ?..511; sąsiedztwo: po: Statystyki: czas pracy podajnika 2 [h] (0x3612) / przed: Statystyki: liczba czyszczeń wymiennika (0x3618) / FW panela: Average oxygen for 70% pwr [%]; typ u8, zakres 0…255, dostep: odczyt na zywo |
| `0x3616` | Average oxygen for 90% pwr [%] (FW panela) | Average oxygen for 90% pwr [%] | U16 | 256…511 | flaga 0x01 + bajt: raw − 256 (zakres wartości 0…255; jeśli x10: 0…25.5) | R (zapis nieprzetestowany) |  | odczyt | (auto) flaga 0/1 (raw 256=0); zakres 256..511; sąsiedztwo: po: Statystyki: czas pracy podajnika 2 [h] (0x3612) / przed: Statystyki: liczba czyszczeń wymiennika (0x3618) / FW panela: Average oxygen for 90% pwr [%]; typ u8, zakres 0…255, dostep: odczyt na zywo |
| `0x3618` | Statystyki: liczba czyszczeń wymiennika | Statistics - Exchanger cleaning count | U16 | 0…4294967295 | liczba | R (zapis nieprzetestowany) |  | odczyt karta: Statystyki | Mapowanie z fw v2.14 |
| `0x3619` | Statystyki: liczba przegrzań kotła | Statistics - Boiler overheat count | U16 | 0…4294967295 | liczba | R (zapis nieprzetestowany) |  | odczyt karta: Statystyki | Mapowanie z fw v2.14 |
| `0x3628` | Statistics - total energy produced [kWh] (FW panela) | Statistics - total energy produced [kWh] | U16 | 0…-1 | bez zakresu (licznik / znacznik czasu / zmienna) | R (zapis nieprzetestowany) |  | odczyt | (auto) zero; zakres 0..-1; sąsiedztwo: przed: Statystyki: liczba zaników zasilania (0x362A) / FW panela: Statistics - total energy produced [kWh]; typ u32, zakres 0…4294967295, dostep: odczyt na zywo |
| `0x3629` | Energy meter type (FW panela) | Energy meter type | U16 | 256…257 | flaga 0x01 + bajt: raw − 256 (zakres wartości 0…1; jeśli x10: 0…0.1) | R (zapis nieprzetestowany) |  | odczyt | (auto) flaga 0/1 (raw 256=0); zakres 256..257; sąsiedztwo: przed: Statystyki: liczba zaników zasilania (0x362A) / FW panela: Energy meter type; typ u8, zakres 0…2, domyslna 0, dostep: nastawa |
| `0x362A` | Statystyki: liczba zaników zasilania | Statistics - reset count | U16 | 0…4294967295 | liczba | R (zapis nieprzetestowany) |  | odczyt karta: Statystyki | Mapowanie z fw v2.14 |

### Parametry 0x3700

| Rejestr | Nazwa | Nazwa panela | Typ | Zakres | Kodowanie / jednostka | Dostęp | PIN | Gdzie w firmware / karcie | Uwagi |
|---|---|---|---|---|---|---|---|---|---|
| `0x3700` | Okres podajnika zasobnika [s] | Storage feeder period [s] | U16 | 5…180 | liczba s (5..180) | R (zapis nieprzetestowany) | klucz 2 | zapis: set_param 42, odczyt fw v2.20 (menu palnika) | (auto) liczba 20; zakres 5..180 zmiana 20→21; poziom menu: klucz 2 (PIN 0999) |
| `0x3703` | Max exhaust gas temp. [C] (FW panela) | Max exhaust gas temp. [C] | U16 | 180…280 |  | R (zapis nieprzetestowany) |  | zapis: set_param 79, odczyt | (auto) liczba 220 (jeśli /10: 22.0); zakres 180..280 / FW panela: Max exhaust gas temp. [C]; typ u16, zakres 180…280, domyslna 220, dostep: nastawa |
| `0x3704` | Moc dmuchawy rozżarzanie [%] | Blower power in incandescing [%] | U16 | 256…356 | flaga+bajt: raw−256 (0..100) | R (zapis nieprzetestowany) | klucz 1 | zapis: set_param 26, odczyt fw v2.20 (menu palnika) | (auto) flaga+bajt: wartość 50 (raw 306); zakres 256..356 zmiana 50→52 (306→308); poziom menu: klucz 1 (PIN 0900) |
| `0x3706` | Current burner power [dkW] (FW panela) | Current burner power [dkW] | U16 | 0…-1 | bez zakresu (licznik / znacznik czasu / zmienna) | R (zapis nieprzetestowany) |  | odczyt | (auto) zero; zakres 0..-1 / FW panela: Current burner power [dkW]; typ u16, zakres 0…65535, domyslna 0, dostep: odczyt na zywo |
| `0x3708` | Kociol – wybieg pompy [min] | Boiler pump overrun [min] | U16 | 256…376 | flaga+bajt: raw = 256 + min (0..120) | R/W (potwierdzone zmiana na panelu i zapisem z ESP) | klucz 1 | zapis: set_param 64, odczyt | Menu → Kocioł → NASTAWY Panel 0→13: skan 256→269 (22.10 23:49); set_param 64 |
| `0x3709` | Nominal power [kW] (FW panela) | Nominal power [kW] | U16 | 4…200 |  | R (zapis nieprzetestowany) |  | zapis: set_param 76, odczyt | (auto) liczba 18; zakres 4..200; sąsiedztwo: przed: Podawanie ręczne – czas (0x370D) / FW panela: Nominal power [kW]; typ u16, zakres 4…200, domyslna 16, dostep: nastawa |
| `0x370B` | Pod. palnika [% pod. zasobnika] | Burner feeder % of stor. feeder | U16 | 50…300 | liczba % (50..300) | R (zapis nieprzetestowany) | klucz 2 | zapis: set_param 41, odczyt fw v2.20 (menu palnika) | (auto) liczba 150 (jeśli /10: 15.0); zakres 50..300; sąsiedztwo: przed: Podawanie ręczne – czas (0x370D) zmiana 150→151; poziom menu: klucz 2 (PIN 0999) |
| `0x370D` | Podawanie ręczne – czas | Igniter preheat time [s] | U16 | 0…300 | sekundy (30) | R (zapis nieprzetestowany) |  | odczyt fw: feed_manual_run | Do weryfikacji |
| `0x370E` | Pellet predose [g] (FW panela) | Pellet predose [g] | U16 | 0…500 |  | R (zapis nieprzetestowany) |  | zapis: set_param 77, odczyt | (auto) liczba 100 (jeśli /10: 10.0); zakres 0..500; sąsiedztwo: po: Podawanie ręczne – czas (0x370D) / FW panela: Pellet predose [g]; typ u16, zakres 0…500, domyslna 100, dostep: nastawa |
| `0x3710` | Fuel consumption [Dkg/h] (FW panela) | Fuel consumption [Dkg/h] | U16 | 0…-1 | bez zakresu (licznik / znacznik czasu / zmienna) | R (zapis nieprzetestowany) |  | odczyt | (auto) zero; zakres 0..-1; sąsiedztwo: po: Podawanie ręczne – czas (0x370D) / FW panela: Fuel consumption [Dkg/h]; typ u16, zakres 0…65535, domyslna 0, dostep: odczyt na zywo |
| `0x3711` | Time to grate cleaning [min] (FW panela) | Time to grate cleaning [min] | U16 | 0…-1 | bez zakresu (licznik / znacznik czasu / zmienna) | R (zapis nieprzetestowany) |  | odczyt | (auto) liczba 180 (jeśli /10: 18.0); zakres 0..-1; sąsiedztwo: po: Podawanie ręczne – czas (0x370D) / FW panela: Time to grate cleaning [min]; typ u16, zakres 0…65535, domyslna 0, dostep: odczyt na zywo |
| `0x3715` | Czas pauzy [min] | Burner pause time [min] | U16 | 256…316 | flaga+bajt: raw−256 (0..60) | R (zapis nieprzetestowany) | klucz 1 | zapis: set_param 36, odczyt fw v2.20 (menu palnika) | (auto) flaga 0/1 (raw 256=0); zakres 256..316 zmiana 0→2 (256→258); poziom menu: klucz 1 (PIN 0900) |
| `0x3716` | Moc w pauzie [%] | Burner pause power [%] | U16 | 261…286 | flaga+bajt: raw−256 (5..30) | R (zapis nieprzetestowany) | klucz 1 | zapis: set_param 37, odczyt fw v2.20 (menu palnika) | (auto) flaga+bajt: wartość 10 (raw 266); zakres 261..286 zmiana 10→12 (266→268); poziom menu: klucz 1 (PIN 0900) |
| `0x3717` | Dmuchawa w pauzie [%] | Burner pause blower power [%] | U16 | 266…306 | flaga+bajt: raw−256 (10..50) | R (zapis nieprzetestowany) | klucz 1 | zapis: set_param 38, odczyt fw v2.20 (menu palnika) | (auto) flaga+bajt: wartość 20 (raw 276); zakres 266..306 zmiana 20→22 (276→278); poziom menu: klucz 1 (PIN 0900) |
| `0x3720` | Outside temp. averaging period [h] (FW panela) | Outside temp. averaging period [h] | U16 | 256…304 | flaga 0x01 + bajt: raw − 256 (zakres wartości 0…48; jeśli x10: 0…4.8) | R (zapis nieprzetestowany) |  | odczyt | (auto) flaga 0/1 (raw 256=0); zakres 256..304 / FW panela: Outside temp. averaging period [h]; typ u8, zakres 0…48, domyslna 12, dostep: nastawa |

### Pomiary, alarmy

| Rejestr | Nazwa | Nazwa panela | Typ | Zakres | Kodowanie / jednostka | Dostęp | PIN | Gdzie w firmware / karcie | Uwagi |
|---|---|---|---|---|---|---|---|---|---|
| `0x4000` | Temperatura powrotu (pomiar) | Boiler return temp [dC] | U16 | 0…1500 | raw/10 °C | R (zapis nieprzetestowany) |  | odczyt fw v2.17: return_temp; karta: temperatura powrotu | Potwierdzone porównaniem z panelem (51,4/51,9/52/52,1/52,3) |
| `0x4001` | CO 1 – temperatura (pomiar) | CH temp measured | U16 | -100…1500 | raw/10 °C | R |  | odczyt fw: ch1_temp | Odczyt |
| `0x4002` | CO 2 – temperatura (pomiar) | - | U16 | -100…1500 | raw/10 °C (wartość śmieciowa: brak czujnika) | R (zapis nieprzetestowany) |  | odczyt fw: ch2_temp | Brak drugiego obiegu / w firmware wyłączone (dwa_obiegi_co: false) |
| `0x4005` | Moc palnika [%] | Burner power [%] | U16 | 0…100 | 0–100 % | R |  | odczyt fw: burner_power; karta: moc[%] | Odczyt Moc palnika [%] = moc[%] na ekranie Palnik (potwierdzone 22:11: panel 47, sensor 46) |
| `0x4010` | Alarm 0 – kod i flagi | Alarm register | U16 | 0…4294967295 | bity 0–15 kod, bit 16 aktywny, bit 17 potwierdzony | R/W (zapis tylko bitu 18 = żądanie potwierdzenia alarmu) |  | odczyt (historia alarmow) fw: alarm; karta: Alarmy (kody w tabeli ALARM_PL) | Zapis potwierdzenia działał; bit 18 wg SDO_SCADA: [18] alarm confirm request; firmware: przycisk „Potwierdz alarm” zapisuje do rejestru najnowszego alarmu (0x4010+slot); opisy kodów: pelletcan-alarmy-kody.csv |
| `0x4011` | Alarm 1 – kod i flagi | - | U16 | 0…4294967295 | bity 0–15 kod, bit 16 aktywny, bit 17 potwierdzony | R/W (zapis tylko bitu 18 = żądanie potwierdzenia alarmu) |  | odczyt (historia alarmow) fw: alarm; karta: Alarmy (kody w tabeli ALARM_PL) | Zapis potwierdzenia działał; bit 18 wg SDO_SCADA: [18] alarm confirm request; firmware: przycisk „Potwierdz alarm” zapisuje do rejestru najnowszego alarmu (0x4010+slot); opisy kodów: pelletcan-alarmy-kody.csv |
| `0x4012` | Alarm 2 – kod i flagi | - | U16 | 0…4294967295 | bity 0–15 kod, bit 16 aktywny, bit 17 potwierdzony | R/W (zapis tylko bitu 18 = żądanie potwierdzenia alarmu) |  | odczyt (historia alarmow) fw: alarm; karta: Alarmy (kody w tabeli ALARM_PL) | Zapis potwierdzenia działał; bit 18 wg SDO_SCADA: [18] alarm confirm request; firmware: przycisk „Potwierdz alarm” zapisuje do rejestru najnowszego alarmu (0x4010+slot); opisy kodów: pelletcan-alarmy-kody.csv |
| `0x4013` | Alarm 3 – kod i flagi | - | U16 | 0…4294967295 | bity 0–15 kod, bit 16 aktywny, bit 17 potwierdzony | R/W (zapis tylko bitu 18 = żądanie potwierdzenia alarmu) |  | odczyt (historia alarmow) fw: alarm; karta: Alarmy (kody w tabeli ALARM_PL) | Zapis potwierdzenia działał; bit 18 wg SDO_SCADA: [18] alarm confirm request; firmware: przycisk „Potwierdz alarm” zapisuje do rejestru najnowszego alarmu (0x4010+slot); opisy kodów: pelletcan-alarmy-kody.csv |
| `0x4014` | Alarm 4 – kod i flagi | - | U16 | 0…4294967295 | bity 0–15 kod, bit 16 aktywny, bit 17 potwierdzony | R/W (zapis tylko bitu 18 = żądanie potwierdzenia alarmu) |  | odczyt (historia alarmow) fw: alarm; karta: Alarmy (kody w tabeli ALARM_PL) | Zapis potwierdzenia działał; bit 18 wg SDO_SCADA: [18] alarm confirm request; firmware: przycisk „Potwierdz alarm” zapisuje do rejestru najnowszego alarmu (0x4010+slot); opisy kodów: pelletcan-alarmy-kody.csv |
| `0x4015` | Alarm 5 – kod i flagi | - | U16 | 0…4294967295 | bity 0–15 kod, bit 16 aktywny, bit 17 potwierdzony | R/W (zapis tylko bitu 18 = żądanie potwierdzenia alarmu) |  | odczyt (historia alarmow) fw: alarm; karta: Alarmy (kody w tabeli ALARM_PL) | Zapis potwierdzenia działał; bit 18 wg SDO_SCADA: [18] alarm confirm request; firmware: przycisk „Potwierdz alarm” zapisuje do rejestru najnowszego alarmu (0x4010+slot); opisy kodów: pelletcan-alarmy-kody.csv |
| `0x4016` | Alarm 6 – kod i flagi | - | U16 | 0…4294967295 | bity 0–15 kod, bit 16 aktywny, bit 17 potwierdzony | R/W (zapis tylko bitu 18 = żądanie potwierdzenia alarmu) |  | odczyt (historia alarmow) fw: alarm; karta: Alarmy (kody w tabeli ALARM_PL) | Zapis potwierdzenia działał; bit 18 wg SDO_SCADA: [18] alarm confirm request; firmware: przycisk „Potwierdz alarm” zapisuje do rejestru najnowszego alarmu (0x4010+slot); opisy kodów: pelletcan-alarmy-kody.csv |
| `0x4017` | Alarm 7 – kod i flagi | - | U16 | 0…4294967295 | bity 0–15 kod, bit 16 aktywny, bit 17 potwierdzony | R/W (zapis tylko bitu 18 = żądanie potwierdzenia alarmu) |  | odczyt (historia alarmow) fw: alarm; karta: Alarmy (kody w tabeli ALARM_PL) | Zapis potwierdzenia działał; bit 18 wg SDO_SCADA: [18] alarm confirm request; firmware: przycisk „Potwierdz alarm” zapisuje do rejestru najnowszego alarmu (0x4010+slot); opisy kodów: pelletcan-alarmy-kody.csv |
| `0x4018` | Alarm 8 – kod i flagi | - | U16 | 0…4294967295 | bity 0–15 kod, bit 16 aktywny, bit 17 potwierdzony | R/W (zapis tylko bitu 18 = żądanie potwierdzenia alarmu) |  | odczyt (historia alarmow) fw: alarm; karta: Alarmy (kody w tabeli ALARM_PL) | Zapis potwierdzenia działał; bit 18 wg SDO_SCADA: [18] alarm confirm request; firmware: przycisk „Potwierdz alarm” zapisuje do rejestru najnowszego alarmu (0x4010+slot); opisy kodów: pelletcan-alarmy-kody.csv |
| `0x4019` | Alarm 9 – kod i flagi | - | U16 | 0…4294967295 | bity 0–15 kod, bit 16 aktywny, bit 17 potwierdzony | R/W (zapis tylko bitu 18 = żądanie potwierdzenia alarmu) |  | odczyt (historia alarmow) fw: alarm; karta: Alarmy (kody w tabeli ALARM_PL) | Zapis potwierdzenia działał; bit 18 wg SDO_SCADA: [18] alarm confirm request; firmware: przycisk „Potwierdz alarm” zapisuje do rejestru najnowszego alarmu (0x4010+slot); opisy kodów: pelletcan-alarmy-kody.csv |
| `0x401A` | Alarm 10 – kod i flagi | - | U16 | 0…4294967295 | bity 0–15 kod, bit 16 aktywny, bit 17 potwierdzony | R/W (zapis tylko bitu 18 = żądanie potwierdzenia alarmu) |  | odczyt (historia alarmow) fw: alarm; karta: Alarmy (kody w tabeli ALARM_PL) | Zapis potwierdzenia działał; bit 18 wg SDO_SCADA: [18] alarm confirm request; firmware: przycisk „Potwierdz alarm” zapisuje do rejestru najnowszego alarmu (0x4010+slot); opisy kodów: pelletcan-alarmy-kody.csv |
| `0x401B` | Alarm 11 – kod i flagi | - | U16 | 0…4294967295 | bity 0–15 kod, bit 16 aktywny, bit 17 potwierdzony | R/W (zapis tylko bitu 18 = żądanie potwierdzenia alarmu) |  | odczyt (historia alarmow) fw: alarm; karta: Alarmy (kody w tabeli ALARM_PL) | Zapis potwierdzenia działał; bit 18 wg SDO_SCADA: [18] alarm confirm request; firmware: przycisk „Potwierdz alarm” zapisuje do rejestru najnowszego alarmu (0x4010+slot); opisy kodów: pelletcan-alarmy-kody.csv |
| `0x401C` | Alarm 12 – kod i flagi | - | U16 | 0…4294967295 | bity 0–15 kod, bit 16 aktywny, bit 17 potwierdzony | R/W (zapis tylko bitu 18 = żądanie potwierdzenia alarmu) |  | odczyt (historia alarmow) fw: alarm; karta: Alarmy (kody w tabeli ALARM_PL) | Zapis potwierdzenia działał; bit 18 wg SDO_SCADA: [18] alarm confirm request; firmware: przycisk „Potwierdz alarm” zapisuje do rejestru najnowszego alarmu (0x4010+slot); opisy kodów: pelletcan-alarmy-kody.csv |
| `0x401D` | Alarm 13 – kod i flagi | - | U16 | 0…4294967295 | bity 0–15 kod, bit 16 aktywny, bit 17 potwierdzony | R/W (zapis tylko bitu 18 = żądanie potwierdzenia alarmu) |  | odczyt (historia alarmow) fw: alarm; karta: Alarmy (kody w tabeli ALARM_PL) | Zapis potwierdzenia działał; bit 18 wg SDO_SCADA: [18] alarm confirm request; firmware: przycisk „Potwierdz alarm” zapisuje do rejestru najnowszego alarmu (0x4010+slot); opisy kodów: pelletcan-alarmy-kody.csv |
| `0x401E` | Alarm 14 – kod i flagi | - | U16 | 0…4294967295 | bity 0–15 kod, bit 16 aktywny, bit 17 potwierdzony | R/W (zapis tylko bitu 18 = żądanie potwierdzenia alarmu) |  | odczyt (historia alarmow) fw: alarm; karta: Alarmy (kody w tabeli ALARM_PL) | Zapis potwierdzenia działał; bit 18 wg SDO_SCADA: [18] alarm confirm request; firmware: przycisk „Potwierdz alarm” zapisuje do rejestru najnowszego alarmu (0x4010+slot); opisy kodów: pelletcan-alarmy-kody.csv |
| `0x401F` | Alarm 15 – kod i flagi | - | U16 | 0…4294967295 | bity 0–15 kod, bit 16 aktywny, bit 17 potwierdzony | R/W (zapis tylko bitu 18 = żądanie potwierdzenia alarmu) |  | odczyt (historia alarmow) fw: alarm; karta: Alarmy (kody w tabeli ALARM_PL) | Zapis potwierdzenia działał; bit 18 wg SDO_SCADA: [18] alarm confirm request; firmware: przycisk „Potwierdz alarm” zapisuje do rejestru najnowszego alarmu (0x4010+slot); opisy kodów: pelletcan-alarmy-kody.csv |
| `0x4020` | Alarm 16 – kod i flagi | - | U16 | 0…4294967295 | bity 0–15 kod, bit 16 aktywny, bit 17 potwierdzony | R/W (zapis tylko bitu 18 = żądanie potwierdzenia alarmu) |  | odczyt (historia alarmow) fw: alarm; karta: Alarmy (kody w tabeli ALARM_PL) | Zapis potwierdzenia działał; bit 18 wg SDO_SCADA: [18] alarm confirm request; firmware: przycisk „Potwierdz alarm” zapisuje do rejestru najnowszego alarmu (0x4010+slot); opisy kodów: pelletcan-alarmy-kody.csv |
| `0x4021` | Alarm 17 – kod i flagi | - | U16 | 0…4294967295 | bity 0–15 kod, bit 16 aktywny, bit 17 potwierdzony | R/W (zapis tylko bitu 18 = żądanie potwierdzenia alarmu) |  | odczyt (historia alarmow) fw: alarm; karta: Alarmy (kody w tabeli ALARM_PL) | Zapis potwierdzenia działał; bit 18 wg SDO_SCADA: [18] alarm confirm request; firmware: przycisk „Potwierdz alarm” zapisuje do rejestru najnowszego alarmu (0x4010+slot); opisy kodów: pelletcan-alarmy-kody.csv |
| `0x4022` | Alarm 18 – kod i flagi | - | U16 | 0…4294967295 | bity 0–15 kod, bit 16 aktywny, bit 17 potwierdzony | R/W (zapis tylko bitu 18 = żądanie potwierdzenia alarmu) |  | odczyt (historia alarmow) fw: alarm; karta: Alarmy (kody w tabeli ALARM_PL) | Zapis potwierdzenia działał; bit 18 wg SDO_SCADA: [18] alarm confirm request; firmware: przycisk „Potwierdz alarm” zapisuje do rejestru najnowszego alarmu (0x4010+slot); opisy kodów: pelletcan-alarmy-kody.csv |
| `0x4023` | Alarm 19 – kod i flagi | - | ? | 0…4294967295 | bity 0–15 kod, bit 16 aktywny, bit 17 potwierdzony | R/W (zapis tylko bitu 18 = żądanie potwierdzenia alarmu) |  | odczyt (historia alarmow) fw: alarm; karta: Alarmy (kody w tabeli ALARM_PL) | Zapis potwierdzenia działał; bit 18 wg SDO_SCADA: [18] alarm confirm request; firmware: przycisk „Potwierdz alarm” zapisuje do rejestru najnowszego alarmu (0x4010+slot); opisy kodów: pelletcan-alarmy-kody.csv |
| `0x4024` | Alarm 0 – czas początku | Alarm date timestamp | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_start | Odczyt |
| `0x4025` | Alarm 1 – czas początku | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_start | Odczyt |
| `0x4026` | Alarm 2 – czas początku | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_start | Odczyt |
| `0x4027` | Alarm 3 – czas początku | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_start | Odczyt |
| `0x4028` | Alarm 4 – czas początku | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_start | Odczyt |
| `0x4029` | Alarm 5 – czas początku | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_start | Odczyt |
| `0x402A` | Alarm 6 – czas początku | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_start | Odczyt |
| `0x402B` | Alarm 7 – czas początku | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_start | Odczyt |
| `0x402C` | Alarm 8 – czas początku | - |  | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_start | Odczyt |
| `0x402D` | Alarm 9 – czas początku | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_start | Odczyt |
| `0x402E` | Alarm 10 – czas początku | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_start | Odczyt |
| `0x402F` | Alarm 11 – czas początku | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_start | Odczyt |
| `0x4030` | Alarm 12 – czas początku | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_start | Odczyt |
| `0x4031` | Alarm 13 – czas początku | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_start | Odczyt |
| `0x4032` | Alarm 14 – czas początku | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_start | Odczyt |
| `0x4033` | Alarm 15 – czas początku | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_start | Odczyt |
| `0x4034` | Alarm 16 – czas początku | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_start | Odczyt |
| `0x4035` | Alarm 17 – czas początku | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_start | Odczyt |
| `0x4036` | Alarm 18 – czas początku | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_start | Odczyt |
| `0x4037` | Alarm 19 – czas początku | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_start | Odczyt |
| `0x4038` | Alarm 0 – czas końca | Alarm confirm timestamp | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_end | Odczyt |
| `0x4039` | Alarm 1 – czas końca | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_end | Odczyt |
| `0x403A` | Alarm 2 – czas końca | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_end | Odczyt |
| `0x403B` | Alarm 3 – czas końca | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_end | Odczyt |
| `0x403C` | Alarm 4 – czas końca | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_end | Odczyt |
| `0x403D` | Alarm 5 – czas końca | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_end | Odczyt |
| `0x403E` | Alarm 6 – czas końca | - |  | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_end | Odczyt |
| `0x403F` | Alarm 7 – czas końca | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_end | Odczyt |
| `0x4040` | Alarm 8 – czas końca | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_end | Odczyt |
| `0x4041` | Alarm 9 – czas końca | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_end | Odczyt |
| `0x4042` | Alarm 10 – czas końca | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_end | Odczyt |
| `0x4043` | Alarm 11 – czas końca | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_end | Odczyt |
| `0x4044` | Alarm 12 – czas końca | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_end | Odczyt |
| `0x4045` | Alarm 13 – czas końca | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_end | Odczyt |
| `0x4046` | Alarm 14 – czas końca | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_end | Odczyt |
| `0x4047` | Alarm 15 – czas końca | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_end | Odczyt |
| `0x4048` | Alarm 16 – czas końca | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_end | Odczyt |
| `0x4049` | Alarm 17 – czas końca | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_end | Odczyt |
| `0x404A` | Alarm 18 – czas końca | - | U16 | 0…4294967295 | znacznik czasu Unix (s od 1970) | R |  | odczyt (historia alarmow) fw: alarm_end | Odczyt |
| `0x404B` | - | - | U16 | 0…-1 | bez zakresu (licznik / znacznik czasu / zmienna) | R (zapis nieprzetestowany) |  | odczyt (historia alarmow) | (auto) znacznik czasu Unix 2026-08-12 21:40 UTC; zakres 0..-1; sąsiedztwo: po: Alarm 18 – czas końca (0x404A) / przed: Alarmy: następna pozycja bufora (0x404C) |
| `0x404C` | Alarmy: następna pozycja bufora | Alarm next index | U16 | 256…275 | 256 + pozycja 0–19; najnowszy = pozycja − 1 | R |  | odczyt (historia alarmow) fw: alarm_pos | Odczyt |
| `0x404D` | Alarmy: liczba alarmów | Number of alarms | U16 | 256…276 | 256 + liczba? | R (zapis nieprzetestowany) |  | odczyt fw: log | Tylko w logu |

## 4. Parametry z binarki panela, jeszcze niewykorzystane (269)

Pełna lista z firmware panela FW2213TK. „Na kotle” = czy rejestr odpowiedział w skanie 6.11.2026 (sub 1). Wartość surowa tylko dla 197 rejestrów ze snapa bazowego. To jest **materiał do dalszej pracy**: wybierz pozycję, sprawdź na panelu, podepnij w firmware (instrukcja w [README.md](README.md)).

| Rejestr | ID | Nazwa z FW panela | Typ | Min | Max | Domyślna | Dostęp panela | Na kotle | Wartość surowa | Status w katalogu |
|---|---|---|---|---|---|---|---|---|---|---|
| `0x0003` | 3 | Language | u8 | 0 | 30 | 0 | nastawa | nie sprawdzono |  | NAZWA Z FW PANELA |
| `0x0004` | 4 | Parameters set Number | u16 | 0 | 65535 | 10 | nastawa | nie sprawdzono |  | NAZWA Z FW PANELA |
| `0x0005` | 5 | Default settings request | u8 | 0 | 1 | 1 | nastawa | nie sprawdzono |  | NAZWA Z FW PANELA |
| `0x200A` | 8202 | Remote boiler 1 temp[dC] | s16 | 0 | 1500 | 0 | live (odczyt) | tak | 19990 | NAZWA Z FW PANELA |
| `0x200B` | 8203 | Remote boiler 2 temp[dC] | s16 | 0 | 1500 | 0 | live (odczyt) | nie |  | NAZWA Z FW PANELA |
| `0x200C` | 8204 | Remote boiler 3 temp[dC] | s16 | 0 | 1500 | 0 | live (odczyt) | tak | 19990 | NAZWA Z FW PANELA |
| `0x200D` | 8205 | Remote boiler 1 requested temp[C] | u16 | 0 | 255 | 0 | live (odczyt) | tak | 0 | NAZWA Z FW PANELA |
| `0x200E` | 8206 | Remote boiler 2 requested temp[C] | u16 | 0 | 255 | 0 | live (odczyt) | tak | 0 | NAZWA Z FW PANELA |
| `0x200F` | 8207 | Remote boiler 3 requested temp[C] | u16 | 0 | 255 | 0 | live (odczyt) | tak | 0 | NAZWA Z FW PANELA |
| `0x2016` | 8214 | Room measured temp | s16 | -100 | 1500 | 0 | live (odczyt) | tak | 0 | NAZWA Z FW PANELA |
| `0x2101` | 8449 | Solar power [W] | u16 | 0 | 10000 |  | live (odczyt) | nie |  | NAZWA Z FW PANELA |
| `0x2102` | 8450 | Solar temperature 2 [C] | s16 | 0 | 1500 |  | live (odczyt) | nie |  | NAZWA Z FW PANELA |
| `0x2103` | 8451 | Solar temperature 3 [C] | s16 | 0 | 1500 |  | live (odczyt) | nie |  | NAZWA Z FW PANELA |
| `0x2104` | 8452 | Solar temperature 4 [C] | s16 | 0 | 1500 |  | live (odczyt) | tak | 0 | NAZWA Z FW PANELA |
| `0x2105` | 8453 | Heating configuration | u8 | 0 | 4 | 1 | nastawa | tak | 257 | NAZWA Z FW PANELA |
| `0x2109` | 8457 | Solar temperature 1 [C] | s16 | 0 | 1500 |  | live (odczyt) | tak | 0 | NAZWA Z FW PANELA |
| `0x2111` | 8465 | Hot water 1 needed temp. [C] | u16 | 0 | 150 | 0 | live (odczyt) | tak | 60 | NAZWA Z FW PANELA |
| `0x2112` | 8466 | Buffer top measured temperature | s16 | 0 | 1500 | 0 | live (odczyt) | tak | 0 | NAZWA Z FW PANELA |
| `0x2113` | 8467 | Buffer bottom measured temperature | s16 | 0 | 1500 | 0 | live (odczyt) | tak | 0 | NAZWA Z FW PANELA |
| `0x2114` | 8468 | Buffer top set temperature | u16 | 7 | 80 | 45 | nastawa | tak | 45 | NAZWA Z FW PANELA |
| `0x2115` | 8469 | Buffer bottom set temperature | u16 | 7 | 80 | 65 | nastawa | tak | 65 | NAZWA Z FW PANELA |
| `0x2116` | 8470 | Solar flow [l/min] | s16 | 7 | 200 | 40 | nastawa | tak | 40 | NAZWA Z FW PANELA |
| `0x2119` | 8473 | Exhaust gas temperature (2) [C] | s16 | -50 | 350 | 0 | live (odczyt) | tak | 0 | NAZWA Z FW PANELA |
| `0x2120` | 8480 | Lambda oxygen [%] | u16 | 0 | 65535 | 0 | live (odczyt) | tak | 0 | NAZWA Z FW PANELA |
| `0x2122` | 8482 | Compatibility igneo solar pump state | u32 | 0 | 4294967295 |  | live (odczyt) | nie sprawdzono |  | NAZWA Z FW PANELA |
| `0x2124` | 8484 | Total fuel counter[hg] | u32 | 0 | 4294967295 | 0 | nastawa | nie sprawdzono |  | NAZWA Z FW PANELA |
| `0x2125` | 8485 | Device type | u32 | 0 | 4294967295 | 1000070001 | live (odczyt) | nie sprawdzono |  | NAZWA Z FW PANELA |
| `0x214A` | 8522 | CH mixer test | u8 | 0 | 2 | 0 | komenda | tak | 256 | NAZWA Z FW PANELA |
| `0x2151` | 8529 | Grate silence mode | u8 | 0 | 1 | 0 | nastawa | tak | 256 | NAZWA Z FW PANELA |
| `0x215B` | 8539 | Airflow speed for 100% of power [m/s] | u16 | 10 | 500 | 150 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x2160` | 8544 | Hot water 1 schedule sunday | u32 | 0 | 16777215 | 4194240 | nastawa | nie |  | POTWIERDZONY |
| `0x2161` | 8545 | Weather forecast 0 | u16 | 0 | 65535 |  | komenda | nie sprawdzono |  | NAZWA Z FW PANELA |
| `0x2162` | 8546 | Weather forecast 1 | u16 | 0 | 65535 |  | komenda | nie sprawdzono |  | NAZWA Z FW PANELA |
| `0x2163` | 8547 | Weather forecast 2 | u16 | 0 | 65535 |  | komenda | nie sprawdzono |  | NAZWA Z FW PANELA |
| `0x2164` | 8548 | Weather validity left time [min] | u8 | 0 | 255 |  | komenda | tak | 256 | NAZWA Z FW PANELA |
| `0x2165` | 8549 | Compatibility timestamp | u32 | 0 | 4294967295 |  | komenda | nie sprawdzono |  | NAZWA Z FW PANELA |
| `0x2166` | 8550 | CH res [dC] | s16 | 0 | 500 |  | komenda | tak | 300 | NAZWA Z FW PANELA |
| `0x216A` | 8554 | Exchanger cleaning request | u8 | 0 | 1 | 0 | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x216B` | 8555 | Exchanger silence mode | u8 | 0 | 1 | 0 | nastawa | tak | 256 | NAZWA Z FW PANELA |
| `0x216F` | 8559 | CH mixer state | u8 | 0 | 2 | 0 | live (odczyt) | tak | 256 | NIEPOTWIERDZONY |
| `0x2170` | 8560 | VideRoom PIN | u16 | 0 | 65535 |  | live (odczyt) | nie sprawdzono |  | TYLKO W FW PANELA |
| `0x218A` | 8586 | Is grate cleaning on | u8 | 0 | 1 | 0 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x2211` | 8721 |  | u16 | 0 | 150 | 0 | live (odczyt) | tak | 7 | NAZWA Z FW PANELA |
| `0x2251` | 8785 | Burner storage feeder | u8 | 0 | 100 | 0 | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x2252` | 8786 | Burner burner feeder | u8 | 0 | 100 | 0 | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x225A` | 8794 | Pwr reg. speed | u8 | 2 | 30 | 10 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x2260` | 8800 | Burner storage feeder work time during refuling [s] | u16 | 0 | 3600 | 30 | live (odczyt) | nie sprawdzono |  | NAZWA Z FW PANELA |
| `0x2266` | 8806 | Refueling need request | u8 | 0 | 1 | 0 | komenda | tak | 256 | NAZWA Z FW PANELA |
| `0x2276` | 8822 | Grate move indicator | u8 | 0 | 2 | 0 | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x2277` | 8823 | Boiler pump state | u8 | 0 | 1 | 0 | live (odczyt) | tak | 257 | NAZWA Z FW PANELA |
| `0x2279` | 8825 | Burner grate test | u8 | 0 | 2 | 0 | komenda | tak | 256 | POTWIERDZONY |
| `0x227B` | 8827 | Pwr reg. Kp | u16 | 0 | 2000 | 60 | nastawa | nie sprawdzono |  | TYLKO W FW PANELA |
| `0x227C` | 8828 | Pwr reg. Ki | u16 | 0 | 2000 | 8 | nastawa | nie sprawdzono |  | TYLKO W FW PANELA |
| `0x227D` | 8829 | Pwr reg. Kd | u16 | 0 | 10000 | 400 | nastawa | nie sprawdzono |  | TYLKO W FW PANELA |
| `0x227E` | 8830 | Pwr reg. Ki 2 | u16 | 0 | 2000 | 40 | nastawa | nie sprawdzono |  | TYLKO W FW PANELA |
| `0x227F` | 8831 | Pwr reg. Kd 2 | u16 | 0 | 10000 | 1400 | nastawa | nie sprawdzono |  | TYLKO W FW PANELA |
| `0x2280` | 8832 | Buffer top set temperature | u16 | 25 | 80 | 0 | live (odczyt) | tak | 0 | NAZWA Z FW PANELA |
| `0x2281` | 8833 | Buffer minimal pump temperature | u8 | 15 | 60 | 25 | nastawa | tak | 281 | NAZWA Z FW PANELA |
| `0x2282` | 8834 | Buffer is automatic top temperature | u8 | 0 | 1 | 0 | nastawa | tak | 256 | NAZWA Z FW PANELA |
| `0x2285` | 8837 | Exchanger cleaner test | u8 | 0 | 2 | 0 | komenda | tak | 367 | NAZWA Z FW PANELA |
| `0x2286` | 8838 | Boiler pump test | u8 | 0 | 2 | 0 | komenda | nie |  | POTWIERDZONY |
| `0x2288` | 8840 | Blower test power | u8 | 0 | 100 | 100 | komenda | tak | 260 | NAZWA Z FW PANELA |
| `0x228A` | 8842 | Pwr reg. Kp 2 | u16 | 0 | 2000 | 150 | nastawa | nie sprawdzono |  | TYLKO W FW PANELA |
| `0x228B` | 8843 | Grate full move time [s] | u16 | 3 | 500 | 120 | nastawa | nie sprawdzono |  | NAZWA Z FW PANELA |
| `0x2293` | 8851 | Exhaust fan test | u8 | 0 | 2 | 0 | komenda | tak | 256 | POTWIERDZONY |
| `0x2294` | 8852 | User fuel counter[kg] | u16 | 0 | 65535 | 0 | nastawa | nie sprawdzono |  | NAZWA Z FW PANELA |
| `0x2298` | 8856 | Exhaust fan test power | u8 | 0 | 100 | 50 | komenda | tak | 275 | POTWIERDZONY |
| `0x229D` | 8861 | CH pump test | u8 | 0 | 2 | 0 | komenda | nie |  | POTWIERDZONY |
| `0x22F5` | 8949 | CH needed temp. [C] | u16 | 0 | 150 |  | live (odczyt) | tak | 29 | NAZWA Z FW PANELA |
| `0x22FD` | 8957 | CH status | u8 | 0 | 255 |  | live (odczyt) | nie |  | NAZWA Z FW PANELA |
| `0x2305` | 8965 | CH room set temp. adjustment [dC] | s16 | -110 | 40 |  | komenda | nie sprawdzono |  | NAZWA Z FW PANELA |
| `0x2309` | 8969 | Room temp. radio sensor batt. volt [mV] | u16 | 0 | 65535 |  | live (odczyt) | tak | 0 | NAZWA Z FW PANELA |
| `0x230D` | 8973 | Room temp. radio sensor signal [%] | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x2311` | 8977 | Room temp. radio sensor time since lasr rec. | u16 | 0 | 65535 |  | live (odczyt) | nie |  | NAZWA Z FW PANELA |
| `0x2315` | 8981 | Automatic summer recognition | u8 | 0 | 1 | 1 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x2319` | 8985 | Room temp. radio sensor soft. ver. before dot | u8 | 0 | 255 |  | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x231D` | 8989 | Room temp. radio sensor soft. ver. after dot | u8 | 0 | 255 |  | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x2321` | 8993 | CH circuit name part1 | u32 | 0 | 4294967295 | 0 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x2325` | 8997 | CH circuit name part2 | u32 | 0 | 4294967295 | 0 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x2329` | 9001 | CH circuit name part3 | u32 | 0 | 4294967295 | 0 | nastawa | nie sprawdzono |  | TYLKO W FW PANELA |
| `0x299B` | 10651 |  | u8 | 0 | 30 | 20 | nastawa | tak | 276 | NAZWA Z FW PANELA |
| `0x299C` | 10652 | Burner blower RPM | u16 | 0 | 65535 | 0 | live (odczyt) | tak | 0 | NAZWA Z FW PANELA |
| `0x299F` | 10655 | Burning type | u8 | 0 | 2 | 0 | nastawa | tak | 256 | NAZWA Z FW PANELA |
| `0x3000` | 12288 | Modulation blower power on wood [%] | u8 | 10 | 100 | 70 | nastawa | tak | 326 | NAZWA Z FW PANELA |
| `0x3001` | 12289 | Start burning wood | u8 | 0 | 1 |  | komenda | tak | 256 | NAZWA Z FW PANELA |
| `0x3004` | 12292 | Virt. energy consumer requested temp [C] | u8 | 7 | 150 | 7 | komenda | nie sprawdzono |  | NAZWA Z FW PANELA |
| `0x3005` | 12293 | Fireup blower power on wood [%] | u8 | 5 | 100 | 20 | nastawa | tak | 276 | NAZWA Z FW PANELA |
| `0x3006` | 12294 | Incandescing blower power on wood [%] | u8 | 1 | 100 | 30 | nastawa | tak | 286 | NAZWA Z FW PANELA |
| `0x3007` | 12295 | Pause blower power on wood [%] | u8 | 0 | 100 | 20 | nastawa | tak | 276 | NAZWA Z FW PANELA |
| `0x3008` | 12296 | Sec. air modulation MIN [%] | u8 | 1 | 100 | 20 | nastawa | tak | 276 | NAZWA Z FW PANELA |
| `0x3009` | 12297 | Sec. air modulation MAX [%] | u8 | 1 | 100 | 80 | nastawa | tak | 336 | NAZWA Z FW PANELA |
| `0x300A` | 12298 | Sec. air mixer position [%] | u8 | 0 | 100 | 0 | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x300B` | 12299 | Stop burning wood | u8 | 0 | 1 |  | komenda | tak | 257 | NAZWA Z FW PANELA |
| `0x300F` | 12303 | Virt. consumer maximal power | u8 | 0 | 100 | 100 | komenda | nie sprawdzono |  | NAZWA Z FW PANELA |
| `0x3010` | 12304 | Grate move interval in modulation [kg] | u8 | 1 | 20 | 5 | nastawa | tak | 261 | NAZWA Z FW PANELA |
| `0x3011` | 12305 | Burner pwr. depend of buf. energy level | u8 | 0 | 1 | 0 | nastawa | tak | 256 | NAZWA Z FW PANELA |
| `0x3012` | 12306 | Grate move interval in modulation [min] | u16 | 1 | 720 | 10 | nastawa | tak | 10 | NAZWA Z FW PANELA |
| `0x3013` | 12307 | Burner blower max RPM | u16 | 500 | 5000 | 2750 | nastawa | nie sprawdzono |  | TYLKO W FW PANELA |
| `0x3116` | 12566 | Solar delta on [C] | u8 | 0 | 20 | 3 | nastawa | tak | 259 | NAZWA Z FW PANELA |
| `0x3117` | 12567 | Solar delta off [C] | u8 | 0 | 10 | 2 | nastawa | tak | 258 | NAZWA Z FW PANELA |
| `0x3118` | 12568 | Solar liquid specific heat [kJ/(kg * C)] | u16 | 15 | 60 | 25 | nastawa | nie |  | NAZWA Z FW PANELA |
| `0x3119` | 12569 | Solar temperature water max [C] | s16 | 70 | 95 | 70 | nastawa | tak | 70 | NAZWA Z FW PANELA |
| `0x311A` | 12570 | Solar temperature alarm max[C] | s16 | 90 | 145 | 90 | nastawa | tak | 90 | NAZWA Z FW PANELA |
| `0x311B` | 12571 | Solar temperature alarm min[C] | s16 | -40 | 0 | -34 | nastawa | tak | 65502 | NAZWA Z FW PANELA |
| `0x311C` | 12572 | Solar pump state | u8 | 0 | 1 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x311F` | 12575 | Solar pump test | u8 | 0 | 2 | 0 | komenda | nie sprawdzono |  | POTWIERDZONY |
| `0x3120` | 12576 | Solar status | u8 | 0 | 1 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x3121` | 12577 | Exchanger cleaning duration [s] | u16 | 5 | 30 | 15 | nastawa | tak | 0 | NAZWA Z FW PANELA |
| `0x3123` | 12579 |  | u8 | 0 | 1 | 0 | nastawa | tak | 256 | NAZWA Z FW PANELA |
| `0x3124` | 12580 |  | u8 | 0 | 1 | 0 | nastawa | tak | 256 | NAZWA Z FW PANELA |
| `0x3125` | 12581 |  | u32 | 0 | 4294967295 | 0 | nastawa | nie sprawdzono |  | NAZWA Z FW PANELA |
| `0x3126` | 12582 |  | u32 | 0 | 4294967295 | 0 | nastawa | nie sprawdzono |  | NAZWA Z FW PANELA |
| `0x3127` | 12583 | Clean burner monit period [kg] | u16 | 0 | 65535 | 300 | live (odczyt) | nie sprawdzono |  | NAZWA Z FW PANELA |
| `0x3128` | 12584 | Clean exchanger monit period [kg] | u16 | 0 | 65535 | 1500 | live (odczyt) | nie sprawdzono |  | NAZWA Z FW PANELA |
| `0x3129` | 12585 | Boiler min hydraulic pressure [0.1bar] | u8 | 1 | 20 | 5 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x312A` | 12586 | Boiler max hydraulic pressure [0.1bar] | u8 | 5 | 40 | 15 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x3170` | 12656 | Buffer pump delta min temperature | u8 | 2 | 20 | 5 | nastawa | tak | 261 | NAZWA Z FW PANELA |
| `0x3171` | 12657 | Buffer T1 measured temperature | s16 | -300 | 1500 |  | live (odczyt) | tak | 19990 | NAZWA Z FW PANELA |
| `0x3172` | 12658 | Buffer T2 measured temperature | s16 | -300 | 1500 |  | live (odczyt) | tak | 19990 | NAZWA Z FW PANELA |
| `0x3173` | 12659 | Buffer T3 measured temperature | s16 | -300 | 1500 |  | live (odczyt) | tak | 19990 | NAZWA Z FW PANELA |
| `0x3174` | 12660 | Buffer internal energy [%] | s16 | -100 | 200 |  | live (odczyt) | tak | 0 | NAZWA Z FW PANELA |
| `0x3333` | 13107 | Boiler pressure[mbar] | u16 | 0 | 65535 | 0 | live (odczyt) | nie |  | NAZWA Z FW PANELA |
| `0x3502` | 13570 | CH expansion module type | u8 | 0 | 1 | 0 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x3511` | 13585 | Cascade master power level | u8 | 1 | 4 | 1 | nastawa | tak | 257 | NAZWA Z FW PANELA |
| `0x3512` | 13586 | Cascade slave 1 power level | u8 | 1 | 4 | 2 | nastawa | tak | 258 | NAZWA Z FW PANELA |
| `0x3513` | 13587 | Cascade slave 2 power level | u8 | 1 | 4 | 3 | nastawa | tak | 259 | NAZWA Z FW PANELA |
| `0x3514` | 13588 | Cascade slave 3 power level | u8 | 1 | 4 | 4 | nastawa | tak | 260 | NAZWA Z FW PANELA |
| `0x3515` | 13589 | Cascade minimal energy [%] | u8 | 0 | 100 | 50 | nastawa | tak | 306 | NAZWA Z FW PANELA |
| `0x3516` | 13590 | Cascade maximal energy [%] | u8 | 0 | 100 | 80 | nastawa | tak | 336 | NAZWA Z FW PANELA |
| `0x3517` | 13591 | Cascade time to inc power lvel [min] | u8 | 0 | 240 | 30 | nastawa | tak | 286 | NAZWA Z FW PANELA |
| `0x3518` | 13592 | Cascade time to dec power lvel [min] | u8 | 0 | 240 | 30 | nastawa | tak | 286 | NAZWA Z FW PANELA |
| `0x3519` | 13593 | Cascade current power lvel | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x351A` | 13594 | Cascade slaves number | u8 | 1 | 3 | 1 | nastawa | tak | 257 | NAZWA Z FW PANELA |
| `0x351B` | 13595 | Cascade timer to inc power lvel [s] | u16 | 0 | 65535 |  | live (odczyt) | tak | 0 | NAZWA Z FW PANELA |
| `0x351C` | 13596 | Cascade timer to dec power lvel [s] | u16 | 0 | 65535 |  | live (odczyt) | tak | 0 | NAZWA Z FW PANELA |
| `0x351E` | 13598 | External fuel storage motor 1 test | u8 | 0 | 2 | 0 | komenda | tak | 256 | POTWIERDZONY |
| `0x351F` | 13599 | External fuel storage motor 2 test | u8 | 0 | 2 | 0 | komenda | tak | 256 | POTWIERDZONY |
| `0x3520` | 13600 | Ext. fuel storage motor 1 transport. time [s] | u16 | 5 | 60 | 30 | nastawa | tak | 30 | NAZWA Z FW PANELA |
| `0x3521` | 13601 | Ext. fuel storage time [s] to empty transport. hose | u16 | 0 | 30 | 15 | nastawa | tak | 15 | NAZWA Z FW PANELA |
| `0x3522` | 13602 | External fuel storage motor 1 state | u8 | 0 | 1 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x3523` | 13603 | External fuel storage motor 2 state | u8 | 0 | 1 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x3524` | 13604 | External fuel storage level sens. state | u8 | 0 | 1 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x3526` | 13606 | Ext. fuel storage motor 1 overrun time [s] | u16 | 3 | 15 | 5 | nastawa | tak | 5 | NAZWA Z FW PANELA |
| `0x3527` | 13607 | Ext. fuel storage feeder work time [s] | u16 | 1 | 60 | 10 | nastawa | tak | 10 | NAZWA Z FW PANELA |
| `0x3528` | 13608 | Ext. fuel storage feeder pause time [s] | u16 | 0 | 30 | 10 | nastawa | tak | 10 | NAZWA Z FW PANELA |
| `0x3529` | 13609 | Ext. fuel storage reserve sensor | u8 | 0 | 1 | 0 | nastawa | tak | 256 | NAZWA Z FW PANELA |
| `0x352A` | 13610 | Ext. fuel stor. reserve sens. state | u8 | 0 | 1 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x352B` | 13611 | Ext. fuel storage max cycles no. | u8 | 5 | 100 | 15 | nastawa | tak | 271 | NAZWA Z FW PANELA |
| `0x3606` | 13830 | Input IN17 config | u8 | 0 | 2 | 0 | nastawa | tak | 256 | NAZWA Z FW PANELA |
| `0x3607` | 13831 | Reserve sensor state | u8 | 0 | 1 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x360A` | 13834 | State on closing actuator out in stop | u8 | 0 | 1 | 0 | nastawa | nie sprawdzono |  | TYLKO W FW PANELA |
| `0x3617` | 13847 | Statistics - Grate cleaning count | u32 | 0 | 4294967295 |  | live (odczyt) | tak | 12467 | NAZWA Z FW PANELA |
| `0x3620` | 13856 | Inside temp [C] CAN IO 5 | s16 | -32768 | 32767 |  | live (odczyt) | tak | 0 | NAZWA Z FW PANELA |
| `0x3621` | 13857 | Inside temp [C] CAN IO 6 | s16 | -32768 | 32767 |  | live (odczyt) | tak | 0 | NAZWA Z FW PANELA |
| `0x3622` | 13858 | Inside temp [C] CAN IO 7 | s16 | -32768 | 32767 |  | live (odczyt) | tak | 0 | NAZWA Z FW PANELA |
| `0x3623` | 13859 | Inside temp [C] CAN IO 4 | s16 | -32768 | 32767 |  | live (odczyt) | tak | 0 | NAZWA Z FW PANELA |
| `0x3624` | 13860 | Inside temp [C] CAN IO 3 | s16 | -32768 | 32767 |  | live (odczyt) | tak | 0 | NAZWA Z FW PANELA |
| `0x3625` | 13861 | Inside temp [C] CAN IO 2 | s16 | -32768 | 32767 |  | live (odczyt) | tak | 0 | NAZWA Z FW PANELA |
| `0x3626` | 13862 | Inside temp [C] CAN IO 1 | s16 | -32768 | 32767 |  | live (odczyt) | tak | 0 | NAZWA Z FW PANELA |
| `0x3627` | 13863 | Inside temp [C] CAN IO 0 | s16 | -32768 | 32767 |  | live (odczyt) | tak | 0 | NAZWA Z FW PANELA |
| `0x362B` | 13867 | Airflow meter | u8 | 0 | 1 | 0 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x362C` | 13868 | Total grate unblock try count | u16 | 0 | 65535 |  | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x3630` | 13872 | CAN IO 0 sw. ver. before dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x3631` | 13873 | CAN IO 1 sw. ver. before dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x3632` | 13874 | CAN IO 2 sw. ver. before dot | u8 | 0 | 255 |  | live (odczyt) | nie |  | NAZWA Z FW PANELA |
| `0x3633` | 13875 | CAN IO 3 sw. ver. before dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x3634` | 13876 | CAN IO 4 sw. ver. before dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x3635` | 13877 | CAN IO 5 sw. ver. before dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x3636` | 13878 | CAN IO 6 sw. ver. before dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x3637` | 13879 | CAN IO 7 sw. ver. before dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x3638` | 13880 | CAN IO 0 sw. ver. after dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x3639` | 13881 | CAN IO 1 sw. ver. after dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x363A` | 13882 | CAN IO 2 sw. ver. after dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x363B` | 13883 | CAN IO 3 sw. ver. after dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x363C` | 13884 | CAN IO 4 sw. ver. after dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x363D` | 13885 | CAN IO 5 sw. ver. after dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x363E` | 13886 | CAN IO 6 sw. ver. after dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x363F` | 13887 | CAN IO 7 sw. ver. after dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x3640` | 13888 | Inside temp [C] CAN IO Mini 0 | s16 | -32768 | 32767 |  | live (odczyt) | tak | 0 | NAZWA Z FW PANELA |
| `0x3648` | 13896 | CAN IO Mini 0 sw. ver. before dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x3650` | 13904 | CAN IO Mini 0 sw. ver. after dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x3658` | 13912 | CAN IO Big sw. ver. before dot | u8 | 0 | 255 |  | live (odczyt) | tak | 260 | NAZWA Z FW PANELA |
| `0x3659` | 13913 | CAN IO Big sw. ver. after dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x365A` | 13914 | Lambda module sw. ver. before dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x365B` | 13915 | Lambda module sw. ver. after dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x365C` | 13916 | Vide room 1 sw. ver. before dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x365D` | 13917 | Vide room 2 sw. ver. before dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x365E` | 13918 | Vide room 3 sw. ver. before dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x365F` | 13919 | Vide room 4 sw. ver. before dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x3660` | 13920 | Vide room 1 sw. ver. after dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x3661` | 13921 | Vide room 2 sw. ver. after dot | u8 | 0 | 255 |  | live (odczyt) | nie |  | NAZWA Z FW PANELA |
| `0x3662` | 13922 | Vide room 3 sw. ver. after dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x3663` | 13923 | Vide room 4 sw. ver. after dot | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x3664` | 13924 | soft. version | u16 | 0 | 65535 | 2213 | live (odczyt) | tak | 2118 | NAZWA Z FW PANELA |
| `0x3665` | 13925 | igneTouch boiler short name | u32 | 0 | 4294967295 |  | live (odczyt) | tak | 1413808128 | NAZWA Z FW PANELA |
| `0x3666` | 13926 | Airflowmeter 1 sw. ver. before dot | u8 | 0 | 255 |  | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x3667` | 13927 | Airflowmeter 1 sw. ver. after dot | u8 | 0 | 255 |  | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x366A` | 13930 | RadioGateway sw. ver. before dot | u8 | 0 | 255 |  | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x366B` | 13931 | RadioGateway sw. ver. after dot | u8 | 0 | 255 |  | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x3702` | 14082 | Nominal exhaust gas temp. [C] | u16 | 90 | 240 | 120 | nastawa | nie |  | NAZWA Z FW PANELA |
| `0x3705` | 14085 | Blower power in hold/pause [%] | u8 | 10 | 100 | 20 | nastawa | tak | 276 | NAZWA Z FW PANELA |
| `0x3707` | 14087 | EGT sensor type | u8 | 0 | 1 | 1 | nastawa | tak | 257 | NAZWA Z FW PANELA |
| `0x370A` | 14090 | Boiler image selector | u8 | 1 | 3 | 1 | nastawa | tak | 259 | NAZWA Z FW PANELA |
| `0x370C` | 14092 | Min fire up time [min] | u8 | 1 | 6 | 1 | nastawa | tak | 257 | NAZWA Z FW PANELA |
| `0x370F` | 14095 | Burning off burner feeder work time [s] | u16 | 0 | 180 | 60 | nastawa | tak | 60 | NAZWA Z FW PANELA |
| `0x3712` | 14098 | Blower type | u8 | 0 | 255 | 3 | nastawa | nie sprawdzono |  | NAZWA Z FW PANELA |
| `0x3713` | 14099 |  | u16 | 30 | 240 | 60 | nastawa | nie |  | NAZWA Z FW PANELA |
| `0x3714` | 14100 |  | u8 | 1 | 30 | 5 | nastawa | tak | 261 | NAZWA Z FW PANELA |
| `0x3718` | 14104 | Next service date timestamp | u32 | 0 | 4294967295 | 0 | nastawa | tak | 0 | NAZWA Z FW PANELA |
| `0x3719` | 14105 | Confirm. service date timestamp | u32 | 0 | 4294967295 | 0 | nastawa | tak | 0 | NAZWA Z FW PANELA |
| `0x371A` | 14106 | Airflowmeter 1 flow | u16 | 0 | 65535 | 0 | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x371B` | 14107 | Min airflow (blower 100%) [dm/s] | u16 | 10 | 1000 | 20 | nastawa | nie sprawdzono |  | TYLKO W FW PANELA |
| `0x371C` | 14108 | Boiler efficiency [d%] | u16 | 0 | 65535 | 0 | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x371D` | 14109 | Oxygen target [0.1%] | s16 | -32768 | 32767 | 0 | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x371E` | 14110 | Airflowmeter 2 flow | u16 | 0 | 65535 | 0 | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x371F` | 14111 | Lambda oxygen averaged [%] | s16 | -32768 | 32767 | 0 | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x3721` | 14113 | Outside temperature averaged | s16 | -500 | 1000 | 0 | live (odczyt) | tak | 30 | NAZWA Z FW PANELA |
| `0x3722` | 14114 | Start settings recovery | u8 | 0 | 1 | 0 | komenda | tak | 256 | NAZWA Z FW PANELA |
| `0x3723` | 14115 | Settings recovered count | u16 | 0 | 65535 | 0 | komenda | tak | 0 | NAZWA Z FW PANELA |
| `0x3724` | 14116 | Out temp. radio sensor batt. volt [mV] | u16 | 0 | 65535 |  | live (odczyt) | tak | 0 | NAZWA Z FW PANELA |
| `0x3725` | 14117 | Out temp. radio sensor signal [%] | u8 | 0 | 255 |  | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x3726` | 14118 | Out temp. radio sensor time since lasr rec. | u16 | 0 | 65535 |  | live (odczyt) | tak | 65535 | NAZWA Z FW PANELA |
| `0x3727` | 14119 | Burner feeder absolut work time [s] | u8 | 0 | 60 | 10 | nastawa | tak | 266 | NAZWA Z FW PANELA |
| `0x3728` | 14120 | Is reset required | u8 | 0 | 1 | 0 | live (odczyt) | tak | 256 | NAZWA Z FW PANELA |
| `0x3729` | 14121 | Is summer time | u8 | 0 | 1 |  | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x372A` | 14122 | Summer time threshold temp. [C] | u8 | 5 | 25 | 18 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x372B` | 14123 | Out temp. radio sensor sw. ver. before dot | u8 | 0 | 255 |  | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x372C` | 14124 | Out temp. radio sensor sw. ver. after dot | u8 | 0 | 255 |  | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x372D` | 14125 |  | u8 | 0 | 1 | 0 | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x372E` | 14126 | [m%] | s32 | 70000 | 130000 |  | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x372F` | 14127 | Is automatic time synchronization | u8 | 0 | 1 | 0 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x3730` | 14128 | SSID part 1 | u32 | 0 | 4294967295 | 0 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x3731` | 14129 | SSID part 2 | u32 | 0 | 4294967295 | 0 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x3732` | 14130 | SSID part 3 | u32 | 0 | 4294967295 | 0 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x3733` | 14131 | SSID part 4 | u32 | 0 | 4294967295 | 0 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x3734` | 14132 | SSID part 5 | u32 | 0 | 4294967295 | 0 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x3735` | 14133 | SSID part 6 | u32 | 0 | 4294967295 | 0 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x3736` | 14134 | KEY part 1 | u32 | 0 | 4294967295 | 0 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x3737` | 14135 | KEY part 2 | u32 | 0 | 4294967295 | 0 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x3738` | 14136 | KEY part 3 | u32 | 0 | 4294967295 | 0 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x3739` | 14137 | KEY part 4 | u32 | 0 | 4294967295 | 0 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x373A` | 14138 | KEY part 5 | u32 | 0 | 4294967295 | 0 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x373B` | 14139 | KEY part 6 | u32 | 0 | 4294967295 | 0 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x373C` | 14140 |  | u8 | 0 | 255 |  | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x373D` | 14141 |  | u8 | 0 | 255 |  | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x373E` | 14142 |  | u8 | 0 | 255 | 0 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x373F` | 14143 |  | u32 | 0 | 4294967295 | 0 | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x3740` | 14144 |  | u32 | 0 | 4294967295 | 0 | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x3741` | 14145 |  | u8 | 0 | 255 | 0 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x3742` | 14146 |  | u8 | 0 | 255 | 0 | komenda | nie |  | TYLKO W FW PANELA |
| `0x3743` | 14147 |  | u8 | 0 | 255 | 0 | komenda | nie |  | TYLKO W FW PANELA |
| `0x3744` | 14148 |  | u8 | 0 | 255 |  | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x3745` | 14149 |  | u8 | 0 | 255 |  | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x3746` | 14150 |  | u8 | 0 | 255 |  | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x3747` | 14151 | Outside calibration [dC] | s16 | -30 | 30 | 0 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x3748` | 14152 | Storage feeder pause in predose[s] | u8 | 1 | 8 | 2 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x3749` | 14153 | Hot water circular pump state | u8 | 0 | 1 | 0 | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x374A` | 14154 | HW1 circular pump test | u8 | 0 | 2 | 0 | komenda | nie |  | TYLKO W FW PANELA |
| `0x374B` | 14155 | Hot water 1 circular pump fork time | u8 | 0 | 10 | 2 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x374C` | 14156 | Hot water 1 circular pump pause time | u8 | 0 | 60 | 10 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x374D` | 14157 | Burner plug disc. possible | u8 | 0 | 1 | 0 | nastawa | nie sprawdzono |  | TYLKO W FW PANELA |
| `0x3750` | 14160 | Sweep mode | u8 | 0 | 1 | 0 | komenda | nie |  | TYLKO W FW PANELA |
| `0x4006` | 16390 | Power regulator [%] | s16 | 0 | 65535 |  | live (odczyt) | nie sprawdzono |  | NAZWA Z FW PANELA |
| `0x4007` | 16391 | Blower power [%] | u8 | 0 | 255 | 0 | live (odczyt) | nie sprawdzono |  | NAZWA Z FW PANELA |
| `0x4008` | 16392 | Burning type active | u8 | 0 | 2 | 0 | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x4009` | 16393 | Exhaust gas temperature (2) [C] | s16 | -50 | 350 | 0 | live (odczyt) | nie |  | TYLKO W FW PANELA |
| `0x400A` | 16394 | Virt. energy consumer set temp [C] | u16 | 7 | 150 | 7 | komenda | tak | 7 | NAZWA Z FW PANELA |
| `0x400C` | 16396 | CH temp for -10C [C] | u8 | 20 | 80 | 50 | nastawa | nie |  | TYLKO W FW PANELA |
| `0x404E` | 16462 | Request reset alarm memory | u8 | 0 | 1 | 0 | komenda | nie |  | TYLKO W FW PANELA |

## 5. Rejestry kotła, których nie ma w binarce panela i których nie używamy (157)

Odpowiadają na skan węzła 4, ale panel ich nie rejestruje (m.in. bloki harmonogramów, liczniki, kopie wartości). Opis jest automatyczny („auto”) – wartość i zakres z odczytu.

| Rejestr | Nazwa | Status | Opis / wartość | Blok |
|---|---|---|---|---|
| `0x03E9` | - | NIEZNANY | (auto) liczba 78 (jeśli /10: 7.8); suby 2-4 nieodczytane | Blok 0x0000–0x0FFF |
| `0x03ED` | - | NIEZNANY | (auto) liczba 3; suby 2-4 nieodczytane | Blok 0x0000–0x0FFF |
| `0x07D1` | - | NIEZNANY | (auto) liczba 215 (jeśli /10: 21.5); suby 2-4 nieodczytane | Blok 0x0000–0x0FFF |
| `0x07D2` | - | NIEZNANY | (auto) liczba 175 (jeśli /10: 17.5); suby 2-4 nieodczytane | Blok 0x0000–0x0FFF |
| `0x07D3` | - | NIEZNANY | (auto) liczba 2; suby 2-4 nieodczytane | Blok 0x0000–0x0FFF |
| `0x07D4` | - | NIEZNANY | (auto) liczba 10; suby 2-4 nieodczytane | Blok 0x0000–0x0FFF |
| `0x07D5` | - | NIEZNANY | (auto) liczba 1; suby 2-4 nieodczytane | Blok 0x0000–0x0FFF |
| `0x07D6` | - | NIEZNANY | (auto) liczba 1; suby 2-4 nieodczytane | Blok 0x0000–0x0FFF |
| `0x07D7` | - | NIEZNANY | (auto) liczba 3; suby 2-4 nieodczytane | Blok 0x0000–0x0FFF |
| `0x07D8` | - | NIEZNANY | (auto) liczba 1; suby 2-4 nieodczytane | Blok 0x0000–0x0FFF |
| `0x07DB` | - | NIEZNANY | (auto) liczba 65 (jeśli /10: 6.5); suby 2-4 nieodczytane | Blok 0x0000–0x0FFF |
| `0x07DE` | - | NIEZNANY | (auto) liczba 1; suby 2-4 nieodczytane | Blok 0x0000–0x0FFF |
| `0x07DF` | - | NIEZNANY | (auto) zero; suby 2-4 nieodczytane | Blok 0x0000–0x0FFF |
| `0x07E0` | - | NIEZNANY | (auto) zero; suby 2-4 nieodczytane | Blok 0x0000–0x0FFF |
| `0x07E1` | - | NIEZNANY | (auto) liczba 1; suby 2-4 nieodczytane | Blok 0x0000–0x0FFF |
| `0x0803` | Harmonogram (maska 24 bit) – dzień 1, prawdopodobnie CO 2 / bufor | ODNALEZIONY – NIEPOTWIERDZONY |  | Blok 0x0000–0x0FFF |
| `0x0804` | Harmonogram (maska 24 bit) – dzień 2, prawdopodobnie CO 2 / bufor | ODNALEZIONY – NIEPOTWIERDZONY |  | Blok 0x0000–0x0FFF |
| `0x0805` | Harmonogram (maska 24 bit) – dzień 3, prawdopodobnie CO 2 / bufor | ODNALEZIONY – NIEPOTWIERDZONY |  | Blok 0x0000–0x0FFF |
| `0x0806` | Harmonogram (maska 24 bit) – dzień 4, prawdopodobnie CO 2 / bufor | ODNALEZIONY – NIEPOTWIERDZONY |  | Blok 0x0000–0x0FFF |
| `0x0807` | Harmonogram (maska 24 bit) – dzień 5, prawdopodobnie CO 2 / bufor | ODNALEZIONY – NIEPOTWIERDZONY |  | Blok 0x0000–0x0FFF |
| `0x0808` | Harmonogram (maska 24 bit) – dzień 6, prawdopodobnie CO 2 / bufor | ODNALEZIONY – NIEPOTWIERDZONY |  | Blok 0x0000–0x0FFF |
| `0x0809` | Harmonogram (maska 24 bit) – dzień 7, prawdopodobnie CO 2 / bufor | ODNALEZIONY – NIEPOTWIERDZONY |  | Blok 0x0000–0x0FFF |
| `0x0BB9` | - | NIEZNANY | (auto) liczba 207 (jeśli /10: 20.7); suby 2-4 nieodczytane | Blok 0x0000–0x0FFF |
| `0x0BBA` | - | NIEZNANY | (auto) liczba 182 (jeśli /10: 18.2); suby 2-4 nieodczytane | Blok 0x0000–0x0FFF |
| `0x0BBB` | - | NIEZNANY | (auto) liczba 1; suby 2-4 nieodczytane | Blok 0x0000–0x0FFF |
| `0x0FD2` | - | NIEZNANY | (auto) liczba 1; suby 2-4 nieodczytane | Blok 0x0000–0x0FFF |
| `0x0FD7` | - | NIEZNANY | (auto) liczba 1; suby 2-4 nieodczytane | Blok 0x0000–0x0FFF |
| `0x2017` | - | NIEZNANY | (auto) zero; zakres -100..1500; sąsiedztwo: po: Tryb CWU (0x2014) / przed: CWU – temperatura zadana (wynikowa) (0x201A) | Ustawienia podstawowe kotła / CO / CWU / tryby |
| `0x2018` | - | NIEZNANY | (auto) zero; zakres -100..1500; sąsiedztwo: po: Tryb CWU (0x2014) / przed: CWU – temperatura zadana (wynikowa) (0x201A) | Ustawienia podstawowe kotła / CO / CWU / tryby |
| `0x2019` | - | NIEZNANY | (auto) zero; zakres -100..1500; sąsiedztwo: przed: CWU – temperatura zadana (wynikowa) (0x201A) | Ustawienia podstawowe kotła / CO / CWU / tryby |
| `0x2033` | - | NIEZNANY | (auto) liczba 210 (jeśli /10: 21.0); zakres 150..300; sąsiedztwo: po: CO – temperatura komfort (zadana) (0x2032) | Ustawienia podstawowe kotła / CO / CWU / tryby |
| `0x2034` | - | NIEZNANY | (auto) liczba 210 (jeśli /10: 21.0); zakres 150..300; sąsiedztwo: po: CO – temperatura komfort (zadana) (0x2032) | Ustawienia podstawowe kotła / CO / CWU / tryby |
| `0x2035` | - | NIEZNANY | (auto) liczba 210 (jeśli /10: 21.0); zakres 150..300; sąsiedztwo: po: CO – temperatura komfort (zadana) (0x2032) | Ustawienia podstawowe kotła / CO / CWU / tryby |
| `0x2049` | - | NIEZNANY | (auto) liczba 180 (jeśli /10: 18.0); zakres ?..300; sąsiedztwo: po: CO – temperatura eko (zadana) (0x2048) | Ustawienia podstawowe kotła / CO / CWU / tryby |
| `0x204A` | - | NIEZNANY | (auto) liczba 180 (jeśli /10: 18.0); zakres 100..300; sąsiedztwo: po: CO – temperatura eko (zadana) (0x2048) | Ustawienia podstawowe kotła / CO / CWU / tryby |
| `0x204B` | - | NIEZNANY | (auto) liczba 180 (jeśli /10: 18.0); zakres 100..300; sąsiedztwo: po: CO – temperatura eko (zadana) (0x2048) | Ustawienia podstawowe kotła / CO / CWU / tryby |
| `0x2066` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..259; sąsiedztwo: po: Tryb CO 2 (0x2065) | Ustawienia podstawowe kotła / CO / CWU / tryby |
| `0x2067` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..259; sąsiedztwo: po: Tryb CO 2 (0x2065) | Ustawienia podstawowe kotła / CO / CWU / tryby |
| `0x2127` | Harmonogram – slot 1 dnia 1 (maska 24 bit) | ODNALEZIONY – NIEPOTWIERDZONY |  | Harmonogram CO i sloty |
| `0x2128` | Harmonogram – slot 2 dnia 1 (maska 24 bit) | ODNALEZIONY – NIEPOTWIERDZONY |  | Harmonogram CO i sloty |
| `0x2129` | Harmonogram – slot 3 dnia 1 (maska 24 bit) | ODNALEZIONY – NIEPOTWIERDZONY |  | Harmonogram CO i sloty |
| `0x212B` | Harmonogram – slot 1 dnia 2 (maska 24 bit) | ODNALEZIONY – NIEPOTWIERDZONY |  | Harmonogram CO i sloty |
| `0x212C` | Harmonogram – slot 2 dnia 2 (maska 24 bit) | ODNALEZIONY – NIEPOTWIERDZONY |  | Harmonogram CO i sloty |
| `0x212D` | Harmonogram – slot 3 dnia 2 (maska 24 bit) | ODNALEZIONY – NIEPOTWIERDZONY |  | Harmonogram CO i sloty |
| `0x212F` | Harmonogram – slot 1 dnia 3 (maska 24 bit) | ODNALEZIONY – NIEPOTWIERDZONY |  | Harmonogram CO i sloty |
| `0x2130` | Harmonogram – slot 2 dnia 3 (maska 24 bit) | ODNALEZIONY – NIEPOTWIERDZONY |  | Harmonogram CO i sloty |
| `0x2131` | Harmonogram – slot 3 dnia 3 (maska 24 bit) | ODNALEZIONY – NIEPOTWIERDZONY |  | Harmonogram CO i sloty |
| `0x2133` | Harmonogram – slot 1 dnia 4 (maska 24 bit) | ODNALEZIONY – NIEPOTWIERDZONY |  | Harmonogram CO i sloty |
| `0x2134` | Harmonogram – slot 2 dnia 4 (maska 24 bit) | ODNALEZIONY – NIEPOTWIERDZONY |  | Harmonogram CO i sloty |
| `0x2135` | Harmonogram – slot 3 dnia 4 (maska 24 bit) | ODNALEZIONY – NIEPOTWIERDZONY |  | Harmonogram CO i sloty |
| `0x2137` | Harmonogram – slot 1 dnia 5 (maska 24 bit) | ODNALEZIONY – NIEPOTWIERDZONY |  | Harmonogram CO i sloty |
| `0x2138` | Harmonogram – slot 2 dnia 5 (maska 24 bit) | ODNALEZIONY – NIEPOTWIERDZONY |  | Harmonogram CO i sloty |
| `0x2139` | Harmonogram – slot 3 dnia 5 (maska 24 bit) | ODNALEZIONY – NIEPOTWIERDZONY |  | Harmonogram CO i sloty |
| `0x213B` | Harmonogram – slot 1 dnia 6 (maska 24 bit) | ODNALEZIONY – NIEPOTWIERDZONY |  | Harmonogram CO i sloty |
| `0x213C` | Harmonogram – slot 2 dnia 6 (maska 24 bit) | ODNALEZIONY – NIEPOTWIERDZONY |  | Harmonogram CO i sloty |
| `0x213D` | Harmonogram – slot 3 dnia 6 (maska 24 bit) | ODNALEZIONY – NIEPOTWIERDZONY |  | Harmonogram CO i sloty |
| `0x213F` | Harmonogram – slot 1 dnia 7 (maska 24 bit) | ODNALEZIONY – NIEPOTWIERDZONY |  | Harmonogram CO i sloty |
| `0x2140` | Harmonogram – slot 2 dnia 7 (maska 24 bit) | ODNALEZIONY – NIEPOTWIERDZONY |  | Harmonogram CO i sloty |
| `0x2141` | Harmonogram – slot 3 dnia 7 (maska 24 bit) | ODNALEZIONY – NIEPOTWIERDZONY |  | Harmonogram CO i sloty |
| `0x2143` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..257; sąsiedztwo: po: CO 1 – tryb pracy (ręczny/pogodowy) (0x2142) / przed: CO 1 – temperatura zadana ręczna [°C] (0x2146) | Ustawienia CO/CWU, harmonogram CWU |
| `0x2144` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..257; sąsiedztwo: po: CO 1 – tryb pracy (ręczny/pogodowy) (0x2142) / przed: CO 1 – temperatura zadana ręczna [°C] (0x2146) | Ustawienia CO/CWU, harmonogram CWU |
| `0x2145` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..257; sąsiedztwo: po: CO 1 – tryb pracy (ręczny/pogodowy) (0x2142) / przed: CO 1 – temperatura zadana ręczna [°C] (0x2146) | Ustawienia CO/CWU, harmonogram CWU |
| `0x2148` | - | NIEZNANY | (auto) flaga+bajt: wartość 50 (raw 306); zakres 276..336; sąsiedztwo: po: CO 2 – temperatura zadana (ręczna) (0x2147) | Ustawienia CO/CWU, harmonogram CWU |
| `0x2149` | - | NIEZNANY | (auto) flaga+bajt: wartość 50 (raw 306); zakres 276..336; sąsiedztwo: po: CO 2 – temperatura zadana (ręczna) (0x2147) | Ustawienia CO/CWU, harmonogram CWU |
| `0x214B` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..?; sąsiedztwo: po: CO 2 – temperatura zadana (ręczna) (0x2147) | Ustawienia CO/CWU, harmonogram CWU |
| `0x214C` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres ?..258 | Ustawienia CO/CWU, harmonogram CWU |
| `0x214D` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..258 | Ustawienia CO/CWU, harmonogram CWU |
| `0x2167` | - | NIEZNANY | (auto) zero; zakres 0..500 | Ustawienia CO/CWU, harmonogram CWU |
| `0x2168` | - | NIEZNANY | (auto) zero; zakres 0..500 | Ustawienia CO/CWU, harmonogram CWU |
| `0x2169` | - | NIEZNANY | (auto) zero; zakres 0..500 | Ustawienia CO/CWU, harmonogram CWU |
| `0x229B` | Pompa CO3 – stan pracy | POTWIERDZONY | Stan pompy obiegu CO3. | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x229C` | Pompa CO4 – stan pracy | POTWIERDZONY | Stan pompy obiegu CO4. | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x229E` | Pompa CO2 – tryb testowy | POTWIERDZONY | Polecenie trybu testowego wyjścia (Menu → Test wyjść, wymaga PIN poziom 2). Zapis zmienia tryb, stan fizyczny wyjścia zależy od sterownika. | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x229F` | Pompa CO3 – tryb testowy | POTWIERDZONY | Polecenie trybu testowego wyjścia (Menu → Test wyjść, wymaga PIN poziom 2). Zapis zmienia tryb, stan fizyczny wyjścia zależy od sterownika. | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22A0` | Pompa CO4 – tryb testowy | POTWIERDZONY | Polecenie trybu testowego wyjścia (Menu → Test wyjść, wymaga PIN poziom 2). Zapis zmienia tryb, stan fizyczny wyjścia zależy od sterownika. | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22A2` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..261 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22A3` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..261 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22A4` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..261 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22A6` | - | NIEZNANY | (auto) flaga 0/1 (raw 257=1); zakres 256..257 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22A7` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..257 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22A8` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..257 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22AF` | - | NIEZNANY | (auto) zero; zakres 10..90; sąsiedztwo: po: CO 2 – temperatura zadana (wynikowa) (0x22AE) | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22B0` | - | NIEZNANY | (auto) zero; zakres 10..90; sąsiedztwo: po: CO 2 – temperatura zadana (wynikowa) (0x22AE) | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22B2` | - | NIEZNANY | (auto) flaga+bajt: wartość 10 (raw 266); zakres 256..286; sąsiedztwo: po: CO 2 – temperatura zadana (wynikowa) (0x22AE) | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22B3` | - | NIEZNANY | (auto) flaga+bajt: wartość 10 (raw 266); zakres 256..286 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22B4` | - | NIEZNANY | (auto) flaga+bajt: wartość 10 (raw 266); zakres 256..286 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22B6` | - | NIEZNANY | (auto) liczba 180 (jeśli /10: 18.0); zakres 60..360 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22B7` | - | NIEZNANY | (auto) liczba 180 (jeśli /10: 18.0); zakres 60..360 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22B8` | - | NIEZNANY | (auto) liczba 180 (jeśli /10: 18.0); zakres 60..360 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22BA` | Mieszacz CO2 – tryb testowy (A/CLOSE/OPEN) | POTWIERDZONY | Polecenie trybu testowego wyjścia (Menu → Test wyjść, wymaga PIN poziom 2). Zapis zmienia tryb, stan fizyczny wyjścia zależy od sterownika. | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22BB` | Mieszacz CO3 – tryb testowy (A/CLOSE/OPEN) | POTWIERDZONY | Polecenie trybu testowego wyjścia (Menu → Test wyjść, wymaga PIN poziom 2). Zapis zmienia tryb, stan fizyczny wyjścia zależy od sterownika. | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22BC` | Mieszacz CO4 – tryb testowy (A/CLOSE/OPEN) | POTWIERDZONY | Polecenie trybu testowego wyjścia (Menu → Test wyjść, wymaga PIN poziom 2). Zapis zmienia tryb, stan fizyczny wyjścia zależy od sterownika. | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22BE` | - | NIEZNANY | (auto) flaga+bajt: wartość 5 (raw 261); zakres 256..306; sąsiedztwo: po: CO 1 – histereza [°C] (0x22BD) / przed: CO 1 – kalibracja czujnika [°C] (0x22C1) | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22BF` | - | NIEZNANY | (auto) flaga+bajt: wartość 5 (raw 261); zakres 256..306; sąsiedztwo: po: CO 1 – histereza [°C] (0x22BD) / przed: CO 1 – kalibracja czujnika [°C] (0x22C1) | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22C0` | - | NIEZNANY | (auto) flaga+bajt: wartość 5 (raw 261); zakres 256..306; sąsiedztwo: po: CO 1 – histereza [°C] (0x22BD) / przed: CO 1 – kalibracja czujnika [°C] (0x22C1) | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22C2` | - | NIEZNANY | (auto) zero; zakres -30..30; sąsiedztwo: po: CO 1 – kalibracja czujnika [°C] (0x22C1) / przed: CO 1 – krzywa pogodowa, temperatura zewnętrzna −20 °C [°C zasilania] (0x22C5) | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22C3` | - | NIEZNANY | (auto) zero; zakres -30..30; sąsiedztwo: po: CO 1 – kalibracja czujnika [°C] (0x22C1) / przed: CO 1 – krzywa pogodowa, temperatura zewnętrzna −20 °C [°C zasilania] (0x22C5) | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22C4` | - | NIEZNANY | (auto) zero; zakres -30..30; sąsiedztwo: po: CO 1 – kalibracja czujnika [°C] (0x22C1) / przed: CO 1 – krzywa pogodowa, temperatura zewnętrzna −20 °C [°C zasilania] (0x22C5) | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22C6` | - | NIEZNANY | (auto) flaga+bajt: wartość 55 (raw 311); zakres 276..336; sąsiedztwo: po: CO 1 – krzywa pogodowa, temperatura zewnętrzna −20 °C [°C zasilania] (0x22C5) / przed: CO 1 – krzywa pogodowa, temperatura zewnętrzna 0 °C [°C zasilania] (0x22C9) | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22C7` | - | NIEZNANY | (auto) flaga+bajt: wartość 55 (raw 311); zakres 276..336; sąsiedztwo: po: CO 1 – krzywa pogodowa, temperatura zewnętrzna −20 °C [°C zasilania] (0x22C5) / przed: CO 1 – krzywa pogodowa, temperatura zewnętrzna 0 °C [°C zasilania] (0x22C9) | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22C8` | - | NIEZNANY | (auto) flaga+bajt: wartość 55 (raw 311); zakres 276..336; sąsiedztwo: po: CO 1 – krzywa pogodowa, temperatura zewnętrzna −20 °C [°C zasilania] (0x22C5) / przed: CO 1 – krzywa pogodowa, temperatura zewnętrzna 0 °C [°C zasilania] (0x22C9) | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22CA` | - | NIEZNANY | (auto) flaga+bajt: wartość 45 (raw 301); zakres 276..336; sąsiedztwo: po: CO 1 – krzywa pogodowa, temperatura zewnętrzna 0 °C [°C zasilania] (0x22C9) / przed: CO 1 – krzywa pogodowa, temperatura zewnętrzna +10 °C [°C zasilania] (0x22CD) | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22CB` | - | NIEZNANY | (auto) flaga+bajt: wartość 45 (raw 301); zakres ?..336; sąsiedztwo: po: CO 1 – krzywa pogodowa, temperatura zewnętrzna 0 °C [°C zasilania] (0x22C9) / przed: CO 1 – krzywa pogodowa, temperatura zewnętrzna +10 °C [°C zasilania] (0x22CD) | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22CC` | - | NIEZNANY | (auto) flaga+bajt: wartość 45 (raw 301); zakres 276..336; sąsiedztwo: po: CO 1 – krzywa pogodowa, temperatura zewnętrzna 0 °C [°C zasilania] (0x22C9) / przed: CO 1 – krzywa pogodowa, temperatura zewnętrzna +10 °C [°C zasilania] (0x22CD) | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22CE` | - | NIEZNANY | (auto) flaga+bajt: wartość 30 (raw 286); zakres 276..336; sąsiedztwo: po: CO 1 – krzywa pogodowa, temperatura zewnętrzna +10 °C [°C zasilania] (0x22CD) | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22CF` | - | NIEZNANY | (auto) flaga+bajt: wartość 30 (raw 286); zakres 276..336; sąsiedztwo: po: CO 1 – krzywa pogodowa, temperatura zewnętrzna +10 °C [°C zasilania] (0x22CD) | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22D0` | - | NIEZNANY | (auto) flaga+bajt: wartość 30 (raw 286); zakres 276..336; sąsiedztwo: po: CO 1 – krzywa pogodowa, temperatura zewnętrzna +10 °C [°C zasilania] (0x22CD) | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22D2` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..257 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22D3` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..257 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22D4` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..257 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22D6` | - | NIEZNANY | (auto) flaga+bajt: wartość 70 (raw 326); zakres 286..336 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22D7` | - | NIEZNANY | (auto) flaga+bajt: wartość 70 (raw 326); zakres 286..336 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22D8` | - | NIEZNANY | (auto) flaga+bajt: wartość 70 (raw 326); zakres 286..336 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22DA` | - | NIEZNANY | (auto) flaga+bajt: wartość 6 (raw 262); brak subów 2-4 (rejestr tylko do odczytu lub sub nie istnieje) | Odczyt ręczny / luka w skanie |
| `0x22DB` | - | NIEZNANY | (auto) flaga+bajt: wartość 6 (raw 262); zakres 256..? | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22DC` | - | NIEZNANY | (auto) flaga+bajt: wartość 6 (raw 262); zakres 256..276 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22DE` | - | NIEZNANY | (auto) flaga+bajt: wartość 18 (raw 274); zakres 256..286 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22DF` | - | NIEZNANY | (auto) flaga+bajt: wartość 18 (raw 274); zakres 256..286 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22E0` | - | NIEZNANY | (auto) flaga+bajt: wartość 18 (raw 274); zakres 256..286 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22E2` | - | NIEZNANY | (auto) flaga+bajt: wartość 15 (raw 271); zakres 256..286 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22E3` | - | NIEZNANY | (auto) flaga+bajt: wartość 15 (raw 271); typ U16, zakres nieznany | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22E4` | - | NIEZNANY | (auto) flaga+bajt: wartość 15 (raw 271); zakres 256..286 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22E6` | - | NIEZNANY | (auto) flaga+bajt: wartość 15 (raw 271); zakres 256..296 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22E7` | - | NIEZNANY | (auto) flaga+bajt: wartość 15 (raw 271); zakres 256..296 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22E8` | - | NIEZNANY | (auto) flaga+bajt: wartość 15 (raw 271); zakres 256..296 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22EA` | - | NIEZNANY | (auto) flaga+bajt: wartość 20 (raw 276); zakres 276..316 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22EB` | - | NIEZNANY | (auto) flaga+bajt: wartość 20 (raw 276); zakres 276..316 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22EC` | - | NIEZNANY | (auto) flaga+bajt: wartość 20 (raw 276); zakres 276..316 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22F2` | - | NIEZNANY | (auto) flaga 0/1 (raw 257=1); zakres 256..257 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22F3` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..257 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22F4` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..257 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22F6` | - | NIEZNANY | (auto) liczba 7; zakres 0..150 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22F7` | - | NIEZNANY | (auto) liczba 7; zakres 0..? | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22F8` | - | NIEZNANY | (auto) liczba 7; zakres 0..150 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22FA` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); brak subów 2-4 (rejestr tylko do odczytu lub sub nie istnieje) | Odczyt ręczny / luka w skanie |
| `0x22FB` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..257 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22FC` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..257 | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22FE` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..511; sąsiedztwo: przed: Wejście: zgoda regulatora (IN3) (0x2301) | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x22FF` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..511; sąsiedztwo: przed: Wejście: zgoda regulatora (IN3) (0x2301) | Palnik, dmuchawa, pompy, parametry serwisowe |
| `0x2300` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..511; sąsiedztwo: przed: Wejście: zgoda regulatora (IN3) (0x2301) | Parametry 0x2300–0x2FFF |
| `0x2302` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..257; sąsiedztwo: po: Wejście: zgoda regulatora (IN3) (0x2301) | Parametry 0x2300–0x2FFF |
| `0x2303` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..257; sąsiedztwo: po: Wejście: zgoda regulatora (IN3) (0x2301) | Parametry 0x2300–0x2FFF |
| `0x2304` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..257; sąsiedztwo: po: Wejście: zgoda regulatora (IN3) (0x2301) | Parametry 0x2300–0x2FFF |
| `0x2306` | - | NIEZNANY | (auto) zero; zakres -110..40 | Parametry 0x2300–0x2FFF |
| `0x2307` | - | NIEZNANY | (auto) zero; zakres -110..40 | Parametry 0x2300–0x2FFF |
| `0x2308` | - | NIEZNANY | (auto) zero; zakres -110..40 | Parametry 0x2300–0x2FFF |
| `0x230A` | - | NIEZNANY | (auto) zero; zakres 0..-1 | Parametry 0x2300–0x2FFF |
| `0x230B` | - | NIEZNANY | (auto) zero; zakres 0..-1 | Parametry 0x2300–0x2FFF |
| `0x230C` | - | NIEZNANY | (auto) zero; zakres 0..-1 | Parametry 0x2300–0x2FFF |
| `0x230E` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..511 | Parametry 0x2300–0x2FFF |
| `0x230F` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..? | Parametry 0x2300–0x2FFF |
| `0x2310` | - | NIEZNANY | (auto) flaga 0/1 (raw 256=0); zakres 256..511 | Parametry 0x2300–0x2FFF |
| `0x2312` | - | NIEZNANY | (auto) liczba 65535 (jeśli /10: 6553.5); zakres 0..-1 | Parametry 0x2300–0x2FFF |
| `0x2313` | - | NIEZNANY | (auto) liczba 65535 (jeśli /10: 6553.5); zakres 0..-1 | Parametry 0x2300–0x2FFF |
| `0x2314` | - | NIEZNANY | (auto) liczba 65535 (jeśli /10: 6553.5); zakres 0..-1 | Parametry 0x2300–0x2FFF |
| `0x4003` | - | NIEZNANY | (auto) zero; zakres -100..1500; sąsiedztwo: po: CO 2 – temperatura (pomiar) (0x4002) / przed: Moc palnika [%] (0x4005) | Pomiary, alarmy |
| `0x4004` | - | NIEZNANY | (auto) zero; zakres -100..1500; sąsiedztwo: po: CO 2 – temperatura (pomiar) (0x4002) / przed: Moc palnika [%] (0x4005) | Pomiary, alarmy |

## 6. Węzeł 86 – CAN IO BIG (CiA 401)

| Rejestr | Nazwa | Status | Opis | Uwagi |
|---|---|---|---|---|
| `0x1018` | Identyfikator urządzenia (Product Code) | NIEZNANY |  | CiA 301 |
| `0x1400` | RPDO1 – COB-ID | NIEZNANY |  | 0x256 |
| `0x1401` | RPDO2 – COB-ID | NIEZNANY |  | 0x356 |
| `0x1402` | RPDO3 – COB-ID | NIEZNANY |  | 0x456 |
| `0x1403` | RPDO4 – COB-ID | NIEZNANY |  | 0x556 |
| `0x1600` | RPDO1 – mapowanie | NIEZNANY |  |  |
| `0x1601` | RPDO2 – mapowanie | NIEZNANY |  |  |
| `0x1800` | TPDO1 – COB-ID | NIEZNANY |  | 0x1D6 |
| `0x1801` | TPDO2 – COB-ID | NIEZNANY |  | 0x2D6 |
| `0x1802` | TPDO3 – COB-ID | NIEZNANY |  | 0x3D6 |
| `0x1803` | TPDO4 – COB-ID | NIEZNANY |  | 0x4D6 |
| `0x1A00` | TPDO1 – mapowanie | NIEZNANY |  |  |
| `0x1A01` | TPDO2 – mapowanie | NIEZNANY |  |  |
| `0x2048` | (rejestr producenta, wartość 240) | NIEZNANY |  | jak CO eko 0x2048 w węźle 4? |
| `0x6000` | Wejścia cyfrowe (CiA 401, 1 B) | POTWIERDZONY |  | odczyt |
| `0x6200` | Wyjścia cyfrowe (CiA 401) | ODNALEZIONY – NIEPOTWIERDZONY |  | Test wyjść (zapis) jeszcze nie zrobiony |
| `0x6401` | Wejścia analogowe (CiA 401, 2 B) | POTWIERDZONY |  | odczyt |
| `0x6411` | Wyjścia analogowe (CiA 401) | ODNALEZIONY – NIEPOTWIERDZONY |  | Test wyjść (zapis) jeszcze nie zrobiony |

## 7. Jak kontynuować pracę

1. **Znajdź rejestr pozycji menu:** wybierz wiersz z sekcji 4 (albo pozycję menu panela), w HA naciśnij **Snap A**, zmień JEDNĄ nastawę na panelu, naciśnij **Snap B** – lista `XXXX:stara>nowa` pokaże rejestr (szczegóły: [README.md](README.md), sekcja 3).
2. **Podepnij w firmware:** dopisz `case 0x....:` w parserze, wpis w `set_param` (ix/lo/hi/lv) i encję w `esphome/PelletCAN_packages.yaml`; w karcie dodaj wiersz na ekranie (patrz CHANGELOG-firmware.md, np. v1.4.18–1.4.23 jako wzór).
3. **Zaktualizuj dokumentację:** `python3 tools/oznacz_uzycie.py` (kolumna „wykorzystany”), popraw status/opis w `katalog-rejestrow.csv`, potem `python3 tools/gen_rejestry_md.py` (ten plik) i `python3 tools/gen_katalog_html.py docs/katalog.html`.
4. **Nowa wersja panela:** po wczytaniu nowego FW panela odtwórz `panel-fw-parametry-*.csv` (rejestracja parametrów funkcją `0x0802143C`, baza ładowania `0x08010000`) i uruchom `python3 tools/scal_nazwy_panela.py`.
5. **Zapisy na kotle** wykonuj ostrożnie: flaga `mirror`, wyłączniki `*_write`, poziom dostępu (klucz 1/2). Nowy zapis testuj na jednym rejestrze i porównaj z tym, co robi panel (`sniff: "true"` pokaże zapisy panela).

Powiązane: [README.md](README.md) (skaner, metoda różnicowa), [PANEL-FW.md](PANEL-FW.md) (analiza firmware panela), [TODO.md](TODO.md), [katalog-rejestrow.csv](katalog-rejestrow.csv), [alarmy-kody.csv](alarmy-kody.csv), [strona katalogu](https://gieoerzet.github.io/PelletCAN/katalog.html).
