# SPECYFIKACJA POZIOMOW DOSTEPU 0 / 1 / 2 (do wdrozenia) — stan 2026-11-23
Zrodla: wykonanie firmware w emulatorze (zrzuty, budowniczy list `0x0804E714`, funkcja PIN `0x08047E74`, widocznosc menu `0x0804C178`). Poziom 3 (PIN 6154) i kod 6666 — poza zakresem (TODO).

## 1. Wprowadzanie PIN
- Wiersz menu "Poziom menu (PIN)" otwiera okno **"Wpisz PIN"**: 4 cyfry, nad kazda przycisk "+", pod kazda "-", przycisk OK. Pozycje przyciskow (ekran 480x272): "+" y=100, "-" y=230, kolumny x = 90 / 170 / 250 / 330; OK (415,230). Cyfra 0..9 (zawijanie nie sprawdzane).
- Po OK (`0x08047E74`): **0900 -> poziom 1**, **0999 -> poziom 2**, kod 0000 -> poziom 0; **kazdy inny kod nie zmienia poziomu** (nie sprawdzano komunikatu o bledzie — brak w kodzie). Poziom zapisany w modelu `+0x158`. (Zweryfikowane w emulatorze: 0900 -> poziom 1, naglowek "klucz 1".)
- Poziom nie jest zapamietywany w parametrach CAN; obowiazuje do zmiany.

## 2. Wspolne dla poziomow >= 1
- **Naglowek kazdego ekranu**: poziom 0 = ikona czlowieka; poziom >= 1 = ikona klucza z cyfra poziomu (1 lub 2) obok ikony domu.
- Menu glowne: poziom 0 = 13 wierszy (przy pelnej konfiguracji): Kociol, Palnik, Ogrzewanie obwod 1..4, Ciepla woda uzytkowa, Solary, Bufor, Historia alarmow, Informacje o programie, Konfiguracja, Poziom menu (PIN). Poziom >= 1 dodaje 6 wierszy: **Jezyk (Language)** [wartosc "PL"], **Alarm dzwiekowy** [przelacznik], **Test wyjsc**, **Statystyki**, **Siec**, **Internet**. Wiersze zalezne od konfiguracji (niezaleznie od poziomu): Ogrzewanie n (0x2105 >= n), CWU (0x2106), Solary (0x2108), Bufor (0x2107), Kaskada (0x350C), Dodatkowy magazyn paliwa (0x3525) — patrz PASS 52.
- Ekran glowny: identyczny na poziomach 0/1/2 (brak roznic).
- Ekran **Ogrzewanie 1..4 / Bufor / Ciepla woda** od poziomu >= 1: dodatkowe pola: Ogrzewanie — napis "Ochrona kotla" (TypedText 87) + temperatura zadana obiegu ("7°C" w emulatorze = PID 0x22F5 CH needed temp.); Bufor — "0%" po lewej zbiornika + temperatura w prawym dolnym rogu; Woda — temperatura w prawym dolnym rogu (zrodlo niezweryfikowane). Warunek pojawienia sie napisu "Ochrona kotla" NIEZWERYFIKOWANY.
- Dialog edycji wartosci i okno power: bez roznic miedzy poziomami.

## 3. Poziom 2 wzgledem poziomu 1
Roznice tylko w listach NASTAWY: **Palnik +4 pozycje**, **Konfiguracja +2** (HALL Activated, Request reset alarm memory). Pozostale ekrany identyczne z poziomem 1 (patrz tabele ponizej: "nowe wzgledem poprzedniego"). Naglowek: cyfra 2 zamiast 1.

## 4. Listy parametrow ekranow NASTAWY wg poziomu (generowane; `data/levels_0_1_2_spec.csv`)
Nazwy w kolumnie "nazwa" to nazwy rekordow firmware (angielskie); etykiety na ekranie sa polskie (TypedText) — mapowanie etykiet do kluczy: do dopracowania (kolejnosc wierszy = kolejnosc tabel; wartosc, jednostka i zakres min/max z `data/runtime_param_table_655.csv`). Klucze 0x47/0x48 = wykresy (Moc dmuchawy modulacja / Wentylator wspomagajacy), nie sa parametrami.
Zapis wartosci: dialog numeryczny -> CAN 0x584 `42 pidL pidH 01 val32` (patrz PASS 52).


## 0x00 — Kocioł

**Poziom 0** (razem 3, nowe wzgledem poprzedniego: 3)

| klucz | PID | nazwa |
|---|---|---|
| 0x000F | 0x2003 | Boiler set manual temp[C] |
| 0x0014 | 0x2208 | Boiler on histeresis |
| 0x0015 | 0x2291 | Boiler off histeresis |

**Poziom 1** (razem 12, nowe wzgledem poprzedniego: 9)

| klucz | PID | nazwa |
|---|---|---|
| 0x0011 | 0x2207 | Boiler minimal pump temperature |
| 0x0016 | 0x3708 | Boiler pump overrun [min] |
| 0x0118 | 0x3508 | Silence hours from |
| 0x0119 | 0x3509 | Silence hours to |
| 0x0026 | 0x216C | Boiler minimal return temperature |
| 0x0028 | 0x216E | Boiler mixer opening time [s] |
| 0x014B | 0x3604 | Fuel reserve [kg] |
| 0x002E | 0x3129 | Boiler min hydraulic pressure [0.1bar] |
| 0x002F | 0x312A | Boiler max hydraulic pressure [0.1bar] |

**Poziom 2** (razem 12, nowe wzgledem poprzedniego: 0)


## 0x01 — Ogrzewanie obwód 1..4 (instancje)

**Poziom 0** (razem 12, nowe wzgledem poprzedniego: 12)

| klucz | PID | nazwa |
|---|---|---|
| 0x00A9 | 0x2032 | CH comf temp set [dC] |
| 0x00AA | 0x2048 | CH eco temp set [dC] |
| 0x00BE | 0x22BD | Room temp hysteresis [C] |
| 0x00B1 | 0x22C1 | Room sensor cal [C] |
| 0x00AF | 0x2142 | CH mode |
| 0x00BC | 0x2146 | Tch set manual [C] |
| 0x00B4 | 0x22C5 | CH temp for -20C [C] |
| 0x00B5 | 0x400C | CH temp for -10C [C] |
| 0x00B6 | 0x22C9 | CH temp for 0C [C] |
| 0x00B7 | 0x22CD | CH temp for -20C [C] |
| 0x00D3 | 0x2315 | Automatic summer recognition |
| 0x00D4 | 0x2321 | CH circuit name part1 |

**Poziom 1** (razem 23, nowe wzgledem poprzedniego: 11)

| klucz | PID | nazwa |
|---|---|---|
| 0x00AD | 0x22D1 | CH source |
| 0x00AE | 0x22B1 | CH delta source [C] |
| 0x00B0 | 0x22A1 | Room temp sensor type |
| 0x00B3 | 0x22D5 | CH max temp [C] |
| 0x00B2 | 0x22A5 | CH sensor use |
| 0x00B8 | 0x22D9 | CH correction factor [C] |
| 0x00BA | 0x22E5 | CH temp lowering [C] |
| 0x00B9 | 0x22E9 | Min CH temp for pump [C] |
| 0x00BB | 0x22B5 | CH mixer opening time [s] |
| 0x00BD | 0x22F1 | Permament pump |
| 0x00CC | 0x22F9 | Tch lowering for energ. consumption reduction |

**Poziom 2** (razem 23, nowe wzgledem poprzedniego: 0)


## 0x02 — 

**Poziom 0** (razem 12, nowe wzgledem poprzedniego: 12)

| klucz | PID | nazwa |
|---|---|---|
| 0x00A9 | 0x2032 | CH comf temp set [dC] |
| 0x00AA | 0x2048 | CH eco temp set [dC] |
| 0x00BE | 0x22BD | Room temp hysteresis [C] |
| 0x00B1 | 0x22C1 | Room sensor cal [C] |
| 0x00AF | 0x2142 | CH mode |
| 0x00BC | 0x2146 | Tch set manual [C] |
| 0x00B4 | 0x22C5 | CH temp for -20C [C] |
| 0x00B5 | 0x400C | CH temp for -10C [C] |
| 0x00B6 | 0x22C9 | CH temp for 0C [C] |
| 0x00B7 | 0x22CD | CH temp for -20C [C] |
| 0x00D3 | 0x2315 | Automatic summer recognition |
| 0x00D4 | 0x2321 | CH circuit name part1 |

**Poziom 1** (razem 23, nowe wzgledem poprzedniego: 11)

| klucz | PID | nazwa |
|---|---|---|
| 0x00AD | 0x22D1 | CH source |
| 0x00AE | 0x22B1 | CH delta source [C] |
| 0x00B0 | 0x22A1 | Room temp sensor type |
| 0x00B3 | 0x22D5 | CH max temp [C] |
| 0x00B2 | 0x22A5 | CH sensor use |
| 0x00B8 | 0x22D9 | CH correction factor [C] |
| 0x00BA | 0x22E5 | CH temp lowering [C] |
| 0x00B9 | 0x22E9 | Min CH temp for pump [C] |
| 0x00BB | 0x22B5 | CH mixer opening time [s] |
| 0x00BD | 0x22F1 | Permament pump |
| 0x00CC | 0x22F9 | Tch lowering for energ. consumption reduction |

**Poziom 2** (razem 23, nowe wzgledem poprzedniego: 0)


## 0x03 — 

**Poziom 0** (razem 12, nowe wzgledem poprzedniego: 12)

| klucz | PID | nazwa |
|---|---|---|
| 0x00A9 | 0x2032 | CH comf temp set [dC] |
| 0x00AA | 0x2048 | CH eco temp set [dC] |
| 0x00BE | 0x22BD | Room temp hysteresis [C] |
| 0x00B1 | 0x22C1 | Room sensor cal [C] |
| 0x00AF | 0x2142 | CH mode |
| 0x00BC | 0x2146 | Tch set manual [C] |
| 0x00B4 | 0x22C5 | CH temp for -20C [C] |
| 0x00B5 | 0x400C | CH temp for -10C [C] |
| 0x00B6 | 0x22C9 | CH temp for 0C [C] |
| 0x00B7 | 0x22CD | CH temp for -20C [C] |
| 0x00D3 | 0x2315 | Automatic summer recognition |
| 0x00D4 | 0x2321 | CH circuit name part1 |

**Poziom 1** (razem 23, nowe wzgledem poprzedniego: 11)

| klucz | PID | nazwa |
|---|---|---|
| 0x00AD | 0x22D1 | CH source |
| 0x00AE | 0x22B1 | CH delta source [C] |
| 0x00B0 | 0x22A1 | Room temp sensor type |
| 0x00B3 | 0x22D5 | CH max temp [C] |
| 0x00B2 | 0x22A5 | CH sensor use |
| 0x00B8 | 0x22D9 | CH correction factor [C] |
| 0x00BA | 0x22E5 | CH temp lowering [C] |
| 0x00B9 | 0x22E9 | Min CH temp for pump [C] |
| 0x00BB | 0x22B5 | CH mixer opening time [s] |
| 0x00BD | 0x22F1 | Permament pump |
| 0x00CC | 0x22F9 | Tch lowering for energ. consumption reduction |

**Poziom 2** (razem 23, nowe wzgledem poprzedniego: 0)


## 0x04 — 

**Poziom 0** (razem 12, nowe wzgledem poprzedniego: 12)

| klucz | PID | nazwa |
|---|---|---|
| 0x00A9 | 0x2032 | CH comf temp set [dC] |
| 0x00AA | 0x2048 | CH eco temp set [dC] |
| 0x00BE | 0x22BD | Room temp hysteresis [C] |
| 0x00B1 | 0x22C1 | Room sensor cal [C] |
| 0x00AF | 0x2142 | CH mode |
| 0x00BC | 0x2146 | Tch set manual [C] |
| 0x00B4 | 0x22C5 | CH temp for -20C [C] |
| 0x00B5 | 0x400C | CH temp for -10C [C] |
| 0x00B6 | 0x22C9 | CH temp for 0C [C] |
| 0x00B7 | 0x22CD | CH temp for -20C [C] |
| 0x00D3 | 0x2315 | Automatic summer recognition |
| 0x00D4 | 0x2321 | CH circuit name part1 |

**Poziom 1** (razem 23, nowe wzgledem poprzedniego: 11)

| klucz | PID | nazwa |
|---|---|---|
| 0x00AD | 0x22D1 | CH source |
| 0x00AE | 0x22B1 | CH delta source [C] |
| 0x00B0 | 0x22A1 | Room temp sensor type |
| 0x00B3 | 0x22D5 | CH max temp [C] |
| 0x00B2 | 0x22A5 | CH sensor use |
| 0x00B8 | 0x22D9 | CH correction factor [C] |
| 0x00BA | 0x22E5 | CH temp lowering [C] |
| 0x00B9 | 0x22E9 | Min CH temp for pump [C] |
| 0x00BB | 0x22B5 | CH mixer opening time [s] |
| 0x00BD | 0x22F1 | Permament pump |
| 0x00CC | 0x22F9 | Tch lowering for energ. consumption reduction |

**Poziom 2** (razem 23, nowe wzgledem poprzedniego: 0)


## 0x05 — Ciepła woda użytkowa

**Poziom 0** (razem 8, nowe wzgledem poprzedniego: 8)

| klucz | PID | nazwa |
|---|---|---|
| 0x00D9 | 0x2010 | Hot water 1 comfort temperature |
| 0x00DA | 0x2012 | Hot water 1 economical temperature |
| 0x00DD | 0x2210 | Hot water 1 heat now |
| 0x00DE | 0x2212 | Hot water 1 histeresis |
| 0x00E3 | 0x2297 | HW1 anti legionella |
| 0x00E7 | 0x300D | Hot water priority |
| 0x00E5 | 0x374B | Hot water 1 circular pump fork time |
| 0x00E6 | 0x374C | Hot water 1 circular pump pause time |

**Poziom 1** (razem 12, nowe wzgledem poprzedniego: 4)

| klucz | PID | nazwa |
|---|---|---|
| 0x00DF | 0x2214 | Hot water 1 source |
| 0x00E0 | 0x2216 | Hot water 1 delta source |
| 0x00E2 | 0x2218 | Hot water 1 delta min temperature |
| 0x00E1 | 0x201C | Hot water 1 temperature max |

**Poziom 2** (razem 12, nowe wzgledem poprzedniego: 0)


## 0x06 — Solary

**Poziom 0** (razem 3, nowe wzgledem poprzedniego: 3)

| klucz | PID | nazwa |
|---|---|---|
| 0x0103 | 0x2116 | Solar flow [l/min] |
| 0x0104 | 0x3116 | Solar delta on [C] |
| 0x0105 | 0x3117 | Solar delta off [C] |

**Poziom 1** (razem 7, nowe wzgledem poprzedniego: 4)

| klucz | PID | nazwa |
|---|---|---|
| 0x0106 | 0x3118 | Solar liquid specific heat [kJ/(kg * C)] |
| 0x0107 | 0x3119 | Solar temperature water max [C] |
| 0x0108 | 0x311A | Solar temperature alarm max[C] |
| 0x0109 | 0x311B | Solar temperature alarm min[C] |

**Poziom 2** (razem 7, nowe wzgledem poprzedniego: 0)


## 0x07 — Bufor

**Poziom 0** (razem 2, nowe wzgledem poprzedniego: 2)

| klucz | PID | nazwa |
|---|---|---|
| 0x00F3 | 0x2114 | Buffer top set temperature |
| 0x00F4 | 0x2115 | Buffer bottom set temperature |

**Poziom 1** (razem 7, nowe wzgledem poprzedniego: 5)

| klucz | PID | nazwa |
|---|---|---|
| 0x00F6 | 0x2281 | Buffer minimal pump temperature |
| 0x00F7 | 0x2282 | Buffer is automatic top temperature |
| 0x009C | 0x299B |  |
| 0x009D | 0x3170 | Buffer pump delta min temperature |
| 0x00FC | 0x3011 | Burner pwr. depend of buf. energy level |

**Poziom 2** (razem 7, nowe wzgledem poprzedniego: 0)


## 0x08 — Kaskada (gdy 0x350C != 0)

**Poziom 0** (razem 9, nowe wzgledem poprzedniego: 9)

| klucz | PID | nazwa |
|---|---|---|
| 0x0158 | 0x351A | Cascade slaves number |
| 0x014D | 0x3511 | Cascade master power level |
| 0x014E | 0x3512 | Cascade slave 1 power level |
| 0x014F | 0x3513 | Cascade slave 2 power level |
| 0x0150 | 0x3514 | Cascade slave 3 power level |
| 0x0151 | 0x3515 | Cascade minimal energy [%] |
| 0x0152 | 0x3516 | Cascade maximal energy [%] |
| 0x0153 | 0x3517 | Cascade time to inc power lvel [min] |
| 0x0154 | 0x3518 | Cascade time to dec power lvel [min] |

**Poziom 1** (razem 9, nowe wzgledem poprzedniego: 0)

**Poziom 2** (razem 9, nowe wzgledem poprzedniego: 0)


## 0x09 — Dodatkowy magazyn paliwa (gdy 0x3525 != 0)

**Poziom 0** (razem 4, nowe wzgledem poprzedniego: 4)

| klucz | PID | nazwa |
|---|---|---|
| 0x015E | 0x3520 | Ext. fuel storage motor 1 transport. time [s] |
| 0x0160 | 0x3521 | Ext. fuel storage time [s] to empty transport. hose |
| 0x0163 | 0x3527 | Ext. fuel storage feeder work time [s] |
| 0x0164 | 0x3528 | Ext. fuel storage feeder pause time [s] |

**Poziom 1** (razem 7, nowe wzgledem poprzedniego: 3)

| klucz | PID | nazwa |
|---|---|---|
| 0x0161 | 0x3529 | Ext. fuel storage reserve sensor |
| 0x0165 | 0x352B | Ext. fuel storage max cycles no. |
| 0x015F | 0x3526 | Ext. fuel storage motor 1 overrun time [s] |

**Poziom 2** (razem 7, nowe wzgledem poprzedniego: 0)


## 0x0A — Palnik

**Poziom 0** (razem 5, nowe wzgledem poprzedniego: 5)

| klucz | PID | nazwa |
|---|---|---|
| 0x0054 | 0x2273 | Burner blower corretion |
| 0x0059 | 0x2270 | Min power |
| 0x005A | 0x2271 | Max power |
| 0x005D | 0x2292 | Fuel calorific [kWh/kg] |
| 0x005C | 0x2272 | Feeder rate [dkg/h] |

**Poziom 1** (razem 24, nowe wzgledem poprzedniego: 19)

| klucz | PID | nazwa |
|---|---|---|
| 0x0047 | 0x2254 | Burner blower |
| 0x0055 | 0x2257 | Max Feeding [s] |
| 0x0057 | 0x2256 | Pellet predose [s] |
| 0x0089 | 0x226A | Brightness threshold |
| 0x0076 | 0x2289 | Blower power during fire up |
| 0x0063 | 0x3704 | Blower power in incandescing [%] |
| 0x0065 | 0x300C | Blower power in burning off [%] |
| 0x0077 | 0x2290 | Incandescing time [min] |
| 0x0078 | 0x299A | Incandenscing fuel [%] |
| 0x008A | 0x226B | Burning off time [min] |
| 0x0069 | 0x3605 | Lambda oxygen control |
| 0x006F | 0x214E | Oxygen for 30% of power [%] |
| 0x0070 | 0x2152 | Oxygen for 100% of power [%] |
| 0x0073 | 0x2258 | Grate cleaning number |
| 0x008D | 0x2999 | Burner max continuous work time [h] |
| 0x00A5 | 0x3715 | Burner pause time [min] |
| 0x00A6 | 0x3716 | Burner pause power [%] |
| 0x00A7 | 0x3717 | Burner pause blower power [%] |
| 0x005B | 0x225A | Pwr reg. speed |

**Poziom 2** (razem 28, nowe wzgledem poprzedniego: 4)

| klucz | PID | nazwa |
|---|---|---|
| 0x0087 | 0x2153 | Burner inertia [min] |
| 0x0079 | 0x3003 | Grate move in modulation [0.1s] |
| 0x0091 | 0x370B | Burner feeder % of stor. feeder |
| 0x00A1 | 0x3700 | Storage feeder period [s] |


## 0x10 — Konfiguracja

**Poziom 0** (razem 5, nowe wzgledem poprzedniego: 5)

| klucz | PID | nazwa |
|---|---|---|
| 0x0125 | 0x3720 | Outside temp. averaging period [h] |
| 0x0008 | 0x372A | Summer time threshold temp. [C] |
| 0x0002 | 0x3747 | Outside calibration [dC] |
| 0x0149 | 0x3603 | Fuel reserve [kg] |
| 0x0126 | 0x372F | Is automatic time synchronization |

**Poziom 1** (razem 24, nowe wzgledem poprzedniego: 19)

| klucz | PID | nazwa |
|---|---|---|
| 0x0114 | 0x3501 | Autoconfig activation |
| 0x0112 | 0x3500 | Main module type |
| 0x0113 | 0x3502 | CH expansion module type |
| 0x010E | 0x2105 | Heating configuration |
| 0x010D | 0x3505 | Outside temperature sensor configuration |
| 0x010F | 0x2106 | Hot water configuration |
| 0x0110 | 0x2108 | Solar configuration |
| 0x0111 | 0x2107 | Buffer configuration |
| 0x0115 | 0x2123 | Lambda module presence |
| 0x0116 | 0x3606 | Input IN17 config |
| 0x0148 | 0x3600 | Tank capacity [kg] |
| 0x011A | 0x350A | Return to boiler temperature sensor |
| 0x011B | 0x350B | Profile number |
| 0x0012 | 0x299E | Boiler pump work mode |
| 0x011C | 0x350C | Is this device cascade master |
| 0x011D | 0x350D | Pressure sensor |
| 0x0122 | 0x3525 | Additional fuel storage |
| 0x011F | 0x3629 | Energy meter type |
| 0x0133 | 0x3722 | Start settings recovery |

**Poziom 2** (razem 26, nowe wzgledem poprzedniego: 2)

| klucz | PID | nazwa |
|---|---|---|
| 0x0090 | 0x299D | HALL Activated |
| 0x016A | 0x404E | Request reset alarm memory |


## 0x11 — Statystyki

**Poziom 0** (razem 13, nowe wzgledem poprzedniego: 13)

| klucz | PID | nazwa |
|---|---|---|
| 0x019A | 0x3608 | Statistics - Ignition cnt |
| 0x019B | 0x3609 | Statistics - Avg ignition time [s] |
| 0x019C | 0x3610 | Statistics - Avg burner power [%] |
| 0x019D | 0x3611 | Feeder 1 total work time [h] |
| 0x019E | 0x3612 | Feeder 2 total work time [h] |
| 0x019F | 0x3507 | Total fuel counter[kg] |
| 0x01A0 | 0x3613 | Average oxygen for 30% pwr [%] |
| 0x01A1 | 0x3614 | Average oxygen for 50% pwr [%] |
| 0x01A2 | 0x3615 | Average oxygen for 70% pwr [%] |
| 0x01A3 | 0x3616 | Average oxygen for 90% pwr [%] |
| 0x01A5 | 0x3618 | Statistics - Exchanger cleaning count |
| 0x01A6 | 0x3619 | Statistics - Boiler overheat count |
| 0x01A7 | 0x362A | Statistics - reset count |

**Poziom 1** (razem 13, nowe wzgledem poprzedniego: 0)

**Poziom 2** (razem 13, nowe wzgledem poprzedniego: 0)
