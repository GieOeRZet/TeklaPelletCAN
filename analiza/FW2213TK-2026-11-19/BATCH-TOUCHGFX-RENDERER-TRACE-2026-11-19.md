# BATCH-TOUCHGFX-RENDERER-TRACE-2026-11-19

## Cel
Nowy tor analizy: odtworzenie rzeczywistego TouchGFX renderer path dla bitmap FW2213TK, zamiast zgadywania dekodowania RGB565.

## Twarde ustalenia z firmware panela / strings.txt
W `firmware/FW2213TK-ghidra/strings.txt` występują bezpośrednio:
- `touchgfx/framework/source/touchgfx/Bitmap.cpp`
- assert `Bitmap database has not been initialized.`
- `HAL::getInstance() && "Cannot set color before HAL is initialized"`
- `LCD16bpp.cpp`
- assert `bitmap.getFormat() != Bitmap::RGB888 && "RGB888 is not supported on 16 bit displays"`
- `HAL.cpp`
- `Bitmap.cpp` assert dotyczący cache.

To jest bezpośredni dowód obecności skompilowanego TouchGFX Bitmap/HAL/LCD16bpp code path w firmware panela.

## Kluczowa korelacja z TouchGFX 4.10
Publiczna dokumentacja TouchGFX 4.10 opisuje `BitmapData` dokładnie jako:
- data pointer
- extraData pointer
- width
- height
- solidRect_x/y/width/height
- 3-bit format upakowany w końcowych bitach `solidRect_height`.

To odpowiada dokładnie naszemu 20-bajtowemu rekordowi:
`u32 data + u32 extraData + 6*u16`.

Dokumentacja potwierdza też, że `extraData` jest kanałem alpha albo CLUT zależnie od formatu.

## Ważne: renderer, nie alternatywny codec
Dokumentacja LCD16bpp pokazuje ścieżkę:
`drawPartialBitmap(Bitmap)` -> `blitCopy(sourceData, sourceFormat, ... alpha, hasTransparentPixels)`.
`blitCopy` wykonuje bezpośrednie kopiowanie/blending do framebuffer oraz uwzględnia przezroczystość.

Nie znaleziono podstaw do hipotezy o QOI/palecie/RGB888 dla naszych 188 rekordów.

## Krytyczne odkrycie dotyczące obecnego extractora
Obecny extractor używa:
`PIL Image.frombytes("RGB", size, rgb, "raw", "RGB;16")`.

Test Pillow wykazał:
- bajty little-endian dla RGB565 `0xF800` (czerwony w RGB565) są przez `RGB;16` zinterpretowane jako **niebieski**;
- `BGR;16` daje dla tego samego `0xF800` poprawną czerwień;
- `0x001F` jest odwrotnie: `RGB;16` daje czerwony, `BGR;16` daje niebieski;
- zielony `0x07E0` pozostaje zielony.

Czyli obserwacja użytkownika „burner czerwony/orange -> wygenerowany niebieski” jest dokładnie zgodna z **R/B swap w obecnym dekoderze Pillow**, a nie z uszkodzeniem adresowania RGB565.

To nie jest jeszcze pełne wyjaśnienie wcześniejszych pasków/rozjechanych przejść; wymaga dalszego porównania layoutu danych i semantyki renderer path. Ale kanały R/B są już wyjaśnione testem kontrolowanym.

## TouchGFX color semantics
Publiczna dokumentacja TouchGFX potwierdza RGB565 jako:
- R 5 bitów
- G 6 bitów
- B 5 bitów
- red = 0xF800
- green = 0x07E0
- blue = 0x001F.

Zatem dla danych firmware zapisanych jako little-endian uint16_t, dekoder musi zachować semantykę bitową RGB565, a nie używać Pillow raw mode `RGB;16` jako bezpośredniego odpowiednika.

## Co dalej
1. Nie zmieniać jeszcze całego ekstraktora.
2. Zbudować referencyjny decoder RGB565 -> RGB przez jawne maskowanie:
   - R = ((v >> 11) & 0x1F) * 255/31
   - G = ((v >> 5) & 0x3F) * 255/63
   - B = (v & 0x1F) * 255/31
3. Zachować A8 osobno i sprawdzić alpha.
4. Porównać bitmapy 011-014 i 002/003.
5. Następnie odszukać w dekompilacji funkcje odpowiadające `Bitmap::drawPartialBitmap`, `LCD16bpp::blitCopy` i `Bitmap::getData/getExtraData/getFormat`.
6. Dopiero po tym poprawić extractor i wygenerować 000..187.

## Ważne ostrzeżenie
Nie utożsamiać jeszcze `FUN_08001ce8` z BitmapDatabase. Jest to hipoteza oparta na rozmiarze i położeniu. Musi zostać potwierdzona strukturą rekordów/referencjami.

## Źródła
- firmware panela: `firmware/FW2213TK-ghidra/strings.txt`
- funkcje: `firmware/FW2213TK-ghidra/functions.txt`
- TouchGFX 4.10 BitmapData: publiczna dokumentacja ST.
