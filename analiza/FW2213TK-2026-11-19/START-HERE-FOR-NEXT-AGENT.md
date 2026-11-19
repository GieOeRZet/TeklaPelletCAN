# TeklaPelletCAN — START HERE — HANDOFF DLA NOWEGO CHATA / AGENTA
Data: 2026-11-19
Branch: ccr-be8a1bcb-5t76j0
Najnowszy commit master: 417bd789fceffd03473f90e8fb317b06f8e6821c

## CEL PROJEKTU
Nie chodzi już tylko o odczyt rejestrów. Cel nadrzędny: odtworzyć panel FW2213TK 1:1, a następnie wykorzystać wiedzę do własnej implementacji ESP.
1:1 obejmuje: ekrany, przejścia, widgety, hierarchię parent/child, bitmapy, teksty/fonty, X/Y/W/H, widoczność, callbacki/touch, konfigurację, CAN/CANopen, read/write, zależności, CO1..CO4, startup, alarmy, timery/state machine, menu serwisowe/test I/O, storage/persistencję i warianty sprzętowe.

## NAJWAŻNIEJSZY NOWY TROP — PRAWDZIWY PROJEKT TOUCHGFX
Firmware zachował ślad własnego kodu producenta:
C:\Estyma\igneoTOUCH\app\nasze\igneoTFT\gui\src\components\WheelSelectorExtra.cpp
oraz nazwy: TypedText, Bitmap, RadioButtonGroup, Container, Slider, Application, MVPApplication.
Potwierdzone są też ścieżki frameworka TouchGFX.
Wniosek: rekonstruować strukturę oryginalnego projektu, a nie traktować UI jako anonimowego kodu binarnego.
Nota źródłowa: analiza/FW2213TK-2026-11-18/TOUCHGFX-REPLIKA-1-1.md

## GŁÓWNY MODEL
BOOT/INIT -> HW/display init -> root/application object -> screen/menu dispatch -> TouchGFX widget tree -> bitmap/text/geometry -> touch/callback -> parameter engine -> CAN/storage/side effects.
Równolegle: classification/setup -> +0x12B typ/klasyfikacja -> +0x12C instancja 1..4 -> base_index + instance - 1 -> parametr CO1..CO4 -> record/CAN/storage.

## EKRAN GŁÓWNY
FUN_08031CCC() jest głównym znanym kontrolerem aktualizacji/konfiguracji.
panel id 1 -> 0x215F -> Outside temperature
panel id 11 -> 0x2002 -> Boiler program
panel id 16 -> 0x2003 -> Boiler set manual temp
panel id 270 -> 0x3505 -> Outside temperature sensor configuration
panel id 271 -> 0x2105 -> Heating configuration/UI state
panel id 327 -> 0x3740 -> nierozwiązana wartość zasobnika
panel id 328 -> 0x3601 -> fuel remaining [kg]
panel id 330 -> 0x3603 -> fuel reserve [kg]

### 63.8 MODULACJA — ROZWIĄZANE
FUN_0803CF54(): id95/0x299F = Burning type; id59/0x4005 = Burner power [%].
FUN_080436B4() dzieli wartość przez 10 i rozdziela część całkowitą/dziesiętną.
raw 638 -> UI 63.8.
To jest twardy łańcuch: CAN 0x4005 -> panel id 59 -> FUN_0803CF54 -> FUN_080436B4 -> UI.
Komponent pobiera też 0x2276 Grate move indicator, 0x2007 Burner state, 0x2250 Flame brightness i 0x2119.

## CO1..CO4 — NIE ODKRYWAĆ OD NOWA
0x2032..0x2035 = CH comfort temperature.
0x2048..0x204B = CH eco temperature.
0x2064..0x2067 = CH program/mode.
count=4: lookup = base_index + instance - 1.
+0x12B = typ/klasyfikacja; +0x12C = właściwy selector instancji.
FUN_08037212() wykorzystuje +0x12C również przy zapisie.
C064 FUN_0803C064() czyta DAT_0803C218[param_2], ustawia klasyfikację/instancję i descriptor.
FUN_08037D00() również pracuje na +0x12B/+0x12C.
Nie wiadomo jeszcze, skąd dokładnie przychodzi param_2; szukać indirect call/vtable w 0x08037C00..0x080386xx.

## WYCOFANE WNIOSKI — NIE WRACAĆ
Nie używać 0x10E -> 0x38130 jako settera ani 0x32146 jako settera.
Nie dodawać +0x10000 do adresów runtime. runtime = 0x08000000 + raw_offset.
Nie zakładać, że count=4 oznacza cztery aktywne obwody.
Nie traktować 0x2105 jako udowodnionego licznika CO.
Nie traktować 0x3505 jako profilu sprzętowego.
Nie przypisywać 0x404E do głównego ekranu bez dalszego śladu.

## UI / RENDERING
Potwierdzone: 480x272, framebuffer/pixel path, RGB565, TouchGFX framework, bitmapy już odzyskane w repo.
Nie ekstraktować bitmap ponownie bez potrzeby.

## NAJLEPSZY NASTĘPNY RUCH
1. Znaleźć więcej nazw własnych komponentów/projektowych ścieżek TouchGFX.
2. Zejść z FUN_08031CCC() i FUN_0803CF54() do parent/child/vtable i konstruktorów.
3. Dla każdego elementu screenshotu odzyskać widget -> X/Y/W/H -> bitmap -> TypedText -> font -> visibility -> callback -> parameter.
4. Połączyć drzewo UI z CO1..CO4, +0x12C i CAN/record engine.
5. Dopiero potem rozszerzać mapę na pozostałe ekrany, service/test I/O i konfigurację.

## STARTOWE PLIKI
analiza/FW2213TK-2026-11-19/MASTER-STATE-HANDOFF-2026-11-19.md
analiza/FW2213TK-2026-11-18/TOUCHGFX-REPLIKA-1-1.md
firmware/FW2213TK-ghidra/decompiled.c
firmware/FW2213TK-ghidra/strings.txt
rejestry/REJESTRY.md
rejestry/panel-fw-mapa-indeks-id.csv
analiza/FW2213TK-2026-11-19/

## ZASADY
Nie zaczynaj od zera. Buduj duże, skonsolidowane wyniki.
Każdy większy wynik zapisz na GitHubie razem z instrukcją kontynuacji.
Oznaczaj: [FW], [DATA], [STRONG], [HYPOTHESIS].
Każdą korektę wcześniejszego wniosku zapisz jawnie.
Nie analizuj pojedynczych rejestrów w izolacji, jeśli można zbudować pełny łańcuch.
Najważniejszy most: prawdziwy projekt TouchGFX producenta -> zdekompilowany firmware -> konkretne widgety -> zasoby/geometria -> parametry CAN.