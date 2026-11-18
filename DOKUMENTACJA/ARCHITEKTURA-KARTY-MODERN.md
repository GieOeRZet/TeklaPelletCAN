# Architektura karty Modern — prosta, bez patchowania (w przeciwieństwie do Classic)

W przeciwieństwie do karty Classic ([`ARCHITEKTURA-KARTY-CLASSIC.md`](ARCHITEKTURA-KARTY-CLASSIC.md), która
patchuje tekstowo obcą bazę `tekla-panel-card.js`), karta Modern to **jeden, samodzielny plik**
(`web/teklapelletmodern-card.js`) napisany od zera, bez żadnej bazy do patchowania — żaden z pułapek/ograniczeń
opisanych w dokumencie o Classic tu nie dotyczy. To jedyny plik ładowany przez HACS (`hacs.json`), standardowy
HA custom element (`customElements.define`), import ES-modułowy (nie globalny `<script>`).

## Jak karta znajduje urządzenie i adresuje punkty

Tak samo jak Classic — przez rejestr urządzeń HA (`hass.devices`, filtr po domenie integracji `teklapelletcan`,
funkcja `ourDevices()`), **nie** przez zgadywanie nazw encji. Różnica w adresowaniu **punktów** (parametrów):
Modern nie zgaduje po `entity_id`, tylko buduje mapę z atrybutu **`tpc_id`**, który integracja HA dokleja do
każdej swojej encji (`buildIndex()`, na początku pliku) — ten sam identyfikator punktu co w firmware. Metadane
(zakres, krok, jednostka, wymagany poziom dostępu) pochodzą z `teklapelletcan-points.js` — plik **generowany
automatycznie** z `rejestry/*.csv` (tym samym źródłem co firmware) przez `tools/gen_points.py`; **nigdy nie
edytować ręcznie**, CI (`host-tests`) sprawdza jego aktualność (`--check`).

Konsekwencja praktyczna: ta karta działa poprawnie niezależnie od tego, jak nazwiesz/przetłumaczysz encje w HA —
liczy się tylko atrybut `tpc_id`, nie string nazwy.

## Obrazki — ta sama pułapka HACS co w Classic

`DEFAULT_ASSET_BASE` (góra pliku) rozróżnia, czy karta jest serwowana z `/hacsfiles/...` (HACS kopiuje przy
instalacji **tylko pliki JS**, katalog `img/` nigdy nie trafia na dysk HA) — wtedy obrazki ładowane są z CDN
(`cdn.jsdelivr.net/gh/GieOeRZet/TeklaPelletModern-card@main/`), inaczej lokalnie względem adresu pliku karty.
Konfigurowalne przez `asset_base` w configu karty, gdyby plik karty i obrazki były serwowane z różnych miejsc
(np. karta tymczasowo w `/local/` do testów).

## Ekrany (`SCREENS`, góra pliku)

`pulpit`, `instalacja`, `harmonogram`, `alarmy`, `menu` — nawigacja przez `_goScreen()`, bez routingu URL (stan
w `this._screen`, re-render przy zmianie). Poziomy dostępu 1/2 — `_ensureLevel(need)`, patrz
[`POZIOMY-DOSTEPU-PIN.md`](POZIOMY-DOSTEPU-PIN.md) (tam też błąd znaleziony i naprawiony w tej karcie: sztywne
700 ms zamienione na pętlę powtórzeń).

## Edytor konfiguracji (`TeklaModernCardEditor`)

Osobna klasa (`customElements.define('teklapelletcan-modern-card-editor', ...)`), `ha-form` ze schematem: pole
`device_id` (tylko gdy wykryto >1 urządzenie integracji) i `boiler_image` (typ 11/12/13/14). `getStubConfig()`
zwraca domyślny config przy pierwszym dodaniu karty z selektora HA.

## Zapisy — zawsze przez usługi integracji

`_call()`/`_callDomain()` wołają `hass.callService(...)` — karta nigdy nie pisze nic z pominięciem Home Assistant
i jego mechanizmów autoryzacji (tak samo jak Classic). Żadnego bezpośredniego REST/WebSocket do urządzenia.

## Trzy miejsca synchronizacji

W przeciwieństwie do Classic (trzy miejsca **współdzielące dokładnie ten sam kod silnika** — karta, portal,
appka), Modern **istnieje tylko jako karta HA** — portal urządzenia i aplikacja Android mają własny,
niezależny interfejs (`android/ui/`, zsynchronizowany do `web/js/` przez `tools/sync_web.py`), który wygląda
podobnie (ten sam "nowoczesny" styl wizualny), ale to **inny kod**, nie ten plik. Nie myl tych dwóch — zmiana w
`web/teklapelletmodern-card.js` nie dotyka appki/portalu i odwrotnie.
