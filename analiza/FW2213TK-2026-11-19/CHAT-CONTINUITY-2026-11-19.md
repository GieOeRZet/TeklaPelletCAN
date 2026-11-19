# TeklaPelletCAN — CIĄGŁOŚĆ ROZMOWY — 2026-11-19

Cel: trwały checkpoint rozmowy i ustaleń. Kolejny agent ma korzystać z tego pliku zamiast ponownie wykonywać zamknięte analizy.

## 1. Instrukcja użytkownika

Użytkownik wymaga wielopoziomowego, wielowątkowego reverse engineeringu:
- działaj -> sprawdzaj -> analizuj -> szukaj -> wracaj do wcześniejszych punktów -> powtarzaj;
- kilka/kilkanaście/kilkadziesiąt przebiegów przed podsumowaniem;
- po znalezieniu faktu idź dalej jego łańcuchem;
- nie dawaj okruchów bez kontynuacji;
- zapisuj zamknięte ustalenia do GitHub, aby nie powielać roboty.

## 2. Żądanie: 151/152

Użytkownik najpierw poprosił o pokazanie bitmap 151 i 152. Następnie wyraźnie nakazał rozszarpanie binarki, bez polegania tylko na wcześniejszym atlasie.

## 3. Direct-BIN bitmap extraction — zamknięte

Źródło: FW2213TK_kopia.bin
Rozmiar: 2,031,616 B = 0x1F0000

Twarda korekta:
runtime pointer -> file offset:
file_offset = runtime_pointer - 0x08010000

Nie używać 0x08000000. Ta błędna baza powoduje śmieciowe obrazy.

Tabela bitmap:
- file offset 0x54450
- runtime 0x08064450
- rekord 20 B
- 188 prawdziwych rekordów
- IDs 000..187

Układ rekordu:
+00 u32 RGB/data pointer
+04 u32 extraData/A8 pointer lub 0
+08 u16 width
+0A u16 height
+0C u16 solidRect.x
+0E u16 solidRect.y
+10 u16 solidRect.width
+12 u16 solidRect.height

RGB = RGB565, 2 B/pixel.
Jeśli extraData != 0, kanał A8 ma W*H bajtów.

## 4. Bitmapy 151/152 z BIN

151:
descriptor 0x5501C
RGB 0x081C5638
A8 0x081E4C7C
30x31

152:
descriptor 0x55030
RGB 0x081C5D7C
A8 0x081E5020
30x31

Różnica RGB pointerów = 0x744 = 30*31*2. To potwierdza kolejne RGB565 payloady.

## 5. 151/152 -> FUN_08047290

Raw disassembly potwierdził:
FUN_08047290
 -> sześć rekordów, stride 0x40
 -> FUN_08047334
 -> FUN_0804C392
 -> FUN_0804C320
 -> resource IDs 151/151/152/152

Czyli 151/152 są prawdziwą parą stanów komponentu 47290.

Nie łączyć ich z wykresem 056/057.

## 6. 056/057

Ekran „Moc dmuchawy modulacja [%]” ma pięć punktów wykresu.

Web/card:
.fmp -> U(56)
.fmp.sel -> U(57)

Czyli:
056 = punkt normalny
057 = punkt selected

To osobny mechanizm od 151/152.

## 7. FUN_08047290 — korekta krytyczna

47290 jest pionowym komponentem sześciu slotów, NIE dolnym paskiem.

Geometria:
X = 100
Y = 50, 84, 118, 152, 186, 220
stride = 0x40

47290:
- rejestruje się przez FUN_080318B4;
- jest aktualizowany przez registry/vtable +0x50;
- używa bitmap 151/152;
- pobiera TypedText dynamicznie.

Caller:
0803EE30 -> 080484B0 -> 08047334

W 0803EE30:
record+0x08 jest pointerem przekazywanym dalej jako argument 7.
W 47334:
TypedTextID = param_7[slot]

## 8. Home root

Home root = FUN_0803E5AC.

Potwierdzone bezpośrednie konstrukcje/attach:
+0x380 -> 08038ED0
+0x3BC -> 08041E1C
+0x3EC -> 08041E1C
+0x41C -> 08047230
+0x42C -> repeated constructor przez 0800DCD4
+0x84F4 -> 0802E716
+0x8F70 -> 08047244
+0x92DC -> 08047290
+0x963C -> 08047604
+0xA26C -> 08047E54
+A5FC/+A628 -> 08038ED0
+A654/+A680 -> 0802DF08
+A6AC -> 08047FD4
+A6BC -> 08047FE8
+A6CC -> 08047FFC
+A6DC -> 08047FE8

Parent/add helper = FUN_08030380:
child parent at +0x14 and child linked into parent +0x28 chain.

Uwaga: drzewo obiektów jest twarde, ale semantyka każdego dziecka nie wynika automatycznie z samego miejsca konstrukcji.

## 9. Prawdziwy bottom bar

47290 NIE jest bottom bar.

Najmocniejszy obecny trop:
160/161, rozmiar 241x49.

Są wizualnie zgodne z dużym ciemnym przyciskiem konfiguracji/settings na pokazanym ekranie.

Jeszcze otwarte:
160/161 -> call-site -> constructor -> parent -> geometry -> callback -> konkretny ekran.

## 10. 370A / boiler graphic

Zamknięty łańcuch:
370A
 -> internal +0x121
 -> FUN_08036FF2
 -> runtime record
 -> RAM 0x20021FA6
 -> u8 1..3
 -> FUN_0803CB2C
 -> FUN_0803CACC
 -> FUN_0803C33E
 -> child +0x85C
 -> resource 11/12/13

370A:
- Boiler image selector
- u8 1..3
- default 1
- RAM 0x20021FA6
- callback/registration 0x0801AB7E

Nie zakładać, że wartość pochodzi z device type/serial.

## 11. C33E/C5B4

0803CACC:
- input + 0x0A
- wynik jako resource ID
- destination +0x85C
- FUN_080307BC

Input 1/2/3 -> bitmap 11/12/13.

0803C33E:
- helper +0x84C
- FUN_080424C4
- +0x85C pozostaje bitmap child

0803C5B4 nie ma bezpośredniego BL; prawdopodobnie ścieżka vtable/indirect.

## 12. Cascade

0803E45C
 -> model[0x158] + model[0x11C]
 -> 08047040
 -> 4 x 080469E8
 -> bitmap 14

Niezależna gałąź. Nie utożsamiać automatycznie z główną grafiką Home.

## 13. CO1/CO2

CO2:
raw około 0x46D2C, runtime 0x08056D2C, TypedText 58 = Ogrzewanie 2, osobny vtable.

CO1:
raw około 0x4B618, runtime 0x0805B618, TypedText 57 = Ogrzewanie 1, osobny vtable.

CO2:
TypedText 348 „Błąd wygaszania” X205 Y195 W200 H70
TypedText 460 „Liczba kotłów slave” X320 Y195 W200 H70
TypedText 68 „Moc 2” przy child +0x85C

08030358 = geometry helper.
0805F87C = X0 Y0 W480 H272.

Rodzina ośmiu konstruktorów:
0804C410
0804C78C
0804CA94
0804CD9C
0804D00C
0804D320
0804D634
0804D948

TypedText:
40..49 zależnie od +0x12B
159 = Temp. maksymalna [°C]
170 = Temperatura CO dla 0°C [°C]
171 = Temperatura CO dla 10°C [°C]
99..102 = OGRZEWANIE 1..4
119..122 = Ogrzewanie obwód 1..4
57 = Ogrzewanie 1
58 = Ogrzewanie 2

Otwarte:
parent/add CO1/CO2, wybór przez Home variant, dynamiczne bitmap writers.

## 14. Home variants

Obiekt:
+0x16BF = 0x3500 Main module type
+0x16C0 = 0x3502 CH expansion
+0x16CC = 0x350B Profile
+0x16C1 = dodatkowe pole konfiguracji
+0x16D5 = osobny warunek inicjalizacji

Main=0:
expansion=0: profile 1/2/3 -> variant 2/3/4
expansion=1: profile 1/2/3 -> variant 5/6/7

Main=1/2 mają osobne gałęzie.

## 15. 0x2105

0x2105 = Heating configuration, zakres 0..4.

Nie ma dowodu:
0x2105 -> liczba CO
0x2105 -> +0x12C

Nie powielać tych hipotez.

0x2106..0x2108 = dodatkowa konfiguracja grzania.
C064 = dispatcher class/instance, nie dowód aktywacji CO.
DAT_0804107C / podobne = Test I/O dla pomp/mieszaczy CO1..CO4.

## 16. Inne ważne komponenty

0802E716:
- host/container
- 648 B
- konstrukcja m.in. 08034866, 080349F4, 08034784
- callbacks 08034A2C..08034A68
- rectangle 480x300
- element 1000x1000
- nie jest bezpośrednim writerem 0B..0E

08047604:
- duży komponent Home
- grupy 5 elementów i 5 tekstów
- 4 obszary 480x200
- prawdopodobny graph/chart
- nie traktować tych regionów jako literalnych boiler bitmaps bez dowodu

08047E54:
- 0802DF80
- resources 0x1B6..0x1B9
- TypedText 468 około X135 Y60 W200
- rola nadal otwarta

## 17. Canonical bitmap inventory

188 bitmap IDs 000..187.

Najważniejsze:
011/012/013/014 = boiler graphics
019/020 = checkbox
056/057 = graph points
070 = slider handle
102/103 = large minus
104 + 168/169 = small minus
110/111 = large OK
112/113/114 = slider dialog pieces
117/118 = large plus
120..137 = mode/time icons
138..143 = circular selector/arrow family
151/152 = 47290 state
160/161 = real lower settings button
163 = slider track
165 = mode slider fill
167 = value slider fill
168/169 = small button background
184/185 = large toggle
186/187 = thin/value-slider elements

Pełna mapa wymiarów znajduje się w:
analiza/FW2213TK-2026-11-19/BITMAP-MAP-DIRECT-BIN-2026-11-19.md

## 18. GitHub artifacts / commits

HANDOFF:
analiza/FW2213TK-2026-11-19/HANDOFF-NOWY-CHAT-2026-11-19.md
commit e1f75d9895eb029b01d043081ade89c719ccb550

START-HERE:
analiza/FW2213TK-2026-11-19/START-HERE-FOR-NEXT-AGENT.md
commit 2ea42a92174eadf59c9f9b760954785af759d29d

BATCH-REORIENTACJA-HOME-CASCADE-2026-11-19.md
commit 84be7eb7cbe44b591338a89f8d7656944bd4602a

BATCH-CO1-CO2-VARIANT-GEOMETRIA-2026-11-19.md
commit f78987d007f8068f7b75d790cc5391311629f80c

BATCH-47290-UPDATE-REGISTRY-2026-11-19.md
commit 9c29bb6eacd496584135b30ff2c2766631879b2c

CORRECTION-47290-VERTICAL-NOT-BOTTOM-2026-11-19.md
commit 119ebc0a59a551972810fb4913ff44e8dc856f24

BATCH-MULTIPASS-47290-C33E-39XXX-2026-11-19.md
commit 3c3ba0953cb2eca11ccaa54a37953292825d3bf1

BATCH-RAW-151-152-47290-AND-BOTTOM-BAR-2026-11-19.md
commit 7968fb5eb8580c64fc45d2ca465ad235e69ac54e

BITMAP-MAP-DIRECT-BIN-2026-11-19.md
commit 06fcc9b6e80ad4141cd18ed4fa88511ddc0a5398

tools/extract_fw_bitmap_table_direct.py
commit 36200e0ce3c7ced25fe47fdde53fc7fac6e1a5e9

START-HERE direct-BIN checkpoint update:
commit ea973136c76fda0e6278ccc1ada140dc9b8814a4

## 19. Ostatnie żądanie użytkownika w tej rozmowie

Użytkownik poprosił:
„Zapis całą tą rozmowę na githubie aby była ciągłość.”

Ten plik jest odpowiedzią na to żądanie i ma być traktowany jako bieżący checkpoint rozmowy.

## 20. Następny agent — nie zaczynaj od początku

Najpierw przeczytaj:
1. ten plik;
2. START-HERE-FOR-NEXT-AGENT.md;
3. BITMAP-MAP-DIRECT-BIN-2026-11-19.md;
4. BATCH-RAW-151-152-47290-AND-BOTTOM-BAR-2026-11-19.md.

Następnie kontynuuj równoległe ścieżki:
A) 160/161 -> realny bottom bar;
B) 151/152 -> dokładna semantyka 47290;
C) Home variant -> CO1/CO2;
D) resource ID -> call-site -> parent -> geometry -> callback.

Nie wykonuj ponownie ekstrakcji 188 bitmap ani ustalania bazy 0x08010000.


## 2026-11-19 — dodatkowa weryfikacja podobnych par bitmap

Użytkownik zwrócił uwagę na podobne pary bitmap z/bez kolorowego środka. Bez zgadywania zidentyfikowano dwa podobne wizualnie zestawy:

- 056/057 — 20x20; 056 normalny punkt bez kolorowego środka, 057 selected z cyan/green środkiem. To para punktu wykresu modulacji dmuchawy.
- 151/152 — 30x31; 151 normalny selektor bez kolorowego środka, 152 selected z cyan/green środkiem. To para używana bezpośrednio przez FUN_08047290/FUN_08047334.
- 184/185 — 45x20; duży toggle normal/active, inna geometria; nie zaliczać do dwóch podobnych par okrągłych.

Wniosek:
- podobieństwo 056/057 i 151/152 jest rzeczywiste wizualnie;
- nie są tym samym zasobem i mają różne rozmiary oraz różne call-site'y;
- aktualny direct-BIN extraction pokazuje środek selected jako cyan/green; określenie „żółty” nie jest obecnie potwierdzone i nie należy go utrwalać jako faktu.

Canonical mapa została rozszerzona o ten wniosek i hash anchors:
- 056: 9d6fe5ce7f99495a1388be8bc97e29537fa1cd6d3ac9eecfa35ddb0286f4b3a2
- 057: ae19e8557619fd9bbbf2caf49c3a7b6da00205bb244436662415abc595cdcb5f
- 151: 6084705837b101fa56d4b5e517792037986e2f2440107cfa58f56b8dd1c79a16
- 152: de91aab8b30f9eb29d0d4c0a7fc236e1d1fd606868e176fc4287d49a4b163b9c

Direct-BIN working set: /mnt/data/tekla_bitmap_extract_directbin_2026-11-19/png/000.png ... 187.png
188 PNGs, decoded from FW2213TK_kopia.bin using base 0x08010000, table 0x54450, stride 0x14, RGB565 + optional A8.


## UI RESOURCE SEMANTICS — USER CONFIRMATION 2026-11-19

The user has now confirmed from the real UI/screens that bitmap resources 184/185 and 69/70 are reused across multiple controls/screens. Treat these as user-observed semantic evidence, separate from firmware call-site proof.

### 184/185 — large ON/OFF toggle
- 184/185 form the ON/OFF toggle itself.
- One state is used with the knob/selector resources 69/70 in the main Power view, lower-right corner, for boiler ON/OFF.
- The same 184/185 toggle mechanism is reused in settings such as DHW/CWU -> Menu -> Anti-legionella and other places, including 'heat now' and other ON/OFF-type controls.
- Therefore 184/185 must NOT be documented merely as a generic settings-row toggle; it is a reusable toggle control family used in the main power view and multiple settings/action screens.

### 69/70 — selector/knob resources with multiple roles
- 69/70 are used as part of the 184/185 ON/OFF selector/knob mechanism in the main Power view and elsewhere.
- The pair is also reused in sliders for temperature and heating mode for CO/DHW (CWU), and in additional slider controls elsewhere.
- Do not assign 69 or 70 exclusively to one widget. Their exact per-state/per-widget role must be established from firmware call-sites and visual geometry.

### Important correction to previous documentation
Previous notes that described 184/185 simply as a generic 'large toggle' were incomplete. The canonical interpretation is now: **reusable ON/OFF toggle family, including main Power-screen boiler ON/OFF and multiple settings/action screens**.
Previous notes that treated 69/70 only as a slider/knob pair were also incomplete: **they participate both in toggle controls and in multiple slider controls**.


## UI REFERENCE CLARIFICATION — SLIDER ICONS — 2026-11-19

User clarification: the supplied slider screenshot is only a visual reference for the **composition of the real UI**, not evidence of exact bitmap dimensions, colors, positions, or spacing.

Above each slider there are **4 icon positions, each with 2 states (active/inactive)**, i.e. 4x2 icon states per slider. The screenshot is a user-made interpretation and its icon sizes, colors, exact layout and proportions are NOT authoritative.

Therefore:
- do not infer bitmap IDs from the screenshot;
- do not infer exact dimensions or colors from the screenshot;
- do not assume the visual arrangement shown is the firmware arrangement;
- use the screenshot only to understand that the real composed control contains four mode icons above each slider and each icon has active/inactive states;
- bitmap identity must be established from direct-BIN extraction + resource references/call-sites + geometry.


## USER-CONFIRMED SLIDER MODE ICONS — 2026-11-19

User confirms that bitmap IDs **130–137** are the four mode icons used above the sliders. The UI composition has four icon positions per slider, with active/inactive states (4x2 states). The previously supplied screenshot is only a visual reference; exact dimensions, colors and layout must still come from the direct-BIN bitmap data and firmware call-sites.

Do not treat 130–137 as generic unrelated mode/time icons anymore: they are now user-confirmed as the slider mode-icon family. The exact mapping of each ID to icon position and active/inactive state remains to be established from firmware/resource references.


# 21. FINAL CHAT PACKAGE — 2026-11-19

Nowy chat ma rozpocząć od:
- MASTER-STATE-CONSOLIDATED-2026-11-19.md
- START-HERE-FOR-NEXT-AGENT.md
- CHAT-CONTINUITY-2026-11-19.md
- BITMAP-MAP-DIRECT-BIN-2026-11-19.md
- BITMAP-PREVIEW-MAP-2026-11-19.md

Szybka mapa bitmap została wydzielona do osobnego pliku, żeby można ją było wkleić do promptu nowego chata bez szukania po historii.

Ostatni punkt:
**051/052 → resource references → widget → pellet quantity parameter → threshold/state.**

Nie ponawiać ekstrakcji 188 bitmap.


# 22. NOWY TOR — TOUCHGFX RENDERER / BITMAPDATABASE — 2026-11-19

Użytkownik nakazał kontynuować analizę firmware panela TouchGFX oraz po zakończeniu zaktualizować plik ciągłości rozmowy na GitHub.

### Twarde ustalenia
W `firmware/FW2213TK-ghidra/strings.txt` są bezpośrednie ślady skompilowanego TouchGFX:
- `touchgfx/framework/source/touchgfx/Bitmap.cpp`
- assert `Bitmap database has not been initialized.`
- `touchgfx/framework/source/platform/driver/lcd/LCD16bpp.cpp`
- assert `bitmap.getFormat() != Bitmap::RGB888 && "RGB888 is not supported on 16 bit displays"`
- `HAL.cpp` i inne elementy frameworka.

Publiczna dokumentacja TouchGFX 4.10 potwierdza, że stary `BitmapData` ma dokładnie 20 B: data + extraData + width + height + solidRect x/y/w/h, przy czym 3-bitowy format jest upakowany w końcowych bitach `solidRect_height`. To odpowiada dokładnie rekordom naszego `FW2213TK.bin`.

### Krytyczne wyjaśnienie R/B
Obecny extractor używał Pillow:
`Image.frombytes("RGB", ..., "raw", "RGB;16")`.

Test kontrolowany wykazał:
- firmware RGB565 `0xF800` = czerwony;
- Pillow `RGB;16` dla little-endian bajtów tego słowa daje niebieski;
- Pillow `BGR;16` daje czerwony;
- `0x001F` analogicznie zamienia czerwony/niebieski;
- `0x07E0` pozostaje zielony.

Zatem obserwowane przez użytkownika „burner czerwony/orange -> wygenerowany niebieski” jest zgodne z R/B swap w obecnym dekoderze Pillow. Nie jest to dowód na złą bazę ani alternatywny codec.

### Renderer path
TouchGFX `LCD16bpp` ma `drawPartialBitmap` oraz `blitCopy(sourceData, sourceFormat, ... alpha, hasTransparentPixels)`; renderer wykonuje kopiowanie/blending do framebuffer. `extraData` jest alpha/CLUT zależnie od formatu.

Nie ma obecnie podstaw do hipotez QOI/paleta/RGB888 dla naszych 188 rekordów.

### Otwarte
R/B jest wyjaśnione. Nadal trzeba ustalić źródło zgłaszanych pasków/„rozjechanych” przejść i potwierdzić dokładną ścieżkę rendererów w dekompilacji.

Nie zakładać jeszcze, że `FUN_08001ce8` jest BitmapDatabase — to hipoteza do potwierdzenia strukturą i referencjami.

### Nowy batch
`analiza/FW2213TK-2026-11-19/BATCH-TOUCHGFX-RENDERER-TRACE-2026-11-19.md`
commit: `fc952b6ed32729e51e776a608a983ccbb699c9f0`

### Następne kroki
1. jawny decoder RGB565 przez maski bitowe;
2. zachować A8 osobno;
3. test 011-014 oraz 002/003;
4. namierzyć w dekompilacji odpowiedniki Bitmap::drawPartialBitmap, LCD16bpp::blitCopy, getData/getExtraData/getFormat;
5. dopiero potem poprawić extractor i regenerować 000..187.


## 23. TOUCHGFX — KOLEJNY PRZEBIEG 2026-11-19

Namierzone adresy z `strings.txt`:
- 0x08034630 = ścieżka `touchgfx/.../Bitmap.cpp`, assert Bitmap database przy 0x080345f3;
- 0x080555be = `LCD16bpp.cpp`, assert RGB888 unsupported przy 0x08055534;
- 0x080568fc = `HAL.cpp`;
- 0x08056ffc = `DMA.cpp`.

Funkcje w tych regionach z `functions.txt`: 080346dc, 0803475c, 080347dc oraz 0805570e (466 B), 080561b0, 0805644c, 08056500, 0805676c, 080567ac, 08056a04, 08056b0c, 08056c7e, 08056d04, 08056df0, 08056e78. `FUN_0805570e` jest obecnie głównym kandydatem LCD16bpp bitmap/blit path; region 080568xx+ to HAL/DMA/blit.

Extractor został poprawiony: jawny little-endian RGB565 zamiast Pillow `RGB;16`. Commit `531125b87572842cb313f179e219280280c7e148`. To eliminuje potwierdzony R/B swap (0xF800 czerwony był generowany jako niebieski).

Batch: `BATCH-TOUCHGFX-RENDERER-TRACE-2026-11-19.md`, commit `1f2764fc273351df915dc5fcfe6d36e958768e7d`.

Następny krok: zrekonstruować instrukcje/argumenty FUN_0805570e i FUN_08056xxx oraz znaleźć pixel loop, alpha i format handling. Nie zamykać jeszcze problemu pasków/rozjechanych przejść.


## 24. PRZEŁOM TOUCHGFX PIXEL LOOP — 2026-11-19

Odnaleziono i odczytano `FUN_0805570E` z `decompiled.c`. To bezpośredni renderer/blit pixel loop.

### Twardy dowód formatu
Sygnatura: `FUN_0805570e(int param_1,int param_2,undefined4 param_3,undefined4 param_4,byte param_5)`.
- param_1 = RGB565 source; odczyt przez `ushort*`, indeksowanie `pixelIndex*2`.
- param_2 = A8 source; odczyt przez `byte*`, 1 B/pixel.
- framebuffer = `ushort*`, adresowanie 2 B/pixel.

Pętle inkrementują source RGB, alpha i framebuffer po 1 pikselu oraz po wierszu pomijają `stride-width`. To dowodzi klasycznego row-major RGB565+A8, bez tile/bit-packing.

### Dokładny blending
Maski: R `0xf800`, G `0x07e0`, B `0x001f`.
Dla global alpha 0xff:
- A8=0 -> skip,
- A8=255 -> bezpośrednia kopia RGB565,
- pośrednia alpha: `((A*src + (256-A)*dst)>>8)` osobno dla każdego kanału.
Dla global alpha != 0xff: efektywna waga `A8*globalAlpha`, normalizacja `>>16`.

### Wniosek
Renderer potwierdza definitywnie, że bitmapy są przechowywane jako liniowe RGB565 + A8. Nie ma dodatkowego kodeka ani tile layoutu. Nie należy zmieniać/tilować danych przy ekstrakcji.

### Co z paskami
Jeżeli po poprawie R/B nadal będą paski geometryczne, problem trzeba szukać w konkretnym descriptorze/pointerze/rozmiarze/format field, a nie w rendererze. Możliwe też, że wcześniejsze paski były skutkiem błędnej interpretacji danych.

Batch: `BATCH-TOUCHGFX-RENDERER-TRACE-2026-11-19.md`, commit `32fa9aa180c73dfd96727c5e7e385ff079084997`.

Następny krok: zastosować poprawiony decoder do realnego firmware i wizualnie/testowo zweryfikować 002/003 oraz 011-014; następnie sprawdzić wszystkie 188 descriptorów pod kątem spójności pointer+size+format.
