# BATCH — MULTIPASS 5C: BITMAP SIBLINGS / RESOURCE BOUNDARY — 2026-11-19

Przeszukano zapisane analizy pod kątem mutacji +0x85C, +0x888, +0x8B4, +0x8E0.

Twarde: wszystkie sześć Bitmap children (+0x330,+0x35C,+0x85C,+0x888,+0x8B4,+0x8E0) startuje z resource 0xFFFF.

Późniejsze twarde mutacje: +0x85C dostaje resource 11/12/13 przez 370A -> 0x121 -> CB2C -> CACC; C5B4 ustawia +0x85C X=40,Y=70. C5B4 ustawia +0x8E0 resource 0x7A=122, X=398, Y=runtime i attach przez parent+0x04.

Nie znaleziono w zapisanych artefaktach równie twardego writer-call-site dla +0x888/+0x8B4. Nie przypisujemy im semantyki z samej kolejności offsetów.

122.png = 35x37. Rodzina 120..123 również ma 35x37, ale geometria nie dowodzi semantyki.

Nie znaleziono nowego mostu 0x10E -> 0x90/0x92 -> assets 144/146 ani bezpośredniego writer-call-site FUN_080307BC(...,0x90/0x92).

Następny atak: indirect method table C33E/C5B4; wszyscy writerzy +0x888/+0x8B4; źródło Y dla +0x8E0; upstream trzech C33E callers; dopiero potem bottom-bar CO.
