# AUTONOMOUS-PASS-110-ALARM-ASYMMETRY-AUDIT-2026-11-23

## Źródło
Dokładny `analiza/FW2213TK-2026-11-22/data/alarm_raise_clear_sites.csv`.

## HARD
Zliczenie nazwanych kodów pokazuje, że katalog nie jest symetryczny:
- clear-only: 7, 43, 53, 115, 250;
- raise-only: 131, 139, 140, 150, 160, 161;
- pozostałe nazwane kody mają co najmniej jeden raise i clear.
- kod 0 ma jeden wpis raise i jeden clear bez tekstu — pozostaje wpisem technicznym/genericznym, nie przypisuję mu alarmu UI.

To jest **audyt katalogu miejsc**, nie dowód biznesowej reguły alarmu. „clear-only” może oznaczać alarm ustawiany inną ścieżką (np. wspólnym mechanizmem komunikacji) albo nieodtworzony raise-site; nie należy automatycznie implementować raise/clear na podstawie samej symetrii.

## Następny krok
Dla kodów asymetrycznych trzeba śledzić caller/context i warunki, zamiast dopisywać brakujące wywołania.
