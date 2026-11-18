# Firmware (ESP32-C6) — architektura rzeczywista

> Uzupełnienie do `docs/ARCHITEKTURA.md` (ogólny projekt, częściowo przeterminowany — patrz uwaga na górze tego
> pliku w repo). Ten dokument opisuje **faktyczną strukturę kodu**, jaka istnieje dziś w `firmware/`, zweryfikowaną
> wprost z drzewa plików, nie z dokumentu planistycznego.

## Sprzęt
Seeed XIAO ESP32-C6 + MCP2515 (SPI, 16 MHz) na magistrali CAN 125 kbit/s kotła (CANopen, węzeł 4 = kocioł, węzeł
90 = ESP, węzeł 86 = CAN IO BIG). Piny domyślne: SCK=GPIO19, MISO=GPIO20, MOSI=GPIO18, CS=GPIO17 (konfigurowalne).

## Moduły — `firmware/components/core/` (kod niezależny od ESP-IDF, testowalny na hoście przez `ctest`)

| Plik | Rola |
|---|---|
| `mcp2515.*` | Sterownik SPI kontrolera CAN (przez interfejs `ISpi` — testowalny z atrapą). |
| `sdo.*`, `sdo_queue.*` | Klient CANopen SDO: odczyt/zapis (expedited, abort), kolejka z priorytetem zapisów, limit czasu, ponowienia. |
| `codec.*` | Kodowanie/dekodowanie wartości rejestrów (flaga+bajt, liczba, ułamek, maska bitowa, int16 ze znakiem) — patrz `rejestry/README.md` §1 "Kodowanie wartości". |
| `point.*`, `points_table.cpp` | Model punktów danych (nastawy) — tabela generowana z `rejestry/punkty.csv` przez `tools/gen_points.py` (CI pilnuje aktualności, `tools/gen_points.py --check`). |
| `reads.*`, `reads_table.cpp` | Model odczytów cyklicznych (sensory, stany) — analogicznie generowane. |
| `entities.*`, `entities_table.cpp` | Mapowanie punktów/odczytów na encje w stylu Home Assistant (nazwy jak w oryginalnym ESPHome, dla zgodności z kartą referencyjną). |
| `access.*` | Poziomy dostępu 0/1/2 (PIN jak w panelu: klucz 1 = PIN 0900, klucz 2 = PIN 0999), autoblokada, blokady zapisu (`mirror`). |
| `engine.*` | Rdzeń logiki: spina punkty/odczyty/dostęp/API w jedną całość, warstwa obliczana (moc kW, spalanie, prognoza paliwa). |
| `alarms.*`, `alarm_names_table.cpp` | Historia alarmów kotła (odczyt, nazwy, potwierdzanie). |
| `api.*` | Implementacja REST/WebSocket niezależna od serwera HTTP (logika, nie transport). |
| `net_fsm.*` | Automat stanów sieci Wi-Fi (AP awaryjny / STA) — patrz `docs/ARCHITEKTURA.md` §12a, tabela zachowań. |
| `mdns.*` | Własny responder mDNS (komponent `mdns` nie jest dostępny w ESP-IDF 5.4 — zaimplementowany ręcznie). |
| `dns.*` | DNS portalu captive (AP pierwszej konfiguracji). |
| `ota.*`, `ota_pubkey.cpp` | Logika weryfikacji aktualizacji: SHA-256 + podpis ECDSA P-256 kluczem publicznym wbudowanym w firmware. |
| `version.*` | Porównywanie wersji, ukrywanie wydań beta przed zwykłym użytkownikiem. |
| `license.*`, `license_pubkey.cpp` | Nieużywany dziś moduł kodu licencyjnego — zachowany w repo na wypadek przyszłego włączenia (`engine` go nie wywołuje). |
| `demo_device.*`, `sim_boiler.h` | Symulator kotła (do testów na hoście i trybu demo aplikacji Android przez JNI). |
| `json_parse.*`, `json_writer.h` | Minimalny parser/writer JSON bez zależności zewnętrznych. |
| `logring.*` | Pierścieniowy bufor logów diagnostycznych. |

## Warstwa ESP-IDF — `firmware/main/` (zależna od sprzętu, nietestowalna na hoście)

| Plik | Rola |
|---|---|
| `main.cpp` | `app_main()` — spina wszystko, inicjalizacja. |
| `spi_idf.*` | Implementacja `ISpi` na prawdziwym SPI ESP-IDF. |
| `wifi_mgr.*` | Sterowanie Wi-Fi STA/AP (NVS, zdarzenia, integracja z `net_fsm`). |
| `firstboot.*` | Pierwsze uruchomienie / portal konfiguracyjny AP. |
| `http_srv.*` | Serwer HTTP (`esp_http_server`) — REST + WebSocket + serwowanie karty WWW z flash. |
| `mdns_srv.*` | Spina własny responder `mdns` (core) z ESP-IDF. |
| `ota_idf.*` | OTA na prawdziwym ESP-IDF: podwójna partycja, `esp_ota_mark_app_valid`, rollback. |
| `store.*` | NVS: konfiguracja sieci, hasło urządzenia, sparowani klienci. |
| `web_assets.h` | Wygenerowany nagłówek z zawartością `web/` spakowaną gzip (patrz `tools/pack_web.py`, `firmware/main/CMakeLists.txt`) — **karta WWW jest częścią obrazu firmware**, jedna aktualizacja = firmware + interfejs. |

## Status (listopad 2026 — skorygowany względem `docs/ARCHITEKTURA.md`)

`docs/ARCHITEKTURA.md` w kilku miejscach pisze "nie było jeszcze uruchamiane na sprzęcie" — **to już nieaktualne**.
Firmware działa na prawdziwym sprzęcie od wydania v1.0.0 (potwierdzone wieloma rundami poprawek OTA, testów
rzeczywistych w tej sesji — np. diagnoza "resetów przy OTA" na prawdziwym kotle, log `raport_6_2.txt`/
`log_3_2.txt`). Aktualny numer wersji: patrz plik `VERSION` w korzeniu repo (od tej sesji: **czysty numer, bez
dopisku numeru builda CI** — `1.0.x`, nie `1.0.x+NN`).

## Komunikacja — pełny łańcuch

```
Kocioł (CANopen, węzeł 4)
   │  SDO (odczyt/zapis rejestrów), 125 kbit/s
   ▼
MCP2515 ──SPI── ESP32-C6
   │  engine: punkty + odczyty + warstwa obliczana + dostęp
   ▼
REST (`/api/v1/...`) + WebSocket (push zmian)
   │
   ├── przeglądarka → portal/karta urządzenia (`web/`, ten sam silnik co karta HA)
   ├── integracja Home Assistant (`custom_components/teklapelletcan`) → encje + usługi
   └── aplikacja Android (natywny proxy Kotlin + JNI do rdzenia `core`) → UI `android/ui`
```

Szczegóły formatu API: `docs/ARCHITEKTURA.md` §7 (tabela endpointów) — wciąż aktualna technicznie.
Szczegóły rejestrów/kodowania: [`../rejestry/`](../rejestry/README.md) — **to jest jedyne, w pełni aktualne i
wyczerpujące źródło** o rejestrach kotła, kodowaniu wartości i metodologii skanowania.

## OTA — dwie partycje, co faktycznie robi "rollback" (listopad 2026)

**NIE jest to oparte na ESPHome** — `firmware/` to czysty ESP-IDF (CMake), ESPHome nie występuje nigdzie w
build-systemie ani w runtime. Jedyny związek z ESPHome to historyczny: część urządzeń mogła wcześniej działać
jako węzły ESPHome, stąd dopisek "(np. ESPHome)" przy przycisku rollbacku (patrz niżej) i ewentualne użycie
dashboardu ESPHome do **pierwszego** wgrania (zastąpione teraz instalatorem WWW, patrz
[`INSTALATOR-WWW.md`](INSTALATOR-WWW.md)).

**Tabela partycji** (`firmware/partitions.csv`) — dwa równoprawne sloty OTA, bez osobnej partycji `factory`:
```
otadata,  data, ota,     0xf000,   0x2000
ota_0,    app,  ota_0,   0x20000,  0x1D0000
ota_1,    app,  ota_1,   0x1F0000, 0x1D0000
```

**Co robi przycisk "Wróć do poprzedniego firmware"** (`web/settings.html` → `POST /api/v1/ota/rollback` →
`ota_rollback_previous()` w `firmware/main/ota_idf.cpp`): ustawia jako startową partycję **tę, która aktualnie
NIE jest uruchomiona** (`esp_ota_get_next_update_partition`). To **nie jest** powrót do "pierwotnego, pierwszego
wgranego" obrazu — nie ma czegoś takiego jak nietykalna kopia zapasowa. Konsekwencje:
- Zaraz po pierwszym ręcznym wgraniu (gdy w drugim slocie wciąż leży to, co było tam wcześniej — np. ESPHome) —
  przycisk faktycznie wraca do tamtego obrazu.
- Po **pierwszej** aktualizacji OTA tego firmware — drugi slot to już poprzednia wersja TEGO firmware, nie
  cokolwiek innego.
- Po **drugiej** aktualizacji — oba sloty to już wersje tego firmware; kliknięcie wraca do przedostatniej. Drugie
  kliknięcie bez nowego OTA między nimi wraca do tej, z której się właśnie zeszło (ping-pong tylko między dwiema
  ostatnimi wersjami — brak głębszej historii, bo są tylko dwa sloty).

**Automatyczny rollback przy zawieszeniu** (`ota_idf.cpp:51-67`, `CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE=y` w
`sdkconfig`) — osobny, już istniejący mechanizm, niezależny od przycisku: po OTA nowa wersja ma 25 s na
"potwierdzenie się" (`esp_ota_mark_app_valid_cancel_rollback()`, wywoływane z `health_task`). Jeśli zawiesi się
lub zrestartuje wcześniej — **bootloader ESP-IDF sam** wraca na poprzednią partycję, bez udziału użytkownika i
bez żadnego kodu aplikacyjnego w tym momencie (dzieje się na poziomie bootloadera, zanim nowa aplikacja zdąży
się w pełni uruchomić).
