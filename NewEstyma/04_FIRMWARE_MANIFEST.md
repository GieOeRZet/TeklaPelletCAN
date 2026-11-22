# NewEstyma — FIRMWARE MANIFEST

## Canonical firmware
Filename: FW2213TK_kopia.bin
Size: 2,031,616 bytes (0x1F0000)
SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

## Address mapping
RAW 0x000000 -> PROJECT 0x08000000
PROJECT = 0x08000000 + RAW
RE_PACK = PROJECT + 0x10000

## Integrity gate
Run:
sha256sum FW2213TK_kopia.bin

Expected:
1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

If different, do not make byte-level claims until the source is identified.

## Current source availability
The canonical BIN is available in the current analysis environment as:
 /mnt/data/FW2213TK_kopia.bin

The connected GitHub API exposes text/blob/tree operations but no direct binary upload action. Therefore the physical BIN must be committed from a normal Git/Git LFS capable client if required in Git itself. This manifest intentionally does not create a fake text .bin.

## Source precedence
1. canonical BIN bytes
2. reproducible runtime trace from canonical BIN
3. RAW disassembly generated from canonical BIN
4. decompilation/export
5. earlier summaries

Earlier summaries never override direct BIN evidence.
