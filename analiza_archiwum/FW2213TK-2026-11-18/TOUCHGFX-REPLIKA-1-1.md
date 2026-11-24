# FW2213TK – TouchGFX: poszukiwanie instrukcji UI 1:1

Cel: odtworzyć zależność widget -> pozycja/rozmiar -> bitmapa -> tekst -> font -> stan -> callback -> parametr CAN/SDO.

Potwierdzone ślady TouchGFX w firmware:
touchgfx/framework/source/touchgfx/Color.cpp
touchgfx/framework/source/touchgfx/containers/Container.cpp
touchgfx/framework/source/touchgfx/Application.cpp
touchgfx/framework/source/touchgfx/Bitmap.cpp
touchgfx/framework/source/touchgfx/containers/Slider.cpp
touchgfx/framework/source/platform/driver/lcd/LCD16bpp.cpp
touchgfx/TypedText.hpp
touchgfx/Bitmap.hpp
touchgfx/widgets/RadioButtonGroup.hpp
touchgfx/widgets/canvas/Canvas.cpp
touchgfx/hal/HAL.cpp
touchgfx/mvp/MVPApplication.hpp

Potwierdzona ścieżka własnego kodu:
C:EstymaigneoTOUCHapp
aszeigneoTFTguisrccomponentsWheelSelectorExtra.cpp

Nie oczekuję jednej instrukcji DRAW_SCREEN. W TouchGFX prawdopodobny jest zestaw kodu/struktur: konstrukcja ekranu, Image/Bitmap, TypedText, TextArea/wildcard, Button/RadioButtonGroup, Slider/WheelSelector, współrzędne, callbacki i aktualizacja modelu.

Dla CO2 trzeba odnaleźć:
- ekran wejściowy Ogrzewanie 2,
- nagłówek,
- listę pozycji,
- typ widgetu,
- pozycje i rozmiary,
- warunki widoczności,
- poziom PIN,
- callback dotknięcia,
- parametr odczytu/zapisu,
- numer bitmapy/zasobu,
- ID tekstu i adresy wszystkich języków.

Bitmapy są już wyciągnięte w repo; nie trzeba ich ponownie ekstraktować. Teraz trzeba znaleźć referencje kodu/zasobu do numerów bitmap.

Warstwy, które chcemy połączyć:
1. zasoby: bitmapy, teksty, fonty;
2. kod UI: ekrany i widgety;
3. model parametrów: rejestracja 448 wpisów;
4. CANopen: tablica 420 par indeks -> ID panela.

Docelowa ścieżka:
Screen/Widget -> TypedText/Bitmap -> panel parameter ID -> CANopen index -> RAM/handler.

Status:
POTWIERDZONE: TouchGFX, framework i własny kod projektu.
POTWIERDZONE: bitmapy są już w repo.
NIEPOTWIERDZONE: dokładna tablica TypedText/Bitmap oraz kod ekranu CO2.
CEL: odtworzenie ekranu CO2 1:1, a potem wykorzystanie mechanizmu do pozostałych ekranów.