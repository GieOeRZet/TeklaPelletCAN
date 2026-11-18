# Poziomy dostępu (PIN 0900/0999) — cztery niezależne implementacje i cztery błędy znalezione w listopadzie 2026

Urządzenie ma trzy poziomy dostępu (0/1/2), identyczne jak w fizycznym panelu Igneo Touch: poziom 1 = PIN `0900`
(klucz 1), poziom 2 = PIN `0999` (klucz 2). Stan jest w encji/punkcie `sensor.tekla_poziom_dostepu` (silnik:
`firmware/components/core/access.*`), wspólny dla wszystkich klientów naraz (nie jest per-klient). Usługa zapisu:
`tekla_estyma_unlock` (`POST /api/v1/call`, `data.pin`).

**Cztery niezależne implementacje** tego samego mechanizmu — każda ma swój własny kod sprawdzający/czekający na
potwierdzenie nowego poziomu, **nie jest to jeden współdzielony moduł**:

| Gdzie | Plik | Jak potwierdza nowy poziom po PIN-ie |
|---|---|---|
| Aplikacja Android + portal WWW (ten sam kod) | `android/ui/js/ui.js` / `web/js/ui.js`, `ensureLevel()`/`enterLevelPin()` | Pętla do 10× po 400 ms, odpytuje `GET /api/v1/states` |
| Karta Classic (HA) | `web/teklapelletclassic-engine.js`, `_pinOk()`/`_lvl()` | Brak czekania — czyta `this._v('acc')` z `hass` na żywo, HA sam odświeży po zmianie stanu |
| Karta Modern (HA) | `web/teklapelletmodern-card.js`, `_ensureLevel()` | Pętla do 10× po 400 ms, czyta `this.level()` z `hass` (do v1.0.8: jedno sztywne 700 ms) |

## Błąd 1 (naprawiony w v1.0.6→v1.0.7): `crypto.subtle` wymaga "bezpiecznego kontekstu"

Dotyczy wyłącznie PIN-u `1948` (ukryte wejście do trybu developera, osobny mechanizm od prawdziwych PIN-ów
poziomu — patrz [`AKTUALIZACJE-OTA.md`](AKTUALIZACJE-OTA.md)). `isDevPin()` haszował PIN przez Web Crypto
(`crypto.subtle.digest`), dostępne tylko w HTTPS/`localhost`/`127.0.0.1` — strona urządzenia w realnej sieci
domowej to zwykły `http://<ip>`, gdzie `crypto.subtle` jest `undefined`. **Każdy** PIN (nie tylko `1948`) kończył
się tam nieobsłużonym wyjątkiem. Własne testy (Playwright na `127.0.0.1`) tego nie złapały — przeglądarka
traktuje `127.0.0.1` jako wyjątkowo bezpieczny mimo HTTP. Fix: prosty, synchroniczny hash FNV-1a, zero zależności
od kontekstu bezpieczeństwa.

## Błąd 2 (naprawiony w v1.0.7): POST zgłaszał sukces, zanim GET zaczynał widzieć nowy poziom

Odpowiedź `POST /api/v1/call` (unlock) ma już **aktualny** poziom — silnik (`Access::unlock()`) aktualizuje go
synchronicznie. Ale osobny `GET /api/v1/states`, na którym opiera się cała reszta UI (`pull()`/`pullNow()`), mógł
pokazywać **starą** wartość jeszcze przez ok. 2 s po udanym odblokowaniu. Pętle potwierdzające w `ensureLevel()`/
`enterLevelPin()` startowały `cur` od `r.json.level` (wartości z POST) — jeśli POST już zgłosił sukces, warunek
pętli `cur < need` był od razu fałszywy i pętla (która miała czekać na GET) **nigdy się nie wykonywała**. Fix:
`cur` zawsze startuje od `0` — zawsze czekamy na prawdziwe potwierdzenie przez GET, niezależnie od tego, co już
zgłosił POST. Zweryfikowane testem z instrumentacją `page.route()` logującą dokładne znaczniki czasu każdego
POST/GET.

## Błąd 3 (naprawiony w v1.0.8): Android — pętla ufała podstawionej odpowiedzi z cache

Natywna warstwa Androida (`Proxy.kt`) ma pamięć podręczną: gdy urządzenie jest **chwilowo** nieosiągalne (typowe
poza domem, słabe/przerywane połączenie — **nie** pełny offline, bo wtedy `POST` od razu zwraca 503 i pętla w
ogóle się nie uruchamia), `GET /api/v1/states` **nie zwraca błędu**, tylko podstawia ostatni zapamiętany odczyt
ze statusem 200, bez żadnego oznaczenia dla JS poza polem `cachedAt` (które mostek `MainActivity.kt` już
przekazywał, ale pętla go nie sprawdzała). Jeśli trafiło to w pętlę potwierdzającą tuż po PIN-ie `0999`, pętla
widziała stary, zapamiętany poziom (np. 1 z poprzedniej sesji w domu) i uznawała to za wynik — mimo że urządzenie
naprawdę ustawiło już poziom 2. Fix: pętla w `ensureLevel()`/`enterLevelPin()` odrzuca odpowiedzi z `cachedAt > 0`
(traktuje jak brak potwierdzenia, próbuje dalej), zamiast ufać staremu, podstawionemu odczytowi.

## Błąd 4 (naprawiony w v1.0.8): Karta Modern — jedno sztywne 700 ms było za krótkie zdalnie

`_ensureLevel()` potwierdzał nowy poziom jednym, sztywnym odczekaniem 700 ms przed odczytem `this.level()` z
`hass`. Trasa urządzenie → integracja HA → websocket do przeglądarki czasem zajmuje dłużej niż 700 ms (zdalny
dostęp przez chmurę/VPN, większe opóźnienie niż w lokalnym Wi-Fi) — karta czytała jeszcze stary poziom i
pokazywała "Ten PIN daje tylko poziom 1", mimo że urządzenie już ustawiło 2. Fix: krótka pętla powtórzeń (do
~10×400 ms), jak w appce/portalu, zamiast jednego, za krótkiego okna czasowego.

## Dla kogoś, kto dodaje piątą implementację (lub naprawia szóstego buga)

Każda z czterech implementacji ma **własną** logikę potwierdzania — nie ma wspólnego modułu "poczekaj na nowy
poziom". Jeśli zgłoszony zostanie podobny problem ("PIN daje niższy poziom niż powinien", zwłaszcza "zdalnie"/
"czasem"/"poza domem"), sprawdź **w kolejności**: (1) czy w ogóle czeka na jakiekolwiek potwierdzenie, czy ufa
pierwszej odpowiedzi; (2) czy odróżnia świeży odczyt od podstawionego/cache'owanego (tylko Android ma to
ryzyko — `cachedAt`); (3) czy okno czasowe/liczba prób jest wystarczająca na realne opóźnienie sieci, nie tylko
na lokalny LAN.
