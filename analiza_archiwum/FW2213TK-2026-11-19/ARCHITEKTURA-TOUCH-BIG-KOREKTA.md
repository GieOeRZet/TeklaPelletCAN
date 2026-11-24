# Korekta architektury IGNEO Touch / CAN I/O BIG

Data: 2026-11-19

## Status
Wcześniejszy model BIG = główny sterownik systemu był zbyt mocny. Dokumentacja Tekla/Estyma wskazuje, że IGNEO Touch jest regulatorem/sterownikiem, natomiast CAN I/O BIG jest modułem wykonawczym wejść/wyjść. BIG może jednak realizować znaczną część podstawowej instalacji bez dodatkowych modułów.

## Ważna korekta
Z dokumentacji Tekla wynika, że pojedynczy BIG może obsługiwać konfiguracje obejmujące m.in. CO1, CO2 i CWU, a zależnie od profilu także bufor i inne funkcje. Dodatkowe moduły CAN są potrzebne dopiero wtedy, gdy wymagania instalacji przekraczają zasoby/typ I/O BIG. Osobny moduł jest przewidziany m.in. dla sondy Lambda.

Nie wolno więc utożsamiać CO2 z drugim modułem rozszerzeniowym, liczby obwodów CO z liczbą modułów ani 0x3502 z prostym przełącznikiem jest/nie ma modułu CO.

## Warstwy systemu
IGNEO TOUCH / FW2213TK = UI, konfiguracja, logika regulatora, parametry i CAN.
CAN I/O BIG = wejścia/wyjścia fizyczne: pompy, mieszacze, dmuchawa, podajnik, czujniki itd.
Pozostałe moduły CAN = np. moduł Lambda ML-2.

## Konsekwencje dla reverse engineeringu
Rozdzielamy co najmniej dwie warstwy.

### A. Konfiguracja sprzętowo-I/O
- 0x3500 Main module type
- 0x3502 CH expansion module type
- 0x350B Profile number
- object+0x16C1 dodatkowa konfiguracja
- object+0x16D5 dodatkowy warunek
Te wartości uczestniczą w wyborze wariantu 1..7 i wyborze całych struktur/pointerów opisujących dostępny wariant sprzętowy.

### B. Konfiguracja funkcjonalna systemu
- 0x2105 Heating configuration, u8, zakres 0..4
- 0x2106 Hot water configuration
- 0x2107 Buffer configuration
- 0x2108 Solar configuration
0x2105 nie może być obecnie interpretowane jako liczba modułów. Bardziej prawdopodobnie opisuje liczbę/konfigurację aktywnych obwodów CO na poziomie systemu regulatora.

## Model roboczy
IGNEO Touch -> funkcjonalna konfiguracja systemu (2105..2108) + identyfikacja/konfiguracja I/O (3500/3502/350B/...) -> wybór wariantu 1..7 -> logiczne obiekty CO/CWU/BUF/SOLAR -> instancje, gdzie +0x12C = 1..4.

Dopiero po ustaleniu zasobów BIG i konfiguracji funkcjonalnej należy wyjaśniać, które instancje CO są dostępne/aktywne.

## Do udowodnienia z dekompilacji
1. Gdzie FW2213TK interpretuje 0x2105.
2. Czy 0x2105 steruje wyłącznie widocznością/konfiguracją UI, czy również tworzeniem logicznych obiektów.
3. Jak warianty 1..7 odpowiadają konkretnym profilom BIG.
4. Dokładne znaczenie 0x3500, 0x3502, 0x350B dla fizycznych wariantów BIG.
5. Zawartość DAT_0804107C (22-entry initialization table).
6. Zawartość DAT_0803C218 (classification table).
7. Źródła object+0x16C1 i object+0x16D5.
8. Gdzie następuje aktywacja/dezaktywacja CO1..CO4.

## Ograniczenie
Dokumentacja jest korelacją architektury produktu, ale nie zastępuje dowodu z FW2213TK. Interpretacje pozostają hipotezami do czasu znalezienia odpowiedniego przepływu w kodzie.