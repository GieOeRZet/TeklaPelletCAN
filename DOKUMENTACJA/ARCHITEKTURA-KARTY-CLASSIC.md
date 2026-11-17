# Architektura karty Classic — mechanizm patchowania silnika

Trzy pliki współpracujące ze sobą, w tej kolejności ładowania:

```
teklapelletclassic-card.js   (cienka warstwa integracji HA — jedyny zasób dashboardu)
        │  dynamic import()
        ▼
teklapelletclassic-engine.js (silnik: patchuje tekla-panel-card.js w locie + dokleja własne moduły)
        │  fetch() + patch tekstowy + <script>
        ▼
tekla-panel-card.js          (baza v6.9 — NIGDY nie edytowana ręcznie, patrz niżej dlaczego)
```

## Dlaczego baza nie jest edytowana bezpośrednio

`tekla-panel-card.js` pochodzi z oryginalnego projektu referencyjnego (PelletCAN) i jest traktowana jako
**niezmienny punkt odniesienia** — każda nasza poprawka to osobny, nazwany patch zamiast bezpośredniej edycji,
dzięki czemu:
- różnicę między "co jest oryginalne" a "co myśmy dodali" widać na pierwszy rzut oka (lista `EDITS` na początku
  `teklapelletclassic-engine.js`),
- aktualizacja bazy z nowej wersji referencyjnej (gdyby kiedyś była potrzebna) nie wymaga ręcznego scalania —
  wystarczy sprawdzić, czy patche nadal "łapią" swoje wzorce.

## Mechanizm patchowania tekstowego (`EDITS`)

`teklapelletclassic-engine.js` na starcie:
1. Pobiera **treść tekstową** `tekla-panel-card.js` (`fetch(...).text()`) — NIE import jako moduł.
2. Przechodzi przez tablicę `EDITS` (dziesiątki wpisów), gdzie każdy wpis to jedno z:
   - `{t: "x", old: "...", new: "..."}` — **dosłowna podmiana ciągu** (musi wystąpić **dokładnie raz** w kodzie,
     inaczej `console.error` — `code.split(e.old).length !== 2`).
   - `{src: "...", fl: "...", new: "..."}` — podmiana przez **wyrażenie regularne** (`src` = wzorzec, `fl` =
     flagi, np. `"gs"`).
3. Wstrzykuje spatchowany kod jako zwykły, globalny `<script>` (IIFE), NIE jako moduł ES — stąd `customElements`
   wewnątrz tego skryptu działa tak samo jak w oryginalnym pliku.
4. Odbiera zdefiniowaną klasę przez `customElements.get('tekla-panel-card')`.

**Konsekwencja dla kogoś, kto to kontynuuje:** jeśli trzeba zmienić coś, co fizycznie siedzi w
`tekla-panel-card.js` (np. strukturę HTML jakiegoś ekranu), **nie edytuj `tekla-panel-card.js`** — dopisz nowy
wpis do `EDITS` w `teklapelletclassic-engine.js` z precyzyjnym `old`/`new` (albo regexem, jeśli fragment się
powtarza). Każdy patch, który przestanie pasować (bo baza się zmieniła), **zgłosi się sam** w konsoli
przeglądarki jako błąd — to jest zamierzony mechanizm wczesnego ostrzegania, nie bug.

## Monkey-patching po zdefiniowaniu klasy (`gate`, nadpisanie `_css`)

Po uzyskaniu klasy `C = customElements.get('tekla-panel-card')`, silnik nadpisuje jej `prototype` bezpośrednio
(bez dziedziczenia/subklasy):

```js
const gate = (name, fn) => {
  const o = C.prototype[name];                       // oryginalna metoda bazy
  C.prototype[name] = function (...a) {
    return FULL(this) ? fn.apply(this, a) : o.apply(this, a);
  };
};
```

`FULL(this)` to dziś zawsze `() => true` (historyczne rozróżnienie "pełna karta" / "lite" zostało wycofane —
komentarz w kodzie: *"od teraz jeden, pelny zestaw grafik panelu (bez opcji »domyslne«) — FULL zawsze prawda"*).
`gate('_nazwaMetody', function(...) {...})` całkowicie **zastępuje** zachowanie danej metody bazy (np. `_fan`,
`_auger`, `_prDlg`) własną implementacją — ale oryginał (`o`) zostaje zachowany jako fallback, gdyby `FULL`
kiedyś znów miało sens przywrócić.

### Nadpisanie CSS (`_css()`)

Style **nie są osobnym plikiem CSS** — cała stylistyka żyje jako długie literały szablonowe (template strings)
zwracane przez metodę `_css()` klasy. Silnik robi:

```js
const oc = C.prototype._css;              // oryginalna metoda stylów bazy
C.prototype._css = function () {
  // ... oblicza zmienne zależne od konfiguracji (this._cfg) ...
  return oc.call(this) + boil + sliderCss + bezelCss + `/* reszta naszych reguł, z !important */`;
};
```

Czyli: **najpierw renderuje się CSS bazy** (niebieski, oryginalny wygląd `tekla-panel-card.js`), **a POTEM
doklejany jest nasz blok**, który nadpisuje selektywnie wybrane reguły przez `!important`. To jest właśnie ten
"FULL-gated override block", o którym mowa w commitach tej sesji — jeden długi ciąg CSS doklejany na końcu.

**Pułapka, w którą wpadliśmy wielokrotnie w tej sesji:** nadpisanie reguły o niewystarczającej specyficzności
(np. `.cell{...}` nie bije `.cell:has(.ind){...}` bazy), nieuwzględnienie `background-origin` (domyślnie
`padding-box`, nie pokrywa obszaru `border` nawet przy przezroczystym kolorze obramowania), czy nieuwzględnienie,
że element nadrzędny bez własnego tła pokazuje tło **innego** elementu (`.top` nie ma tła, pokazuje `.screen`) —
każda z tych pułapek dawała realny, zgłoszony przez użytkownika błąd wizualny ("niebieskie przebija przez
dziurę" itp.). Przy każdej nowej regule CSS w tym bloku **sprawdzaj realnym renderem (Playwright), nie tylko
czytaniem kodu**, bo kaskada CSS tu jest nieoczywista.

### Konfigurowalne elementy sterowane przez `this._cfg`

Flagi/wartości z konfiguracji karty HA (`this._cfg`, wypełniane przez `teklapelletclassic-card.js` z YAML-a karty)
wpływają na CSS generowane przez `_css()`:
- `this._cfg.boiler_image` — typ grafiki kotła (11/12/13/14), różne proporcje.
- `this._cfg.show_bezel` (domyślnie `true`/nieobecne = pokazana) — `false` spłaszcza `.bezel` (usuwa zaokrągloną,
  czarną obudowę z bocznymi "diodami" LED) i chowa `.strip`.

Ważne: **kolory suwaków NIE są (już) konfigurowalne** — próba dodania tej opcji w tej sesji została wycofana na
wyraźne życzenie (miała zastąpić autentyczne bitmapy panelu własnym, dowolnym kolorem; ostatecznie zdecydowano
się na stałe, prawdziwe bitmapy — patrz [`BITMAPY-PANELU.md`](BITMAPY-PANELU.md), sekcja `163`/`165`/`167`).

## Punkt wejścia HA: `teklapelletclassic-card.js`

Jedyny zasób dashboardu tej karty (HACS `filename` w `hacs.json`). Jego zadania:
1. `dynamic import()` silnika (`teklapelletclassic-engine.js`) z tego samego katalogu — tylko raz
   (`customElements.get('tekla-panel-card')` jako strażnik).
2. Wykrycie urządzenia integracji TeklaPelletCAN **przez rejestr urządzeń HA**
   (`identifiers[0] === "teklapelletcan"`), NIE przez zgadywanie prefiksu encji po całym Home Assistant (tak jak
   robi to stara, ogólna `pelletcan-card` — różnica opisana w `docs/ARCHITEKTURA.md`, p. 10).
3. Automatyczny dobór prefiksu encji dla znalezionego urządzenia (`window.__igneoFind.devices(...)`).
4. Edytor karty HA (`ha-form`) z polami: ekran startowy, język, obraz kotła, pokaż obudowę — bez ręcznego
   mapowania encji.

## Trzy miejsca, w których żyje DOKŁADNIE ten sam kod silnika

`teklapelletclassic-engine.js` i `tekla-panel-card.js` są używane **bez żadnej duplikacji** w trzech miejscach:
1. Karta HACS (`teklapelletclassic-card.js` → dynamic import, jak wyżej).
2. Portal WWW samego urządzenia (`web/classic.html` ładuje bezpośrednio ten sam silnik).
3. Aplikacja Android — przy budowie (`android/app/build.gradle`, zadanie `syncAssets`) katalog `web/` jest
   kopiowany do assets APK bez modyfikacji (patrz [`APLIKACJA-ANDROID.md`](APLIKACJA-ANDROID.md)).

**To oznacza: każda poprawka w `web/teklapelletclassic-engine.js` automatycznie trafia do wszystkich trzech
miejsc jednocześnie** — nie trzeba (i nie wolno) kopiować zmian ręcznie do innych lokalizacji w tym repozytorium.
Jedyne miejsce, gdzie trzeba pamiętać o ręcznej synchronizacji, to **downstream repo**
`GieOeRZet/TeklaPelletClassic-card` — tam ląduje kopia tych plików dopiero przy wydaniu (zadanie CI
`publish-card-classic`), więc zmiana w tym repo nie jest widoczna u użytkowników HACS, dopóki nie zrobi się
release'u. (To był dokładnie ten błąd, który spowodował "wracanie starej karty" opisane w historii commitów —
`web/teklapelletclassic-card.js`, czyli źródło synchronizacji CI, było nieaktualne względem downstream repo.)
