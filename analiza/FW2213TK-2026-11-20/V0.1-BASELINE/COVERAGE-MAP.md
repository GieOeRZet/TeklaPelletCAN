# V0.1 Coverage Map

## Confirmed regions
- 0x000000: Cortex-M vectors
- 0x08B4CC: IAR init table
- 0x093208: Reset_Handler
- 0x08F74C: __cmain
- 0x062D82: main
- 0x02F008: 188 parameter records
- 0x02BDF0..0x02DB54: HomeView core
- 0x031CCC..0x0320BE: HomeView update logic
- 0x032110..0x032212: Home navigation callbacks (partial)
- 0x036FF2..0x037540: parameter read/write/search
- 0x037578: main CAN mapping table
- 0x037B48: special CAN mapping table
- 0x03F008: parameter dictionary
- 0x057C80..0x058220: runtime/queue support (partial)
- 0x060B80..0x061940: CAN peripheral/config (partial)
- 0x05AE08: TypedText EN pointer table
- 0x05BD80: TypedText PL pointer table
- 0x064A2C+: language resources
- 0x06F58C: known option table
- 0x0185B0..0x018630: range check
- 0x018840..0x01908E: buffer/register/time
- 0x039250..0x03933E: date/time conversion

## Large remaining areas
The global scan shows substantial executable/application/framework regions around:
- 0x30000..0x3A000
- 0x40000..0x5B000
- 0x5E000..0x65000
- 0x67000..0x7D000
- 0x80000..0xA0000
plus scattered runtime/data/library regions through the remainder of the 0x1F0000 image.

These are coverage gaps, not claims that every byte is code.

## Required classification
Every range must eventually be classified:
CODE_CONFIRMED / CODE_LIKELY / DATA_POINTER_TABLE / STRING / BITMAP_ASSET / COMPRESSED / UNKNOWN.

Linear objdump is insufficient for this step.