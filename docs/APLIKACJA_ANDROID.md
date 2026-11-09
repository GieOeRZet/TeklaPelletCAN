# Aplikacja Android

Aplikacja (`teklapelletcan.apk` w wydaniu na GitHubie, Android 10+) jest **samodzielna**: jej interfejs (`android/ui`, HTML/JS) jest wbudowany w APK i działa także bez sieci. Z urządzeniem rozmawia wyłącznie natywna warstwa (Kotlin), która pilnuje blokady zapisu i zapamiętuje ostatnie odczyty.

## Co potrafi
- **Lista urządzeń**: wyszukiwanie przez mDNS (`_teklapelletcan._tcp`) albo ręczny adres IP; rozpoznaje to samo urządzenie po ID, gdy zmieni adres (DHCP); podsumowanie ostatnich wartości.
- **Pulpit** (kocioł z grafiką Tekli, palnik, CWU, CO, paliwo, alarm, temperatury), **Instalacja** (schemat zbiornik → palnik → kocioł → CO/CWU z wartościami na żywo), **Nastawy** (zadane i tryby kotła/CO/CWU), **Alarmy** (historia, potwierdzanie), **Wszystkie parametry** (generowane z opisu punktów urządzenia `/api/v1/points`, z poziomami dostępu).
- **Poziomy kotła 1 i 2** (PIN jak w panelu): okno z klawiaturą PIN, plakietka poziomu, autoblokada po 5 minutach bezczynności; pozycje wyższych poziomów oznaczone kłódką.
- **Tryb demo**: wirtualny kocioł (ten sam rdzeń C++ co w firmware przez JNI) z żywymi odczytami, bez sieci i bez kotła.
- **Oryginalna karta** i **konfiguracja urządzenia** (aktualizacja firmware, dziennik, Wi‑Fi, antena) – osobne okno z menu, dostępne tylko przy odblokowanej aplikacji.
- **Pełny ekran poziomo** (paski systemowe ukryte), układ pionowy z kafelkami.

## Bezpieczeństwo (jak działa blokada)
1. Przy pierwszym uruchomieniu ustawiasz **PIN aplikacji** (4–12 cyfr, zapis jako skrót PBKDF2 z solą; 5 błędów → blokada 30 s, rosnąca) i wybierasz, czy używać **odcisku palca** (domyślnie nie).
2. Bez odblokowania aplikacja jest w trybie **podglądu**: widać wszystkie wartości i parametry, ale żadne zapisy nie docierają do urządzenia (egzekwuje to natywny proxy, nie tylko interfejs).
3. Odblokowanie (PIN lub odcisk) trwa **5 minut od ostatniej aktywności**; kończy je też wyłączenie ekranu i wyjście z aplikacji. Aplikacja wraca wtedy na pulpit, a niezatwierdzona edycja jest odrzucana.
4. Poziom kotła (PIN 0900/0999) wymaga odblokowanej aplikacji; przy blokadzie aplikacja zdejmuje poziom kotła (poziom jest wspólny dla wszystkich klientów urządzenia).
5. Zapomniany PIN nie do odzyskania: „Usuń PIN i ustawienia bezpieczeństwa” w Ustawieniach aplikacji.

## Czas urządzenia i aktualizacje
- **Czas:** ESP nie ma internetu ani RTC, więc przy otwarciu urządzenia aplikacja ustawia mu zegar (`POST /api/v1/time`, dozwolone także w trybie podglądu). Urządzenie podaje `time` i `features` w `/api/v1/info`; aplikacja używa tylko funkcji, które firmware ma.
- **Aktualizacje:** aplikacja sprawdza manifest z gałęzi `updates` (ten sam co strona urządzenia). Baner o nowej aplikacji (lista zmian, „Pobierz APK”, strona wydania) pokazuje się na liście urządzeń i w Ustawieniach aplikacji; baner o nowym firmware urządzenia (lista zmian, „Zainstaluj w konfiguracji”) – na pulpicie. „Później” odkłada baner dla danej wersji. Sekcja `app` w manifeście powstaje przy wydaniu stabilnym (`make_manifest.py --app-tag`).

## Poza domem
Gdy urządzenie jest nieosiągalne, aplikacja pokazuje **ostatnie znane wartości** z godziną i wyraźnym banerem „Brak połączenia z kotłem”, a sterowanie jest niedostępne.

## Budowa
Android SDK pobiera CI (`.github/workflows/ci.yml`, zadanie `android`): `cd android && ./gradlew assembleRelease`. Lokalnie: JDK 17, Android SDK (platforma 35, NDK, CMake).
`web/` (oryginalna karta, strony urządzenia) i `android/ui` (nowy interfejs) trafiają do `assets` przy budowie (`syncAssets`), rdzeń firmware (`firmware/components/core`) kompiluje CMake (`android/app/src/main/cpp`).

## Podpis APK
Sekrety CI: `ANDROID_KEYSTORE_B64`, `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD`. Bez nich podpis robi klucz testowy z repozytorium, a **wydanie odmówi publikacji** takiego APK (zabezpieczenie w `github-release`). Klucz trzymaj poza repozytorium (kopia w menedżerze haseł) – bez niego nie da się aktualizować zainstalowanych aplikacji.

## Testy
- `android/jvmtest` (JVM): bramka zapisu, PIN i blokada prób, cache, proxy (`./gradlew -p jvmtest run`).
- `android/test/e2e_ui.js` (Chromium + atrapa mostu natywnego + `demo_server`): pierwsze uruchomienie, PIN, pulpit, instalacja, zapis po odblokowaniu, poziomy kotła, wygasanie po 5 min, tryb offline z ostatnimi danymi, menu, ustawienia aplikacji.
- `android/test/e2e_app.js`: oryginalna karta i konfiguracja w trybie demo.
- Warstwa JNI i Kotlin: kompilacja w CI z prawdziwym SDK; zachowanie na telefonie – patrz „Ograniczenia”.

## Ograniczenia / do zrobienia
- Aplikacja nie była jeszcze uruchamiana na prawdziwym telefonie. Wyszukiwanie mDNS działa tylko w tej samej podsieci/VLAN co telefon.
- Parytet z oryginalną kartą: ekrany Konfiguracja / Test wyjść / Statystyki / Sieć / harmonogramy są na razie dostępne przez „Panel kotła (oryginał)” i „Wszystkie parametry”; kolejne przenoszone do nowego stylu etapami (patrz `docs/TODO.md`).
- Do zrobienia: instalacja aktualizacji aplikacji bez wychodzenia do przeglądarki, powiadomienia o alarmach (+ endpoint `/api/v1/summary`, blueprint HA), widżet.
- Test dymny na prawdziwym emulatorze Androida (`android-emulator` w CI): zrzuty ekranu trafiają na gałąź `ci-screens`.
