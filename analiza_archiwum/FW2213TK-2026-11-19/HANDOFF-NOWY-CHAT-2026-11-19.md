# TeklaPelletCAN — HANDOFF NOWY CHAT — 2026-11-19

> **CZYTAJ TEN PLIK PRZED ANALIZĄ.** GitHub jest pamięcią projektu. Nie zaczynaj od zera.

## 1. KOLEJNOŚĆ CZYTANIA

Repo: GieOeRZet/TeklaPelletCAN  
Branch: ccr-be8a1bcb-5t76j0

Najpierw:
1. START-HERE-FOR-NEXT-AGENT.md
2. ten plik
3. MASTER-STATE-CONSOLIDATED-2026-11-19.md
4. BATCH-PERSISTENT-CONTINUATION-MEMORY-2026-11-19.md
5. ASSET-ATLAS-189-BITMAPS-2026-11-19.md
6. następnie **wszystkie batch-notes** w analiza_archiwum/FW2213TK-2026-11-19/
7. firmware/FW2213TK-ghidra/functions.txt
8. firmware/FW2213TK-ghidra/strings.txt
9. firmware/FW2213TK-ghidra/README.md
10. firmware/FW2213TK-ghidra/decompiled.c

Nie wystarczy przeczytać tytułów. Szukaj korekt, zamkniętych łańcuchów i punktów OPEN.

## 2. CEL

Badamy oryginalny FW2213TK panela IGNEO Touch. Celem jest rekonstrukcja 1:1: ekranów, menu, TouchGFX widget tree, parent/child, Bitmap/TypedText, geometrii, visibility, touch/callback, parameter engine, CAN/CANopen, CO1..CO4, konfiguracji, startup, alarmów, service/test i storage.

**Nie robimy mockupu. Odzyskujemy architekturę firmware.**

## 3. TRYB PRACY

Użytkownik wymaga wielopoziomowych przebiegów:
**znajdź → przeanalizuj → kontynuuj ślad → sprawdź sąsiednie funkcje/tabele/asset → wróć do głównego łańcucha → kolejny przebieg → dopiero raport.**

Nie zatrzymuj się na pojedynczym adresie. Mały trop rozwijaj bez przerywania głównego badania. Wykonuj kilka passów: code-flow, data-flow, widget-flow, asset-flow, CAN/model-flow, touch/callback i geometry/parent.

Evidence:
- [FW] bezpośredni kod,
- [DATA] tabela/raw/asset,
- [STRONG] kilka niezależnych dowodów,
- [HYPOTHESIS] brak twardego mostu,
- OPEN,
- REJECTED/CORRECTION.

Nigdy nie wymyślaj bitmap, vtable, callbacków, geometrii ani semantyki.

## 4. RAW BIN

FW2213TK_kopia.bin:
- 2 031 616 B
- SHA256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

Adres:
runtime = 0x08000000 + raw_offset

Nie dodawaj +0x10000 do adresów funkcji. Jeśli BIN jest dostępny, weryfikuj istotne adresy w bajtach i odróżniaj Thumb code od data/string/bitmap table. Jeśli BIN nie jest dostępny, nie wymyślaj bajtów.

## 5. FRAMEWORK / PANEL

Panel: 480x272 RGB565.

Twardy ślad producenta:
C:\Estyma\igneoTOUCH\app\nasze\igneoTFT\gui\src\components\WheelSelectorExtra.cpp

Występują ślady TouchGFX: Application, MVPApplication, Container, Bitmap, Slider, TypedText, RadioButtonGroup, Canvas, HAL, LCD16bpp.

## 6. NAMESPACE — KRYTYCZNE

Osobne są:
- Bitmap resource ID,
- TypedText ID,
- CAN/external parameter ID,
- internal model/panel index,
- RAM/storage.

Przykład: TypedText 57 = „Ogrzewanie 1”, ale Bitmap resource 57 to zupełnie inny namespace. Zawsze pisz „Bitmap resource 57” albo „TypedText 57”.

## 7. CO1..CO4 — ZAMKNIĘTE

+0x12B = typ/klasyfikacja.  
+0x12C = instancja 1..4.

Nie nazywaj +0x12B numerem CO.

FUN_0803C064 używa DAT_0803C218[param_2] i dla klas 1..4 ustawia type oraz instance. FUN_08036FF2 uwzględnia +0x12C przy rozwiązywaniu family-of-4.

Record engine:
- FUN_0801143C — registration,
- FUN_080115F6 — lookup,
- FUN_0801167A — read +0x14,
- FUN_080116E6 — read +0x1C,
- stride 0x2C.

+0x12C bierze udział w READ i WRITE.

Heating builder FUN_0803E714 jest wspólny dla CO1..CO4 i korzysta z parameter IDs, mappera i widget refresh.

## 8. ACCESS / CONFIG

FUN_08037E74:
- 0 → +0x158=0
- 900 → +0x158=1
- 999 → +0x158=2
- 0x1BF1 → +0x158=3

To jest gate wariantu/trybu UI, nie numer CO.

0x2105:
- internal 0x10F,
- Heating configuration,
- u8, 0..4, default 1,
- RAM 0x20021FAF,
- FUN_08031CCC używa go w FUN_0802D3E0/FUN_0802D91C.

**Nie jest udowodnione**, że 0x2105 bezpośrednio tworzy N obiektów CO. Stara hipoteza 0x10E = liczba CO jest odrzucona: 0x10E -> CAN 0x3505 = outside-temperature-sensor configuration.

Hardware/profile:
0x3500 main module, 0x3502 CH expansion, 0x350B profile; osobne pola +0x16C1/+0x16D5.

## 9. 370A — ZAMKNIĘTY ŁAŃCUCH

0x370A = Boiler image selector, u8, 1..3, RAM 0x20021FA6.

ZAMKNIĘTE:
0x370A
→ internal 0x121
→ FUN_08036FF2
→ mapping table @ 0x08037984
→ FUN_08037094
→ FUN_080115F6
→ record +0x0C
→ storage 0x20021FA6
→ value 1..3
→ FUN_0803CB2C
→ FUN_0803CACC
→ Bitmap +0x85C
→ FUN_080307BC
→ resource 11/12/13

Mapowanie jest twarde:
1→11→011.png
2→12→012.png
3→13→013.png

Assety:
011=105x126, 012=108x141, 013=82x145.
+0x85C ma X=40,Y=70.

**Nie analizuj tego ponownie, chyba że nowy dowód dotyczy innego miejsca tego samego łańcucha.**

0x0801AB7E nie jest callbackiem 370A; raw analysis wykazała data/pixel/table region.

## 10. C33E / C5B4

FUN_0803C33E tworzy realne Bitmap children:
+0x330, +0x35C, +0x85C, +0x888, +0x8B4, +0x8E0.

Trzy raw BL callers:
08039AD6 <- FUN_08039A48
08039BBE <- FUN_08039B30
08039CA6 <- FUN_08039C18

CB04 = constructor/wiring updater.  
CB2C = runtime refresh.  
307BC = rzeczywista zmiana Bitmap resource.

C5B4:
- +0x85C X=40,Y=70,
- attach +0x85C przez parent +0x04,
- +0x8E0 resource 0x7A, X=398,Y=runtime, attach przez +0x04.

**+0x84C NIE jest parentem +0x85C.** Jest osobnym helper/objectem przez FUN_080424C4.

0x7A=122, asset 122.png=35x37. +0x8E0 box X=398..433. Semantyka OPEN.

C5B4 dispatch nadal OPEN.

## 11. CASCADE — ODSEPAROWANY

internal 0x158 → external 0x351A = cascade slaves number.  
internal 0x11C → external 0x350C = cascade master flag.

Gałąź:
0x158/0x11C → FUN_0803E45C → FUN_08047040 → 469E8 composites → fixed resource 14.

FUN_080469E8: real Bitmap child +0x13C, resource 14. 014.png=54x100.

DAT_08046CC4 nie jest potwierdzonym vtable; raw target wskazuje UTF-16/resource data. Nie wracaj do starej teorii.

## 12. HOME / 6 SLOTÓW — GŁÓWNY PUNKT WZNOWIENIA

FUN_0803E5AC = silny Home/Main root candidate.

Tworzy m.in.:
+0x84F4 FUN_0802E716
+0x8F70 FUN_08047244
+0x92DC FUN_08047290
+0x963C FUN_08047604
+0xA26C FUN_08047E54
+0xA5FC/+0xA628 FUN_08038ED0
i dalsze komponenty.

**KOREKTA:** 47244 + 47290[6] NIE jest udowodnionym sześcioma poziomymi kafelkami dolnego paska. FUN_08047334 układa sześć rekordów PIONOWO:
Y≈50,84,118,152,186,220.

FUN_08047290:
- 6 visual records @ DAT_0804732C, stride 0x40,
- 6 text records @ DAT_08047330, stride 0x34.

FUN_08047334 dla każdego slotu tworzy composite przez:
FUN_0804C320, FUN_0804C392, FUN_080313A4, pozycję, kolor i dzieci.

**Każdy slot ma własny TypedText.**

### Hipoteza użytkownika
Sześć pionowych bloków może być menu otwieranym przez dolny prawy przycisk. Użytkownik widzi w oryginalnym sofcie takie menu; 3. lub 4. pozycja prowadzi do CO. Dostęp:
Basic → PIN 0900 → PIN 0999 → wyższy poziom.
To jest obserwacja użytkownika, nie dowód kodowy.

Cel:
slot → resource → TypedText → string → visibility/access → touch/callback → target screen.

## 13. NAJNOWSZY TROPIK — 4752C / 475A4

W rejonie Home znaleziono:
- FUN_0804752C: FUN_080307BC z **Bitmap resource 57** przy 0x08047558.
- FUN_080475A4: podobne wywołanie z **resource 57** przy 0x080475C2.

To jest ważne, ale:
**Bitmap resource 57 ≠ TypedText 57.**

TypedText 57 = „Ogrzewanie 1”.
Bitmap resource 57 musi zostać znaleziony jako 057.png i zbadany osobno.

## 14. TYPEDTEXTY CO

Potwierdzone:
- TypedText 57 = Ogrzewanie 1
- TypedText 58 = Ogrzewanie 2
- TypedText 99..102 = OGRZEWANIE 1..4
- TypedText 119..122 = Ogrzewanie obwód 1..4

Nie zakładaj, że te IDs są tekstami sześciu slotów. Najpierw odzyskaj param_7 i DAT_08047330.

## 15. ASSET ATLAS

189 prawdziwych PNG w web/img/panel:
000..187 + 76b.

Ważne:
077 MENU
079 header 480x45
094 tap/water
096 info
097 messages
098 service
099 profile
100 network
101 lock
115 power
120..137 35x37 family
138..143 status
144/145 CO1
146/147 CO2
153..155 Wi-Fi
157..161 schedule
163/165/167 horizontal sliders
164/166 vertical
173..176 water/CWU
177/178 switch
179 large 67x151
180/181 switch
182/183 flame/stop
184/185 OFF/ON
186/187 slider/gradient
011..013 boiler images
014 separate cascade resource

Zawsze używaj realnego PNG, nie zgaduj po wymiarach.

## 16. REALNY BOTTOM BAR

Użytkownik potwierdził:
[ MENU ][ ZASOBNIK ][ PALNIK ][ CO1 ][ PUSTY/CO2 ][ CWU ][ POWER ]

144.png = CO1 active, 145 alternate.  
146.png = CO2 active, 147 alternate.

Direct firmware writer proof dla 144/146 nadal OPEN.

## 17. NAJWAŻNIEJSZY PLAN NA NOWY CHAT

### PASS A — call sites 47334
Odzyskaj wszystkie call sites FUN_08047334.
Ustal wszystkie parametry, szczególnie **param_7**.

### PASS B — tables
Odzyskaj zawartość:
DAT_0804732C
DAT_08047330
i przypisz slot 0..5.

### PASS C — 4752C / 475A4
Rozwiń pełne funkcje, adresy 0x08047558/0x080475C2 i wszystkie resource IDs. Znajdź 057.png i jego realny wygląd.

### PASS D — TypedText
Dla każdego slotu:
TypedText ID → realny string.

### PASS E — visual
slot → Bitmap resource(s) → PNG → X/Y/W/H → parent/child.

### PASS F — access
Szukaj +0x158, PIN 0900/0999/0x1BF1, visibility/enable. Ustal czy menu jest filtrowane.

### PASS G — touch/callback
slot → touch method → handler → target screen/action.

### PASS H — CO/CWU cross-check
Porównaj z 144/145,146/147,173..176 oraz TypedText 57/58/99..102/119..122. Potrzebny jest kodowy most, nie tylko podobieństwo.

### PASS I — dopiero potem render
Renderuj dopiero z realnych assetów + realnej geometrii + parent/visibility.

## 18. RÓWNOLEGŁE OTWARTE TEMATY

Po wyczerpaniu 6-slot menu:
- dispatch C5B4,
- FUN_080424C4/+0x84C,
- pełna mutacja +0x85C/+0x888/+0x8B4/+0x8E0,
- runtime BitmapData 11/12/13,
- trzy sibling constructors 39A48/39B30/39C18,
- WheelSelectorExtra vptr/class proof,
- heating builder/raw tables,
- identity/profile.

Nie porzucaj głównego łańcucha na rzecz drobiazgu.

## 19. PERSISTENCJA

Po dużym multipass:
1. utwórz BATCH-....md,
2. zapisz dowody i corrections,
3. zaktualizuj MASTER,
4. zaktualizuj START-HERE,
5. commit,
6. podaj SHA i ścieżkę.

Nie zostawiaj wiedzy tylko w czacie.

## 20. OSTATECZNA REGUŁA

Nie próbuj szybko „zgadnąć co to jest”. Celem jest odzyskanie architektury:
**source trace → firmware object → resource/TypedText → geometry → parent → visibility → touch → handler → model → CAN/storage.**

Jeżeli nie ma dowodu: OPEN.
Jeżeli dowód obala starą teorię: CORRECTION.
Jeżeli jest pełny kodowy łańcuch: STRONG/PROVEN.

**Bieżący punkt wznowienia: sześć pionowych slotów 47290/47334 + 4752C/475A4 + param_7/DAT_08047330.**
