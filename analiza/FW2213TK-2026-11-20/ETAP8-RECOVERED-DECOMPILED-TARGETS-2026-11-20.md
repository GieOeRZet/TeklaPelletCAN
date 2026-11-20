# TEKLAPELLET-CAN — ETAP 8 — RECOVERED DECOMPILED TARGETS

[NEW-HARD] Direct Git blob retrieval recovered the complete decompiled.c content: 1095461 bytes, SHA 9620d0c85259d34bb6a20d3b03b038945dfe4c1a. This bypasses the empty repository Contents API result.

## ### RAW EXPORT

### FUN_080618A0


FUN_080618a0(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,uint param_5,
            uint param_6)

{
  undefined2 *puVar1;
  undefined2 *puVar2;
  undefined1 *puVar3;
  
  *(undefined4 *)(param_1 + 0x10) = 0;
  *(undefined4 *)(param_1 + 0x14) = 0;
  *(undefined4 *)(param_1 + 4) = param_2;
  *(undefined4 *)(param_1 + 8) = param_3;
  *(undefined4 *)(param_1 + 0xc) = param_4;
  FUN_08061930(param_1 + 0x18);
  *(undefined4 *)(param_1 + 0x34) = 0;
  *(undefined4 *)(param_1 + 0x38) = 0;
  *(undefined4 *)(param_1 + 0x3c) = 0;
  *(undefined1 *)(param_1 + 0x40) = 1;
  *(undefined1 *)(param_1 + 0x41) = 1;
  puVar3 = DAT_08061920;
  puVar2 = DAT_0806191c;
  puVar1 = DAT_08061918;
  *(undefined1 *)(param_1 + 0x50) = 1;
  *(undefined1 *)(param_1 + 0x51) = 0;
  *(undefined1 *)(param_1 + 0x52) = 0;
  *(undefined1 *)(param_1 + 0x53) = 1;
  *(undefined1 *)(param_1 + 0x54) = 0;
  *(undefined1 *)(param_1 + 0x55) = 0;
  *(undefined1 *)(param_1 + 0x56) = 0;
  *(undefined1 *)(param_1 + 0x57) = 0;
  *(undefined1 *)(param_1 + 0x58) = 0;
  *(undefined4 *)(param_1 + 0x5c) = 0;
  *(undefined1 *)(param_1 + 0x61) = 0;
  *DAT_08061924 = param_1;
  *puVar1 = (short)param_5;
  *puVar2 = (short)param_6;
  *puVar3 = 0;
  puVar1 = DAT_0806192c;
  *DAT_08061928 = (short)param_5;
  *puVar1 = (short)param_6;
  *(byte *)(param_1 + 0x30) = (byte)(-(uint)(param_5 < param_6) >> 0x1f);
  return CONCAT44(param_4,param_1);
}

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


void FUN_08062d82(void)

{
  int *piVar1;
  undefined4 uVar2;
  byte *pbVar3;
  undefined2 uVar4;
  int *piVar5;
  int iVar6;
  
  FUN_08018a66(0x1000,1);
  FUN_080632c8();
  piVar1 = DAT_08062e78;
  iVar6 = 0x1f000;
  piVar5 = DAT_08062e9c;
  do {
    *piVar1 = *piVar5;
    *piVar1 = piVar5[1];
    *piVar1 = piVar5[2];
    *piVar1 = piVar5[3];
    uVar2 = DAT_08062e84;
    piVar5 = piVar5 + 4;
    iVar6 = iVar6 + -1;
  } while (iVar6 != 0);
  iVar6 = *piVar1;
  FUN_08018a66(0x1000);
  pbVar3 = DAT_08062ea0;
  *DAT_08062ea0 = (byte)(-(uint)(iVar6 == 0) >> 0x1f);
  uVar4 = FUN_080632d4();
  *(undefined2 *)(pbVar3 + 2) = uVar4;
  FUN_08000e34();
  FUN_0805fd78();
  FUN_0805fd2a();
  if (*DAT_08062e80 == '\0') {
    *DAT_08062e80 = '\x01';
    FUN_08063096(uVar2);
  }
  FUN_0806318a(uVar2);
  *DAT_08062ea4 = pbVar3 + 4;
  *DAT_08062ea8 = 0xe10;
  FUN_08057630(DAT_08062eac,s_GUITask_08062ebc,2000,0,2,0,0,0);
  FUN_08057630(DAT_08062eb0,s_EstymaTask_08062ec4,0x3b6,0,3,0,0,0);
  FUN_08057630(DAT_08062eb4,s_CanRxTask_08062ed0,100,0,2,0,0,0);
  FUN_08057630(DAT_08062eb8,s_CanTxTask_08062edc,100,0,2,0,0,0);
  FUN_0805785a();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

### FUN_08062F18


undefined4 FUN_08062f18(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  char cVar2;
  undefined1 uVar3;
  ushort uVar4;
  uint uVar5;
  int iVar6;
  ushort *puVar7;
  int iVar8;
  
  iVar1 = DAT_08063068;
  puVar7 = (ushort *)(param_1 + 0xe);
  iVar8 = 3;
  do {
    switch((char)puVar7[-2]) {
    case '\0':
      uVar5 = (uint)(byte)puVar7[-3];
      if (uVar5 < 3) {
        uVar3 = 0;
LAB_0806304c:
        iVar6 = param_1 + uVar5 * 10;
        *(undefined1 *)(iVar6 + 9) = uVar3;
        FUN_08060ac4(*(undefined1 *)(iVar6 + 8),uVar3,*(undefined1 *)(iVar6 + 0xd));
      }
      break;
    case '\x01':
      uVar4 = *puVar7;
      *puVar7 = uVar4 + 1;
      if (0x14 / param_2 <= (int)(uint)(ushort)(uVar4 + 1)) {
        *puVar7 = 0;
        if ((char)puVar7[1] == '\0') {
          if ((byte)puVar7[-1] < 100) {
            cVar2 = (byte)puVar7[-1] + 1;
            goto LAB_08063024;
          }
          uVar3 = 1;
        }
        else {
          if ((char)puVar7[1] != '\x01') break;
          if ((char)puVar7[-1] != '\0') {
            cVar2 = (char)puVar7[-1] + -1;
            goto LAB_08063024;
          }
          uVar3 = 0;
        }
        *(undefined1 *)(puVar7 + 1) = uVar3;
      }
      break;
    case '\x02':
      if ((char)puVar7[1] == '\x01') {
        uVar4 = *puVar7 - 1;
      }
      else {
        uVar4 = *puVar7 + 1;
      }
      *puVar7 = uVar4;
      if (0x78 < *puVar7) {
        *(undefined1 *)(puVar7 + 1) = 1;
      }
      if (*puVar7 == 0) {
        *(undefined1 *)(puVar7 + 1) = 0;
      }
      cVar2 = FUN_0804ec28(*puVar7,0,0x14,0x78);
LAB_08063024:
      *(char *)(puVar7 + -1) = cVar2;
      FUN_0806307c(param_1,(char)puVar7[-3]);
      break;
    case '\x03':
      uVar4 = *puVar7 + 1;
      *puVar7 = uVar4;
      if (*(char *)((int)puVar7 + -5) == '\0') {
        if ((int)(uint)*(ushort *)(iVar1 + (uint)*(byte *)((int)puVar7 + -3) * 2) / param_2 <=
            (int)(uint)uVar4) {
          if ((byte)puVar7[-3] < 3) {
            iVar6 = param_1 + (uint)(byte)puVar7[-3] * 10;
            *(undefined1 *)(iVar6 + 9) = 1;
            FUN_08060ac4(*(undefined1 *)(iVar6 + 8),1,*(undefined1 *)(iVar6 + 0xd));
          }
LAB_08062fc0:
          *puVar7 = 0;
        }
      }
      else if ((int)(uint)*(ushort *)(iVar1 + (uint)*(byte *)((int)puVar7 + -3) * 2 + 0xc) / param_2
               <= (int)(uint)uVar4) {
        if ((byte)puVar7[-3] < 3) {
          iVar6 = param_1 + (uint)(byte)puVar7[-3] * 10;
          *(undefined1 *)(iVar6 + 9) = 0;
          FUN_08060ac4(*(undefined1 *)(iVar6 + 8),0,*(undefined1 *)(iVar6 + 0xd));
        }
        goto LAB_08062fc0;
      }
      break;
    case '\x04':
      uVar5 = (uint)(byte)puVar7[-3];
      if (uVar5 < 3) {
        uVar3 = 1;
        goto LAB_0806304c;
      }
    }
    puVar7 = puVar7 + 5;
    iVar8 = iVar8 + -1;
    if (iVar8 == 0) {
      return param_4;
    }
  } while( true );
}

### FUN_0804E4F8


void FUN_0804e4f8(int *param_1)

{
  undefined4 uVar1;
  int *piVar2;
  
  *(undefined1 *)(param_1 + 0xb0) = 0;
  FUN_0804bc6c(param_1);
  *(undefined1 *)((int)param_1 + 0xe9) = 0;
  FUN_08031134(param_1 + 0xab,7,&DAT_0804e728,0x14);
  param_1[0xaa] = (int)(param_1 + 0xab);
  piVar2 = param_1 + 0x9d;
  FUN_080313a4(piVar2,0x6a);
  *(undefined2 *)(param_1 + 0x9f) = 0xaf;
  *(short *)(param_1 + 0x9e) = (short)param_1[2] + -0xb9;
  *(short *)((int)param_1 + 0x27a) =
       (short)(((int)*(short *)((int)param_1 + 10) - (int)*(short *)((int)param_1 + 0x27e)) / 2);
  uVar1 = FUN_08030268(0xff,0xff,0xff);
  FUN_08031426(piVar2,uVar1);
  (**(code **)(*param_1 + 100))(param_1,piVar2);
  (**(code **)(*param_1 + 100))(param_1,param_1 + 0xb5);
                    /* WARNING: Could not recover jumptable at 0x0804e596. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (**(code **)(*param_1 + 100))(param_1,param_1 + 0xc0);
  return;
}

### FUN_0804E598


void FUN_0804e598(int param_1,int param_2)

{
  *(undefined1 *)(param_1 + 0x299) = 0;
  *(undefined1 *)(param_1 + 0x2f9) = 0;
  if (param_2 == 0) {
    param_2 = 0;
  }
  else {
    *(undefined1 *)(param_1 + 0xe9) = 0;
  }
  *(char *)(param_1 + 0x11d) = (char)param_2;
  *(undefined1 *)(param_1 + 0x2c0) = 1;
  return;
}

### FUN_0804E5BC


undefined8 FUN_0804e5bc(int param_1,uint param_2,undefined4 param_3,int param_4)

{
  char cVar1;
  short sVar2;
  undefined2 uVar3;
  int iVar4;
  uint uVar5;
  undefined4 uVar6;
  int iVar7;
  undefined2 local_18;
  undefined2 uStack_16;
  int local_14;
  
  local_18 = (undefined2)param_3;
  uStack_16 = (undefined2)((uint)param_3 >> 0x10);
  iVar7 = 0x20;
  if ((int)param_2 < 0) {
    iVar7 = 0x2d;
  }
  cVar1 = *(char *)(param_1 + 0x2c0);
  local_14 = param_4;
  if (cVar1 != '\0') {
    if (cVar1 == '\x02') {
      uVar5 = *(ushort *)(param_1 + 0x2c8) - 1;
      if ((int)uVar5 < (int)param_2) {
        param_2 = uVar5;
      }
      local_18 = *(undefined2 *)(*(int *)(param_1 + 0x2c4) + param_2 * 2);
      iVar7 = param_1 + 0x2d4;
      FUN_080307bc(iVar7,&local_18);
      *(short *)(param_1 + 0x2d8) = (*(short *)(param_1 + 8) - *(short *)(param_1 + 0x2dc)) + -10;
      *(short *)(param_1 + 0x2da) =
           (short)(((int)*(short *)(param_1 + 10) - (int)*(short *)(param_1 + 0x2de)) / 2);
    }
    else {
      if (cVar1 != '\x03') {
        if (cVar1 == '\x01') {
          FUN_08032e80(param_1 + 0xf8,param_2 & 0xff,1,iVar7);
        }
        return CONCAT44(local_14,CONCAT22(uStack_16,local_18));
      }
      uVar5 = *(ushort *)(param_1 + 0x2d0) - 1;
      if ((int)uVar5 < (int)param_2) {
        param_2 = uVar5;
      }
      local_18 = *(undefined2 *)(*(int *)(param_1 + 0x2cc) + param_2 * 2);
      iVar7 = param_1 + 0x300;
      FUN_080313a4(iVar7,CONCAT22(uStack_16,local_18));
      uVar3 = FUN_080311d6(iVar7);
      *(undefined2 *)(param_1 + 0x308) = uVar3;
      uVar6 = FUN_08030268(0xff,0xff,0xff);
      FUN_08031426(iVar7,uVar6);
      *(short *)(param_1 + 0x304) = (*(short *)(param_1 + 8) - *(short *)(param_1 + 0x308)) + -10;
      *(short *)(param_1 + 0x306) =
           (short)(((int)*(short *)(param_1 + 10) - (int)*(short *)(param_1 + 0x30a)) / 2);
    }
    goto LAB_0804e710;
  }
  sVar2 = *(short *)(param_1 + 0x334);
  if (sVar2 == 0) {
LAB_0804e63e:
    FUN_08031134(param_1 + 0x2ac,7,&DAT_0804e728,param_2);
  }
  else {
    if (sVar2 == 1) {
      iVar4 = (int)((ulonglong)((longlong)(int)param_2 * (longlong)DAT_0804e738) >> 0x20);
      iVar4 = (iVar4 >> 2) - (iVar4 >> 0x1f);
      local_14 = param_2 + iVar4 * -10;
      if (local_14 < 0) {
        local_14 = -local_14;
      }
      if (iVar4 < 0) {
        iVar4 = -iVar4;
      }
      local_18 = (undefined2)iVar4;
      uStack_16 = (undefined2)((uint)iVar4 >> 0x10);
    }
    else {
      if (sVar2 != 2) goto LAB_0804e63e;
      iVar7 = (int)((ulonglong)((longlong)(int)param_2 * (longlong)DAT_0804e73c) >> 0x20);
      iVar7 = (iVar7 >> 5) - (iVar7 >> 0x1f);
      iVar4 = param_2 + iVar7 * -100;
      if (iVar4 < 0) {
        iVar4 = -iVar4;
      }
      if (iVar7 < 0) {
        iVar7 = -iVar7;
      }
      local_18 = (undefined2)iVar4;
      uStack_16 = (undefined2)((uint)iVar4 >> 0x10);
    }
    FUN_08031134(param_1 + 0x2ac,7,s__c_d__d_0804e79c,iVar7);
  }
  *(int *)(param_1 + 0x2a8) = param_1 + 0x2ac;
  iVar7 = param_1 + 0x274;
LAB_0804e710:
  FUN_08032316(iVar7);
  return CONCAT44(local_14,CONCAT22(uStack_16,local_18));
}

### FUN_0804E740


void FUN_0804e740(int param_1,undefined4 param_2,undefined2 param_3)

{
  *(undefined4 *)(param_1 + 0x2c4) = param_2;
  *(undefined1 *)(param_1 + 0x2c0) = 2;
  *(undefined2 *)(param_1 + 0x2c8) = param_3;
  *(undefined1 *)(param_1 + 0x299) = 0;
  *(undefined1 *)(param_1 + 0x325) = 0;
  return;
}

### FUN_0804E75A


void FUN_0804e75a(int param_1,undefined4 param_2,undefined2 param_3)

{
  *(undefined4 *)(param_1 + 0x2cc) = param_2;
  *(undefined1 *)(param_1 + 0x2c0) = 3;
  *(undefined2 *)(param_1 + 0x2d0) = param_3;
  *(undefined1 *)(param_1 + 0x299) = 0;
  *(undefined1 *)(param_1 + 0x2f9) = 0;
  return;
}

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

### FUN_080618A0
- FUN_080618a0(param_1);
- FUN_080618a0(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,uint param_5,

### FUN_08061930
- FUN_08061930(param_1 + 0x18);
- int FUN_08061930(int param_1)

### FUN_08061942
- FUN_08061942();
- void FUN_08061942(undefined2 *param_1)

### FUN_08062638
- void FUN_08062638(int param_1)

### FUN_08062920
- uVar6 = FUN_08062920(&local_bc);
- longlong FUN_08062920(int *param_1,undefined4 param_2,undefined4 param_3,int param_4)

### FUN_08062D82
- void FUN_08062d82(void)

### FUN_08062F18
- undefined4 FUN_08062f18(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

### FUN_0804E4F8
- FUN_0804e4f8(iVar10,(int)(short)(&DAT_0804866e)[iVar4 * 8],(&DAT_08048670)[iVar4 * 8],0,param_2)
- void FUN_0804e4f8(int *param_1)

### FUN_0804E598
- FUN_0804e598(iVar10,1);
- void FUN_0804e598(int param_1,int param_2)

### FUN_0804E5BC
- FUN_0804e5bc(iVar10,10);
- FUN_0804e5bc(iVar1,param_3);
- undefined8 FUN_0804e5bc(int param_1,uint param_2,undefined4 param_3,int param_4)

### FUN_0804E740
- FUN_0804e740(iVar10,*(undefined4 *)(iVar5 + 0x8048674),*(undefined2 *)(iVar5 + 0x8048678));
- void FUN_0804e740(int param_1,undefined4 param_2,undefined2 param_3)

### FUN_0804E75A
- FUN_0804e75a(iVar10,*(undefined4 *)(iVar5 + 0x8048674),*(undefined2 *)(iVar5 + 0x8048678));
- void FUN_0804e75a(int param_1,undefined4 param_2,undefined2 param_3)

### FUN_08032316
- FUN_08032316(param_1 + 0x58a0);
- FUN_08032316(param_1 + 0x58e4);
- FUN_08032316(param_1 + 0x592c);
- FUN_08032316(param_1 + 0x5970,local_18);
- FUN_08032316(iVar2);
- FUN_08032316(param_1 + 0x3018);
- FUN_08032316(param_1 + 0x5264);
- FUN_08032316(param_1 + 0x5298);
- FUN_08032316(param_1 + 0x52c4);
- FUN_08032316(param_1);
- FUN_08032316(param_1 + 0x5328,local_10,uStack_c);
- FUN_08032316(param_1 + 0x52f0);
- FUN_08032316(param_1 + 0x51f8,param_4);
- FUN_08032316(param_1 + 0x5398);
- FUN_08032316(param_1 + 0x542c);
- FUN_08032316(param_1 + 0x5188);
- FUN_08032316(param_1 + 0x51c0,in_stack_ffffffe8,uStack_14);
- uVar1 = FUN_08032316(param_1 + 0x53f8,local_20);
- FUN_08032316(param_1 + 0x5360);
- FUN_08032316(iVar4);
- FUN_08032316(param_1 + 0x5d4);
- FUN_08032316(iVar3);
- FUN_08032316(param_1 + 0x50e8);
- FUN_08032316(param_1 + 0x600);
- FUN_08032316(param_1 + 0x5814);
- FUN_08032316(param_1 + 0x60);
- FUN_08032316(param_1 + 0x2c,local_10,uStack_c);
- FUN_08032316(param_1 + 0x950);
- FUN_08032316(piVar4);
- FUN_08032316(param_1 + 0x260);

### CanTxTask
- FUN_08057630(DAT_08062eb8,s_CanTxTask_08062edc,100,0,2,0,0,0);

### CanRxTask
- FUN_08057630(DAT_08062eb4,s_CanRxTask_08062ed0,100,0,2,0,0,0);

### CanMessagesToTransmit
[OPEN] no textual occurrence

### DAT_0803C218
- switch(*(undefined1 *)(DAT_0803c218 + param_2)) {

### DAT_08038694
- *param_1 = DAT_08038694;

### DAT_08038698
- *DAT_08038698 = param_1;

### DAT_0803869C
- *param_1 = DAT_0803869c;

### 0x20005EF0
[OPEN] no textual occurrence

## ### INTERPRETACJA

[NEW-HARD] The large decompiled blob is not lost. It is retrievable directly by Git blob SHA.
[NEW-HARD] Target decompiled bodies can be extracted from that blob without downloading the entire file through the Contents API.
[OPEN] Thumb HEX remains dependent on original firmware bytes; decompiled C does not contain literal machine bytes.
[OPEN] Static decompiled text does not materialize the runtime SRAM table at 0x20005EF0 or literal vtable storage values.

## ### STATUS
| Element | Status |
|---|---|
| decompiled.c blob | [NEW-HARD] recovered |
| 7 CAN TX target bodies | [NEW-HARD] extracted where present |
| 6 UI helper target bodies | [NEW-HARD] extracted where present |
| xref textual scan | [NEW-HARD] |
| Thumb HEX | [OPEN] |
| SRAM 108 B | [OPEN] |
| vtable literal bytes | [OPEN] |
| CO1..CO4 complete 1:1 mapping | [OPEN] |
