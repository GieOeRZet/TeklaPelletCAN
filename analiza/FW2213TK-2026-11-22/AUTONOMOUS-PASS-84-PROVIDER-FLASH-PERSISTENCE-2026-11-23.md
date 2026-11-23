# AUTONOMOUS PASS 84 — PROVIDER 0x080A31F0 / FLASH PERSISTENCE — 2026-11-23

## 1. Provider vtable
Runtime vtable 0x080A31F0 / PROJECT 0x080931F0 / RAW 0x931F0:
- slot 0 -> PROJECT 0x0800DB31 / RAW 0xDB30
- slot 1 -> PROJECT 0x0800DB79 / RAW 0xDB78
- slot 4 -> PROJECT 0x080617FF / RAW 0x517FE

## 2. Slot 0 = persistent GET
RAW 0xDB30 takes an index/key in r1, transforms it to an internal word-address pair, calls FUN_08014BBA twice and combines two u16 results into one u32 at [r2]. The return value reports whether the second lookup succeeded.

FUN_08014BBA is not a generic CAN read. It searches a flash-resident table:
- flash base 0x08008000;
- secondary flash region 0x0800C000;
- runtime bookkeeping around 0x200247D4 / 0x200248D8;
- sentinel 0xEEEE and error/status 0xAB are handled explicitly.

Therefore provider slot 0 is a persistence-layer GET, not a CAN provider.

## 3. Slot 1 = persistent SET / typed encoding
RAW 0xDB78 reads a type selector from stack and supports selectors 1..5. Selectors 1..3 encode the supplied value as byte/halfword/word forms; selectors 4..5 use the same two-u16 split representation used by the persistent store. The actual store path is FUN_08014C14 -> FUN_08014CC0 after validation.

FUN_08014CC0 validates the persistent flash state and searches existing entries before committing. It uses FUN_08014C58 to validate the flash area and then FUN_08014888 for the flash-state transition/commit machinery.

Thus the provider vtable is the parameter manager's nonvolatile persistence backend.

## 4. Constructor
RAW 0xDB08 installs vptr 0x080A31F0 and calls FUN_08014870 + FUN_08014A70, then clears a flag in the global flash-state object. This is consistent with provider initialization/recovery before parameter-manager use.

## 5. Slot 4
PROJECT 0x080617FF / RAW 0x517FE changes the object's vptr to 0x080A3200 and initializes subobjects at +0x24 and +0x10 through an indirect method. It is a state-transition/initialization method, not the normal GET/SET data path. Full semantic name remains OPEN.

## 6. Conclusion
Provider 0x080A31F0 is now functionally classified as the nonvolatile flash persistence backend behind parameter manager 0x20008D84. CAN transport remains above the manager; provider GET/SET are local persistence operations.