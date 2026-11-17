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

## Zasięg zmiany (pliki)

`android/ui/js/ui.js`, `android/ui/js/main.js`, `android/ui/js/views.js` (+ zsynchronizowane kopie w `web/js/`
przez `tools/sync_web.py` — `native.js` jest wyjątkiem, ma dwa celowo różne warianty), `web/settings.html`,
`web/update.js`, `web/teklapelletclassic-engine.js`, `android/app/src/main/kotlin/.../MainActivity.kt`. Test
regresyjny: `web/test/e2e_device_ui.js` (sekcja "tryb developera").
