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


## NOWY PRZEBIEG — 2026-11-19

### Namierzone adresy frameworka TouchGFX
Z `strings.txt`:
- `0x08034630` -> ścieżka `touchgfx/.../Bitmap.cpp`; bezpośrednio wcześniej `0x080345f3` assert "Bitmap database has not been initialized.".
- `0x080555be` -> `touchgfx/.../platform/driver/lcd/LCD16bpp.cpp`; assert przy `0x08055534` blokujący RGB888 na ekranie 16-bit.
- `0x080568fc` -> `touchgfx/.../hal/HAL.cpp`.
- `0x08056ffc` -> `touchgfx/.../hal/DMA.cpp`.

W `functions.txt` w sąsiedztwie tych regionów są m.in.:
- `FUN_080346dc` 128 B
- `FUN_0803475c` 30 B
- `FUN_080347dc` 76 B
- `FUN_0805570e` 466 B
- `FUN_080561b0` 36 B
- `FUN_0805644c` 180 B
- `FUN_08056500` 180 B
- `FUN_0805676c` 44 B
- `FUN_080567ac` 26 B
- `FUN_08056a04` 42 B
- `FUN_08056b0c` 238 B
- `FUN_08056c7e` 134 B
- `FUN_08056d04` 164 B
- `FUN_08056df0` 76 B
- `FUN_08056e78` 36 B

To zawęża dalsze szukanie: `FUN_0805570e` i okolice są głównym kandydatem dla LCD16bpp/bitmap blit path; `FUN_080568xx+` to HAL/blit/DMA path.

### Decoder został poprawiony
`tools/extract_fw_bitmap_table_direct.py` nie używa już Pillow `RGB;16`. Zastosowano jawny little-endian RGB565:
- R = bits 11..15
- G = bits 5..10
- B = bits 0..4
- rozszerzenie do 8 bitów przez bit replication.

Commit: `531125b87572842cb313f179e219280280c7e148`.

To jest korekta implementacji wynikająca z kontrolowanego testu `0xF800`, nie arbitralna zamiana kanałów.

### Nadal otwarte
Nie mamy jeszcze bezpośredniego dowodu z disassembly, która z funkcji `FUN_0805570e` / `FUN_08056xxx` wykonuje konkretny pixel loop. Następny przebieg ma zrekonstruować argumenty i instrukcje tych funkcji oraz znaleźć odwołania do formatów/alpha.


## PRZEŁOM — FUN_0805570E ODNALEZIONA I ZDEKOMPILOWANA

Mamy bezpośredni pixel loop z firmware, a nie tylko poszlaki.

Sygnatura:
`FUN_0805570e(int param_1, int param_2, undefined4 param_3, undefined4 param_4, byte param_5)`

### Co robi param_1 / param_2
- `param_1` jest źródłem RGB565: wskaźnik jest liczony jako `param_1 + pixelIndex*2`, a następnie czytany przez `ushort *puVar14`.
- `param_2` jest źródłem A8: `byte *pbVar12 = param_2 + pixelIndex`.
- To jest dokładnie nasz model `RGB565 + A8`.

### Co robi renderer
Framebuffer jest pobierany przez wirtualne wywołanie `DAT_08055dcc + 0x20`; wynik jest traktowany jako `ushort*puVar8` i adresowany jako:
`framebuffer + (x + y*framebufferStride)*2`.

Pętla robi zwykły row-major traversal:
- RGB: `puVar14++`
- alpha: `pbVar12++`
- framebuffer: `puVar8++`
- po każdym wierszu pomija `stride - width` elementów.

To jest **dowód, że dane RGB565 bitmapy nie mają żadnego tajemniczego tile/packing layoutu**. Są czytane liniowo, piksel po pikselu.

### Dokładny alpha blending
Dla `param_5 == 0xff`:
- alpha 0 -> nic,
- alpha 255 -> kopia RGB565,
- 0 < alpha < 255 -> każdy kanał RGB565 jest mieszany osobno:
  `((alpha*srcChannel + (256-alpha)*dstChannel) >> 8)`.

Maski są dokładnie:
- R: `0xf800`
- G: `0x07e0`
- B: `0x001f`.

Dla globalnego alpha `param_5 != 0xff`, efektywna waga to `A8 * param_5`, a normalizacja jest przez `0x10000`.

### Wniosek dla ekstraktora
Nie wolno mieszać A8 z RGB przy ekstrakcji. PNG powinien zachować:
`RGB565 source -> jawny R5/G6/B5 -> RGB`
plus:
`A8 source -> PNG alpha`.

**Nie ma podstaw, by przekształcać/tilować/rozpakowywać RGB565.**

### Bardzo ważna konsekwencja dla problemu „pasków”
Jeżeli po poprawie R/B nadal występują geometryczne paski/rozjazdy, przyczyna nie leży w rendererze TouchGFX ani w tajemniczym codec. Trzeba wtedy sprawdzić:
1. czy `data_ptr` rzeczywiście wskazuje początek bitmap payload;
2. czy `width*height*2` jest właściwym rozmiarem;
3. czy są bitmapy z innym formatem mimo wcześniejszego założenia format=0;
4. czy oglądany PNG nie jest efektem błędnego odczytu wskaźnika/offsetu dla konkretnego ID;
5. czy wcześniejsze „paski” były w istocie efektem błędnej interpretacji kanałów.

### Najważniejszy fakt
`FUN_0805570E` nie wykonuje żadnej konwersji RGB565 do RGB888. Operuje bezpośrednio na 16-bitowym słowie i maskach RGB565. To praktycznie zamyka hipotezę o alternatywnym formacie pikseli.
