# DOKUMENTACJA — spis treści

Ten folder zawiera dokumentację **uzupełniającą** to, co już istnieje w repozytorium — nie duplikuje tego, co już
jest dobrze opisane gdzie indziej. Cel: żeby ktoś, kto kontynuuje ten projekt, nie musiał odkrywać ponownie
rzeczy wypracowanych (często metodą prób i błędów) w listopadzie 2026.

## Gdzie czego szukać

| Temat | Dokument |
|---|---|
| **Rejestry kotła, CANopen, dekompilacja firmware panelu Igneo Touch, metodologia skanowania** | [`../rejestry/README.md`](../rejestry/README.md) i [`../rejestry/REJESTRY.md`](../rejestry/REJESTRY.md) — **najbardziej wyczerpujące, aktualne źródło w całym projekcie, zacznij tutaj jeśli szukasz czegokolwiek o rejestrach**. |
| Ogólna architektura projektu (cele, nazewnictwo, API, bezpieczeństwo, partycje flash) | [`../docs/ARCHITEKTURA.md`](../docs/ARCHITEKTURA.md) — techniczne sekcje aktualne, status implementacji miejscami przeterminowany (patrz [`FIRMWARE.md`](FIRMWARE.md) dla korekty). |
| **Firmware — rzeczywista struktura modułów, komunikacja, status** | [`FIRMWARE.md`](FIRMWARE.md) |
| **Karta Classic — mechanizm patchowania silnika, trzy miejsca użycia, pułapki CSS** | [`ARCHITEKTURA-KARTY-CLASSIC.md`](ARCHITEKTURA-KARTY-CLASSIC.md) |
| **Mapa bitmap panelu** (`img/panel/*.png`) — co która przedstawia, gdzie użyta, metodologia weryfikacji | [`BITMAPY-PANELU.md`](BITMAPY-PANELU.md) |
| **Aplikacja Android — warstwa natywna, UI, synchronizacja z portalem** | [`APLIKACJA-ANDROID.md`](APLIKACJA-ANDROID.md) (uzupełnia [`../docs/APLIKACJA_ANDROID.md`](../docs/APLIKACJA_ANDROID.md)) |
| **Integracja Home Assistant — pliki, encje, czego brakuje** | [`INTEGRACJA-HA.md`](INTEGRACJA-HA.md) |
| **Aktualizacje OTA — kanał stabilny domyślnie, ukryty tryb developera** | [`AKTUALIZACJE-OTA.md`](AKTUALIZACJE-OTA.md) |
| **Poziomy dostępu/PIN (0900/0999) — cztery niezależne implementacje, cztery naprawione błędy** | [`POZIOMY-DOSTEPU-PIN.md`](POZIOMY-DOSTEPU-PIN.md) |
| **Instalator WWW (ESP Web Tools) — wgranie firmware bez ESPHome, przez przeglądarkę** | [`INSTALATOR-WWW.md`](INSTALATOR-WWW.md) |
| Pierwsze uruchomienie urządzenia | [`../docs/PIERWSZE_URUCHOMIENIE.md`](../docs/PIERWSZE_URUCHOMIENIE.md) |
| Budowanie firmware/aplikacji lokalnie | [`../docs/BUDOWANIE.md`](../docs/BUDOWANIE.md) |
| Zdalne wgranie firmware (bez fizycznego dostępu) | [`../docs/WGRANIE_ZDALNE.md`](../docs/WGRANIE_ZDALNE.md) |
| Lista otwartych zadań | [`../docs/TODO.md`](../docs/TODO.md) |

## Pięć repozytoriów projektu

| Repozytorium | Zawartość | README |
|---|---|---|
| [`GieOeRZet/TeklaPelletCAN`](https://github.com/GieOeRZet/TeklaPelletCAN) | To repozytorium — firmware, integracja HA, obie karty, aplikacja Android (źródła rozwojowe) | [`../README.md`](../README.md) |
| [`GieOeRZet/TeklaPelletCAN_HA`](https://github.com/GieOeRZet/TeklaPelletCAN_HA) | Integracja HA (wydania HACS) | README w tamtym repo |
| [`GieOeRZet/TeklaPelletClassic-card`](https://github.com/GieOeRZet/TeklaPelletClassic-card) | Karta "replika panelu" (wydania HACS) | README w tamtym repo |
| [`GieOeRZet/TeklaPelletModern-card`](https://github.com/GieOeRZet/TeklaPelletModern-card) | Karta w stylu aplikacji Android (wydania HACS) | README w tamtym repo |
| [`GieOeRZet/TeklaPelletDroid`](https://github.com/GieOeRZet/TeklaPelletDroid) | Aplikacja Android (wydania .apk) | README w tamtym repo |

Każde z downstream repozytoriów (`_HA`, `Classic-card`, `Modern-card`, `Droid`) dostaje swoją zawartość **dopiero
przy wydaniu** (zadania CI `publish-*` w `.github/workflows/ci.yml`) — źródło prawdy dla kodu zawsze jest w tym
repozytorium (`TeklaPelletCAN`), nigdy odwrotnie. Jeśli coś wygląda inaczej w repo downstream niż tutaj — tutaj
jest prawda, tam czeka na kolejne wydanie.

## Historia wersji (co się zmieniło, dla kogoś, kto wraca do projektu)

| Wersja | Co się zmieniło |
|---|---|
| v1.0.6 | Kanał aktualizacji zawsze stabilny domyślnie + ukryty tryb developera (PIN `1948`, hash FNV-1a) — patrz [`AKTUALIZACJE-OTA.md`](AKTUALIZACJE-OTA.md). Ikona HACS integracji (`custom_components/teklapelletcan/brand/icon.png`, potwierdzona działająca). |
| v1.0.7 | Fix: `crypto.subtle` (PIN `1948`/poziomu nie działał na realnym urządzeniu przez HTTP). Fix: ekran "Konfiguracja" nie odświeżał wartości. Fix: komunikat po PIN-ie pokazywał stary poziom (POST/GET staleness) — patrz [`POZIOMY-DOSTEPU-PIN.md`](POZIOMY-DOSTEPU-PIN.md) błędy 1–2. |
| v1.0.8 | Fix: tekstury karty Classic gasły trwale po samoczynnym odświeżeniu — patrz [`ARCHITEKTURA-KARTY-CLASSIC.md`](ARCHITEKTURA-KARTY-CLASSIC.md). Fix: PIN poziomu 2 bywał fałszywie ograniczany do poziomu 1 (appka + karta Modern) — patrz [`POZIOMY-DOSTEPU-PIN.md`](POZIOMY-DOSTEPU-PIN.md) błędy 3–4. Dodany **instalator WWW** (ESP Web Tools) — patrz [`INSTALATOR-WWW.md`](INSTALATOR-WWW.md). |

## Nieukończone/otwarte punkty tej dokumentacji
- Pełen, numer-po-numerze opis wszystkich 189 bitmap panelu — opisano tylko te użyte w kodzie i potwierdzone
  wizualnie; reszta czeka na kogoś, kto będzie tego faktycznie potrzebował (patrz metodologia w
  [`BITMAPY-PANELU.md`](BITMAPY-PANELU.md), żeby nie powtórzyć błędów tej sesji).
- **Ikona HACS integracji — POTWIERDZONA, działająca**: `custom_components/teklapelletcan/brand/icon.png` (bez
  zmian w `hacs.json`/`manifest.json`), zweryfikowana empirycznie na realnym, publicznym przykładzie
  (`Corsw/homeassistant-generic-hygrostat`). Wcześniejsze (błędne) ustalenie w tym dokumencie, że mechanizm "nie
  wszedł do HACS", było oparte na nieaktualnym PR-ze i zostało skorygowane po znalezieniu działającego przykładu.
  Ikona karty (kategoria HACS "Plugin") — **nadal niepotwierdzona**: `brand/icon.png` w korzeniu repo karty jest
  tylko próbą best-effort (jedyna poszlaka to niezweryfikowany komentarz w zewnętrznym issue), nie ma
  potwierdzonego, działającego przykładu jak dla integracji.
