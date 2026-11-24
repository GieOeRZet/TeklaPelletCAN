# AUTONOMOUS PASS 115 — UI CONTEXT REGISTRY / 12B DISPATCH RECONCILIATION — 2026-11-23

## Cel
Nie powtarzać wadliwego view_off binding. Zamiast tego domknąć statycznie to, co można domknąć z rejestru MenuTree/context: relację selector -> dispatcher -> +0x12B -> page-family resource.

## HARD
Z wcześniejszego raw analysis:
- FUN_0803C064 ma pełny TBB dla selectorów 0..20.
- selector 16 -> FUN_0803856C -> zapis context+0x12B = 0x11.
- selector 17 -> FUN_08038568 -> zapis context+0x12B = 0x10.
- selector 18 -> FUN_08038574 -> osobna ścieżka.
- FUN_0807EB00 rejestruje/rozpoznaje rekordy po bazie +0x3B4 i stride 0x274, a następnie przekazuje indeks do FUN_0803C064.
- +0x12A, +0x12B i +0x12C są osobnymi wymiarami kontekstu.
- Context 3 używa +0x12B:
  - 0x10 -> resource 0x35,
  - 0x11 -> resource 0x37,
  - pozostałe -> resource 0x32.
- Context 2 używa +0x12B jako switch 0..10 do rodziny resource 0x28..0x31.
- +0x12C ma niezależne wartości 1..4.

## Wniosek
Nie należy mapować +0x12B na aktywny obieg CO ani na prosty numer menu. To selector rodziny/wariantu strony, którego producentem jest rejestrowy dispatcher.

## UI binding boundary
To nie daje jeszcze dowodu A69/A95 -> widget 6068/6120 ani 0xF3->0x2114. Te dwa problemy pozostają OPEN.

## Następny target
S1.3:
1. odzyskać runtime/source registry odpowiadający rekordom 16/17/18;
2. znaleźć ich resource/title/PID/callback;
3. dopiero wtedy powiązać 0x12B z konkretną semantyką;
4. równolegle analizować callsite'y setterów 0x08056028/0x08056040 w granicach źródłowego presenter map.
