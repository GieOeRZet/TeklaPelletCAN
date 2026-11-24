# FW2213TK – TouchGFX: rzeczywista baza TypedText / tekstów

## Przełomowe znalezisko

W BIN znajduje się 8 równoległych tabel wskaźników do tekstów, po jednej na język. Każda tabela ma 495 wpisów × 4 bajty.

Początki tabel: raw 0x59E90, 0x5A64C, 0x5AE08, 0x5B5C4, 0x5BD80, 0x5C53C, 0x5CCF8, 0x5D4B4.
Odstęp: 0x7BC = 495 × 4.

Dowód: w każdej tabeli wpis nr 0 wskazuje na osobną kopię stringu ABC. W BIN znaleziono 8 kopii ABC.

## ID tekstu

Indeks wpisu w tabeli jest wspólnym ID tekstu. Dla polskiej tabeli 0x5BD80:
- 57 = Ogrzewanie 1
- 58 = Ogrzewanie 2
- 99 = OGRZEWANIE 1
- 100 = OGRZEWANIE 2
- 101 = OGRZEWANIE 3
- 102 = OGRZEWANIE 4
- 119 = Ogrzewanie obwód 1
- 120 = Ogrzewanie obwód 2
- 121 = Ogrzewanie obwód 3
- 122 = Ogrzewanie obwód 4

W tabeli angielskiej te same ID dają odpowiednio Heating 1/2, HEATING 1/2/3/4 oraz Heating 1/2/3/4.

## Języki

Na podstawie treści tabel:
- tabela 0: ES
- tabela 1: EST
- tabela 2: EN
- tabela 3: LT
- tabela 4: PL
- tabela 5: RO
- tabela 6: SK
- tabela 7: CZ

## Teksty parametrów CO

- 150 = Comfort temperature / Temperatura komfortowa [°C]
- 151 = Economical temperature / Temperatura ekonomiczna [°C]
- 152 = Program / Program
- 154 = Histeresis / Histereza [°C]
- 164 = Work mode / Tryb pracy
- 165 = Room sensor / Czujnik pokojowy
- 166 = Room sensor calib. / Kalibracja czujnika pok. [°C]
- 167 = HC sensor / Czujnik CO
- 168 = Temp. HC for -20°C / Temperatura CO dla -20°C [°C]
- 169 = Temp. HC for -10°C / Temperatura CO dla -10°C [°C]
- 170 = Temp. HC for 0°C / Temperatura CO dla 0°C [°C]
- 171 = Temp. HC for 10°C / Temperatura CO dla 10°C [°C]
- 172 = Temp HC corr. factor / Wsp. korekcji t. CO [°C/°C]
- 173 = Min HC temp. pump / MIN temperatura CO pomp [°C]
- 174 = Mixing valve time / Czas mieszacza [s]
- 175 = HC temp. set manually / Temperatura CO zadana ręcznie [°C]
- 176 = Hot water priority / Priorytet CWU
- 177 = Pump test / Test pompy
- 178 = Mixing valve test / Test mieszacza
- 179 = Pump constant / Stała pompa

Przykład: PL TypedText 120 -> wpis 0x5BD80 + 120*4 = 0x5BF60 -> wskaźnik 0x08098B58 -> Ogrzewanie obwód 2.

## Znaczenie

Mamy teraz rzeczywisty mechanizm: TypedText ID -> tabela języka -> adres UTF-16 stringu.
To pozwala przestać zgadywać mapowanie tekstów na podstawie kolejności przypadkowych stringów.

Następny cel: znaleźć kod UI używający konkretnych ID TypedText i połączyć Screen/View -> TypedText ID -> widget -> współrzędne -> bitmap -> callback -> parametr.