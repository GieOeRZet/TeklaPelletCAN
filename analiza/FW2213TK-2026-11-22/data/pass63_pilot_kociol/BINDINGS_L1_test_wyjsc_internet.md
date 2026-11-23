# Wiazania widget -> PID (PID-diff, poziom dostepu 0)


## wezel 15_screen — 346 widgetow w inwentarzu, 24 PID-ow ekranu

| PID | nazwa | klasa | widget | pozycja | zasob statyczny | regula (wartosc -> stan) |
|---|---|---|---|---|---|---|
| 0x2286 | Boiler pump test | command | 0x20016274 | 439,0 40x30 | tekst '#%' | 0 -> vis=1 '47'; 1 -> vis=1 '45'; 2 -> vis=1 '47' |
| 0x2288 | Blower test power | command | 0x200192e8 | 289,614 33x33 | bitmapa 70 | 0 -> vis=1 bmp=70; 100 -> vis=1 bmp=70 rect=[164, 0, 33, 33]; 50 -> vis=1 bmp=70 rect=[82, 0, 33, 33]; 1 -> vis=1 bmp=70 rect=[1, 0, 33, 33] |
| 0x2288 | Blower test power | command | 0x20019314 | 137,624 168x11 |  | 0 -> vis=1; 100 -> vis=1 rect=[9, 10, 171, 11]; 50 -> vis=1 rect=[9, 10, 89, 11]; 1 -> vis=1 rect=[9, 10, 8, 11] |
| 0x2298 | Exhaust fan test power | command | 0x200196f8 | 208,664 33x33 | bitmapa 70 | 0 -> vis=1 bmp=70; 100 -> vis=1 bmp=70 rect=[164, 0, 33, 33]; 50 -> vis=1 bmp=70 rect=[82, 0, 33, 33]; 1 -> vis=1 bmp=70 rect=[1, 0, 33, 33] |
| 0x2298 | Exhaust fan test power | command | 0x20019724 | 137,674 87x11 |  | 0 -> vis=1; 100 -> vis=1 rect=[9, 10, 171, 11]; 50 -> vis=1 rect=[9, 10, 89, 11]; 1 -> vis=1 rect=[9, 10, 8, 11] |
| 0x374A | HW1 circular pump test | command | 0x20016274 | 439,0 40x30 | tekst '#%' | 0 -> vis=1 '47'; 1 -> vis=1 '45'; 2 -> vis=1 '45' |

PID-y czytane na ekranie bez zmiany widgetow w tescie (live/zablokowane/zaleznosc warunkowa): 0x214A CH mixer test (command); 0x214B CH mixer test (command); 0x214C CH mixer test (command); 0x214D CH mixer test (command); 0x216D Boiler return mixer test (command); 0x2259 Burner storage feeder test (command); 0x2279 Burner grate test (command); 0x2283 Blower test (command); 0x2284 Igniter test (command); 0x2285 Exchanger cleaner test (command); 0x2293 Exhaust fan test (command); 0x2295 Burner feeder test (command); 0x2296 HW1 pump test (command); 0x229D CH pump test (command); 0x229E CH pump test (command); 0x229F CH pump test (command); 0x22A0 CH pump test (command); 0x311F Solar pump test (command); 0x351E External fuel storage motor 1 test (command); 0x351F External fuel storage motor 2 test (command)


## wezel 18_screen — 74 widgetow w inwentarzu, 8 PID-ow ekranu

| PID | nazwa | klasa | widget | pozycja | zasob statyczny | regula (wartosc -> stan) |
|---|---|---|---|---|---|---|
| 0x373D |  | live | 0x20016ba4 | 435,50 32x23 | bitmapa 154 | 0 -> vis=0 bmp=153; 255 -> vis=0 bmp=153; 127 -> vis=0 bmp=153; 1 -> vis=1 bmp=153 |
| 0x373E |  | setting | 0x20016fc8 | 155,168 33x33 | bitmapa 70 | 0 -> vis=1 bmp=70; 255 -> vis=1 bmp=70 rect=[29, 0, 33, 33]; 127 -> vis=1 bmp=70 rect=[29, 0, 33, 33]; 1 -> vis=1 bmp=70 rect=[29, 0, 33, 33] |
| 0x373E |  | setting | 0x20016ff4 | 164,173 7x20 |  | 0 -> vis=1; 255 -> vis=1 rect=[9, 5, 36, 20]; 127 -> vis=1 rect=[9, 5, 36, 20]; 1 -> vis=1 rect=[9, 5, 36, 20] |
| 0x373F |  | live | 0x20016d98 | 35,110 190x25 | tekst '#' | 0 -> vis=1 'SERIAL:'; 4294967295 -> vis=1 'SERIAL:'; 2147483647 -> vis=1 'SERIAL: 2147483647'; 1 -> vis=1 'SERIAL: 1'; 5678 -> vis=1 'SERIAL: 5678' |
| 0x3740 |  | live | 0x20016d60 | 35,140 120x25 | tekst '#' | 0 -> vis=1 'PIN:'; 4294967295 -> vis=1 'PIN:'; 2147483647 -> vis=1 'PIN: 214748'; 1 -> vis=1 'PIN: 1'; 5678 -> vis=1 'PIN: 5678' |
| 0x3746 |  | live | 0x20016cb8 | 428,70 33x15 | tekst '#' | 0 -> vis=0 'mqtt'; 255 -> vis=1 'mqtt'; 127 -> vis=1 'mqtt'; 1 -> vis=0 'mqtt' |

PID-y czytane na ekranie bez zmiany widgetow w tescie (live/zablokowane/zaleznosc warunkowa): 0x373C  (live); 0x3744  (live); 0x3745  (live)
