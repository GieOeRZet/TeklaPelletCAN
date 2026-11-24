# Kontrakt API <-> ui_model (E6)

Cel: ESP/karta HA/www/Android renderuja ekrany panelu Estyma z `ui_model` i zasilaja je danymi z istniejacego API urzadzenia TeklaPelletCAN. **Bez zmiany istniejacych endpointow i nazw encji** (CLAUDE.md pkt 6/8) - to opis warstwy mapujacej.

## 1. Podzial odpowiedzialnosci
| Warstwa | Zrodlo | Zawartosc |
|---|---|---|
| Struktura/wyglad (statyczna) | `ui_model/*.json` (menu_tree, lists, list_scales, program_screen, alarms, outputs_test, home_dialogs*, internet_editor) | drzewo menu, warunki widocznosci (`config_cond`, `level_min`), wiersze list: PID, nazwa EN, typ, zakres, skala/format, przyciski/dialogi |
| Wartosci (dynamiczne) | API urzadzenia `GET /api/v1/states?prefix=<slug>` (integracja `custom_components/teklapelletcan`, koordynator odpytuje) | `{id, domain, state, attributes{unit_of_measurement,device_class}}` na punkt z `rejestry/odczyty.csv` |
| Zapis | `POST /api/v1/call` (uslugi `teklapelletcan.<node>_<akcja>`), `POST /api/v1/write` | tylko punkty z `klucz_zapisu` (`rejestry/punkty.csv`), poziom zapisu wg `poziom` |
| Mapowanie PID -> punkt | `ui_model/pid_to_point.json` (generowane) | `pid` panelu -> `point_id` (= `id` w odczyty.csv) -> encja HA |

## 2. Reguly renderowania karty
1. Nawigacja wg `menu_tree.edges` (`from`,`to`,`tap`,`level_min`,`effect`); wiersze MENU wg `menu_rows` z filtrem `visible_in` (warunek konfiguracji `|L<poziom>`).
2. Lista (`lists.json`: klucz `0xNN|EKRAN|instN`): wiersz = `panel_key`, `pid`, `name_en`, `kind` (number/enum/switch/...), `raw_min/raw_max`, `level_min`; format wartosci z `list_scales.json` (`scale`, `decimals`, `display`, `samples` jako zrodlo prawdy dla formatowania).
3. Wartosc wiersza = `states[point_id].state` (PID -> point_id przez `pid_to_point.json`); brak punktu (`NO_DEVICE_POINT`) -> wyswietl `--` i nie oferuj edycji.
4. Edycja: dialog wg `kind` (liczbowy: zakres/krok z ui_model; enum: etykiety OPEN - uzyj `name_en` dopoki brak tablicy), zapis tylko gdy punkt ma `write_key` i poziom uzytkownika >= `level_min`.
5. ZAKAZ: karta nie wysyla zapisow bez jawnej akcji uzytkownika; tryb "dane przykladowe" w prototypie nie laczy sie z urzadzeniem.

## 3. Stan wiedzy / ograniczenia (OPEN)
- Etykiety enum, krok dialogu liczbowego, stany alarm/offline: `NewEstyma/BACKLOG.md`, `OPEN_POD_MUREM.md`.
- Mapowanie widget -> PID na HOME ~80%.


<!-- BEGIN GENERATED -->

## Pokrycie PID listy panelu -> punkty urzadzenia (generowane: tools/build_api_contract.py)

PID w listach ui_model: **144**; zmapowane na punkt odczytu/zapisu: **68**; bez punktu w urzadzeniu: **76**.

PID zrodel live (`live_sources.json`): 23, z czego z punktem odczytu: 6.

Brakujace (kandydaci do dodania w `rejestry/odczyty.csv`/`punkty.csv` - decyzja wlasciciela, to zmiana katalogu urzadzenia):

| PID | nazwa (EN) | listy |
|---|---|---|
| 0x3129 | Boiler min hydraulic pressure [0.1bar] | 0x00/KOCIOL/inst1 |
| 0x312A | Boiler max hydraulic pressure [0.1bar] | 0x00/KOCIOL/inst1 |
| 0x400C | CH temp for -10C [C] | 0x01/OGRZEWANIE/inst1, 0x02/OGRZEWANIE/inst1, 0x03/OGRZEWANI |
| 0x2315 | Automatic summer recognition | 0x01/OGRZEWANIE/inst1, 0x02/OGRZEWANIE/inst1, 0x03/OGRZEWANI |
| 0x2321 | CH circuit name part1 | 0x01/OGRZEWANIE/inst1, 0x02/OGRZEWANIE/inst1, 0x03/OGRZEWANI |
| 0x374B | Hot water 1 circular pump fork time | 0x05/CWU/inst1 |
| 0x374C | Hot water 1 circular pump pause time | 0x05/CWU/inst1 |
| 0x2116 | Solar flow [l/min] | 0x06/SOLARY/inst1 |
| 0x3116 | Solar delta on [C] | 0x06/SOLARY/inst1 |
| 0x3117 | Solar delta off [C] | 0x06/SOLARY/inst1 |
| 0x3118 | Solar liquid specific heat [kJ/(kg * C)] | 0x06/SOLARY/inst1 |
| 0x3119 | Solar temperature water max [C] | 0x06/SOLARY/inst1 |
| 0x311A | Solar temperature alarm max[C] | 0x06/SOLARY/inst1 |
| 0x311B | Solar temperature alarm min[C] | 0x06/SOLARY/inst1 |
| 0x2114 | Buffer top set temperature | 0x07/BUFOR/inst1 |
| 0x2115 | Buffer bottom set temperature | 0x07/BUFOR/inst1 |
| 0x2281 | Buffer minimal pump temperature | 0x07/BUFOR/inst1 |
| 0x2282 | Buffer is automatic top temperature | 0x07/BUFOR/inst1 |
| 0x299B |  | 0x07/BUFOR/inst1 |
| 0x3170 | Buffer pump delta min temperature | 0x07/BUFOR/inst1 |
| 0x3011 | Burner pwr. depend of buf. energy level | 0x07/BUFOR/inst1 |
| 0x351A | Cascade slaves number | 0x08/KASKADA/inst1 |
| 0x3511 | Cascade master power level | 0x08/KASKADA/inst1 |
| 0x3512 | Cascade slave 1 power level | 0x08/KASKADA/inst1 |
| 0x3513 | Cascade slave 2 power level | 0x08/KASKADA/inst1 |
| 0x3514 | Cascade slave 3 power level | 0x08/KASKADA/inst1 |
| 0x3515 | Cascade minimal energy [%] | 0x08/KASKADA/inst1 |
| 0x3516 | Cascade maximal energy [%] | 0x08/KASKADA/inst1 |
| 0x3517 | Cascade time to inc power lvel [min] | 0x08/KASKADA/inst1 |
| 0x3518 | Cascade time to dec power lvel [min] | 0x08/KASKADA/inst1 |
| 0x3520 | Ext. fuel storage motor 1 transport. time [s] | 0x09/MAGAZYN/inst1 |
| 0x3521 | Ext. fuel storage time [s] to empty transport. hose | 0x09/MAGAZYN/inst1 |
| 0x3527 | Ext. fuel storage feeder work time [s] | 0x09/MAGAZYN/inst1 |
| 0x3528 | Ext. fuel storage feeder pause time [s] | 0x09/MAGAZYN/inst1 |
| 0x3529 | Ext. fuel storage reserve sensor | 0x09/MAGAZYN/inst1 |
| 0x352B | Ext. fuel storage max cycles no. | 0x09/MAGAZYN/inst1 |
| 0x3526 | Ext. fuel storage motor 1 overrun time [s] | 0x09/MAGAZYN/inst1 |
| 0x225A | Pwr reg. speed | 0x0A/PALNIK/inst1 |
| 0x3720 | Outside temp. averaging period [h] | 0x10/KONFIGURACJA/inst1 |
| 0x372A | Summer time threshold temp. [C] | 0x10/KONFIGURACJA/inst1 |
| 0x3747 | Outside calibration [dC] | 0x10/KONFIGURACJA/inst1 |
| 0x3603 | Fuel reserve [kg] | 0x10/KONFIGURACJA/inst1 |
| 0x372F | Is automatic time synchronization | 0x10/KONFIGURACJA/inst1 |
| 0x3501 | Autoconfig activation | 0x10/KONFIGURACJA/inst1 |
| 0x3500 | Main module type | 0x10/KONFIGURACJA/inst1 |
| 0x3502 | CH expansion module type | 0x10/KONFIGURACJA/inst1 |
| 0x2105 | Heating configuration | 0x10/KONFIGURACJA/inst1 |
| 0x3505 | Outside temperature sensor configuration | 0x10/KONFIGURACJA/inst1 |
| 0x2106 | Hot water configuration | 0x10/KONFIGURACJA/inst1 |
| 0x2108 | Solar configuration | 0x10/KONFIGURACJA/inst1 |
| 0x2107 | Buffer configuration | 0x10/KONFIGURACJA/inst1 |
| 0x2123 | Lambda module presence | 0x10/KONFIGURACJA/inst1 |
| 0x3606 | Input IN17 config | 0x10/KONFIGURACJA/inst1 |
| 0x350A | Return to boiler temperature sensor | 0x10/KONFIGURACJA/inst1 |
| 0x350B | Profile number | 0x10/KONFIGURACJA/inst1 |
| 0x299E | Boiler pump work mode | 0x10/KONFIGURACJA/inst1 |
| 0x350C | Is this device cascade master | 0x10/KONFIGURACJA/inst1 |
| 0x350D | Pressure sensor | 0x10/KONFIGURACJA/inst1 |
| 0x3525 | Additional fuel storage | 0x10/KONFIGURACJA/inst1 |
| 0x3629 | Energy meter type | 0x10/KONFIGURACJA/inst1 |
| 0x3722 | Start settings recovery | 0x10/KONFIGURACJA/inst1 |
| 0x299D | HALL Activated | 0x10/KONFIGURACJA/inst1 |
| 0x404E | Request reset alarm memory | 0x10/KONFIGURACJA/inst1 |
| 0x3608 | Statistics - Ignition cnt | 0x11/STATYSTYKI/inst1 |
| 0x3609 | Statistics - Avg ignition time [s] | 0x11/STATYSTYKI/inst1 |
| 0x3610 | Statistics - Avg burner power [%] | 0x11/STATYSTYKI/inst1 |
| 0x3611 | Feeder 1 total work time [h] | 0x11/STATYSTYKI/inst1 |
| 0x3612 | Feeder 2 total work time [h] | 0x11/STATYSTYKI/inst1 |
| 0x3507 | Total fuel counter[kg] | 0x11/STATYSTYKI/inst1 |
| 0x3613 | Average oxygen for 30% pwr [%] | 0x11/STATYSTYKI/inst1 |
| 0x3614 | Average oxygen for 50% pwr [%] | 0x11/STATYSTYKI/inst1 |
| 0x3615 | Average oxygen for 70% pwr [%] | 0x11/STATYSTYKI/inst1 |
| 0x3616 | Average oxygen for 90% pwr [%] | 0x11/STATYSTYKI/inst1 |
| 0x3618 | Statistics - Exchanger cleaning count | 0x11/STATYSTYKI/inst1 |
| 0x3619 | Statistics - Boiler overheat count | 0x11/STATYSTYKI/inst1 |
| 0x362A | Statistics - reset count | 0x11/STATYSTYKI/inst1 |

<!-- END GENERATED -->
