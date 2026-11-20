# MULTIPASS-21 — HOME ASSET SEMANTICS / USER VISUAL ANCHORS / REUSE AUDIT
Data: 2026-11-20

## Cel

Włączyć najnowszą obserwację użytkownika jako źródło prawdy dla semantyki trzech realnych bitmap Home: 115, 144, 174. Następnie oddzielić pozycję na Home, znaczenie ikony, możliwość ponownego użycia tego samego bitmapu na innych ekranach oraz firmware resource path.

## PASS 01 — BITMAP 115

User-verified Home position:

115 = kafelek w prawym dolnym rogu ekranu głównego.

W obecnym modelu: Home = dolny prawy kafelek; bitmap ID = 115; semantic family = settings/menu/power-related.

[USER VISUAL][CLOSED dla pozycji Home]
[FW][CLOSED dla istnienia assetu]
[FW writer/path][OPEN]

## PASS 02 — BITMAP 144

User-verified Home position:

144 = ikona CO1 na kafelku Home, 4. kafelek od lewej, czyli również 4. od prawej.

Przy siedmiu widocznych strefach dolnego paska daje to: 1 MENU, 2 paliwo/zasobnik, 3 palnik, 4 CO1/144, 5 pozostały/warunkowy, 6 CWU/174, 7 prawy dolny/115.

[USER VISUAL][CLOSED dla pozycji i semantyki]
[FW][CLOSED dla istnienia assetu]
[FW direct writer][OPEN]

Bitmap 144 ma rodzinę 144/145, co jest zgodne z możliwością stanów/wariantów, ale exact state-selection path nadal pozostaje OPEN.

## PASS 03 — BITMAP 174

User-verified Home position:

174 = ikona CWU, 6. kafelek od lewej, czyli 2. od prawej.

Jednocześnie użytkownik wskazuje ważną rzecz: 174 nie musi być zasobem wyłącznie Home. Ten sam symbol pojawia się również jako część złożonego obrazu zbiornika ciepłej wody na innym ekranie.

Wniosek: semantic identity = CWU/woda użytkowa; Home placement = slot 6/7; reuse on other screen = STRONG/USER VERIFIED; resource ID is a reusable asset, not a unique widget identity.

Nie należy więc szukać wyłącznie 174 -> Home constructor. Należy szukać 174 -> resource resolution -> all consumers -> parent/component context.

[USER VISUAL][CLOSED dla Home]
[RESOURCE SEMANTICS][STRONG]
[REUSE][STRONG/USER OBSERVATION]
[DIRECT FW writer/consumer graph][OPEN]

## PASS 04 — BITMAP FAMILY 174/175/176

Direct bitmap documentation gives:
- 174 = 38x40
- 175 = 37x40
- 176 = 38x40

The atlas groups 174/175/176 as a tap/water family.

Therefore the firmware likely contains a reusable visual family for water/CWU states, but exact roles of 174 vs 175 vs 176 are not to be guessed from dimensions alone.

## PASS 05 — HOME SEVEN-ZONE VISUAL MODEL

The user's observation now closes the semantic positions of three anchors:

| Home slot | Position | Asset | Meaning |
|---:|---|---:|---|
| 1 | first from left | 77 candidate | MENU |
| 2 | second | 51/52/53 family | fuel/hopper |
| 3 | third | unresolved | burner |
| 4 | fourth / fourth from right | 144 | CO1 |
| 5 | fifth | unresolved/conditional | other/CO2/etc. |
| 6 | sixth / second from right | 174 | CWU |
| 7 | seventh / rightmost | 115 | settings/menu/power-related |

Only rows 4, 6, 7 are closed by direct user visual identification. Rows 1, 2 and 3 have prior independent evidence of candidate resources, but their exact firmware Home writer/layout remains separate. Slot 5 remains OPEN.

## PASS 06 — IMPORTANT ARCHITECTURAL CONSEQUENCE

Do NOT model bitmap IDs as widget IDs.

Correct abstraction:
Bitmap ID -> resource table -> BitmapData -> one or more widget instances -> parent/component -> screen.

Therefore one resource may appear on Home, in a detailed screen, in a composite drawing, or in several state variants.

The user's observation about 174 is exactly the kind of evidence that supports this resource/component separation.

## PASS 07 — 47290 IS STILL SEPARATE

The six-slot vertical component X=100, Y=50,84,118,152,186,220 still cannot be identified with the seven horizontal Home zones.

The new user observation does not change that conclusion.

## PASS 08 — 174 TARGETED REVERSE-ENGINEERING ATTACK

Highest-value next search is now not just 174 -> Home, but:
resource 174 (0xAE) -> resource-table entry -> all resource setter/writer paths -> all BitmapData consumers -> parent object -> geometry -> TypedText/state -> screen/factory -> touch/callback.

Special attention: neighboring resource IDs 175 (0xAF), 176 (0xB0), large tank/water composite asset 179, any CWU parameter/sensor screen, and Home bottom component.

This should tell us whether the tank-screen occurrence and Home occurrence share the same Bitmap child class, the same generic bitmap setter, or separate composites using the same resource.

## PASS 09 — 115 / 144 / 174 SHOULD BE TREATED DIFFERENTLY

115: Home-specific visual anchor from user. Reuse elsewhere is not established.

144: Home CO1 icon. Family 144/145. Likely state/variant resource family. Exact writer remains OPEN.

174: Home CWU icon. Independently observed reuse in CWU tank composite. Therefore explicitly a reusable semantic resource.

## PASS 10 — CURRENT EVIDENCE MATRIX

| Fact | Status |
|---|---|
| 115 exists as firmware bitmap | HARD |
| 115 = Home lower-right tile | USER VISUAL CLOSED |
| 144 exists as firmware bitmap | HARD |
| 144 = Home CO1, slot 4 | USER VISUAL CLOSED |
| 174 exists as firmware bitmap | HARD |
| 174 = Home CWU, slot 6 | USER VISUAL CLOSED |
| 174 reused in CWU tank composite | USER OBSERVATION / STRONG |
| 174 is exclusive to Home | REJECTED |
| direct original FW writer for 144 | OPEN |
| direct original FW writer for 174 | OPEN |
| direct original FW writer for 115 | OPEN |
| exact Home factory | OPEN |
| exact Home tile geometry for 115/144/174 | OPEN |
| 7 horizontal zones = 47244+47290 | REJECTED |

## NEXT ATTACK

1. Resource 174 full consumer graph.
2. Resource 144 full consumer graph.
3. Resource 115 full consumer graph.
4. Resource family 174/175/176 comparison.
5. Resource 179 tank composite and its relation to 174.
6. Locate all Bitmap setter calls around resource IDs 0xAE/0xAF/0xB0.
7. Recover parent geometry for Home slot 4/6/7.
8. Recover actual Home screen factory.
9. Reconstruct the seven-zone layout only after those independent paths converge.

## HONESTY NOTE

The three Home positions above are user-observed facts supplied directly in the current investigation. They are stronger than previous speculative labels for those positions, but they do not replace firmware call-site proof. The goal is to use them as anchors to locate the corresponding firmware paths.
