# Wiazania widget -> PID (PID-diff, poziom dostepu 0)


## wezel 0_screen — 52 widgetow w inwentarzu, 3 PID-ow ekranu

| PID | nazwa | klasa | widget | pozycja | zasob statyczny | regula (wartosc -> stan) |
|---|---|---|---|---|---|---|
| 0x2001 | Boiler temp[dC] | live | 0x200169b4 | 180,65 157x104 | tekst '#' | 100 -> vis=1 '9.9'; 400 -> vis=1 '39.9'; 650 -> vis=1 '64.9'; 900 -> vis=1 '89.8' |
| 0x2110 | Hot water 1 measured temperature | live | 0x20016274 | 439,0 40x30 | tekst '#%' | 100 -> vis=1 '42'; 400 -> vis=1 '42'; 650 -> vis=1 '42'; 900 -> vis=1 '44' |

PID-y czytane na ekranie bez zmiany widgetow w tescie (live/zablokowane/zaleznosc warunkowa): 0x215F Outside temperature (live)


## wezel 6_screen — 135 widgetow w inwentarzu, 2 PID-ow ekranu

| PID | nazwa | klasa | widget | pozycja | zasob statyczny | regula (wartosc -> stan) |
|---|---|---|---|---|---|---|
| 0x2110 | Hot water 1 measured temperature | live | 0x20017404 | 180,50 157x104 | tekst '#' | 100 -> vis=1 '9.9'; 400 -> vis=1 '39.9'; 650 -> vis=1 '64.9'; 900 -> vis=1 '89.8' |
| 0x2110 | Hot water 1 measured temperature | live | 0x20017474 | 429,195 49x32 | tekst '#°C' | 100 -> vis=1 '35'; 400 -> vis=1 '7'; 650 -> vis=1 '7'; 900 -> vis=1 '7' |

PID-y czytane na ekranie bez zmiany widgetow w tescie (live/zablokowane/zaleznosc warunkowa): 0x2001 Boiler temp[dC] (live)


## wezel 7_screen — 48 widgetow w inwentarzu, 4 PID-ow ekranu

| PID | nazwa | klasa | widget | pozycja | zasob statyczny | regula (wartosc -> stan) |
|---|---|---|---|---|---|---|
| 0x2109 | Solar temperature 1 [C] | live | 0x20016274 | 439,0 40x30 | tekst '#%' | 100 -> vis=1 '43'; 400 -> vis=1 '43'; 650 -> vis=1 '36'; 900 -> vis=1 '36' |
| 0x2109 | Solar temperature 1 [C] | live | 0x20016978 | 0,52 90x44 | tekst '#' | 100 -> vis=1 '9.9'; 400 -> vis=1 '39.9'; 650 -> vis=1 '64.9'; 900 -> vis=1 '89.8' |
| 0x2109 | Solar temperature 1 [C] | live | 0x20016a20 | 258,154 480x44 | tekst 'P=#W' | 100 -> vis=1 '0'; 400 -> vis=1 '0'; 650 -> vis=1 '4166'; 900 -> vis=1 '8316' |
| 0x2102 | Solar temperature 2 [C] | live | 0x20016274 | 439,0 40x30 | tekst '#%' | 100 -> vis=1 '37'; 400 -> vis=1 '43'; 650 -> vis=1 '43'; 900 -> vis=1 '36' |
| 0x2102 | Solar temperature 2 [C] | live | 0x200169e8 | 256,57 480x73 | tekst '#' | 100 -> vis=1 '9.9'; 400 -> vis=1 '39.9'; 650 -> vis=1 '64.9'; 900 -> vis=1 '89.8' |
| 0x2103 | Solar temperature 3 [C] | live | 0x200169b0 | 0,168 150x44 | tekst '#' | 100 -> vis=1 '9.9'; 400 -> vis=1 '39.9'; 650 -> vis=1 '64.9'; 900 -> vis=1 '89.8' |

PID-y czytane na ekranie bez zmiany widgetow w tescie (live/zablokowane/zaleznosc warunkowa): 0x2104 Solar temperature 4 [C] (live)


## wezel 8_screen — 51 widgetow w inwentarzu, 5 PID-ow ekranu

| PID | nazwa | klasa | widget | pozycja | zasob statyczny | regula (wartosc -> stan) |
|---|---|---|---|---|---|---|
| 0x2112 | Buffer top measured temperature | live | 0x2001695c | 0,50 300x73 | tekst '#' | 100 -> vis=1 '9.9'; 400 -> vis=1 '39.9'; 650 -> vis=1 '64.9'; 900 -> vis=1 '89.8' |
| 0x2112 | Buffer top measured temperature | live | 0x20016a74 | 75,118 138x32 | tekst '#%' | 100 -> vis=1 '22'; 400 -> vis=1 '37'; 650 -> vis=1 '49'; 900 -> vis=1 '62' |
| 0x2112 | Buffer top measured temperature | live | 0x20016aac | 416,195 62x32 | tekst '#°C' | 100 -> vis=1 '85'; 400 -> vis=1 '85'; 650 -> vis=1 '7'; 900 -> vis=1 '7' |
| 0x2113 | Buffer bottom measured temperature | live | 0x200168ec | 0,135 300x73 | tekst '#' | 100 -> vis=1 '9.9'; 400 -> vis=1 '39.9'; 650 -> vis=1 '64.9'; 900 -> vis=1 '89.8' |
| 0x2113 | Buffer bottom measured temperature | live | 0x20016a74 | 75,118 138x32 | tekst '#%' | 100 -> vis=1 '22'; 400 -> vis=1 '37'; 650 -> vis=1 '49'; 900 -> vis=1 '62' |
| 0x3171 | Buffer T1 measured temperature | live | 0x200169cc | 0,80 76x32 | tekst '#°C' | 100 -> vis=0 '9.9'; 400 -> vis=0 '39.9'; 650 -> vis=0 '64.9'; 900 -> vis=0 '89.8' |
| 0x3171 | Buffer T1 measured temperature | live | 0x20016a74 | 75,118 138x32 | tekst '#%' | 100 -> vis=1 '22'; 400 -> vis=1 '37'; 650 -> vis=1 '49'; 900 -> vis=1 '62' |
| 0x3172 | Buffer T2 measured temperature | live | 0x20016a04 | 0,120 76x32 | tekst '#°C' | 100 -> vis=0 '9.9'; 400 -> vis=0 '39.9'; 650 -> vis=0 '64.9'; 900 -> vis=0 '89.8' |
| 0x3172 | Buffer T2 measured temperature | live | 0x20016a74 | 75,118 138x32 | tekst '#%' | 100 -> vis=1 '22'; 400 -> vis=1 '37'; 650 -> vis=1 '49'; 900 -> vis=1 '62' |
| 0x3173 | Buffer T3 measured temperature | live | 0x20016a3c | 0,160 76x32 | tekst '#°C' | 100 -> vis=0 '9.9'; 400 -> vis=0 '39.9'; 650 -> vis=0 '64.9'; 900 -> vis=0 '89.8' |
| 0x3173 | Buffer T3 measured temperature | live | 0x20016a74 | 75,118 138x32 | tekst '#%' | 100 -> vis=1 '22'; 400 -> vis=1 '37'; 650 -> vis=1 '49'; 900 -> vis=1 '62' |

PID-y czytane na ekranie bez zmiany widgetow w tescie (live/zablokowane/zaleznosc warunkowa): brak


## wezel home — 280 widgetow w inwentarzu, 3 PID-ow ekranu

| PID | nazwa | klasa | widget | pozycja | zasob statyczny | regula (wartosc -> stan) |
|---|---|---|---|---|---|---|
| 0x2001 | Boiler temp[dC] | live | 0x2001b360 | 180,35 157x104 | tekst '#' | 100 -> vis=1 '9.9'; 650 -> vis=1 '64.9' |
| 0x215F | Outside temperature | live | 0x20016638 | 360,7 38x21 | bitmapa 181 | 100 -> vis=0 bmp=181; 650 -> vis=0 bmp=180 |

PID-y czytane na ekranie bez zmiany widgetow w tescie (live/zablokowane/zaleznosc warunkowa): 0x2110 Hot water 1 measured temperature (live)
