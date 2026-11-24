# MAPA DOCELOWA — szkic przed FREEZE

Stan bazowy: 9bd6139707f4c6a2cd9c6907fb7dfe5202c18239
Branch roboczy: chatgpt/porzadek-inwentarz-2026-11-24

## Zasady
- Niczego nie przenoszę ani nie usuwam w tym etapie.
- ui_model jest proponowanym jedynym źródłem prawdy dla modelu UI.
- evidence przechowuje dowody i wyniki pomiarów.
- raw przechowuje surowe wyniki z indeksem do końca projektu.
- Usuwanie tylko dla plików identycznych co do bajtu.
- Pozostałe pliki trafiają do archiwum dopiero po decyzji, z adnotacją „zastąpione przez X”.
- Erraty zostają przy oryginałach.
- DO_PYTANIA = brak wystarczającego dowodu.

## Proponowana struktura
NewEstyma/
  ui_model/
  evidence/reports/
  evidence/data/
  evidence/visual/
  raw/
  porzadek/

## Stary adres -> nowy adres
analiza_archiwum/FW2213TK-2026-11-18/CO2-INSTANCJA-INDEXOWANIE.md;NewEstyma/evidence/reports/FW2213TK-2026-11-18/CO2-INSTANCJA-INDEXOWANIE.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-18/CO2-PELNY-ZESTAW-2026-11-18.md;NewEstyma/evidence/reports/FW2213TK-2026-11-18/CO2-PELNY-ZESTAW-2026-11-18.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-18/CO2-REWIZJA.md;NewEstyma/evidence/reports/FW2213TK-2026-11-18/CO2-REWIZJA.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-18/CO2-TEKSTY-PARAMETRY.md;NewEstyma/evidence/reports/FW2213TK-2026-11-18/CO2-TEKSTY-PARAMETRY.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-18/ESTYMA-MANUAL-CO1-CO2-KORELACJA.md;NewEstyma/evidence/reports/FW2213TK-2026-11-18/ESTYMA-MANUAL-CO1-CO2-KORELACJA.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-18/MAIN-SCREEN-UI-REKONSTRUKCJA.md;NewEstyma/evidence/reports/FW2213TK-2026-11-18/MAIN-SCREEN-UI-REKONSTRUKCJA.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-18/TOUCHGFX-REPLIKA-1-1.md;NewEstyma/evidence/reports/FW2213TK-2026-11-18/TOUCHGFX-REPLIKA-1-1.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-18/TOUCHGFX-TEXT-DATABASE.md;NewEstyma/evidence/reports/FW2213TK-2026-11-18/TOUCHGFX-TEXT-DATABASE.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/1167A-CO-INSTANCE-LOOKUP.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/1167A-CO-INSTANCE-LOOKUP.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/ARCHITEKTURA-TOUCH-BIG-KOREKTA.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/ARCHITEKTURA-TOUCH-BIG-KOREKTA.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/ARCHITEKTURA-WSPOLNEGO-STORAGE-CO1-CO4.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/ARCHITEKTURA-WSPOLNEGO-STORAGE-CO1-CO4.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/ASSET-ATLAS-189-BITMAPS-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/ASSET-ATLAS-189-BITMAPS-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-051-052-PELLET-HOPPER-TRACE-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-051-052-PELLET-HOPPER-TRACE-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-0x12B-UI-CO1-CO4-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-0x12B-UI-CO1-CO4-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-0x12B-UI-WIDGET-VALUE-CHAIN-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-0x12B-UI-WIDGET-VALUE-CHAIN-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-2105-GENERIC-ENGINE-GRANICA-AKTYWACJI-CO-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-2105-GENERIC-ENGINE-GRANICA-AKTYWACJI-CO-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-370A-UPDATE-GEOMETRY-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-370A-UPDATE-GEOMETRY-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-469E8-ACTIVE-MODULE-BINDING-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-469E8-ACTIVE-MODULE-BINDING-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-469E8-BITMAP-WRITER-VTABLE-TRACE-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-469E8-BITMAP-WRITER-VTABLE-TRACE-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-47290-UPDATE-REGISTRY-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-47290-UPDATE-REGISTRY-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-ACCESS-158-AND-HEATING-METADATA-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-ACCESS-158-AND-HEATING-METADATA-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-ASSET-CO1-CO2-CONFIG-TRACE-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-ASSET-CO1-CO2-CONFIG-TRACE-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-BOILER-GRAPHICS-REAL-ASSETS-VS-MOCK-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-BOILER-GRAPHICS-REAL-ASSETS-VS-MOCK-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-BOILER-IMAGE-NEGATIVE-CALLSITE-AND-370A-CALLBACK-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-BOILER-IMAGE-NEGATIVE-CALLSITE-AND-370A-CALLBACK-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-C064-CHAIN-37D00-INSTANCJA-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-C064-CHAIN-37D00-INSTANCJA-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-C064-DIRECT-CLASS-INSTANCE-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-C064-DIRECT-CLASS-INSTANCE-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-CALLBACK-COMPARISON-AND-469E8-UPDATE-BOUNDARY-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-CALLBACK-COMPARISON-AND-469E8-UPDATE-BOUNDARY-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-CALLBACK-ENGINE-317AE-469E8-VTABLE-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-CALLBACK-ENGINE-317AE-469E8-VTABLE-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-CO-INSTANCE-REJESTRACJA-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-CO-INSTANCE-REJESTRACJA-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-CO1-CO2-VARIANT-GEOMETRIA-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-CO1-CO2-VARIANT-GEOMETRIA-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-CO2-612E0-HELPER-BOUNDARY-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-CO2-612E0-HELPER-BOUNDARY-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-CO2-WIDGET-GEOMETRY-VTABLE-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-CO2-WIDGET-GEOMETRY-VTABLE-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-CONSOLIDACJA-C064-4107C-DATA-BOUNDARY-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-CONSOLIDACJA-C064-4107C-DATA-BOUNDARY-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-DUZA-TOZSAMOSC-KOTLA-TOUCHGFX-WARIANT-GRAFIKA-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-DUZA-TOZSAMOSC-KOTLA-TOUCHGFX-WARIANT-GRAFIKA-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-FIRMWARE-BIN-TRACE-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-FIRMWARE-BIN-TRACE-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-FOURTH-PASS-C33E-C5B4-GEOMETRY-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-FOURTH-PASS-C33E-C5B4-GEOMETRY-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-GRANICA-2105-MODULY-COUNT4-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-GRANICA-2105-MODULY-COUNT4-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-HEATING-12PARAM-158-MODE-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-HEATING-12PARAM-158-MODE-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-HOME-47290-ROLE-CORRECTION-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-HOME-47290-ROLE-CORRECTION-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-HOME-BOILER-WIDGET-469E8-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-HOME-BOILER-WIDGET-469E8-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-HOME-HEADER-4A114-AND-REAL-BOILER-BITMAP14-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-HOME-HEADER-4A114-AND-REAL-BOILER-BITMAP14-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-HOME-HOST-2E716-469E8-BOUNDARY-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-HOME-HOST-2E716-469E8-BOUNDARY-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-HOME-NEXT-2E716-AND-370A-BOUNDARY-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-HOME-NEXT-2E716-AND-370A-BOUNDARY-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-HOME-ROOT-BOILER-GRAPHICS-SPINE-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-HOME-ROOT-BOILER-GRAPHICS-SPINE-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-HOME-SCREEN-ZONES-7x-BOTTOM-UPPER-WIDGET-TREE-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-HOME-SCREEN-ZONES-7x-BOTTOM-UPPER-WIDGET-TREE-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-IDENTYFIKACJA-KOTLA-FW-VARIANT-GRAFIKA-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-IDENTYFIKACJA-KOTLA-FW-VARIANT-GRAFIKA-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-KOREKTA-UI-WARUNKOWE-WIDGETY-CO-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-KOREKTA-UI-WARUNKOWE-WIDGETY-CO-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-METHOD-CLUSTER-C5B4-CACC-CB2C-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-METHOD-CLUSTER-C5B4-CACC-CB2C-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-MOST-2105-WARIANTY-INSTANCJE-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-MOST-2105-WARIANTY-INSTANCJE-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-MULTIPASS-47290-C33E-39XXX-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-MULTIPASS-47290-C33E-39XXX-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-MULTIPASS-5C-BITMAP-SIBLINGS-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-MULTIPASS-5C-BITMAP-SIBLINGS-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-MULTIPASS-C064-VTABLE-10E-CO-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-MULTIPASS-C064-VTABLE-10E-CO-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-MULTIPASS-CO2-UI-CHAIN-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-MULTIPASS-CO2-UI-CHAIN-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-MULTIPASS-CURRENT-HOME-BOTTOM-RECONCILIATION-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-MULTIPASS-CURRENT-HOME-BOTTOM-RECONCILIATION-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-MULTIPASS-HOME-BOTTOM-CORRECTION-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-MULTIPASS-HOME-BOTTOM-CORRECTION-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-MULTIPASS-HOPPER-CAN-GEOMETRY-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-MULTIPASS-HOPPER-CAN-GEOMETRY-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-MULTIPASS-VERTICAL-TRACE-370A-MODEL-469E8-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-MULTIPASS-VERTICAL-TRACE-370A-MODEL-469E8-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-PARAMETER-CONFIG-VS-RECORD-ENGINE-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-PARAMETER-CONFIG-VS-RECORD-ENGINE-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-PERSISTENT-CONTINUATION-MEMORY-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-PERSISTENT-CONTINUATION-MEMORY-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-RAW-151-152-47290-AND-BOTTOM-BAR-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-RAW-151-152-47290-AND-BOTTOM-BAR-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-RAW-BIN-RECOVERY-469E8-47040-370A-CORRECTION-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-RAW-BIN-RECOVERY-469E8-47040-370A-CORRECTION-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-RAW-CORRECTION-121-370A-CASCADE-469E8-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-RAW-CORRECTION-121-370A-CASCADE-469E8-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-RAW-MULTIPASS-121-370A-UI-BITMAP-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-RAW-MULTIPASS-121-370A-UI-BITMAP-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-REORIENTACJA-HOME-CASCADE-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-REORIENTACJA-HOME-CASCADE-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-REPO-AUDIT-HIDDEN-METHOD-CORRECTION-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-REPO-AUDIT-HIDDEN-METHOD-CORRECTION-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-REVALIDATION-318B4-469E8-370A-BRANCH-SPLIT-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-REVALIDATION-318B4-469E8-370A-BRANCH-SPLIT-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-REWALIDACJA-CO-OBIEKT-C064-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-REWALIDACJA-CO-OBIEKT-C064-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-SCREENSHOT-BOTTOM-7-ZONES-RIGHT-BUTTON-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-SCREENSHOT-BOTTOM-7-ZONES-RIGHT-BUTTON-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-SPINE-HOME-HEATING-INSTANCE-WIDGET-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-SPINE-HOME-HEATING-INSTANCE-WIDGET-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-TOUCH-1-1-ARCHITEKTURA-UI-PARAMETR-OBIEKT-CAN-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-TOUCH-1-1-ARCHITEKTURA-UI-PARAMETR-OBIEKT-CAN-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-TOUCHGFX-RENDERER-TRACE-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-TOUCHGFX-RENDERER-TRACE-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-TRACE-10E-3505-UI-CO-ASSET-BOUNDARY-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-TRACE-10E-3505-UI-CO-ASSET-BOUNDARY-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-TRACE-C064-SINGLETON-MODULE-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-TRACE-C064-SINGLETON-MODULE-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-TRACE-CO-AKTYWACJA-GRANICA-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-TRACE-CO-AKTYWACJA-GRANICA-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-TRACE-INSTANCJA-0x12C-410FC2-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-TRACE-INSTANCJA-0x12C-410FC2-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-TRACE-UI-2105-UNIKALNY-CALLSITE-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-TRACE-UI-2105-UNIKALNY-CALLSITE-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-TYPE-INSTANCE-0x12B-0x12C-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-TYPE-INSTANCE-0x12B-0x12C-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-UI-CO2-SCREEN-SIZE-OBJECT-CHAIN-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-UI-CO2-SCREEN-SIZE-OBJECT-CHAIN-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-UI-FRAGMENT-ALREADY-BUILDABLE-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-UI-FRAGMENT-ALREADY-BUILDABLE-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BATCH-WHEELSELECTOR-SOURCE-BOUNDARY-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BATCH-WHEELSELECTOR-SOURCE-BOUNDARY-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BITMAP-MAP-DIRECT-BIN-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BITMAP-MAP-DIRECT-BIN-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/BITMAP-PREVIEW-MAP-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/BITMAP-PREVIEW-MAP-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/CHAT-CONTINUITY-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/CHAT-CONTINUITY-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/CO-INSTANCJE-REJESTRACJA-vs-MODUL.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/CO-INSTANCJE-REJESTRACJA-vs-MODUL.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/CONTINUATION-INSTRUCTION-TRACE-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/CONTINUATION-INSTRUCTION-TRACE-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/CORRECTION-47290-VERTICAL-NOT-BOTTOM-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/CORRECTION-47290-VERTICAL-NOT-BOTTOM-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/DYNAMICZNE-INSTANCJE-CO-ZRODLO-INSTANCJI.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/DYNAMICZNE-INSTANCJE-CO-ZRODLO-INSTANCJI.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/HANDOFF-NOWY-CHAT-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/HANDOFF-NOWY-CHAT-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/INSTANCJA-0x12C-KONFIGURACJA-I-DALSZY-TRACE.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/INSTANCJA-0x12C-KONFIGURACJA-I-DALSZY-TRACE.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/KOREKTA-4107C-TEST-IO-vs-CO.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/KOREKTA-4107C-TEST-IO-vs-CO.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/MAPOWANIE-PANEL-vs-RAM.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/MAPOWANIE-PANEL-vs-RAM.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/MASTER-STATE-CONSOLIDATED-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/MASTER-STATE-CONSOLIDATED-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/MASTER-STATE-HANDOFF-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/MASTER-STATE-HANDOFF-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/MECHANIZM-REKORDOW-PARAMETROW.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/MECHANIZM-REKORDOW-PARAMETROW.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/MODUL-CH-INSTANCJA-0x12C-I-LOOKUP.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/MODUL-CH-INSTANCJA-0x12C-I-LOOKUP.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/PAKIET-BIG-INSTANCJE-KLASYFIKACJA-OBIEKTOW.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/PAKIET-BIG-INSTANCJE-KLASYFIKACJA-OBIEKTOW.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/PANEL-1-1-FULL-CONFIGURATION-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/PANEL-1-1-FULL-CONFIGURATION-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/PARAMETRY-MECHANIZM-INDEXOWANIA.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/PARAMETRY-MECHANIZM-INDEXOWANIA.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/PRZELOM-1167A-TABLICE-OBIEKTOWE-I-STORAGE.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/PRZELOM-1167A-TABLICE-OBIEKTOWE-I-STORAGE.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/PRZELOM-2105-LICZBA-OBWODOW-CO.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/PRZELOM-2105-LICZBA-OBWODOW-CO.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/PRZELOM-CAN-DO-RAM-PARAMETRU-0x62B22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/PRZELOM-CAN-DO-RAM-PARAMETRU-0x62B22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/PRZELOM-CO-2105-ROZDZIELENIE-COUNT-vs-CONFIG-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/PRZELOM-CO-2105-ROZDZIELENIE-COUNT-vs-CONFIG-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/PRZELOM-MAIN-IO-EXPANSION-PROFIL-WARIANTY.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/PRZELOM-MAIN-IO-EXPANSION-PROFIL-WARIANTY.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/PRZELOM-MODULY-VARIANTY-INSTANCJE-CH.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/PRZELOM-MODULY-VARIANTY-INSTANCJE-CH.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/PRZELOM-REJESTRACJA-CO1-CO4-PETLA-0x809A.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/PRZELOM-REJESTRACJA-CO1-CO4-PETLA-0x809A.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/REKORD-0x2C-CZTERY-INSTANCJE.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/REKORD-0x2C-CZTERY-INSTANCJE.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/REKORD-DESKRYPTOR-WARTOSC-0x14700-0x11812.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/REKORD-DESKRYPTOR-WARTOSC-0x14700-0x11812.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/REWALIDACJA-2105-vs-3505-UI-TRACE-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/REWALIDACJA-2105-vs-3505-UI-TRACE-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/REWALIDACJA-ADRESOW-38130-3212C-2026-11-19.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/REWALIDACJA-ADRESOW-38130-3212C-2026-11-19.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/START-HERE-FOR-NEXT-AGENT.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/START-HERE-FOR-NEXT-AGENT.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-19/TRACE-WARIANTOW-MAIN-IO-EXPANSION-PROFIL.md;NewEstyma/evidence/reports/FW2213TK-2026-11-19/TRACE-WARIANTOW-MAIN-IO-EXPANSION-PROFIL.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/BATCH-6154-CONTEXT-INSTANCE-AND-PAGE-FAMILY-MULTIPASS-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/BATCH-6154-CONTEXT-INSTANCE-AND-PAGE-FAMILY-MULTIPASS-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/BATCH-6154-DEEP-MULTIPASS-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/BATCH-6154-DEEP-MULTIPASS-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/BATCH-6154-LEVEL3-UI-GATES-MULTIPASS-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/BATCH-6154-LEVEL3-UI-GATES-MULTIPASS-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/BATCH-ANIMATION-ENGINE-AND-ACTUATOR-MAPS-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/BATCH-ANIMATION-ENGINE-AND-ACTUATOR-MAPS-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/BATCH-CONFIG-ACCESS-RESOLVER-MULTIPASS-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/BATCH-CONFIG-ACCESS-RESOLVER-MULTIPASS-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/BATCH-MAIN-MENU-ACCESS-SECOND-PASS-21-RECORD-CORRECTION-MULTIPASS-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/BATCH-MAIN-MENU-ACCESS-SECOND-PASS-21-RECORD-CORRECTION-MULTIPASS-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/BATCH-MAIN-MENU-ROW-FORENSICS-MULTIPASS-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/BATCH-MAIN-MENU-ROW-FORENSICS-MULTIPASS-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/BATCH-ORIGINAL-SOFTWARE-ARCHITECTURE-RESET-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/BATCH-ORIGINAL-SOFTWARE-ARCHITECTURE-RESET-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/BATCH-ORIGINAL-TOUCH-HOME-IMPLEMENTATION-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/BATCH-ORIGINAL-TOUCH-HOME-IMPLEMENTATION-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/BATCH-PIN-ACCESS-AND-RESET-MULTIPASS-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/BATCH-PIN-ACCESS-AND-RESET-MULTIPASS-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/BATCH-WHOLE-SOFTWARE-MULTIPASS-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/BATCH-WHOLE-SOFTWARE-MULTIPASS-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/CHAT-ARCHIVE-RAW-STATUS.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/CHAT-ARCHIVE-RAW-STATUS.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/CHAT-CONTINUITY-2026-11-20-ARCHITECTURE-RESET.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/CHAT-CONTINUITY-2026-11-20-ARCHITECTURE-RESET.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/CHAT-CONTINUITY-2026-11-20-BLOWER-FAMILIES-WHOLE-SOFTWARE-RESET.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/CHAT-CONTINUITY-2026-11-20-BLOWER-FAMILIES-WHOLE-SOFTWARE-RESET.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/CHAT-CONTINUITY-2026-11-20-MULTIPASS-20-CONFIG-CORRECTION.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/CHAT-CONTINUITY-2026-11-20-MULTIPASS-20-CONFIG-CORRECTION.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/CHAT-CONTINUITY-2026-11-20-MULTIPASS-TRAINING.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/CHAT-CONTINUITY-2026-11-20-MULTIPASS-TRAINING.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/CHAT-CONTINUITY-INDEX-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/CHAT-CONTINUITY-INDEX-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/CHAT-HANDOFF-NEXT-2026-11-20-HOME-TRACE.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/CHAT-HANDOFF-NEXT-2026-11-20-HOME-TRACE.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/CHECKPOINT-47290-LANGUAGE-UPDATE-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/CHECKPOINT-47290-LANGUAGE-UPDATE-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/CHECKPOINT-47290-SOURCE-CONTEXT-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/CHECKPOINT-47290-SOURCE-CONTEXT-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/DOCUMENTATION-COVERAGE-AUDIT-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/DOCUMENTATION-COVERAGE-AUDIT-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/ETAP14-EXECUTION-MANIFEST-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/ETAP14-EXECUTION-MANIFEST-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/ETAP8-RECOVERED-DECOMPILED-TARGETS-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/ETAP8-RECOVERED-DECOMPILED-TARGETS-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/EXTERNAL-AGENT-HARD-TASK-2E-DDCA-2EADE-7F5EC-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/EXTERNAL-AGENT-HARD-TASK-2E-DDCA-2EADE-7F5EC-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/EXTERNAL-AGENT-RAW-DATA-PACK-0x68-GRAPH-REGISTRY-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/EXTERNAL-AGENT-RAW-DATA-PACK-0x68-GRAPH-REGISTRY-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/EXTERNAL-AGENT-SINGLE-FILE-HARD-TASK-2026-11-20.txt;NewEstyma/evidence/reports/FW2213TK-2026-11-20/EXTERNAL-AGENT-SINGLE-FILE-HARD-TASK-2026-11-20.txt;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/HOME-GEOMETRY-FW-ONLY-MULTIPASS-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/HOME-GEOMETRY-FW-ONLY-MULTIPASS-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/HOME-GEOMETRY-USER-VISUAL-CORRELATION-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/HOME-GEOMETRY-USER-VISUAL-CORRELATION-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/MASTER-HANDOFF-FOR-NEXT-AGENT-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/MASTER-HANDOFF-FOR-NEXT-AGENT-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/MULTIPASS-12-6154-DEEP-AUDIT-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/MULTIPASS-12-6154-DEEP-AUDIT-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/MULTIPASS-13-6154-NUMERIC-CONTROL-PARAM-BINDING-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/MULTIPASS-13-6154-NUMERIC-CONTROL-PARAM-BINDING-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/MULTIPASS-14-6154-17-WRAPPER-MATRIX-ATTACK-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/MULTIPASS-14-6154-17-WRAPPER-MATRIX-ATTACK-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/MULTIPASS-15-GRAPH-056-057-2261-227A-HARD-TRACE-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/MULTIPASS-15-GRAPH-056-057-2261-227A-HARD-TRACE-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/MULTIPASS-16-REUSABLE-GRAPH-MARKERS-CONFIG-UI-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/MULTIPASS-16-REUSABLE-GRAPH-MARKERS-CONFIG-UI-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/MULTIPASS-17-BLOWER-FAMILIES-CONFIGURATION-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/MULTIPASS-17-BLOWER-FAMILIES-CONFIGURATION-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/MULTIPASS-18-DIRECT-STRING-AND-FAN-BRANCH-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/MULTIPASS-18-DIRECT-STRING-AND-FAN-BRANCH-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/MULTIPASS-19-0x68-RESOLVER-CORRECTION-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/MULTIPASS-19-0x68-RESOLVER-CORRECTION-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/MULTIPASS-19-WHOLE-SOFTWARE-SOURCE-CROSSCHECK-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/MULTIPASS-19-WHOLE-SOFTWARE-SOURCE-CROSSCHECK-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/MULTIPASS-20-0x47-0x48-GRAPH-FAMILY-CLOSURE-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/MULTIPASS-20-0x47-0x48-GRAPH-FAMILY-CLOSURE-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/MULTIPASS-20-DEEP-CONFIG-ACCESS-SOURCE-OF-TRUTH-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/MULTIPASS-20-DEEP-CONFIG-ACCESS-SOURCE-OF-TRUTH-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/MULTIPASS-21-HOME-ASSET-SEMANTICS-115-144-174-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/MULTIPASS-21-HOME-ASSET-SEMANTICS-115-144-174-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/MULTIPASS-21-IAR-INIT-TABLE-EXECUTION-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/MULTIPASS-21-IAR-INIT-TABLE-EXECUTION-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/MULTIPASS-22-DEEP-CROSSCHECK-174-2105-MANUFACTURER-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/MULTIPASS-22-DEEP-CROSSCHECK-174-2105-MANUFACTURER-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/MULTIPASS-22-IAR-LZ77-DATA-CLOSURE-AND-480C0-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/MULTIPASS-22-IAR-LZ77-DATA-CLOSURE-AND-480C0-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/MULTIPASS-2261-2265-GRAPH-VS-47290-CORRECTION-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/MULTIPASS-2261-2265-GRAPH-VS-47290-CORRECTION-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/MULTIPASS-23-IAR-LZ77-47-48-CLOSURE-480C0-TYPEDTEXT-RAW-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/MULTIPASS-23-IAR-LZ77-47-48-CLOSURE-480C0-TYPEDTEXT-RAW-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/MULTIPASS-24-CONSOLIDATED-UPLOADED-RESULTS-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/MULTIPASS-24-CONSOLIDATED-UPLOADED-RESULTS-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/MULTIPASS-25-47290-47-48-OPTION-TABLES-PIN-4E9DC-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/MULTIPASS-25-47290-47-48-OPTION-TABLES-PIN-4E9DC-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/MULTIPASS-47290-3EC18-SEMANTIC-DISAMBIGUATION-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/MULTIPASS-47290-3EC18-SEMANTIC-DISAMBIGUATION-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/MULTIPASS-47290-LANGUAGE-UPDATE-DEEP-ATTACK-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/MULTIPASS-47290-LANGUAGE-UPDATE-DEEP-ATTACK-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/MULTIPASS-47290-SOURCE-CONTEXT-DEEP-TRACE-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/MULTIPASS-47290-SOURCE-CONTEXT-DEEP-TRACE-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/MULTIPASS-HOME-01-115-144-174-FUN31CCC-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/MULTIPASS-HOME-01-115-144-174-FUN31CCC-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/P0-FUN-0803E714-PANEL-LIST-BUILDER-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/P0-FUN-0803E714-PANEL-LIST-BUILDER-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/RAPORT-DLA-AGENTA-CI-GITHUB-ETAP3.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/RAPORT-DLA-AGENTA-CI-GITHUB-ETAP3.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/RAPORT-ETAP5-CAN-TX-C064-VTABLE-WIDGET-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/RAPORT-ETAP5-CAN-TX-C064-VTABLE-WIDGET-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/RAPORT-ETAP6-TX-SRAM-VTABLE-WIDGET-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/RAPORT-ETAP6-TX-SRAM-VTABLE-WIDGET-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/RAPORT-ETAP7-TX-UI-SRAM-VTABLE-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/RAPORT-ETAP7-TX-UI-SRAM-VTABLE-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/RAW-DECOMPILED-SNIPPET-BUNDLE-0x68-GRAPH-REGISTRY-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/RAW-DECOMPILED-SNIPPET-BUNDLE-0x68-GRAPH-REGISTRY-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/SOURCE-OF-TRUTH-POLICY-2026-11-20.md;NewEstyma/evidence/reports/FW2213TK-2026-11-20/SOURCE-OF-TRUTH-POLICY-2026-11-20.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/080307bc-decompiled.c.txt;NewEstyma/raw/decompiled/080307bc-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/08031ccc-decompiled.c.txt;NewEstyma/raw/decompiled/08031ccc-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/08036ff2-decompiled.c.txt;NewEstyma/raw/decompiled/08036ff2-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/080370c0-decompiled.c.txt;NewEstyma/raw/decompiled/080370c0-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/0803716e-decompiled.c.txt;NewEstyma/raw/decompiled/0803716e-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/08037212-decompiled.c.txt;NewEstyma/raw/decompiled/08037212-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/0803c064-decompiled.c.txt;NewEstyma/raw/decompiled/0803c064-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/0803cf54-decompiled.c.txt;NewEstyma/raw/decompiled/0803cf54-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/0803e5ac-decompiled.c.txt;NewEstyma/raw/decompiled/0803e5ac-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/0803e714-decompiled.c.txt;NewEstyma/raw/decompiled/0803e714-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/0803ec18-decompiled.c.txt;NewEstyma/raw/decompiled/0803ec18-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/0803eecc-decompiled.c.txt;NewEstyma/raw/decompiled/0803eecc-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/08043a36-decompiled.c.txt;NewEstyma/raw/decompiled/08043a36-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/08043a74-decompiled.c.txt;NewEstyma/raw/decompiled/08043a74-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/08043b44-decompiled.c.txt;NewEstyma/raw/decompiled/08043b44-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/0804752c-decompiled.c.txt;NewEstyma/raw/decompiled/0804752c-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/08047604-decompiled.c.txt;NewEstyma/raw/decompiled/08047604-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/08047a8a-decompiled.c.txt;NewEstyma/raw/decompiled/08047a8a-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/08047b80-decompiled.c.txt;NewEstyma/raw/decompiled/08047b80-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/08047ba6-decompiled.c.txt;NewEstyma/raw/decompiled/08047ba6-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/08047c1a-decompiled.c.txt;NewEstyma/raw/decompiled/08047c1a-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/08047d80-decompiled.c.txt;NewEstyma/raw/decompiled/08047d80-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/08048468-decompiled.c.txt;NewEstyma/raw/decompiled/08048468-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/080484b0-decompiled.c.txt;NewEstyma/raw/decompiled/080484b0-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/080484f0-decompiled.c.txt;NewEstyma/raw/decompiled/080484f0-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/08048520-decompiled.c.txt;NewEstyma/raw/decompiled/08048520-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/08048624-decompiled.c.txt;NewEstyma/raw/decompiled/08048624-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-20/raw-snippets/0807eb36-decompiled.c.txt;NewEstyma/raw/decompiled/0807eb36-decompiled.c.txt;PROPOZYCJA;Surowy materiał.
analiza_archiwum/FW2213TK-2026-11-21/ARTIFACT-INDEX-ETAP31-52.md;NewEstyma/evidence/reports/FW2213TK-2026-11-21/ARTIFACT-INDEX-ETAP31-52.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-21/BASE-ADDRESS-CORRECTION-2026-11-21.md;NewEstyma/evidence/reports/FW2213TK-2026-11-21/BASE-ADDRESS-CORRECTION-2026-11-21.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-21/CONTINUATION-PROMPT-ETAP31.md;NewEstyma/evidence/reports/FW2213TK-2026-11-21/CONTINUATION-PROMPT-ETAP31.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-21/CONTINUATION-PROMPT-OPEN1-P5.md;NewEstyma/evidence/reports/FW2213TK-2026-11-21/CONTINUATION-PROMPT-OPEN1-P5.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-21/ETAP15-EXECUTION-REPORT-2026-11-21.md;NewEstyma/evidence/reports/FW2213TK-2026-11-21/ETAP15-EXECUTION-REPORT-2026-11-21.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-21/ETAP16-EXECUTION-REPORT-2026-11-21.md;NewEstyma/evidence/reports/FW2213TK-2026-11-21/ETAP16-EXECUTION-REPORT-2026-11-21.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-21/ETAP17-EXECUTION-REPORT-2026-11-21.md;NewEstyma/evidence/reports/FW2213TK-2026-11-21/ETAP17-EXECUTION-REPORT-2026-11-21.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-21/ETAP18-EXECUTION-REPORT-2026-11-21.md;NewEstyma/evidence/reports/FW2213TK-2026-11-21/ETAP18-EXECUTION-REPORT-2026-11-21.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-21/ETAP19-EXECUTION-REPORT-2026-11-21.md;NewEstyma/evidence/reports/FW2213TK-2026-11-21/ETAP19-EXECUTION-REPORT-2026-11-21.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-21/ETAP20-EXECUTION-REPORT-2026-11-21.md;NewEstyma/evidence/reports/FW2213TK-2026-11-21/ETAP20-EXECUTION-REPORT-2026-11-21.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-21/ETAP22-EXECUTION-REPORT-2026-11-21.md;NewEstyma/evidence/reports/FW2213TK-2026-11-21/ETAP22-EXECUTION-REPORT-2026-11-21.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-21/ETAP23-EXECUTION-REPORT-2026-11-21.md;NewEstyma/evidence/reports/FW2213TK-2026-11-21/ETAP23-EXECUTION-REPORT-2026-11-21.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-21/ETAP24-EXECUTION-REPORT-2026-11-21.md;NewEstyma/evidence/reports/FW2213TK-2026-11-21/ETAP24-EXECUTION-REPORT-2026-11-21.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-21/FULL-HANDOFF-2026-11-21.md;NewEstyma/evidence/reports/FW2213TK-2026-11-21/FULL-HANDOFF-2026-11-21.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-21/FULL-HANDOFF-CORRECTED-2026-11-21.md;NewEstyma/evidence/reports/FW2213TK-2026-11-21/FULL-HANDOFF-CORRECTED-2026-11-21.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-21/MASTER-CONTEXT-ETAP1-30-ESP32C6.md;NewEstyma/evidence/reports/FW2213TK-2026-11-21/MASTER-CONTEXT-ETAP1-30-ESP32C6.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-21/MASTER-CONTEXT-ETAP1-38-P0-P6.md;NewEstyma/evidence/reports/FW2213TK-2026-11-21/MASTER-CONTEXT-ETAP1-38-P0-P6.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-21/MASTER-CONTEXT-ETAP1-52-FINAL.md;NewEstyma/evidence/reports/FW2213TK-2026-11-21/MASTER-CONTEXT-ETAP1-52-FINAL.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-21/RAW_PACKET7_OPEN1_P4.txt;NewEstyma/evidence/reports/FW2213TK-2026-11-21/RAW_PACKET7_OPEN1_P4.txt;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-21/RAW_PACKET8_OPEN1_P5.txt;NewEstyma/evidence/reports/FW2213TK-2026-11-21/RAW_PACKET8_OPEN1_P5.txt;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-21/RE-EXPLORER-README.md;NewEstyma/evidence/reports/FW2213TK-2026-11-21/RE-EXPLORER-README.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/10-PASS-PARAMETER-SYNC-PUBLICATION-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/10-PASS-PARAMETER-SYNC-PUBLICATION-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-10-PASS-08-CAN-OBJECT-GRAPH-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-10-PASS-08-CAN-OBJECT-GRAPH-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-07-MENU-D60-RECONCILIATION-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-07-MENU-D60-RECONCILIATION-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-09-OPEN1-RUNTIME-CLOSURE-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-09-OPEN1-RUNTIME-CLOSURE-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-10-ESTYMA-TASK-SPINE-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-10-ESTYMA-TASK-SPINE-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-11-PARAMETER-MANAGER-CLOSURE-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-11-PARAMETER-MANAGER-CLOSURE-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-12-RANGE-DEFAULT-CLOSURE-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-12-RANGE-DEFAULT-CLOSURE-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-13-STARTUP-REGISTRATION-CHAIN-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-13-STARTUP-REGISTRATION-CHAIN-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-14-RUNTIME-CALLBACK-BRIDGE-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-14-RUNTIME-CALLBACK-BRIDGE-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-15-RE-TOOLCHAIN-UPGRADE-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-15-RE-TOOLCHAIN-UPGRADE-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-16-EXHAUSTIVE-OPEN1-RECHECK-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-16-EXHAUSTIVE-OPEN1-RECHECK-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-17-PARAMETER-MANAGER-SCHEDULER-CLOSURE-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-17-PARAMETER-MANAGER-SCHEDULER-CLOSURE-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-18-PROVIDER-VTABLE-GET-CLOSURE-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-18-PROVIDER-VTABLE-GET-CLOSURE-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-19-PROVIDER-GET-SET-ADDRESS-BASE-CLOSURE-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-19-PROVIDER-GET-SET-ADDRESS-BASE-CLOSURE-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-20-LOCAL-WRITE-PUBLICATION-CAN-BRIDGE-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-20-LOCAL-WRITE-PUBLICATION-CAN-BRIDGE-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-21-MENU-RAW-MATRIX-RUNTIME-ANCHOR-AUDIT-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-21-MENU-RAW-MATRIX-RUNTIME-ANCHOR-AUDIT-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-22-IAR-DATA-MENU-RUNTIME-TABLE-CLOSURE-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-22-IAR-DATA-MENU-RUNTIME-TABLE-CLOSURE-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-23-POINTER-FLOW-MENU-RUNTIME-MUTATION-AUDIT-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-23-POINTER-FLOW-MENU-RUNTIME-MUTATION-AUDIT-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-24-THUMB2-POINTER-FLOW-CORRECTION-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-24-THUMB2-POINTER-FLOW-CORRECTION-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-25-MENU-ACCESS-ROW-PID117-CLOSURE-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-25-MENU-ACCESS-ROW-PID117-CLOSURE-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-26-PID0117-RESOLVER-NEGATIVE-CLOSURE-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-26-PID0117-RESOLVER-NEGATIVE-CLOSURE-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-27-ROW-F8-DESCRIPTOR-VALUE15-CLOSURE-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-27-ROW-F8-DESCRIPTOR-VALUE15-CLOSURE-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-28-RUNTIME-CLASS-FIRST-LEVEL-UI-DISPATCH-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-28-RUNTIME-CLASS-FIRST-LEVEL-UI-DISPATCH-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-29-RUNTIME-CLASS-CALLBACK-DESCRIPTOR-LAYER-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-29-RUNTIME-CLASS-CALLBACK-DESCRIPTOR-LAYER-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-30-UI-CALLBACK-OBJECT-VTABLE-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-30-UI-CALLBACK-OBJECT-VTABLE-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-31-VTABLE-SLOT2-CALLBACK-BRIDGE-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-31-VTABLE-SLOT2-CALLBACK-BRIDGE-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-32-CLASS12-PARAMETER3-CYCLIC-OPERATION-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-32-CLASS12-PARAMETER3-CYCLIC-OPERATION-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-33-RUNTIME-KEY3-PROVENANCE-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-33-RUNTIME-KEY3-PROVENANCE-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-34-RUNTIME-KEY3-STORAGE-TYPE-CLOSURE-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-34-RUNTIME-KEY3-STORAGE-TYPE-CLOSURE-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-35-RUNTIME-PARAM-TABLE-EMULATION-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-35-RUNTIME-PARAM-TABLE-EMULATION-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-36-PID-MATRIX-ACCESS-CLASS-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-36-PID-MATRIX-ACCESS-CLASS-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-37-CAN-POLLER-AND-RX-BEHAVIOR-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-37-CAN-POLLER-AND-RX-BEHAVIOR-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-38-LOCAL-CHANGE-PUBLICATION-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-38-LOCAL-CHANGE-PUBLICATION-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-39-LANGUAGE-CLASS12-SETLANGUAGE-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-39-LANGUAGE-CLASS12-SETLANGUAGE-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-40-MENU-ROWS-BUILT-IN-FIRMWARE-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-40-MENU-ROWS-BUILT-IN-FIRMWARE-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-41-MENU-CLICK-DISPATCH-EXECUTED-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-41-MENU-CLICK-DISPATCH-EXECUTED-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-42-FULL-SYSTEM-EMULATION-HOME-SCREEN-RENDER-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-42-FULL-SYSTEM-EMULATION-HOME-SCREEN-RENDER-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-43-CAN-BOOT-TRAFFIC-NODE-TABLE-2026-11-23.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-43-CAN-BOOT-TRAFFIC-NODE-TABLE-2026-11-23.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-44-TOUCH-FT5X06-UI-ATLAS-2026-11-23.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-44-TOUCH-FT5X06-UI-ATLAS-2026-11-23.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-45-MENU-CAPABILITY-PIN-CONFIG-SCREEN-2026-11-23.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-45-MENU-CAPABILITY-PIN-CONFIG-SCREEN-2026-11-23.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-46-ACCESS-LEVELS-PANEL-LISTS-2026-11-23.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-46-ACCESS-LEVELS-PANEL-LISTS-2026-11-23.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-47-GATES-BITMAPS-TRACING-2026-11-23.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-47-GATES-BITMAPS-TRACING-2026-11-23.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-48-LEVEL3-GATE-CHILD-2026-11-23.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-48-LEVEL3-GATE-CHILD-2026-11-23.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-49-LEVEL-NONZERO-GATES-2026-11-23.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-49-LEVEL-NONZERO-GATES-2026-11-23.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-50-HOME-POWER-POPUP-2026-11-23.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-50-HOME-POWER-POPUP-2026-11-23.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-51-ALARMS-2026-11-23.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-51-ALARMS-2026-11-23.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-52-HOME-RTC-TOOLS-2026-11-23.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-52-HOME-RTC-TOOLS-2026-11-23.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-53-IGNITION-LOCK-ALARM-INDICATOR-2026-11-23.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-53-IGNITION-LOCK-ALARM-INDICATOR-2026-11-23.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-54-INTERNET-WIFI-CAN-NODES-2026-11-23.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-54-INTERNET-WIFI-CAN-NODES-2026-11-23.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-56-FONTS-2026-11-23.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-56-FONTS-2026-11-23.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-59-UI-MODEL-2026-11-23.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-59-UI-MODEL-2026-11-23.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-60-UI-ACTION-GRAPH-2026-11-23.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-60-UI-ACTION-GRAPH-2026-11-23.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-62-RTC-SYNC-FROM-CAN-EXECUTED-2026-11-23.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-62-RTC-SYNC-FROM-CAN-EXECUTED-2026-11-23.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-63-PID-DIFF-PILOT-KOCIOL-2026-11-23.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-63-PID-DIFF-PILOT-KOCIOL-2026-11-23.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-64-LIVE-SOURCE-CAN-IO-MODULES-2026-11-23.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-64-LIVE-SOURCE-CAN-IO-MODULES-2026-11-23.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-66-RED-BACKGROUND-DMA2D-RESET-2026-11-23.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-66-RED-BACKGROUND-DMA2D-RESET-2026-11-23.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-67-LIVE-SOURCES-CAN-IO-SIMULATOR-2026-11-23.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-67-LIVE-SOURCES-CAN-IO-SIMULATOR-2026-11-23.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PASS-SIEC-CAN-MODULE-DISCOVERY-2026-11-24.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PASS-SIEC-CAN-MODULE-DISCOVERY-2026-11-24.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-PROGRESS-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-PROGRESS-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/AUTONOMOUS-RUNTIME-PACKAGE-ACCEPTANCE-2026-11-24.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/AUTONOMOUS-RUNTIME-PACKAGE-ACCEPTANCE-2026-11-24.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/CAN-WRITE-ATTACK-01-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/CAN-WRITE-ATTACK-01-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/EXTERNAL-AUDIT-ASSESSMENT-2026-11-23.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/EXTERNAL-AUDIT-ASSESSMENT-2026-11-23.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/EXTERNAL-AUDIT-DISCOVERY-FW2213TK-2026-11-23.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/EXTERNAL-AUDIT-DISCOVERY-FW2213TK-2026-11-23.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/INSTANCE-CAPABILITY-GRAPH-ATTACK-01-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/INSTANCE-CAPABILITY-GRAPH-ATTACK-01-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/MENU-TREE-2026-11-23.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/MENU-TREE-2026-11-23.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/MENUTREE-ATTACK-01-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/MENUTREE-ATTACK-01-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/MENUTREE-ATTACK-02-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/MENUTREE-ATTACK-02-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/MENUTREE-ATTACK-03-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/MENUTREE-ATTACK-03-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/MENUTREE-FULL-CLOSURE-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/MENUTREE-FULL-CLOSURE-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/PAGE-WIDGET-FACTORY-RESOURCE-REGISTRY-CLOSURE-01-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/PAGE-WIDGET-FACTORY-RESOURCE-REGISTRY-CLOSURE-01-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/PARAMETER-2C-RUNTIME-TABLE-CLOSURE-01-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/PARAMETER-2C-RUNTIME-TABLE-CLOSURE-01-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/PARAMETER-CAN-GRAPH-ATTACK-01-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/PARAMETER-CAN-GRAPH-ATTACK-01-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/PARAMETER-ENGINE-CROSS-LAYER-CLOSURE-01-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/PARAMETER-ENGINE-CROSS-LAYER-CLOSURE-01-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/PARAMETER-RESPONSE-DISPATCH-100-CLOSURE-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/PARAMETER-RESPONSE-DISPATCH-100-CLOSURE-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/PARAMETER-SIDECAR-SYNC-CLOSURE-05-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/PARAMETER-SIDECAR-SYNC-CLOSURE-05-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/PARAMETER-SYNC-PUBLICATION-CLOSURE-06-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/PARAMETER-SYNC-PUBLICATION-CLOSURE-06-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/RE-HARNESS-PASS-02-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/RE-HARNESS-PASS-02-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/RE-HARNESS-PROGRESS-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/RE-HARNESS-PROGRESS-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/RECORD-DESCRIPTOR-HARD-CLOSURE-03-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/RECORD-DESCRIPTOR-HARD-CLOSURE-03-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/RECORD-ENGINE-CROSS-LAYER-CLOSURE-02-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/RECORD-ENGINE-CROSS-LAYER-CLOSURE-02-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/RECORD-SEMANTIC-CLOSURE-04-2026-11-22.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/RECORD-SEMANTIC-CLOSURE-04-2026-11-22.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/SPEC-POZIOMY-DOSTEPU-0-1-2.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/SPEC-POZIOMY-DOSTEPU-0-1-2.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/WIDGETS-BY-SCREEN-2026-11-23.md;NewEstyma/evidence/reports/FW2213TK-2026-11-22/WIDGETS-BY-SCREEN-2026-11-23.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-22/data/access_gates_scan.csv;NewEstyma/evidence/data/access_gates_scan.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/actions_pass61_L0_partial.json;NewEstyma/evidence/data/actions_pass61_L0_partial.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/actions_pass65_L0_nodes6-11.json;NewEstyma/evidence/data/actions_pass65_L0_nodes6-11.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/actions_pass65_L1_nodes12-18.json;NewEstyma/evidence/data/actions_pass65_L1_nodes12-18.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/actions_pass65_cfg_kaskada_magazyn.json;NewEstyma/evidence/data/actions_pass65_cfg_kaskada_magazyn.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/actions_pass65_home.json;NewEstyma/evidence/data/actions_pass65_home.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/alarm_codes_texts.csv;NewEstyma/evidence/data/alarm_codes_texts.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/alarm_raise_clear_sites.csv;NewEstyma/evidence/data/alarm_raise_clear_sites.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/atlas/dialog_paliwo.png;NewEstyma/evidence/data/atlas/dialog_paliwo.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/atlas/dialog_pin.png;NewEstyma/evidence/data/atlas/dialog_pin.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/atlas/dialog_ustaw_czas.png;NewEstyma/evidence/data/atlas/dialog_ustaw_czas.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/atlas/historia_alarmow.png;NewEstyma/evidence/data/atlas/historia_alarmow.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/atlas/home.png;NewEstyma/evidence/data/atlas/home.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/atlas/home_po_pin_6154_z_konfiguracja.png;NewEstyma/evidence/data/atlas/home_po_pin_6154_z_konfiguracja.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/atlas/home_z_konfiguracja.png;NewEstyma/evidence/data/atlas/home_z_konfiguracja.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/atlas/kociol.png;NewEstyma/evidence/data/atlas/kociol.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/atlas/konfiguracja.png;NewEstyma/evidence/data/atlas/konfiguracja.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/atlas/konfiguracja_przewiniete.png;NewEstyma/evidence/data/atlas/konfiguracja_przewiniete.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/atlas/menu_pelna_konfiguracja_gora.png;NewEstyma/evidence/data/atlas/menu_pelna_konfiguracja_gora.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/atlas/menu_pelna_konfiguracja_srodek.png;NewEstyma/evidence/data/atlas/menu_pelna_konfiguracja_srodek.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/atlas/menu_scrolled.png;NewEstyma/evidence/data/atlas/menu_scrolled.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/atlas/menu_top.png;NewEstyma/evidence/data/atlas/menu_top.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/atlas/ogrzewanie_1.png;NewEstyma/evidence/data/atlas/ogrzewanie_1.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/atlas/palnik.png;NewEstyma/evidence/data/atlas/palnik.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps.zip;NewEstyma/evidence/data/bitmaps.zip;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/manifest.csv;NewEstyma/evidence/data/bitmaps/manifest.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/000.png;NewEstyma/evidence/data/bitmaps/png/000.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/001.png;NewEstyma/evidence/data/bitmaps/png/001.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/002.png;NewEstyma/evidence/data/bitmaps/png/002.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/003.png;NewEstyma/evidence/data/bitmaps/png/003.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/004.png;NewEstyma/evidence/data/bitmaps/png/004.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/005.png;NewEstyma/evidence/data/bitmaps/png/005.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/006.png;NewEstyma/evidence/data/bitmaps/png/006.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/007.png;NewEstyma/evidence/data/bitmaps/png/007.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/008.png;NewEstyma/evidence/data/bitmaps/png/008.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/009.png;NewEstyma/evidence/data/bitmaps/png/009.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/010.png;NewEstyma/evidence/data/bitmaps/png/010.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/011.png;NewEstyma/evidence/data/bitmaps/png/011.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/012.png;NewEstyma/evidence/data/bitmaps/png/012.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/013.png;NewEstyma/evidence/data/bitmaps/png/013.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/014.png;NewEstyma/evidence/data/bitmaps/png/014.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/015.png;NewEstyma/evidence/data/bitmaps/png/015.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/016.png;NewEstyma/evidence/data/bitmaps/png/016.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/017.png;NewEstyma/evidence/data/bitmaps/png/017.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/018.png;NewEstyma/evidence/data/bitmaps/png/018.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/019.png;NewEstyma/evidence/data/bitmaps/png/019.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/020.png;NewEstyma/evidence/data/bitmaps/png/020.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/021.png;NewEstyma/evidence/data/bitmaps/png/021.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/022.png;NewEstyma/evidence/data/bitmaps/png/022.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/023.png;NewEstyma/evidence/data/bitmaps/png/023.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/024.png;NewEstyma/evidence/data/bitmaps/png/024.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/025.png;NewEstyma/evidence/data/bitmaps/png/025.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/026.png;NewEstyma/evidence/data/bitmaps/png/026.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/027.png;NewEstyma/evidence/data/bitmaps/png/027.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/028.png;NewEstyma/evidence/data/bitmaps/png/028.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/029.png;NewEstyma/evidence/data/bitmaps/png/029.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/030.png;NewEstyma/evidence/data/bitmaps/png/030.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/031.png;NewEstyma/evidence/data/bitmaps/png/031.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/032.png;NewEstyma/evidence/data/bitmaps/png/032.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/033.png;NewEstyma/evidence/data/bitmaps/png/033.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/034.png;NewEstyma/evidence/data/bitmaps/png/034.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/035.png;NewEstyma/evidence/data/bitmaps/png/035.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/036.png;NewEstyma/evidence/data/bitmaps/png/036.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/037.png;NewEstyma/evidence/data/bitmaps/png/037.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/038.png;NewEstyma/evidence/data/bitmaps/png/038.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/039.png;NewEstyma/evidence/data/bitmaps/png/039.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/040.png;NewEstyma/evidence/data/bitmaps/png/040.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/041.png;NewEstyma/evidence/data/bitmaps/png/041.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/042.png;NewEstyma/evidence/data/bitmaps/png/042.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/043.png;NewEstyma/evidence/data/bitmaps/png/043.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/044.png;NewEstyma/evidence/data/bitmaps/png/044.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/045.png;NewEstyma/evidence/data/bitmaps/png/045.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/046.png;NewEstyma/evidence/data/bitmaps/png/046.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/047.png;NewEstyma/evidence/data/bitmaps/png/047.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/048.png;NewEstyma/evidence/data/bitmaps/png/048.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/049.png;NewEstyma/evidence/data/bitmaps/png/049.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/050.png;NewEstyma/evidence/data/bitmaps/png/050.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/051.png;NewEstyma/evidence/data/bitmaps/png/051.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/052.png;NewEstyma/evidence/data/bitmaps/png/052.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/053.png;NewEstyma/evidence/data/bitmaps/png/053.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/054.png;NewEstyma/evidence/data/bitmaps/png/054.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/055.png;NewEstyma/evidence/data/bitmaps/png/055.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/056.png;NewEstyma/evidence/data/bitmaps/png/056.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/057.png;NewEstyma/evidence/data/bitmaps/png/057.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/058.png;NewEstyma/evidence/data/bitmaps/png/058.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/059.png;NewEstyma/evidence/data/bitmaps/png/059.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/060.png;NewEstyma/evidence/data/bitmaps/png/060.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/061.png;NewEstyma/evidence/data/bitmaps/png/061.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/062.png;NewEstyma/evidence/data/bitmaps/png/062.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/063.png;NewEstyma/evidence/data/bitmaps/png/063.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/064.png;NewEstyma/evidence/data/bitmaps/png/064.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/065.png;NewEstyma/evidence/data/bitmaps/png/065.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/066.png;NewEstyma/evidence/data/bitmaps/png/066.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/067.png;NewEstyma/evidence/data/bitmaps/png/067.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/068.png;NewEstyma/evidence/data/bitmaps/png/068.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/069.png;NewEstyma/evidence/data/bitmaps/png/069.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/070.png;NewEstyma/evidence/data/bitmaps/png/070.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/071.png;NewEstyma/evidence/data/bitmaps/png/071.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/072.png;NewEstyma/evidence/data/bitmaps/png/072.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/073.png;NewEstyma/evidence/data/bitmaps/png/073.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/074.png;NewEstyma/evidence/data/bitmaps/png/074.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/075.png;NewEstyma/evidence/data/bitmaps/png/075.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/076.png;NewEstyma/evidence/data/bitmaps/png/076.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/077.png;NewEstyma/evidence/data/bitmaps/png/077.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/078.png;NewEstyma/evidence/data/bitmaps/png/078.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/079.png;NewEstyma/evidence/data/bitmaps/png/079.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/080.png;NewEstyma/evidence/data/bitmaps/png/080.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/081.png;NewEstyma/evidence/data/bitmaps/png/081.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/082.png;NewEstyma/evidence/data/bitmaps/png/082.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/083.png;NewEstyma/evidence/data/bitmaps/png/083.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/084.png;NewEstyma/evidence/data/bitmaps/png/084.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/085.png;NewEstyma/evidence/data/bitmaps/png/085.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/086.png;NewEstyma/evidence/data/bitmaps/png/086.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/087.png;NewEstyma/evidence/data/bitmaps/png/087.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/088.png;NewEstyma/evidence/data/bitmaps/png/088.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/089.png;NewEstyma/evidence/data/bitmaps/png/089.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/090.png;NewEstyma/evidence/data/bitmaps/png/090.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/091.png;NewEstyma/evidence/data/bitmaps/png/091.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/092.png;NewEstyma/evidence/data/bitmaps/png/092.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/093.png;NewEstyma/evidence/data/bitmaps/png/093.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/094.png;NewEstyma/evidence/data/bitmaps/png/094.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/095.png;NewEstyma/evidence/data/bitmaps/png/095.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/096.png;NewEstyma/evidence/data/bitmaps/png/096.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/097.png;NewEstyma/evidence/data/bitmaps/png/097.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/098.png;NewEstyma/evidence/data/bitmaps/png/098.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/099.png;NewEstyma/evidence/data/bitmaps/png/099.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/100.png;NewEstyma/evidence/data/bitmaps/png/100.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/101.png;NewEstyma/evidence/data/bitmaps/png/101.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/102.png;NewEstyma/evidence/data/bitmaps/png/102.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/103.png;NewEstyma/evidence/data/bitmaps/png/103.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/104.png;NewEstyma/evidence/data/bitmaps/png/104.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/105.png;NewEstyma/evidence/data/bitmaps/png/105.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/106.png;NewEstyma/evidence/data/bitmaps/png/106.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/107.png;NewEstyma/evidence/data/bitmaps/png/107.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/108.png;NewEstyma/evidence/data/bitmaps/png/108.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/109.png;NewEstyma/evidence/data/bitmaps/png/109.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/110.png;NewEstyma/evidence/data/bitmaps/png/110.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/111.png;NewEstyma/evidence/data/bitmaps/png/111.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/112.png;NewEstyma/evidence/data/bitmaps/png/112.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/113.png;NewEstyma/evidence/data/bitmaps/png/113.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/114.png;NewEstyma/evidence/data/bitmaps/png/114.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/115.png;NewEstyma/evidence/data/bitmaps/png/115.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/116.png;NewEstyma/evidence/data/bitmaps/png/116.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/117.png;NewEstyma/evidence/data/bitmaps/png/117.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/118.png;NewEstyma/evidence/data/bitmaps/png/118.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/119.png;NewEstyma/evidence/data/bitmaps/png/119.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/120.png;NewEstyma/evidence/data/bitmaps/png/120.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/121.png;NewEstyma/evidence/data/bitmaps/png/121.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/122.png;NewEstyma/evidence/data/bitmaps/png/122.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/123.png;NewEstyma/evidence/data/bitmaps/png/123.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/124.png;NewEstyma/evidence/data/bitmaps/png/124.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/125.png;NewEstyma/evidence/data/bitmaps/png/125.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/126.png;NewEstyma/evidence/data/bitmaps/png/126.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/127.png;NewEstyma/evidence/data/bitmaps/png/127.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/128.png;NewEstyma/evidence/data/bitmaps/png/128.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/129.png;NewEstyma/evidence/data/bitmaps/png/129.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/130.png;NewEstyma/evidence/data/bitmaps/png/130.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/131.png;NewEstyma/evidence/data/bitmaps/png/131.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/132.png;NewEstyma/evidence/data/bitmaps/png/132.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/133.png;NewEstyma/evidence/data/bitmaps/png/133.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/134.png;NewEstyma/evidence/data/bitmaps/png/134.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/135.png;NewEstyma/evidence/data/bitmaps/png/135.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/136.png;NewEstyma/evidence/data/bitmaps/png/136.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/137.png;NewEstyma/evidence/data/bitmaps/png/137.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/138.png;NewEstyma/evidence/data/bitmaps/png/138.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/139.png;NewEstyma/evidence/data/bitmaps/png/139.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/140.png;NewEstyma/evidence/data/bitmaps/png/140.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/141.png;NewEstyma/evidence/data/bitmaps/png/141.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/142.png;NewEstyma/evidence/data/bitmaps/png/142.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/143.png;NewEstyma/evidence/data/bitmaps/png/143.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/144.png;NewEstyma/evidence/data/bitmaps/png/144.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/145.png;NewEstyma/evidence/data/bitmaps/png/145.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/146.png;NewEstyma/evidence/data/bitmaps/png/146.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/147.png;NewEstyma/evidence/data/bitmaps/png/147.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/148.png;NewEstyma/evidence/data/bitmaps/png/148.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/149.png;NewEstyma/evidence/data/bitmaps/png/149.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/150.png;NewEstyma/evidence/data/bitmaps/png/150.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/151.png;NewEstyma/evidence/data/bitmaps/png/151.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/152.png;NewEstyma/evidence/data/bitmaps/png/152.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/153.png;NewEstyma/evidence/data/bitmaps/png/153.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/154.png;NewEstyma/evidence/data/bitmaps/png/154.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/155.png;NewEstyma/evidence/data/bitmaps/png/155.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/156.png;NewEstyma/evidence/data/bitmaps/png/156.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/157.png;NewEstyma/evidence/data/bitmaps/png/157.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/158.png;NewEstyma/evidence/data/bitmaps/png/158.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/159.png;NewEstyma/evidence/data/bitmaps/png/159.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/160.png;NewEstyma/evidence/data/bitmaps/png/160.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/161.png;NewEstyma/evidence/data/bitmaps/png/161.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/162.png;NewEstyma/evidence/data/bitmaps/png/162.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/163.png;NewEstyma/evidence/data/bitmaps/png/163.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/164.png;NewEstyma/evidence/data/bitmaps/png/164.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/165.png;NewEstyma/evidence/data/bitmaps/png/165.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/166.png;NewEstyma/evidence/data/bitmaps/png/166.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/167.png;NewEstyma/evidence/data/bitmaps/png/167.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/168.png;NewEstyma/evidence/data/bitmaps/png/168.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/169.png;NewEstyma/evidence/data/bitmaps/png/169.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/170.png;NewEstyma/evidence/data/bitmaps/png/170.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/171.png;NewEstyma/evidence/data/bitmaps/png/171.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/172.png;NewEstyma/evidence/data/bitmaps/png/172.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/173.png;NewEstyma/evidence/data/bitmaps/png/173.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/174.png;NewEstyma/evidence/data/bitmaps/png/174.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/175.png;NewEstyma/evidence/data/bitmaps/png/175.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/176.png;NewEstyma/evidence/data/bitmaps/png/176.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/177.png;NewEstyma/evidence/data/bitmaps/png/177.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/178.png;NewEstyma/evidence/data/bitmaps/png/178.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/179.png;NewEstyma/evidence/data/bitmaps/png/179.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/180.png;NewEstyma/evidence/data/bitmaps/png/180.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/181.png;NewEstyma/evidence/data/bitmaps/png/181.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/182.png;NewEstyma/evidence/data/bitmaps/png/182.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/183.png;NewEstyma/evidence/data/bitmaps/png/183.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/184.png;NewEstyma/evidence/data/bitmaps/png/184.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/185.png;NewEstyma/evidence/data/bitmaps/png/185.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/186.png;NewEstyma/evidence/data/bitmaps/png/186.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/png/187.png;NewEstyma/evidence/data/bitmaps/png/187.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/sheet_000_063.png;NewEstyma/evidence/data/bitmaps/sheet_000_063.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/sheet_064_127.png;NewEstyma/evidence/data/bitmaps/sheet_064_127.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/bitmaps/sheet_128_187.png;NewEstyma/evidence/data/bitmaps/sheet_128_187.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/can_node_names.csv;NewEstyma/evidence/data/can_node_names.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/can_tx_boot_no_partners.csv;NewEstyma/evidence/data/can_tx_boot_no_partners.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/fonts/font0_h12/atlas.png;NewEstyma/evidence/data/fonts/font0_h12/atlas.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/fonts/font0_h12/glyph_data_4bpp.bin;NewEstyma/evidence/data/fonts/font0_h12/glyph_data_4bpp.bin;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/fonts/font0_h12/glyphs.csv;NewEstyma/evidence/data/fonts/font0_h12/glyphs.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/fonts/font1_h20/atlas.png;NewEstyma/evidence/data/fonts/font1_h20/atlas.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/fonts/font1_h20/glyph_data_4bpp.bin;NewEstyma/evidence/data/fonts/font1_h20/glyph_data_4bpp.bin;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/fonts/font1_h20/glyphs.csv;NewEstyma/evidence/data/fonts/font1_h20/glyphs.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/fonts/font2_h26/atlas.png;NewEstyma/evidence/data/fonts/font2_h26/atlas.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/fonts/font2_h26/glyph_data_4bpp.bin;NewEstyma/evidence/data/fonts/font2_h26/glyph_data_4bpp.bin;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/fonts/font2_h26/glyphs.csv;NewEstyma/evidence/data/fonts/font2_h26/glyphs.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/fonts/font3_h36/atlas.png;NewEstyma/evidence/data/fonts/font3_h36/atlas.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/fonts/font3_h36/glyph_data_4bpp.bin;NewEstyma/evidence/data/fonts/font3_h36/glyph_data_4bpp.bin;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/fonts/font3_h36/glyphs.csv;NewEstyma/evidence/data/fonts/font3_h36/glyphs.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/fonts/font4_h64/atlas.png;NewEstyma/evidence/data/fonts/font4_h64/atlas.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/fonts/font4_h64/glyph_data_4bpp.bin;NewEstyma/evidence/data/fonts/font4_h64/glyph_data_4bpp.bin;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/fonts/font4_h64/glyphs.csv;NewEstyma/evidence/data/fonts/font4_h64/glyphs.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/fonts/font5_h92/atlas.png;NewEstyma/evidence/data/fonts/font5_h92/atlas.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/fonts/font5_h92/glyph_data_4bpp.bin;NewEstyma/evidence/data/fonts/font5_h92/glyph_data_4bpp.bin;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/fonts/font5_h92/glyphs.csv;NewEstyma/evidence/data/fonts/font5_h92/glyphs.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/fonts/fonts_meta.json;NewEstyma/evidence/data/fonts/fonts_meta.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/fonts_glyph_pngs.zip;NewEstyma/evidence/data/fonts_glyph_pngs.zip;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/function_coverage.csv;NewEstyma/evidence/data/function_coverage.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/function_coverage_static.csv;NewEstyma/evidence/data/function_coverage_static.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/function_coverage_triage.csv;NewEstyma/evidence/data/function_coverage_triage.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/home_data_binding.csv;NewEstyma/evidence/data/home_data_binding.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/home_presenter_keys.txt;NewEstyma/evidence/data/home_presenter_keys.txt;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/kaskada_presenter_keys.txt;NewEstyma/evidence/data/kaskada_presenter_keys.txt;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/level3_gate_wrappers_17.csv;NewEstyma/evidence/data/level3_gate_wrappers_17.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/levels_0_1_2_spec.csv;NewEstyma/evidence/data/levels_0_1_2_spec.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/menu_click_effects_21.csv;NewEstyma/evidence/data/menu_click_effects_21.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/menu_rows_21.csv;NewEstyma/evidence/data/menu_rows_21.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/menu_rows_pass61_L0.txt;NewEstyma/evidence/data/menu_rows_pass61_L0.txt;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/menu_rows_pass61_L2.txt;NewEstyma/evidence/data/menu_rows_pass61_L2.txt;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/panel_lists_by_level.csv;NewEstyma/evidence/data/panel_lists_by_level.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/panel_lists_by_level.md;NewEstyma/evidence/data/panel_lists_by_level.md;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/BINDINGS_L0_cascade_fuelstore.csv;NewEstyma/evidence/data/pass63_pilot_kociol/BINDINGS_L0_cascade_fuelstore.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/BINDINGS_L0_cascade_fuelstore.md;NewEstyma/evidence/data/pass63_pilot_kociol/BINDINGS_L0_cascade_fuelstore.md;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/BINDINGS_L0_pilot.csv;NewEstyma/evidence/data/pass63_pilot_kociol/BINDINGS_L0_pilot.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/BINDINGS_L0_pilot.md;NewEstyma/evidence/data/pass63_pilot_kociol/BINDINGS_L0_pilot.md;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/BINDINGS_L0_test5.csv;NewEstyma/evidence/data/pass63_pilot_kociol/BINDINGS_L0_test5.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/BINDINGS_L0_test5.md;NewEstyma/evidence/data/pass63_pilot_kociol/BINDINGS_L0_test5.md;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/BINDINGS_L1_test_wyjsc_internet.csv;NewEstyma/evidence/data/pass63_pilot_kociol/BINDINGS_L1_test_wyjsc_internet.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/BINDINGS_L1_test_wyjsc_internet.md;NewEstyma/evidence/data/pass63_pilot_kociol/BINDINGS_L1_test_wyjsc_internet.md;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/BINDINGS_LIVE_L0.csv;NewEstyma/evidence/data/pass63_pilot_kociol/BINDINGS_LIVE_L0.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/BINDINGS_LIVE_L0.md;NewEstyma/evidence/data/pass63_pilot_kociol/BINDINGS_LIVE_L0.md;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/cands.json;NewEstyma/evidence/data/pass63_pilot_kociol/cands.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/live_diff_0.json;NewEstyma/evidence/data/pass63_pilot_kociol/live_diff_0.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/live_diff_6.json;NewEstyma/evidence/data/pass63_pilot_kociol/live_diff_6.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/live_diff_7.json;NewEstyma/evidence/data/pass63_pilot_kociol/live_diff_7.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/live_diff_8.json;NewEstyma/evidence/data/pass63_pilot_kociol/live_diff_8.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/live_diff_h.json;NewEstyma/evidence/data/pass63_pilot_kociol/live_diff_h.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/pid_diff_1_screen.json;NewEstyma/evidence/data/pass63_pilot_kociol/pid_diff_1_screen.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/pid_diff_2_screen.json;NewEstyma/evidence/data/pass63_pilot_kociol/pid_diff_2_screen.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/pid_diff_2_screen_22A1_2301.json;NewEstyma/evidence/data/pass63_pilot_kociol/pid_diff_2_screen_22A1_2301.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/pid_diff_3_screen.json;NewEstyma/evidence/data/pass63_pilot_kociol/pid_diff_3_screen.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/pid_diff_6_screen.json;NewEstyma/evidence/data/pass63_pilot_kociol/pid_diff_6_screen.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/pid_diff_7_screen.json;NewEstyma/evidence/data/pass63_pilot_kociol/pid_diff_7_screen.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/pid_diff_8_screen.json;NewEstyma/evidence/data/pass63_pilot_kociol/pid_diff_8_screen.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/pid_diff_HOME.json;NewEstyma/evidence/data/pass63_pilot_kociol/pid_diff_HOME.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/pid_diff_INTERNET_L1.json;NewEstyma/evidence/data/pass63_pilot_kociol/pid_diff_INTERNET_L1.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/pid_diff_KASKADA.json;NewEstyma/evidence/data/pass63_pilot_kociol/pid_diff_KASKADA.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/pid_diff_MAGAZYN.json;NewEstyma/evidence/data/pass63_pilot_kociol/pid_diff_MAGAZYN.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/pid_diff_TEST_WYJSC_L1.json;NewEstyma/evidence/data/pass63_pilot_kociol/pid_diff_TEST_WYJSC_L1.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/pid_diff_kociol.json;NewEstyma/evidence/data/pass63_pilot_kociol/pid_diff_kociol.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/sheet_0x2002.png;NewEstyma/evidence/data/pass63_pilot_kociol/sheet_0x2002.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/sheet_0x2005.png;NewEstyma/evidence/data/pass63_pilot_kociol/sheet_0x2005.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/sheet_0x216F.png;NewEstyma/evidence/data/pass63_pilot_kociol/sheet_0x216F.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/sheet_0x350A.png;NewEstyma/evidence/data/pass63_pilot_kociol/sheet_0x350A.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/sheet_0x350D.png;NewEstyma/evidence/data/pass63_pilot_kociol/sheet_0x350D.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/sheet_0x3629.png;NewEstyma/evidence/data/pass63_pilot_kociol/sheet_0x3629.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_pilot_kociol/sheet_0x370A.png;NewEstyma/evidence/data/pass63_pilot_kociol/sheet_0x370A.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass63_view_classes.json;NewEstyma/evidence/data/pass63_view_classes.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pass64_live/modmap_default_config.json;NewEstyma/evidence/data/pass64_live/modmap_default_config.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/pid_matrix_655.csv;NewEstyma/evidence/data/pid_matrix_655.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/poll_sequence_655.csv;NewEstyma/evidence/data/poll_sequence_655.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/presenter_map.csv;NewEstyma/evidence/data/presenter_map.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/ram_clusters.csv;NewEstyma/evidence/data/ram_clusters.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/raw_listings/listing_08048468.txt;NewEstyma/evidence/data/raw_listings/listing_08048468.txt;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/raw_listings/listing_0804858a.txt;NewEstyma/evidence/data/raw_listings/listing_0804858a.txt;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/raw_listings/listing_08054848.txt;NewEstyma/evidence/data/raw_listings/listing_08054848.txt;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/raw_listings/listing_08054ab8.txt;NewEstyma/evidence/data/raw_listings/listing_08054ab8.txt;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/raw_listings/listing_08056028.txt;NewEstyma/evidence/data/raw_listings/listing_08056028.txt;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/raw_listings/listing_08056040.txt;NewEstyma/evidence/data/raw_listings/listing_08056040.txt;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/raw_listings/listing_08056a1c.txt;NewEstyma/evidence/data/raw_listings/listing_08056a1c.txt;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/raw_listings/listing_08056a44.txt;NewEstyma/evidence/data/raw_listings/listing_08056a44.txt;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/resolver_t1.csv;NewEstyma/evidence/data/resolver_t1.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/resolver_t2.csv;NewEstyma/evidence/data/resolver_t2.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/rtc_timestamp_probe.json;NewEstyma/evidence/data/rtc_timestamp_probe.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/runtime_param_table_655.csv;NewEstyma/evidence/data/runtime_param_table_655.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/screen_home_emulated.png;NewEstyma/evidence/data/screen_home_emulated.png;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/settings_labels/L2_row0.json;NewEstyma/evidence/data/settings_labels/L2_row0.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/settings_labels/L2_row1.json;NewEstyma/evidence/data/settings_labels/L2_row1.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/settings_labels/L2_row2.json;NewEstyma/evidence/data/settings_labels/L2_row2.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/settings_labels/L2_row6.json;NewEstyma/evidence/data/settings_labels/L2_row6.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/texts_all_languages.csv;NewEstyma/evidence/data/texts_all_languages.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/typedtext_database.csv;NewEstyma/evidence/data/typedtext_database.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_key_usage.csv;NewEstyma/evidence/data/ui_key_usage.csv;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/INDEX.json;NewEstyma/ui_model/INDEX.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/README.md;NewEstyma/ui_model/README.md;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/alarms.json;NewEstyma/ui_model/alarms.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/H_home.png;NewEstyma/ui_model/atlas/H_home.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L0_0_screen.png;NewEstyma/ui_model/atlas/L0_0_screen.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L0_0_settings.png;NewEstyma/ui_model/atlas/L0_0_settings.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L0_10_screen.png;NewEstyma/ui_model/atlas/L0_10_screen.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L0_10_settings.png;NewEstyma/ui_model/atlas/L0_10_settings.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L0_11_screen.png;NewEstyma/ui_model/atlas/L0_11_screen.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L0_11_settings.png;NewEstyma/ui_model/atlas/L0_11_settings.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L0_1_screen.png;NewEstyma/ui_model/atlas/L0_1_screen.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L0_1_settings.png;NewEstyma/ui_model/atlas/L0_1_settings.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L0_2_screen.png;NewEstyma/ui_model/atlas/L0_2_screen.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L0_2_settings.png;NewEstyma/ui_model/atlas/L0_2_settings.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L0_3_screen.png;NewEstyma/ui_model/atlas/L0_3_screen.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L0_3_settings.png;NewEstyma/ui_model/atlas/L0_3_settings.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L0_4_screen.png;NewEstyma/ui_model/atlas/L0_4_screen.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L0_4_settings.png;NewEstyma/ui_model/atlas/L0_4_settings.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L0_5_screen.png;NewEstyma/ui_model/atlas/L0_5_screen.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L0_5_settings.png;NewEstyma/ui_model/atlas/L0_5_settings.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L0_6_screen.png;NewEstyma/ui_model/atlas/L0_6_screen.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L0_6_settings.png;NewEstyma/ui_model/atlas/L0_6_settings.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L0_7_screen.png;NewEstyma/ui_model/atlas/L0_7_screen.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L0_7_settings.png;NewEstyma/ui_model/atlas/L0_7_settings.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L0_8_screen.png;NewEstyma/ui_model/atlas/L0_8_screen.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L0_8_settings.png;NewEstyma/ui_model/atlas/L0_8_settings.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L0_9_screen.png;NewEstyma/ui_model/atlas/L0_9_screen.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L0_9_settings.png;NewEstyma/ui_model/atlas/L0_9_settings.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L1_12_screen.png;NewEstyma/ui_model/atlas/L1_12_screen.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L1_13_screen.png;NewEstyma/ui_model/atlas/L1_13_screen.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L1_14_screen.png;NewEstyma/ui_model/atlas/L1_14_screen.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L1_15_screen.png;NewEstyma/ui_model/atlas/L1_15_screen.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L1_15_settings.png;NewEstyma/ui_model/atlas/L1_15_settings.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L1_16_screen.png;NewEstyma/ui_model/atlas/L1_16_screen.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L1_16_settings.png;NewEstyma/ui_model/atlas/L1_16_settings.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L1_17_screen.png;NewEstyma/ui_model/atlas/L1_17_screen.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/L1_18_screen.png;NewEstyma/ui_model/atlas/L1_18_screen.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/LC_10_screen.png;NewEstyma/ui_model/atlas/LC_10_screen.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/LC_10_settings.png;NewEstyma/ui_model/atlas/LC_10_settings.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/LC_9_screen.png;NewEstyma/ui_model/atlas/LC_9_screen.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/LC_9_settings.png;NewEstyma/ui_model/atlas/LC_9_settings.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/auto.png;NewEstyma/ui_model/atlas/auto.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/czas.png;NewEstyma/ui_model/atlas/czas.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/data.png;NewEstyma/ui_model/atlas/data.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/paliwo.png;NewEstyma/ui_model/atlas/paliwo.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/prog_co1.png;NewEstyma/ui_model/atlas/prog_co1.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/prog_cwu.png;NewEstyma/ui_model/atlas/prog_cwu.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/prog_kociol.png;NewEstyma/ui_model/atlas/prog_kociol.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/atlas/zasilanie.png;NewEstyma/ui_model/atlas/zasilanie.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/audit_siec/siec_cases_montage.png;NewEstyma/ui_model/audit_siec/siec_cases_montage.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/dialog_shots/alarmy_arrows_states.png;NewEstyma/ui_model/dialog_shots/alarmy_arrows_states.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/dialog_shots/alarmy_nav_ack_L1.png;NewEstyma/ui_model/dialog_shots/alarmy_nav_ack_L1.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/dialog_shots/alarmy_nieaktywny_potwierdz.png;NewEstyma/ui_model/dialog_shots/alarmy_nieaktywny_potwierdz.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/dialog_shots/alarmy_screen.png;NewEstyma/ui_model/dialog_shots/alarmy_screen.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/dialog_shots/edit_enum_pin_menu_sheet.png;NewEstyma/ui_model/dialog_shots/edit_enum_pin_menu_sheet.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/dialog_shots/edit_number_enum_sheet.png;NewEstyma/ui_model/dialog_shots/edit_number_enum_sheet.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/dialog_shots/home_control.png;NewEstyma/ui_model/dialog_shots/home_control.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/dialog_shots/home_dialogs_sequences.png;NewEstyma/ui_model/dialog_shots/home_dialogs_sequences.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/dialog_shots/home_dlg_auto.png;NewEstyma/ui_model/dialog_shots/home_dlg_auto.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/dialog_shots/home_dlg_czas.png;NewEstyma/ui_model/dialog_shots/home_dlg_czas.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/dialog_shots/home_dlg_data.png;NewEstyma/ui_model/dialog_shots/home_dlg_data.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/dialog_shots/home_dlg_paliwo.png;NewEstyma/ui_model/dialog_shots/home_dlg_paliwo.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/dialog_shots/home_dlg_zasilanie.png;NewEstyma/ui_model/dialog_shots/home_dlg_zasilanie.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/dialog_shots/list_enum_text_dialogs_sheet.png;NewEstyma/ui_model/dialog_shots/list_enum_text_dialogs_sheet.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/dialog_shots/list_number_dialogs_sheet.png;NewEstyma/ui_model/dialog_shots/list_number_dialogs_sheet.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/dialog_shots/list_row_kinds_sheet.png;NewEstyma/ui_model/dialog_shots/list_row_kinds_sheet.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/dialog_shots/pin_6154_entered.png;NewEstyma/ui_model/dialog_shots/pin_6154_entered.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/dialog_shots/pin_dialog_sheet.png;NewEstyma/ui_model/dialog_shots/pin_dialog_sheet.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/dialog_shots/program_day_dialog.png;NewEstyma/ui_model/dialog_shots/program_day_dialog.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/dialog_shots/program_edit_sequence_sheet.png;NewEstyma/ui_model/dialog_shots/program_edit_sequence_sheet.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/dialog_shots/program_list.png;NewEstyma/ui_model/dialog_shots/program_list.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/dialog_shots/program_scroll_and_copy_sheet.png;NewEstyma/ui_model/dialog_shots/program_scroll_and_copy_sheet.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/dialogs_edit_pin.json;NewEstyma/ui_model/dialogs_edit_pin.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/H_home.json;NewEstyma/ui_model/extras/H_home.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L0_0_screen.json;NewEstyma/ui_model/extras/L0_0_screen.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L0_0_settings.json;NewEstyma/ui_model/extras/L0_0_settings.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L0_10_screen.json;NewEstyma/ui_model/extras/L0_10_screen.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L0_10_settings.json;NewEstyma/ui_model/extras/L0_10_settings.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L0_11_screen.json;NewEstyma/ui_model/extras/L0_11_screen.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L0_11_settings.json;NewEstyma/ui_model/extras/L0_11_settings.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L0_1_screen.json;NewEstyma/ui_model/extras/L0_1_screen.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L0_1_settings.json;NewEstyma/ui_model/extras/L0_1_settings.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L0_2_screen.json;NewEstyma/ui_model/extras/L0_2_screen.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L0_2_settings.json;NewEstyma/ui_model/extras/L0_2_settings.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L0_3_screen.json;NewEstyma/ui_model/extras/L0_3_screen.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L0_3_settings.json;NewEstyma/ui_model/extras/L0_3_settings.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L0_4_screen.json;NewEstyma/ui_model/extras/L0_4_screen.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L0_4_settings.json;NewEstyma/ui_model/extras/L0_4_settings.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L0_5_screen.json;NewEstyma/ui_model/extras/L0_5_screen.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L0_5_settings.json;NewEstyma/ui_model/extras/L0_5_settings.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L0_6_screen.json;NewEstyma/ui_model/extras/L0_6_screen.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L0_6_settings.json;NewEstyma/ui_model/extras/L0_6_settings.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L0_7_screen.json;NewEstyma/ui_model/extras/L0_7_screen.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L0_7_settings.json;NewEstyma/ui_model/extras/L0_7_settings.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L0_8_screen.json;NewEstyma/ui_model/extras/L0_8_screen.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L0_8_settings.json;NewEstyma/ui_model/extras/L0_8_settings.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L0_9_screen.json;NewEstyma/ui_model/extras/L0_9_screen.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L0_9_settings.json;NewEstyma/ui_model/extras/L0_9_settings.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L1_12_screen.json;NewEstyma/ui_model/extras/L1_12_screen.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L1_13_screen.json;NewEstyma/ui_model/extras/L1_13_screen.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L1_14_screen.json;NewEstyma/ui_model/extras/L1_14_screen.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L1_15_screen.json;NewEstyma/ui_model/extras/L1_15_screen.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L1_15_settings.json;NewEstyma/ui_model/extras/L1_15_settings.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L1_16_screen.json;NewEstyma/ui_model/extras/L1_16_screen.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L1_16_settings.json;NewEstyma/ui_model/extras/L1_16_settings.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L1_17_screen.json;NewEstyma/ui_model/extras/L1_17_screen.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/L1_18_screen.json;NewEstyma/ui_model/extras/L1_18_screen.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/LC_10_screen.json;NewEstyma/ui_model/extras/LC_10_screen.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/LC_10_settings.json;NewEstyma/ui_model/extras/LC_10_settings.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/LC_9_screen.json;NewEstyma/ui_model/extras/LC_9_screen.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/extras/LC_9_settings.json;NewEstyma/ui_model/extras/LC_9_settings.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/home_dialogs.json;NewEstyma/ui_model/home_dialogs.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/home_dialogs_widgets.json;NewEstyma/ui_model/home_dialogs_widgets.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/home_overlays_changed.json;NewEstyma/ui_model/home_overlays_changed.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/internet_editor.json;NewEstyma/ui_model/internet_editor.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/levels_widget_deltas.csv;NewEstyma/ui_model/levels_widget_deltas.csv;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/list_scales.json;NewEstyma/ui_model/list_scales.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/lists.json;NewEstyma/ui_model/lists.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/live_sources.json;NewEstyma/ui_model/live_sources.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/menu_sweep.json;NewEstyma/ui_model/menu_sweep.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/menu_tree.json;NewEstyma/ui_model/menu_tree.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/menu_tree.md;NewEstyma/ui_model/menu_tree.md;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/outputs_test.json;NewEstyma/ui_model/outputs_test.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/program_bit_to_rect_kociol_monday.json;NewEstyma/ui_model/program_bit_to_rect_kociol_monday.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/program_screen.json;NewEstyma/ui_model/program_screen.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/render_eval.csv;NewEstyma/ui_model/render_eval.csv;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/render_eval.md;NewEstyma/ui_model/render_eval.md;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/schema/README.md;NewEstyma/ui_model/schema/README.md;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/schema/alarms.schema.json;NewEstyma/ui_model/schema/alarms.schema.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/schema/common.schema.json;NewEstyma/ui_model/schema/common.schema.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/schema/dialogs_edit_pin.schema.json;NewEstyma/ui_model/schema/dialogs_edit_pin.schema.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/schema/home_dialogs.schema.json;NewEstyma/ui_model/schema/home_dialogs.schema.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/schema/home_dialogs_widgets.schema.json;NewEstyma/ui_model/schema/home_dialogs_widgets.schema.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/schema/home_overlays_changed.schema.json;NewEstyma/ui_model/schema/home_overlays_changed.schema.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/schema/internet_editor.schema.json;NewEstyma/ui_model/schema/internet_editor.schema.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/schema/list_scales.schema.json;NewEstyma/ui_model/schema/list_scales.schema.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/schema/lists.schema.json;NewEstyma/ui_model/schema/lists.schema.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/schema/live_sources.schema.json;NewEstyma/ui_model/schema/live_sources.schema.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/schema/menu_sweep.schema.json;NewEstyma/ui_model/schema/menu_sweep.schema.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/schema/menu_tree.schema.json;NewEstyma/ui_model/schema/menu_tree.schema.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/schema/outputs_test.schema.json;NewEstyma/ui_model/schema/outputs_test.schema.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/schema/program_bit_to_rect_kociol_monday.schema.json;NewEstyma/ui_model/schema/program_bit_to_rect_kociol_monday.schema.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/schema/program_screen.schema.json;NewEstyma/ui_model/schema/program_screen.schema.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/editor/editor_seq.json;NewEstyma/ui_model/sii_acceptance/editor/editor_seq.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/editor/editor_seq.png;NewEstyma/ui_model/sii_acceptance/editor/editor_seq.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/info/RUN_SUMMARY.json;NewEstyma/ui_model/sii_acceptance/info/RUN_SUMMARY.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/info/info_2170_0.png;NewEstyma/ui_model/sii_acceptance/info/info_2170_0.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/info/info_2170_1.png;NewEstyma/ui_model/sii_acceptance/info/info_2170_1.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/info/info_2170_5678.png;NewEstyma/ui_model/sii_acceptance/info/info_2170_5678.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/info/info_2170_65535.png;NewEstyma/ui_model/sii_acceptance/info/info_2170_65535.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/info/info_3664_532.png;NewEstyma/ui_model/sii_acceptance/info/info_3664_532.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/info/info_3664_533.png;NewEstyma/ui_model/sii_acceptance/info/info_3664_533.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/info/info_3665_1.png;NewEstyma/ui_model/sii_acceptance/info/info_3665_1.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/internet/RUN_SUMMARY.json;NewEstyma/ui_model/sii_acceptance/internet/RUN_SUMMARY.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/internet/int_373D_0.png;NewEstyma/ui_model/sii_acceptance/internet/int_373D_0.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/internet/int_373D_2.png;NewEstyma/ui_model/sii_acceptance/internet/int_373D_2.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/internet/int_373E_0.png;NewEstyma/ui_model/sii_acceptance/internet/int_373E_0.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/internet/int_373E_1.png;NewEstyma/ui_model/sii_acceptance/internet/int_373E_1.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/internet/int_3741_0.png;NewEstyma/ui_model/sii_acceptance/internet/int_3741_0.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/internet/int_3741_1.png;NewEstyma/ui_model/sii_acceptance/internet/int_3741_1.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/internet/int_ssid_chunks.png;NewEstyma/ui_model/sii_acceptance/internet/int_ssid_chunks.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/internet/int_tap_ssid.png;NewEstyma/ui_model/sii_acceptance/internet/int_tap_ssid.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/siec/RUN_SUMMARY.json;NewEstyma/ui_model/sii_acceptance/siec/RUN_SUMMARY.json;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/siec/siec_empty.png;NewEstyma/ui_model/sii_acceptance/siec/siec_empty.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/siec/siec_n22_unknown.png;NewEstyma/ui_model/sii_acceptance/siec/siec_n22_unknown.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/siec/siec_n45.png;NewEstyma/ui_model/sii_acceptance/siec/siec_n45.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/siec/siec_n56.png;NewEstyma/ui_model/sii_acceptance/siec/siec_n56.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/siec/siec_n56_57.png;NewEstyma/ui_model/sii_acceptance/siec/siec_n56_57.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/siec/siec_n57.png;NewEstyma/ui_model/sii_acceptance/siec/siec_n57.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/siec/siec_n57_56.png;NewEstyma/ui_model/sii_acceptance/siec/siec_n57_56.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/siec/siec_n5B.png;NewEstyma/ui_model/sii_acceptance/siec/siec_n5B.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/verification_stage2/v_info.png;NewEstyma/ui_model/sii_acceptance/verification_stage2/v_info.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/verification_stage2/v_siec9.png;NewEstyma/ui_model/sii_acceptance/verification_stage2/v_siec9.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/ui_model/sii_acceptance/verification_stage2/v_siec_sw.png;NewEstyma/ui_model/sii_acceptance/verification_stage2/v_siec_sw.png;PROPOZYCJA;ui_model jako źródło prawdy, agent UI zatwierdza.
analiza_archiwum/FW2213TK-2026-11-22/data/widgets_by_state.json;NewEstyma/evidence/data/widgets_by_state.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/widgets_home_with_view_off.json;NewEstyma/evidence/data/widgets_home_with_view_off.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/widgets_inv_A.json;NewEstyma/evidence/data/widgets_inv_A.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/widgets_inv_A2.json;NewEstyma/evidence/data/widgets_inv_A2.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/widgets_inv_pass61_L0.json;NewEstyma/evidence/data/widgets_inv_pass61_L0.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/widgets_inv_pass61_L2.json;NewEstyma/evidence/data/widgets_inv_pass61_L2.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/widgets_inv_pass65_L1.json;NewEstyma/evidence/data/widgets_inv_pass65_L1.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/widgets_inv_pass65_L1_all.json;NewEstyma/evidence/data/widgets_inv_pass65_L1_all.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/widgets_inv_pass65_L3.json;NewEstyma/evidence/data/widgets_inv_pass65_L3.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/widgets_inv_pass65_cascade_fuelstore_L0.json;NewEstyma/evidence/data/widgets_inv_pass65_cascade_fuelstore_L0.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/widgets_inv_pass65_home_L0.json;NewEstyma/evidence/data/widgets_inv_pass65_home_L0.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/widgets_inv_pass65_program_kociol_co1_cwu.json;NewEstyma/evidence/data/widgets_inv_pass65_program_kociol_co1_cwu.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/widgets_inv_pass70_cascade_fuelstore_L3.json;NewEstyma/evidence/data/widgets_inv_pass70_cascade_fuelstore_L3.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/widgets_invm2_L2_partial.json;NewEstyma/evidence/data/widgets_invm2_L2_partial.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/widgets_invm2_casc_partial.json;NewEstyma/evidence/data/widgets_invm2_casc_partial.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/widgets_invm_L0.json;NewEstyma/evidence/data/widgets_invm_L0.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/widgets_invm_L2.json;NewEstyma/evidence/data/widgets_invm_L2.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/data/widgets_invm_casc.json;NewEstyma/evidence/data/widgets_invm_casc.json;PROPOZYCJA;Dane/evidence, nie usuwać poza exact duplicate.
analiza_archiwum/FW2213TK-2026-11-22/screens/pass48_header_L3_vs_L2.png;NewEstyma/evidence/visual/screens/pass48_header_L3_vs_L2.png;PROPOZYCJA;Dowód wizualny.
analiza_archiwum/FW2213TK-2026-11-22/screens/pass49_bufor_L0_vs_L1.png;NewEstyma/evidence/visual/screens/pass49_bufor_L0_vs_L1.png;PROPOZYCJA;Dowód wizualny.
analiza_archiwum/FW2213TK-2026-11-22/screens/pass49_co1_L0_vs_L1.png;NewEstyma/evidence/visual/screens/pass49_co1_L0_vs_L1.png;PROPOZYCJA;Dowód wizualny.
analiza_archiwum/FW2213TK-2026-11-22/screens/pass51_historia_alarmow_nawigacja_potwierdz.png;NewEstyma/evidence/visual/screens/pass51_historia_alarmow_nawigacja_potwierdz.png;PROPOZYCJA;Dowód wizualny.
analiza_archiwum/FW2213TK-2026-11-22/screens/pass52_kaskada_magazyn_paliwa.png;NewEstyma/evidence/visual/screens/pass52_kaskada_magazyn_paliwa.png;PROPOZYCJA;Dowód wizualny.
analiza_archiwum/FW2213TK-2026-11-22/screens/pass52_row6.png;NewEstyma/evidence/visual/screens/pass52_row6.png;PROPOZYCJA;Dowód wizualny.
analiza_archiwum/FW2213TK-2026-11-22/screens/pass52_row6_gear.png;NewEstyma/evidence/visual/screens/pass52_row6_gear.png;PROPOZYCJA;Dowód wizualny.
analiza_archiwum/FW2213TK-2026-11-22/screens/pass52_row7.png;NewEstyma/evidence/visual/screens/pass52_row7.png;PROPOZYCJA;Dowód wizualny.
analiza_archiwum/FW2213TK-2026-11-22/screens/pass52_row7_gear.png;NewEstyma/evidence/visual/screens/pass52_row7_gear.png;PROPOZYCJA;Dowód wizualny.
analiza_archiwum/FW2213TK-2026-11-22/screens/pass52_slider_bitmaps_163_165_186_187.png;NewEstyma/evidence/visual/screens/pass52_slider_bitmaps_163_165_186_187.png;PROPOZYCJA;Dowód wizualny.
analiza_archiwum/FW2213TK-2026-11-22/screens/pass54_pin_dialog_0900.png;NewEstyma/evidence/visual/screens/pass54_pin_dialog_0900.png;PROPOZYCJA;Dowód wizualny.
analiza_archiwum/FW2213TK-2026-11-22/screens/pass55_info_statystyki_siec_konfiguracja_alarmy.png;NewEstyma/evidence/visual/screens/pass55_info_statystyki_siec_konfiguracja_alarmy.png;PROPOZYCJA;Dowód wizualny.
analiza_archiwum/FW2213TK-2026-11-22/screens/pass58_menu_rows_pin_jezyk_test_stat_siec_internet.png;NewEstyma/evidence/visual/screens/pass58_menu_rows_pin_jezyk_test_stat_siec_internet.png;PROPOZYCJA;Dowód wizualny.
analiza_archiwum/FW2213TK-2026-11-22/screens/pass62_rtc_sync_from_can_0x2165.png;NewEstyma/evidence/visual/screens/pass62_rtc_sync_from_can_0x2165.png;PROPOZYCJA;Dowód wizualny.
analiza_archiwum/FW2213TK-2026-11-22/screens/render_CWU_poz0_480x272.png;NewEstyma/evidence/visual/screens/render_CWU_poz0_480x272.png;PROPOZYCJA;Dowód wizualny.
analiza_archiwum/FW2213TK-2026-11-22/screens/render_CWU_poz0_960x544.png;NewEstyma/evidence/visual/screens/render_CWU_poz0_960x544.png;PROPOZYCJA;Dowód wizualny.
analiza_archiwum/FW2213TK-2026-11-22/screens/render_CWU_poz2_480x272.png;NewEstyma/evidence/visual/screens/render_CWU_poz2_480x272.png;PROPOZYCJA;Dowód wizualny.
analiza_archiwum/FW2213TK-2026-11-22/screens/render_CWU_poz2_960x544.png;NewEstyma/evidence/visual/screens/render_CWU_poz2_960x544.png;PROPOZYCJA;Dowód wizualny.
analiza_archiwum/FW2213TK-2026-11-22/screens/render_HOME_L1_480x272.png;NewEstyma/evidence/visual/screens/render_HOME_L1_480x272.png;PROPOZYCJA;Dowód wizualny.
analiza_archiwum/FW2213TK-2026-11-22/screens/render_HOME_power_popup_480x272.png;NewEstyma/evidence/visual/screens/render_HOME_power_popup_480x272.png;PROPOZYCJA;Dowód wizualny.
analiza_archiwum/FW2213TK-2026-11-22/screens/render_HOME_power_popup_960x544.png;NewEstyma/evidence/visual/screens/render_HOME_power_popup_960x544.png;PROPOZYCJA;Dowód wizualny.
analiza_archiwum/FW2213TK-2026-11-22/screens/render_HOME_power_popup_by_config.png;NewEstyma/evidence/visual/screens/render_HOME_power_popup_by_config.png;PROPOZYCJA;Dowód wizualny.
analiza_archiwum/FW2213TK-2026-11-24/CHATGPT-SII-STAGE2.md;NewEstyma/evidence/reports/FW2213TK-2026-11-24/CHATGPT-SII-STAGE2.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
analiza_archiwum/FW2213TK-2026-11-24/CHATGPT-UI-MODEL-STAGE1.md;NewEstyma/evidence/reports/FW2213TK-2026-11-24/CHATGPT-UI-MODEL-STAGE1.md;DO_PYTANIA;Raport/historyczne dane, potrzebny lineage.
