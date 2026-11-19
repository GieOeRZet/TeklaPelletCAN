# HANDOFF — TeklaPelletCAN — 2026-11-19

## TRYB
Kontynuuj reverse engineering FW2213TK bez zatrzymywania się na pojedynczych znaleziskach. Użytkownik chce duże przełomy, nie raporty z każdego adresu. Szukaj samodzielnie. Każdy znaczący batch zapisuj na GitHub.

## REPO
GieOeRZet/TeklaPelletCAN
Ostatni commit analityczny: 3074de3654e98e109d1bd690f114544223c19c8e
Wcześniejszy stan: f38b79e3159cef62eb31f709786278c2effd2081

## CEL
Znaleźć kodowy most:
0x2105 (liczba CO) -> aktywacja/utworzenie CO1..CO4 -> +0x12C instancja -> parametry CAN.

Nie wracaj do hipotezy, że DAT_0804107C / 0x08040FC2 tworzy CO. To bardzo prawdopodobnie tabela Test I/O.

## MODEL
Touch = regulator/UI/logika konfiguracji.
CAN I/O BIG = wykonanie fizycznych I/O.

Warstwy:
1. 0x2105..0x2108 = konfiguracja funkcjonalna
2. 0x3500, 0x3502, 0x350B + 0x16C1/0x16D5 = hardware/profil
3. wariant 1..7
4. logiczne obiekty CO1..CO4
5. module+0x12C = instance 1..4
6. base + instance - 1
7. CAN / BIG

## KLUCZOWE FAKTY
- 0x2105 = Heating configuration, u8, 0..4, default 1, storage 0x20021FAF, map 0x0801A5B0.
- Dokumentacja: Ilość obwodów grzewczych określa ilość obwodów CO.
- BIG profile: P1 CO+CWU+bufor; P2 CO1+CO2+CWU; P3 CO1+CO2+CWU+bufor.
- 0x2105 nie występuje w kConf; 0x2106/7/8 występują.
- 0x3500 Main module type; 0x3502 CH expansion module type; 0x350B Profile number.
- Main=0: expansion=0 + profile 1/2/3 => variants 2/3/4; expansion=1 => variants 5/6/7.
- +0x12B = klasyfikacja/typ obiektu, nie numer CO.
- +0x12C = numer instancji 1..4.
- 0x08037D00 ustawia +0x12C na 1..4 dla klas 1..4.
- 0x08036FF2 mapuje parametr -> panel slot z uwzględnieniem context+0x12C.
- 0x0802167A / 0x1167A = lookup 4 rekordów; 0x08011812 zapisuje rekord.
- 0x0802143C / 0x1143C tworzy rekord 0x2C: +08 CAN index, +0C storage pointer, +10 type.
- 0x08037212 i 0x080370C0 budują index base + instance - 1.
- Rodziny CO: 0x2032..35 -> 0x20020964; 0x2048..4B -> 0x20020966; 0x2064..67 -> 0x2002096E.
- CSV: 0x2032 count=4, 0x2048 count=4, 0x2064 count=4, harmonogram 0x2126..0x213E, 0x2142 count=4.
- TouchGFX ma Ogrzewanie obwód 1..4.
- 0x08040FC2 / DAT_0804107C = najpewniej Test I/O; obejmuje testy pomp/mikserów CO1..CO4 itd.
- 0x08036D60 czyta parametr indeks 3; semantyka nieustalona.
- Konstruktor 0x08037CA4; default 0x08037E9C: +0x128=1, +0x12C=1, +0x12B=0.
- 0x0803C064 używa DAT_0803C218 i rozróżnia klasy 0, 1..4, 5..10, 0x0B..0x14.
- Brak literalnych referencji do 0x2105 / 0x20021FAF / 0x0801A5B0 w obecnym decompiled.c. Szukać użycia pośredniego/generic parameter engine.

## PRIORYTET
1. Wszystkie ścieżki tworzące obiekty z +0x12B/+0x12C.
2. Warunki ograniczające instancje 1..4.
3. Związek z wariantem 1..7.
4. Generic engine, przez który 0x20021FAF może być używany pośrednio.
5. Dopiero potem dokładne mapowanie Main/Expansion/Profile -> fizyczne CO.

## RAPORTOWANIE
Nie raportuj pojedynczych wyników. Zbieraj kilka powiązanych dowodów i raportuj dopiero przełom. Przy znaczącym postępie zapisz markdown na GitHub i podaj commit SHA.

## STYL
Polski, krótko, technicznie. Etykiety: UDOWODNIONE / BARDZO PRAWDOPODOBNE / HIPOTEZA.