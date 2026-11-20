# CHAT ARCHIVE — RAW TRANSCRIPT STATUS
Date: 2026-11-20

## User requirement

The user explicitly requires that the **entire conversation/chat be preserved in Git**, not merely a technical summary, so that a future chat/agent can continue with the full conversational context.

## Important limitation

The GitHub connector available to this agent does NOT expose a function that retrieves the complete ChatGPT conversation transcript, including messages that are no longer present in the current tool-visible context or messages represented internally as skipped/truncated turns.

Therefore this file is intentionally a **status/manifest**, not a claim that a literal complete transcript has been copied.

It would be incorrect to fabricate missing messages or call a summary a full transcript.

## What is currently persisted

The following are persistent technical/context handoffs:

- MASTER-STATE-CONSOLIDATED-2026-11-19.md
- START-HERE-FOR-NEXT-AGENT.md
- BATCH-WHOLE-SOFTWARE-MULTIPASS-2026-11-20.md
- BATCH-ANIMATION-ENGINE-AND-ACTUATOR-MAPS-2026-11-20.md
- BATCH-ORIGINAL-TOUCH-HOME-IMPLEMENTATION-2026-11-20.md
- BATCH-ORIGINAL-SOFTWARE-ARCHITECTURE-RESET-2026-11-20.md
- CHAT-CONTINUITY-2026-11-20-ARCHITECTURE-RESET.md

## Current scope rule

The project is a new ESP/CAN implementation intended to reproduce the original Estyma/igneoTouch firmware behavior 1:1 except for the physical platform. Existing TeklaPelletCAN behavior is not the source of truth.

## Required next action for a true raw archive

A true raw archive must be produced from the platform's conversation transcript/export (or from a tool that exposes the complete conversation). Once the complete transcript is available as a file or tool result, it can be stored verbatim in this repository.

## Do not mistake

- technical handoff != raw transcript
- summary != raw transcript
- reconstructed context != raw transcript
- model memory != raw transcript

No missing chat text should be invented.
