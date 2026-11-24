# Wiazania widget -> PID (PID-diff, poziom dostepu 0)


## wezel 7_screen — 48 widgetow w inwentarzu, 6 PID-ow ekranu

| PID | nazwa | klasa | widget | pozycja | zasob statyczny | regula (wartosc -> stan) |
|---|---|---|---|---|---|---|

PID-y czytane na ekranie bez zmiany widgetow w tescie (live/zablokowane/zaleznosc warunkowa): 0x2101 Solar power [W] (live); 0x2102 Solar temperature 2 [C] (live); 0x2103 Solar temperature 3 [C] (live); 0x2109 Solar temperature 1 [C] (live); 0x311C Solar pump state (live); 0x3120 Solar status (live)


## wezel 8_screen — 51 widgetow w inwentarzu, 10 PID-ow ekranu

| PID | nazwa | klasa | widget | pozycja | zasob statyczny | regula (wartosc -> stan) |
|---|---|---|---|---|---|---|
| 0x2115 | Buffer bottom set temperature | setting | 0x20016924 | 320,143 67x44 | tekst '#°C' | 7 -> vis=1 '7'; 80 -> vis=1 '80'; 43 -> vis=1 '43' |
| 0x2115 | Buffer bottom set temperature | setting | 0x20016a74 | 75,118 138x32 | tekst '#%' | 7 -> vis=1 '100'; 80 -> vis=1 '0'; 43 -> vis=1 '0' |
| 0x2280 | Buffer top set temperature | live | 0x20016994 | 320,58 67x44 | tekst '#°C' | 25 -> vis=1 '25'; 80 -> vis=1 '80'; 52 -> vis=1 '52' |

PID-y czytane na ekranie bez zmiany widgetow w tescie (live/zablokowane/zaleznosc warunkowa): 0x2112 Buffer top measured temperature (live); 0x2113 Buffer bottom measured temperature (live); 0x2211  (live); 0x2277 Boiler pump state (live); 0x3171 Buffer T1 measured temperature (live); 0x3172 Buffer T2 measured temperature (live); 0x3173 Buffer T3 measured temperature (live); 0x3174 Buffer internal energy [%] (live)


## wezel 3_screen — 155 widgetow w inwentarzu, 21 PID-ow ekranu

| PID | nazwa | klasa | widget | pozycja | zasob statyczny | regula (wartosc -> stan) |
|---|---|---|---|---|---|---|
| 0x2065 | CH program | setting | 0x20017584 | 357,60 45x44 | tekst '#' | 0 -> vis=0 '7.0'; 1 -> vis=0 '18.0' rect=[357, 60, 63, 44]; 2 -> vis=0 '18.0' rect=[357, 60, 63, 44]; 3 -> vis=0 '21.0' rect=[357, 60, 63, 44] |
| 0x2065 | CH program | setting | 0x20017694 | 429,195 49x32 | tekst '#°C' | 0 -> vis=1 '7'; 1 -> vis=1 '7'; 2 -> vis=1 '7'; 3 -> vis=1 '60' |
| 0x2065 | CH program | setting | 0x20017820 | 423,62 35x37 | bitmapa 130 | 0 -> vis=1 bmp=130; 1 -> vis=1 bmp=126; 2 -> vis=1 bmp=132; 3 -> vis=1 bmp=124 |
| 0x2127 | CH schedule monday | setting | 0x2001652c | 391,119 65x8 |  | 0 -> vis=1; 16777215 -> vis=1 rect=[1, 0, 96, 8]; 8388607 -> vis=1 rect=[1, 0, 93, 8]; 1 -> vis=1 rect=[1, 0, 5, 8]; 5678 -> vis=1 rect=[5, 0, 13, 8] |
| 0x2127 | CH schedule monday | setting | 0x2001655c | 431,119 0x8 |  | 0 -> vis=1; 16777215 -> vis=1; 8388607 -> vis=1; 1 -> vis=1; 5678 -> vis=1 rect=[21, 0, 5, 8] |
| 0x2127 | CH schedule monday | setting | 0x2001658c | 366,119 0x8 |  | 0 -> vis=1; 16777215 -> vis=1; 8388607 -> vis=1; 1 -> vis=1; 5678 -> vis=1 rect=[37, 0, 9, 8] |
| 0x2127 | CH schedule monday | setting | 0x200165bc | 366,119 0x8 |  | 0 -> vis=1; 16777215 -> vis=1; 8388607 -> vis=1; 1 -> vis=1; 5678 -> vis=1 rect=[49, 0, 5, 8] |
| 0x22A2 | Room temp sensor type | setting | 0x20016274 | 439,0 40x30 | tekst '#%' | 0 -> vis=1 '42'; 1 -> vis=1 '42'; 2 -> vis=1 '42'; 3 -> vis=1 '42'; 4 -> vis=1 '42'; 5 -> vis=1 '32' |
| 0x22A2 | Room temp sensor type | setting | 0x200162f8 | 9,239 19x19 | bitmapa 138 | 0 -> vis=1 bmp=138; 1 -> vis=1 bmp=138; 2 -> vis=1 bmp=138; 3 -> vis=1 bmp=138; 4 -> vis=1 bmp=138; 5 -> vis=0 bmp=138 |
| 0x22A2 | Room temp sensor type | setting | 0x20016a7c | 255,70 60x22 | bitmapa 177 | 0 -> vis=0 bmp=177; 1 -> vis=0 bmp=177; 2 -> vis=0 bmp=177; 3 -> vis=0 bmp=177; 4 -> vis=1 bmp=177; 5 -> vis=0 bmp=177 |
| 0x22A2 | Room temp sensor type | setting | 0x20017584 | 357,60 45x44 | tekst '#' | 0 -> vis=0 '7.0'; 1 -> vis=1 '7.0'; 2 -> vis=1 '7.0'; 3 -> vis=1 '7.0'; 4 -> vis=0 '7.0'; 5 -> vis=1 '7.0' |
| 0x22A2 | Room temp sensor type | setting | 0x200175c8 | 235,52 109x73 | tekst '#' | 0 -> vis=0 '0.0'; 1 -> vis=1 '0.0'; 2 -> vis=1 '0.0'; 3 -> vis=1 '0.0'; 4 -> vis=0 '0.0'; 5 -> vis=1 '0.0' |
| 0x22A6 | CH sensor use | setting | 0x2001760c | 23,80 45x44 | tekst '#' | 0 -> vis=0 '0.0'; 1 -> vis=1 '0.0' |
| 0x22BA | CH mixer state | live | 0x2001784c | 40,234 34x30 |  | 0 -> vis=0; 1 -> vis=1; 2 -> vis=1 |
| 0x22BA | CH mixer state | live | 0x200178a4 | 59,234 15x4 | bitmapa 107 | 0 -> vis=1 bmp=107; 1 -> vis=1 bmp=106 rect=[0, 0, 15, 4]; 2 -> vis=1 bmp=107 |
| 0x230A | Room temp. radio sensor batt. volt [mV] | live | 0x2001771c | 268,45 40x15 | tekst '#mV' | 0 -> vis=1 '0'; 65535 -> vis=1 '65535'; 32767 -> vis=1 '32767'; 1 -> vis=1 '1'; 5678 -> vis=1 '5678' |
| 0x230E | Room temp. radio sensor signal [%] | live | 0x200176d8 | 238,45 26x15 | tekst '#%' | 0 -> vis=1 '0'; 255 -> vis=1 '255'; 127 -> vis=1 '127'; 1 -> vis=1 '1' |
| 0x2312 | Room temp. radio sensor time since lasr rec. | live | 0x20017764 | 313,45 29x15 | tekst '#s' | 0 -> vis=1 '0'; 65535 -> vis=1 '65535'; 32767 -> vis=1 '32767'; 1 -> vis=1 '1'; 5678 -> vis=1 '5678' |
| 0x231A | Room temp. radio sensor soft. ver. before dot | live | 0x200177a8 | 358,45 20x15 | tekst '#' | 0 -> vis=1 'v0.0'; 255 -> vis=1 'v255.'; 127 -> vis=1 'v127.'; 1 -> vis=1 'v1.0' |
| 0x231E | Room temp. radio sensor soft. ver. after dot | live | 0x200177a8 | 358,45 20x15 | tekst '#' | 0 -> vis=1 'v0.0'; 255 -> vis=1 'v0.25'; 127 -> vis=1 'v0.12'; 1 -> vis=1 'v0.1' |
| 0x2322 | CH circuit name part1 | setting | 0x200181ac | 138,45 200x25 | tekst '#' | 0 -> vis=1 ''; 4294967295 -> vis=1 ''; 2147483647 -> vis=1 'ÿÿÿ'; 1 -> vis=1 ''; 5678 -> vis=1 '' |
| 0x4002 | CH temp measured | live | 0x2001760c | 23,80 45x44 | tekst '#' | -100 -> vis=0 '-10.0'; 1500 -> vis=0 '150.0' rect=[23, 80, 81, 44]; 700 -> vis=0 '70.0' rect=[23, 80, 63, 44]; 1 -> vis=0 '0.1' rect=[23, 80, 45, 44]; 0 -> vis=0 '0.0' rect=[23, 80, 45, 44] |
| 0x4002 | CH temp measured | live | 0x20017650 | 71,80 26x32 | tekst '#' | -100 -> vis=1 '70'; 1500 -> vis=1 '70' rect=[107, 80, 26, 32]; 700 -> vis=1 '70' rect=[89, 80, 26, 32]; 1 -> vis=1 '70' rect=[71, 80, 26, 32]; 0 -> vis=1 '70' rect=[71, 80, 26, 32] |

PID-y czytane na ekranie bez zmiany widgetow w tescie (live/zablokowane/zaleznosc warunkowa): 0x2017 Room measured temp (live); 0x2167 CH res [dC] (command); 0x229A CH pump state (live); 0x22AE CH temp calc (live); 0x22F6 CH needed temp. [C] (live); 0x22FE CH status (live); 0x2302 CH thermostat state (live); 0x2326 CH circuit name part2 (setting); 0x232A CH circuit name part3 (setting)
