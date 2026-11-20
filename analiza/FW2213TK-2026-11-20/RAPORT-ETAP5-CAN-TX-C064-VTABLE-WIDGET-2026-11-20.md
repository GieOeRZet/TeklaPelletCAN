# TEKLAPELLET-CAN — RAPORT ETAP 5
Data: 2026-11-20
Repo: GieOeRZet/TeklaPelletCAN
Branch: ccr-be8a1bcb-5t76j0

## 0. ANTY-DUBLOWANIE
[CONFIRMED-REPEAT] Wcześniej zamknięte i nie liczone jako nowe: FUN_08037212 -> FUN_08011812; base+instance-1; istnienie CanTxTask/@CanMessagesToTransmit; DAT_0803C218=0x20005EF0; selectors 16/17/18; vptr setup FUN_08037CA4; FUN_0803E714 -> FUN_08036FF2 -> FUN_0804842C; widget base +0x42C, stride 0x338.

## 1. CAN TX / @CanMessagesToTransmit
[CONFIRMED-REPEAT] strings.txt: 0x08062ED0='CanRxTask', 0x08062EDC='CanTxTask', 0x08065553='@CanMessagesToTransmit'.
[CONFIRMED-REPEAT] FUN_0803EECC wywołuje FUN_08037212(context, parameter_id, value).
[OPEN] W functions.txt potwierdzono wskazane funkcje: 0x080618A0/120 B, 0x08061930/18 B, 0x08061942/20 B, 0x08062638/718 B, 0x08062920/212 B, 0x08062D82/238 B, 0x08062F18/324 B. Brak pełnych raw/dekompilacji tych funkcji w dostępnym eksporcie repo. Nie da się twardo wskazać producenta @CanMessagesToTransmit, formatu kolejki, encoder'a, CAN mailbox/peripheral ani ACK/SDO.
[OPEN] Punkt urwania pozostaje FUN_08037212 -> FUN_08011812 -> record/local storage. Nie dopisano hipotezy bxCAN/HAL.

## 2. DAT_0803C218 / 0x20005EF0 / C064
[CONFIRMED-REPEAT] DAT_0803C218 wskazuje runtime SRAM 0x20005EF0; C064 wykonuje switch na byte[DAT_0803C218+param_2].
[NEW-HARD] Dostępny RAW C064 pokazuje obsługę indeksów/klas 0..20. Klasy 1..4 kończą wspólną ścieżkę z +0x12B=1..4 oraz +0x12C=1..4. Klasy 5..10 wywołują odpowiednio FUN_080381E4, 080383B0, 08038278, 080382CA, 080382A6, 0803809C. 11..15 mają osobne ścieżki; 16 -> +0x12B=0x11, 17 -> +0x12B=0x10, 18 -> tabela 0x080387B8, 19 -> wybór 0x080387D0/0x080387D8, 20 -> +0x12B=0x13.
RAW fragment klas 1..4: 'case 1: iVar3=FUN_080314ba(); bVar4=1; break;' ... 'case 4: iVar3=FUN_080314ba(); bVar4=4; break;' następnie '+299=uVar6' i '+300=bVar4'.
[OPEN] Nie odzyskano literalnych 108 bajtów 0x20005EF0..0x20005F5B. Brak też bezpośredniego źródła ich inicjalizacji. Nie zgadywać zawartości.

## 3. VTABLE / FUN_0803EC18
[CONFIRMED-REPEAT] FUN_08037CA4 ustawia vptr przez DAT_08038694/DAT_0803869C; wcześniejszy RAW potwierdza indirect calls przez sloty +0x04,+0x08,+0x0C,+0x10,+0x14,+0x28.
[OPEN] Literalne wartości DAT_08038694/98/9C oraz cele slotów nadal wymagają BIN/Ghidra memory export.
[NEW-HARD] FUN_0803EC18 ma cztery twardo rozpoznane typy rekordów: type 5 -> FUN_08048520; type 0 -> FUN_08048468; type 3 -> FUN_080484B0; type 4 -> FUN_080484F0.
[NEW-HARD] Dla type 5: key 0x47 rozwiązuje 0x4A..0x4E, key 0x48 rozwiązuje 0x4F..0x53, a następnie oba warianty trafiają do FUN_08048520.
RAW: 'if (sVar2 == 0x47) { local_44=FUN_08036ff2(*puVar13,0x4a); ... local_24=FUN_08036ff2(*puVar13,0x4e); } else { ... 0x4f..0x53; } ... FUN_08048520(...)'.

## 4. WIDGET +0x42C + N*0x338
[CONFIRMED-REPEAT] FUN_080480C0 raw Thumb: 0x480E8 addw r4,r5,#0x42C; 0x4810A mov.w r0,#0x338; 0x48112 add r9,r0; druga pętla 0x4828A..0x482A2 ponownie używa N*0x338 + 0x42C.
[NEW-HARD] FUN_080480C0 zapisuje widget+0x334 z tabeli: '48172 ldrb r0,[r7,#0x7]; 48174 strh.w r0,[r9,#0x334]'.
[NEW-HARD] Dla type 1 zapisuje widget+0x270: po FUN_0804E598 następuje '4819E str.w r0,[r9,#0x270]'.
[NEW-HARD] Opisowy rekord tabeli ma stride 0x10; RAW używa pól +0x02, +0x04, +0x06, +0x07 oraz +0x08/+0x0C. Pole +0x06 wybiera typ 1/2/3/5.
[NEW-HARD] Type 1 -> FUN_0804E598 i +0x270; type 2 -> FUN_0804E740; type 3 -> FUN_0804E75A; type 5 -> FUN_0804E740; inne -> ścieżka FUN_0804E5BC(value,10).
[OPEN] Brak twardego linku widget N -> TypedText 119/120/121/122, brak twardego widget N -> konkretny Bitmap oraz brak twardego callbacku konkretnego CO widgetu. Sama tabela resource nie może być bezpośrednio utożsamiana z TypedText bez jej odzyskania i analizy callee.

## 5. NOWE CLOSURES
1. [NEW-HARD] C064: pełny switch klas 0..20 w dostępnej dekompilacji; klasy 1..4 ustawiają +0x12B/+0x12C.
2. [NEW-HARD] C064/EC18: pełne rozpoznanie czterech typów rekordów 5/0/3/4 i ich bezpośrednich callee.
3. [NEW-HARD] 480C0: potwierdzenie konkretnych pól widget record +0x334/+0x270 oraz tabeli 16-B rekordów resource.
4. [OPEN] CAN TX fizyczny chain.
5. [OPEN] 108-byte runtime selector table.
6. [OPEN] vtable slot targets.
7. [OPEN] widget -> exact TypedText/Bitmap/callback.

## 6. ŹRÓDŁA RAW
firmware/FW2213TK-ghidra/functions.txt
firmware/FW2213TK-ghidra/strings.txt
analiza/FW2213TK-2026-11-20/raw-snippets/0803c064-decompiled.c.txt
analiza/FW2213TK-2026-11-20/raw-snippets/0803ec18-decompiled.c.txt
analiza/FW2213TK-2026-11-20/MULTIPASS-23-IAR-LZ77-47-48-CLOSURE-480C0-TYPEDTEXT-RAW-2026-11-20.md