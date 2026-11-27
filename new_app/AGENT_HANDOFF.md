# TeklaPelletCAN — Android NEW APP — dokumentacja przekazania dla agenta

Stan dokumentacji: 2026-11-27
Repozytorium: GieOeRZet/TeklaPelletCAN
Gałąź aplikacji: android-new-app

## 1. CEL

Budujemy nową aplikację Android TeklaPelletCAN do obsługi modułu ESP32/CAN sterującego kotłem Tekla/Estyma.

Docelowo aplikacja ma:
- łączyć się z modułem,
- wykrywać go przez BLE oraz Wi-Fi/mDNS,
- pozwalać na ręczne dodanie adresu IP,
- obsługiwać konfigurację nowego modułu przez jego AP,
- prezentować stan kotła i instalacji,
- sterować kotłem,
- udostępniać parametry, harmonogramy, alarmy i test wyjść,
- działać offline z ostatnim cache,
- mieć PIN/biometrię,
- używać tego samego UI co webowy portal urządzenia.

Najważniejsza reguła UX:

### Brak modułu
Po pierwszym uruchomieniu aplikacja pokazuje DEMO / wirtualny kocioł. Na pulpicie ma być wyraźny przycisk „＋ Dodaj moduł”.

### Moduł dodany
Po dodaniu prawdziwego modułu DEMO znika całkowicie z pulpitu. Urządzenie można zmieniać/dodawać także przez Menu.

## 2. DOCELOWY INTERFEJS

Styl: nowoczesny, ciemny, techniczny, czytelny, z pomarańczowym akcentem Tekla.

Jest też drugi styl: Panel kotła (oryginał), związany z odwzorowaniem interfejsu Estyma.

Pulpit:
- Kocioł: temperatura, zadana, powrót, zewnętrzna, tryb, stan.
- Palnik: stan, moc %, moc kW, temperatura, dmuchawa, podajnik.
- CWU: temperatura, zadana, pompa.
- CO: temperatura, zadana, pompa, mieszacz.
- Paliwo: ilość, pojemność, %, prognoza.
- Alarm: aktualny/ostatni alarm.
- Komunikacja: CAN i online/offline.

Obecne dane DEMO:
64,8 °C kocioł, 60 °C zadana, 41,9 °C powrót, -3 °C zewnętrzna, CWU 53,9/55 °C, CO 49,8/45 °C, paliwo 28/135 kg, 21%, prognoza 3 dni.

## 3. NAWIGACJA

Dolny pasek:
- Pulpit
- Instalacja
- Harmonogram
- Alarmy
- Menu

Dodatkowe ekrany:
Kocioł, Palnik, CO, CWU, Test wyjść, Konfiguracja, Parametry, Harmonogram, Alarmy i historia, Zbiornik paliwa, Zasilanie i tryby, Ustawienia aplikacji, Motyw i styl, Tryb developera.

Instalacja ma docelowo pokazywać schemat:
zbiornik paliwa → palnik → kocioł → CO/CWU.

## 4. DODAWANIE URZĄDZENIA

Trzy drogi:
1. Automatyczne wykrywanie: BLE oraz Wi-Fi/mDNS.
2. Ręczny IP: aplikacja odpytuje GET /api/v1/info i potwierdza TeklaPelletCAN.
3. Nowe urządzenie/AP: telefon łączy się z TeklaPelletCAN-XXXX i uruchamia konfigurację.

Lista urządzeń ma obsługiwać:
- zapisane urządzenia,
- znalezione urządzenia,
- online/offline,
- firmware,
- temperaturę kotła,
- zmianę nazwy,
- usunięcie.

## 5. BEZPIECZEŃSTWO

PIN aplikacji: 4–12 cyfr, opcjonalna biometria, blokada przy starcie, zmiana PIN i reset.

PIN aplikacji ma chronić sterowanie, ale zwykły podgląd i dodawanie urządzeń mają być dostępne bez PIN.

Poziom kotła:
- poziom 1: 0900
- poziom 2: 0999

Funkcje serwisowe, Konfiguracja i Test wyjść mają być widoczne dopiero po odblokowaniu odpowiedniego poziomu.

## 6. OFFLINE / CACHE

Aplikacja ma zapamiętywać ostatnie dane, pokazywać podgląd offline, jasno oznaczać brak połączenia i pozwalać wyczyścić cache.

## 7. ARCHITEKTURA — WAŻNE

Pierwsza wersja nowej aplikacji była robiona w Compose, ale była zbyt uproszczona i nie odpowiadała uzgodnionemu UI.

Kierunek został zmieniony.

Obecna architektura:

Android Activity
→ WebView
→ istniejące android/ui
→ JavaScript
→ natywny most TPCNative
→ REST/API urządzenia

Nie należy teraz pisać drugiego niezależnego UI w Compose.

Źródłem interfejsu jest istniejące android/ui.

## 8. SYNCHRONIZACJA UI DO APK

Plik: new_app/app/build.gradle.kts

Zadanie syncUiAssets kopiuje ../android/ui do assetów APK.

Wykluczone są index.html i style.css, bo ich wersje aplikacyjne są w new_app/app/src/main/assets/.

preBuild zależy od syncUiAssets.

Dzięki temu Android używa tego samego UI co portal/web.

## 9. MAIN ACTIVITY

Plik:
new_app/app/src/main/kotlin/pl/gieoerzet/teklapelletcan/newapp/MainActivity.kt

MainActivity:
- hostuje WebView,
- włącza JavaScript i DOM storage,
- ładuje file:///android_asset/index.html,
- rejestruje TPCNative,
- obsługuje Android Back,
- wybór urządzenia,
- DEMO,
- HTTP do urządzenia,
- /api/v1/info,
- demonstracyjne /api/v1/states.

## 10. OSTATNIA POPRAWKA KODU

Commit:
caf9d9b520e8d48a12e47f0a124a12c519b8f57c

Opis: Fix NEW app demo startup and device ping

Zrobiono:
- przy braku realnego modułu selectedBase = demo://,
- selectedName = Demo – wirtualny kocioł,
- zapis real_module=false,
- start do #/d/pulpit,
- selectDevice normalizuje demo i demo://,
- ping DEMO zwraca wirtualne ID/FW,
- ping prawdziwego modułu robi GET /api/v1/info z timeoutem,
- odpowiedź przekazywana jest do window.tpcPing.

## 11. DIAGNOSTYKA STARTU

android/ui/index.html ma diagnostykę JS:
- window.error,
- unhandledrejection,
- timeout 6 s.

Zamiast czarnego ekranu ma pojawić się komunikat „Błąd uruchomienia interfejsu” i treść błędu.

## 12. MAIN.JS — CO JUŻ JEST

android/ui/js/main.js zawiera:
- router,
- pulpit,
- instalację,
- menu,
- listę urządzeń,
- ręczny IP,
- discovery UI,
- DEMO,
- PIN UI,
- poziomy kotła,
- parametry,
- harmonogram,
- alarmy,
- test wyjść,
- konfigurację,
- cache UI,
- aktualizacje,
- ustawienia wyglądu,
- ustawienia aplikacji.

android/ui/js/native.js jest cienką warstwą nad TPCNative i obsługuje request/response oraz urządzenia.

## 13. WAŻNE: PLACEHOLDERY

Aplikacja nie jest jeszcze produkcyjna.

W MainActivity nadal są placeholdery:
- getDevices() zwraca obecnie [],
- saveDevices() nic nie zapisuje,
- startDiscovery() jest pusty,
- stopDiscovery() jest pusty,
- część PIN/biometrii jest placeholderem,
- deviceSummary() zwraca {},
- konfiguracja urządzenia przez natywny most nie jest kompletna,
- BLE nie jest jeszcze spięte z realnym discovery,
- mDNS/Wi-Fi discovery nie jest jeszcze spięte z realnym discovery.

UI dla tych funkcji istnieje, ale backend natywny wymaga dalszej implementacji.

Nie wolno twierdzić, że BLE/discovery/PIN/biometria są gotowe tylko dlatego, że mają ekrany.

## 14. GRADLE

new_app/app/build.gradle.kts:
- namespace pl.gieoerzet.teklapelletcan.newapp
- applicationId pl.gieoerzet.teklapelletcan.newapp
- compileSdk 35
- minSdk 29
- targetSdk 35
- versionCode 3
- versionName 0.3.0
- Java 17
- Kotlin JVM 17
- minifikacja wyłączona.

## 15. CI

Workflow:
.github/workflows/new-app.yml

Nazwa: TeklaPellet NEW APP

Push na android-new-app oraz zmiany new_app/** lub workflow uruchamiają:
1. build,
2. smoke emulator.

Build:
gradle -p new_app :app:assembleDebug --no-daemon

Artifact:
TeklaPellet-NEW-debug

Smoke:
- API 30,
- google_apis,
- x86_64,
- Pixel 2,
- SwiftShader,
- bez okna,
- bez snapshotu,
- bez audio,
- bez animacji.

Smoke ma:
1. zainstalować APK,
2. uruchomić MainActivity,
3. sprawdzić PID,
4. sprawdzić aktywną Activity,
5. wykonać screenshot,
6. zebrać logcat i dumpsys.

## 16. HISTORIA PROBLEMÓW CI

Problem assetów:
index.html/style.css były kopiowane podwójnie. Naprawiono przez exclude w syncUiAssets.

Problem Kotlin:
Discovery.kt importował ContextCompat bez zależności androidx.core. Zmieniono na context.checkSelfPermission.

Commit:
df198c15dd0afa6d9f8d8571cb7d5761b2990cb2

Problem emulatora:
pierwotnie użyto -accel off. Runner zgłaszał:
Software CPU emulation (-accel off) is not supported.

Naprawa:
ANDROID_I_WANT_MY_TCG=yes i usunięcie -accel off.

Commit:
83646a777c6e722ab46eeba81b922d8218b02c0e

Następnie API 34 zmieniono na API 30, żeby emulator był lżejszy.

Commit:
56e208a86f14394811d1247150bd416002cbd5af

Run 25:
45905924832

Build przeszedł, ale smoke nadal nie uzyskał poprawnie uruchomionego emulatora / bootu.

To nie było potwierdzenie crashu aplikacji. Był to problem środowiska emulatora.

## 17. NAJWAŻNIEJSZY GATE AKCEPTACYJNY

APK NIE jest gotowe tylko dlatego, że Gradle jest zielone.

Wymagane:
1. build,
2. uruchomienie Android Emulatora,
3. instalacja APK,
4. start MainActivity,
5. PID,
6. aktywna Activity,
7. prawdziwy screenshot,
8. wizualna inspekcja screenshotu,
9. porównanie z uzgodnionym UI,
10. poprawki,
11. ponowny test,
12. ponowny screenshot.

Dopiero wtedy APK może być nazwane gotowym.

Użytkownik wyraźnie powiedział, że bez przejścia emulatora i sprawdzenia wyglądu aplikacja jest dla niego nieużyteczna.

## 18. OSTATNI APK

Z Run 25 pobrano artifact TeklaPellet-NEW-debug i przekazano użytkownikowi.

APK było zbudowane, ale NIE było emulatorowo zweryfikowane.

Użytkownik zgłosił, że aplikacja nie działa.

Tamten APK należy traktować jako niewiarygodny build testowy, nie jako wersję referencyjną.

## 19. PLAN DALSZYCH PRAC

ETAP A — uruchomienie:
- doprowadzić emulator CI do bootu,
- zainstalować aktualny APK,
- zrobić screenshot,
- sprawdzić DEMO,
- sprawdzić „＋ Dodaj moduł”,
- sprawdzić ekran 1080×2400,
- sprawdzić dolny kafel Zasilanie,
- sprawdzić pełne „z 135 kg”.

ETAP B — backend natywny:
- lista urządzeń,
- zapis urządzeń,
- BLE,
- mDNS,
- ręczny IP,
- AP setup,
- PIN,
- biometria,
- cache,
- summary,
- otwieranie konfiguracji.

ETAP C — realne API:
Android UI → TPCNative → HTTP/REST → ESP32 → CAN → Estyma.

ETAP D — bezpieczeństwo:
PIN, biometria, poziomy 1/2, timeout, bezpieczne przechowywanie.

ETAP E — discovery:
BLE, mDNS, Wi-Fi, ręczny IP, AP.

ETAP F — offline/cache.

ETAP G — OTA.

## 20. STAN

ZROBIONE:
- osobna gałąź android-new-app,
- osobny moduł new_app,
- WebView host,
- TPCNative,
- integracja android/ui,
- synchronizacja UI do APK,
- dashboard DEMO,
- dane DEMO,
- menu,
- nawigacja,
- ekrany,
- UI listy urządzeń,
- UI ręcznego IP,
- UI discovery,
- UI AP setup,
- UI PIN/biometrii,
- UI cache,
- UI aktualizacji,
- diagnostyka JS,
- poprawiony start DEMO,
- poprawiony ping,
- Gradle build w CI,
- smoke workflow i diagnostyka.

NIEZROBIONE / NIEPOTWIERDZONE:
- działający emulator CI,
- screenshot aktualnego APK,
- wizualna akceptacja aktualnego APK,
- pełne BLE,
- pełne mDNS,
- natywne zapisywanie urządzeń,
- pełny PIN/biometria,
- pełny cache,
- pełny backend API,
- OTA end-to-end,
- wersja produkcyjna.

## 21. INSTRUKCJA DLA NASTĘPNEGO AGENTA

Nie zaczynać Androida od zera.
Nie zastępować aktualnego UI kolejnym uproszczonym Compose mockupem.

Najpierw przeczytać:
- new_app/AGENT_HANDOFF.md
- android/ui/js/main.js
- android/ui/js/native.js
- android/ui/index.html
- new_app/app/src/main/kotlin/pl/gieoerzet/teklapelletcan/newapp/MainActivity.kt
- new_app/app/build.gradle.kts
- .github/workflows/new-app.yml

Sprawdzić aktualny HEAD android-new-app.

Pierwsze zadanie:
doprowadzić aktualny APK do realnego uruchomienia na emulatorze, zdobyć screenshot i sprawdzić wizualnie aplikację.

Dopiero potem kontynuować implementację backendu natywnego i integrację z ESP32.
