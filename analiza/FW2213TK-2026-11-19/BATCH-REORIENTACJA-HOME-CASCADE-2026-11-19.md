# BATCH — 2026-11-19 — REORIENTACJA HOME / ODSEPAROWANIE CASCADE OD HOME

## Wynik
Po ponownym pionowym przejściu przez istniejące ślady raw BIN/Ghidra potwierdzono, że gałąź:
`FUN_0803E45C -> model[0x158] + model[0x11C] -> FUN_08047040 -> 4x FUN_080469E8 -> Bitmap 14`
jest osobną gałęzią związaną z wyborem/liczbą elementów cascade. Nie należy jej używać jako głównego toru rekonstrukcji Home/Main bez nowego hard edge.

`FUN_08047040` jest konkretnym selektorem 1..3: steruje stanem czterech powtarzalnych instancji 469E8. Jego caller `FUN_0803E45C` podaje model[0x158] oraz model[0x11C]. To jest wzorzec mechanizmu wariantowania, ale nie jest dowodem na 370A.

## Ważny stan Home
Prawdziwy Home/Main root pozostaje:
`FUN_0803E5AC`

Bezpośrednie elementy:
- +0x213D -> FUN_0802E716 = dynamic content host
- +0x23DC -> FUN_08047244
- +0x24B7 -> FUN_08047290 = 6 pionowych slotów
- +0x258F -> FUN_08047604 = duży content/composite; cztery obszary 480x200
- +0x289B -> FUN_08047E54
- +0xA5FC/+0xA628 -> FUN_08038ED0
- dalsze +0xA654/+0xA680 -> FUN_0802DF08
- +0xA6AC/+0xA6BC/+0xA6CC/+0xA6DC -> FUN_08047FD4/FE8/FFC/FE8

`480x200` pozostaje interpretowane jako obszar/page content, nie bitmapa.

## Hardware/profile — istotne dla celu użytkownika
Twardo odzyskana warstwa wariantów:
- 0x3500 = Main module type
- 0x3502 = CH expansion module type
- 0x350B = Profile number

Dla Main=0:
- expansion=0: profile 1/2/3 -> wariant 2/3/4
- expansion=1: profile 1/2/3 -> wariant 5/6/7

Wybrany indeks służy do pobierania dziesiątek struktur/pointerów. To jest dokładnie ten mechanizm, którego szukamy, jeśli Home ma mieć wszystkie warianty sprzętowe.

Dodatkowo +0x16C1 wpływa na wybór struktur, a +0x16D5 jest osobnym warunkiem.

## 370A
Zamknięty łańcuch:
`370A -> internal 0x121 -> FUN_08036FF2 -> runtime record -> RAM 0x20021FA6 -> u8 1..3 -> FUN_0803CB2C -> FUN_0803CACC -> C33E child +0x85C -> resource 11/12/13`

Nie należy ponownie otwierać tego łańcucha.

## Najważniejszy otwarty problem
Trzy sibling constructors:
- FUN_08039A48
- FUN_08039B30
- FUN_08039C18

wspólnie tworzą `FUN_0803C33E`, który ma:
+0x330, +0x35C, +0x85C, +0x888, +0x8B4, +0x8E0.

+0x85C ma X=40,Y=70 i jest miejscem dla runtime Bitmap 11/12/13.
Trzeba teraz ustalić, który z trzech siblingów jest konkretnym Home/Main boiler screen oraz jak upstream łączy go z root/variant package.

## Nowy kierunek
Nie wracać do 469E8 ani 370A chain.
Atak:
1. porównać 39A48/39B30/39C18 poza wspólnym C33E;
2. znaleźć ich parent/add/geometry i warunki wariantowe;
3. odzyskać wybór struktury 2..7 z 3500/3502/350B;
4. połączyć wybrany wariant z konkretnym siblingiem 39A48/39B30/39C18;
5. równolegle rozebrać 47290 i późniejsze root childy po resource/TypedText/geometry;
6. dopiero potem złożyć pełny Home variant matrix.

## Zasada
Nie utożsamiać 469E8/Bitmap14 z głównym Home tylko dlatego, że bitmapa wygląda jak kocioł. Raw evidence wskazuje osobną gałąź cascade.
