# ETAP 8 — RECOVERED FROM GITHUB BLOB

[NEW-HARD] Blob 9620d0c85259d34bb6a20d3b03b038945dfe4c1a was fetched directly with the Git blob API. Content length: 1095461 bytes. This bypasses the empty Contents-API fetch of decompiled.c.

## ### RAW EXPORT

### FUN_080618A0
[OPEN] Function body not found by exact function-definition scan.

### FUN_08061930

int FUN_08061930(int param_1)

{
  FUN_08061942();
  *(undefined4 *)(param_1 + 0x10) = 0;
  *(undefined2 *)(param_1 + 0x14) = 0;
  return param_1;
}

### FUN_08061942

void FUN_08061942(undefined2 *param_1)

{
  *param_1 = 0;
  param_1[1] = 0;
  param_1[2] = 0;
  param_1[3] = 0;
  param_1[4] = 0;
  param_1[5] = 0;
  param_1[6] = 0;
  *(undefined1 *)(param_1 + 7) = 0;
  return;
}

### FUN_08062638

void FUN_08062638(int param_1)

{
  undefined1 *puVar1;
  byte *pbVar2;
  char *pcVar3;
  byte bVar4;
  uint uVar5;
  undefined4 uVar6;
  undefined4 *puVar7;
  int iVar8;
  uint *puVar9;
  longlong lVar10;
  undefined4 local_d0;
  undefined4 uStack_cc;
  undefined4 local_c8;
  undefined4 uStack_c4;
  undefined4 local_c0;
  uint local_bc;
  uint local_b8;
  uint local_b4;
  uint local_b0;
  uint local_ac;
  int local_a8;
  int local_a4;
  undefined4 local_9c;
  undefined4 local_90;
  undefined4 uStack_8c;
  undefined1 auStack_88 [8];
  undefined4 local_80;
  undefined4 uStack_7c;
  undefined1 auStack_78 [8];
  undefined4 local_70;
  undefined4 uStack_6c;
  undefined1 auStack_68 [8];
  undefined4 local_60;
  undefined4 uStack_5c;
  undefined1 auStack_58 [8];
  undefined4 local_50;
  undefined4 uStack_4c;
  undefined1 auStack_48 [8];
  undefined4 local_40;
  undefined4 uStack_3c;
  undefined1 auStack_38 [8];
  undefined4 local_30;
  undefined4 uStack_2c;
  undefined1 auStack_28 [8];
  undefined4 local_20;
  undefined4 uStack_1c;
  undefined1 auStack_18 [8];
  
  puVar9 = (uint *)(param_1 + 8);
  bVar4 = *(char *)(param_1 + 0x14) + 1;
  *(byte *)(param_1 + 0x14) = bVar4;
  if (bVar4 < 10) {
    return;
  }
  *(undefined1 *)(param_1 + 0x14) = 0;
  *puVar9 = 0;
  uVar6 = DAT_08062908;
  FUN_080115f6(&local_d0,DAT_08062908,0x2299);
  local_20 = local_d0;
  uStack_1c = uStack_cc;
  FUN_08014728(auStack_18,&local_20,5);
  uVar5 = FUN_08014734(auStack_18);
  *puVar9 = uVar5 & 1 | *puVar9;
  FUN_080115f6(&local_d0,uVar6,0x229a);
  local_30 = local_d0;
  uStack_2c = uStack_cc;
  FUN_08014728(auStack_28,&local_30,5);
  uVar5 = FUN_08014734(auStack_28);
  *puVar9 = (uVar5 & 1) << 1 | *puVar9;
  FUN_080115f6(&local_d0,uVar6,0x229b);
  local_40 = local_d0;
  uStack_3c = uStack_cc;
  FUN_08014728(auStack_38,&local_40,5);
  uVar5 = FUN_08014734(auStack_38);
  *puVar9 = (uVar5 & 1) << 2 | *puVar9;
  FUN_080115f6(&local_d0,uVar6,0x229c);
  local_50 = local_d0;
  uStack_4c = uStack_cc;
  FUN_08014728(auStack_48,&local_50,5);
  uVar5 = FUN_08014734(auStack_48);
  *puVar9 = (uVar5 & 1) << 3 | *puVar9;
  FUN_080115f6(&local_d0,uVar6,0x311c);
  local_60 = local_d0;
  uStack_5c = uStack_cc;
  FUN_08014728(auStack_58,&local_60,5);
  uVar5 = FUN_08014734(auStack_58);
  *puVar9 = (uVar5 & 1) << 0x12 | *puVar9;
  FUN_080115f6(&local_d0,uVar6,0x2277);
  local_70 = local_d0;
  uStack_6c = uStack_cc;
  FUN_08014728(auStack_68,&local_70,5);
  uVar5 = FUN_08014734(auStack_68);
  *puVar9 = (uVar5 & 1) << 0x13 | *puVar9;
  FUN_080115f6(&local_d0,uVar6,0x2278);
  local_80 = local_d0;
  uStack_7c = uStack_cc;
  FUN_08014728(auStack_78,&local_80,5);
  uVar5 = FUN_08014734(auStack_78);
  *puVar9 = (uVar5 & 1) << 0x10 | *puVar9;
  if (*(int *)(param_1 + 0x10) != *(int *)(param_1 + 0xc)) {
    FUN_080115f6(&local_d0,uVar6,0x372f);
    local_90 = local_d0;
    uStack_8c = uStack_cc;
    FUN_08014728(auStack_88,&local_90,5);
    lVar10 = FUN_08014734(auStack_88);
    if (lVar10 != 0) {
      local_d0 = *(undefined4 *)(param_1 + 0xc);
      uStack_cc = 0;
      puVar7 = (undefined4 *)FUN_08039370(&local_d0);
      *(char *)(param_1 + 0x20) = (char)puVar7[2];
      *(char *)(param_1 + 0x1f) = (char)puVar7[1];
      *(char *)(param_1 + 0x1e) = (char)*puVar7;
      *(short *)(param_1 + 0x26) = (short)puVar7[5] + 0x76c;
      *(char *)(param_1 + 0x24) = (char)puVar7[4] + '\x01';
      *(char *)(param_1 + 0x22) = (char)puVar7[6] + -1;
      *(char *)(param_1 + 0x23) = (char)puVar7[3];
      local_c0 = CONCAT31(CONCAT21(CONCAT11(local_c0._3_1_,*(undefined1 *)(param_1 + 0x1e)),
                                   *(undefined1 *)(param_1 + 0x1f)),*(undefined1 *)(param_1 + 0x20))
      ;
      FUN_08018e94(0,&local_c0);
      FUN_08015260(&local_c8,param_1 + 0x22,6);
      FUN_08039324(local_c8,uStack_c4);
      goto LAB_080628fe;
    }
  }
  puVar1 = DAT_0806290c;
  FUN_08018f18(0,DAT_0806290c);
  puVar7 = DAT_08062910;
  *(undefined1 *)DAT_08062910 = puVar1[2];
  *(undefined1 *)((int)puVar7 + 1) = puVar1[1];
  pbVar2 = DAT_08062914;
  *(undefined1 *)((int)puVar7 + 2) = *puVar1;
  local_c0 = *puVar7;
  FUN_08039250(param_1 + 0x15,&local_c0);
  FUN_08018ff8(0,pbVar2);
  pcVar3 = DAT_0806291c;
  bVar4 = *pbVar2;
  iVar8 = (int)((ulonglong)((longlong)(int)(uint)bVar4 * (longlong)DAT_08062918) >> 0x20) +
          (uint)bVar4;
  *DAT_0806291c = bVar4 + ((char)(iVar8 >> 2) - (char)(iVar8 >> 0x1f)) * -7;
  pcVar3[1] = pbVar2[2];
  pcVar3[2] = pbVar2[1];
  *(ushort *)(pcVar3 + 4) = pbVar2[3] + 2000;
  local_c8 = *(undefined4 *)pcVar3;
  uStack_c4 = *(undefined4 *)(pcVar3 + 4);
  FUN_0803925e(param_1 + 0x18,&local_c8);
  local_b4 = (uint)*(byte *)(param_1 + 0x17);
  local_b8 = (uint)*(byte *)(param_1 + 0x16);
  local_bc = (uint)*(byte *)(param_1 + 0x15);
  local_a8 = *(ushort *)(param_1 + 0x1c) - 0x76c;
  local_ac = (*(byte *)(param_1 + 0x1a) + 0xb) % 0xc;
  local_b0 = (uint)*(byte *)(param_1 + 0x19);
  local_a4 = *(byte *)(param_1 + 0x18) + 1;
  local_a4 = local_a4 + (local_a4 * 0x9249 + 0x9249U >> 0x12) * -7;
  local_9c = 0xffffffff;
  uVar6 = FUN_08062920(&local_bc);
  *(undefined4 *)(param_1 + 0xc) = uVar6;
LAB_080628fe:
  *(undefined4 *)(param_1 + 0x10) = *(undefined4 *)(param_1 + 0xc);
  return;
}

### FUN_08062920

longlong FUN_08062920(int *param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  longlong lVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  
  iVar5 = param_1[4] / 0xc;
  iVar3 = param_1[4] % 0xc;
  if (iVar3 < 0) {
    iVar3 = iVar3 + 0xc;
    iVar5 = iVar5 + -1;
  }
  if (iVar5 < 0) {
    iVar4 = -0x80000000 - iVar5;
    if (param_1[5] < -0x80000000 - iVar5) {
      return -1;
    }
  }
  else {
    iVar4 = param_4;
    if ((0 < iVar5) && (iVar4 = param_1[5], 0x7fffffff - iVar5 < iVar4)) {
      return -1;
    }
  }
  iVar2 = param_1[5];
  iVar3 = FUN_0803bbf4(iVar5 + iVar2,iVar3,iVar5,iVar4,param_4);
  iVar7 = *param_1 / DAT_080629f4;
  iVar4 = *param_1 + (param_1[2] % 0x18) * 0xe10 + (param_1[1] % 0x5a0) * 0x3c;
  lVar1 = (longlong)DAT_080629f4 *
          (longlong)
          (DAT_080629f8 +
          param_1[1] / 0x5a0 + param_1[2] / 0x18 + param_1[3] + (iVar5 + iVar2) * 0x16d + iVar3 +
          iVar7) + (longlong)(iVar4 - DAT_080629f4 * iVar7);
  uVar6 = (uint)lVar1;
  iVar3 = (int)((ulonglong)lVar1 >> 0x20);
  FUN_0803bc3c(param_1,iVar4,uVar6,iVar3,param_1[8]);
  if (0 < param_1[8]) {
    lVar1 = CONCAT44(iVar3 - (uint)(uVar6 < 0xe10),uVar6 - 0xe10);
  }
  iVar3 = FUN_0803bb58();
  return lVar1 - iVar3;
}

### FUN_08062D82
[OPEN] Function body not found by exact function-definition scan.

### FUN_08062F18
[OPEN] Function body not found by exact function-definition scan.

### FUN_0804E4F8
[OPEN] Function body not found by exact function-definition scan.

### FUN_0804E598
[OPEN] Function body not found by exact function-definition scan.

### FUN_0804E5BC
[OPEN] Function body not found by exact function-definition scan.

### FUN_0804E740
[OPEN] Function body not found by exact function-definition scan.

### FUN_0804E75A
[OPEN] Function body not found by exact function-definition scan.

### FUN_08032316

undefined8 FUN_08032316(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 local_10;
  undefined4 uStack_c;
  
  local_10 = param_3;
  uStack_c = param_4;
  FUN_08015260(&local_10,param_1 + 1,8);
  local_10 = 0;
  (**(code **)(*param_1 + 0x10))(param_1,&local_10);
  return CONCAT44(uStack_c,local_10);
}

## ### XREF / CALLGRAPH

- FUN_080618A0: 0 textual occurrence(s) in recovered decompiled blob.
- FUN_08061930: 2 textual occurrence(s) in recovered decompiled blob.
- FUN_08061942: 2 textual occurrence(s) in recovered decompiled blob.
- FUN_08062638: 1 textual occurrence(s) in recovered decompiled blob.
- FUN_08062920: 2 textual occurrence(s) in recovered decompiled blob.
- FUN_08062D82: 0 textual occurrence(s) in recovered decompiled blob.
- FUN_08062F18: 0 textual occurrence(s) in recovered decompiled blob.
- FUN_0804E4F8: 0 textual occurrence(s) in recovered decompiled blob.
- FUN_0804E598: 0 textual occurrence(s) in recovered decompiled blob.
- FUN_0804E5BC: 0 textual occurrence(s) in recovered decompiled blob.
- FUN_0804E740: 0 textual occurrence(s) in recovered decompiled blob.
- FUN_0804E75A: 0 textual occurrence(s) in recovered decompiled blob.
- FUN_08032316: 101 textual occurrence(s) in recovered decompiled blob.
- CanTxTask: 1 occurrence(s).
- CanRxTask: 1 occurrence(s).
- CanMessagesToTransmit: 0 occurrence(s).
- DAT_0803C218: 0 occurrence(s).
- DAT_08038694: 1 occurrence(s).
- DAT_08038698: 1 occurrence(s).
- DAT_0803869C: 0 occurrence(s).
- 0x20005EF0: 0 occurrence(s).

## ### INTERPRETACJA

[NEW-HARD] The complete decompiled.c content is recoverable from blob SHA 9620d0c85259d34bb6a20d3b03b038945dfe4c1a; the blocker was the repository Contents fetch path, not loss of the blob.
[OPEN] Literal Thumb HEX still requires the original BIN bytes; the recovered C is decompilation, not raw machine code.
[OPEN] 108-byte runtime SRAM cannot be recovered from static decompiled C alone unless the initializer/source writes are present and fully identified.
[OPEN] Literal vtable bytes require memory/BIN export unless represented explicitly in the decompiled blob.

## ### STATUS
| Element | Status |
|---|---|
| Full decompiled.c blob recovered | [NEW-HARD] |
| CAN TX function bodies | [NEW-HARD]/see RAW EXPORT |
| UI helper bodies | [NEW-HARD]/see RAW EXPORT |
| Xref occurrence scan | [NEW-HARD] |
| Thumb HEX | [OPEN] |
| SRAM 0x20005EF0..0x20005F5B | [OPEN] |
| Vtable 0x08038694..0x080386C7 literal bytes | [OPEN] |
