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
Partycje (`firmware/partitions.csv`): NVS, otadata, 2 × OTA po 1,8 MB, `storage` 256 KB (opcjonalne grafiki panela). **Karta WWW jest wbudowana w obraz firmware** (gzip), więc jedna paczka = jedna atomowa aktualizacja firmware i karty.

## 12. Plan
1. Szkielet repo + dokument (ten) ✔
2. Firmware: MCP2515 + SDO + model punktów (odczyt), wygenerowany z `rejestry/`.
3. Portal AP/Wi-Fi, mDNS, `/info`.
4. API + WebSocket + strona z kartą.
5. Zapis, poziomy dostępu, parowanie.
6. Integracja HA.
7. Aplikacja Android.

## 12a. Aktualizacje (OTA) i awaryjny AP

### Skąd urządzenie wie o nowej wersji
ESP **nie ma internetu**, więc nie sprawdza wersji samo. Robi to klient, który internet ma:
1. **Manifest** `manifest.json` publikuje CI przy wydaniu (GitHub Pages, nagłówek CORS `*`): `{version, notes, url, size, sha256, signature, min_version}`. Plik `.bin` leży obok manifestu (na Pages/raw, nie na `objects.githubusercontent.com`, bo ten nie ma CORS).
2. Klient porównuje `manifest.version` z `/api/v1/info.version` (logika `version.h`, wydania `-beta` ukryte, chyba że włączono kanał testowy).
3. Jeśli jest nowsza – **komunikat „Dostępna aktualizacja X.Y.Z” + lista zmian + przycisk „Zaktualizuj”**:
   - **Karta (na stronie ESP i w HA):** baner w menu, przeglądarka pobiera `.bin` i wgrywa go do ESP (`POST /api/v1/ota`).
   - **Integracja HA:** natywna encja `update` (HA pokazuje „Aktualizacja dostępna” i przycisk Zainstaluj), integracja pobiera `.bin` i wysyła do ESP, pokazując postęp.
   - **Aplikacja Android:** to samo co karta.
   - Ręcznie: wgranie pliku `.bin` na stronie urządzenia (gdy nie ma internetu nigdzie).

### Bezpieczeństwo aktualizacji
- Wgranie wymaga tokenu **właściciela** (nie zwykłego klienta).
- ESP sprawdza `sha256` i **podpis ECDSA P-256** obrazu kluczem publicznym wbudowanym w firmware (klucz prywatny tylko w sekretach CI). Obcy plik jest odrzucony przed przełączeniem partycji.
- Odrzucane są obrazy dla innego układu, starsze od `min_version` oraz z innym ID projektu.

### Przebieg i odporność na awarie
1. Obraz jest zapisywany do **nieaktywnej** partycji OTA (druga działa dalej, kocioł nie traci obsługi).
2. Po weryfikacji restart na nową partycję; kocioł nie jest zapisywany w trakcie aktualizacji.
3. Nowa wersja musi w ciągu 60 s zgłosić „zdrowie”: Wi-Fi działa lub AP wystawiony, MCP2515 odpowiada, API słucha. Dopiero wtedy `esp_ota_mark_app_valid`. W przeciwnym razie (lub po 3 nieudanych startach) **automatyczny powrót** do poprzedniej wersji (`CONFIG_APP_ROLLBACK_ENABLE`).
4. Aktualizacja nie kasuje NVS (sieć, hasło, sparowani klienci); zmiany formatu NVS są wersjonowane z migracją.

### Awaryjny punkt dostępu (automat sieci, `net_fsm`, testy na hoście)
| Sytuacja | Zachowanie |
|---|---|
| Pierwsze uruchomienie, brak sieci | tylko AP `TeklaPelletCAN-XXXX` + portal |
| Dane są, łączenie | próba 30 s bez AP |
| Nie połączono po 30 s (zła sieć/hasło/router wyłączony) | **AP wraca** (AP+STA), STA dalej próbuje w tle |
| Utrata działającej sieci | 30 s cichej próby, potem AP wraca |
| Sieć wróciła | AP znika dopiero po 10 s stabilnego połączenia |
| Nowe dane wpisane w portalu | AP zostaje do końca testu; po sukcesie portal pokazuje IP; po porażce wracają **poprzednie** dane i portal pokazuje błąd |
| Reset fabryczny (BOOT 10 s) | czyści sieć, hasło i klientów, wraca portal |

### „Od strzała” – lista kontrolna jakości
- Test na hoście logiki: SDO, kodowanie, MCP2515, wersje, automat sieci (CI przy każdym pushu).
- Release: CI buduje `.bin`, podpisuje, generuje `manifest.json`, publikuje na Pages i w Releases.
- Pierwsza instalacja z kabla USB (`idf.py flash` lub gotowy plik `*.factory.bin` + skrypt), każda kolejna – z przycisku.
- Wersja firmware widoczna w `/info`, na karcie, w HA i na panelu kotła (węzeł 90, jak w PelletCAN).

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
- Dodano: `version` (porównywanie wersji, ukrywanie wydań beta), `net_fsm` (automat AP/STA z awaryjnym AP i testem nowych danych) – z testami.
- Dodano: `point` + `points_table.cpp` (81 nastaw wygenerowanych z `rejestry/punkty.csv` przez `tools/gen_points.py`, CI pilnuje aktualności), `access` (poziomy 0/1/2, PIN, autoblokada 5 min, `mirror`, walidacja zakresu i kodowanie zapisu), `sdo_queue` (jedno zapytanie w locie, priorytet zapisów, limit czasu 200 ms, 2 ponowienia, abort), kodowanie wartości ze znakiem (int16) – z testami.
- `firmware/main`: warstwa ESP-IDF (SPI, `app_main` z próbnym odczytem). **Kompiluje się w ESP-IDF 5.4.1 dla ESP32-C6** (obraz ok. 166 KB), ale nie był jeszcze uruchamiany na sprzęcie. Zobacz [BUDOWANIE.md](BUDOWANIE.md).

## 16. Jak przenosić nowości z ESPHome (PelletCAN)
W ESPHome każdy rejestr siedzi w kilku równoległych tablicach C++ w lambdach (`ix/lo/hi/lv`, listy odczytu `l0/l1/l2`, kodowanie w łańcuchu `if/else`) i w kluczach numerycznych zaszytych w karcie. Ręczny transfer jest żmudny i podatny na błędy, dlatego:
1. **Jedno źródło prawdy:** tabela punktów w `rejestry/` (indeks, kodowanie, zakres, poziom, nazwa). Firmware (generowana tablica C++), karta i integracja HA biorą z niej wszystko; integracja i karta czytają ją z urządzenia (`/points`), więc nowy punkt nie wymaga zmian w HA ani w karcie.
2. **Import:** `python3 tools/import_pelletcan.py <PelletCAN_packages.yaml>` odtwarza z ESPHome tablicę nastaw (`rejestry/punkty.csv`, 81 pozycji: indeks, kodowanie, zakres, poziom). Po dodaniu nastawy w ESPHome uruchamiasz skrypt i widzisz w `git diff` tylko nowe wiersze.
3. **Czego skrypt nie przeniesie:** logiki w lambdach (moc kW, spalanie, prognoza, harmonogramy, test wyjść, PDO) – te elementy przepisujemy ręcznie w module `calc`.
