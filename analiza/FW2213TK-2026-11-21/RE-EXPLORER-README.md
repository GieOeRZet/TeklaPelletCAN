# OpenAI RE Explorer

The project received `FW2213TK_RE_PACK (1).zip`, an indexed RE package for the authoritative firmware. OpenAI created `OPENAI_RE_EXPLORER.zip` to query windows, literals, BL calls and indexed disassembly.

## Rule
RAW BIN is the source of truth. RE pack is an index. Critical disassembly must be verified against raw bytes.

## Current use
Use the explorer to accelerate OPEN-1 around `0x200114C0`, `0x20008D60`, `0x20008D84`, `0x200244EC`, `0x2002466C`, `0x0800FF44`, `0x0800FF50`, `0x0806E59C`, `0x080629FC`, and vtable `0x08094508`.

Do not treat automatic disassembly as proof of function boundaries or data/code classification.
