# Instrukcja Tekla Pellet / igneoTouch — korelacja CO1/CO2 z firmware
## Źródło
Oficjalna instrukcja instalatora Estyma:
`InstrukcjaTeklaPelletInstalator_PL.pdf`, TKP-PL-I 20190802.

## Najważniejsze potwierdzenie z dokumentacji
Instrukcja pokazuje dwa warianty instalacji z dwoma obiegami CO:
- **Profil 2: CO1 + CO2 + CWU**
- **Profil 3: CO1 + CO2 + CWU + Bufor**

W Profilu 2 dokumentacja podaje osobne wyjścia:
- Pompa CO 1 obwodu
- Otwieranie mieszacza 1 obwodu
- Zamykanie mieszacza 1 obwodu
- Otwieranie mieszacza 2 obwodu
- Zamykanie mieszacza 2 obwodu
- Pompa CO 2 obwodu

oraz osobne wejścia:
- Czujnik temperatury CO 1 obwodu
- Czujnik temperatury pokojowej 1 obwodu
- Czujnik temperatury CO 2 obwodu
- Czujnik temperatury pokojowej 2 obwodu

To jest bezpośrednie potwierdzenie, że CO2 jest **drugim rzeczywistym obiegiem grzewczym**, a nie tylko nazwą ekranu/elementu UI.

## Korelacja z FW2213TK

### Potwierdzone w firmware
- TypedText ID 57 = `Ogrzewanie 1`
- TypedText ID 58 = `Ogrzewanie 2`
- TypedText ID 119 = `Ogrzewanie obwód 1`
- TypedText ID 120 = `Ogrzewanie obwód 2`
- `0x2065 -> panel ID 168` = `Tryb CO 2`
- `0x2064 -> panel ID 191` = `Tryb CO 1`
- `0x4001` = temperatura CO zmierzona, **count=4** w katalogu parametrów firmware.
- wiele parametrów CO ma w firmware wariant wieloinstancyjny `count=4`.

### Parametry CO z katalogu firmware
Najważniejsze potwierdzone wpisy:
- `0x2032` — CH comf temp set, ID 170
- `0x2048` — CH eco temp set, ID 171
- `0x2142` — CH mode
- `0x2146` — Tch set manual
- `0x2166` — CH res
- `0x22A5` — CH sensor use
- `0x22AD` — CH temp calc
- `0x22B1` — CH delta source
- `0x22B5` — CH mixer opening time
- `0x22B9` — CH mixer state
- `0x22BD` — Room temp hysteresis
- `0x22C1` — Room sensor cal
- `0x22C5` — CH temp for -20C
- `0x400C` — CH temp for -10C, count=4
- `0x22C9` — CH temp for 0C
- `0x22D1` — CH source
- `0x22D5` — CH max temp
- `0x22D9` — CH correction factor
- `0x22E5` — CH temp lowering
- `0x22E9` — Min CH temp for pump
- `0x22F1` — Permanent pump
- `0x22F5` — CH needed temp
- `0x2301` — CH thermostat state
- `0x2305` — CH room set temp adjustment
- `0x2315` — Automatic summer recognition
- `0x2321 / 0x2325 / 0x2329` — CH circuit name parts 1–3, count=4

## Co dokument mówi o logice CO
Instrukcja opisuje:
- źródło energii dla CO,
- zwiększenie temperatury źródła względem zadanej CO,
- czujnik pokojowy,
- maksymalną temperaturę CO,
- obecność czujnika CO,
- współczynnik korekcji temperatury CO,
- maksymalną temperaturę zewnętrzną dla pracy pompy,
- obniżenie temperatury CO,
- minimalną temperaturę CO dla pompy,
- czas mieszacza,
- stałą pracę pompy,
- obniżenie TCO dla ochrony powrotu.

Dokumentacja opisuje też ręczne zadawanie temperatury CO oraz tryb komfort/ekonomiczny. To dobrze odpowiada zestawowi parametrów znalezionemu w firmware.

## Ważne ograniczenie
Instrukcja **nie podaje adresów CANopen ani panel-ID**. Nie wolno więc traktować jej jako źródła mapowania adresów. Jej rola w reverse engineeringu jest inna: potwierdza architekturę funkcjonalną CO1/CO2 i fizyczne wejścia/wyjścia drugiego obiegu.

## Wniosek dla dalszej analizy
Najbardziej prawdopodobny model danych firmware to:
`obieg CO[0..3] -> zestaw parametrów wieloinstancyjnych`.

Dla instalacji opisanej przez dokumentację aktywne są co najmniej:
- CO1
- CO2

ale firmware ma miejsce na więcej instancji, co jest zgodne z obecnością napisów:
- Ogrzewanie obwód 1
- Ogrzewanie obwód 2
- Ogrzewanie obwód 3
- Ogrzewanie obwód 4

**Nie uznajemy jeszcze za udowodnione**, które dokładnie indeksy/offsety RAM odpowiadają instancji CO2. To trzeba potwierdzić analizą kodu rejestracji parametrów, indeksowania count=4 oraz odczytu/zapisu konkretnych instancji.

## Źródła
Oficjalna instrukcja Estyma, strony PDF 14–16 (Profil 2/3) oraz 22–25 (opis funkcji Ogrzewania).
