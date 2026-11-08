# TeklaPelletCAN – architektura (wersja robocza 0.1)

## 1. Cele
1. Własny firmware ESP32-C6 (XIAO) + MCP2515, bez ESPHome, z funkcjonalnością jak w PelletCAN (odczyt i zapis nastaw, harmonogramy, poziomy dostępu, test wyjść, statystyki, alarmy, diagnostyka).
2. Pierwsze uruchomienie: własny AP z portalem (w stylu Shelly) – wybór sieci Wi-Fi, opcjonalnie stałe IP.
3. Integracja Home Assistant (HACS) znajdująca urządzenie automatycznie (mDNS) lub po adresie IP.
4. Pod adresem IP urządzenia działa pełna karta (zapis i odczyt), ta sama co w HA.
5. Później: aplikacja Android (wyszukiwanie lub ręczne dodanie urządzenia).

Zasady: urządzenie **nie łączy się z internetem** (czas pochodzi od klientów); brak elementu = „-”; każda zmiana = bump wersji + changelog.

## 2. Nazewnictwo
Projekt `TeklaPelletCAN`, prefiks kodu `teklapelletcan`, karta `custom:teklapelletcan-card`, domena HA `teklapelletcan`, usługa mDNS `_teklapelletcan._tcp`, AP `TeklaPelletCAN-XXXX` (XXXX = końcówka MAC).

## 3. Schemat
```
Kocioł ─CAN 125k─ MCP2515 ─SPI─ ESP32-C6 (ESP-IDF)
  węzeł 4                         ├─ warstwa CAN/CANopen: SDO, PDO, NMT, węzeł 90
                                  ├─ model punktów (rejestr → wartość, typ, zakres, poziom dostępu)
                                  ├─ API REST + WebSocket, mDNS
                                  ├─ portal AP (captive) i strona WWW (karta z flash, gzip)
                                  └─ NVS: Wi-Fi, IP, hasło urządzenia, sparowani klienci
         ┌────────────────────────┼─────────────────────────┐
  przeglądarka (http://IP)   integracja HA (HACS)    aplikacja Android
```

## 4. Firmware – moduły (`firmware/main/`)
| Moduł | Zadanie |
|---|---|
| `mcp2515` | sterownik SPI, tryby, filtry, przerwanie INT |
| `canopen` | SDO klient (odczyt/zapis 1/2/4 B), kolejka zapytań, PDO, NMT, tożsamość węzła 90 |
| `points` | model punktów danych wygenerowany z `rejestry/` (nazwa, typ, kodowanie, zakres, R/W, poziom) |
| `scheduler` | cykliczny odczyt: poziom 0 stale, klucz 1/2 po PIN-ie, zapis i na żądanie |
| `access` | poziomy 0/1/2, PIN, auto-blokada, blokady zapisu (`mirror`, `*_write`) |
| `calc` | moc kW, spalanie kg/h, zużycie 24 h, prognoza paliwa, historia alarmów |
| `net` | Wi-Fi STA/AP, portal captive, DNS, mDNS, stałe IP/DHCP |
| `api` | REST + WebSocket, parowanie, tokeny |
| `store` | NVS: konfiguracja i lista klientów |
| `ota` | aktualizacja z WWW (podwójna partycja OTA) |
| `diag` | skaner rejestrów, Snap A/B, raport diagnostyczny |

Sprzęt domyślny: Seeed XIAO ESP32-C6, MCP2515 16 MHz; SCK=GPIO19, MISO=GPIO20, MOSI=GPIO18, CS=GPIO17 (jak w PelletCAN). Piny i prędkość CAN konfigurowalne. Węzeł ESP w CAN: 90.

## 5. Pierwsze uruchomienie i sieć
1. Brak zapisanej sieci → AP `TeklaPelletCAN-XXXX` z hasłem domyślnym `qwerty123` (decyzja właściciela; jawne w dokumentacji i zmienialne w portalu/WWW) + portal captive (DNS przekierowuje na 192.168.4.1). AP działa tylko do czasu skonfigurowania sieci, a portal wymusza ustawienie hasła urządzenia; do tego czasu zapis na kocioł jest zablokowany.
2. Portal: skan sieci 2,4 GHz, wybór, hasło, opcjonalnie IP/maska/brama/DNS (domyślnie DHCP), ustawienie hasła urządzenia, nazwa urządzenia.
3. Zapis do NVS, próba połączenia; sukces → AP wyłączony, adres IP pokazany w portalu; błąd → AP zostaje.
4. Utrata sieci → po ok. 1 min AP awaryjny ponownie (bez kasowania danych). Reset fabryczny: przytrzymanie przycisku BOOT 10 s lub z WWW.

## 6. Czas
Brak NTP/internetu. Klient (przeglądarka, HA, aplikacja) wysyła czas przy łączeniu i okresowo (`POST /api/time`). ESP trzyma offset względem zegara monotonicznego; do restartu czas jest „nieustawiony” i znaczniki alarmów są liczone z rejestrów kotła (Unix w sekundach). Opcjonalnie później: NTP po włączeniu w konfiguracji (domyślnie wyłączone).

## 7. API (szkic)
Wersja `v1`, JSON, `http://<ip>/api/v1/...`.
| Endpoint | Metoda | Opis |
|---|---|---|
| `/info` | GET | id, nazwa, wersja fw, model, liczba punktów, czy sparowano (bez uwierzytelnienia) |
| `/points` | GET | opis punktów (id, nazwa, typ, jednostka, klasa HA, R/W, poziom) |
| `/state` | GET | aktualne wartości wszystkich punktów |
| `/ws` | WebSocket | push zmian `{id: wartość}`; komendy zapisu |
| `/pair` | POST | parowanie klienta (kod) → token |
| `/clients` | GET/DELETE | lista sparowanych klientów, odwołanie dostępu |
| `/write` | POST | zapis punktu (token + poziom dostępu) |
| `/unlock` | POST | PIN → poziom 1/2 |
| `/time` | POST | ustawienie czasu przez klienta |
| `/wifi`, `/ota`, `/reset` | POST | konfiguracja, aktualizacja, reset (tylko z tokenem właściciela) |
| `/diag/*` | GET/POST | skaner SDO, Snap A/B, raport |

## 8. Bezpieczeństwo i parowanie
- Odczyt bez parowania (do decyzji: wyłączalny), każdy zapis tylko z tokenem klienta.
- Pierwsza konfiguracja ustawia hasło urządzenia (właściciel). Parowanie klienta: kod z WWW urządzenia lub hasło właściciela → token (losowy 128 bit), zapis w NVS (hash).
- Lista klientów: ID klienta (dla HA: `installation_uuid`), nazwa, data. **Ta sama instalacja HA nie doda urządzenia drugi raz** (urządzenie odrzuca ponowne parowanie tego ID; po stronie HA `unique_id` = ID urządzenia). **Wiele różnych HA może korzystać z jednego urządzenia.**
- Dodatkowo „flaga sparowania” w `/info` (liczba klientów), żeby portal/HA pokazały stan.
- Zapisy na kocioł: jak w PelletCAN – sprawdzanie zakresów, poziomu dostępu, blokady `mirror`/`*_write`.

## 9. Integracja HA (`custom_components/teklapelletcan`)
- Config flow: wykrycie przez zeroconf `_teklapelletcan._tcp` lub ręczne IP → kod parowania → entry z `unique_id` = ID urządzenia.
- Coordinator z WebSocket (push) i REST jako fallback; encje tworzone z `/points`.
- Usługi odpowiadające akcjom z PelletCAN (set_param, set_setpoint, set_schedule, unlock, diag).
- Karta `teklapelletcan-card` dostarczana razem z integracją (HACS, zasób dashboardu).

## 10. Karta (`web/`)
Jeden kod, dwa tryby: **urządzenie** (rozmawia z API ESP, serwowana z LittleFS) i **HA** (rozmawia przez integrację). Tłumaczenia (11 języków), tryb demo, edytor wizualny w HA. Kod startowy przeniesiony z `dist/` projektu PelletCAN i przepięty z encji ESPHome na model punktów.

## 11. Pamięć flash (XIAO C6, 4 MB)
Partycje: bootloader, NVS, 2 × OTA (ok. 1,3 MB każda), LittleFS na kartę i grafiki (ok. 700 KB, gzip). Grafiki panela (opcja „pełne”) osobno i opcjonalnie.

## 12. Plan
1. Szkielet repo + dokument (ten) ✔
2. Firmware: MCP2515 + SDO + model punktów (odczyt), wygenerowany z `rejestry/`.
3. Portal AP/Wi-Fi, mDNS, `/info`.
4. API + WebSocket + strona z kartą.
5. Zapis, poziomy dostępu, parowanie.
6. Integracja HA.
7. Aplikacja Android.

## 13. Decyzje
- Hasło AP: `qwerty123` (domyślne, zmienialne).
- Odczyt bez parowania: domyślnie włączony (wyłączalny); zapis tylko z tokenem.
- Sprzęt: XIAO ESP32-C6; interfejs w 11 językach (z `pelletcan-lang.js`).
- Czas od klienta, bez internetu na ESP.

## 14. Otwarte
- Dokładny format opisu punktów (generator z CSV w `rejestry/`).
- Hasło AP jest wspólne dla wszystkich egzemplarzy – rozważyć losowe hasło wyświetlane na naklejce/w logu.

## 15. Stan implementacji
- `firmware/components/core` (bez zależności od ESP, testy na hoście, `ctest`): ramka CAN, klient SDO (odczyt/zapis expedited, abort), kodowanie wartości rejestrów, sterownik MCP2515 przez interfejs `ISpi`.
- `firmware/main`: warstwa ESP-IDF (SPI, `app_main` z próbnym odczytem). **Jeszcze niezbudowane w ESP-IDF** – to kod do pierwszej kompilacji na sprzęcie.
