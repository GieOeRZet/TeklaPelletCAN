# CHAT / CONTINUITY INDEX — TeklaPelletCAN
Data: 2026-11-20

## Purpose

This index tells a new agent where to recover the accumulated conversational and technical context.

## Canonical entry point

MASTER-HANDOFF-FOR-NEXT-AGENT-2026-11-20.md

It contains:
- project goal;
- source-of-truth hierarchy;
- analysis rules;
- firmware hash;
- tooling;
- UI/menu/PIN state;
- bitmap and TypedText state;
- graph/blower branch;
- configuration architecture;
- current OPEN queue;
- documentation rules;
- raw-transcript limitation.

## Core continuity

- START-HERE-FOR-NEXT-AGENT.md
- MASTER-STATE-CONSOLIDATED-2026-11-19.md
- CHAT-ARCHIVE-RAW-STATUS.md
- CHAT-CONTINUITY-2026-11-20-ARCHITECTURE-RESET.md
- CHAT-CONTINUITY-2026-11-20-BLOWER-FAMILIES-WHOLE-SOFTWARE-RESET.md
- SOURCE-OF-TRUTH-POLICY-2026-11-20.md
- DOCUMENTATION-COVERAGE-AUDIT-2026-11-20.md

## Main technical branches

### 6154 / access
- MULTIPASS-12-6154-DEEP-AUDIT-2026-11-20.md
- MULTIPASS-13-6154-NUMERIC-CONTROL-PARAM-BINDING-2026-11-20.md
- MULTIPASS-14-6154-17-WRAPPER-MATRIX-ATTACK-2026-11-20.md

### Home / UI
- BATCH-ORIGINAL-TOUCH-HOME-IMPLEMENTATION-2026-11-20.md
- HOME-GEOMETRY-FW-ONLY-MULTIPASS-2026-11-20.md
- HOME-GEOMETRY-USER-VISUAL-CORRELATION-2026-11-20.md
- BATCH-HOME-HOST-2E716-469E8-BOUNDARY-2026-11-19.md

### 47290
- MULTIPASS-47290-SOURCE-CONTEXT-DEEP-TRACE-2026-11-20.md
- CHECKPOINT-47290-SOURCE-CONTEXT-2026-11-20.md
- MULTIPASS-47290-3EC18-SEMANTIC-DISAMBIGUATION-2026-11-20.md

### Graph / blower / exhaust fan
- MULTIPASS-15-GRAPH-056-057-2261-227A-HARD-TRACE-2026-11-20.md
- MULTIPASS-16-REUSABLE-GRAPH-MARKERS-CONFIG-UI-2026-11-20.md
- MULTIPASS-2261-2265-GRAPH-VS-47290-CORRECTION-2026-11-20.md
- MULTIPASS-17-BLOWER-FAMILIES-CONFIGURATION-2026-11-20.md
- MULTIPASS-18-DIRECT-STRING-AND-FAN-BRANCH-2026-11-20.md

### General / animation / architecture
- BATCH-WHOLE-SOFTWARE-MULTIPASS-2026-11-20.md
- BATCH-ANIMATION-ENGINE-AND-ACTUATOR-MAPS-2026-11-20.md
- BATCH-ORIGINAL-SOFTWARE-ARCHITECTURE-RESET-2026-11-20.md

## Important rule about chats

These files are continuity summaries/checkpoints. They are not claimed to be literal full transcripts.

CHAT-ARCHIVE-RAW-STATUS.md explicitly records that the current GitHub connector cannot retrieve hidden/truncated ChatGPT turns.

If an exported conversation becomes available as a file:
1. store it verbatim;
2. add its path here;
3. do not replace it with a summary.

## Current branch to continue

Extra/boost/exhaust fan configuration:
resolver 0x68 -> FUN_08043A36 -> Podajnik palnika / Wentylator wspomagający -> configuration gate -> 0x2268..0x227A.

Do not lose the global 1:1 reconstruction objective while closing this branch.
