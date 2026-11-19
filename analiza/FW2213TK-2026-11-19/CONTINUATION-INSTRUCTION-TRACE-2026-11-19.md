# CONTINUATION-INSTRUCTION-TRACE-2026-11-19

## Cel nadrzędny
Kontynuować reverse engineering FW2213TK bez cofania się do luźnego przeszukiwania. Celem jest pełny, dowodowy trace mechanizmu CO1..CO4:

param_2 -> mechanizm wywołania C064 -> DAT_0803C218[param_2] -> class 1..4 -> object+0x12B/+0x12C -> runtime instancji -> lookup parametru -> CAN.

## Zasady pracy
- Decompiled.c z aktualnego canonical commit jest źródłem prawdy.
- Każdy wniosek musi mieć podstawę w kodzie/danych; hipotezy oznaczać osobno.
- Nie wracać do wycofanego tropu 0x08042146 / 0x38130.
- Nie utożsamiać 0x10E/0x10F z CO bez nowego dowodu.
- Nie zatrzymywać pracy po pojedynczym adresie/bajcie. Łączyć kilka wyników w jeden batch.
- Po każdym większym przełomie zapisać skonsolidowaną notatkę na GitHubie.
- Nie tworzyć notatek opisujących jedynie zamiary; notatka ma zawierać wykonany trace, dowody, granice pewności i następny konkretny target.
- Jeśli analiza wymaga danych, których decompiled.c nie zawiera, szukać surowych artefaktów firmware/hex/bin/dump lub innych artefaktów repo. Nie rekonstruować danych z domysłów.
- Przy zmianie modelu wcześniejsze twierdzenie należy jawnie osłabić/skorygować, zamiast pozostawiać sprzeczne wersje.

## Aktualny stan
Canonical commit przed/na którym opiera się analiza: a16008a1734bc4ed28bbb30339b51ac1d758e58c.
Nowsze notatki znajdują się w analiza/FW2213TK-2026-11-19/.

### Twarde fakty C064
FUN_0803C064(param_1,param_2):
- czyta DAT_0803C218[param_2],
- dla klas 1..4 ustawia object+0x12B = class,
- jednocześnie ustawia object+0x12C = 1..4,
- obiekt jest pobierany przez FUN_080314BA(),
- brak zwykłego bezpośredniego call-site C064 w decompiled.c.

DAT_0803C218:
- adres 0x0803C218,
- następna funkcja 0x0803C284,
- rozmiar obszaru 0x6C = 108 bajtów,
- zawartość nie została jeszcze wiarygodnie odzyskana.

### Twarde fakty drugiej ścieżki instancji
FUN_08040FC2:
- iteruje 22 wpisy DAT_0804107C,
- bierze trzecie pole wpisu,
- jeżeli nie jest -1, zapisuje je do object+0x12C,
- pierwszy element wpisu jest indeksem przekazywanym do FUN_08036FF2,
- wynik idzie do FUN_08040E46.

FUN_08041020:
- używa tej samej tabeli DAT_0804107C,
- zapisuje wartość z DAT_08041080[param_2*6] do object+0x12C, jeśli != -1,
- następnie wykonuje FUN_08037212(..., DAT_0804107C[param_2*3], param_3).

Wniosek:
C064 nie jest jedynym znanym źródłem +0x12C. Nie wolno już zakładać, że tylko C064 materializuje instancję.

## Potwierdzony dalszy engine
object+0x12C jest używany w FUN_08036FF2/FUN_08037212 do wyboru wpisu instancyjnego:
- dla pierwszej tabeli indeks bazowy jest modyfikowany o instance-1,
- następnie następuje dalszy lookup i warstwa CAN.
Nie należy jeszcze przypisywać konkretnych 0x2105..0x2108 bez bezpośredniego trace.

## Aktualny priorytet
1. Odzyskać surową zawartość DAT_0804107C (22 wpisy x 3 elementy) i DAT_08041080.
2. Przeanalizować FUN_08040E46 oraz FUN_08040E2A.
3. Ustalić, które wpisy tabeli dają instancje 1,2,3,4.
4. Zidentyfikować param_index tych wpisów i połączyć je z CO.
5. Równolegle znaleźć mechanizm pośredniego wywołania FUN_0803C064 i źródło param_2.
6. Odzyskać DAT_0803C218.
7. Dopiero po tych krokach scalać C218 z 4107C i mapować do 0x2105..0x2108/CAN.

## Jak kontynuować w nowym chacie
Nie zaczynać od pytania użytkownika o kontekst. Najpierw przeczytać:
- ten plik,
- BATCH-TRACE-C064-SINGLETON-MODULE-2026-11-19.md,
- BATCH-TRACE-INSTANCJA-0x12C-410FC2-2026-11-19.md,
- oraz najnowsze notatki w katalogu analiza/FW2213TK-2026-11-19.

Następnie od razu wykonywać analizę na GitHubie. Użytkownik oczekuje pracy ciągłej i skonsolidowanych wyników, nie raportowania każdego małego kroku.

## Raportowanie
Po większym batchu:
- podać kilka połączonych ustaleń,
- wskazać co jest twardym dowodem,
- wskazać co nadal jest hipotezą,
- zapisać wynik na GitHubie,
- w odpowiedzi podać link do commita, aby użytkownik mógł wkleić go do nowego chatu jako punkt kontynuacji.
