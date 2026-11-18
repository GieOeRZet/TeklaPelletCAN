# FW2213TK – Ogrzewanie / drugi obwód CO – stan analizy

Najważniejsze znalezisko: firmware ma osobne etykiety dla czterech obwodów:
raw 0x088B30 = Ogrzewanie obwód 1
raw 0x088B58 = Ogrzewanie obwód 2
raw 0x088B80 = Ogrzewanie obwód 3
raw 0x088BA8 = Ogrzewanie obwód 4

Drugi blok:
raw 0x08EF50 = Ogrzewanie 1
raw 0x08EF6C = Ogrzewanie 2
raw 0x08EF88 = Woda użytkowa
raw 0x08EFDC = OGRZEWANIE 1
raw 0x08EFF8 = OGRZEWANIE 2
raw 0x08F014 = OGRZEWANIE 3
raw 0x08F030 = OGRZEWANIE 4

Parametry CH/CO znalezione w panel-fw-parametry-FW2213TK.csv:
0x2032 CH comf temp set [dC], u16, 150..300, default 210, RAM 0x20020964
0x2048 CH eco temp set [dC], u16, 100..300, default 180, RAM 0x20020966
0x2064 CH program, u8, 0..3, default 0, RAM 0x2002096E
0x2126..0x213E CH schedule monday..sunday, u32, 0..16777215, default 4194240, RAM 0x200209A8..0x200209C0
0x2142 CH mode, u8, 0..1, default 0, RAM 0x20020976
0x2146 Tch set manual [C], u8, 20..80, default 60, RAM 0x20020977
0x214A CH mixer test, u8, 0..2, RAM 0x20020956
0x2166 CH res [dC], s16, 0..500, RAM 0x20020968
0x216F CH mixer state, u8, 0..2, RAM 0x20020FEA
0x2299 CH pump state, u8, 0..1, RAM 0x20020922
0x229D CH pump test, u8, 0..2, RAM 0x20020928
0x22A1 Room temp sensor type, u8, 0..5, RAM 0x20020974
0x22A5 CH sensor use, u8, 0..1, RAM 0x20020975
0x22AD CH temp calc, s16, 10..90, RAM 0x2002096C
0x22B1 CH delta source [C], u8, 0..30, default 5, RAM 0x20020987
0x22B5 CH mixer opening time [s], u16, 60..360, default 180, RAM 0x2002095E
0x22B9 CH mixer state, u8, 0..2, RAM 0x20020962
0x22BD Room temp hysteresis [C], u8, 0..50, default 5, RAM 0x2002096A
0x22C1 Room sensor cal [C], s16, -30..30, RAM 0x20020970
0x22C5 CH temp for -20C [C], u8, 20..80, default 55, RAM 0x2002097A
0x22C9 CH temp for 0C [C], u8, 20..80, default 45, RAM 0x2002097C
0x22CD CH temp for -20C [C], u8, 20..80, default 30, RAM 0x2002097D
0x22D1 CH source, u8, 0..1, RAM 0x20020986
0x22D5 CH max temp [C], u8, 30..80, default 70, RAM 0x2002097E
0x22D9 CH correction factor [C], u8, 0..20, default 6, RAM 0x2002097F
0x22E5 CH temp lowering [C], u8, 0..40, default 15, RAM 0x20020982
0x22E9 Min CH temp for pump [C], u8, 20..60, default 20, RAM 0x20020983
0x22F1 Permament pump, u8, 0..1, RAM 0x20020985
0x22F5 CH needed temp. [C], u16, 0..150, RAM 0x200208F4
0x22F9 Tch lowering for energ. consumption reduction, u8, 0..1, RAM 0x20020990
0x22FD CH status, u8, 0..255, RAM 0x200209A0

Uwaga: ten zestaw nie dowodzi jeszcze, że każdy parametr jest konkretnie CO2. Teksty CH są wspólne, a numer obwodu może być wybierany przez instancję/ekran.

W katalogu są również kandydaci na dodatkowe harmonogramy:
0x2127 Harmonogram – slot 1 dnia 1 (maska 24 bit)
0x0809 Harmonogram (maska 24 bit) – dzień 7, prawdopodobnie CO2 / bufor
To są hipotezy, nie potwierdzenie CO2.

Następny etap:
1. znaleźć kod wybierający instancję CO1..CO4;
2. znaleźć zasób TypedText dla Ogrzewanie obwód 1..4;
3. znaleźć strukturę ekranu CO i widgety;
4. połączyć widget -> tekst -> bitmapa -> parametr -> CANopen;
5. ustalić dokładnie CO2.