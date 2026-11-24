# MULTIPASS-17 — Dmuchawa palnika vs wentylator wspomagający/spalin — 2026-11-20

Nowy dowód z oficjalnej instrukcji Estyma/Tekla: pkt 4.2.1 „Moc dmuchawy modulacja” opisuje wykres obrotów dmuchawy w funkcji mocy palnika. W tym samym rozdziale osobno występuje „Wentylator wspomagający” z adnotacją „Charakterystyka jak w pkt 4.2.1”.

Wniosek: firmware ma co najmniej dwie odrębne rodziny pięciopunktowych charakterystyk:

A) Dmuchawa palnika:
- 0x2261 = 20%
- 0x2262 = 40%
- 0x2263 = 60%
- 0x2264 = 80%
- 0x2265 = 100%

B) Druga charakterystyka wentylatora:
- 0x2268 = exh. fan char. 1, domyślnie 20
- 0x226E = exh. fan char. 2, domyślnie 30
- 0x226F = exh. fan char. 3, domyślnie 40
- 0x2275 = exh. fan char. 4, domyślnie 50
- 0x227A = exh. fan char. 5, domyślnie 60

Nie należy łączyć obu rodzin w jeden zestaw 10 punktów. FUN_0803EC18 ma osobne gałęzie: 0x4A..0x4E -> pierwsza rodzina oraz 0x4F..0x53 -> druga rodzina. Obie korzystają z ogólnego mechanizmu komponentu wykresu.

To bardzo dobrze wyjaśnia obserwację użytkownika: brak drugiego wykresu w jego konkretnym menu nie oznacza, że druga rodzina nie istnieje. Najbardziej prawdopodobne jest warunkowanie UI przez konfigurację/wyposażenie kotła. Dokładny gate pozostaje OPEN; trzeba znaleźć xref konfiguracji do drugiej rodziny i jej tytuł/rodzica UI.

Dalszy atak: odzyskać gate drugiej charakterystyki, sprawdzić zależność od typu modułu/modelu/aktywnego wentylatora oraz zamknąć osobny tytuł TypedText i host/content. 056/057 pozostają markerami komponentu wykresu.
