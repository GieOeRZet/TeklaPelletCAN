# MULTIPASS-23 — IAR LZ77 + 0x47/0x48 CLOSURE; FUN_080480C0 + TYPEDTEXT TABLE RAW
Data: 2026-11-20
Firmware: FW2213TK_kopia.bin
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

## 1. Closed IAR/startup chain

- 0x94644 = __iar_program_start
- 0x8B4A8 = __iar_init_vfp
- 0x8F74C = __cmain
- 0x89440 = __iar_data_init3
- 0x6E68C = __iar_lz77_init3
- 0x784F4 = __iar_zero_init3

IAR data-init record 2:
- record address: 0x8B4E0
- source file offset: 0x96114
- source span requested: 0x96114..0x9694E
- destination: 0x20000000
- reconstructed output: 0x118B3 bytes / 71859 bytes
- reconstructed target list block: 0x20011534..0x20011669, 310 bytes.

## 2. Closed 0x47 / 0x48 branch

- 0x0047 = graph family A, parameters 0x2261..0x2265
- 0x0047 is case 10 (Palnik)
- gate: context + 0x158 != 0
- list location: 0x200115D0, first element of 19-element list

- 0x0048 = graph family B, parameters 0x2268, 0x226E, 0x226F, 0x2275, 0x227A
- 0x0048 is case 0 (Kocioł), NOT case 10
- gate: context + 0x158 != 0
- list location: 0x200115B0, first element of 10-element list

- case 0x10 = Konfiguracja, including 0x10D..0x116 family
- case 0x11 = Statystyki/Info, 0x19A..0x1A7 family

## 3. Requested raw Thumb disassembly: FUN_080480C0

Command:
llvm-objdump -D --triple=thumbv7m --start-address=0x480c0 --stop-address=0x48422

Raw output:

480c0: e92d 4ffe       push.w {r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, lr}
480c4: 4605            mov r5, r0
480c6: f248 40ec       movw r0, #0x84ec
480ca: 4428            add r0, r5
480cc: 4692            mov r10, r2
480ce: 6041            str r1, [r0, #0x4]
480d0: f44f 706e       mov.w r0, #0x3b8
480d4: eb05 0b00       add.w r11, r5, r0
480d8: f89d 0008       ldrb.w r0, [sp, #0x8]
480dc: f89d 1030       ldrb.w r1, [sp, #0x30]
480e0: f20f 5688       adr.w r6, #1416
480e4: 4450            add r0, r10
480e6: 1808            adds r0, r1, r0
480e8: f205 442c       addw r4, r5, #0x42c
480ec: f88b 0000       strb.w r0, [r11]
480f0: f04f 0800       mov.w r8, #0x0
480f4: 46a1            mov r9, r4
480f6: e00d            b 0x48114
480f8: 89ba            ldrh r2, [r7, #0xc]
480fa: 68b9            ldr r1, [r7, #0x8]
480fc: 4648            mov r0, r9
480fe: f006 fb1f       bl 0x4e740
48102: 210a            movs r1, #0xa
48104: 4648            mov r0, r9
48106: f006 fa59       bl 0x4e5bc
4810a: f44f 704e       mov.w r0, #0x338
4810e: f108 0801       add.w r8, r8, #0x1
48112: 4481            add r9, r0
48114: f89b 0000       ldrb.w r0, [r11]
48118: 4580            cmp r8, r0
4811a: da47            bge 0x481ac
4811c: f248 42ec       movw r2, #0x84ec
48120: 442a            add r2, r5
48122: 2000            movs r0, #0x0
48124: 6852            ldr r2, [r2, #0x4]
48126: 4631            mov r1, r6
48128: f932 3018       ldrsh.w r3, [r2, r8, lsl #1]
4812c: f9b1 7000       ldrsh.w r7, [r1]
48130: 42bb            cmp r3, r7
48132: bf1e            ittt ne
48134: 1c40            addne r0, r0, #0x1
48136: f9b1 7010       ldrshne.w r7, [r1, #0x10]
4813a: 42bb            cmpne r3, r7
4813c: bf1e            ittt ne
4813e: 1c40            addne r0, r0, #0x1
48140: f9b1 7020       ldrshne.w r7, [r1, #0x20]
48144: 42bb            cmp r3, r7
48146: d008            beq 0x4815a
48148: f9b1 7030       ldrsh.w r7, [r1, #0x30]
4814c: 1c40            adds r0, r0, #0x1
4814e: 42bb            cmp r3, r7
48150: d003            beq 0x4815a
48152: 1c40            adds r0, r0, #0x1
48154: 3140            adds r1, #0x40
48156: 28bc            cmp r0, #0xbc
48158: dbe6            blt 0x48128
4815a: 28bc            cmp r0, #0xbc
4815c: bf08            it eq
4815e: 2000            moveq r0, #0x0
48160: eb06 1700       add.w r7, r6, r0, lsl #4
48164: 88ba            ldrh r2, [r7, #0x4]
48166: f9b7 1002       ldrsh.w r1, [r7, #0x2]
4816a: 2300            movs r3, #0x0
4816c: 4648            mov r0, r9
4816e: f006 f9c3       bl 0x4e4f8
48172: 79f8            ldrb r0, [r7, #0x7]
48174: f8a9 0334       strh.w r0, [r9, #0x334]
48178: 79b8            ldrb r0, [r7, #0x6]
4817a: 2801            cmp r0, #0x1
4817c: d006            beq 0x4818c
4817e: 2802            cmp r0, #0x2
48180: d0ba            beq 0x480f8
48182: 2803            cmp r0, #0x3
48184: d00c            beq 0x481a0
48186: 2805            cmp r0, #0x5
48188: d0b6            beq 0x480f8
4818a: e7ba            b 0x48102
4818c: 2101            movs r1, #0x1
4818e: 4648            mov r0, r9
48190: f006 fa02       bl 0x4e598
48194: f24a 60dc       movw r0, #0xa6dc
48198: 4428            add r0, r5
4819a: f8c9 0270       str.w r0, [r9, #0x270]
4819e: e7b0            b 0x48102
481a0: 89ba            ldrh r2, [r7, #0xc]
481a2: 68b9            ldr r1, [r7, #0x8]
481a4: 4648            mov r0, r9
481a6: f006 fad8       bl 0x4e75a
481aa: e7aa            b 0x48102
481ac: f248 40ec       movw r0, #0x84ec
481b0: f04f 0900       mov.w r9, #0x0
481b4: 502c            str r4, [r5, r0]
481b6: f44f 7061       mov.w r0, #0x384
481ba: 4428            add r0, r5
481bc: 6304            str r4, [r0, #0x30]
481be: 4628            mov r0, r5
481c0: f006 faf0       bl 0x4e7a4
481c4: 2014            movs r0, #0x14
481c6: f8ab 003e       strh.w r0, [r11, #0x3e]
481ca: f44f 7060       mov.w r0, #0x380
481ce: eb05 0800       add.w r8, r5, r0
481d2: f44f 707b       mov.w r0, #0x3ec
481d6: 1829            adds r1, r5, r0
481d8: 4640            mov r0, r8
481da: f002 f944       bl 0x4a466
481de: ea5f 000a       movs.w r0, r10
481e2: d00f            beq 0x48204
481e4: f24a 60bc       movw r0, #0xa6bc
481e8: 182f            adds r7, r5, r0
481ea: f8c4 726c       str.w r7, [r4, #0x26c]
481ee: 4621            mov r1, r4
481f0: 4640            mov r0, r8
481f2: f002 f938       bl 0x4a466
481f6: f109 0901       add.w r9, r9, #0x1
481fa: f44f 704e       mov.w r0, #0x338
481fe: 45d1            cmp r9, r10
48200: 4404            add r4, r0
48202: dbf2            blt 0x481ea
48204: f89d 0008       ldrb.w r0, [sp, #0x8]
48208: 2800            cmp r0, #0x0
4820a: d04f            beq 0x482ac
4820c: f24a 6004       movw r0, #0xa604
48210: 182e            adds r6, r5, r0
48212: 2032            movs r0, #0x32
48214: 8070            strh r0, [r6, #0x2]
48216: a901            add r1, sp, #0x4
48218: f44f 70f0       mov.w r0, #0x1e0
4821c: 8030            strh r0, [r6]
4821e: 205b            movs r0, #0x5b
48220: f8ad 0004       strh.w r0, [sp, #0x4]
48224: f24a 6054       movw r0, #0xa654
48228: 182c            adds r4, r5, r0
4822a: 4620            mov r0, r4
4822c: f7e8 fac6       bl 0x307bc
48230: f9b6 7002       ldrsh.w r7, [r6, #0x2]
48234: f8b6 005a       ldrh.w r0, [r6, #0x5a]
48238: f8ad 0000       strh.w r0, [sp]
4823c: f9b6 1058       ldrsh.w r1, [r6, #0x58]
48240: f9b6 0000       ldrsh.w r0, [r6]
48244: 6d32            ldr r2, [r6, #0x50]
48246: 6ad2            ldr r2, [r2, #0x2c]
48248: 1a40            subs r0, r0, r1
4824a: eb00 70d0       add.w r0, r0, r0, lsr #31
4824e: 1040            asrs r0, r0, #0x1
48250: f1a0 0114       sub.w r1, r0, #0x14
48254: b209            sxth r1, r1
48256: 4620            mov r0, r4
48258: 4790            blx r2
4825a: f9bd 0000       ldrsh.w r0, [sp]
4825e: 6d32            ldr r2, [r6, #0x50]
48260: 6b12            ldr r2, [r2, #0x30]
48262: 1a38            subs r0, r7, r0
48264: eb00 70d0       add.w r0, r0, r0, lsr #31
48268: 1040            asrs r0, r0, #0x1
4826a: 1f41            subs r1, r0, #0x5
4826c: b209            sxth r1, r1
4826e: 4620            mov r0, r4
48270: 4790            blx r2
48272: f24a 50fc       movw r0, #0xa5fc
48276: 182e            adds r6, r5, r0
48278: 4621            mov r1, r4
4827a: 4630            mov r0, r6
4827c: f7e8 f880       bl 0x30380
48280: 4631            mov r1, r6
48282: 4640            mov r0, r8
48284: f002 f8ef       bl 0x4a466
48288: e010            b 0x482ac
4828a: f44f 704e       mov.w r0, #0x338
4828e: fb00 f009       mul r0, r0, r9
48292: 4428            add r0, r5
48294: f24a 61bc       movw r1, #0xa6bc
48298: 4429            add r1, r5
4829a: f8c0 1698       str.w r1, [r0, #0x698]
4829e: f109 0901       add.w r9, r9, #0x1
482a2: f200 412c       addw r1, r0, #0x42c
482a6: 4640            mov r0, r8
482a8: f002 f8dd       bl 0x4a466
482ac: f89d 0008       ldrb.w r0, [sp, #0x8]
482b0: eb0a 0400       add.w r4, r10, r0
482b4: 45a1            cmp r9, r4
482b6: dbe8            blt 0x4828a
482b8: f89d 0030       ldrb.w r0, [sp, #0x30]
482bc: 2800            cmp r0, #0x0
482be: d052            beq 0x48366
482c0: f24a 6004       movw r0, #0xa604
482c4: 182e            adds r6, r5, r0
482c6: 2032            movs r0, #0x32
482c8: 85f0            strh r0, [r6, #0x2e]
482ca: a901            add r1, sp, #0x4
482cc: f44f 70f0       mov.w r0, #0x1e0
482d0: 85b0            strh r0, [r6, #0x2c]
482d2: 205c            movs r0, #0x5c
482d4: f8ad 0004       strh.w r0, [sp, #0x4]
482d8: f24a 6080       movw r0, #0xa680
482dc: eb05 0a00       add.w r10, r5, r0
482e0: 4650            mov r0, r10
482e2: f7e8 fa6b       bl 0x307bc
482e6: f24a 6088       movw r0, #0xa688
482ea: 4428            add r0, r5
482ec: f9b6 702e       ldrsh.w r7, [r6, #0x2e]
482f0: 8841            ldrh r1, [r0, #0x2]
482f2: f8ad 1000       strh.w r1, [sp]
482f6: f9b0 0000       ldrsh.w r0, [r0]
482fa: f9b6 102c       ldrsh.w r1, [r6, #0x2c]
482fe: 6ff2            ldr r2, [r6, #0x7c]
48300: 6ad2            ldr r2, [r2, #0x2c]
48302: 1a08            subs r0, r1, r0
48304: eb00 70d0       add.w r0, r0, r0, lsr #31
48308: 1040            asrs r0, r0, #0x1
4830a: f1a0 0114       sub.w r1, r0, #0x14
4830e: b209            sxth r1, r1
48310: 4650            mov r0, r10
48312: 4790            blx r2
48314: f9bd 0000       ldrsh.w r0, [sp]
48318: 6ff2            ldr r2, [r6, #0x7c]
4831a: 6b12            ldr r2, [r2, #0x30]
4831c: 1a38            subs r0, r7, r0
4831e: eb00 70d0       add.w r0, r0, r0, lsr #31
48322: 1040            asrs r0, r0, #0x1
48324: 1f41            subs r1, r0, #0x5
48326: b209            sxth r1, r1
48328: 4650            mov r0, r10
4832a: 4790            blx r2
4832c: f24a 6028       movw r0, #0xa628
48330: 182e            adds r6, r5, r0
48332: 4651            mov r1, r10
48334: 4630            mov r0, r6
48336: f7e8 f823       bl 0x30380
4833a: 4631            mov r1, r6
4833c: 4640            mov r0, r8
4833e: f002 f892       bl 0x4a466
48342: e010            b 0x48366
48344: f44f 704e       mov.w r0, #0x338
48348: fb00 f009       mul r0, r0, r9
4834c: 4428            add r0, r5
4834e: f24a 61bc       movw r1, #0xa6bc
48352: 4429            add r1, r5
48354: f8c0 1698       str.w r1, [r0, #0x698]
48358: f109 0901       add.w r9, r9, #0x1
4835c: f200 412c       addw r1, r0, #0x42c
48360: 4640            mov r0, r8
48362: f002 f880       bl 0x4a466
48366: f89d 0030       ldrb.w r0, [sp, #0x30]
4836a: 1820            adds r0, r4, r0
4836c: 4581            cmp r9, r0
4836e: dbe9            blt 0x48344
48370: 2014            movs r0, #0x14
48372: f8ab 000e       strh.w r0, [r11, #0xe]
48376: f44f 706f       mov.w r0, #0x3bc
4837a: 1829            adds r1, r5, r0
4837c: 4640            mov r0, r8
4837e: f002 f872       bl 0x4a466
48382: 2014            movs r0, #0x14
48384: f8a5 0384       strh.w r0, [r5, #0x384]
48388: 4641            mov r1, r8
4838a: f44f 7030       mov.w r0, #0x2c0
4838e: 182c            adds r4, r5, r0
48390: 4620            mov r0, r4
48392: f001 fcec       bl 0x49d6e
48396: 6822            ldr r2, [r4]
48398: 6ad2            ldr r2, [r2, #0x2c]
4839a: 2100            movs r1, #0x0
4839c: 4620            mov r0, r4
4839e: 4790            blx r2
483a0: 6822            ldr r2, [r4]
483a2: 6b12            ldr r2, [r2, #0x30]
483a4: 211e            movs r1, #0x1e
483a6: 4620            mov r0, r4
483a8: 4790            blx r2
483aa: 481e            ldr r0, [pc, #0x78]
483ac: 88a1            ldrh r1, [r4, #0x4]
483ae: f9b0 0000       ldrsh.w r0, [r0]
483b2: 1a40            subs r0, r0, r1
483b4: 8120            strh r0, [r4, #0x8]
483b6: 481c            ldr r0, [pc, #0x70]
483b8: 88e1            ldrh r1, [r4, #0x6]
483ba: f9b0 0000       ldrsh.w r0, [r0]
483be: 1a40            subs r0, r0, r1
483c0: 1f40            subs r0, r0, #0x5
483c2: 8160            strh r0, [r4, #0xa]
483c4: 2102            movs r1, #0x2
483c6: 4620            mov r0, r4
483c8: f001 fe61       bl 0x4a08e
483cc: 2106            movs r1, #0x6
483ce: 4620            mov r0, r4
483d0: f001 fe5a       bl 0x4a088
483d4: 4621            mov r1, r4
483d6: 1d28            adds r0, r5, #0x4
483d8: f7e7 ffd2       bl 0x30380
483dc: f7e9 f86d       bl 0x314ba
483e0: f7ef fd37       bl 0x37e52
483e4: b202            sxth r2, r0
483e6: 2100            movs r1, #0x0
483e8: 4620            mov r0, r4
483ea: f001 fc35       bl 0x49c58
483ee: 4628            mov r0, r5
483f0: f006 faf4       bl 0x4e9dc
483f4: f648 7195       movw r1, #0x8f95
483f8: 2000            movs r0, #0x0
483fa: 5468            strb r0, [r5, r1]
483fc: f249 3101       movw r1, #0x9301
48400: 5468            strb r0, [r5, r1]
48402: f248 40f4       movw r0, #0x84f4
48406: 182c            adds r4, r5, r0
48408: f24a 60cc       movw r0, #0xa6cc
4840c: 1829            adds r1, r5, r0
4840e: 4620            mov r0, r4
48410: f7e6 fac5       bl 0x2e99e
48414: 4621            mov r1, r4
48416: 1d28            adds r0, r5, #0x4
48418: f7e7 ffb2       bl 0x30380
4841c: b003            add sp, #0xc
4841e: e8bd 8ff0       pop.w {r4, r5, r6, r7, r8, r9, r10, r11, pc}

## 4. Requested raw hex: 0x7F58C..0x7F5EB (96 bytes)

Offset 0x7F58C:
CD 60 0A 08 ED 60 0A 08 00 00 00 00 00 00 00 00
BB D8 05 08 00 00 00 00 33 3A 04 08 0D F5 05 08
EB 60 0A 08 7F 44 08 08 73 3C 04 08 3B 3E 04 08
39 3F 04 08 61 ED 07 08 ED 60 0A 08 00 00 00 00
00 00 00 00 55 F6 07 08 00 00 00 00 33 3A 04 08
DD 3D 05 08 EB 60 0A 08 D1 44 05 08 73 3C 04 08

## 5. Exact byte span

Start: 0x7F58C
Length: 0x60 = 96 bytes
End-exclusive: 0x7F5EC
Last byte: 0x7F5EB
