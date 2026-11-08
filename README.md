# TeklaPelletCAN

Własny firmware (ESP-IDF, C++) dla ESP32 z modułem CAN (MCP2515), który czyta i zapisuje parametry kotła pelletowego Tekla/Estyma po magistrali CAN (CANopen SDO, węzeł 4, 125 kbit/s). Następca projektu [PelletCAN](https://github.com/GieOeRZet/PelletCAN) (ESPHome) – bez ESPHome, z własnym portalem konfiguracji, własnym API, stroną WWW z pełną kartą, integracją Home Assistant i (później) aplikacją Android.

> Status: **projekt w początkowej fazie** – szkielet repozytorium i architektura. Zobacz [docs/ARCHITEKTURA.md](docs/ARCHITEKTURA.md).

## Elementy
| Katalog | Zawartość |
|---|---|
| `firmware/` | firmware ESP32 (ESP-IDF, C++): CAN/CANopen, API, portal AP, WWW |
| `web/` | karta `teklapelletcan-card` – jeden kod dla strony na ESP i dla Home Assistant |
| `custom_components/teklapelletcan/` | integracja Home Assistant (HACS) |
| `android/` | aplikacja Android (później) |
| `rejestry/` | katalog rejestrów CANopen kotła (przeniesiony z PelletCAN) |
| `docs/` | dokumentacja i architektura |

## Zastrzeżenia
Projekt niezależny i nieoficjalny, niezwiązany z firmami Tekla ani Estyma. Zapis parametrów na własne ryzyko (może naruszać gwarancję). Szczegóły i licencja – jak w PelletCAN, zobacz [LICENSE](LICENSE).
