# RAW DECOMPILED SNIPPET INDEX — FW2213TK_kopia.bin

Firmware SHA-256: `1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071`
Source: `firmware/FW2213TK-ghidra/decompiled.c` (blob SHA `9620d0c85259d34bb6a20d3b03b038945dfe4c1a`).

These are exact extracted function blocks from the committed Ghidra decompiled output, copied without semantic edits. Ghidra types/names remain approximate. Addresses are raw/runtime as embedded in file comments.

## 0803cf54

```c
// 0803cf54

void FUN_0803cf54(int param_1)

{
  undefined1 uVar1;
  undefined1 uVar2;
  undefined2 uVar3;
  undefined4 uVar4;
  int iVar5;
  undefined *puVar6;
  
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x39);
  FUN_08043a74(*(undefined4 *)(param_1 + 0xc),uVar1);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x5f);
  uVar4 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x3a);
  FUN_0804368a(*(undefined4 *)(param_1 + 0xc),uVar4,uVar1);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x5f);
  uVar4 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x3b);
  FUN_080436b4(*(undefined4 *)(param_1 + 0xc),uVar4,uVar1);
  uVar4 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x3e);
  FUN_08043746(*(undefined4 *)(param_1 + 0xc),uVar4);
  uVar4 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x3f);
  FUN_08043760(*(undefined4 *)(param_1 + 0xc),uVar4);
  iVar5 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x116);
  if (iVar5 != 2) {
    uVar4 = 0;
  }
  else {
    uVar4 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x40);
  }
  FUN_0804377a(*(undefined4 *)(param_1 + 0xc),uVar4,iVar5 == 2);
  uVar4 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x47);
  FUN_080437a0(*(undefined4 *)(param_1 + 0xc),uVar4);
  uVar3 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x44);
  FUN_080437d2(*(undefined4 *)(param_1 + 0xc),uVar3);
  uVar4 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x22);
  FUN_0804381a(*(undefined4 *)(param_1 + 0xc),uVar4);
  uVar4 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x8b);
  FUN_0804388e(*(undefined4 *)(param_1 + 0xc),uVar4);
  uVar4 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x8c);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x90);
  FUN_08043844(*(undefined4 *)(param_1 + 0xc),uVar1,uVar4);
  uVar4 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x6a);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x115);
  FUN_080438b8(*(undefined4 *)(param_1 + 0xc),uVar1,uVar4);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0xa0);
  FUN_08043874(*(undefined4 *)(param_1 + 0xc),uVar1);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x68);
  FUN_08043a36(*(undefined4 *)(param_1 + 0xc),uVar1);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x5f);
  uVar3 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0xa2);
  FUN_080436f8(*(undefined4 *)(param_1 + 0xc),uVar3,uVar1);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x5f);
  uVar2 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x39);
  uVar3 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0xa3);
  FUN_08043b44(*(undefined4 *)(param_1 + 0xc),uVar3,uVar2,uVar1);
  uVar3 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x95);
  FUN_08043b94(*(undefined4 *)(param_1 + 0xc),uVar3);
  uVar3 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x6b);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x120);
  FUN_08043908(*(undefined4 *)(param_1 + 0xc),uVar1,uVar3);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x41);
  FUN_08043954(*(undefined4 *)(param_1 + 0xc),1,uVar1);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x45);
  FUN_08043954(*(undefined4 *)(param_1 + 0xc),0,uVar1);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x46);
  FUN_08043954(*(undefined4 *)(param_1 + 0xc),2,uVar1);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x47);
  FUN_08043954(*(undefined4 *)(param_1 + 0xc),3,uVar1);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x75);
  FUN_08043954(*(undefined4 *)(param_1 + 0xc),4,uVar1);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x85);
  FUN_08043b3a(*(undefined4 *)(param_1 + 0xc),uVar1);
  iVar5 = *(int *)(param_1 + 0xc);
  if (*(char *)(DAT_0803d174 + 0x285) == '\0') {
    puVar6 = &DAT_08043bfc;
  }
  else {
    puVar6 = &DAT_08043c00;
  }
  FUN_08031134(iVar5 + 0x149e,3,puVar6);
  FUN_08032316(iVar5 + 0xea0);
  return;
}


```

## 08043a36

```c
// 08043a36

void FUN_08043a36(int param_1,int param_2)

{
  undefined2 local_1c [2];
  undefined2 local_18 [2];
  undefined2 local_14 [2];
  undefined2 local_10 [4];
  
  if (param_2 == 1) {
    local_14[0] = 0xb6;
  }
  else {
    local_14[0] = 0xb7;
  }
  local_18[0] = 0xa9;
  local_1c[0] = 0xa8;
  local_10[0] = local_14[0];
  FUN_0802ddca(param_1 + 0xf74,local_1c,local_18,local_14,local_10);
  FUN_08032316(param_1 + 0xf74);
  return;
}


```

## 0803ec18

```c
// 0803ec18

void FUN_0803ec18(int param_1,int param_2)

{
  char cVar1;
  short sVar2;
  short sVar3;
  short sVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  byte bVar9;
  byte bVar10;
  short *psVar11;
  int iVar12;
  undefined4 *puVar13;
  int iVar14;
  bool bVar15;
  bool bVar16;
  int local_50;
  undefined4 local_4c;
  undefined4 local_48;
  uint local_44;
  undefined4 local_40;
  undefined4 local_3c;
  undefined4 local_38;
  undefined4 local_34;
  undefined4 local_30;
  undefined4 local_2c;
  undefined4 local_28;
  undefined4 local_24;
  
  iVar5 = FUN_080314ba();
  iVar14 = param_1 + param_2 * 2;
  *(undefined4 *)(iVar5 + 0x15c) = 0;
  sVar2 = *(short *)(iVar14 + 0x20);
  iVar5 = 0;
  psVar11 = &DAT_0803f008;
  do {
    sVar3 = *psVar11;
    bVar15 = sVar2 == sVar3;
    if (!bVar15) {
      iVar5 = iVar5 + 1;
      sVar3 = psVar11[8];
    }
    bVar16 = sVar2 == sVar3;
    iVar12 = iVar5;
    if (!bVar15 && !bVar16) {
      iVar12 = iVar5 + 1;
      sVar3 = psVar11[0x10];
    }
    iVar5 = iVar12;
    if (((bVar15 || bVar16) || sVar2 == sVar3) || (iVar5 = iVar12 + 1, sVar2 == psVar11[0x18]))
    break;
    iVar5 = iVar12 + 2;
    psVar11 = psVar11 + 0x20;
  } while (iVar5 < 0xbc);
  if (iVar5 == 0xbc) {
    iVar5 = 0;
  }
  iVar12 = iVar5 * 0x10;
  cVar1 = (&DAT_0803f00e)[iVar12];
  if (cVar1 == '\x05') {
    sVar2 = (&DAT_0803f008)[iVar5 * 8];
    if (sVar2 == 0x47 || sVar2 == 0x48) {
      local_48 = 0x14;
      local_40 = 0x28;
      puVar13 = (undefined4 *)(param_1 + 8);
      local_38 = 0x3c;
      local_30 = 0x50;
      local_28 = 100;
      if (sVar2 == 0x47) {
        local_44 = FUN_08036ff2(*puVar13,0x4a);
        local_3c = FUN_08036ff2(*puVar13,0x4b);
        local_34 = FUN_08036ff2(*puVar13,0x4c);
        local_2c = FUN_08036ff2(*puVar13,0x4d);
        local_24 = FUN_08036ff2(*puVar13,0x4e);
        local_4c = 0x8e;
      }
      else {
        local_44 = FUN_08036ff2(*puVar13,0x4f);
        local_3c = FUN_08036ff2(*puVar13,0x50);
        local_34 = FUN_08036ff2(*puVar13,0x51);
        local_2c = FUN_08036ff2(*puVar13,0x52);
        local_24 = FUN_08036ff2(*puVar13,0x53);
        local_4c = 0x7e;
      }
      local_50 = 100;
      FUN_08048520(*(undefined4 *)(param_1 + 0x1c),&local_48,5,0);
    }
  }
  else if (cVar1 == '\0') {
    sVar3 = (&DAT_0803f008)[iVar5 * 8];
    if (*DAT_0803eec4 != sVar3) {
      bVar10 = 1;
      psVar11 = DAT_0803eec4 + 1;
      do {
        sVar4 = *psVar11;
        bVar15 = sVar4 == sVar3;
        if (!bVar15) {
          bVar10 = bVar10 + 1;
          sVar4 = psVar11[1];
        }
        bVar16 = sVar4 == sVar3;
        bVar9 = bVar10;
        if (!bVar15 && !bVar16) {
          bVar9 = bVar10 + 1;
          sVar4 = psVar11[2];
        }
        bVar10 = bVar9;
        if (((bVar15 || bVar16) || sVar4 == sVar3) || (bVar10 = bVar9 + 1, psVar11[3] == sVar3))
        break;
        bVar10 = bVar9 + 2;
        psVar11 = psVar11 + 4;
      } while (bVar10 < 0xd);
      if (0xc < bVar10) {
        puVar13 = (undefined4 *)(param_1 + 8);
        if (sVar2 != 0xa9) {
          iVar5 = FUN_0803716e(*puVar13,(int)*(short *)(iVar14 + 0x20));
          uVar7 = FUN_080370c0(*puVar13,(int)*(short *)(iVar14 + 0x20));
          uVar6 = FUN_08036ff2(*puVar13,(int)*(short *)(iVar14 + 0x20));
          bVar10 = *(byte *)(iVar12 + 0x803f00f);
          local_50 = iVar5;
        }
        else {
          uVar6 = FUN_08036ff2();
          bVar10 = *(byte *)(iVar12 + 0x803f00f);
          uVar7 = uRam0803fbcc;
          local_50 = iRam0803fbd0;
        }
        local_4c = (uint)bVar10;
        FUN_08048468(*(undefined4 *)(param_1 + 0x1c),(int)*(short *)(iVar12 + 0x803f00a),uVar6,uVar7
                    );
      }
    }
  }
  else if (cVar1 == '\x03') {
    if (sVar2 != 0xa9) {
      uVar7 = FUN_080370c0(*(undefined4 *)(param_1 + 8));
      uVar6 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),(int)*(short *)(iVar14 + 0x20));
      local_48 = *(undefined4 *)(iVar12 + 0x803f010);
      bVar10 = *(byte *)(iVar12 + 0x803f00f);
      local_50 = *(ushort *)(iVar12 + 0x803f014) - 1;
    }
    else {
      uVar6 = FUN_08036ff2();
      local_48 = *(undefined4 *)(iVar12 + 0x803f010);
      bVar10 = *(byte *)(iVar12 + 0x803f00f);
      local_50 = iRam0803fbd0;
      uVar7 = uRam0803fbcc;
    }
    local_4c = (uint)bVar10;
    FUN_080484b0(*(undefined4 *)(param_1 + 0x1c),(int)*(short *)(iVar12 + 0x803f00a),uVar6,uVar7);
  }
  else if (cVar1 == '\x04') {
    puVar13 = (undefined4 *)(param_1 + 8);
    uVar7 = FUN_08036ff2(*puVar13,0xd4);
    uVar6 = FUN_08036ff2(*puVar13,0xd5);
    uVar8 = FUN_08036ff2(*puVar13,0xd6);
    local_50 = CONCAT13((char)uVar7,
                        CONCAT21(CONCAT11((char)((uint)uVar7 >> 8),(char)((uint)uVar7 >> 0x10)),
                                 (char)((uint)uVar7 >> 0x18)));
    local_4c = CONCAT13((char)uVar6,
                        CONCAT12((char)((uint)uVar6 >> 8),
                                 CONCAT11((char)((uint)uVar6 >> 0x10),(char)((uint)uVar6 >> 0x18))))
    ;
    local_48._3_1_ = (undefined1)uVar8;
    local_48._0_3_ =
         CONCAT12((char)((uint)uVar8 >> 8),
                  CONCAT11((char)((uint)uVar8 >> 0x10),(char)((uint)uVar8 >> 0x18)));
    local_44 = local_44 & 0xffffff00;
    FUN_080484f0(*(undefined4 *)(param_1 + 0x1c),(int)*(short *)(iVar12 + 0x803f00a),&local_50,0xd);
  }
  *(short *)(param_1 + 0xea) = (short)param_2;
  return;
}


```

## 08048624

```c
// 08048624

void FUN_08048624(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  iVar1 = *(int *)(param_1 + 0x84ec);
  uVar3 = 0;
  do {
    if ((int)(uint)*(byte *)(param_1 + 0x3b8) <= (int)uVar3) {
LAB_0804864e:
      uVar2 = FUN_08032f08(uVar3 * 0x338 + param_1 + 0x524);
      FUN_0803eecc(*(undefined4 *)(param_1 + 0x3c),uVar2,param_4);
      return;
    }
    if (param_2 == iVar1) {
      FUN_0803ec18(*(undefined4 *)(param_1 + 0x3c),uVar3 & 0xffff);
      goto LAB_0804864e;
    }
    uVar3 = uVar3 + 1;
    iVar1 = iVar1 + 0x338;
  } while( true );
}


```

## 0807eb36

```c
// 0807eb36

void FUN_0807eb36(int param_1,int param_2)

{
  uint uVar1;
  
  for (uVar1 = 0; (int)uVar1 < (int)(uint)*(byte *)(param_1 + 0x3b8); uVar1 = uVar1 + 1) {
    if (param_2 == *(int *)(param_1 + 0x3b4) + uVar1 * 0x274) {
      FUN_0803ec18(*(undefined4 *)(param_1 + 0x3c),uVar1 & 0xffff);
    }
  }
  return;
}


```

## 0804752c

```c
// 0804752c

undefined8 FUN_0804752c(int param_1,int param_2)

{
  short sVar1;
  short sVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  short sVar6;
  int iVar7;
  bool bVar8;
  undefined2 local_18;
  undefined6 uStack_16;
  
  sVar2 = *(short *)(param_1 + 0x36);
  sVar6 = *(short *)(param_1 + 6);
  sVar1 = *(short *)(param_1 + 0x32);
  local_18 = 0x39;
  FUN_080307bc(param_1 + 0x2c,&local_18);
  FUN_08032316(param_1 + 0x2c);
  iVar7 = (int)(short)(sVar1 + sVar6 + sVar2 / 2);
  sVar6 = *(short *)(param_2 + 0xc) - *(short *)(param_2 + 8);
  iVar5 = *(int *)(param_1 + 0x8c);
  iVar3 = sVar6 + iVar7;
  bVar8 = SBORROW4(iVar3,iVar5);
  iVar4 = iVar3 - iVar5;
  if (iVar5 <= iVar3) {
    bVar8 = SBORROW4(*(int *)(param_1 + 0x90),iVar3);
    iVar4 = *(int *)(param_1 + 0x90) - iVar3;
  }
  if (iVar4 < 0 == bVar8) {
    FUN_080323be(param_1,0,(int)sVar6);
  }
  if ((*(int **)(param_1 + 0xe0) != (int *)0x0) &&
     (iVar4 = (**(code **)(**(int **)(param_1 + 0xe0) + 0xc))(), iVar4 != 0)) {
    (**(code **)(**(int **)(param_1 + 0xe0) + 8))(*(int **)(param_1 + 0xe0),param_1,iVar7);
  }
  return CONCAT62(uStack_16,local_18);
}


```

## 08047604

```c
// 08047604

undefined4 * FUN_08047604(undefined4 *param_1)

{
  short sVar1;
  int iVar2;
  undefined4 uVar3;
  int *piVar4;
  int iVar5;
  undefined4 *puVar6;
  undefined4 *puVar7;
  int *piVar8;
  short sVar9;
  short *psVar10;
  int iVar11;
  bool bVar12;
  undefined2 uVar13;
  undefined4 local_34;
  short local_30;
  undefined2 uStack_2e;
  undefined2 local_2c [2];
  undefined2 local_28 [2];
  
  FUN_0802e620();
  iVar2 = DAT_08047e20;
  uVar3 = DAT_08047e1c;
  *param_1 = DAT_08047e18;
  puVar7 = param_1 + 0x28;
  *(undefined1 *)(param_1 + 0x27) = 0xff;
  FUN_0802dd4c(puVar7);
  param_1[0x28] = DAT_08047e24;
  *(undefined1 *)((int)param_1 + 0xc6) = 0xff;
  param_1[0x32] = 0;
  *(undefined1 *)(param_1 + 0x33) = 0;
  piVar8 = param_1 + 0x277;
  FUN_0802dd4c(param_1 + 0x34);
  param_1[0x34] = DAT_08047e28;
  param_1[0x3e] = 0;
  FUN_0802fc10(param_1 + 0x3f);
  FUN_0802fc10(param_1 + 0x4c);
  FUN_0800dcd4(param_1 + 0x59,DAT_08047e2c,0x40,5);
  FUN_0804dc9c(param_1 + 0xa9);
  FUN_0800dcd4(param_1 + 0xba,DAT_08047e30,0xe4,5);
  FUN_0800dcd4(param_1 + 0x1d7,DAT_08047e34,0x54,4);
  FUN_0804dce0(param_1 + 0x22b,0,0xff);
  FUN_0800dcd4(param_1 + 0x231,uVar3,0x38,5);
  FUN_0800dcd4(piVar8,uVar3,0x38,5);
  piVar4 = param_1 + 0x2e0;
  FUN_0802dd74(piVar4);
  *piVar4 = iVar2 + 8;
  param_1[0x2f1] = 3;
  FUN_0802dd74(param_1 + 0x2f2);
  param_1[0x2f2] = iVar2 + 8;
  param_1[0x303] = 3;
  FUN_0804dd7c(param_1 + 0x304,param_1,DAT_08047e44,DAT_08047e48);
  FUN_0804dd90(param_1 + 0x308,param_1,DAT_08047e4c,DAT_08047e50);
  FUN_08030358(puVar7,0x23,0x32,0x14f,0xb4);
  FUN_08030380(param_1,puVar7);
  puVar7 = DAT_08047e38;
  iVar2 = (int)*(short *)((int)param_1 + 0xaa);
  FUN_08030358(param_1 + 0x34,(int)*(short *)(param_1 + 0x29),(int)*(short *)((int)param_1 + 0xa6),
               (int)*(short *)(param_1 + 0x2a),iVar2);
  FUN_0802e652(param_1,0x8e);
  param_1[0x1a] = 100;
  iVar5 = 0;
  param_1[0x1b] = 0;
  iVar11 = 0;
  param_1[0x1c] = 100;
  puVar6 = param_1 + 0xba;
  do {
    FUN_08030380(param_1 + 0x34,puVar6);
    FUN_08047c1a(param_1,iVar5,iVar11,*puVar7);
    puVar6[0x23] = 0x28;
    iVar5 = iVar5 + 1;
    puVar6[0x24] = 0xa0;
    puVar6[0x38] = param_1 + 0x308;
    iVar11 = iVar11 + 0x19;
    puVar6 = puVar6 + 0x39;
    puVar7 = puVar7 + 1;
  } while (iVar5 < 5);
  iVar5 = 0;
  puVar7 = param_1 + 0x2c2;
  psVar10 = (short *)(param_1 + 0xbb);
  do {
    uVar13 = (undefined2)((uint)iVar2 >> 0x10);
    FUN_08031134(puVar7,5,&DAT_08047b7c);
    piVar8[0xd] = (int)puVar7;
    iVar2 = CONCAT22(uVar13,0x1d4);
    FUN_080313a4(piVar8,iVar2);
    *(undefined2 *)(piVar8 + 2) = 0x32;
    *(undefined2 *)(piVar8 + 1) = 0;
    uVar3 = FUN_08030268(0xff,0xff,0xff);
    FUN_08031426(piVar8,uVar3);
    sVar9 = *(short *)((int)param_1 + 0xd6);
    sVar1 = *(short *)((int)param_1 + 0xda);
    (**(code **)(*piVar8 + 0x2c))(piVar8,(int)(short)(*(short *)(param_1 + 0x35) + *psVar10));
    (**(code **)(*piVar8 + 0x30))(piVar8,(int)(short)(sVar1 + sVar9));
    FUN_08030380(param_1,piVar8);
    iVar5 = iVar5 + 1;
    puVar7 = puVar7 + 3;
    piVar8 = piVar8 + 0xe;
    psVar10 = psVar10 + 0x72;
  } while (iVar5 < 5);
  iVar5 = 0;
  piVar8 = param_1 + 0x1d7;
  sVar9 = 0;
  do {
    uVar13 = (undefined2)((uint)iVar2 >> 0x10);
    (**(code **)(*piVar8 + 0x34))
              (piVar8,(int)*(short *)(param_1 + 0x35),(int)*(short *)((int)param_1 + 0xd6));
    (**(code **)(*piVar8 + 0x38))(piVar8,0x1e0);
    (**(code **)(*piVar8 + 0x3c))(piVar8,200);
    local_34 = CONCAT22(uVar13,sVar9);
    sVar1 = (short)piVar8[0xc];
    bVar12 = sVar1 == sVar9;
    if (bVar12) {
      sVar1 = *(short *)((int)piVar8 + 0x32);
    }
    uVar13 = uStack_2e;
    if (!bVar12 || sVar1 != sVar9) {
      *(short *)(piVar8 + 0xc) = sVar9;
      *(short *)((int)piVar8 + 0x32) = sVar9;
      local_30 = sVar9;
      uVar13 = uStack_2e;
      FUN_0804de80(piVar8);
    }
    local_30 = ((short)iVar5 + 1) * 0x140;
    local_34 = CONCAT22(uVar13,local_30);
    sVar1 = (short)piVar8[0xd];
    bVar12 = sVar1 == local_30;
    if (bVar12) {
      sVar1 = *(short *)((int)piVar8 + 0x36);
    }
    uVar13 = uStack_2e;
    if (!bVar12 || sVar1 != local_30) {
      *(short *)(piVar8 + 0xd) = local_30;
      *(short *)((int)piVar8 + 0x36) = local_30;
      FUN_0804de80(piVar8);
    }
    local_34 = CONCAT22(uVar13,0xc0);
    local_30 = 0xc0;
    sVar1 = (short)piVar8[0xc];
    bVar12 = sVar1 == 0xc0;
    if (bVar12) {
      sVar1 = *(short *)((int)piVar8 + 0x32);
    }
    uVar13 = uStack_2e;
    if (!bVar12 || sVar1 != 0xc0) {
      *(undefined2 *)(piVar8 + 0xc) = 0xc0;
      *(undefined2 *)((int)piVar8 + 0x32) = 0xc0;
      FUN_0804de80(piVar8);
    }
    local_34._0_2_ = 0x1840;
    _local_30 = CONCAT22(uStack_2e,0x3c0);
    sVar1 = (short)piVar8[0xd];
    bVar12 = sVar1 == 0x1840;
    if (bVar12) {
      sVar1 = *(short *)((int)piVar8 + 0x36);
    }
    local_34._2_2_ = uVar13;
    if (!bVar12 || sVar1 != 0x3c0) {
      *(undefined2 *)(piVar8 + 0xd) = 0x1840;
      *(undefined2 *)((int)piVar8 + 0x36) = 0x3c0;
      FUN_0804de80(piVar8);
    }
    local_34 = CONCAT22(local_34._2_2_,0xa0);
    iVar2 = local_34;
    if ((short)piVar8[0xe] != 0xa0) {
      *(undefined2 *)(piVar8 + 0xe) = 0xa0;
      FUN_0804de80(piVar8);
    }
    FUN_0804e218(piVar8,param_1 + 0x22b);
    FUN_08030380(param_1,piVar8);
    iVar5 = iVar5 + 1;
    piVar8 = piVar8 + 0x15;
    sVar9 = sVar9 + 0x140;
  } while (iVar5 < 4);
  local_28[0] = 5;
  local_2c[0] = 5;
  local_30 = 0xa9;
  local_34._0_2_ = 0xa8;
  FUN_0802ddca(piVar4,&local_34,&local_30,local_2c,local_28);
  (**(code **)(*piVar4 + 0x2c))(piVar4,0x181);
  (**(code **)(*piVar4 + 0x30))(piVar4,0x3c);
  param_1[0x2ea] = param_1 + 0x304;
  FUN_08030380(param_1,piVar4);
  local_28[0] = 3;
  local_2c[0] = 3;
  _local_30 = CONCAT22(uStack_2e,0xa9);
  local_34 = CONCAT22(local_34._2_2_,0xa8);
  FUN_0802ddca(param_1 + 0x2f2,&local_34,&local_30,local_2c,local_28);
  sVar9 = *(short *)((int)param_1 + 0xb86);
  (**(code **)(param_1[0x2f2] + 0x2c))(param_1 + 0x2f2,(int)*(short *)(param_1 + 0x2e1));
  (**(code **)(param_1[0x2f2] + 0x30))(param_1 + 0x2f2,(int)(short)(sVar9 + 0x32));
  param_1[0x2fc] = param_1 + 0x304;
  FUN_08030380(param_1,param_1 + 0x2f2);
  FUN_08030380(param_1,param_1 + 0x34);
  FUN_08032316(param_1 + 0x34);
  uVar3 = FUN_08030268(0x2c,0xa8,0xd1);
  FUN_0804dd02(param_1 + 0x22b,uVar3,0xff);
  FUN_080323be(param_1 + 0xb,0,0xfffffffb);
  return param_1;
}


```

## 08048520

```c
// 08048520

void FUN_08048520(int param_1)

{
  FUN_08047a8a(param_1 + 0x963c);
  FUN_0802eade(param_1 + 0x84f4,param_1 + 0x963c);
  return;
}


```

## 0803c064

```c
// 0803c064

void FUN_0803c064(int param_1,int param_2)

{
  short sVar1;
  undefined4 uVar2;
  int iVar3;
  byte bVar4;
  undefined4 *puVar5;
  undefined1 uVar6;
  int *piVar7;
  int iVar8;
  undefined1 auStack_20 [24];
  
  switch(*(undefined1 *)(DAT_0803c218 + param_2)) {
  case 0:
    FUN_080314ba();
    FUN_08038008();
    return;
  case 1:
    iVar3 = FUN_080314ba();
    bVar4 = 1;
    break;
  case 2:
    iVar3 = FUN_080314ba();
    bVar4 = 2;
    break;
  case 3:
    iVar3 = FUN_080314ba();
    bVar4 = 3;
    break;
  case 4:
    iVar3 = FUN_080314ba();
    bVar4 = 4;
    break;
  case 5:
    FUN_080314ba();
    FUN_080381e4();
    return;
  case 6:
    FUN_080314ba();
    FUN_080383b0();
    return;
  case 7:
    FUN_080314ba();
    FUN_08038278();
    return;
  case 8:
    FUN_080314ba();
    FUN_080382ca();
    return;
  case 9:
    FUN_080314ba();
    FUN_080382a6();
    return;
  case 10:
    FUN_080314ba();
    FUN_0803809c();
    return;
  case 0xb:
    iVar3 = FUN_080314ba();
    piVar7 = (int *)(iVar3 + 0x10c);
    iVar8 = iVar3 + 0x110;
    if (*(char *)(iVar3 + 0x12a) == '\0') {
      puVar5 = (undefined4 *)0x8038798;
    }
    else {
      puVar5 = (undefined4 *)0x80387a0;
    }
    goto LAB_08037f88;
  case 0xc:
    sVar1 = FUN_080373ba(*(undefined4 *)(param_1 + 8));
    FUN_080373e6(*(undefined4 *)(param_1 + 8),sVar1 + 1);
    FUN_080314ba();
    FUN_08037f5c();
    return;
  default:
    iVar3 = FUN_080314ba();
    piVar7 = (int *)(iVar3 + 0x10c);
    iVar8 = iVar3 + 0x110;
    if (*(char *)(iVar3 + 0x12a) == '\0') {
      puVar5 = (undefined4 *)0x80387a8;
    }
    else {
      puVar5 = (undefined4 *)0x80387b0;
    }
    goto LAB_08037f88;
  case 0xe:
    return;
  case 0xf:
    FUN_0802eade(*(int *)(param_1 + 0xc) + 0x37b0,*(int *)(param_1 + 0xc) + 0x422c);
    return;
  case 0x10:
    iVar3 = FUN_080314ba();
    uVar6 = 0x11;
    goto LAB_08038488;
  case 0x11:
    iVar3 = FUN_080314ba();
    uVar6 = 0x10;
LAB_08038488:
    *(undefined1 *)(iVar3 + 299) = uVar6;
    puVar5 = &DAT_08038790;
LAB_0803857c:
    uVar2 = FUN_08039494(auStack_20,iVar3,*puVar5,puVar5[1]);
    FUN_080394a8(iVar3 + 0x110,uVar2);
    *(int *)(iVar3 + 0x10c) = iVar3 + 0x110;
    return;
  case 0x12:
    iVar3 = FUN_080314ba();
    puVar5 = &DAT_080387b8;
    goto LAB_0803857c;
  case 0x13:
    iVar3 = FUN_080314ba();
    piVar7 = (int *)(iVar3 + 0x10c);
    iVar8 = iVar3 + 0x110;
    if (*(char *)(iVar3 + 0x12a) == '\0') {
      puVar5 = (undefined4 *)0x80387d0;
    }
    else {
      puVar5 = (undefined4 *)0x80387d8;
    }
    goto LAB_08037f88;
  case 0x14:
    iVar3 = FUN_080314ba();
    piVar7 = (int *)(iVar3 + 0x10c);
    *(undefined1 *)(iVar3 + 299) = 0x13;
    iVar8 = iVar3 + 0x110;
    if (*(char *)(iVar3 + 0x12a) == '\x01') {
      puVar5 = (undefined4 *)0x8038770;
    }
    else {
      puVar5 = (undefined4 *)0x8038778;
    }
    goto LAB_08037f88;
  }
  if (bVar4 == 4) {
    uVar6 = 4;
  }
  else if (bVar4 == 3) {
    uVar6 = 3;
  }
  else if (bVar4 == 2) {
    uVar6 = 2;
  }
  else {
    uVar6 = 1;
  }
  piVar7 = (int *)(iVar3 + 0x10c);
  *(undefined1 *)(iVar3 + 299) = uVar6;
  if (4 < bVar4) {
    bVar4 = 4;
  }
  *(byte *)(iVar3 + 300) = bVar4;
  iVar8 = iVar3 + 0x110;
  if (*(char *)(iVar3 + 0x12a) == '\0') {
    puVar5 = &DAT_08038708;
  }
  else if (*(char *)(iVar3 + 0x12a) == '\x01') {
    puVar5 = (undefined4 *)0x8038710;
  }
  else {
    puVar5 = &DAT_08038718;
  }
LAB_08037f88:
  uVar2 = FUN_08039494(auStack_20,iVar3,*puVar5,puVar5[1]);
  FUN_080394a8(iVar8,uVar2);
  *piVar7 = iVar8;
  return;
}


```

## 08036ff2

```c
// 08036ff2

undefined4 FUN_08036ff2(undefined4 param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  short sVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  short *psVar7;
  bool bVar8;
  bool bVar9;
  bool bVar10;
  
  iVar1 = FUN_080314ba();
  iVar4 = 0;
  if (param_2 == 0xa8) {
LAB_08037036:
    sVar3 = *(short *)((int)&DAT_08037b4a + iVar4) + (ushort)*(byte *)(iVar1 + 300) + -1;
  }
  else {
    uVar5 = 1;
    psVar7 = &DAT_08037b4c;
    do {
      iVar4 = (int)*psVar7;
      bVar8 = iVar4 == param_2;
      if (!bVar8) {
        uVar5 = uVar5 + 1;
        iVar4 = (int)psVar7[2];
      }
      bVar9 = iVar4 == param_2;
      if (!bVar8 && !bVar9) {
        uVar5 = uVar5 + 1;
        iVar4 = (int)psVar7[4];
      }
      bVar10 = iVar4 != param_2;
      if ((!bVar8 && !bVar9) && bVar10) {
        uVar5 = uVar5 + 1;
        iVar4 = (int)psVar7[6];
      }
      if (((bVar8 || bVar9) || !bVar10) || iVar4 == param_2) {
        iVar4 = uVar5 << 2;
        goto LAB_08037036;
      }
      uVar5 = uVar5 + 1;
      psVar7 = psVar7 + 8;
    } while (uVar5 < 0x31);
    uVar5 = 0;
    psVar7 = &DAT_08037578;
    while (*psVar7 != param_2) {
      iVar1 = (int)psVar7[2];
      uVar6 = uVar5 + 1;
      bVar8 = iVar1 == param_2;
      if (!bVar8) {
        uVar6 = uVar5 + 2;
        iVar1 = (int)psVar7[4];
      }
      bVar9 = iVar1 == param_2;
      uVar5 = uVar6;
      if (!bVar8 && !bVar9) {
        uVar5 = uVar6 + 1;
        iVar1 = (int)psVar7[6];
      }
      if ((bVar8 || bVar9) || iVar1 == param_2) break;
      uVar5 = uVar5 + 1;
      psVar7 = psVar7 + 8;
      if (0x173 < uVar5) {
        return 0;
      }
    }
    sVar3 = (&DAT_0803757a)[uVar5 * 2];
  }
  uVar2 = FUN_08037094(param_1,sVar3);
  return uVar2;
}


```

## 080484b0

```c
// 080484b0

void FUN_080484b0(int param_1,undefined2 param_2,undefined4 param_3,undefined4 param_4,
                 undefined4 param_5,undefined4 param_6,undefined4 param_7)

{
  int iVar1;
  
  *(undefined1 *)(param_1 + 0x9301) = 1;
  iVar1 = param_1 + 0x92dc;
  FUN_08047334(iVar1,param_2,param_3,param_4,param_5,param_6,param_7);
  FUN_0802eade(param_1 + 0x84f4,iVar1);
  FUN_08032316(iVar1);
  return;
}


```

## 0803eecc

```c
// 0803eecc

void FUN_0803eecc(int param_1,undefined4 param_2)

{
  FUN_08037212(*(undefined4 *)(param_1 + 8),
               (int)*(short *)(param_1 + (uint)*(ushort *)(param_1 + 0xea) * 2 + 0x20),param_2);
  return;
}


```

## 0803e5ac

```c
// 0803e5ac

undefined8
FUN_0803e5ac(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 local_10;
  
  local_10 = param_4;
  FUN_0804714c();
  *param_1 = DAT_0803e6d0;
  FUN_08041dfc(param_1 + 0xb0);
  FUN_08038ed0(param_1 + 0xe0);
  param_1[0xe0] = DAT_0803e6d4;
  *(undefined1 *)(param_1 + 0xeb) = 1;
  *(undefined2 *)((int)param_1 + 0x3ae) = 0;
  *(undefined2 *)(param_1 + 0xec) = 0;
  FUN_08041e1c(param_1 + 0xef);
  FUN_08041e1c(param_1 + 0xfb);
  FUN_08047230(param_1 + 0x107,param_1,*DAT_0803e6d8,DAT_0803e6d8[1]);
  uVar1 = DAT_0803e6e0;
  *param_1 = DAT_0803e6dc;
  FUN_0800dcd4(param_1 + 0x10b,uVar1,0x338,0x28);
  FUN_0802e716(param_1 + 0x213d);
  FUN_08047244(param_1 + 0x23dc);
  FUN_08047290(param_1 + 0x24b7);
  FUN_08047604(param_1 + 0x258f);
  FUN_08047e54(param_1 + 0x289b);
  FUN_08038ed0(param_1 + 0x297f);
  FUN_08038ed0(param_1 + 0x298a);
  local_10._0_2_ = 0xffff;
  FUN_0802df08(param_1 + 0x2995,&local_10);
  local_10 = CONCAT22(local_10._2_2_,0xffff);
  FUN_0802df08(param_1 + 0x29a0,&local_10);
  FUN_08047fd4(param_1 + 0x29ab,param_1,*DAT_0803e6e4,DAT_0803e6e4[1]);
  FUN_08047fe8(param_1 + 0x29af,param_1,*DAT_0803e6e8,DAT_0803e6e8[1]);
  FUN_08047ffc(param_1 + 0x29b3,param_1,*DAT_0803e6ec,DAT_0803e6ec[1]);
  FUN_08047fe8(param_1 + 0x29b7,param_1,*DAT_0803e6f0,DAT_0803e6f0[1]);
  return CONCAT44(local_10,param_1);
}


```

## 08047d80

```c
// 08047d80

undefined4 FUN_08047d80(int param_1,int param_2,int param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  undefined4 local_28;
  
  uVar1 = DAT_08047e3c;
  iVar2 = (0xa0 - param_3) * (*(int *)(param_1 + 0x70) - *(int *)(param_1 + 0x6c));
  iVar2 = (int)((ulonglong)((longlong)iVar2 * (longlong)DAT_08047e40) >> 0x20) + iVar2;
  iVar2 = (iVar2 >> 6) - (iVar2 >> 0x1f);
  local_28 = param_4;
  for (uVar4 = 0; uVar4 < *(byte *)(param_1 + 0x60); uVar4 = uVar4 + 1 & 0xff) {
    iVar3 = (short)uVar4 * 0xe4 + param_1;
    if (param_2 == iVar3 + 0x2e8) {
      *(int *)(param_1 + uVar4 * 4 + 0x88) = iVar2;
      FUN_08031134(iVar3 + 0x3b4,5,uVar1,iVar2);
      FUN_08032316(iVar3 + 0x37c);
      *(char *)(param_1 + 0x9c) = (char)uVar4;
      FUN_08047ba6(param_1,uVar4,0xa0 - param_3);
    }
    else {
      local_28 = CONCAT22(local_28._2_2_,0x38);
      FUN_080307bc(iVar3 + 0x314,&local_28);
      FUN_08032316(iVar3 + 0x314);
    }
  }
  return local_28;
}


```

## 08047c1a

```c
// 08047c1a

void FUN_08047c1a(int param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  bool bVar5;
  
  iVar1 = *(int *)(param_1 + 0x68);
  if ((param_3 <= iVar1) && (iVar1 = param_3, param_3 < 0)) {
    iVar1 = 0;
  }
  iVar2 = *(int *)(param_1 + 0x70);
  bVar5 = SBORROW4(iVar2,param_4);
  iVar3 = iVar2 - param_4;
  if (param_4 <= iVar2) {
    iVar2 = *(int *)(param_1 + 0x6c);
    bVar5 = SBORROW4(param_4,iVar2);
    iVar3 = param_4 - iVar2;
  }
  if (iVar3 < 0 != bVar5) {
    param_4 = iVar2;
  }
  iVar3 = param_1 + param_2 * 4;
  *(int *)(iVar3 + 0x74) = iVar1;
  *(int *)(iVar3 + 0x88) = param_4;
  iVar3 = ((iVar1 - *(int *)(param_1 + 100)) * 300) /
          (*(int *)(param_1 + 0x68) - *(int *)(param_1 + 100));
  iVar1 = *(int *)(param_1 + 0x70) - *(int *)(param_1 + 0x6c);
  iVar1 = (iVar1 / 2 + param_4 * 0x78) / iVar1;
  if (4 < param_2) {
    return;
  }
  iVar2 = param_2 * 0xe4 + param_1;
  piVar4 = (int *)(iVar2 + 0x2e8);
  FUN_08031134(iVar2 + 0x3b4,5,DAT_08047e3c);
  FUN_08032316(iVar2 + 0x37c);
  (**(code **)(*piVar4 + 0x34))
            (piVar4,(int)(short)((((short)iVar3 + 0x14) - *(short *)(iVar2 + 0x318)) -
                                *(short *)(iVar2 + 0x31c) / 2),
             (int)(short)(((0xa0 - (short)iVar1) - *(short *)(iVar2 + 0x31a)) -
                         *(short *)(iVar2 + 0x31e) / 2));
  FUN_08032316(piVar4);
  iVar1 = 0xa0 - iVar1;
  param_1 = param_1 + param_2 * 0x54;
  iVar3 = iVar3 + 0x14;
  if (param_2 != 0) {
    iVar2 = param_1 + 0x708;
    FUN_0804e410(iVar2,iVar3,iVar1);
    FUN_0804e354(iVar2);
    if (param_2 == 4) {
      return;
    }
  }
  param_1 = param_1 + 0x75c;
  FUN_0804e454(param_1,iVar3,iVar1);
  FUN_0804e354(param_1);
  return;
}


```

## 08047a8a

```c
// 08047a8a

void FUN_08047a8a(int param_1,int *param_2,int param_3,undefined4 param_4,undefined4 param_5,
                 undefined2 param_6)

{
  short sVar1;
  short sVar2;
  int iVar3;
  uint uVar4;
  int *piVar5;
  short *local_30;
  
  *(char *)(param_1 + 0x60) = (char)param_3;
  FUN_0802e652(param_1,param_6);
  *(int *)(param_1 + 100) = *param_2;
  *(int *)(param_1 + 0x68) = *param_2;
  if (param_3 == 0) {
    uVar4 = 0;
    goto LAB_08047b54;
  }
  piVar5 = param_2;
  iVar3 = param_3;
  do {
    if (*piVar5 < *(int *)(param_1 + 100)) {
      *(int *)(param_1 + 100) = *piVar5;
    }
    if (*(int *)(param_1 + 0x68) < *piVar5) {
      *(int *)(param_1 + 0x68) = *piVar5;
    }
    piVar5 = piVar5 + 2;
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  uVar4 = 0;
  iVar3 = param_1 + 0xb08;
  piVar5 = (int *)(param_1 + 0x9dc);
  local_30 = (short *)(param_1 + 0x2ec);
  do {
    *(undefined4 *)(param_1 + 0x6c) = param_4;
    *(undefined4 *)(param_1 + 0x70) = param_5;
    FUN_08047c1a(param_1,uVar4,*param_2,param_2[1]);
    sVar1 = *(short *)(param_1 + 0xd6);
    sVar2 = *(short *)(param_1 + 0xda);
    (**(code **)(*piVar5 + 0x2c))(piVar5,(int)(short)(*(short *)(param_1 + 0xd4) + *local_30));
    (**(code **)(*piVar5 + 0x30))(piVar5,(int)(short)(sVar2 + sVar1));
    FUN_08031134(iVar3,5,&DAT_08047b7c,*param_2);
    FUN_08032316(piVar5);
    uVar4 = uVar4 + 1;
    piVar5 = piVar5 + 0xe;
    iVar3 = iVar3 + 0xc;
    param_2 = param_2 + 2;
    local_30 = local_30 + 0x72;
  } while ((int)uVar4 < param_3);
  for (; (int)uVar4 < 5; uVar4 = uVar4 + 1 & 0xff) {
LAB_08047b54:
    *(undefined1 *)(param_1 + uVar4 * 0x38 + 0xa01) = 0;
    *(undefined1 *)(uVar4 * 0xe4 + param_1 + 0x30d) = 0;
  }
  return;
}


```

## 080307bc

```c
// 080307bc

undefined8 FUN_080307bc(int *param_1,undefined2 *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  short sVar2;
  int iVar3;
  undefined4 uStack_10;
  short local_c;
  short local_a;
  
  local_c = (short)param_4;
  local_a = (short)((uint)param_4 >> 0x10);
  *(undefined2 *)((int)param_1 + 0x26) = *param_2;
  uStack_10 = param_3;
  sVar2 = FUN_0803439c((int)param_1 + 0x26);
  (**(code **)(*param_1 + 0x38))(param_1,(int)sVar2);
  sVar2 = FUN_080343ea((int)param_1 + 0x26);
  (**(code **)(*param_1 + 0x3c))(param_1,(int)sVar2);
  FUN_08034438(&uStack_10,(int)param_1 + 0x26);
  iVar3 = FUN_0803439c((int)param_1 + 0x26);
  if (iVar3 <= local_c) {
    FUN_08034438(&uStack_10,(int)param_1 + 0x26);
    iVar3 = FUN_080343ea((int)param_1 + 0x26);
    if (iVar3 <= local_a) {
      uVar1 = 0;
      goto LAB_08030822;
    }
  }
  uVar1 = 1;
LAB_08030822:
  *(undefined1 *)((int)param_1 + 0x29) = uVar1;
  return CONCAT26(local_a,CONCAT24(local_c,uStack_10));
}


```

## 08031ccc

```c
// 08031ccc

void FUN_08031ccc(int param_1)

{
  undefined1 uVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  undefined2 uVar5;
  undefined2 uVar6;
  int iVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  int iVar10;
  byte local_2c;
  undefined1 local_2b;
  undefined1 local_2a;
  undefined1 local_29;
  undefined1 local_28 [2];
  undefined2 local_26 [3];
  
  FUN_080372f6(*(undefined4 *)(param_1 + 8),local_28,&local_29,&local_2c);
  FUN_08037372(*(undefined4 *)(param_1 + 8),&local_2a,&local_2b,local_26);
  FUN_0802d238(*(undefined4 *)(param_1 + 0xc),local_28[0],local_29,local_2c);
  FUN_0802d2f4(*(undefined4 *)(param_1 + 0xc),local_2a,local_2b,local_26[0]);
  iVar7 = FUN_080372b0(*(undefined4 *)(param_1 + 8));
  FUN_0802d29c(*(undefined4 *)(param_1 + 0xc),iVar7 != 0);
  iVar7 = FUN_080372c8(*(undefined4 *)(param_1 + 8));
  FUN_0802d2e4(*(undefined4 *)(param_1 + 0xc),iVar7 == 0);
  iVar7 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x135);
  FUN_0802d2c0(*(undefined4 *)(param_1 + 0xc),~-(uint)(iVar7 == 0) >> 0x1f);
  uVar8 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),1);
  uVar9 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x10d);
  FUN_0802d572(*(undefined4 *)(param_1 + 0xc),uVar1,uVar9,uVar8);
  iVar7 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0xb);
  if (iVar7 == 0) {
    FUN_0802d344(*(undefined4 *)(param_1 + 0xc),4,0);
    FUN_0802d344(*(undefined4 *)(param_1 + 0xc),0,0);
    FUN_0802d344(*(undefined4 *)(param_1 + 0xc),1,0);
    FUN_0802d344(*(undefined4 *)(param_1 + 0xc),2,0);
    FUN_0802d344(*(undefined4 *)(param_1 + 0xc),3,0);
    FUN_08037212(*(undefined4 *)(param_1 + 8),0x68,1);
  }
  else {
    FUN_0802d344(*(undefined4 *)(param_1 + 0xc),4,1);
    iVar7 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0xac);
    FUN_0802d344(*(undefined4 *)(param_1 + 0xc),1,iVar7 != 0);
    iVar7 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0xd7);
    FUN_0802d344(*(undefined4 *)(param_1 + 0xc),2,iVar7 != 0);
    iVar7 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0xdc);
    FUN_0802d344(*(undefined4 *)(param_1 + 0xc),3,iVar7 != 0);
  }
  iVar7 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x39);
  if (((iVar7 == 0) || (iVar7 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x39), iVar7 == 9)) ||
     (iVar7 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x39), iVar7 == 10)) {
    uVar8 = 0;
  }
  else {
    uVar8 = 1;
  }
  FUN_0802d344(*(undefined4 *)(param_1 + 0xc),0,uVar8);
  uVar8 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0xb);
  FUN_0802d398(*(undefined4 *)(param_1 + 0xc),uVar8);
  uVar8 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0xac);
  iVar7 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x10e);
  FUN_0802d3bc(*(undefined4 *)(param_1 + 0xc),0 < iVar7,uVar8);
  uVar8 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0xd7);
  iVar7 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x10e);
  FUN_0802d3ce(*(undefined4 *)(param_1 + 0xc),1 < iVar7,uVar8);
  uVar8 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0xdc);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x10f);
  FUN_0802d3e0(*(undefined4 *)(param_1 + 0xc),uVar1,uVar8);
  uVar8 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0xc);
  FUN_0802d440(*(undefined4 *)(param_1 + 0xc),uVar8);
  uVar8 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0xe);
  FUN_0802d48a(*(undefined4 *)(param_1 + 0xc),uVar8);
  iVar7 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0xb);
  if (iVar7 == 0) {
    uVar8 = 4;
  }
  else {
    uVar8 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x10);
  }
  FUN_0802d524(*(undefined4 *)(param_1 + 0xc),uVar8);
  uVar8 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),local_2c + 0x18);
  FUN_0802d79a(*(undefined4 *)(param_1 + 0xc),uVar8);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x39);
  FUN_0802d7a4(*(undefined4 *)(param_1 + 0xc),uVar1);
  uVar8 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x43);
  FUN_0802d7e8(*(undefined4 *)(param_1 + 0xc),uVar8);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x42);
  FUN_0802d81e(*(undefined4 *)(param_1 + 0xc),uVar1);
  uVar8 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x147);
  FUN_0802d7f4(*(undefined4 *)(param_1 + 0xc),uVar8);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x14c);
  FUN_0802db04(*(undefined4 *)(param_1 + 0xc),uVar1);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x10f);
  FUN_0802d91c(*(undefined4 *)(param_1 + 0xc),uVar1);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x111);
  FUN_0802d996(*(undefined4 *)(param_1 + 0xc),uVar1);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x121);
  FUN_0802db0e(*(undefined4 *)(param_1 + 0xc),uVar1);
  iVar7 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x10e);
  if (iVar7 < 1) {
    FUN_0802d998(*(undefined4 *)(param_1 + 0xc),1,0);
  }
  else {
    FUN_0802d998(*(undefined4 *)(param_1 + 0xc),1,1);
    iVar7 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x10e);
    if (1 < iVar7) {
      uVar8 = 1;
      goto LAB_08031fde;
    }
  }
  uVar8 = 0;
LAB_08031fde:
  FUN_0802d998(*(undefined4 *)(param_1 + 0xc),2,uVar8);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x14a);
  iVar7 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x147);
  iVar10 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x148);
  FUN_0802da54(*(undefined4 *)(param_1 + 0xc),(iVar7 * 100) / iVar10,uVar1);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x133);
  uVar5 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x134);
  FUN_0802d4a4(*(undefined4 *)(param_1 + 0xc),uVar5,uVar1);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),10);
  uVar2 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),9);
  uVar5 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),5);
  uVar6 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),3);
  uVar3 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),4);
  uVar4 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x10d);
  FUN_0802d18c(*(undefined4 *)(param_1 + 0xc),uVar4,uVar3,uVar6,uVar5,uVar2,uVar1);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),7);
  FUN_0802db2e(*(undefined4 *)(param_1 + 0xc),uVar1);
  uVar1 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x137);
  uVar2 = FUN_08036ff2(*(undefined4 *)(param_1 + 8),0x136);
  FUN_0802db54(*(undefined4 *)(param_1 + 0xc),uVar2,uVar1);
  return;
}


```

## 08037212

```c
// 08037212

undefined4 FUN_08037212(undefined4 param_1,int param_2,undefined4 param_3)

{
  undefined4 uVar1;
  byte *pbVar2;
  int iVar3;
  int iVar4;
  undefined2 *puVar5;
  short *psVar6;
  uint uVar7;
  
  iVar3 = FUN_080314ba();
  pbVar2 = DAT_08037558;
  uVar1 = DAT_0803754c;
  psVar6 = &DAT_08037b48;
  *DAT_08037558 = *(byte *)(iVar3 + 300);
  iVar3 = 0x31;
  while ((*psVar6 != param_2 ||
         (iVar4 = FUN_08011812(uVar1,psVar6[1] + (ushort)*pbVar2 + -1,param_3,5,1,1), iVar4 != 0)))
  {
    psVar6 = psVar6 + 2;
    iVar3 = iVar3 + -1;
    if (iVar3 == 0) {
      uVar7 = 0;
      puVar5 = &DAT_0803757a;
      do {
        if ((short)puVar5[-1] == param_2) {
          iVar3 = FUN_08011812(uVar1,*puVar5,param_3,5,1,1);
          if (iVar3 == 0) {
            return 1;
          }
          *(short *)(pbVar2 + 2) = (short)uVar7;
          *(short *)(pbVar2 + 6) = (short)param_2;
          *(undefined4 *)(pbVar2 + 8) = param_3;
          *(undefined2 *)(pbVar2 + 4) = *puVar5;
        }
        uVar7 = uVar7 + 1;
        puVar5 = puVar5 + 2;
      } while (uVar7 < 0x174);
      return 0;
    }
  }
  return 1;
}


```

## 080370c0

```c
// 080370c0

undefined4 FUN_080370c0(undefined4 param_1,int param_2)

{
  char *pcVar1;
  int iVar2;
  undefined4 uVar3;
  short *psVar4;
  undefined1 auStack_38 [4];
  char local_34;
  undefined4 local_30;
  undefined4 uStack_2c;
  undefined4 local_28;
  undefined4 uStack_24;
  undefined4 local_20;
  undefined4 uStack_1c;
  
  pcVar1 = DAT_08037550;
  if (*DAT_08037550 == '\0') {
    *DAT_08037550 = '\x01';
    iVar2 = FUN_080314ba();
    pcVar1[1] = *(char *)(iVar2 + 300);
  }
  uVar3 = DAT_0803754c;
  iVar2 = 0x31;
  psVar4 = &DAT_08037b48;
  do {
    if (*psVar4 == param_2) {
      FUN_0801167a(&local_30,uVar3,psVar4[1] + (ushort)(byte)pcVar1[1] + -1);
      local_28 = local_30;
      uStack_24 = uStack_2c;
      FUN_08014728(auStack_38,&local_28,5);
      if (local_34 != '\x06') goto LAB_08037156;
    }
    psVar4 = psVar4 + 2;
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  psVar4 = &DAT_08037578;
  iVar2 = 0x174;
  do {
    if (*psVar4 == param_2) {
      FUN_0801167a(&local_30,uVar3,psVar4[1]);
      local_20 = local_30;
      uStack_1c = uStack_2c;
      FUN_08014728(auStack_38,&local_20,5);
      if (local_34 != '\x06') {
LAB_08037156:
        uVar3 = FUN_08014734(auStack_38);
        return uVar3;
      }
    }
    psVar4 = psVar4 + 2;
    iVar2 = iVar2 + -1;
    if (iVar2 == 0) {
      return 9;
    }
  } while( true );
}


```

## 0803716e

```c
// 0803716e

undefined4 FUN_0803716e(undefined4 param_1,int param_2)

{
  char *pcVar1;
  undefined4 uVar2;
  int iVar3;
  short *psVar4;
  undefined1 auStack_38 [4];
  char local_34;
  undefined4 local_30;
  undefined4 uStack_2c;
  undefined4 local_28;
  undefined4 uStack_24;
  undefined4 local_20;
  undefined4 uStack_1c;
  
  pcVar1 = DAT_08037554;
  if (*DAT_08037554 == '\0') {
    *DAT_08037554 = '\x01';
    iVar3 = FUN_080314ba();
    pcVar1[1] = *(char *)(iVar3 + 300);
  }
  uVar2 = DAT_0803754c;
  iVar3 = 0x31;
  psVar4 = &DAT_08037b48;
  do {
    if (*psVar4 == param_2) {
      FUN_080116e6(&local_30,uVar2,psVar4[1] + (ushort)(byte)pcVar1[1] + -1);
      local_28 = local_30;
      uStack_24 = uStack_2c;
      FUN_08014728(auStack_38,&local_28,5);
      if (local_34 != '\x06') goto LAB_08037162;
    }
    psVar4 = psVar4 + 2;
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  psVar4 = &DAT_08037578;
  iVar3 = 0x174;
  do {
    if (*psVar4 == param_2) {
      FUN_080116e6(&local_30,uVar2,psVar4[1]);
      local_20 = local_30;
      uStack_1c = uStack_2c;
      FUN_08014728(auStack_38,&local_20,5);
      if (local_34 != '\x06') {
LAB_08037162:
        uVar2 = FUN_08014734(auStack_38);
        return uVar2;
      }
    }
    psVar4 = psVar4 + 2;
    iVar3 = iVar3 + -1;
    if (iVar3 == 0) {
      return 999;
    }
  } while( true );
}


```

## 08047ba6

```c
// 08047ba6

longlong FUN_08047ba6(int param_1,int param_2,int param_3,uint param_4)

{
  int iVar1;
  uint uVar2;
  
  if (param_2 != 0) {
    iVar1 = (short)param_2 * 0x54 + param_1;
    uVar2 = (uint)*(short *)(iVar1 + 0x73c);
    iVar1 = iVar1 + 0x708;
    FUN_0804e410(iVar1,(int)((uVar2 + ((uVar2 & 0xfffff) >> 0xf)) * 0x10000) >> 0x15,0xa0 - param_3)
    ;
    FUN_0804e354(iVar1);
  }
  if (param_2 < 4) {
    param_1 = (short)param_2 * 0x54 + param_1;
    iVar1 = param_1 + 0x75c;
    uVar2 = (uint)*(short *)(param_1 + 0x78c);
    FUN_0804e454(iVar1,(int)((uVar2 + ((uVar2 & 0xfffff) >> 0xf)) * 0x10000) >> 0x15,0xa0 - param_3)
    ;
    FUN_0804e354(iVar1);
    return CONCAT44(param_4,1);
  }
  return (ulonglong)param_4 << 0x20;
}


```

## 08047b80

```c
// 08047b80

undefined4 FUN_08047b80(int param_1,int param_2,uint *param_3)

{
  uint uVar1;
  
  for (uVar1 = 0; uVar1 < *(byte *)(param_1 + 0x60); uVar1 = uVar1 + 1 & 0xff) {
    *(undefined4 *)(param_2 + uVar1 * 4) = *(undefined4 *)(param_1 + uVar1 * 4 + 0x88);
  }
  *param_3 = (uint)*(byte *)(param_1 + 0x60);
  return 1;
}


```

## 08043a74

```c
// 08043a74

uint FUN_08043a74(int param_1,uint param_2,undefined4 param_3,uint param_4)

{
  ushort uVar1;
  bool bVar2;
  uint uVar3;
  ushort *puVar4;
  int iVar5;
  uint local_28;
  
  if (10 < param_2) {
    return param_4;
  }
  puVar4 = &DAT_08043c2e;
  iVar5 = 0xb;
  local_28 = param_4;
  do {
    if ((byte)puVar4[-1] == param_2) {
      uVar1 = *puVar4;
      local_28 = (uint)uVar1;
      FUN_080313a4(param_1 + 0xed8,local_28);
      bVar2 = uVar1 == 0xc || uVar1 == 0xd;
      *(bool *)(param_1 + 0xb0d) = bVar2;
      *(bool *)(param_1 + 0xb45) = bVar2;
      FUN_08032316(param_1 + 0xae8);
      FUN_08032316(param_1 + 0xb20);
    }
    puVar4 = puVar4 + 2;
    iVar5 = iVar5 + -1;
  } while (iVar5 != 0);
  uVar3 = FUN_08032316(param_1 + 0xed8,local_28);
  return uVar3;
}


```

## 08043b44

```c
// 08043b44

void FUN_08043b44(int param_1,int param_2,int param_3,int param_4)

{
  undefined1 uVar1;
  char *pcVar2;
  int local_10;
  undefined4 uStack_c;
  
  if (param_3 == 5 && param_4 == 0) {
    local_10 = param_2 + ((uint)(param_2 * 0x8889) >> 0x15) * -0x3c;
    if (local_10 < 10) {
      pcVar2 = s__d_0_d_08043c1c;
    }
    else {
      pcVar2 = s__d__d_08043c0c;
    }
    FUN_08031134(param_1 + 0x13c6,6,pcVar2,(uint)(param_2 * 0x8889) >> 0x15);
    uVar1 = 1;
  }
  else {
    uVar1 = 0;
  }
  *(undefined1 *)(param_1 + 0xc95) = uVar1;
  FUN_08032316(param_1 + 0xc70,local_10,uStack_c);
  return;
}


```

