# ChatGPT SII — Stage 2 handoff

Owner: ChatGPT
Branch: ccr-be8a1bcb-5t76j0-chatgpt-sii

Canonical firmware:
- FW2213TK_kopia.bin
- SHA-256 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071

Stage 2 dynamic evidence:
- SIEĆ: node 0x56/0x57/0x5B/0x45 plus 0x40/0x46/0x78/0x50/0x54/0x55/0x7A..0x7D; 8-row limit; identity does not determine name; heartbeat alone creates row; 10000-tick persistence.
- INFO: 0x3664 source proven by pre-entry storage change; L0/L1 header variant; no live PID reads during render; 0x3665 and 0x2170 remain unresolved.
- INTERNET: SSID 24-char editor, 4 chars/u32, 0x3730..0x3735, backspace, cancel paths, full character-set lengths/content, PASSWORD PID 0x3736, WiFi 0x373E, remote changes 0x3741, persistence after re-entry.

Repo data:
- analiza/FW2213TK-2026-11-24/data/ui_model/siec/chatgpt_dynamic_stage2.json
- analiza/FW2213TK-2026-11-24/data/ui_model/info/chatgpt_dynamic_stage2.json
- analiza/FW2213TK-2026-11-24/data/ui_model/internet/chatgpt_dynamic_stage2.json
- analiza/FW2213TK-2026-11-24/CHATGPT-SII-STAGE2.md

Classification:
Results are recorded as STRONG dynamic evidence because the local execution used a reconstructed runtime core from repository tools. Do not silently promote to FACT-DYNAMIC until the exact repo acceptance harness is rerun.

OPEN:
- exact-harness rerun and repo-native PNG evidence
- INFO full PID diff / exact boiler-name and PIN source
- INTERNET full PASSWORD matrix / SERIAL-PIN rationale / 0x5B correlation / header status source
- SIEĆ SW formatting / 0x57 SW omission / fourth-column source / exact offline timeout
