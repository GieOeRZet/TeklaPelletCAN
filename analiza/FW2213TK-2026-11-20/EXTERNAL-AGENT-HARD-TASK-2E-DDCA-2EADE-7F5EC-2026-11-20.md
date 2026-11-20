# TeklaPelletCAN — HARD TASK PACK — FUN_0802DDCA / FUN_0802EADE / FUN_0807F5EC
Date: 2026-11-20

## Mission
Second-agent task. Do NOT rely on prior semantic labels. Reconstruct and challenge the UI/runtime architecture from the supplied evidence.

### Priority A — FUN_0802DDCA (66 bytes)
We need the COMPLETE original Ghidra/decompiled body, not a guessed prototype.
Known size: 66 bytes at 0x0802DDCA.
Known callers:
- FUN_08043A36(parent+0xF74, &0xA8, &0xA9, &icon, &icon)
- FUN_08047604(..., &0xA8, &0xA9, &5, &5)
- FUN_08047604(..., &0xA8, &0xA9, &3, &3)

Caller code:
```c
void FUN_08043A36(int param_1,int param_2) {
  undefined2 local_1c [2], local_18 [2], local_14 [2], local_10 [4];
  if (param_2 == 1) local_14[0] = 0xb6; else local_14[0] = 0xb7;
  local_18[0] = 0xa9;
  local_1c[0] = 0xa8;
  local_10[0] = local_14[0];
  FUN_0802ddca(param_1 + 0xf74,local_1c,local_18,local_14,local_10);
  FUN_08032316(param_1 + 0xf74);
}
```

Relevant second caller:
```c
local_28[0]=5; local_2c[0]=5; local_30=0xa9; local_34._0_2_=0xa8;
FUN_0802ddca(piVar4,&local_34,&local_30,local_2c,local_28);
...
local_28[0]=3; local_2c[0]=3; _local_30=CONCAT22(...,0xa9);
local_34=CONCAT22(...,0xa8);
FUN_0802ddca(param_1+0x2f2,&local_34,&local_30,local_2c,local_28);
```

Questions:
1. Recover exact body from raw Thumb if available.
2. Determine exact ABI/signature and whether arguments are pointers to 16-bit bitmap IDs.
3. Identify all writes/virtual calls made by the function.
4. Prove whether it is ButtonWithIcon::setBitmaps-like behavior or a generic bitmap setter.
5. Identify whether the four arguments map to released/pressed/disabled/selected states, and whether duplicated icon IDs imply state aliasing.
6. Trace resulting vtable calls to the actual widget implementation.

### Priority B — FUN_0802EADE (340 bytes)
Known size: 340 bytes at 0x0802EADE.
Call pattern strongly indicates host/content switching:
- 08048468: FUN_0802EADE(parent+0x84F4, parent+0x8F70)
- 080484B0: FUN_0802EADE(parent+0x84F4, parent+0x92DC)
- 080484F0: FUN_0802EADE(parent+0x84F4, parent+0xA26C)
- 08048520: FUN_0802EADE(parent+0x84F4, parent+0x963C)
- 0803C064 case 0xF: FUN_0802EADE(ctx+0x37B0, ctx+0x422C)

Questions:
1. Recover COMPLETE body.
2. Determine exact object types of both arguments from field accesses/vtables.
3. Find whether it removes an old child, inserts a new child, changes visibility, reparents, or does multiple operations.
4. Identify all virtual methods invoked and map each vtable slot to semantic operation.
5. Determine ownership/lifetime: does host own content? Is old content detached but retained?
6. Determine whether this is a TouchGFX Container/ScrollableContainer/CustomContainer replacement primitive.
7. Compare all five call sites and infer what is invariant vs caller-specific.
8. Trace caller 08048520 backwards into graph creation and caller 0803C064 case 0xF into navigation/content selection.
9. Produce a memory-layout diagram for host and content objects with offsets proven from code.

### Priority C — FUN_0807F5EC
Only pointer evidence is currently known:
- registry type byte 5 records at table 0x0803F008 can carry pointer 0x0807F5EC.
- Searchable decompiled repo does not contain standalone body.
Questions:
1. Find every direct BL/BLX/function-pointer reference in raw firmware.
2. Determine whether 0x0807F5EC is a constructor, factory, resolver, callback, or vtable entry.
3. Trace all incoming and outgoing edges.
4. If it is a constructor/factory, recover object size, vtable, field initialization, and all downstream users.
5. Connect it to registry keys 0x47/0x48 without assuming semantics.
6. Identify exact object/class and screen/content if provable.
7. Compare against other type-5 registry records to identify the registry schema.

### Priority D — registry family 0x47 / 0x48
Hard evidence from FUN_0803EC18:
- reads key from table 0x0803F008.
- record type byte == 5.
- key 0x47 -> resolver indices 0x4A..0x4E -> parameters 0x2261..0x2265.
- key 0x48 -> resolver indices 0x4F..0x53 -> parameters 0x2268,0x226E,0x226F,0x2275,0x227A.
- both call FUN_08048520(ctx+0x1C, &local_48, 5, 0).
- X = 20,40,60,80,100.
- local_4C = 0x8E for 0x47, 0x7E for 0x48.

Critical: do not label 0x8E/0x7E as title/TypedText without proof.

### Priority E — hardest cross-check
Independently determine whether the semantic chain is:
registry key -> constructor/factory -> graph content -> dynamic host -> graph points -> parameter family
or whether 0x47/0x48 select something else.
Find the actual Family-B hardware/configuration gate. Do NOT reuse resolver 0x68/parameter 0x300B as that gate; that hypothesis is REJECTED.

## Evidence classification
Every conclusion must be marked HARD / STRONG / INFERENCE / OPEN / REJECTED.
Do not use numeric proximity as semantic proof.
Do not resurrect rejected hypotheses without new direct evidence.

## Existing hard snippets
The repository contains:
- raw-snippets/0803ec18-decompiled.c.txt
- raw-snippets/08043a36-decompiled.c.txt
- raw-snippets/08047604-decompiled.c.txt
- raw-snippets/08048468-decompiled.c.txt
- raw-snippets/080484b0-decompiled.c.txt
- raw-snippets/080484f0-decompiled.c.txt
- raw-snippets/08048520-decompiled.c.txt
- raw-snippets/0803c064-decompiled.c.txt
