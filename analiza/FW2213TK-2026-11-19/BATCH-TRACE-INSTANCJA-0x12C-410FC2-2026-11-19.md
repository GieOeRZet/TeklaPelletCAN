# BATCH-TRACE-INSTANCJA-0x12C-410FC2-2026-11-19

## Przełom: C064 nie jest jedynym znanym źródłem +0x12C

Znaleziono bezpośredni kodowy zapis pola object+0x12C poza FUN_0803C064:

FUN_08040FC2(param_1,param_2)

W pętli po 22 wpisach tabeli DAT_0804107C:
1. psVar6[2] jest pobierane jako sVar1.
2. jeżeli sVar1 != -1, firmware pobiera obiekt przez FUN_080314BA().
3. zapisuje object+0x12C = sVar1.
4. bierze pierwsze pole wpisu: iVar3 = *psVar6.
5. odczytuje wartość parametru przez FUN_08036FF2(context, iVar3).
6. przekazuje ją do FUN_08040E46(object_context, iVar5, uVar2).

Wpis tabeli ma więc strukturę co najmniej [param_index, ..., instance_or_special_value]. Tabela jest iterowana 22 razy, iVar5 = 0..0x15.

## Drugi dowód: setter analogiczny

FUN_08041020(param_1,param_2,param_3) pobiera DAT_08041080[param_2*6]. Jeżeli wartość != -1, zapisuje ją do object+0x12C, a następnie wywołuje FUN_08037212(context, DAT_0804107C[param_2*3], param_3).

Ta sama tabela DAT_0804107C jest więc używana zarówno przy odczycie/aktualizacji jak i zapisie.

## Co to zmienia w modelu C064

Dotychczasowy model param_2 -> C064 -> C218 -> class 1..4 -> +0x12B/+0x12C pozostaje prawdziwy jako jedna ścieżka klasyfikacji obiektu, ale C064 nie jest jedynym miejscem ustawiającym instancję.

Mamy co najmniej dwie ścieżki:

Ścieżka A — klasyfikator C064:
param_2 -> DAT_0803C218[param_2] -> class 1..4 -> +0x12B = class -> +0x12C = class

Ścieżka B — tabela 4107C:
DAT_0804107C[i] -> trzecie pole -> object+0x12C
oraz równolegle:
DAT_0804107C[i].param_index -> FUN_08036FF2 -> FUN_08040E46

## Rozróżnienie

C064 ustawia jednocześnie +0x12B = class i +0x12C = 1..4.
FUN_08040FC2 ustawia tylko +0x12C z trzeciego pola tabeli.

Na obecnym etapie C064 wygląda na klasyfikację/wybór wariantu obiektu, a 4107C na runtime przypisanie instancji do konkretnego wpisu/slotu. Nie scalamy tych mechanizmów bez kolejnego dowodu.

## Nowy priorytet

1. odzyskać DAT_0804107C (22 x 3 x 16 bit),
2. ustalić które pierwsze pola są indeksami parametrów CO,
3. ustalić które trzecie pola przyjmują 1,2,3,4,
4. prześledzić FUN_08040E46 i FUN_08040E2A,
5. dopiero potem wrócić do C064 i sprawdzić, czy C218 opisuje ten sam zestaw slotów.

To może dać bezpośrednią odpowiedź, jak firmware materializuje CO1..CO4 w runtime, nawet jeśli wejście do C064 pozostanie pośrednie.

## Pewność

Twarde: FUN_08040FC2 zapisuje +0x12C; źródłem jest trzecie pole DAT_0804107C; tabela ma 22 wpisy; FUN_08041020 używa tej samej tabeli; C064 niezależnie ustawia +0x12B/+0x12C dla klas 1..4.

Nieznane: pełna zawartość DAT_0804107C, semantyka wszystkich 22 wpisów, które wpisy dotyczą CO1..CO4 oraz kolejność C064 vs 410FC2.