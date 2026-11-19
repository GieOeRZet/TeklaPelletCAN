# BATCH — 0x2105 vs Profile BIG vs aktywne CO — 2026-11-19

## Przełom

Oficjalna instrukcja Tekla/Igneo Touch definiuje w konfiguracji: Autokonfiguracja, Główny moduł IO, Ilość obwodów grzewczych oraz Numer profilu. „Ilość obwodów grzewczych” wprost określa ilość obwodów CO.

Dla CAN I/O BIG producent pokazuje:
- Profil 1 = CO + CWU + Bufor
- Profil 2 = CO1 + CO2 + CWU
- Profil 3 = CO1 + CO2 + CWU + Bufor

## UDOWODNIONE

1. 0x2105 = Heating configuration, u8, zakres 0..4, default 1, storage 0x20021FAF.
2. Dokumentacja opisuje odpowiadającą funkcję jako „Ilość obwodów grzewczych — Określa ilość obwodów CO”.
3. Profil nie jest liczbą obwodów: opisuje fizyczny wariant instalacji BIG i mapowanie I/O.
4. Firmware ma osobną warstwę 0x3500 Main module type, 0x3502 CH expansion module type, 0x350B Profile number oraz wybór wariantu 1..7.
5. 0x2105 nie występuje w kConf używanym przez nasz silnik odczytu konfiguracji; kConf zawiera 0x3501, 0x3500, 0x3505, 0x3720, 0x2106, 0x2108, 0x2107 itd.

## BARDZO PRAWDOPODOBNE

0x2105 jest parametrem systemowym określającym liczbę logicznych obwodów CO, natomiast 0x3500/0x3502/0x350B określają sposób ich fizycznej realizacji przez BIG i moduły rozszerzeniowe.

To tłumaczy jednoczesne istnienie zakresu 0..4 dla 0x2105, tylko 2 obwodów CO w profilach BIG 2/3 oraz dynamicznych instancji +0x12C = 1..4.

## NOWY CEL

Nie szukamy już prostego 0x2105 -> create CO1..CO4. Szukamy miejsca, w którym konfiguracja systemu ogranicza/udostępnia instancje CO 1..4:

    0x2105 = funkcja systemu / liczba CO
             |
    0x3500 + 0x3502 + 0x350B = hardware / BIG / profil
             |
             v
          wariant 1..7
             |
             v
          obiekty CO1..CO4
             |
             v
          +0x12C = instancja 1..4
             |
             v
          base_index + instance - 1
             |
             v
          parametry CAN

Priorytet dalszego trace: warunki tworzenia/aktywacji obiektów klas 1..4, źródło +0x12B/+0x12C oraz ich związek z wariantem wybranym w 0x08000E34.
