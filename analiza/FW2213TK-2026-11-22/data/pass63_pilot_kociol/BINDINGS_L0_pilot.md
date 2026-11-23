# Wiazania widget -> PID (PID-diff, poziom dostepu 0)


## wezel 0_screen — 52 widgetow w inwentarzu, 14 PID-ow ekranu

| PID | nazwa | klasa | widget | pozycja | zasob statyczny | regula (wartosc -> stan) |
|---|---|---|---|---|---|---|
| 0x2002 | Boiler program | setting | 0x20016918 | 398,53 35x37 | bitmapa 122 | 0 -> vis=1 bmp=133; 3 -> vis=1 bmp=128; 1 -> vis=1 bmp=135 |
| 0x2002 | Boiler program | setting | 0x200169ec | 358,53 36x44 | tekst '#' | 0 -> vis=1 '7'; 3 -> vis=1 '65'; 1 -> vis=1 '65' |
| 0x2005 | Boiler on/off | setting | 0x20016918 | 398,53 35x37 | bitmapa 122 | 0 -> vis=1 bmp=120; 1 -> vis=1 bmp=122 |
| 0x216F | CH mixer state | live | 0x20016acc | 81,234 34x30 |  | 0 -> vis=0; 2 -> vis=1; 1 -> vis=1 |
| 0x216F | CH mixer state | live | 0x20016b24 | 100,234 15x4 | bitmapa 107 | 0 -> vis=1 bmp=107; 2 -> vis=1 bmp=107; 1 -> vis=1 bmp=106 rect=[0, 0, 15, 4] |
| 0x350A | Return to boiler temperature sensor | setting | 0x20016a24 | 230,180 200x70 | tekst 'T. powrotu=#' | 0 -> vis=0 '0.70'; 1 -> vis=1 '0.0' |
| 0x350D | Pressure sensor | setting | 0x20016a94 | 80,180 200x70 | tekst 'Ciśnienie=#' | 0 -> vis=0 '0.70'; 1 -> vis=1 '0.0' |
| 0x3629 | Energy meter type | setting | 0x20016274 | 439,0 40x30 | tekst '#%' | 0 -> vis=1 '43'; 2 -> vis=1 '44'; 1 -> vis=1 '44' |
| 0x3629 | Energy meter type | setting | 0x20016a5c | 7,43 250x70 | tekst 'Energia łącznie [kWh]=#' | 0 -> vis=0 '0'; 2 -> vis=1 '0'; 1 -> vis=1 '0' |
| 0x370A | Boiler image selector | setting | 0x20016894 | 40,70 82x145 | bitmapa 13 | 1 -> vis=1 bmp=11; 3 -> vis=1 bmp=13 rect=[40, 70, 82, 145]; 2 -> vis=1 bmp=12 rect=[40, 70, 108, 141] |

PID-y czytane na ekranie bez zmiany widgetow w tescie (live/zablokowane/zaleznosc warunkowa): 0x2001 Boiler temp[dC] (live); 0x2004 Boiler set result temp[C] (live); 0x216A Exchanger cleaning request (live); 0x2277 Boiler pump state (live); 0x3333 Boiler pressure[mbar] (live); 0x3628 Statistics - total energy produced [kWh] (live); 0x4000 Boiler return temp [dC] (live)


## wezel 1_screen — 79 widgetow w inwentarzu, 27 PID-ow ekranu

| PID | nazwa | klasa | widget | pozycja | zasob statyczny | regula (wartosc -> stan) |
|---|---|---|---|---|---|---|
| 0x2123 | Lambda module presence | setting | 0x20016d18 | 270,150 200x70 | tekst 'tlen[%]=#' | 0 -> vis=0 '11.2'; 1 -> vis=1 '0.0' |
| 0x2250 | Burner brightness | live | 0x20016b90 | 270,125 200x70 | tekst 'jasność=#' | 0 -> vis=1 '0'; 100 -> vis=1 '100'; 50 -> vis=1 '50'; 1 -> vis=1 '1' |
| 0x2283 | Blower test | command | 0x200169f8 | 1,235 34x27 | bitmapa 8 | 0 -> vis=0 bmp=8; 2 -> vis=1 bmp=8; 1 -> vis=0 bmp=8 |
| 0x2283 | Blower test | command | 0x20016bc8 | 5,200 35x70 | tekst '#' | 0 -> vis=0 '16.0'; 2 -> vis=1 '100'; 1 -> vis=0 '16.0' |
| 0x3606 | Input IN17 config | setting | 0x20016ea0 | 160,125 200x70 | tekst 'spaliny[°C]=#' | 0 -> vis=0 '11'; 2 -> vis=1 '0'; 1 -> vis=0 '11' |
| 0x3710 | Fuel consumption [Dkg/h] | live | 0x20016ae8 | 270,50 200x70 | tekst 'spalanie[kg/h]=#' | 0 -> vis=1 '0.0'; 65535 -> vis=1 '6553.'; 32767 -> vis=1 '3276.'; 1 -> vis=1 '0.1'; 5678 -> vis=1 '567.8' |
| 0x4005 | Burner power [%] | live | 0x20016b20 | 270,100 200x70 | tekst 'moc[%]=#' | 0 -> vis=1 '0'; 100 -> vis=1 '100'; 50 -> vis=1 '50'; 1 -> vis=1 '1' |

PID-y czytane na ekranie bez zmiany widgetow w tescie (live/zablokowane/zaleznosc warunkowa): 0x2007 Burner state (live); 0x2119 Exhaust gas temperature (2) [C] (live); 0x2120 Lambda oxygen [%] (live); 0x2251 Burner storage feeder (live); 0x2252 Burner burner feeder (live); 0x2253 Burner igniter (live); 0x2254 Burner blower (live); 0x226C Burner feeder temperature [dC] (live); 0x226D Burner storage feeding time [dS] (live); 0x2276 Grate move indicator (live); 0x228C Exhaust fan power (live); 0x299C Burner blower RPM (live); 0x299D HALL Activated (setting); 0x300A Sec. air mixer position [%] (live); 0x300B Stop burning wood (command); 0x362B Airflow meter (setting); 0x3706 Current burner power [dkW] (live); 0x3711 Time to grate cleaning [min] (live); 0x371A Airflowmeter 1 flow (live); 0x4008 Burning type active (live)


## wezel 2_screen — 155 widgetow w inwentarzu, 21 PID-ow ekranu

| PID | nazwa | klasa | widget | pozycja | zasob statyczny | regula (wartosc -> stan) |
|---|---|---|---|---|---|---|
| 0x2064 | CH program | setting | 0x20017584 | 357,60 45x44 | tekst '#' | 0 -> vis=0 '7.0'; 3 -> vis=0 '21.0' rect=[357, 60, 63, 44]; 1 -> vis=0 '18.0' rect=[357, 60, 63, 44] |
| 0x2064 | CH program | setting | 0x20017694 | 429,195 49x32 | tekst '#°C' | 0 -> vis=1 '7'; 3 -> vis=1 '60'; 1 -> vis=1 '7' |
| 0x2064 | CH program | setting | 0x20017820 | 423,62 35x37 | bitmapa 130 | 0 -> vis=1 bmp=130; 3 -> vis=1 bmp=124; 1 -> vis=1 bmp=126 |
| 0x2126 | CH schedule monday | setting | 0x2001652c | 391,119 65x8 |  | 0 -> vis=1; 16777215 -> vis=1 rect=[1, 0, 96, 8]; 8388607 -> vis=1 rect=[1, 0, 93, 8]; 1 -> vis=1 rect=[1, 0, 5, 8]; 5678 -> vis=1 rect=[5, 0, 13, 8] |
| 0x2126 | CH schedule monday | setting | 0x2001655c | 431,119 0x8 |  | 0 -> vis=1; 16777215 -> vis=1; 8388607 -> vis=1; 1 -> vis=1; 5678 -> vis=1 rect=[21, 0, 5, 8] |
| 0x2126 | CH schedule monday | setting | 0x2001658c | 366,119 0x8 |  | 0 -> vis=1; 16777215 -> vis=1; 8388607 -> vis=1; 1 -> vis=1; 5678 -> vis=1 rect=[37, 0, 9, 8] |
| 0x2126 | CH schedule monday | setting | 0x200165bc | 366,119 0x8 |  | 0 -> vis=1; 16777215 -> vis=1; 8388607 -> vis=1; 1 -> vis=1; 5678 -> vis=1 rect=[49, 0, 5, 8] |
| 0x22A1 | Room temp sensor type | setting | 0x20016274 | 439,0 40x30 | tekst '#%' | 0 -> vis=1 '42'; 5 -> vis=1 '33'; 2 -> vis=1 '42'; 1 -> vis=1 '42' |
| 0x22A1 | Room temp sensor type | setting | 0x200162f8 | 9,239 19x19 | bitmapa 138 | 0 -> vis=1 bmp=138; 5 -> vis=0 bmp=138; 2 -> vis=1 bmp=138; 1 -> vis=1 bmp=138 |
| 0x22A1 | Room temp sensor type | setting | 0x20017584 | 357,60 45x44 | tekst '#' | 0 -> vis=0 '7.0'; 5 -> vis=1 '7.0'; 2 -> vis=1 '7.0'; 1 -> vis=1 '7.0' |
| 0x22A1 | Room temp sensor type | setting | 0x200175c8 | 235,52 109x73 | tekst '#' | 0 -> vis=0 '0.0'; 5 -> vis=1 '0.0'; 2 -> vis=1 '0.0'; 1 -> vis=1 '0.0' |
| 0x22A5 | CH sensor use | setting | 0x2001760c | 23,80 45x44 | tekst '#' | 0 -> vis=0 '0.0'; 1 -> vis=1 '0.0' |
| 0x22B9 | CH mixer state | live | 0x2001784c | 40,234 34x30 |  | 0 -> vis=0; 2 -> vis=1; 1 -> vis=1 |
| 0x22B9 | CH mixer state | live | 0x200178a4 | 59,234 15x4 | bitmapa 107 | 0 -> vis=1 bmp=107; 2 -> vis=1 bmp=107; 1 -> vis=1 bmp=106 rect=[0, 0, 15, 4] |
| 0x2309 | Room temp. radio sensor batt. volt [mV] | live | 0x2001771c | 268,45 40x15 | tekst '#mV' | 0 -> vis=1 '0'; 65535 -> vis=1 '65535'; 32767 -> vis=1 '32767'; 1 -> vis=1 '1'; 5678 -> vis=1 '5678' |
| 0x230D | Room temp. radio sensor signal [%] | live | 0x200176d8 | 238,45 26x15 | tekst '#%' | 0 -> vis=1 '0'; 255 -> vis=1 '255'; 127 -> vis=1 '127'; 1 -> vis=1 '1' |
| 0x2311 | Room temp. radio sensor time since lasr rec. | live | 0x20017764 | 313,45 29x15 | tekst '#s' | 0 -> vis=1 '0'; 65535 -> vis=1 '65535'; 32767 -> vis=1 '32767'; 1 -> vis=1 '1'; 5678 -> vis=1 '5678' |
| 0x2319 | Room temp. radio sensor soft. ver. before dot | live | 0x200177a8 | 358,45 20x15 | tekst '#' | 0 -> vis=1 'v0.0'; 255 -> vis=1 'v255.'; 127 -> vis=1 'v127.'; 1 -> vis=1 'v1.0' |
| 0x231D | Room temp. radio sensor soft. ver. after dot | live | 0x200177a8 | 358,45 20x15 | tekst '#' | 0 -> vis=1 'v0.0'; 255 -> vis=1 'v0.25'; 127 -> vis=1 'v0.12'; 1 -> vis=1 'v0.1' |
| 0x2321 | CH circuit name part1 | setting | 0x200181ac | 138,45 200x25 | tekst '#' | 0 -> vis=1 ''; 4294967295 -> vis=1 ''; 2147483647 -> vis=1 'ÿÿÿ'; 1 -> vis=1 ''; 5678 -> vis=1 '' |
| 0x4001 | CH temp measured | live | 0x2001760c | 23,80 45x44 | tekst '#' | -100 -> vis=0 '-10.0'; 1500 -> vis=0 '150.0' rect=[23, 80, 81, 44]; 700 -> vis=0 '70.0' rect=[23, 80, 63, 44]; 1 -> vis=0 '0.1' rect=[23, 80, 45, 44]; 0 -> vis=0 '0.0' rect=[23, 80, 45, 44] |
| 0x4001 | CH temp measured | live | 0x20017650 | 71,80 26x32 | tekst '#' | -100 -> vis=1 '70'; 1500 -> vis=1 '70' rect=[107, 80, 26, 32]; 700 -> vis=1 '70' rect=[89, 80, 26, 32]; 1 -> vis=1 '70' rect=[71, 80, 26, 32]; 0 -> vis=1 '70' rect=[71, 80, 26, 32] |

PID-y czytane na ekranie bez zmiany widgetow w tescie (live/zablokowane/zaleznosc warunkowa): 0x2016 Room measured temp (live); 0x2166 CH res [dC] (command); 0x2299 CH pump state (live); 0x22AD CH temp calc (live); 0x22F5 CH needed temp. [C] (live); 0x22FD CH status (live); 0x2301 CH thermostat state (live); 0x2325 CH circuit name part2 (setting); 0x2329 CH circuit name part3 (setting)


## wezel 6_screen — 135 widgetow w inwentarzu, 7 PID-ow ekranu

| PID | nazwa | klasa | widget | pozycja | zasob statyczny | regula (wartosc -> stan) |
|---|---|---|---|---|---|---|
| 0x2014 | Hot water 1 program | setting | 0x200174d0 | 423,67 35x37 | bitmapa 126 | 0 -> vis=1 bmp=130; 3 -> vis=1 bmp=124; 1 -> vis=1 bmp=126 |
| 0x201A | Hot water 1 result temperature | live | 0x2001743c | 352,65 63x44 | tekst '#' | 0 -> vis=1 '0'; 500 -> vis=1 '500'; 250 -> vis=1 '250'; 1 -> vis=1 '1' |
| 0x2154 | Hot water 1 schedule monday | setting | 0x2001652c | 391,119 65x8 |  | 0 -> vis=1; 16777215 -> vis=1 rect=[1, 0, 96, 8]; 8388607 -> vis=1 rect=[1, 0, 93, 8]; 1 -> vis=1 rect=[1, 0, 5, 8]; 5678 -> vis=1 rect=[5, 0, 13, 8] |
| 0x2154 | Hot water 1 schedule monday | setting | 0x2001655c | 431,119 0x8 |  | 0 -> vis=1; 16777215 -> vis=1; 8388607 -> vis=1; 1 -> vis=1; 5678 -> vis=1 rect=[21, 0, 5, 8] |
| 0x2154 | Hot water 1 schedule monday | setting | 0x2001658c | 366,119 0x8 |  | 0 -> vis=1; 16777215 -> vis=1; 8388607 -> vis=1; 1 -> vis=1; 5678 -> vis=1 rect=[37, 0, 9, 8] |
| 0x2154 | Hot water 1 schedule monday | setting | 0x200165bc | 366,119 0x8 |  | 0 -> vis=1; 16777215 -> vis=1; 8388607 -> vis=1; 1 -> vis=1; 5678 -> vis=1 rect=[49, 0, 5, 8] |

PID-y czytane na ekranie bez zmiany widgetow w tescie (live/zablokowane/zaleznosc warunkowa): 0x2110 Hot water 1 measured temperature (live); 0x2111 Hot water 1 needed temp. [C] (live); 0x2278 Hot water pump state (live); 0x3749 Hot water circular pump state (live)
