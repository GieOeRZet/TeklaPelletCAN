# Mapa przeniesien (E5, 2026-11-24)
| stary | nowy | uwagi |
|---|---|---|
| `analiza/` | `analiza_archiwum/` | `git mv` calego katalogu (historia zachowana, `git log --follow`); wszystkie odwolania tekstowe `analiza/` -> `analiza_archiwum/` w narzedziach i dokumentacji (104 pliki); sciezki w kodzie przez `tools/paths.py` (`ESTYMA_ANALIZA` nadpisuje nazwe) |
| `analiza/FW2213TK-2026-11-22/data/ui_model/` | `analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/` | jedyne zrodlo prawdy ui_model |
Weryfikacja: `python3 tools/smoke_test.py` PASS przed i po; walidator ui_model PASS; dialog_render_eval (PIN, czas) bez zmian wyniku; INDEX.json przebudowany.
