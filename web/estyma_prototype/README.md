# Prototyp karty Estyma igneoTouch (E7)
Otwarcie: `cd web/estyma_prototype && python3 -m http.server 8765` -> http://localhost:8765/ (statyczne pliki, bez zaleznosci).
- Start = HOME; kafelek MENU -> menu z filtrem poziomu PIN i konfiguracji (pasek u gory), wiersz -> ekran (tlo PNG z danych firmware + zywe pola), kafel nastaw (prawy dol) -> lista nastaw (wartosci domyslne z firmware), naglowek `<` wstecz, ikona domu -> HOME.
- Okna HOME (Paliwo, Zasilanie, Auto, Czas, Data): obrazy z renderera z danych; OK zamyka.
- Dane = PRZYKLADOWE (`DEMO` w app.js); karta nie laczy sie z urzadzeniem i nic nie zapisuje.
Pliki generowane (nie edytowac recznie): `model.json` (`tools/build_proto_model.py`), `screens/*.png|json` (`tools/export_card_screen.py` + `tools/merge_bindings.py`), `dialogs/*.png` (`tools/dialog_render_eval.py`).
Wymaga emulatora i firmware tylko do ODTWORZENIA danych; sama karta dziala bez nich.
Zrodlo prawdy: `analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/` (kontrakt API: `API_KONTRAKT.md`, mapowanie PID->punkt: `pid_to_point.json`).

## Edycja i tryb odczytu z urzadzenia
- Lista nastaw: klik w wiersz liczbowy/enum -> dialog liczbowy (suwak, -/+, OK); wartosc tylko w pamieci strony (nic nie jest zapisywane).
- `?api=http://adres` -> karta odpytuje `GET /api/v1/states` co 2 s (tylko odczyt, bez autoryzacji) i podstawia wartosci pol, ktorych binding ma `id` punktu (koncowka id encji). Przetestowane na atrapie serwera; na prawdziwym urzadzeniu NIE testowane (CORS, id encji = `<prefix>_<id>` - do sprawdzenia przez wlasciciela).
