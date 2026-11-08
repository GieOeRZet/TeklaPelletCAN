# TeklaPelletCAN – TODO

## Karta WWW → ekran „Informacje o programie”
- [ ] Wskaźnik aktualizacji (zielone MENU, „Informacje o programie”, „Odrzuć aktualizację”) sprawdza dziś `version.json` starego projektu PelletCAN i porównuje z wersją firmware ESPHome. Ma pokazywać **nową wersję oprogramowania modułu (ESP TeklaPelletCAN)** z manifestu `updates/manifest.json` (kanał beta/stabilny) i jej **changelog** (`notes` z manifestu; docelowo pełna lista zmian).
- [ ] Przycisk „Zainstaluj” z tego ekranu może prowadzić do `/settings.html` (aktualizacja jednym kliknięciem już działa).

## Aktualizacje i wydania
- [ ] **Własny klucz podpisu OTA** zamiast testowego z repo: `python3 tools/ota_sign.py init`, `ota_sign.py pubkey`, sekret `OTA_SIGNING_KEY`; wydanie przejściowe podpisane starym kluczem z nowym kluczem publicznym w środku.
- [ ] Encja `update` w integracji HA (powiadomienie + instalacja z HA).
- [ ] Pełny changelog (`CHANGELOG-firmware.md`) generowany do manifestu przy tagu `v*`.

## Firmware / sprzęt
- [ ] Weryfikacja na kotle: odczyty vs panel, potem włączenie zapisu; test zapisów (nastawy, tryby, harmonogramy, podajnik, dmuchawa).
- [ ] Snap A/B (migawki rejestrów) – dziś „nieobsługiwane”.
- [ ] Wykrywanie słabej anteny zewnętrznej (RSSI), nie tylko braku połączenia.
- [ ] Zapis i odczyt czasu od klienta (przeglądarka/HA) dla znaczników alarmów.

## Integracje
- [ ] Aplikacja Android (wyszukiwanie przez mDNS lub ręczne dodanie; ta sama karta).
- [ ] Zweryfikować wykrywanie zeroconf w HA na prawdziwym urządzeniu.
