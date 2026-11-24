# ui_model

Machine-readable contract for measured/static Estyma UI reconstruction.

Datasets: menu_tree/menu_sweep; lists; alarms; outputs_test; live_sources; home_dialogs/home_dialogs_widgets/home_overlays_changed; dialogs_edit_pin; program_screen/program_bit_to_rect_kociol_monday; internet_editor; sii_acceptance evidence; extras; schema.

Evidence labels follow METODYKA_EMULATOR.md: MEASURED, STRONG, INFERENCE, OPEN, REJECTED. Unknown fields are allowed.

Consumers should use menu_tree for navigation/context, screen files for controls/data, live_sources for live provenance, alarms for alarm semantics, dialog files for modal rules, program files for PROGRAM and internet_editor for INTERNET. Evidence is provenance, not a substitute for the model.

Known gaps remain in NewEstyma/OPEN_POD_MUREM.md and individual open fields. This stage does not alter another agent's measured data.

Validation: python3 tools/validate_ui_model.py
