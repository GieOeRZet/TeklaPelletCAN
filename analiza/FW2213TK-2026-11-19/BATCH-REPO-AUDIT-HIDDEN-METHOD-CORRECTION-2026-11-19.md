# PASS 5C — REPO AUDIT: KOREKTA „HIDDEN METHOD CLUSTER” — 2026-11-19

## Cel
Zweryfikować poprzedni wniosek, że C33E/C5B4/424C4/CACC/CB04/CB2C wszystkie są poza `functions.txt`.

## 1. Twarda korekta

Ponowny odczyt aktualnego `firmware/FW2213TK-ghidra/functions.txt` na commit 56d2ca4e4dbed3d730ce6d57bfb0a884347c4aeb wykazał:

- `0803CACC FUN_0803cacc 20` — JEST w functions.txt.
- `0803CB2C FUN_0803cb2c 270` — JEST w functions.txt.

Zatem wcześniejszy zapis w BATCH-METHOD-CLUSTER, że CACC i CB2C „nie mają wpisów w functions.txt”, jest nieaktualny i zostaje WYCOFANY.

Dodatkowo:
- `0803C550 FUN_0803c550 100` kończy się dokładnie na `0x0803C5B4`.
- C5B4 nadal NIE ma osobnego wpisu.
- `0804204A FUN_0804204a 204` kończy się na `0x08042116`, a następny wpis to `0804272C`; `FUN_080424C4` nadal nie ma osobnego wpisu.
- C33E nadal nie ma osobnego wpisu między rozpoznanymi funkcjami w tym regionie.

## 2. Zaktualizowany obraz „gapu”

Nie mamy już jednego jednolitego klastra sześciu nierozpoznanych funkcji.

Rzeczywisty stan:

```
C33E       -> poza normalnym wpisem functions.txt [OPEN boundary]
C5B4       -> poza normalnym wpisem functions.txt [OPEN boundary]

424C4      -> poza normalnym wpisem functions.txt [OPEN boundary]

CACC       -> NORMALNY wpis functions.txt, 20 B
CB2C       -> NORMALNY wpis functions.txt, 270 B
```

To jest istotne, ponieważ CACC/CB2C można teraz traktować jako normalnie zarejestrowane funkcje Ghidra przy analizie call graphu; nie należy sztucznie szukać dla nich „hidden method table” tylko dlatego, że starsza notatka tak twierdziła.

## 3. Co nadal pozostaje interesujące

C33E/C5B4/424C4 rzeczywiście leżą na granicach/obszarach, których automatyczna lista funkcji nie rozdzieliła tak, jak oczekujemy.

To nadal uzasadnia atak na:
- granice C33E,
- granice C5B4,
- granice 424C4,
- ich sąsiednie dane/function-pointer storage.

Ale NIE należy rozszerzać tego automatycznie na CACC/CB2C.

## 4. Wpływ na główny trace

Zamknięty łańcuch 370A pozostaje bez zmian:

```
0x370A
 -> internal 0x121
 -> FUN_08036FF2
 -> FUN_08037094
 -> FUN_080115F6
 -> 0x20021FA6
 -> u8 1..3
 -> FUN_0803CB2C
 -> FUN_0803CACC
 -> Bitmap +0x85C
 -> resource 11/12/13
```

To nie jest cofnięte.

## 5. Nowy priorytet

Zamiast szukać „wspólnego hidden-method table dla C33E/C5B4/CACC/CB04/CB2C”, kolejność jest teraz:

1. odzyskać dokładną granicę C33E;
2. odzyskać dokładną granicę C5B4;
3. odzyskać dokładną granicę 424C4;
4. dla CACC/CB2C korzystać normalnie z ich wpisów w functions.txt i ich call graphu;
5. znaleźć wszystkie odwołania do +0x85C/+0x888/+0x8B4/+0x8E0;
6. dopiero potem szukać wspólnej klasy/metody.

## 6. Ważna konsekwencja

To jest przykład, dlaczego na początku każdego nowego chatu trzeba audytować repozytorium, a nie ślepo ufać starszemu handoffowi.

Stary handoff zachowujemy jako historię, ale aktualny `functions.txt` ma pierwszeństwo.

Status:
- 370A chain: CLOSED.
- CACC/CB2C „hidden”: CORRECTED — normal entries.
- C33E/C5B4/424C4 boundaries: OPEN.
- +0x84C semantics: OPEN.
- sibling 39A48/39B30/39C18: OPEN.
- Bitmap 11/12/13 registry records: OPEN.
