# TEKLAPELLET-CAN — RAPORT ETAP 6
Data: 2026-11-20
Repo: GieOeRZet/TeklaPelletCAN
Branch: ccr-be8a1bcb-5t76j0

## 0. ZASADA ANTY-DUBLOWANIA
[CONFIRMED-REPEAT] Nie ponawiam jako nowych: FUN_08037212 -> FUN_08011812; istnienie CanTxTask/@CanMessagesToTransmit; DAT_0803C218=0x20005EF0; switch C064 i klasy 1..20; vptr/registry zamknięte wcześniej; widget base +0x42C/stride 0x338.

## 1. CAN TX — próba ekstrakcji wskazanych funkcji
[OPEN] Wskazane adresy są obecne w funkcjach.txt, ale aktualny GitHub fetch dla `firmware/FW2213TK-ghidra/decompiled.c` zwraca pustą treść przy zachowanym SHA blob `9620d0c85259d34bb6a20d3b03b038945dfe4c1a`. Nie ma więc dostępnego tekstowego ciała dekompilacji, z którego można bezpośrednio wyciągnąć pełne ciała:
- 0x080618A0 / FUN_080618A0
- 0x08061930 / FUN_08061930
- 0x08061942 / FUN_08061942
- 0x08062638 / FUN_08062638
- 0x08062920 / FUN_08062920
- 0x08062D82 / FUN_08062D82
- 0x08062F18 / FUN_08062F18.
[CONFIRMED-REPEAT] `strings.txt` nadal daje `CanRxTask`, `CanTxTask`, `@CanMessagesToTransmit`.
[OPEN] Nie znaleziono w dostępnych artefaktach nowego, bezpośredniego dowodu łączącego te symbole z encoderem CAN, kolejką, mailboxem lub ACK/SDO. Nie wolno uznać samych adresów funkcji za taki dowód.
[OPEN] Łańcuch nadal urywa się na potwierdzonym `FUN_08037212 -> FUN_08011812 -> record/local storage`.

## 2. 0x20005EF0 / DAT_0803C218 / VTABLE
[CONFIRMED-REPEAT] `DAT_0803C218` wskazuje `0x20005EF0`, a `FUN_0803C064` czyta `byte[DAT_0803C218 + param_2]`.
[OPEN] Dostępny zrekonstruowany SRAM obejmuje `0x20000000..0x200118B3`; nie zawiera zakresu `0x20005EF0`, ponieważ ten adres leży poza odzyskanym blokiem. Zatem nie ma w obecnym materiale literalnych 108 bajtów `0x20005EF0..0x20005F5B`.
[OPEN] Nie odzyskano źródła inicjalizacji tej tablicy z dostępnego eksportu `decompiled.c`.
[OPEN] `DAT_08038694/98/9C` oraz sloty `+0x04,+0x08,+0x0C,+0x10,+0x14,+0x28` nadal wymagają raw memory/BIN export. Sam tekstowy raport nie zawiera literalnych wartości wskaźników.

## 3. WIDGET / RESOURCE / CALLBACK
[CONFIRMED-REPEAT] `FUN_080480C0` używa 16-bajtowych opisów resource i pola `+0x06` do wyboru type 1/2/3/5.
[CONFIRMED-REPEAT] Type 1 -> `FUN_0804E598` i zapis widget+0x270; type 2/5 -> `FUN_0804E740`; type 3 -> `FUN_0804E75A`; ścieżka ogólna -> `FUN_0804E5BC`.
[NEW-HARD] Z wcześniejszego dostępnego artefaktu UI: wpis przy `0x0807F5EC` jest opisany jako rekord dla `0x47/0x48`, type 5, count 1, z wartością `{0x0037}`; dokumentacja analizy wiąże tę wartość z TypedText ID 55 i przekazaniem przez `FUN_080480C0` do `FUN_0804E740`. To nie jest jednak dowód dla CO1..CO4 ani TypedText 119..122.
[CONFIRMED-REPEAT] `FUN_08048468`, `FUN_080484B0`, `FUN_080484F0` ustawiają content `+0x25 = 1`, wołają `FUN_0802EADE`, a następnie `FUN_08032316(content)`; `FUN_08048520` nie wykonuje tych dwóch operacji bezpośrednio.
[OPEN] Brak dostępnego ciała `FUN_0804E598/740/75A/5BC` pozwalającego twardo zmapować rekord `+0x42C+N*0x338` do TypedText 119..122, konkretnego Bitmap ID i callbacku konkretnego widgetu CO.
[OPEN] Nie wolno utożsamiać `0x0037`/TypedText 55 z `119..122`.

## 4. WYNIK ETAPU 6
### [NEW-HARD]
- Brak nowych closure w fizycznym CAN TX z powodu niedostępnego ciała `decompiled.c` w narzędziu fetch; nie przedstawiam blokady jako odkrycia firmware.
- Dostępny materiał pozwala potwierdzić osobno istniejący rekord resource `0x0807F5EC -> {0x0037}` / TypedText 55, ale nie zamyka CO widget mapping.

### [OPEN]
1. Pełna dekompilacja/dysasembler 7 funkcji TX.
2. Producer/consumer `@CanMessagesToTransmit`.
3. Format elementu TX i encoder.
4. CAN peripheral/mailbox.
5. ACK/SDO correlation.
6. Literalne 108 B `0x20005EF0..0x20005F5B`.
7. Literalne vtable `DAT_08038694/98/9C` i cele slotów.
8. Ciała `FUN_0804E598/740/75A/5BC/32316` potrzebne do 1:1 resource/callback mapping.

## 5. BLOKER ŹRÓDŁOWY
Najważniejszy problem techniczny tego przebiegu: repozytoryjny blob `firmware/FW2213TK-ghidra/decompiled.c` istnieje według GitHub metadata (SHA `9620d0c85259d34bb6a20d3b03b038945dfe4c1a`), lecz connector zwraca dla niego pustą zawartość. W repo są natomiast `functions.txt`, `strings.txt` i wcześniejsze raporty RAW. Bez samego ciała dekompilacji/raw BIN nie należy rekonstruować brakujących funkcji z nazw/adresów.

## 6. ŹRÓDŁA
- `firmware/FW2213TK-ghidra/decompiled.c` — metadata dostępne, content fetch pusty.
- `firmware/FW2213TK-ghidra/functions.txt` — adresy funkcji dostępne.
- `firmware/FW2213TK-ghidra/strings.txt` — nazwy CanRxTask/CanTxTask/@CanMessagesToTransmit.
- wcześniejsze raporty `analiza_archiwum/FW2213TK-2026-11-20/`.