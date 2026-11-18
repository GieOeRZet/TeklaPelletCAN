# CI i proces wydania — mechanika, pułapki, jak bezpiecznie pracować z downstream repo

To repozytorium (`TeklaPelletCAN`) jest **jedynym źródłem prawdy**. Cztery downstream repozytoria
(`TeklaPelletCAN_HA`, `TeklaPelletClassic-card`, `TeklaPelletModern-card`, `TeklaPelletDroid`) dostają swoją
zawartość **wyłącznie** przez zadania `publish-*` w `.github/workflows/ci.yml`, uruchamiane ręcznie
(`workflow_dispatch`) z zaznaczonymi checkboxami — **nigdy automatycznie** przy zwykłym pushu. Nigdy nie edytuj
kodu bezpośrednio w downstream repo — przy następnym `publish-*` zostanie nadpisany (poza jednym wyjątkiem, patrz
niżej: README Droida).

## Jak wywołać wydanie

`workflow_dispatch` na `ci.yml` z `release_tag` (np. `v1.0.9`) tworzy GitHub Release **w tym repo** i publikuje
kanał stabilny firmware. **Nie** publikuje automatycznie do żadnego downstream repo — każdy z czterech
checkboxów (`publish_integration`, `publish_card_classic`, `publish_card_modern`, `publish_apk`) trzeba zaznaczyć
**osobno, tylko gdy dana rzecz faktycznie się zmieniła** w tym wydaniu (opisy pól w YAML mówią to samo — czytaj je
przy każdym wywołaniu). Przykład: poprawka wyłącznie w `android/ui/js/ui.js` → tylko `publish_apk`; poprawka w
`web/teklapelletclassic-engine.js` → tylko `publish_card_classic`.

## Co dokładnie kopiuje każde zadanie `publish-*` — i gdzie są pułapki

| Zadanie | Źródło → cel | **Pułapka** |
|---|---|---|
| `publish-integration` | `custom_components/teklapelletcan/` → to samo w `TeklaPelletCAN_HA` | `rsync -a --delete --exclude='__pycache__'` — pełna synchronizacja folderu, bezpieczna (nic ręcznego tam nie powinno być). |
| `publish-card-classic` | 5 plików JS + `rsync -a --delete web/img/ → img/` | **`--delete` kasuje wszystko w `img/` downstream repo, czego nie ma w `web/img/` tego repa.** Dlatego własne screenshoty do README tego repo muszą iść do **innego** folderu (np. `readme-img/`), nigdy do `img/`. |
| `publish-card-modern` | `teklapelletmodern-card.js` + `teklapelletcan-points.js` + `rsync --delete web/img/` | Ta sama pułapka `--delete` na `img/` co wyżej. |
| `publish-apk` | artefakt APK z joba `android` (musi być podpisany kluczem **produkcyjnym** — job sam to sprawdza i przerywa, jeśli nie) | `README.md`/`LICENSE` dopisywane **tylko jeśli ich tam jeszcze nie ma** (`[ -f ... ] || ...`) — **nigdy nie nadpisuje** istniejącego README. To jedyny downstream, gdzie ręczna edycja README jest trwale bezpieczna. |

Każde zadanie (poza APK) robi `git clone --depth 1` do `/tmp/pub`, kopiuje pliki, `git add -A`, commit (tylko gdy
są zmiany) i `git push origin HEAD:main` — potem, jeśli podano `release_tag`, kasuje ewentualne stare wydanie o
tym tagu i tworzy nowe (`gh release create`) w downstream repo.

## Jeśli kiedyś ręcznie klonujesz/edytujesz downstream repo (np. agent w osobnej sesji poprawia README)

1. **Zawsze `git fetch origin main` i sprawdź, czy lokalny klon nie jest przestarzały** względem `origin/main`
   przed commitem — CI mogło zdążyć zrobić nowy `publish-*` między sklonowaniem a Twoim pushem (`git log --oneline
   -1 FETCH_HEAD` vs `HEAD`; `git merge-base --is-ancestor HEAD FETCH_HEAD` mówi, czy lokalny klon jest w tyle).
   Jeśli tak: `git stash`, `git checkout -B main FETCH_HEAD`, `git stash pop`/`git apply` na nowej bazie, dopiero
   potem commit+push. Płytkie klony (`--depth 1`/małe `clone_depth`) są z definicji podatne na to, że zdąży
   przyjść nowszy `publish-*` — to się zdarzyło realnie wielokrotnie w listopadzie 2026.
2. **Przed nadpisaniem README w `TeklaPelletDroid` sprawdź historię** — jeden z wcześniejszych agentów w tej
   sesji o mało nie cofnął celowej, ręcznej edycji właściciela (usunięcie sekcji deweloperskich z README dla
   użytkownika końcowego). `publish-apk` nigdy go nie nadpisze automatycznie, ale **Ty jako agent też nie
   powinieneś**, chyba że wiesz, że to bezpieczne — zawsze przejrzyj `git log`/`git diff` przed pushem.
3. Nigdy nie zmieniaj plików w `img/` repo karty bez świadomości, że następny `publish-card-*` i tak je nadpisze
   (`--delete`) — jeśli chcesz coś tam trwale dodać (np. screenshot), musi to wejść przez `web/img/` w **tym**
   repozytorium, albo iść do osobnego folderu nieobjętego synchronizacją (np. `readme-img/`).

## Testy lokalnie (co odpala `host-tests`/`web-ui`/`android` w CI)

Zbuduj symulatory na hoście (ESP-IDF niepotrzebne do tego — to zwykłe C++/CMake):
```
cmake -S firmware/test -B build-host && cmake --build build-host
```
Powstają: `build-host/sim_server` (pełny symulator urządzenia z realnym enginem), `build-host/demo_server`
(lżejszy, do testów UI appki/karty/portalu), `build-host/test_core`/`test_engine` (testy jednostkowe przez
`ctest`).

| Co testujesz | Jak uruchomić |
|---|---|
| Rdzeń (core, bez sprzętu) | `ctest --test-dir build-host --output-on-failure` |
| Portal WWW urządzenia (PIN, OTA, Wi-Fi, ustawienia) | `build-host/sim_server 8102 web &` → `node web/test/e2e_device_ui.js http://127.0.0.1:8102 /tmp/ota` — **wymaga** fixture OTA w `/tmp/ota` (patrz `.github/workflows/ci.yml`, krok "Test UI urządzenia" — generuje `good.bin`/`good.sig`/`good.pkg.bin`/`tampered.bin` przez `tools/ota_sign.py`, bez nich test wywali `ENOENT`). |
| Karta Classic + Modern (w kontekście HA) | `build-host/demo_server 8098 web &` → `node web/test/e2e_teklapelletcan_card.js http://127.0.0.1:8098 /tmp` |
| Aplikacja Android — powłoka/tryb demo | `build-host/demo_server 8098 web &` → `node android/test/e2e_app.js android/ui web http://127.0.0.1:8098 /tmp` |
| Aplikacja Android — pełne UI | `build-host/demo_server 8099 android/ui &` → `node android/test/e2e_ui.js http://127.0.0.1:8099 /tmp` |

Wszystkie testy e2e używają Playwright (potrzebny `npm i playwright` w `web/test/node_modules` — w tym
środowisku agenta Playwright+Chromium są już globalnie zainstalowane, `require('playwright')` działa z
dowolnego katalogu bez instalacji).

**Generowane tabele** (`tools/gen_points.py`, `tools/sync_web.py`) muszą być aktualne — CI sprawdza to flagą
`--check` jako pierwszy krok (`host-tests`). Jeśli edytujesz `rejestry/punkty.csv`/`rejestry/odczyty.csv` albo
cokolwiek w `android/ui/js/`, uruchom odpowiednie narzędzie bez `--check`, żeby zregenerować/zsynchronizować, PRZED
commitem.

## Pułapka środowiskowa (nie-deterministyczna, niezwiązana z kodem)

W tym środowisku agenta (sandbox) `git push`/niektóre komendy bywają nieprzewidywalnie blokowane przez
"Claude Code auto mode classifier" nawet dla zwykłych, już zatwierdzonych operacji. Nie ma jednego
deterministycznego obejścia — pomaga: rozdzielenie `git add && git commit` od `git push` na osobne wywołania,
albo drobna zmiana składni polecenia. To kwestia środowiska, nie błąd w repo czy w workflow.
