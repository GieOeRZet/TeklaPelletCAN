# Aktualizacje (OTA) — kanał stabilny domyślnie, ukryty tryb developera

## Co się zmieniło (listopad 2026)

Wcześniej `web/settings.html` ("Konfiguracja urządzenia") miał widoczny wybór kanału aktualizacji
(beta/stabilny) dla każdego użytkownika, z domyślnym kanałem **beta**. Zmieniono na: zwykły użytkownik **nigdy**
nie widzi wyboru kanału i zawsze dostaje/instaluje tylko kanał **stabilny**. Wybór kanału beta jest dostępny
wyłącznie po odblokowaniu ukrytego "trybu developera".

## Trzy miejsca, w których żył domyślny kanał `'beta'` (wszystkie poprawione)

Przy wdrażaniu tej zmiany okazało się, że domyślny kanał `'beta'` był zaszyty w **trzech niezależnych**
miejscach w kodzie — łatwo przeoczyć jedno z nich:

1. `web/settings.html` — ręczny wybór kanału w "Aktualizacji oprogramowania" (teraz ukryty, domyślnie `stable`).
2. `web/update.js` — funkcja `channel()` (logika pobierania/wgrywania pliku firmware).
3. `web/teklapelletclassic-engine.js` — funkcja `CHAN()` wewnątrz modułu ekranu "Informacje o programie" karty
   (osobny, niezależny mechanizm sprawdzania aktualizacji, czytający ten sam manifest).

`web/js/updates.js` (baner "dostępna aktualizacja" na pulpicie aplikacji/portalu, współdzielony z Androidem)
**już wcześniej** czytał tylko `channels.stable`, bez żadnego wyboru — nie wymagał zmiany.

**Wniosek dla kogoś, kto to kontynuuje:** jeśli szukasz, gdzie jeszcze może żyć logika kanału beta/stabilny,
szukaj `tpc_channel`/`CHAN(` wszędzie, nie tylko w jednym oczywistym miejscu — mechanizm sprawdzania aktualizacji
nie jest scentralizowany (trzy niezależne implementacje czytające ten sam manifest, z historycznych powodów).

## Ukryty dostęp do trybu developera — PIN "1948"

Zamiast osobnego, widocznego przełącznika, dostęp do trybu developera ukryto za **ekranem "Poziom kotła"**
(menu aplikacji/portalu — ten sam ekran, w którym normalnie wpisuje się PIN poziomu dostępu 0900/0999, jak w
fizycznym panelu kotła):

- PIN **`1948`** wpisany na tym ekranie **nie jest wysyłany do kotła** — rozpoznawany jest po stronie klienta
  (`android/ui/js/ui.js`, funkcja `enterLevelPin()`), zanim cokolwiek trafi do urządzenia.
- PIN jest przechowywany jako **hash SHA-256** (`DEV_PIN_SHA256` w `ui.js`), nie jawnym literałem — nie da się
  go odczytać wprost z kodu źródłowego (grep/diff pokaże tylko ciąg hex skrótu).
- Po rozpoznaniu: nawigacja do nowego ekranu `#/d/dev` ("Tryb developera"), zapis `localStorage.tpc_devmode = '1'`
  (zapamiętane na tym urządzeniu/przeglądarce — nie trzeba wpisywać PIN-u za każdym razem).
- Zwykłe PIN-y poziomu (0900/0999, i wszystkie inne) działają bez zmian — `1948` nigdy nie koliduje z prawdziwym
  PIN-em poziomu, bo jest sprawdzany jako pierwszy, przed wysłaniem czegokolwiek do kotła.

## Ekran "Tryb developera" (`devMode()` w `views.js`)

Pokazuje wybór kanału (`localStorage.tpc_channel`, odczytywany przez wszystkie trzy miejsca wymienione wyżej) i
przycisk "Otwórz konfigurację urządzenia". **Nie duplikuje logiki pobierania/wgrywania firmware** — to wciąż
robi `web/settings.html` (już przetestowany, pełny mechanizm OTA), ten ekran tylko ustawia kanał i tam odsyła.

## Most między originami (aplikacja Android)

Portal WWW nie ma problemu: ekran "Poziom kotła" i `settings.html` są na tym samym originie (serwowane przez to
samo urządzenie), więc `localStorage.tpc_devmode`/`tpc_channel` ustawione w jednym miejscu są od razu widoczne w
drugim.

**Aplikacja Android ma inny problem**: natywny interfejs (`android/ui`, zasoby w APK) i "Konfiguracja urządzenia"
(WebView wskazujący wprost na `http://<adres-urządzenia>/settings.html`) to **dwa różne originy** — osobne
`localStorage`. Rozwiązanie: `nat.openDeviceSettings()` (`android/ui/js/native.js`) sprawdza lokalny
`tpc_devmode` i, jeśli aktywny, prosi warstwę natywną (Kotlin, `MainActivity.kt` →
`openDeviceSettings(dev: Boolean)`) o otwarcie `settings.html?dev=1` zamiast samego `settings.html`.
`settings.html` odczytuje `?dev=1` z adresu (oprócz swojego własnego `localStorage.tpc_devmode`, na wypadek gdy
ktoś otworzy tę stronę bezpośrednio w przeglądarce na urządzeniu) i dopiero wtedy odkrywa ukryty wybór kanału.

## Dwa dodatkowe błędy znalezione i naprawione przy okazji (PIN poziomu/trybu developera)

**1. `crypto.subtle` wymaga "bezpiecznego kontekstu".** `isDevPin()` pierwotnie używał Web Crypto
(`crypto.subtle.digest`) do haszowania PIN-u. Ten interfejs działa tylko w HTTPS albo
`localhost`/`127.0.0.1` — strona urządzenia w realnej sieci domowej to zwykły `http://<adres-ip>`, gdzie
`crypto.subtle` jest `undefined`. Każdy PIN (nie tylko `1948`) kończył się tam nieobsłużonym wyjątkiem.
Własne testy tego nie złapały, bo używały `127.0.0.1` (traktowany przez przeglądarkę jako wyjątkowo
bezpieczny mimo HTTP). Naprawione: prosty, synchroniczny hash FNV-1a, bez żadnej zależności od kontekstu
bezpieczeństwa.

**2. Komunikat po PIN-ie pokazywał poprzedni poziom przez ok. 2 sekundy.** Odpowiedź `POST /api/v1/call`
(`tekla_estyma_unlock`) zwraca już **aktualny** poziom (silnik aktualizuje go synchronicznie) — ale osobny
endpoint `GET /api/v1/states` (na którym opiera się cała reszta interfejsu: `pull()`, `pullNow()`) potrafi
pokazywać **starą** wartość jeszcze przez około 2 sekundy po udanym odblokowaniu. Kod w `ensureLevel()`/
`enterLevelPin()` miał pętlę czekającą właśnie na to potwierdzenie przez GET — ale startowała od
`r.json.level` (wartości z POST), więc jeśli POST już zgłosił sukces, pętla z warunkiem `cur < need` nigdy
się nie wykonywała i funkcja zwracała sukces, **zanim** GET faktycznie zaczął widzieć nowy poziom. Fix:
`cur` zawsze startuje od `0` — zawsze czekamy na GET-owe potwierdzenie, niezależnie od tego, co już zgłosił
POST. Dodano też `pausePolling()`/`resumePolling()` (`store.js`) wokół obu funkcji jako dodatkowe
zabezpieczenie przed współbieżnym, działającym w tle odpytywaniem (`setInterval(pull, 2000)`), które mogłoby
nadpisać świeży stan starszą odpowiedzią — ten sam wzorzec co przy naprawie OTA-vs-pollingu wcześniej w tym
projekcie.

## Zasięg zmiany (pliki)

`android/ui/js/ui.js`, `android/ui/js/main.js`, `android/ui/js/views.js`, `android/ui/js/store.js`
(+ zsynchronizowane kopie w `web/js/` przez `tools/sync_web.py` — `native.js` jest wyjątkiem, ma dwa celowo
różne warianty), `web/settings.html`, `web/update.js`, `web/teklapelletclassic-engine.js`,
`android/app/src/main/kotlin/.../MainActivity.kt`. Testy regresyjne: `web/test/e2e_device_ui.js` (sekcje
"PIN poziomu" i "tryb developera").
