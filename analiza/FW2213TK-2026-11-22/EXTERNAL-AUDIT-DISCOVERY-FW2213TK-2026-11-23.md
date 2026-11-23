# Wynik audytu odkrywczego FW2213TK

## Wniosek główny

Nie mamy jeszcze podstaw, aby uznać reverse engineering firmware za kompletny.

Dotychczasowa analiza bardzo dobrze zamknęła znane ścieżki, ale firmware zawiera jeszcze niezmapowane funkcjonalności, szczególnie poza głównym grafem:

`UI → PID → CAN`

Najważniejszy wynik audytu: istnieje druga warstwa funkcjonalna Estymy, która nie jest reprezentowana wyłącznie przez główną macierz parametrów.

---

## 1. Pamięć alarmów / diagnostyka

W firmware występują osobne elementy:

- `Alarm date timestamp`
- `Alarm register`
- `Alarm confirm timestamp`
- `Alarm next index`
- `Number of alarms`
- `Request reset alarm memory`
- `Is reset required`

Wskazuje to na pełny mechanizm zarządzania historią alarmów, a nie tylko ekran wyświetlający zapisane alarmy.

### Status

**NEW OPEN — bardzo mocny kandydat do osobnego reverse engineeringu.**

---

## 2. Mechanizm „Default settings request”

Występuje osobny element:

`Default settings request`

Jest to szczególnie interesujące, ponieważ może oznaczać funkcję przywracania ustawień fabrycznych niezależną od zwykłego zapisu PID.

W połączeniu z:

- `Request reset alarm memory`
- `Is reset required`

sugeruje to istnienie warstwy operacji serwisowych/resetowych, której nie mieliśmy jeszcze zamkniętej jako osobnego subsystemu.

### Status

**NEW OPEN**

---

## 3. Konfiguracja modułów / identyfikacja sprzętu

W danych występują:

- `Main module type`
- `CH expansion module type`
- `Profile number`
- `Vide room 2 sw. ver. after dot`
- `Vide room 3 sw. ver. after dot`
- `Vide room 4 sw. ver. after dot`
- `soft. version`
- `boiler short name`

Wskazuje to na bogatszy model konfiguracji sprzętowej i wersjonowania modułów, niż wynikałoby z samego grafu PID/CAN.

Szczególnie `CH expansion module type` oraz `Profile number` mogą być związane z dynamicznym wyborem możliwości urządzenia, a nie tylko z poziomem menu.

### Status

**NEW OPEN**

---

## 4. Nie w pełni zamknięta mapa CAN/peripheral

Bulk scan wykazał wiele adresów peryferyjnych, których obecność jest potwierdzona, ale nie wszystkie zostały przypisane do konkretnej funkcjonalności.

Przykładowe adresy:

- `0x40000000`
- `0x40000400`
- `0x40000800`
- `0x40000C00`
- `0x40001000`
- `0x40001400`
- `0x40001800`
- `0x40002800`

Nie jest to samo w sobie dowodem na nowe funkcje, ale oznacza, że pełna mapa sprzętowa firmware nadal nie jest zamknięta.

---

## 5. Globalny RAM — klastry poza prostym modelem PID

Najczęściej referencjonowane adresy obejmują m.in.:

- `0x200247C8` — 60 referencji
- `0x200247CA` — 46
- `0x20021FA0` — 39
- `0x200247D0` — 33
- `0x2002481C` — 30
- `0x20024818` — 27
- `0x200243E4` — 22
- `0x200247C5` — 22

Część tych obszarów nie wygląda na zwykłą tabelę parametrów i powinna być traktowana jako potencjalne struktury runtime/stanu.

---

# Najważniejsze niezamknięte obszary

1. **System alarmów + pamięć alarmów**
2. **Factory/default reset**
3. **Serwisowe operacje na konfiguracji**
4. **Identyfikacja typu modułów i profilu sprzętowego**
5. **Wersjonowanie/identyfikacja modułów zewnętrznych**
6. **Pozostałe klasy/struktury runtime niewchodzące bezpośrednio w PID**
7. **Część peryferiów i ich funkcji**
8. **Część CAN sklasyfikowana dotychczas tylko jako „PDO-like”**
9. **Nieprzypisane funkcje z grafu 2810 celów BL**

---

# Kluczowa obserwacja dotycząca parametrów

Dotychczasowy model:

`260 parametrów = konfiguracja urządzenia`

jest zbyt wąski.

Mamy:

- **655 rekordów runtime**
- **260 pozycji katalogowych**

ale dodatkowo występują:

- obiekty i stan runtime,
- identyfikatory modułów,
- alarmy,
- reset flags,
- profile,
- wersje,
- struktury runtime,
- mechanizmy serwisowe.

Oznacza to, że pełny model Estymy musi obejmować więcej niż samą macierz PID.

---

# Konkluzja

Nie znaleziono podstaw, aby uznać firmware za w pełni zmapowany.

Przeciwnie — audyt wskazuje na dalsze, konkretne obszary funkcjonalne do odkrycia.

Najważniejszy kierunek dalszej analizy:

**alarmy → pamięć alarmów → reset/default settings → profile/moduły → struktury runtime → pozostałe CAN/peripheral → nieprzypisane funkcje.**

To właśnie te obszary należy teraz traktować jako główną ścieżkę dalszego reverse engineeringu.
