# Wiazania widget -> PID (PID-diff, poziom dostepu 0)


## wezel 9_screen — 72 widgetow w inwentarzu, 19 PID-ow ekranu

| PID | nazwa | klasa | widget | pozycja | zasob statyczny | regula (wartosc -> stan) |
|---|---|---|---|---|---|---|
| 0x200A | Remote boiler 1 temp[dC] | live | 0x20016bac | 150,100 70x50 | tekst '#' | 0 -> vis=0 '0.0°'; 1500 -> vis=0 '150.0°'; 750 -> vis=0 '75.0°'; 1 -> vis=0 '0.1°' |
| 0x200B | Remote boiler 2 temp[dC] | live | 0x20016d48 | 250,100 70x50 | tekst '#' | 0 -> vis=1 '0.0°'; 1500 -> vis=1 '150.0°'; 750 -> vis=1 '75.0°'; 1 -> vis=1 '0.1°' |
| 0x200C | Remote boiler 3 temp[dC] | live | 0x20016ee4 | 350,100 70x50 | tekst '#' | 0 -> vis=0 '0.0°'; 1500 -> vis=0 '150.0°'; 750 -> vis=0 '75.0°'; 1 -> vis=0 '0.1°' |
| 0x200D | Remote boiler 1 requested temp[C] | live | 0x20016be4 | 175,90 45x50 | tekst '#' | 0 -> vis=1 '0°'; 255 -> vis=1 '255°'; 127 -> vis=1 '127°'; 1 -> vis=1 '1°' |
| 0x200E | Remote boiler 2 requested temp[C] | live | 0x20016d80 | 275,90 45x50 | tekst '#' | 0 -> vis=1 '0°'; 255 -> vis=1 '255°'; 127 -> vis=1 '127°'; 1 -> vis=1 '1°' |
| 0x200F | Remote boiler 3 requested temp[C] | live | 0x20016f1c | 375,90 45x50 | tekst '#' | 0 -> vis=1 '0°'; 255 -> vis=1 '255°'; 127 -> vis=1 '127°'; 1 -> vis=1 '1°' |
| 0x350C | Is this device cascade master | setting | 0x200168ec | 205,195 200x70 | tekst 'Stopień mocy #' | 0 -> vis=0 '0'; 1 -> vis=1 '0' |
| 0x350C | Is this device cascade master | setting | 0x2001697c | 50,50 70x150 |  | 0 -> vis=0; 1 -> vis=1 |
| 0x350C | Is this device cascade master | setting | 0x20016b18 | 150,50 70x150 |  | 0 -> vis=0; 1 -> vis=1 |
| 0x3511 | Cascade master power level | setting | 0x20016a80 | 80,150 45x50 | tekst '#' | 1 -> vis=1 '1'; 2 -> vis=1 '2'; 3 -> vis=1 '3'; 4 -> vis=1 '4' |
| 0x3512 | Cascade slave 1 power level | setting | 0x20016c1c | 180,150 45x50 | tekst '#' | 1 -> vis=1 '1'; 2 -> vis=1 '2'; 3 -> vis=1 '3'; 4 -> vis=1 '4' |
| 0x3513 | Cascade slave 2 power level | setting | 0x20016db8 | 280,150 45x50 | tekst '#' | 1 -> vis=1 '1'; 2 -> vis=1 '2'; 3 -> vis=1 '3'; 4 -> vis=1 '4' |
| 0x3514 | Cascade slave 3 power level | setting | 0x20016f54 | 380,150 45x50 | tekst '#' | 1 -> vis=1 '1'; 2 -> vis=1 '2'; 3 -> vis=1 '3'; 4 -> vis=1 '4' |
| 0x3518 | Cascade time to dec power lvel [min] | setting | 0x20016924 | 320,195 200x70 | tekst '#' | 0 -> vis=0 '00:00:00'; 240 -> vis=0 '00:04:00'; 120 -> vis=0 '00:02:00'; 1 -> vis=0 '00:00:01' |
| 0x3519 | Cascade current power lvel | live | 0x200168ec | 205,195 200x70 | tekst 'Stopień mocy #' | 0 -> vis=1 '0'; 255 -> vis=1 '255'; 127 -> vis=1 '127'; 1 -> vis=1 '1' |
| 0x351A | Cascade slaves number | setting | 0x20016cb4 | 250,50 70x150 |  | 1 -> vis=0; 2 -> vis=1; 3 -> vis=1 |
| 0x351A | Cascade slaves number | setting | 0x20016e50 | 350,50 70x150 |  | 1 -> vis=0; 2 -> vis=0; 3 -> vis=1 |
| 0x351B | Cascade timer to inc power lvel [s] | live | 0x20016894 | 460,205 10x9 | bitmapa 68 | 0 -> vis=0 bmp=68; 65535 -> vis=1 bmp=68; 32767 -> vis=1 bmp=68; 1 -> vis=1 bmp=68; 5678 -> vis=1 bmp=68 |
| 0x351B | Cascade timer to inc power lvel [s] | live | 0x20016924 | 320,195 200x70 | tekst '#' | 0 -> vis=0 '00:00:30'; 65535 -> vis=1 '00:30:01'; 32767 -> vis=1 '09:36:09'; 1 -> vis=1 '00:29:59'; 5678 -> vis=1 '017:07:3' |
| 0x351C | Cascade timer to dec power lvel [s] | live | 0x200168c0 | 460,205 10x9 | bitmapa 25 | 0 -> vis=0 bmp=25; 65535 -> vis=1 bmp=25; 32767 -> vis=1 bmp=25; 1 -> vis=1 bmp=25; 5678 -> vis=1 bmp=25 |
| 0x351C | Cascade timer to dec power lvel [s] | live | 0x20016924 | 320,195 200x70 | tekst '#' | 0 -> vis=0 '00:00:30'; 65535 -> vis=1 '00:30:01'; 32767 -> vis=1 '09:36:09'; 1 -> vis=1 '00:29:59'; 5678 -> vis=1 '017:07:3' |
| 0x400A | Virt. energy consumer set temp [C] | command | 0x20016a48 | 75,90 45x50 | tekst '#' | 7 -> vis=1 '7°'; 150 -> vis=1 '150°'; 78 -> vis=1 '78°' |

PID-y czytane na ekranie bez zmiany widgetow w tescie (live/zablokowane/zaleznosc warunkowa): 0x2001 Boiler temp[dC] (live); 0x3517 Cascade time to inc power lvel [min] (setting)


## wezel 10_screen — 47 widgetow w inwentarzu, 5 PID-ow ekranu

| PID | nazwa | klasa | widget | pozycja | zasob statyczny | regula (wartosc -> stan) |
|---|---|---|---|---|---|---|
| 0x3529 | Ext. fuel storage reserve sensor | setting | 0x200169bc | 370,157 11x21 | bitmapa 29 | 0 -> vis=0 bmp=29; 1 -> vis=1 bmp=29 |

PID-y czytane na ekranie bez zmiany widgetow w tescie (live/zablokowane/zaleznosc warunkowa): 0x3522 External fuel storage motor 1 state (live); 0x3523 External fuel storage motor 2 state (live); 0x3524 External fuel storage level sens. state (live); 0x352A Ext. fuel stor. reserve sens. state (live)
