# MULTIPASS-19 — WHOLE-SOFTWARE / SOURCE-CROSSCHECK / CONTRADICTION AUDIT — 2026-11-20

## Scope

This run continued the chronological audit of `analiza/` instead of restarting from summaries. It re-read the current 2026-11-20 continuity checkpoints, the principal 2026-11-19 master/CO/UI/bitmap/TouchGFX traces, and cross-checked the current model against the official Estyma/Tekla installer documentation.

Firmware source of truth:
- FW2213TK_kopia.bin
- SHA-256: 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071
- size: 0x1F0000
- bitmap/runtime asset base: 0x08010000
- bitmap descriptor table: 0x54450
- 188 bitmap resources, 000..187

## 1. Chronological coverage result

The current `analiza/` tree was enumerated before this run. The analysis was continued in chronological order:
- 2026-11-18 foundation/UI/CO/TouchGFX notes
- 2026-11-19 raw firmware, bitmap, CO instance, Home, TouchGFX renderer, hopper, configuration, continuity/master notes
- 2026-11-20 corrections, architecture reset, 6154, 21-menu model, 47290 disambiguation, Home geometry, graph/fan families and source-of-truth audits

Important: the repository contains 143 files under `analiza/`. Tool output limits prevent presenting all files in one model-visible response. Batches were therefore read sequentially. This document records the consolidated result; it does NOT claim that a single tool response contained all 143 files.

## 2. Current source-of-truth hierarchy

1. raw firmware / direct disassembly
2. direct extracted firmware data/assets
3. official Estyma/Tekla documentation as functional/terminology cross-check
4. direct user observations/screenshots
5. legacy project implementation

Any older hypothesis contradicted by later firmware evidence is rejected.

## 3. Critical stale-hypothesis audit

### Rejected
- 47290 = Home bottom bar
- 47290 = blower graph
- 47290 = proven language selector
- 056/057 = 151/152
- +0x12B = CO instance
- +0x158 = CO number
- 0x3505 = directly proven CO count
- 0x2105 = directly proven constructor of CO objects
- 370A 1/2/3 = bitmap 011/012/013 by numeric coincidence
- 0x0801AB7E = executable function
- DAT_08046CC4 = proven vtable
- old 0x08042146 -> 0x38130 chain as final proof
- FUN_08038ED0 = proven WheelSelectorExtra constructor
- generated Home render = firmware geometry/color proof

### Current hard/strong model
- +0x12B = object class/type; +0x12C = active instance dimension.
- FUN_08036FF2 implements family-of-4 + instance - 1.
- record engine stride = 0x2C.
- 188 bitmap table is real TouchGFX BitmapData-style RGB565 + optional A8.
- 056 is hard-proven in graph point rendering.
- 151/152 are hard-proven in FUN_08047290 six-slot selector.
- graph uses five points for 0x2261..0x2265.
- second five-point family is 0x2268/226E/226F/2275/227A.
- TypedText 183 = PL "Wentylator wspomagający [%]"; ID 199 = "Moc dmuchawy modulacja [%]".
- 21 main-menu row family is now closed as a 21-slot structure with access-dependent construction of slots 15..20.
- 6154 = access level 3 and adds real +/- controls to 17 UI branches.

## 4. Official documentation cross-check

Official installer manual:
https://estyma.pl/wp-content/uploads/2020/02/InstrukcjaTeklaPelletInstalator_PL.pdf

Relevant hard external facts:

### Access levels
The manual states that menu is divided into access levels and that parameters are hidden depending on the selected level. It explicitly documents level 0 and installer code 0900. This independently supports the firmware model of access-gated widget construction. Firmware additionally closes 0999 -> level 2 and 6154 -> level 3.

### Configuration persistence/restart
The manual states that after configuration changes, especially module-type/source changes, the device must be power-cycled after allowing time for settings to be saved. This supports modeling configuration changes as persistent state + restart/initialization boundaries, not just transient UI state.

### Autoconfiguration
The manual's configuration section includes autoconfiguration and describes automatic detection of connected modules/devices. This strongly supports keeping hardware/module discovery separate from the functional configuration parameters.

### Heating-circuit count
The installer menu explicitly contains "Ilość obwodów grzewczych" and says it determines the number of CO circuits. This is a strong semantic cross-check for the firmware's separate Heating configuration parameter 0x2105 (range 0..4), but it is NOT a substitute for the missing direct firmware fan-out.

### Profiles
The manual documents profiles with different system compositions, including:
- Profil 1: CO + CWU + Bufor
- Profil 2: CO1 + CO2 + CWU
- Profil 3: CO1 + CO2 + CWU + Bufor

This independently confirms that profile selection and number/type of circuits are related but distinct configuration dimensions.

### Blower curves
Section 4.2.1 describes a modifiable blower-speed curve as a function of burner power. The same manual separately lists "Wentylator wspomagający" and states that its characteristic is as in 4.2.1. This matches the firmware's two separate five-point parameter families.

### Automatic firmware update
The manual says microSD firmware update starts automatically after power-on, reports start/end via LEDs, and returns to the Home screen after update. Therefore the hypothesis that the six-slot 47290 component is an interactive update-language screen is currently weak and must not be assumed.

### Parameter copy
The manual says settings can be copied between two IgneoTouch controllers over CAN and the visible count runs to about 570 parameters. This is important architecture evidence: the panel contains a large parameter/configuration layer spanning CAN, persistence and UI; it should not be modeled as a small fixed Home-only application.

## 5. New architecture conclusion from the cross-check

The strongest current model is a multi-axis configuration system:

```
hardware/module discovery
  0x3500 / 0x3502 / 0x350B / related variant fields
        |
        v
hardware/profile variant
        |
        +-----------------------------+
        |                             |
functional configuration          object/class selection
0x2105..0x2108                    +0x12B / +0x12C
        |                             |
        v                             v
system capabilities             instance-aware parameter engine
        |                             |
        +-------------+---------------+
                      |
                      v
                screen/menu resolver
                      |
               access-level gates
                      |
                host/content tree
                      |
          widgets/resources/TypedText
                      |
              touch/callback/write
                      |
                 CAN/storage
```

This architecture is more consistent with all current evidence than a single "number of CO -> create N widgets" mechanism.

## 6. 0x2105 status — refined

Current status:
- HARD: parameter 0x2105 exists, name "Heating configuration", u8, range 0..4, storage 0x20021FAF.
- HARD: panel index 0x10F maps to 0x2105.
- HARD: 0x10F is consumed in FUN_08031CCC and affects UI state/graphics.
- STRONG/CORRELATION: official manual has "Ilość obwodów grzewczych" with exactly the expected 0..4 semantic space.
- OPEN: exact firmware fan-out from 0x2105 to activation/count of CO instances.

Do not promote 0x2105 to CLOSED "CO count" until a direct data-flow path is found.

## 7. 0x3505 / 0x10E status — refined

Current firmware catalog calls 0x3505 "Outside temperature sensor configuration", range 0..2.

FUN_08031CCC definitely uses panel index 0x10E as two thresholds (>0, >1) for UI elements.

An older 2026-11-19 note proposed a 0x10E -> 0x38130 -> +0x12C instance path. Later repository audits explicitly withdrew the old 0x08042146 evidence because that address lies outside the recognized FUN_0804204A boundary. Therefore that chain must NOT be used as current proof.

Current status:
- 0x3505 semantic from parameter catalogue: STRONG/HARD DATA.
- 0x10E thresholded UI fan-out: HARD.
- 0x10E -> CO instance selector: OPEN.
- old 0x38130 proof: REJECTED/STALE.

## 8. CO instance engine — current invariant

The following is safe to implement in the behavioral model:

```
parameter family base
        +
(active instance - 1)
        =
concrete family member
```

For example:
- 0x2032 + instance 1 - 1 = 0x2032
- 0x2032 + instance 2 - 1 = 0x2033
- 0x2032 + instance 3 - 1 = 0x2034
- 0x2032 + instance 4 - 1 = 0x2035

This is independent of the unresolved question of what system configuration activates which instances.

## 9. Graph/fan family — integrated conclusion

The firmware contains a reusable five-point graph mechanism.

Family A:
- 0x2261, 0x2262, 0x2263, 0x2264, 0x2265
- points at 20/40/60/80/100% burner power
- graph point resource 056
- host/content around +0x84F4 / +0x963C

Family B:
- 0x2268, 0x226E, 0x226F, 0x2275, 0x227A
- separate five-point exhaust/extra-fan characteristic family
- same general graph/update mechanism

Direct firmware string branch:
- TypedText 183 = Wentylator wspomagający [%]
- TypedText 199 = Moc dmuchawy modulacja [%]

This strongly supports the manual's terminology and confirms that the second family is not a fictional or generic ten-point graph.

OPEN:
- exact gate selecting family B,
- exact screen factory/content ID for family B,
- exact direct graph writer for bitmap 057.

## 10. 47290 — current model

Hard:
- six slots
- X=100
- Y=50+34*slot
- resources 151/152
- labels supplied through caller object +0x08 -> six u16 TypedText IDs
- separate from graph 056/057

Current hypothesis:
- reusable six-slot selector/list component in a dynamic content page.

Language:
- selector 90 = Language
- parameter ID 3 = Language
- eight language TypedText tables
- 47290 -> Language is OPEN and currently leaning negative because:
  - six slots != eight compiled language tables
  - current traced 0803EC18 context is parameter/model-heavy and resolves 0x4A..0x53
  - no direct selector-90 -> 47290 navigation edge is closed.

Update:
- official manual describes automatic update, not interactive update-language selection.
- therefore 47290 = updater-language screen is currently WEAK/OPEN.

## 11. Home geometry — current invariant

Hard:
- coordinate space 480x272
- geometry helper FUN_08030358
- 47290 vertical geometry
- graph central region (35,50,335,180)
- graph layers initially 480x200
- several exact CO2 widget rectangles
- Home visual resource correlations: 115=settings/power tile, 144=CO1 icon, 174=CWU icon

OPEN:
- actual Home factory/navigation entry
- exact parent geometry of 115/144/174
- full tile grid
- touch rectangles vs visual rectangles
- runtime placement of several reusable components

## 12. Bitmap renderer invariant

TouchGFX renderer `FUN_0805570E` proves:
- linear RGB565 source
- separate A8 source
- 16-bit framebuffer
- direct row-major pixel traversal
- RGB565 masks 0xF800/0x07E0/0x001F
- alpha blending in RGB565

Therefore the bitmap extraction baseline is CLOSED:
- no hidden tiling/codec
- no RGB888 conversion in firmware bitmap path
- file offset = runtime pointer - 0x08010000

The remaining bitmap gap is artifact persistence: the complete 188 PNG set is documented but not confirmed as individually committed GitHub files.

## 13. Highest-value next attack

The next run should NOT spend time rediscovering closed areas.

Priority order:

1. **0x2105 / 0x10F full read fan-out**
   - find every raw read of RAM 0x20021FAF
   - classify caller/context
   - identify whether reads reach configuration resolver, module variant, object selection or only UI
   - search for writes/persistence/commit path

2. **0x10E / 0x3505 full read fan-out**
   - find every consumer of the corresponding storage
   - separate outside-sensor logic from any circuit-availability logic
   - do not use the withdrawn 0x38130 chain

3. **C064 indirect call**
   - recover vtable/factory path
   - recover DAT_0803C218 raw 108 bytes
   - identify which param_2 values produce classes 1..4

4. **47290 label source**
   - writer of object+0x08
   - recover six u16 IDs
   - decode all eight language tables
   - independently trace selector 90 navigation

5. **Home assets**
   - indirect resource resolution for 115/144/174
   - parent geometry and callback chain

6. **graph family B**
   - gate and page factory for 0x2268..0x227A
   - 057 writer

7. **370A**
   - full consumer graph of RAM 0x20021FA6
   - resolve selector -> resource index without numeric assumptions

## 14. Required persistence

This checkpoint is a technical summary, not a raw transcript. It records:
- what was re-read,
- what was cross-checked,
- what was corrected,
- what is closed,
- what remains open,
- next attack order.

Next major run should append another continuity/checkpoint file rather than overwrite history.
