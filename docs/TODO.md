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
- [x] Aplikacja Android (mDNS/ręcznie, ta sama karta, tryb demo) – patrz `docs/APLIKACJA_ANDROID.md`.
- [ ] Aplikacja: sprawdzenie na prawdziwym telefonie (NSD, wiązanie z Wi‑Fi bez internetu, pobieranie dziennika), powiadomienia o alarmach, samoaktualizacja.
- [ ] Poziomy encji w HA (podstawowe / rozszerzone / wszystkie) zamiast wszystkich ~190 encji.
- [ ] Własny klucz podpisu APK (sekrety `ANDROID_KEYSTORE_*`) zamiast testowego.
- [ ] Zweryfikować wykrywanie zeroconf w HA na prawdziwym urządzeniu.

## Aplikacja – etap 1 (zrobiony) i następne
- [x] Samodzielny interfejs, PIN aplikacji, odcisk (opcja), blokada zapisu 5 min, poziomy kotła 1/2, ostatnie dane offline.
- [ ] Parytet z kartą: harmonogramy (CWU/CO/zasobnik), Konfiguracja, Test wyjść, Statystyki, Sieć, język, alarm dźwiękowy – w nowym stylu (lista parytetu + test).
- [ ] `/api/v1/time` w firmware + ustawianie czasu przy otwarciu aplikacji.
- [ ] Aktualizator aplikacji (manifest `app`, `min_fw`/`min_app`), baner o aktualizacji firmware z listą zmian.
- [ ] Powiadomienia o alarmach (usługa w tle w domowej sieci, `/api/v1/summary`), blueprint HA.
- [ ] Zrzuty z emulatora Androida w CI (gałąź ze zrzutami) i ujednolicone, wyższej rozdzielczości grafiki kotła 11/12/14.

## Karta TeklaPelletCAN-card (zrobione) i następne kroki
- [x] `teklapelletclassic-card`: wyłącznie integracja TeklaPelletCAN, urządzenie z rejestru HA (nie zgadywanie po encjach), auto-dobór encji, wybór urządzenia w edytorze przy kilku integracjach, grafiki pełne domyślnie.
- [ ] Zsynchronizować wybór grafiki/obrazu kotła z ustawieniem na samym urządzeniu (dziś niezależne – urządzenie nie wystawia tego jako encja HA).
- [ ] Karta `TeklaPelletCAN-modern` w stylu nowej aplikacji Android (patrz niżej) – projekt do zrobienia.
- [ ] Rozważyć `CARD_DOMAIN_ONLY` flag / translation_key na encjach integracji, żeby karta mogła odróżniać urządzenia bez polegania tylko na `identifiers`.

## Karta TeklaPelletCAN-modern (do zaprojektowania, nie zaczęte)
Styl spójny z nową aplikacją Android (pulpit z grafikami Tekli, schemat instalacji, harmonogramy, poziomy 1/2 z PIN-em jak w oryginale – bez biometrii, bo to środowisko przeglądarki HA). Te same proporcje karty co `teklapelletclassic-card`/oryginał (żeby komponowała się w istniejące dashboardy). Pomysł na modułowość: osobne mniejsze karty (pulpit/instalacja/harmonogram/alarmy) albo jedna karta z zakładkami – do decyzji przy starcie prac.
