# TEKLAPELLET-CAN — ETAP 17 — EXECUTION REPORT

**Data:** 2026-11-21  
**Repo:** `GieOeRZet/TeklaPelletCAN`  
**Branch:** `ccr-be8a1bcb-5t76j0`  
**Firmware:** `FW2213TK_kopia.bin`  
**Size:** `0x1F0000` = 2,031,616 B  
**SHA-256:** `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`

Źródłem wykonania był fizyczny BIN. Nie używano `decompiled.c` jako źródła dla P1/P2/P3.

---

# 1. RAW EXPORT

## 1.1 P1 — callers i pełne ciało `0x0806E59C`

### Direct caller scan

[NEW-HARD] Pełny skan Thumb-2 wykazał:
- bezpośrednie `BL -> 0x0806E59C`: **0**
- bezpośrednie `B.W -> 0x0806E59C`: **0**
- literal `0x0806E59C`: **0**
- literal Thumb `0x0806E59D`: **0**

[NEW-STRONG] `0x0806E59C` jest potwierdzonym miejscem używającym `0x200244EC`, ale nie ma bezpośredniego caller'a przez `BL/B.W`. Sama obecność literal-pool `0x200244EC` nie wystarcza więc do uznania tej funkcji za aktywne centralne TX API.

[OPEN] Pozostaje możliwość wywołania pośredniego przez callback/wskaźnik; w tej rundzie nie znaleziono literalnego wskaźnika do `0x0806E59C`.

### Pełne ciało

Raw `0x6E59C`, runtime `0x0806E59C`:

```text
00000000 <_binary__tmp_fw17_bin_start>:
   6e59c: b500         	push	{lr}
   6e59e: b085         	sub	sp, #0x14
   6e5a0: 8808         	ldrh	r0, [r1]
   6e5a2: 9000         	str	r0, [sp]
   6e5a4: 2000         	movs	r0, #0x0
   6e5a6: 9001         	str	r0, [sp, #0x4]
   6e5a8: f8ad 0008    	strh.w	r0, [sp, #0x8]
   6e5ac: 7888         	ldrb	r0, [r1, #0x2]
   6e5ae: f88d 000a    	strb.w	r0, [sp, #0xa]
   6e5b2: 78c8         	ldrb	r0, [r1, #0x3]
   6e5b4: f88d 000b    	strb.w	r0, [sp, #0xb]
   6e5b8: 7908         	ldrb	r0, [r1, #0x4]
   6e5ba: f88d 000c    	strb.w	r0, [sp, #0xc]
   6e5be: 7948         	ldrb	r0, [r1, #0x5]
   6e5c0: f88d 000d    	strb.w	r0, [sp, #0xd]
   6e5c4: 7988         	ldrb	r0, [r1, #0x6]
   6e5c6: f88d 000e    	strb.w	r0, [sp, #0xe]
   6e5ca: 79c8         	ldrb	r0, [r1, #0x7]
   6e5cc: f88d 000f    	strb.w	r0, [sp, #0xf]
   6e5d0: 7a08         	ldrb	r0, [r1, #0x8]
   6e5d2: f88d 0010    	strb.w	r0, [sp, #0x10]
   6e5d6: 7a48         	ldrb	r0, [r1, #0x9]
   6e5d8: f88d 0011    	strb.w	r0, [sp, #0x11]
   6e5dc: 7a88         	ldrb	r0, [r1, #0xa]
   6e5de: f88d 0012    	strb.w	r0, [sp, #0x12]
   6e5e2: 480a         	ldr	r0, [pc, #0x28]         @ 0x6e60c <_binary__tmp_fw17_bin_start+0x6e60c>
   6e5e4: 7a42         	ldrb	r2, [r0, #0x9]
   6e5e6: 2a00         	cmp	r2, #0x0
   6e5e8: bf04         	itt	eq
   6e5ea: 7a80         	ldrbeq	r0, [r0, #0xa]
   6e5ec: 2801         	cmpeq	r0, #0x1
   6e5ee: bf1e         	ittt	ne
   6e5f0: 8808         	ldrhne	r0, [r1]
   6e5f2: f240 6104    	movwne	r1, #0x604
   6e5f6: 4288         	cmpne	r0, r1
   6e5f8: d106         	bne	0x6e608 <_binary__tmp_fw17_bin_start+0x6e608> @ imm = #0xc
   6e5fa: 4805         	ldr	r0, [pc, #0x14]         @ 0x6e610 <_binary__tmp_fw17_bin_start+0x6e610>
   6e5fc: 6800         	ldr	r0, [r0]
   6e5fe: 2300         	movs	r3, #0x0
   6e600: 2201         	movs	r2, #0x1
   6e602: 4669         	mov	r1, sp
   6e604: f7e8 fe0e    	bl	0x57224 <_binary__tmp_fw17_bin_start+0x57224> @ imm = #-0x173e4
   6e608: b005         	add	sp, #0x14
   6e60a: bd00         	pop	{pc}
```

[NEW-HARD] Funkcja:
1. rezerwuje `0x14` B na stosie,
2. pobiera wejście z `r1`,
3. buduje lokalny bufor przez `[r1+0]` oraz bajty `[r1+2..0xA]`,
4. korzysta z obiektu `0x2002466C`,
5. blokuje wysyłkę przy `byte[+9]==0 && byte[+10]==1`,
6. w pozostałym przypadku wymaga wejściowego ID `0x0604`,
7. pobiera uchwyt `CanMessagesToTransmit` z `0x200244EC`,
8. wywołuje `0x08057224` z `r0=*0x200244EC`, `r1=SP`, `r2=1`, `r3=0`.

Literal pool:
```text
0x0806E60C -> 0x2002466C
0x0806E610 -> 0x200244EC
```

[NEW-STRONG] `0x0806E59C` jest wyspecjalizowanym wrapperem dla ścieżki `0x0604`, nie ogólnym `CanSendMessage(frame)`.

---

## 1.2 P2 — `0x08062A90` i blok `0x08062A00..0x08062B22`

### `0x08062A90`

```text
00000000 <_binary__tmp_fw17_bin_start>:
   62a90: b538         	push	{r3, r4, r5, lr}
   62a92: 0004         	movs	r4, r0
   62a94: 000d         	movs	r5, r1
   62a96: 8828         	ldrh	r0, [r5]
   62a98: f5b0 7f10    	cmp.w	r0, #0x240
   62a9c: db09         	blt	0x62ab2 <_binary__tmp_fw17_bin_start+0x62ab2> @ imm = #0x12
   62a9e: 8828         	ldrh	r0, [r5]
   62aa0: f5b0 7f16    	cmp.w	r0, #0x258
   62aa4: da05         	bge	0x62ab2 <_binary__tmp_fw17_bin_start+0x62ab2> @ imm = #0xa
   62aa6: 2001         	movs	r0, #0x1
   62aa8: 7260         	strb	r0, [r4, #0x9]
   62aaa: 0020         	movs	r0, r4
   62aac: f000 f8e4    	bl	0x62c78 <_binary__tmp_fw17_bin_start+0x62c78> @ imm = #0x1c8
   62ab0: 8260         	strh	r0, [r4, #0x12]
   62ab2: 8828         	ldrh	r0, [r5]
   62ab4: f240 5184    	movw	r1, #0x584
   62ab8: 4288         	cmp	r0, r1
   62aba: d112         	bne	0x62ae2 <_binary__tmp_fw17_bin_start+0x62ae2> @ imm = #0x24
   62abc: 7b20         	ldrb	r0, [r4, #0xc]
   62abe: 2800         	cmp	r0, #0x0
   62ac0: d00f         	beq	0x62ae2 <_binary__tmp_fw17_bin_start+0x62ae2> @ imm = #0x1e
   62ac2: 7c20         	ldrb	r0, [r4, #0x10]
   62ac4: 2801         	cmp	r0, #0x1
   62ac6: d10c         	bne	0x62ae2 <_binary__tmp_fw17_bin_start+0x62ae2> @ imm = #0x18
   62ac8: 78e8         	ldrb	r0, [r5, #0x3]
   62aca: b2c0         	uxtb	r0, r0
   62acc: 0940         	lsrs	r0, r0, #0x5
   62ace: b2c0         	uxtb	r0, r0
   62ad0: 2802         	cmp	r0, #0x2
   62ad2: d106         	bne	0x62ae2 <_binary__tmp_fw17_bin_start+0x62ae2> @ imm = #0xc
   62ad4: 0029         	movs	r1, r5
   62ad6: 0020         	movs	r0, r4
   62ad8: f000 f823    	bl	0x62b22 <_binary__tmp_fw17_bin_start+0x62b22> @ imm = #0x46
   62adc: 88e0         	ldrh	r0, [r4, #0x6]
   62ade: 1c40         	adds	r0, r0, #0x1
   62ae0: 80e0         	strh	r0, [r4, #0x6]
   62ae2: bd31         	pop	{r0, r4, r5, pc}
   62ae4: b53e         	push	{r1, r2, r3, r4, r5, lr}
   62ae6: 0004         	movs	r4, r0
   62ae8: 000d         	movs	r5, r1
   62aea: 2008         	movs	r0, #0x8
   62aec: f88d 0002    	strb.w	r0, [sp, #0x2]
   62af0: 2040         	movs	r0, #0x40
   62af2: f88d 0003    	strb.w	r0, [sp, #0x3]
   62af6: 0028         	movs	r0, r5
   62af8: f88d 0004    	strb.w	r0, [sp, #0x4]
   62afc: 0028         	movs	r0, r5
   62afe: b280         	uxth	r0, r0
   62b00: 0a00         	lsrs	r0, r0, #0x8
   62b02: f88d 0005    	strb.w	r0, [sp, #0x5]
   62b06: 2001         	movs	r0, #0x1
   62b08: f88d 0006    	strb.w	r0, [sp, #0x6]
   62b0c: f240 6004    	movw	r0, #0x604
   62b10: f8ad 0000    	strh.w	r0, [sp]
   62b14: 4669         	mov	r1, sp
   62b16: 6960         	ldr	r0, [r4, #0x14]
   62b18: 6962         	ldr	r2, [r4, #0x14]
   62b1a: 6812         	ldr	r2, [r2]
   62b1c: 6812         	ldr	r2, [r2]
   62b1e: 4790         	blx	r2
   62b20: bd37         	pop	{r0, r1, r2, r4, r5, pc}
```

[NEW-HARD] `0x08062A90`:
- czyta `StdId` z `[r1+0]`,
- dla `0x0240 <= StdId < 0x0258` ustawia `[object+9]=1`,
- sprawdza `StdId == 0x0584`,
- wymaga `object+0x0C != 0`,
- wymaga `object+0x10 == 1`,
- wymaga `(data[3] >> 5) == 2`,
- wykonuje `BL 0x08062B22`,
- inkrementuje `[object+6]`.

### Korekta połączenia

[NEW-HARD] Raw control flow pokazuje osobno:
```text
blok z 0x08062A40 -> BL 0x08062AE4
0x08062AD8        -> BL 0x08062B22
0x08062A90        -> BL 0x08062B22
```

[REJECTED] Bezpośredni model:
```text
FUN_08063B80 -> 0x08062A40 -> 0x08062AE4 -> 0x08062B22
```
dla ścieżki `0x08062A90` jest niepoprawny.

### `0x08062AE4`

[NEW-HARD] Blok buduje ramkę z ID `0x0604` i wywołuje callback przez wskaźnik pod `object+0x14`. Nie ma bezpośredniego `BL 0x0806E59C`.

---

## 1.3 P2 — `0x08062B22`

Początek:
```text
00000000 <_binary__tmp_fw17_bin_start>:
   62b22: e92d 43f0    	push.w	{r4, r5, r6, r7, r8, r9, lr}
   62b26: b08d         	sub	sp, #0x34
   62b28: 0004         	movs	r4, r0
   62b2a: 000d         	movs	r5, r1
   62b2c: 7968         	ldrb	r0, [r5, #0x5]
   62b2e: 7929         	ldrb	r1, [r5, #0x4]
   62b30: ea51 2600    	orrs.w	r6, r1, r0, lsl #8
   62b34: 79af         	ldrb	r7, [r5, #0x6]
   62b36: b2b6         	uxth	r6, r6
   62b38: f243 7022    	movw	r0, #0x3722
   62b3c: 4286         	cmp	r6, r0
   62b3e: d004         	beq	0x62b4a <_binary__tmp_fw17_bin_start+0x62b4a> @ imm = #0x8
   62b40: b2b6         	uxth	r6, r6
   62b42: f243 7023    	movw	r0, #0x3723
   62b46: 4286         	cmp	r6, r0
   62b48: d101         	bne	0x62b4e <_binary__tmp_fw17_bin_start+0x62b4e> @ imm = #0x2
   62b4a: 2001         	movs	r0, #0x1
   62b4c: 4681         	mov	r9, r0
   62b4e: fa5f f989    	uxtb.w	r9, r9
   62b52: f1b9 0f01    	cmp.w	r9, #0x1
   62b56: f000 808c    	beq.w	0x62c72 <_binary__tmp_fw17_bin_start+0x62c72> @ imm = #0x118
   62b5a: 0032         	movs	r2, r6
   62b5c: b292         	uxth	r2, r2
   62b5e: 69a1         	ldr	r1, [r4, #0x18]
   62b60: 4668         	mov	r0, sp
   62b62: f7ae fd48    	bl	0x115f6 <_binary__tmp_fw17_bin_start+0x115f6> @ imm = #-0x51570
   62b66: e9dd 0100    	ldrd	r0, r1, [sp]
   62b6a: f7ae fa2a    	bl	0x10fc2 <_binary__tmp_fw17_bin_start+0x10fc2> @ imm = #-0x51bac
   62b6e: 4680         	mov	r8, r0
   62b70: fa5f f888    	uxtb.w	r8, r8
   62b74: f1b8 0f06    	cmp.w	r8, #0x6
   62b78: d07b         	beq	0x62c72 <_binary__tmp_fw17_bin_start+0x62c72> @ imm = #0xf6
   62b7a: b2ff         	uxtb	r7, r7
   62b7c: 2f01         	cmp	r7, #0x1
   62b7e: d178         	bne	0x62c72 <_binary__tmp_fw17_bin_start+0x62c72> @ imm = #0xf0
   62b80: fa5f f888    	uxtb.w	r8, r8
   62b84: f1b8 0f01    	cmp.w	r8, #0x1
   62b88: d009         	beq	0x62b9e <_binary__tmp_fw17_bin_start+0x62b9e> @ imm = #0x12
   62b8a: d372         	blo	0x62c72 <_binary__tmp_fw17_bin_start+0x62c72> @ imm = #0xe4
   62b8c: f1b8 0f03    	cmp.w	r8, #0x3
   62b90: d029         	beq	0x62be6 <_binary__tmp_fw17_bin_start+0x62be6> @ imm = #0x52
   62b92: d314         	blo	0x62bbe <_binary__tmp_fw17_bin_start+0x62bbe> @ imm = #0x28
   62b94: f1b8 0f05    	cmp.w	r8, #0x5
   62b98: d03e         	beq	0x62c18 <_binary__tmp_fw17_bin_start+0x62c18> @ imm = #0x7c
   62b9a: d356         	blo	0x62c4a <_binary__tmp_fw17_bin_start+0x62c4a> @ imm = #0xac
   62b9c: e069         	b	0x62c72 <_binary__tmp_fw17_bin_start+0x62c72> @ imm = #0xd2
   62b9e: 79e9         	ldrb	r1, [r5, #0x7]
   62ba0: a80a         	add	r0, sp, #0x28
   62ba2: f7b1 fdb5    	bl	0x14710 <_binary__tmp_fw17_bin_start+0x14710> @ imm = #-0x4e496
   62ba6: 2101         	movs	r1, #0x1
   62ba8: 9101         	str	r1, [sp, #0x4]
   62baa: 2100         	movs	r1, #0x0
   62bac: 9100         	str	r1, [sp]
   62bae: e9d0 2300    	ldrd	r2, r3, [r0]
   62bb2: 0031         	movs	r1, r6
   62bb4: b289         	uxth	r1, r1
   62bb6: 69a0         	ldr	r0, [r4, #0x18]
   62bb8: f7ae fe2b    	bl	0x11812 <_binary__tmp_fw17_bin_start+0x11812> @ imm = #-0x513aa
   62bbc: e059         	b	0x62c72 <_binary__tmp_fw17_bin_start+0x62c72> @ imm = #0xb2
   62bbe: 7a28         	ldrb	r0, [r5, #0x8]
   62bc0: 79e9         	ldrb	r1, [r5, #0x7]
   62bc2: ea51 2100    	orrs.w	r1, r1, r0, lsl #8
   62bc6: b289         	uxth	r1, r1
   62bc8: a808         	add	r0, sp, #0x20
   62bca: f7b1 fd9d    	bl	0x14708 <_binary__tmp_fw17_bin_start+0x14708> @ imm = #-0x4e4c6
   62bce: 2101         	movs	r1, #0x1
   62bd0: 9101         	str	r1, [sp, #0x4]
   62bd2: 2100         	movs	r1, #0x0
   62bd4: 9100         	str	r1, [sp]
   62bd6: e9d0 2300    	ldrd	r2, r3, [r0]
   62bda: 0031         	movs	r1, r6
   62bdc: b289         	uxth	r1, r1
   62bde: 69a0         	ldr	r0, [r4, #0x18]
   62be0: f7ae fe17    	bl	0x11812 <_binary__tmp_fw17_bin_start+0x11812> @ imm = #-0x513d2
   62be4: e045         	b	0x62c72 <_binary__tmp_fw17_bin_start+0x62c72> @ imm = #0x8a
   62be6: 7aa8         	ldrb	r0, [r5, #0xa]
   62be8: 7a69         	ldrb	r1, [r5, #0x9]
   62bea: 0409         	lsls	r1, r1, #0x10
   62bec: ea51 6000    	orrs.w	r0, r1, r0, lsl #24
   62bf0: 7a29         	ldrb	r1, [r5, #0x8]
   62bf2: ea50 2001    	orrs.w	r0, r0, r1, lsl #8
   62bf6: 79e9         	ldrb	r1, [r5, #0x7]
   62bf8: 4301         	orrs	r1, r0
   62bfa: a806         	add	r0, sp, #0x18
   62bfc: f7b1 fd80    	bl	0x14700 <_binary__tmp_fw17_bin_start+0x14700> @ imm = #-0x4e500
   62c00: 2101         	movs	r1, #0x1
   62c02: 9101         	str	r1, [sp, #0x4]
   62c04: 2100         	movs	r1, #0x0
   62c06: 9100         	str	r1, [sp]
   62c08: e9d0 2300    	ldrd	r2, r3, [r0]
   62c0c: 0031         	movs	r1, r6
   62c0e: b289         	uxth	r1, r1
   62c10: 69a0         	ldr	r0, [r4, #0x18]
   62c12: f7ae fdfe    	bl	0x11812 <_binary__tmp_fw17_bin_start+0x11812> @ imm = #-0x51404
   62c16: e02c         	b	0x62c72 <_binary__tmp_fw17_bin_start+0x62c72> @ imm = #0x58
   62c18: 7aa8         	ldrb	r0, [r5, #0xa]
   62c1a: 7a69         	ldrb	r1, [r5, #0x9]
   62c1c: 0409         	lsls	r1, r1, #0x10
   62c1e: ea51 6000    	orrs.w	r0, r1, r0, lsl #24
   62c22: 7a29         	ldrb	r1, [r5, #0x8]
   62c24: ea50 2001    	orrs.w	r0, r0, r1, lsl #8
   62c28: 79e9         	ldrb	r1, [r5, #0x7]
   62c2a: 4301         	orrs	r1, r0
   62c2c: a804         	add	r0, sp, #0x10
   62c2e: f7b1 fd77    	bl	0x14720 <_binary__tmp_fw17_bin_start+0x14720> @ imm = #-0x4e512
   62c32: 2101         	movs	r1, #0x1
   62c34: 9101         	str	r1, [sp, #0x4]
   62c36: 2100         	movs	r1, #0x0
   62c38: 9100         	str	r1, [sp]
   62c3a: e9d0 2300    	ldrd	r2, r3, [r0]
   62c3e: 0031         	movs	r1, r6
   62c40: b289         	uxth	r1, r1
   62c42: 69a0         	ldr	r0, [r4, #0x18]
   62c44: f7ae fde5    	bl	0x11812 <_binary__tmp_fw17_bin_start+0x11812> @ imm = #-0x51436
   62c48: e013         	b	0x62c72 <_binary__tmp_fw17_bin_start+0x62c72> @ imm = #0x26
   62c4a: 7a28         	ldrb	r0, [r5, #0x8]
   62c4c: 79e9         	ldrb	r1, [r5, #0x7]
   62c4e: ea51 2100    	orrs.w	r1, r1, r0, lsl #8
   62c52: b209         	sxth	r1, r1
   62c54: a802         	add	r0, sp, #0x8
   62c56: f7b1 fd5f    	bl	0x14718 <_binary__tmp_fw17_bin_start+0x14718> @ imm = #-0x4e542
   62c5a: 2101         	movs	r1, #0x1
   62c5c: 9101         	str	r1, [sp, #0x4]
   62c5e: 2100         	movs	r1, #0x0
   62c60: 9100         	str	r1, [sp]
   62c62: e9d0 2300    	ldrd	r2, r3, [r0]
   62c66: 0031         	movs	r1, r6
   62c68: b289         	uxth	r1, r1
   62c6a: 69a0         	ldr	r0, [r4, #0x18]
   62c6c: f7ae fdd1    	bl	0x11812 <_binary__tmp_fw17_bin_start+0x11812> @ imm = #-0x5145e
   62c70: e7ff         	b	0x62c72 <_binary__tmp_fw17_bin_start+0x62c72> @ imm = #-0x2
   62c72: b00d         	add	sp, #0x34
   62c74: e8bd 83f0    	pop.w	{r4, r5, r6, r7, r8, r9, pc}
```

[CONFIRMED-REPEAT] `0x08062B22` składa 16-bitowy indeks z `frame+4/+5`, znajduje rekord parametru, rozpoznaje typ i dekoduje wartość. Typy 1..5 są obsługiwane, a zapis kończy się w `0x08011812`.

---

# 2. RAW EXPORT — 12 rodzin handlerów `FUN_08063B80`

[NEW-HARD] Pierwszy twardy poziom mapy filtrów:

| Handler | Filtr `StdId` |
|---|---|
| `0x0800E2D2` | `base+0x180`, `base+0x280`, `base+0x380`, `base+0x480`; druga baza także `+0x180/+0x280` |
| `0x0800DFC6` | `base+0x180`, `base+0x280`, baza z `[obj+8]` |
| `0x08063E10` | `base+0x180`, `base+0x280`, baza z `[obj+0x0C]`; dalsza gałąź zakresu `0x0259..0x0383` |
| `0x08063F30` | `base+0x180`, `base+0x280`, baza z `[obj+0x11]` |
| `0x0800FEB4` | `base+0x180`, baza z `[obj+6]` |
| `0x0800FF50` | `base+0x600`, baza z `[obj+8]`; dalej `data[3]>>5` = 1/2 |
| `0x0800F894` | `0x0701..0x077F` oraz `0x0581..0x0600` |
| `0x0806369E` | `base+0x584` oraz `base+0x1EE`, baza z `[obj+0x14]` |
| `0x0800F0D0` | `base+0x180`, baza z `[obj+0x1F]`; dodatkowo `StdId==0x0288` |
| `0x08062A90` | `0x0240..0x0257` oraz `0x0584` |
| `0x08063FBA` | `base+0x180`, baza z `[obj+2]` |
| `0x08064008` | `base+0x180`, `base+0x280`, baza z `[obj+6]` |

[NEW-HARD] Dla `0x0800F894` pierwszy filtr jest absolutny i tworzy indeks:
```text
0x0701..0x077F
0x0581..0x0600
```
który następnie służy do adresowania tablicy obiektu.

[NEW-HARD] Dla `0x0806369E`, gałąź `base+0x584` dodatkowo wymaga `(data[3] >> 5)==2` oraz `data[4..5]==0x2001`.

[NEW-HARD] Dla `0x08064008`, pierwsza gałąź rozbija `data[4]` na bity:
```text
&0x03
bits 2..3
bits 4..5
bits 6..7
```

---

# 3. P3 — 23 rekordy Heating → polski `TypedText`

[NEW-HARD] Dla pola `+0x02` użyto tabeli wskaźników pod raw `0x5BD80` i translacji:
```text
file_offset = pointer - 0x08010000
```

| Heating ID | `+0x02` | Polski tekst |
|---|---:|---|
| `A9` | `0x005D` | W tym trybie temperatura zadawana jest automatycznie. |
| `AA` | `0x005E` | Paliwo |
| `BE` | `0x0061` | KOCIOŁ |
| `AD` | `0x0064` | OGRZEWANIE 2 |
| `AF` | `0x006B` | NASTAWY |
| `B0` | `0x006C` | HISTORIA ALARMÓW |
| `B1` | `0x006D` | INFO |
| `B2` | `0x006E` | KONFIGURACJA |
| `B3` | `0x0066` | OGRZEWANIE 4 |
| `B4` | `0x006F` | TEST WYJŚĆ |
| `B5` | `0x0070` | STATYSTYKI |
| `B6` | `0x0071` | PROGRAM |
| `B7` | `0x0072` | SIEĆ |
| `B8` | `0x0073` | KASKADA |
| `B9` | `0x0074` | INTERNET |
| `BB` | `0x0075` | Kocioł |
| `BC` | `0x0076` | Palnik |
| `BD` | `0x007A` | Ogrzewanie obwód 4 |
| `AE` | `0x0065` | OGRZEWANIE 3 |
| `BA` | `0x00A9` | Temperatura CO dla -10°C [°C] |
| `CC` | `0x00CB` | Wstępna dawka paliwa [g] |
| `D3` | `0x019D` | Uszkodzenie czujnika powrotu solarów |
| `D4` | `0x0106` | Napięcie gdy ruszt wysunięty [V] |

## Type=3

[NEW-HARD] Tablice zostały odczytane bezpośrednio z:
- AF: raw `0x6F5FC`, 2 × u16
- B0: raw `0x6F600`, 6 × u16
- AD: raw `0x6F61C`, 2 × u16

### AF

Raw `0x6F5FC`, values: `0x00AC`, `0x00AD`

- `0x00AC` → **Wsp. korekcji t. CO [°C/°C]**
- `0x00AD` → **MIN temperatura CO pomp [°C]**
### B0

Raw `0x6F600`, values: `0x00AF`, `0x00B0`, `0x00B1`, `0x00B3`, `0x00B4`, `0x00B5`

- `0x00AF` → **Temperatura CO zadana ręcznie [°C]**
- `0x00B0` → **Priorytet CWU   **
- `0x00B1` → **Test pompy      **
- `0x00B3` → **Stała pompa**
- `0x00B4` → **Magazyn paliwa transport(1)**
- `0x00B5` → **Magazyn paliwa podajnik(2)**
### AD

Raw `0x6F61C`, values: `0x003C`, `0x0043`

- `0x003C` → **Sterownik**
- `0x0043` → **Moc 1**

[NEW-STRONG] Wartości `type=3` są więc bezpośrednimi ID `TypedText` dla opcji listy/enum, a nie przypadkowymi wartościami.

---

# 4. XREF / CALLGRAPH

```text
FUN_08063B80
  |
  +--> 36 wywołań / 12 rodzin handlerów
  |
  +--> 0x08062A90
          |
          +--> StdId 0x0584
                 |
                 +--> data[3]>>5 == 2
                 |
                 +--> 0x08062B22
                         |
                         +--> parameter index
                         +--> type decode
                         +--> 0x08011812
```

Osobna gałąź:
```text
blok z 0x08062A40
  |
  +--> 0x08062AE4
          |
          +--> budowa ramki 0x0604
          +--> BLX callback [object+0x14]
```

TX:
```text
0x0806E59C
  |
  +--> 0x200244EC
  +--> 0x08057224
```

[NEW-HARD] Brak bezpośredniego `BL/B.W` do `0x0806E59C`.

---

# 5. INTERPRETACJA

## 5.1 TX

[NEW-STRONG] `0x0806E59C` nie jest obecnie udowodnionym centralnym TX API. Jest specjalizowanym helperem związanym z `0x0604`, ale w całym BIN nie ma bezpośredniego caller'a `BL/B.W`.

[OPEN] Następny krok: `0x08057224` i wyszukiwanie pośredniego wywołania `0x0806E59C`.

## 5.2 RX

[NEW-STRONG] `FUN_08063B80` jest fan-out dispatcherem. Semantyka ID jest rozłożona pomiędzy 12 rodzin handlerów.

## 5.3 Parametry

[NEW-HARD] `0x08062A90 -> 0x08062B22 -> 0x08011812` jest bezpośrednio potwierdzoną ścieżką zapisu parametru dla odpowiedniej gałęzi RX.

## 5.4 Heating/UI

[NEW-HARD] Wszystkie 23 pola `+0x02` mają teraz bezpośrednie mapowanie na polskie teksty firmware.

[NEW-STRONG] AD/AF/B0 mają listy ID `TypedText`, więc można przejść do konkretnego mapowania enumów/opcji UI.

---

# 6. STATUS

| Element | Status |
|---|---|
| pełne ciało `0x0806E59C` | [NEW-HARD] |
| bezpośredni caller `BL/B.W` `0x0806E59C` | [NEW-HARD] — 0 |
| `0x0806E59C` → `0x200244EC` | [CONFIRMED-REPEAT] |
| filtr `0x0604` | [NEW-HARD] |
| `0x0806E59C -> 0x08057224` | [NEW-HARD] |
| `0x08062A90` filtry | [NEW-HARD] |
| `0x08062A90 -> 0x08062B22` | [NEW-HARD] |
| `0x08062A40 -> 0x08062AE4` | [NEW-HARD] |
| `0x08062AE4` buduje `0x0604` | [NEW-HARD] |
| `63B80 -> 62A40` jako bezpośredni chain | [REJECTED] |
| 12 rodzin handlerów | [NEW-HARD] |
| pierwsza mapa filtrów CAN ID | [NEW-HARD] |
| 23 rekordy Heating → TypedText | [NEW-HARD] |
| AD/AF/B0 listy TypedText | [NEW-HARD] |
| formalne ACK/SDO/PDO semantics | [OPEN] |
| pełna ścieżka `0x08057224` | [OPEN] |
| pośredni caller `0x0806E59C` | [OPEN] |
| `0x20005EF0..0x20005F5B` | [OPEN] |

---

# 7. PRIORYTET NASTĘPNEGO PASSU

1. `0x08057224` → pełna ścieżka TX.
2. Pośrednie wywołanie / callback `0x0806E59C`.
3. Pełne porównania danych w 12 rodzinach handlerów.
4. `AD/AF/B0` → konkretne widgety i enumy.
5. Dopiero potem formalne nazwanie ACK/SDO/PDO, jeśli raw evidence to potwierdzi.

**Brak zgadywanych semantyk protokołu.**