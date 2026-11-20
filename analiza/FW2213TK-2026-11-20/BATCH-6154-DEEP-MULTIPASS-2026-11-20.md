# BATCH-6154 deep multipass checkpoint

A deeper 2026-11-20 pass expanded the 6154 analysis. Full report:

- `analiza/FW2213TK-2026-11-20/BATCH-6154-DEEP-MULTIPASS-2026-11-20.md`

Key closure: the 17 level-3 sites are 17 distinct wrapper functions, each directly called once, all implementing the same conditional insertion of `parent+0x23C` when `context+0x158 >= 3`. `FUN_0802FB04` independently proves +0x23C is the increment control and +0x284 the decrement control over +0x60 bounded by +0x64. Thus level 3 changes the actual widget tree.

Still OPEN: exact screen/title, parameter/CAN ID, +0x60/+0x64 source, and configuration reachability for each of the 17 instances.
