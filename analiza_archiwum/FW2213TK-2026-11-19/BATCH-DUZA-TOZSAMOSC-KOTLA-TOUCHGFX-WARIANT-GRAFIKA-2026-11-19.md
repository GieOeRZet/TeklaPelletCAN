# DUŻY BATCH — FW2213TK: TOŻSAMOŚĆ KOTŁA, WARIANT, GRAFIKA I ŚLAD ORYGINALNEGO TOUCHGFX
Data: 2026-11-19

## 0. Najważniejszy wynik
Po zestawieniu oryginalnego firmware, tabeli rejestracji, snapshotu CAN i śladów kompilacji TouchGFX widać już wyraźnie, że panel nie musi „wiedzieć jaki to kocioł” z numeru seryjnego zapisanego w jego własnym binarium.

Firmware ma kilka niezależnych identyfikatorów/warstw:
CAN / regulator -> 0x2125 Device type + 0x3665 igneTouch boiler short name + 0x3664 soft. version -> 0x3500/0x3502/0x350B hardware/profile -> 0x2105..0x2108 konfiguracja funkcjonalna -> 0x370A Boiler image selector -> TouchGFX widget tree -> bitmapy/TypedText/geometria/widoczność.

## 1. [FW] 0x2125 — Device type
- ID 0x2125
- u32
- RAM 0x20022088
- default 1000070001
- callback/rejestracja 0x0801B2EE
- 1000070001 = 0x3B9BDB71
- snapshot urządzenia również zawiera 0x3B9BDB71.

To jest rzeczywisty, nazwany przez firmware identyfikator Device type. Nie mamy jeszcze mapy 0x3B9BDB71 -> konkretny model Tekli, więc nazwy nie zgadujemy.

## 2. [FW] 0x3665 — igneTouch boiler short name
- ID 0x3665
- u32
- RAM 0x20008D4C
- callback/rejestracja 0x0801D3E6
- snapshot: 0x54450000

Reprezentacja bajtowa to 54 45 00 00, czyli przy interpretacji MSB-first daje ASCII „TE” + dwa zera. To silna hipoteza, że jest to krótki kod urządzenia, ale nie twierdzimy jeszcze, że TE oznacza Tekla.

Najważniejsze jest to, że nazwa pola w oryginalnym FW brzmi dosłownie: igneTouch boiler short name.

## 3. [FW] 0x3664 — soft. version
- ID 0x3664
- u16
- RAM 0x200114E8
- callback/rejestracja 0x0801D35A
- default w analizowanym FW: 2213
- snapshot: 2118

Nie wolno automatycznie utożsamiać nazwy pliku FW2213TK z aktualną wartością 0x3664. Widzimy jednocześnie skompilowany default 2213 i rzeczywisty odczyt 2118.

To bardzo dobrze pasuje do informacji o procedurze serwisowej, gdzie producent chce wersję softu Touch, ale nie dowodzi jeszcze mechanizmu aktualizacji.

## 4. [FW] 0x370A — Boiler image selector
- ID 0x370A
- u8
- zakres 1..3
- default 1
- RAM 0x20021FA6
- callback/rejestracja 0x0801AB7E
- snapshot raw 259

Panelowy zapis flag+bajt oznacza raw = 256 + wartość, więc 259 = 3.

To jest twardy dowód, że oryginalny firmware ma parametr nazwany Boiler image selector.

## 5. [FW] Hardware profile: 0x3500 / 0x3502 / 0x350B
0x3500 = Main module type
0x3502 = CH expansion module type
0x350B = Profile number

W głównym obiekcie odpowiadają im +0x16BF, +0x16C0 i +0x16CC.

Dla Main=0:
expansion=0: profile 1 -> wariant 2, profile 2 -> wariant 3, profile 3 -> wariant 4.
expansion=1: profile 1 -> wariant 5, profile 2 -> wariant 6, profile 3 -> wariant 7.

Wybrany indeks jest następnie używany do pobierania dziesiątek struktur/pointerów. To jest twardy dowód, że hardware/profile wybiera cały pakiet zachowania, a nie pojedynczy parametr.

## 6. [STRONG] Co z tego wynika dla pytania „skąd panel wie jaki kocioł?”
Najbardziej prawdopodobny runtime chain jest obecnie:
regulator/CAN -> Device type + boiler short name + hardware/profile -> wariant logiki -> konfiguracja funkcjonalna -> UI.

To jest znacznie bardziej prawdopodobne niż „serial jest zakodowany w binarium i z niego panel wybiera ekran”.

Numer seryjny może być używany przez producenta przy dystrybucji właściwego pliku aktualizacji, ale nie znaleźliśmy jeszcze połączenia stringów SERIAL: z konkretnym parametrem modelu.

## 7. [FW] Oryginalny custom TouchGFX producenta
Firmware zawiera dokładną ścieżkę:
C:\Estyma\igneoTOUCH\app\nasze\igneoTFT\gui\src\components\WheelSelectorExtra.cpp

oraz assert:
extraTextIndex < NUMBER_OF_EXTRA_TEXTS

Adresy:
0x08038D74 = assert extraTextIndex
0x08038D9C = ścieżka WheelSelectorExtra.cpp

To nie jest już tylko identyfikacja frameworka. Jest to ślad konkretnego pliku własnego kodu producenta.

## 8. [FW] Obszar funkcji własnego komponentu
Wokół śladu WheelSelectorExtra znajduje się gęsty blok funkcji:
0x080387E0, 0x080387F4, 0x0803882A, 0x0803885C, 0x08038998, 0x08038B54, 0x08038CF4, 0x08038DF0, 0x08038E04, 0x08038E18, 0x08038E2C, 0x08038E80, 0x08038E94, 0x08038ED0, 0x08038F80, 0x08039010, 0x0803904C, 0x08039068, 0x0803907C, 0x08039090, 0x080390A4, 0x080390BA, 0x080390FC.

Najciekawszy nowy punkt: FUN_08038ED0 występuje już w kandydacie Home/Main dwa razy:
root + 0xA5FC -> FUN_08038ED0
root + 0xA628 -> FUN_08038ED0

[HYPOTHESIS] Jeśli vptr potwierdzi, że FUN_08038ED0 jest konstruktorem customowego komponentu WheelSelectorExtra, Home/Main zawiera dwa egzemplarze tego komponentu.

## 9. [FW] Framework TouchGFX zachowany w firmware
Potwierdzone ślady: Application.cpp, MVPApplication.hpp, Container.cpp, Bitmap.cpp, Slider.cpp, TypedText.hpp, Bitmap.hpp, RadioButtonGroup.hpp, Canvas.cpp, HAL.cpp, LCD16bpp.cpp.

Czyli mamy rozdział:
custom producenta: WheelSelectorExtra.cpp
framework: Application / Container / Bitmap / Slider / TypedText / RadioButtonGroup / Canvas / HAL / LCD16bpp.

## 10. [FW] Konkretne drzewo komponentowe już odzyskane
CO2:
0x08056D2C -> global 0x20024814 -> +0x12A=2 -> 0x0805D948 -> 0x080612E0 -> child +0x48 -> geometry 0,0,480,272.

CO1:
0x0805B618 -> osobna klasa/vtable raw 0x7F778.

Wspólny builder CO:
+0x12B = typ/klasyfikacja; +0x12C = instancja -> FUN_0803E714 -> 12/11 ID parametrów -> FUN_08036FF2(+0x12C) -> FUN_0804842C -> widget record -> FUN_0804E5BC -> refresh FUN_08032316.

To jest już bardzo mocny odpowiednik architektury C++/TouchGFX: Container -> child widgets -> resource/geometry -> update -> parameter model.

## 11. [FW] Rzeczywiste dynamiczne elementy Home
Modulacja: CAN 0x4005 -> panel id 59 -> FUN_0803CF54 -> FUN_080436B4 -> raw 638 = 63.8.
Temperatura zewnętrzna: CAN 0x215F -> panel id 1 -> FUN_08031CCC.
Tryb kotła: CAN 0x2002 -> panel id 11.
Zadana ręczna: CAN 0x2003 -> panel id 16.
Wynikowa zadana: CAN 0x2004 -> panel id 15.
Zasobnik: id327 -> 0x3740, id328 -> 0x3601, id330 -> 0x3603.

## 12. [DATA] Rzeczywiste bitmapy kotłów
Wyciągnięty pakiet bitmap zawiera:
011.png = 105x126
012.png = 108x141
013.png = 82x145
014.png = 54x100

To są bitmapy z tablicy bitmap firmware. Poprzednia wygenerowana ilustracja kotła nie była assetem FW.

## 13. [STRONG] 370A nie zostało jeszcze połączone z 011..014
Mamy dwa niezależne fakty:
FW: 0x370A = 1..3.
Pakiet bitmap: 011..014.

Brakuje jeszcze prawdziwego kodu mapującego selector na bitmap ID. Nie zakładamy żadnej kolejności.

Możliwe architektury to m.in. selector 1..3 jako klasy, dodatkowy wybór przez hardware profile albo fallback bitmapowy. Rozstrzyga to dopiero ślad Bitmap/BitmapData w kodzie.

## 14. [STRONG] Najlepszy model architektury
REGULATOR/CAN
 -> 0x2125 Device type
 -> 0x3665 boiler short name
 -> 0x3664 software version
 -> 0x3500/3502/350B hardware profile
 -> 0x2105..0x2108 functional configuration
 -> 0x370A image selector
 -> UI variant
 -> TouchGFX Container/Bitmap/TypedText/WheelSelector
 -> geometry/visibility/callback
 -> parameter engine
 -> CAN.

## 15. Następny atak — pionowo, nie szeroko
Priorytet A: zamknąć 0x370A -> kod wyboru Bitmap -> bitmap ID -> widget -> geometria.
Priorytet B: vptr dla obiektów root+0xA5FC i root+0xA628 oraz sprawdzenie, czy FUN_08038ED0 jest WheelSelectorExtra.
Priorytet C: znaleźć call-chain 0x2125/0x3665 i ustalić, czy Device type/short name wpływa na wariant UI.
Priorytet D: dopiero potem łączyć SERIAL z updaterem.

## STATUS
[FW] 0x2125 Device type = 0x3B9BDB71.
[FW] 0x3665 igneTouch boiler short name = 0x54450000.
[FW] 0x3664 soft. version = default 2213, snapshot 2118.
[FW] 0x370A Boiler image selector = 3 w snapshot.
[FW] 0x3500/3502/350B wybierają cały pakiet wariantu.
[FW] WheelSelectorExtra.cpp jest prawdziwym śladem własnego kodu Estymy.
[FW] TouchGFX framework jest zachowany.
[STRONG] panel najprawdopodobniej dostaje część tożsamości modelu przez CAN/regulator.
[HYPOTHESIS] FUN_08038ED0 może być customowym WheelSelectorExtra używanym dwa razy w Home/Main.
[NIEUDOWODNIONE] SERIAL = numer seryjny używany przez updater.
[NIEUDOWODNIONE] 370A 1/2/3 = bitmapy 011/012/013.