# ChatGPT UI model package — Stage 1

2026-11-24

Implemented Stage 1 from NewEstyma/ZADANIE_CHATGPT_UI_MODEL_PAKIET.md: Draft 2020-12 schemas, validator, recursive index generator and README.

Intentional inconsistencies are reported, not corrected: legacy datasets lack schema_version; home_dialogs_widgets.json, home_overlays_changed.json, lists.json and program_bit_to_rect_kociol_monday.json lack top-level evidence. Nested extras/* and sii_acceptance/* JSON are indexed recursively but currently report missing per-file schemas because Stage 1 targets ui_model/*.json. No measured dataset was changed.
