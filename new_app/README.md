# TeklaPellet NEW

Nowa aplikacja Android budowana niezależnie od katalogu android/.

Architektura:
- Kotlin + Jetpack Compose + Material 3 + własny Glass/industrial theme.
- Brak WebView i brak zależności od starego Android UI.
- BLE discovery dla urządzeń reklamujących TeklaPellet-*.
- mDNS _teklapelletcan._tcp + ręczny adres IP.
- REST API urządzenia po Wi-Fi.
- Tryb DEMO wyłącznie przed dodaniem pierwszego prawdziwego modułu.
- Po dodaniu modułu DEMO znika z UI.
- Moduły Solar/Bufor/Kaskada/Magazyn są dynamiczne i dostępne z MENU; CO2 jest drugim obiegiem.
