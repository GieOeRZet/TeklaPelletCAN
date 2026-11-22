# Platform-independent recovered parameter model

This module is an executable software representation of the parts of the Estyma
parameter engine that are already closed by firmware evidence.

Closed:
- record stride 0x2C
- PID +0x08
- storage binding +0x0C
- runtime type +0x10
- minimum +0x14
- maximum +0x1C
- default/reset +0x24
- typed descriptor: 4-byte payload + 1-byte type
- type 1/2/3/4/5 = U8/U16/U32/S16/S32
- status 6 = above maximum
- status 7 = below minimum
- status 5 = type/range-width rejection
- family instance resolution = base + instance - 1
- 49 family positions + 372 singleton positions = 568 logical mapper positions

Explicitly not guessed:
- semantics of adjacent R+0x2C/R+0x30 sidecar state
- full 49 family base list
- full 372 singleton list
- CAN publication after local update
- complete UI resource binding
