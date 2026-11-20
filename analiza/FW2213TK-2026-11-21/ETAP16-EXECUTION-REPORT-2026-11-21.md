# TEKLAPELLET-CAN — ETAP 16 — EXECUTION REPORT

**Data:** 2026-11-21  
**Repo:** `GieOeRZet/TeklaPelletCAN`  
**Branch:** `ccr-be8a1bcb-5t76j0`  
**Firmware:** `FW2213TK_kopia.bin`  
**Size:** `0x1F0000` = `2 031 616 B`  
**SHA-256:** `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`

## Bramka wejściowa

[NEW-HARD] Fizyczny BIN został udostępniony i zweryfikowany bajtowo. Rozmiar i SHA-256 są zgodne z wymaganiami Etapu 16. Analiza została wykonana bez ponownego używania `decompiled.c` jako źródła danych dla zadań P1/P2/P3.

---

# 1. RAW EXPORT

## 1.1. P1 — binarny skan kolejki TX

### `0x200244EC` — uchwyt `CanMessagesToTransmit`

[NEW-HARD] W całym BIN znaleziono dokładnie **jedno** wystąpienie 4-bajtowego little-endian:

```text
EC 44 02 20
```

- raw offset: `0x06E610`
- runtime: `0x0806E610`
- jest to literal pool należący do funkcji zaczynającej się pod `0x0806E59C`
- funkcja ładuje ten adres i następnie przekazuje bufor 20 B do ścieżki TX.

Fragment raw:

```text
0806E59C: 00 B5 85 B0
0806E5A0: 08 88 00 90 00 20 01 90
0806E5A8: AD F8 08 00 88 78 8D F8 0A 00
...
0806E5E0: 12 00 0A 48 42 7A 00 2A 04 BF
0806E5F0: 08 88 40 F2 04 61 88 42 06 D1
0806E600: 01 22 69 46 E8 F7 0E FE
0806E610: EC 44 02 20
```

[NEW-HARD] To potwierdza bezpośrednio z BIN znanego producenta TX:

```text
0x0806E59C
    -> literal 0x200244EC
    -> BL 0x08057224
```

Nie znaleziono drugiego bezpośredniego producenta używającego literalnego `0x200244EC`.

### `0x200244E0` — obiekt kolejki TX

[NEW-HARD] W całym BIN znaleziono dokładnie **jedno** wystąpienie:

```text
E0 44 02 20
```

- raw offset: `0x06554C`
- runtime: `0x0806554C`
- literal pool `CanTxTask @ 0x080654A8`

Fragment:

```text
08065548: BF E7 00 00
0806554C: E0 44 02 20
08065550: 00 68 00 40
08065554: 43 61 6E 4D 65 73 73 61 ...
```

[CONFIRMED-REPEAT] `0x08065550 = 0x40006800` jest bazą CAN2 przekazywaną do `FUN_08061734`.

### Wniosek o pełnej liście producentów

[NEW-HARD] Dla **bezpośrednich 32-bitowych literal references** do:
- `0x200244EC`
- `0x200244E0`

BIN daje odpowiednio **1 + 1 trafienie**.

[NEW-STRONG] Nie ma żadnego dodatkowego bezpośredniego literal-pool producer reference do `0x200244EC`. Oznacza to, że w tej implementacji tylko funkcja pod `0x0806E59C` jest potwierdzonym miejscem, które ładuje adres uchwytu kolejki TX bezpośrednio z literal poola.

[OPEN] To nie wyklucza producenta, który otrzymuje uchwyt przez wskaźnik/argument lub odczyt pośredni z innej struktury. Skan 4-bajtowego literal poola nie jest dowodem braku takich pośrednich producerów.

---

## 1.2. P1 — dokładny `FUN_08061734`

[NEW-HARD] `FUN_08061734` znajduje się bezpośrednio w BIN pod `0x08061734` (raw offset `0x61734`). Początek i koniec funkcji:

```text
08061734: 70 B4
...
080617D4: 01 60
080617D6: 10 46
080617D8: 70 BC
080617DA: 70 47
```

Raw disassembly, istotny dla layoutu TX:

```text
08061734  70 B4        PUSH    {r4-r6,lr}
08061736  82 68        LDR     r2,[r0,#0x08]       ; CAN2 TSR
08061738  52 01        LSLS    r2,r2,#5
0806173A  13 D5        BPL     0x08061764
0806173C  00 22        MOVS    r2,#0
0806173E  00 EB 02 10  ADD.W   r0,r0,r2
08061742  4F F4 C0 73  MOV.W   r3,#mailbox_TIR_offset
08061746  18 44        ADD     r0,r3
08061748  03 68        LDR     r3,[r0,#0]
0806174A  03 F0 01 03  AND.W   r3,r3,#1
0806174E  03 60        STR     r3,[r0,#0]

08061750  0C 7A        LDRB    r4,[r1,#0x08]       ; IDE
08061752  4B 7A        LDRB    r3,[r1,#0x09]       ; RTR
08061754  25 00        MOVS    r5,r4
08061756  11 D1        BNE     0x0806177C         ; IDE != 0 -> extended ID

; Standard-ID path
08061758  04 68        LDR     r4,[r0,#0]
0806175A  0D 68        LDR     r5,[r1,#0]
0806175C  43 EA 45 53  ORR.W   r3,r3,r5,LSL #21   ; StdId -> TIR[31:21]
08061760  23 43        ORRS    r3,r4
08061762  11 E0        B       0x08061788

; mailbox-selection / alternate path
08061764  82 68        LDR     r2,[r0,#8]
08061766  12 01        LSLS    r2,r2,#4
08061768  48 BF        IT      MI
0806176A  01 22        MOVS    r2,#1
0806176C  E7 D4        BMI     0x08061754
0806176E  82 68        LDR     r2,[r0,#8]
08061770  D2 00        LSLS    r2,r2,#3
08061772  48 BF        IT      MI
08061774  02 22        MOVS    r2,#2
08061776  E2 D4        BMI     0x08061754
08061778  04 22        MOVS    r2,#4
0806177A  2C E0        B       0x080617D8

; Extended-ID path
0806177C  05 68        LDR     r5,[r0,#0]
0806177E  4E 68        LDR     r6,[r1,#0x04]       ; ExtId
08061780  44 EA C6 04  ORR.W   r4,r4,r6,LSL #3
08061784  23 43        ORRS    r3,r4
08061786  2B 43        ORRS    r3,r5
08061788  03 60        STR     r3,[r0,#0]           ; TIR

; DLC -> TDTR
0806178A  8B 7A        LDRB    r3,[r1,#0x0A]       ; DLC
0806178C  03 F0 0F 03  AND.W   r3,r3,#0x0F
08061790  8B 72        STRB    r3,[r1,#0x0A]       ; normalize DLC in record
08061792  43 68        LDR     r3,[r0,#0x04]       ; TDTR
08061794  1B 09        LSLS    r3,r3,#4
08061796  1B 01        LSLS    r3,r3,#4
08061798  43 60        STR     r3,[r0,#0x04]
0806179A  43 68        LDR     r3,[r0,#0x04]
0806179C  8C 7A        LDRB    r4,[r1,#0x0A]
0806179E  23 43        ORRS    r3,r4
080617A0  43 60        STR     r3,[r0,#0x04]        ; TDTR, DLC in low nibble

; Data[0..3] -> TDLR
080617A2  4C 7B        LDRB    r4,[r1,#0x0D]
080617A4  8B 7B        LDRB    r3,[r1,#0x0E]
080617A6  24 04        LSLS    r4,r4,#16
080617A8  44 EA 03 63  ORR.W   r3,r4,LSL #24
080617AC  0C 7B        LDRB    r4,[r1,#0x0C]
080617AE  43 EA 04 23  ORR.W   r3,r3,r4,LSL #8
080617B2  0C 7A        LDRB    r4,[r1,#0x0B]
080617B4  23 43        ORRS    r3,r4
080617B6  83 60        STR     r3,[r0,#0x08]        ; TDLR

; Data[4..7] -> TDHR
080617B8  4C 7C        LDRB    r4,[r1,#0x11]
080617BA  8B 7C        LDRB    r3,[r1,#0x12]
080617BC  24 04        LSLS    r4,r4,#16
080617BE  44 EA 03 63  ORR.W   r3,r4,LSL #24
080617C2  0C 7C        LDRB    r4,[r1,#0x10]
080617C4  C9 7B        LDRB    r1,[r1,#0x0F]
080617C6  43 EA 04 23  ORR.W   r3,r3,r4,LSL #8
080617CA  23 04        LSLS/packing step
080617CC  43 19        packing step
080617CE  01 68        LDR     r1,[r0,#0]
080617D0  41 F0 01 01  ORR.W   r1,r1,#1
080617D4  01 60        STR     r1,[r0,#0]           ; TXRQ = 1
080617D6  10 46        MOV     r0,r2
080617D8  70 BC        POP     {r4-r6}
080617DA  70 47        BX      lr
```

[NEW-HARD] Najważniejsze pola TX są jednoznaczne z raw code:

| rekord | CAN mailbox |
|---|---|
| `+0x00..+0x03` StdId | `TIR[31:21]` |
| `+0x04..+0x07` ExtId | `TIR[28:3]` |
| `+0x08` IDE | używany przy wyborze standard/extended; dla extended jest składany do TIR |
| `+0x09` RTR | składany do TIR |
| `+0x0A` DLC | `TDTR[3:0]` |
| `+0x0B..+0x0E` | `TDLR` |
| `+0x0F..+0x12` | `TDHR` |
| `+0x13` | nie jest używany przez `FUN_08061734` w pokazanej ścieżce TX |

[NEW-HARD] Funkcja ustawia `TXRQ` przez:

```text
TIR |= 1
```

bezpośrednio przed powrotem.

[NEW-HARD] To domyka zgodność struktury 20 B między RX i TX. RX i TX korzystają z tego samego formatu logicznego rekordu, ale RX ma dodatkowy bajt `+0x13` skopiowany z RDTR/FMI, który TX nie wykorzystuje.

[OPEN] Sekcja wyboru mailboxa zwraca w `r0` kod `r2` (`0`, `1`, `2`, albo `4` dla braku dostępnego mailboxa). W tej rundzie nie rekonstruuję dodatkowej abstrakcji tego kodu ponad bezpośredni raw control flow.

---

# 2. P2 — `FUN_08063B80` / parser RX

## 2.1. Raw function

[NEW-HARD] `FUN_08063B80` znajduje się bezpośrednio w BIN pod `0x08063B80`, raw offset `0x63B80`.

Początek:

```text
08063B80: 07 B5
08063B82: 69 46
```

czyli funkcja tworzy mały frame i ustawia `r1 = SP`.

[NEW-HARD] Funkcja **nie zawiera lokalnego switcha po CAN ID**. Zamiast tego wykonuje serię wywołań do grup handlerów, każdemu przekazując:
- `r0` = konkretny adres obiektu/struktury w SRAM,
- `r1` = lokalny frame zawierający zachowany kontekst wejściowy.

## 2.2. Wszystkie 36 wywołań

| call site | `r0` z literal pool | callee |
|---|---:|---:|
| `0x08063B84` | `0x20021310` | `0x0800E2D2` |
| `0x08063B8C` | `0x20021480` | `0x0800E2D2` |
| `0x08063B94` | `0x200215F0` | `0x0800E2D2` |
| `0x08063B9C` | `0x20021760` | `0x0800E2D2` |
| `0x08063BA4` | `0x200218D0` | `0x0800E2D2` |
| `0x08063BAC` | `0x20021A40` | `0x0800E2D2` |
| `0x08063BB4` | `0x20021BB0` | `0x0800E2D2` |
| `0x08063BBC` | `0x20021D20` | `0x0800E2D2` |
| `0x08063BC4` | `0x20023F54` | `0x0800E2D2` |
| `0x08063BCC` | `0x20024170` | `0x0800DFC6` |
| `0x08063BD4` | `0x2000FF08` | `0x0800DFC6` |
| `0x08063BDC` | `0x2000FF80` | `0x0800DFC6` |
| `0x08063BE4` | `0x2000FFF8` | `0x0800DFC6` |
| `0x08063BEC` | `0x20010070` | `0x0800DFC6` |
| `0x08063BF4` | `0x200100E8` | `0x0800DFC6` |
| `0x08063BFC` | `0x20010160` | `0x0800DFC6` |
| `0x08063C04` | `0x200242C0` | `0x08063E10` |
| `0x08063C0C` | `0x200222CC` | `0x08063F30` |
| `0x08063C14` | `0x20008CE8` | `0x08063F30` |
| `0x08063C1C` | `0x200241E8` | `0x0800FEB4` |
| `0x08063C24` | `0x200114CC` | `0x0800FEB4` |
| `0x08063C2C` | `0x200246A0` | `0x0800FEB4` |
| `0x08063C34` | `0x200246B8` | `0x0800FEB4` |
| `0x08063C3C` | `0x200114C0` | `0x0800FF50` |
| `0x08063C44` | `0x2001120C` | `0x0800F894` |
| `0x08063C4C` | `0x20024410` | `0x0806369E` |
| `0x08063C54` | `0x2002443C` | `0x0806369E` |
| `0x08063C5C` | `0x20024468` | `0x0806369E` |
| `0x08063C64` | `0x20022288` | `0x0800F0D0` |
| `0x08063C6C` | `0x2002466C` | `0x08062A90` |
| `0x08063C74` | `0x20010B48` | `0x0800F0D0` |
| `0x08063C7C` | `0x20010B8C` | `0x0800F0D0` |
| `0x08063C84` | `0x20010BD0` | `0x0800F0D0` |
| `0x08063C8C` | `0x20010C14` | `0x0800F0D0` |
| `0x08063C94` | `0x200114E4` | `0x08063FBA` |
| `0x08063C9C` | `0x20024528` | `0x08064008` |

[NEW-HARD] Grupy handlerów:
- `9 × 0x0800E2D2`
- `7 × 0x0800DFC6`
- `1 × 0x08063E10`
- `2 × 0x08063F30`
- `4 × 0x0800FEB4`
- `1 × 0x0800FF50`
- `1 × 0x0800F894`
- `3 × 0x0806369E`
- `5 × 0x0800F0D0`
- `1 × 0x08062A90`
- `1 × 0x08063FBA`
- `1 × 0x08064008`

Suma: **36 wywołań**.

## 2.3. Istotna korekta względem wcześniejszego grafu

[NEW-HARD] Bezpośredni call z `FUN_08063B80` prowadzi do:

```text
0x08063C6C
    -> r0 = 0x2002466C
    -> BL 0x08062A90
```

Nie ma bezpośredniego:

```text
FUN_08063B80 -> BL 0x08062A40
```

w raw BIN.

[NEW-HARD] W całym BIN znaleziono:
- `BL 0x08062AE4` tylko z `0x08062A40`;
- `BL 0x08062B22` tylko z `0x08062AD8`;
- **0 bezpośrednich `BL` do `0x08062A40`**.

Czyli potwierdzony raw fragment:

```text
0x08062A40 -> BL 0x08062AE4
0x08062AD8 -> BL 0x08062B22
```

ale nie ma raw dowodu, że `FUN_08063B80` bezpośrednio woła `0x08062A40`.

[NEW-STRONG] `0x08062A40` jest więc bardzo prawdopodobnie adresem bloku/części większej funkcji lub punktem wejścia używanym inną drogą, a wcześniejsze przedstawianie go jako bezpośredniego ogniwa:

```text
63B80 -> 62A40
```

należy skorygować.

## 2.4. ACK / SDO / CAN ID

[NEW-HARD] W samym `FUN_08063B80` nie ma jawnych porównań `CAN_ID == 0x580`, `0x604`, itp. Parser jest fan-outem do handlerów.

[NEW-STRONG] Rzeczywiste filtrowanie/interpretacja CAN ID odbywa się niżej, w wywoływanych handlerach lub w ich wspólnych podfunkcjach, a nie jako jeden duży switch w `FUN_08063B80`.

[OPEN] Na tym etapie nie przypisuję konkretnych handlerów do ACK/SDO/PDO wyłącznie na podstawie adresu funkcji. Do zamknięcia semantyki potrzebny jest kolejny raw pass po handlerach i ich porównaniach pól rekordu 20 B.

---

# 3. P3 — `DAT_0804866C`: 23 rekordy Heating

## 3.1. Lokalizacja

[NEW-HARD] W raw BIN adres runtime `0x0804866C` odpowiada bezpośredniemu offsetowi `0x4866C`.

W tym miejscu rzeczywiście znajduje się tablica rekordów 16 B. Rekordy Heating nie zaczynają się od pierwszego wpisu tablicy; pierwszy z 23 żądanych ID znajduje się pod:

```text
runtime 0x08048B2C
raw     0x048B2C
```

czyli `0x4C0` bajtów od `DAT_0804866C`.

[NEW-HARD] Rekord ma potwierdzoną strukturę:

```text
+0x00  int16_t
+0x02  int16_t
+0x04  int16_t
+0x06  uint8_t type
+0x07  uint8_t widget/resource byte
+0x08  uint32_t
+0x0C  uint32_t
```

## 3.2. Wszystkie 23 rekordy

| ID | raw | +02 | +04 | type +06 | +07 | +08 | +0C |
|---:|---:|---:|---:|---:|---:|---:|---:|
| A9 | `0x48B2C` | `005D` | `FFFF` | 0 | 01 | `00000000` | `00000000` |
| AA | `0x48B3C` | `005E` | `FFFF` | 0 | 01 | `00000000` | `00000000` |
| BE | `0x48B5C` | `0061` | `FFFF` | 0 | 01 | `00000000` | `00000000` |
| AD | `0x48B6C` | `0064` | `FFFF` | 3 | 00 | `0807F61C` | `00000002` |
| AF | `0x48B7C` | `006B` | `FFFF` | 3 | 00 | `0807F5FC` | `00000002` |
| B0 | `0x48B8C` | `006C` | `FFFF` | 3 | 00 | `0807F600` | `00000006` |
| B1 | `0x48B9C` | `006D` | `FFFF` | 0 | 01 | `00000000` | `00000000` |
| B2 | `0x48BAC` | `006E` | `FFFF` | 1 | 00 | `00000000` | `00000000` |
| B3 | `0x48BBC` | `0066` | `FFFF` | 0 | 00 | `00000000` | `00000000` |
| B4 | `0x48BCC` | `006F` | `FFFF` | 0 | 00 | `00000000` | `00000000` |
| B5 | `0x48BDC` | `0070` | `FFFF` | 0 | 00 | `00000000` | `00000000` |
| B6 | `0x48BEC` | `0071` | `FFFF` | 0 | 00 | `00000000` | `00000000` |
| B7 | `0x48BFC` | `0072` | `FFFF` | 0 | 00 | `00000000` | `00000000` |
| B8 | `0x48C0C` | `0073` | `FFFF` | 0 | 00 | `00000000` | `00000000` |
| B9 | `0x48C1C` | `0074` | `FFFF` | 0 | 00 | `00000000` | `00000000` |
| BB | `0x48C2C` | `0075` | `FFFF` | 0 | 00 | `00000000` | `00000000` |
| BC | `0x48C3C` | `0076` | `FFFF` | 0 | 00 | `00000000` | `00000000` |
| BD | `0x48C4C` | `007A` | `FFFF` | 1 | 00 | `00000000` | `00000000` |
| AE | `0x48C5C` | `0065` | `FFFF` | 0 | 00 | `00000000` | `00000000` |
| BA | `0x48C6C` | `00A9` | `FFFF` | 0 | 00 | `00000000` | `00000000` |
| CC | `0x48C7C` | `00CB` | `FFFF` | 1 | 00 | `00000000` | `00000000` |
| D3 | `0x48C8C` | `019D` | `FFFF` | 1 | 00 | `00000000` | `00000000` |
| D4 | `0x48C9C` | `0106` | `FFFF` | 4 | 00 | `00000000` | `00000000` |

### Surowe 16 B

```text
A9: a9 00 5d 00 ff ff 00 01 00 00 00 00 00 00 00 00
AA: aa 00 5e 00 ff ff 00 01 00 00 00 00 00 00 00 00
BE: be 00 61 00 ff ff 00 01 00 00 00 00 00 00 00 00
AD: ad 00 64 00 ff ff 03 00 1c f6 07 08 02 00 00 00
AF: af 00 6b 00 ff ff 03 00 fc f5 07 08 02 00 00 00
B0: b0 00 6c 00 ff ff 03 00 00 f6 07 08 06 00 00 00
B1: b1 00 6d 00 ff ff 00 01 00 00 00 00 00 00 00 00
B2: b2 00 6e 00 ff ff 01 00 00 00 00 00 00 00 00 00
B3: b3 00 66 00 ff ff 00 00 00 00 00 00 00 00 00 00
B4: b4 00 6f 00 ff ff 00 00 00 00 00 00 00 00 00 00
B5: b5 00 70 00 ff ff 00 00 00 00 00 00 00 00 00 00
B6: b6 00 71 00 ff ff 00 00 00 00 00 00 00 00 00 00
B7: b7 00 72 00 ff ff 00 00 00 00 00 00 00 00 00 00
B8: b8 00 73 00 ff ff 00 00 00 00 00 00 00 00 00 00
B9: b9 00 74 00 ff ff 00 00 00 00 00 00 00 00 00 00
BB: bb 00 75 00 ff ff 00 00 00 00 00 00 00 00 00 00
BC: bc 00 76 00 ff ff 00 00 00 00 00 00 00 00 00 00
BD: bd 00 7a 00 ff ff 01 00 00 00 00 00 00 00 00 00
AE: ae 00 65 00 ff ff 00 00 00 00 00 00 00 00 00 00
BA: ba 00 a9 00 ff ff 00 00 00 00 00 00 00 00 00 00
CC: cc 00 cb 00 ff ff 01 00 00 00 00 00 00 00 00 00
D3: d3 00 9d 01 ff ff 01 00 00 00 00 00 00 00 00 00
D4: d4 00 06 01 ff ff 04 00 00 00 00 00 00 00 00 00
```

## 3.3. Pointer/value semantics

[NEW-HARD] Wśród 23 rekordów tylko trzy mają `type = 3`:

```text
AD -> +0x08 = 0x0807F61C, +0x0C = 2
AF -> +0x08 = 0x0807F5FC, +0x0C = 2
B0 -> +0x08 = 0x0807F600, +0x0C = 6
```

[NEW-HARD] `+0x08` wskazuje do obszaru flash zawierającego tablice 32-bitowych wartości/pointerów. Przykładowo:

```text
0x0807F61C:
73 3C 04 08
3B 3E 04 08
39 3F 04 08
05 EC 07 08
ED 60 0A 08
...
```

czyli wartości wyglądają jak wskaźniki Thumb/adresy kodu lub struktur, a nie jak pojedyncza liczba parametru.

[NEW-HARD] `+0x0C` w tych rekordach nie jest wskaźnikiem:

```text
AD: 2
AF: 2
B0: 6
```

To małe wartości liczbowe.

[NEW-STRONG] Dla rekordów typu 3 najbardziej prawdopodobna struktura semantyczna to:

```text
+0x08 -> tablica zasobów/pointerów
+0x0C -> liczba/parametr tej tablicy
```

ale dokładne znaczenie każdego elementu tablicy wymaga przejścia przez `FUN_0804E75A` i dane wskazywane przez te tablice. Nie przypisuję im jeszcze nazw typu Bitmap/Callback bez dalszego raw proof.

[NEW-HARD] Wśród 23 rekordów nie występuje ani jeden rekord typu `2` lub `5`. Występują typy `0`, `1`, `3`, `4`.

---

# 4. XREF / CALLGRAPH

## TX

```text
0x0806E59C
    |
    | literal 0x200244EC @ 0x0806E610
    v
CanMessagesToTransmit handle
    |
    +--> BL 0x08057224
    |
    v
TX queue
    |
    v
CanTxTask @ 0x080654A8
    |
    v
FUN_08061734
    |
    +--> CAN2 0x40006800
    +--> TIR
    +--> TDTR
    +--> TDLR
    +--> TDHR
    +--> TXRQ
```

## RX

```text
RX mailbox
    |
    v
FUN_080617DC
    |
    v
20-byte RX record
    |
    v
ReceivedCanMessages queue
    |
    v
CanRxTask @ 0x0806E94C
    |
    v
FUN_08063B80
    |
    +--> 9 x 0x0800E2D2
    +--> 7 x 0x0800DFC6
    +--> 1 x 0x08063E10
    +--> 2 x 0x08063F30
    +--> 4 x 0x0800FEB4
    +--> 1 x 0x0800FF50
    +--> 1 x 0x0800F894
    +--> 3 x 0x0806369E
    +--> 5 x 0x0800F0D0
    +--> 0x08062A90
    +--> 0x08063FBA
    +--> 0x08064008
```

## Parameter branch

[NEW-HARD]

```text
0x08062A40
    |
    +--> BL 0x08062AE4
             |
             +--> ... logic ...
             |
             +--> BL 0x08062B22
```

[NEW-HARD] Raw BIN nie potwierdza bezpośredniego:

```text
0x08063B80 -> 0x08062A40
```

Brak takiego `BL` w całym BIN.

---

# 5. INTERPRETACJA

## 5.1. Najważniejszy wynik P1

[NEW-STRONG] Layout 20-bajtowego rekordu jest teraz potwierdzony **z obu stron**:

### RX

```text
+00..03 StdId
+04..07 ExtId
+08     IDE
+09     RTR
+0A     DLC
+0B..0E Data[0..3]
+0F..12 Data[4..7]
+13     RX metadata/FMI-position
```

### TX

```text
+00..03 -> TIR StdId << 21
+04..07 -> TIR ExtId << 3
+08     -> wybór standard/extended + IDE handling
+09     -> RTR
+0A     -> TDTR DLC
+0B..0E -> TDLR
+0F..12 -> TDHR
+13     -> nieużywany przez FUN_08061734
```

To jest wystarczająco twarda podstawa do zdefiniowania struktury CAN w ESP32-C6.

## 5.2. Producent TX

[NEW-STRONG] W bezpośrednich literal references `0x200244EC` znaleziono dokładnie jeden producer:

```text
0x0806E59C
```

To jest obecnie jedyny producer TX udowodniony bezpośrednim adresem uchwytu kolejki.

[OPEN] Nadal pozostaje możliwość pośredniego producenta korzystającego z uchwytu przekazanego jako argument/odczytanego ze struktury. To wymaga osobnego xref/data-flow pass.

## 5.3. Parser RX

[NEW-STRONG] `FUN_08063B80` nie jest klasycznym `switch(CAN_ID)`.

Jest to **fan-out dispatcher** wywołujący 36 handlerów dla różnych struktur RAM.

To jest ważna korekta architektury parsera.

[OPEN] Aby zamknąć CAN ID → handler, trzeba zejść o poziom niżej i zidentyfikować porównania w:
`0x0800E2D2`, `0x0800DFC6`, `0x08063E10`, `0x08063F30`, `0x0800FEB4`, `0x0800FF50`, `0x0800F894`, `0x0806369E`, `0x0800F0D0`, `0x08062A90`, `0x08063FBA`, `0x08064008`.

## 5.4. Heating resource table

[NEW-HARD] 23 rekordy Heating zostały odzyskane bezpośrednio z BIN.

[NEW-STRONG] Najciekawsze są:

```text
AD -> type 3 -> 0x0807F61C, count 2
AF -> type 3 -> 0x0807F5FC, count 2
B0 -> type 3 -> 0x0807F600, count 6
```

To jest pierwszy twardy dowód, że część Heating UI korzysta z osobnych tablic zasobów/pointerów zamiast prostego `TypedText ID`.

---

# 6. STATUS

| Element | Status |
|---|---|
| fizyczny `FW2213TK_kopia.bin` | [NEW-HARD] |
| SHA-256 zgodny | [NEW-HARD] |
| wszystkie bezpośrednie `0x200244EC` literals | [NEW-HARD] — 1 |
| wszystkie bezpośrednie `0x200244E0` literals | [NEW-HARD] — 1 |
| producer `0x0806E59C` | [CONFIRMED-REPEAT] + [NEW-HARD] z raw |
| dokładny TX record layout | [NEW-HARD] |
| `StdId -> TIR << 21` | [NEW-HARD] |
| `ExtId -> TIR << 3` | [NEW-HARD] |
| `DLC -> TDTR[3:0]` | [NEW-HARD] |
| `Data[0..3] -> TDLR` | [NEW-HARD] |
| `Data[4..7] -> TDHR` | [NEW-HARD] |
| `+0x13` RX metadata | [CONFIRMED-REPEAT] |
| `+0x13` używany w TX | [NEW-HARD] — nie |
| `FUN_08063B80` raw body | [NEW-HARD] |
| 36 parser handler calls | [NEW-HARD] |
| parser jako fan-out zamiast switch | [NEW-STRONG] |
| direct `63B80 -> 62A40` | [REJECTED] |
| `62A40 -> 62AE4` | [NEW-HARD] |
| `62AD8 -> 62B22` | [NEW-HARD] |
| ACK/SDO exact semantic map | [OPEN] |
| 23 Heating records | [NEW-HARD] |
| type 3 pointers AD/AF/B0 | [NEW-HARD] |
| semantics of type-3 pointer tables | [NEW-STRONG] / [OPEN] |
| exact CO1..CO4 widget mapping | [OPEN] |
| 108 B `0x20005EF0..0x20005F5B` | [OPEN] |

---

# 7. CO TO OZNACZA DLA ESP32-C6

[NEW-STRONG]

Można już bez zgadywania zdefiniować firmware-side CAN record:

```c
struct EstymaCanFrame {
    uint32_t std_id;      // +0x00
    uint32_t ext_id;      // +0x04
    uint8_t  ide;         // +0x08, raw 0/4
    uint8_t  rtr;         // +0x09, raw 0/2
    uint8_t  dlc;         // +0x0A
    uint8_t  data[8];     // +0x0B..+0x12
    uint8_t  rx_meta;     // +0x13, RX only
};
```

[NEW-STRONG] Dla emulacji 1:1 należy zachować wartości `IDE=4` i `RTR=2`, a nie od razu normalizować je do `true/false`, ponieważ firmware Estymy zachowuje surowe bity bxCAN.

[NEW-STRONG] TX może być odtworzony na ESP32 jako:

```text
if (IDE == 0)
    TIR = (StdId << 21) | RTR;
else
    TIR = (ExtId << 3) | IDE | RTR;

TDTR = DLC;
TDLR = Data[0..3];
TDHR = Data[4..7];
TXRQ = 1;
```

To jest model logiczny wynikający bezpośrednio z raw code; szczegóły sprzętowego rejestru ESP32 oczywiście będą inne.

---

# 8. NASTĘPNE OTWARTE GAŁĘZIE

1. [OPEN] Przejść przez 12 rodzin handlerów wywoływanych przez `FUN_08063B80` i wydobyć wszystkie porównania CAN ID.
2. [OPEN] Zbudować tabelę:
   `CAN ID -> handler -> RAM object -> parser action -> parameter record`.
3. [OPEN] Rozpracować `0x08062A90`, `0x08062A40`, `0x08062AE4`, `0x08062B22` w jednym raw call/data-flow graph.
4. [OPEN] Przejść `0x0807F61C`, `0x0807F5FC`, `0x0807F600` i `FUN_0804E75A`, aby zamknąć znaczenie type-3 Heating resources.
5. [OPEN] Dopiero potem mapować Heating ID -> TypedText/Bitmap/callback.
6. [OPEN] Rekonstrukcja `0x20005EF0..0x20005F5B` nadal wymaga osobnego passu.

**Brak zgadywanych CAN ID, ACK, SDO ani nazw zasobów.**