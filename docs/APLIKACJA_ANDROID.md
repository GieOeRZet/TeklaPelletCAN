# Aplikacja Android

Aplikacja (`teklapelletcan.apk` w wydaniu na GitHubie, Android 10+) to:

- **Lista urządzeń** – urządzenia z sieci wyszukuje sama (mDNS, `_teklapelletcan._tcp`), można też wpisać adres IP. Zmiana adresu po DHCP jest rozpoznawana po ID urządzenia.
- **Widok urządzenia** – ta sama strona, którą serwuje samo urządzenie: pełna karta kotła (z grafikami Estymy, PIN-y 0900/0999), Ustawienia, aktualizacja firmware, dziennik i raport (zapis do „Pobrane” + udostępnianie).
  Dzięki temu aplikacja zawsze pokazuje to, co umie firmware w urządzeniu – nie trzeba osobno aktualizować aplikacji przy nowych funkcjach.
- **Konfiguracja nowego urządzenia** – po połączeniu telefonu z siecią `TeklaPelletCAN-XXXX` aplikacja otwiera portal pierwszej konfiguracji (`10.77.77.1`) i kieruje ruch przez Wi‑Fi, także gdy ta sieć nie ma internetu.
- **Tryb demo** – wirtualny kocioł z żywymi odczytami. Działa bez sieci: w aplikacji pracuje **ten sam rdzeń C++ co w firmware** (silnik, API, tabele punktów – biblioteka natywna przez JNI), więc karta, zapisy, PIN-y, ustawienia i dziennik zachowują się jak na prawdziwym urządzeniu. Nic nie jest wysyłane do żadnego kotła.

Hasło urządzenia (do parowania) jest potrzebne tylko wtedy, gdy w Ustawieniach wyłączysz „Panel WWW bez hasła”; wtedy aplikacja zapyta o nie przy pierwszej zmianie (okno dialogowe).

## Budowa

Android SDK pobiera CI (`.github/workflows/ci.yml`, zadanie `android`): `cd android && ./gradlew assembleRelease`. Lokalnie potrzebne są JDK 17, Android SDK (platforma 35, NDK, CMake).
Strony z `web/` oraz powłoka z `android/shell/` są kopiowane do `assets` przy budowie (zadanie `syncAssets`), a rdzeń firmware (`firmware/components/core`) kompiluje CMake (`android/app/src/main/cpp`).

## Podpis APK

Bez sekretów CI podpis robi klucz **testowy** z repozytorium (`android/dev-release.jks`, hasło `tekla-dev`). Do wydań docelowych ustaw sekrety `ANDROID_KEYSTORE_B64`, `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD`. Zmiana klucza oznacza konieczność odinstalowania aplikacji (Android nie pozwala aktualizować pliku podpisanego innym kluczem).

## Testy

- `android/test/e2e_app.js` (Chromium): powłoka (wyszukiwanie, dodawanie, duplikaty, zmiana adresu, usuwanie) i tryb demo (karta, żywe odczyty, PIN, zapis nastawy, ustawienia, dziennik). Serwer `demo_server` (`firmware/test/demo_server.cpp`) używa dokładnie tej samej klasy `DemoDevice`, którą wywołuje JNI.
- Warstwa JNI i kod Kotlin sprawdzane są kompilacją (Kotlin względem frameworka Android 15) i próbą z JVM; pełne zachowanie na telefonie – patrz „Ograniczenia”.

## Ograniczenia / do zrobienia

- Aplikacja nie była jeszcze uruchamiana na prawdziwym telefonie (CI tylko buduje APK). Wyszukiwanie mDNS (NSD) działa tylko w tej samej podsieci/VLAN co telefon.
- Powiadomienia o alarmach w tle (wymaga usługi pierwszoplanowej albo pushy) – do zrobienia.
- Samoaktualizacja aplikacji – na razie ręcznie z wydania GitHub.
