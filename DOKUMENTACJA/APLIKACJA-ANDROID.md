# Aplikacja Android — architektura rzeczywista

> Uzupełnienie do `docs/APLIKACJA_ANDROID.md` (ogólny opis funkcji — wciąż w większości aktualny). Sekcja
> "Ograniczenia" tamtego pliku pisze "aplikacja nie była jeszcze uruchamiana na prawdziwym telefonie" —
> **to jest już nieaktualne**: aplikacja działa na sprzęcie, OTA było wielokrotnie testowane i naprawiane na
> żywym kotle w listopadzie 2026 (patrz historia commitów: naprawa "resetów przy OTA" przez wstrzymanie
> pollingu dashboardu na czas otwartego okna urządzenia).

## Warstwa natywna (Kotlin) — `android/app/src/main/kotlin/pl/gieoerzet/teklapelletcan/`

| Plik | Rola |
|---|---|
| `MainActivity.kt` | Główna aktywność: WebView z interfejsem (`android/ui`), okno urządzenia (`openDeviceWindow`), obsługa zdarzeń `device_opened`/`device_closed` (wstrzymanie/wznowienie pollingu dashboardu — patrz niżej), watchdog ładowania z timeoutem i fallbackiem do cache. |
| `Backend.kt` | Model "backendu" (aktualnie wybranego/sparowanego urządzenia): adres, klucz, status demo. |
| `Discovery.kt` | Wyszukiwanie urządzeń w sieci (mDNS `_teklapelletcan._tcp`) + ręczny adres IP. |
| `Proxy.kt` | Pośredniczy między WebView a prawdziwym urządzeniem/API — jedno miejsce, przez które przechodzą wszystkie zapisy (egzekwuje blokadę zapisu, nie tylko interfejs). |
| `Http.kt` | Niskopoziomowy klient HTTP do komunikacji z ESP. |
| `Cache.kt` | Ostatnie znane odczyty (do pracy offline / ekranu "Brak połączenia z kotłem"); też źródło dla `cache.tpc` — fallbacku oryginalnej karty, gdy urządzenie jest nieosiągalne. |
| `Security.kt` | PIN aplikacji (PBKDF2 + sól), licznik błędnych prób z rosnącym opóźnieniem, (opcjonalnie) biometria. |
| `Store.kt` | Trwałe dane aplikacji (ustawienia, sparowane urządzenia). |
| `DemoHost.kt` | Tryb demo — wirtualny kocioł przez JNI do tego samego rdzenia C++ co firmware (`firmware/components/core`, skompilowany przez `android/app/src/main/cpp`). |
| `Native.kt` | Pomost JNI do rdzenia C++. |

## Warstwa interfejsu — `android/ui/js/` (ten sam kod co portal WWW urządzenia, patrz niżej)

| Plik | Rola |
|---|---|
| `main.js` | Punkt wejścia, routing, polling dashboardu (`pull()` co ~2 s), obsługa zdarzeń z warstwy natywnej (`onEvent`) — w tym `device_opened`/`device_closed` wstrzymujące/wznawiające polling, gdy otwarte jest okno "Panel kotła (oryginał)" lub "Konfiguracja urządzenia" (naprawa z tej sesji: OTA przez te okna konkurowało o ograniczone gniazda HTTP urządzenia z pollingiem dashboardu w tle). |
| `views.js` | Widoki/ekrany (pulpit, instalacja, nastawy, alarmy, parametry). |
| `store.js` | Stan po stronie JS (cache lokalny, ustawienia UI). |
| `theme.js` | Motyw ciemny/jasny/systemowy, styl Nowoczesny/Estyma. |
| `updates.js` | Logika sprawdzania aktualizacji (manifest, `parseVer`/`cmpVer` — patrz [`AKTUALIZACJE-OTA.md`](AKTUALIZACJE-OTA.md)). |
| `native.js` | Most do warstwy natywnej (Android) **lub** zwykły `fetch()` z parowaniem hasłem (portal urządzenia, `web/js/native.js`) — ten sam plik synchronizowany między dwoma miejscami przez `tools/sync_web.py`. |

**Ważne:** `android/ui/js/{store,ui,views,main,updates,theme}.js` + `style.css` są **synchronizowane** do
`web/js/` przez `tools/sync_web.py` (CI sprawdza to w kroku "Tabele wygenerowane aktualne" —
`python3 tools/sync_web.py --check`). Edytując którykolwiek z tych plików **zawsze uruchom
`python3 tools/sync_web.py`** przed commitem, inaczej CI czerwieni się na niezgodności (dokładnie taki błąd
zdarzył się w tej sesji przy poprawce pollingu). Plik `native.js` jest wyjątkiem — ma dwie różne, celowo
odmienne implementacje (Android JNI-bridge vs. zwykły `fetch()` portalu).

## "Panel kotła (oryginał)" i "Konfiguracja urządzenia" — jak to działa

Te dwa okna otwierają się jako WebView wskazujący **wprost na adres urządzenia** (`openDeviceWindow`), ładując
dokładnie tę samą kartę/portal co w przeglądarce (`web/classic.html`, `web/index.html` → ten sam silnik co
[karta Classic](ARCHITEKTURA-KARTY-CLASSIC.md)). To NIE jest osobny, natywny ekran Androida — to przeglądarkowy
WebView skierowany na żywe IP kotła. Stąd:
- gdy urządzenie jest nieosiągalne (np. telefon na transmisji komórkowej, poza siecią lokalną) — WebView dostaje
  błąd ładowania; naprawiono to przez watchdog z timeoutem 4 s (`DEVICE_LOAD_TIMEOUT_MS`) i fallback do
  `cache.tpc` (te same dane co ekran główny, z ostatniego znanego odczytu) zamiast gołego komunikatu o błędzie;
- gdy otwarte jest to okno, aplikacja **wstrzymuje polling dashboardu w tle** (zdarzenie `device_opened`), żeby
  nie konkurować o ograniczoną liczbę jednoczesnych gniazd HTTP urządzenia podczas wgrywania aktualizacji (OTA) —
  bez tego wgrywanie firmware kończyło się resetami urządzenia na prawdziwym sprzęcie.

## Budowa i podpis
Patrz `docs/APLIKACJA_ANDROID.md` §"Budowa" i §"Podpis APK" — te sekcje są aktualne i techniczne, bez zmian.
