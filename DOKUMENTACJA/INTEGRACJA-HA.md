# Integracja Home Assistant — architektura rzeczywista

> Uzupełnienie do `docs/ARCHITEKTURA.md` §9 (ogólny opis, wciąż aktualny w założeniach).

## Pliki — `custom_components/teklapelletcan/`

| Plik | Rola |
|---|---|
| `__init__.py` | Konfiguracja wpisu integracji (`async_setup_entry`), koordynator danych. |
| `config_flow.py` | Kreator dodawania integracji: wykrycie zeroconf (`_teklapelletcan._tcp`) lub ręczny adres IP, parowanie. |
| `api.py` | Klient REST/WebSocket do urządzenia (odpowiednik `Http.kt`/`Proxy.kt` aplikacji Android, ale po stronie HA). |
| `entity.py` | Bazowa klasa encji (wspólne `device_info`, `unique_id` itd.). |
| `sensor.py`, `binary_sensor.py` | Encje odczytowe (temperatury, stany, liczniki). |
| `select.py` | Encje wyboru z listy (np. tryb pracy). |
| `button.py` | Encje-przyciski (akcje jednorazowe — np. test wyjść, potwierdzenie alarmu). |
| `switch.py` | Przełączniki (wł./wył.). |
| `const.py` | Stałe (domena `teklapelletcan`, nazwy usług itd.). |
| `strings.json` | Teksty UI kreatora konfiguracji (tłumaczenia HA). |

**Brak platformy `update`** (encja natywnej aktualizacji HA, planowana w `docs/TODO.md`: *"Encja `update` w
integracji HA (powiadomienie + instalacja z HA)"*) — **nie jest jeszcze zaimplementowana**. Dziś aktualizacja
firmware odbywa się przez kartę/portal urządzenia lub aplikację Android, nie przez natywny mechanizm `update.*`
Home Assistant. To wciąż otwarty punkt z listy TODO.

**Brak platform `number`/`text`** — nastawy liczbowe (temperatury zadane, histerezy itd.) nie są dziś wystawione
jako natywne encje `number.*`/`text.*` tej integracji; zapis odbywa się przez usługi (`set_param`,
`set_setpoint`, ...) wołane z poziomu karty (Classic/Modern), nie wprost z poziomu automatyzacji/UI encji HA bez
karty. To techniczne ograniczenie obecnego stanu integracji, nie celowa decyzja architektoniczna — wart
odnotowania dla kogoś, kto chciałby to rozwijać dalej (np. automatyzacje HA bez karty wymagałyby wywołania
usługi, nie prostego `number.set_value`).

## Encje i nazewnictwo

Zgodność wsteczna z oryginalnym projektem referencyjnym (ESPHome): encje mają te same nazwy/`entity_id` co w
ESPHome, żeby karta referencyjna (`pelletcan-card`) działała bez zmian również na tej integracji — patrz
`docs/ARCHITEKTURA.md` §18 i katalog `rejestry/encje.csv` (190 encji oryginalnych: 119 sensorów, 42 tekstowe, 13
binarnych, 11 przycisków, 3 selecty, 2 przełączniki — stan docelowy z ESPHome, nie wszystko jest dziś 1:1
przeniesione do tej integracji, patrz akapit wyżej o brakujących platformach).

## Karty NIE są częścią integracji

Integracja wystawia wyłącznie encje i usługi — żadna karta Lovelace nie jest wymuszana ani wstrzykiwana
automatycznie przy instalacji integracji. Karty (Classic, Modern) to osobne repozytoria HACS, instalowane
niezależnie — patrz [`ARCHITEKTURA-KARTY-CLASSIC.md`](ARCHITEKTURA-KARTY-CLASSIC.md) i README repozytorium
`TeklaPelletModern-card`.
