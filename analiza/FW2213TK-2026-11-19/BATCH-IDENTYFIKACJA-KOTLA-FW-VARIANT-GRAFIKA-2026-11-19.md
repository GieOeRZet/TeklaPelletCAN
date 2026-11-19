# IDENTYFIKACJA KOTŁA / WERSJA FW / DOBÓR GRAFIKI — 2026-11-19

## Najważniejszy wynik

Hipoteza użytkownika o tym, że panel wie jaki to kocioł z konfiguracji/rejestrów, jest bardzo mocno zgodna z firmware. W FW2213TK nie ma jednego pola model kotła, tylko kilka warstw identyfikacji i konfiguracji.

### 1. Bezpośrednio potwierdzone parametry identyfikacyjne
- 0x2125 = Device type; u32; domyślna wartość w tabeli FW: 1000070001; RAM 0x20022088.
- 0x3664 = soft. version; u16; RAM 0x200114E8; w zrzucie z FW wartość 2118.
- 0x3665 = igneTouch boiler short name; u32; RAM 0x20008D4C; odczytana wartość 0x54450000.
- 0x370A = Boiler image selector; u8; zakres 1..3; RAM 0x20021FA6; kod rejestracji 0x0801AB7E; obecny raw 259 oznacza po kodowaniu flagi 256+n wartość n=3.

To ostatnie jest szczególnie ważne: firmware panela ma parametr nazwany dosłownie Boiler image selector. Nie jest to nazwa naszej aplikacji — pochodzi z oryginalnego FW2213TK.

### 2. Osobna warstwa wariantu sprzętowego
- 0x3500 = Main module type
- 0x3502 = CH expansion module type
- 0x350B = Profile number

W głównym obiekcie są one pod offsetami +0x16BF, +0x16C0 i +0x16CC. Kod wybiera na ich podstawie cały zestaw struktur/pointerów.

Dla Main=0: expansion=0 daje profile 1/2/3 -> warianty 2/3/4, a expansion=1 daje profile 1/2/3 -> warianty 5/6/7. To jest twardy dowód z FW, że konfiguracja sprzętowa wybiera cały pakiet zachowania.

### 3. Warstwy, których nie wolno mieszać

IDENTYFIKACJA:
- 0x2125 Device type
- 0x3664 soft. version
- 0x3665 igneTouch boiler short name

WARIANT SPRZĘTOWO-I/O:
- 0x3500 Main module type
- 0x3502 CH expansion module type
- 0x350B Profile number

KONFIGURACJA FUNKCJONALNA:
- 0x2105 Heating configuration
- 0x2106 Hot water configuration
- 0x2107 Buffer configuration
- 0x2108 Solar configuration

PARAMETR WIZUALNY:
- 0x370A Boiler image selector (1..3)

Nie robimy więc skrótu serial -> jeden ekran. Najpierw trzeba rozdzielić identyfikację urządzenia, wariant sprzętowy, konfigurację instalacji i wybór grafiki.

### 4. Numer seryjny producenta

W strings firmware istnieją literalne teksty PASSWORD:, SERIAL:, PIN: %u i SERIAL: %u w okolicy 0x08045914..0x08045940. To jest twardy dowód, że pojęcie SERIAL istnieje w tym firmware.

Nie znaleźliśmy jeszcze call-chainu tych stringów do konkretnego pola konfiguracji kotła. Nie wolno więc twierdzić, że SERIAL z tych napisów jest numerem seryjnym kotła używanym przez producenta do doboru paczki FW.

Stan:
- [FW] SERIAL istnieje jako pojęcie/tekst.
- [NIEUDOWODNIONE] SERIAL = numer seryjny kotła.
- [NIEUDOWODNIONE] producent dobiera binarkę po tym polu wprost.
- [STRONG] procedura producenta numer seryjny + wersja softu bardzo dobrze pasuje do istnienia wariantów FW, ale sama procedura nie dowodzi jeszcze konkretnego pola w kodzie.

### 5. Co to zmienia w renderze

Poprzedni mockup był zbyt mocno projektowym HMI. Od teraz render ma powstawać z łańcucha: konfiguracja urządzenia -> wariant FW -> realne komponenty TouchGFX -> realne bitmapy/TypedText -> geometria -> dynamiczne parametry.

Już mamy twarde elementy Home/Main:
- 480x272.
- kandydat root FUN_0803E5AC.
- +0x92DC -> FUN_08047290 tworzący dokładnie 6 powtarzalnych elementów.
- TypedText 96 = MENU.
- TypedText 63 = Wyłączony.
- TypedText 57 = Ogrzewanie 1.
- TypedText 58 = Ogrzewanie 2.
- TypedText 119..122 = Ogrzewanie obwód 1..4.
- TypedText 348 = Błąd wygaszania: (205,195,200,70).
- TypedText 460 = Liczba kotłów slave: (320,195,200,70).

Dynamiczne parametry już twardo spięte z UI obejmują m.in. 0x215F outside temperature, 0x2002 boiler program, 0x2003 manual setpoint, 0x2004 result setpoint, 0x3601 fuel left i 0x3603 fuel reserve.

### 6. Najbliższy priorytet
1. Trace 0x370A od rejestracji parametru do kodu UI/bitmap selector.
2. Znaleźć wszystkie użycia 0x3664 i 0x3665.
3. Znaleźć call-site stringów SERIAL: / SERIAL: %u.
4. Ustalić mapowanie wartości 0x370A = 1/2/3 na konkretne bitmapy z tablicy 188/189 obrazów.
5. Połączyć 0x3500/3502/350B z konkretnym wariantem Home/Main.
6. Kontynuować FUN_0803E5AC -> +0x92DC -> 6 elementów -> bitmap -> callback.
7. Dopiero wtedy render 480x272 oparty na dowodach.

## Pewność
- [FW] 0x370A jest parametrem Boiler image selector, zakres 1..3.
- [FW] 0x3664 jest soft. version.
- [FW] 0x3665 jest igneTouch boiler short name.
- [FW] 0x3500/3502/350B uczestniczą w wyborze całego wariantu konfiguracji.
- [FW] literalne teksty SERIAL/PASSWORD/PIN istnieją.
- [NIEUDOWODNIONE] serial producenta = konkretne pole RAM/CAN.
- [NIEUDOWODNIONE] 370A jest bezpośrednio wyliczany z numeru seryjnego.