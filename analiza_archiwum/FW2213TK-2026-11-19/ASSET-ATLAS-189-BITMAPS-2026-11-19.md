# ASSET ATLAS — 189 firmware bitmaps — 2026-11-19

Source: web/img/panel/. The extraction is documented as 189 PNG assets originating from the firmware bitmap table around runtime 0x08054450.
Numbered assets: 000.png through 187.png (188 assets) plus 76b.png (1 asset).

## Confirmed bottom-bar mapping
The real user screen confirms seven logical bottom zones. Zone 4 is CO1. Zone 5 is empty when one CO circuit is configured and becomes CO2 when two CO circuits are configured.
144.png = CO1 active, 41x36, white radiator with 1.
145.png = CO1 alternate/inactive rendering, 41x36.
146.png = CO2 active, 43x36, white radiator with 2.
147.png = CO2 alternate/inactive rendering, 43x36.

## Other immediately identifiable assets
079 = 480x45 header background.
077 = MENU icon.
094 = tap/water icon.
096 = information icon.
097 = messages/dialog icon.
098 = service/wrench icon.
099 = user/profile icon.
100 = network/topology icon.
101 = user/lock icon.
102/103 = 155x38 button backgrounds.
110/111/119 = 52x36 button family.
115 = power icon.
148/149/150 = radiator/boiler construction pieces.
157 = schedule axis.
160/161 = schedule/cycle buttons.
163/165/167 = horizontal slider families.
164/166 = vertical slider components.
174/175/176 = tap/water family.
177/178 = switch family.
179 = large 67x151 tank/boiler graphic.
184/185 = OFF/ON toggle backgrounds.
186/187 = horizontal slider/gradient family.
76b = alternate 68x75 tile/background.

## Full dimension inventory
000 270x124; 001 34x27; 002 27x27; 003 18x12; 004 12x18; 005 18x12; 006 134x37; 007 134x37; 008 34x27; 009 34x27; 010 34x27; 011 105x126; 012 108x141; 013 82x145; 014 54x100; 015 21x126; 016 20x34; 017 149x99; 018 30x30; 019 30x31; 020 30x31; 021 279x61; 022 284x35; 023 8x158; 024 279x61; 025 10x9; 026 18x21; 027 68x28; 028 68x28; 029 11x21; 030 11x21; 031 68x28; 032 68x28; 033 30x30; 034 34x27; 035 34x27; 036 34x27; 037 34x27; 038 34x27; 039 30x18;
040 34x27; 041 34x27; 042 34x27; 043 29x38; 044 25x33; 045 29x38; 046 34x19; 047 9x21; 048 29x155; 049 29x155; 050 57x43; 051 34x29; 052 34x29; 053 34x29; 054 118x209; 055 35x37; 056 20x20; 057 20x20; 058 34x27; 059 34x27;
060 34x27; 061 34x27; 062 38x56; 063 17x31; 064 10x24; 065 34x27; 066 34x27; 067 34x27; 068 10x9; 069 46x46; 070 33x33; 071 367x1; 072 10x14; 073 68x75; 074 68x75; 075 68x75; 076 68x75; 077 30x26; 078 39x50; 079 480x45;
080 440x1; 081 440x50; 082 39x50; 083 39x50; 084 39x50; 085 39x50; 086 39x50; 087 39x50; 088 39x50; 089 39x50; 090 39x50; 091 39x23; 092 39x23; 093 39x23; 094 39x23; 095 39x50; 096 39x50; 097 39x50; 098 39x50; 099 39x50;
100 39x50; 101 39x50; 102 155x38; 103 155x38; 104 52x36; 105 34x27; 106 15x4; 107 15x4; 108 20x7; 109 20x7; 110 52x36; 111 52x36; 112 10x242; 113 10x242; 114 10x242; 115 41x40; 116 20x35; 117 155x38; 118 155x38; 119 52x36;
120 35x37; 121 35x37; 122 35x37; 123 35x37; 124 35x37; 125 35x37; 126 35x37; 127 35x37; 128 35x37; 129 35x37; 130 35x37; 131 35x37; 132 35x37; 133 35x37; 134 35x37; 135 35x37; 136 35x37; 137 35x37; 138 19x19; 139 19x19;
140 19x19; 141 19x19; 142 19x19; 143 19x19; 144 41x36; 145 41x36; 146 43x36; 147 43x36; 148 31x89; 149 12x89; 150 5x89; 151 30x31; 152 30x31; 153 32x23; 154 32x23; 155 32x23; 156 27x27; 157 370x24; 158 98x16; 159 31x49;
160 241x49; 161 241x49; 162 23x21; 163 301x16; 164 6x166; 165 301x16; 166 6x166; 167 301x16; 168 52x36; 169 52x36; 170 241x1; 171 1x47; 172 83x96; 173 27x34; 174 38x40; 175 37x40; 176 38x40; 177 60x22; 178 60x22; 179 67x151;
180 38x21; 181 38x21; 182 41x30; 183 41x30; 184 45x20; 185 45x20; 186 181x11; 187 181x11; 76b 68x75.

## Reverse-engineering rule
For every UI object: identify firmware resource ID, map it to the extracted PNG, inspect the actual pixels, then use firmware-derived X/Y/W/H and parent/child relations. Do not invent graphics when an extracted asset exists.