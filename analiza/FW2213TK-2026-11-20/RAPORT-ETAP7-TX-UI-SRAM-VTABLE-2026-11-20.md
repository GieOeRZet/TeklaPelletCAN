# TEKLAPELLET-CAN — RAPORT ETAP 7
Data: 2026-11-20
Repo: GieOeRZet/TeklaPelletCAN
Branch: ccr-be8a1bcb-5t76j0

## 0. ZASADA ANTY-DUBLOWANIA
Etap 7 wykonano wyłącznie jako próbę odzyskania materiału istniejącego już w repozytorium/historii oraz jako inwentaryzację brakujących eksportów. Nie przedstawiam zamkniętych ustaleń jako nowych.

## 1. OBEJŚCIE PUSTEGO decompiled.c

### [CONFIRMED-REPEAT]
firmware/FW2213TK-ghidra/decompiled.c nadal ma blob SHA 9620d0c85259d34bb6a20d3b03b038945dfe4c1a, ale fetch na branchu ccr-be8a1bcb-5t76j0 zwraca pustą treść.

### [NEW-STRONG]
Istniejący committed bundle: analiza/FW2213TK-2026-11-20/RAW-DECOMPILED-SNIPPET-BUNDLE-0x68-GRAPH-REGISTRY-2026-11-20.md zawiera dokładne bloki wybranych funkcji z decompiled.c, ale sprawdzenie jego treści wykazało brak pełnych bloków dla:
- 0x080618A0
- 0x08061930
- 0x08061942
- 0x08062638
- 0x08062920
- 0x08062D82
- 0x08062F18
- 0x0804E598
- 0x0804E740
- 0x0804E75A
- 0x0804E5BC
Bundle zawiera jedynie odniesienia do FUN_08032316, nie jego pełny blok.

### [CONFIRMED-REPEAT]
firmware/FW2213TK-ghidra/functions.txt potwierdza same funkcje i ich rozmiary: 0x080618A0/120 B, 0x08061930/18 B, 0x08061942/20 B, 0x08062638/718 B, 0x08062920/212 B, 0x08062D82/238 B, 0x08062F18/324 B, 0x0804E598/36 B, 0x0804E5BC/362 B, 0x0804E740/26 B, 0x0804E75A/26 B, 0x08032316/30 B.

### [OPEN]
W repo nie znaleziono alternatywnego committed raw-disassembly/decompiled body dla tych funkcji. Brakujący materiał to przede wszystkim: surowe bajty BIN, Thumb disassembly, xref/callgraph oraz dla TX xref do @CanMessagesToTransmit i CanTxTask. Nie rekonstruuję ciał z samych nazw/adresów.

## 2. ISTNIEJĄCE RAPORTY / 0x20005EF0 / VTABLE / CO1..CO4
### [CONFIRMED-REPEAT]
W istniejących raportach powtarzają się już zamknięte fakty: DAT_0803C218=0x20005EF0; FUN_0803C064 czyta DAT_0803C218[param_2]; klasy 1..4 ustawiają +0x12B i +0x12C; TypedText 119..122 = Ogrzewanie obwód 1..4; 0x0807F5EC / 0x6F5EC / keys 0x47,0x48 / type 5 / value 0x0037 (TypedText 55); vtable/data addresses DAT_08038694/98/9C są znane, ale literalne wartości slotów nadal nie są odzyskane.

### [OPEN]
Przeszukanie istniejących raportów pod kątem 0x20005EF0 / DAT_0803C218, DAT_08038694/98/9C, 0x0807F5EC, TypedText 119..122, CO1..CO4 i callback nie ujawniło nowego literalnego dumpu 108 B, literalnych vtable pointerów ani twardego 1:1 widget->TypedText/Bitmap/callback dla CO1..CO4.

## 3. WAŻNA KOREKTA RAPORTU ETAPU 6
### [NEW-HARD]
W Etapie 6 zapisano błędnie, że zakres 0x20005EF0..0x20005F5B leży poza odzyskanym SRAM 0x20000000..0x200118B3. To jest arytmetycznie nieprawidłowe. 0x20005EF0 i cały zakres 0x20005EF0..0x20005F5B mieszczą się w 0x20000000..0x200118B3.
Prawidłowy status: adres jest w zrekonstruowanym zakresie SRAM; w dostępnych artefaktach nie odzyskano jednak literalnej zawartości tych 108 B w sposób pozwalający użyć ich jako twardego dumpu; źródło/inicjalizator nadal jest OPEN.

## 4. MINIMALNY ZRZUT POTRZEBNY DO ZAMKNIĘCIA OPEN
### A. CAN TX
Surowe bajty Thumb dokładnie dla:
- 0x080618A0..0x08061917 — 120 B
- 0x08061930..0x08061941 — 18 B
- 0x08061942..0x08061955 — 20 B
- 0x08062638..0x08062905 — 718 B
- 0x08062920..0x080629F3 — 212 B
- 0x08062D82..0x08062E6F — 238 B
- 0x08062F18..0x0806305B — 324 B
oraz xref/callers dla @CanMessagesToTransmit, CanTxTask i CanRxTask. Najlepiej jeden eksport: adres, bajty, Thumb disassembly, call/xref target.

### B. UI/resource helpers
Surowe bajty + Thumb disassembly:
- 0x0804E598..0x0804E5BB — 36 B
- 0x0804E5BC..0x0804E725 — 362 B
- 0x0804E740..0x0804E759 — 26 B
- 0x0804E75A..0x0804E773 — 26 B
- 0x08032316..0x08032333 — 30 B
Dodatkowo bardzo wskazany helper: 0x0804E4F8..0x0804E597 — 160 B oraz xref/callers tych funkcji.

### C. DAT_0803C218 / 108 B
Runtime RAM dump: 0x20005EF0..0x20005F5B — dokładnie 108 B. Najlepiej z adresami i informacją, skąd pochodzi blok (loader/init/struct field). Sam BIN nie wystarczy, jeżeli bajty są tworzone lub zmieniane dopiero w RAM.

### D. VTABLE
Literalne bajty: 0x08038694..0x080386BF, 0x08038698..0x080386C3, 0x0803869C..0x080386C7. Trzeba oznaczyć, które wartości są wskaźnikami do kodu, danych albo innym polem struktury.

### E. CO1..CO4 widget mapping
Potrzebne są xref do konstruktorów/initializerów widgetów powiązanych z FUN_0803E714, zapisy do object + 0x42C + N*0x338, wywołania FUN_080480C0, literalne wartości resource table oraz ewentualny vtable slot + target. To ma pozwolić dojść do CO1/CO2/CO3/CO4 -> widget record -> TypedText -> Bitmap -> callback/write path.

## 5. WYNIK ETAPU 7
### [NEW-HARD]
1. Zweryfikowano branch ccr-be8a1bcb-5t76j0 bezpośrednio: decompiled.c ma pusty fetch, ale committed snippet bundle jest dostępny.
2. Zweryfikowano zawartość snippet bundle: nie zawiera pełnych ciał 11 z 12 wskazanych funkcji; FUN_08032316 występuje tylko jako wywołanie.
3. Skorygowano błąd Etapu 6 dotyczący zakresu SRAM.

### [NEW-STRONG]
Istniejące raw-snippets/bundle nie stanowią ukrytej kopii brakujących funkcji TX ani helperów 4E598/4E740/4E75A/4E5BC. Historia commitów zawiera wcześniejsze pakiety RAW, ale nie znaleziono w nich committed ciał wskazanych funkcji; brakujący materiał nadal trzeba dostarczyć z lokalnego Ghidra/BIN.

### [CONFIRMED-REPEAT]
Funkcje TX i ich rozmiary; CanTxTask/@CanMessagesToTransmit; DAT_0803C218=0x20005EF0; TypedText 119..122; 0x0807F5EC -> 0x0037 / TypedText 55; vtable addresses bez literalnych targetów.

### [OPEN]
1. Fizyczny CAN TX chain.
2. 7 ciał funkcji TX.
3. 5 ciał helperów UI.
4. 108 B RAM 0x20005EF0..0x20005F5B.
5. Literalne vtable.
6. 1:1 CO1..CO4 widget/resource/callback mapping.

## 6. ŹRÓDŁA
- firmware/FW2213TK-ghidra/decompiled.c
- firmware/FW2213TK-ghidra/functions.txt
- analiza/FW2213TK-2026-11-20/RAW-DECOMPILED-SNIPPET-BUNDLE-0x68-GRAPH-REGISTRY-2026-11-20.md
- wcześniejsze raporty analiza/FW2213TK-2026-11-19/ i analiza/FW2213TK-2026-11-20/
- commit history repozytorium