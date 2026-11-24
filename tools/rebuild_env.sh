#!/usr/bin/env bash
# Odtwarza srodowisko robocze emulatora w /tmp/w (punkty kontrolne menu dla poziomow L0, L1, L3 i kaskady/magazynu). Wymaga FW2213TK_kopia.bin w katalogu repo.
set -e
cd "$(dirname "$0")/.."
FW=${FW:-FW2213TK_kopia.bin}
[ -f "$FW" ] || { echo "Brak $FW (firmware nie jest w repo - poproc wlasciciela)"; exit 1; }
sha256sum "$FW" | grep -q 1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071 || { echo "ZLY SHA-256 firmware"; exit 1; }
export ESTYMA_IDLE_FAST=1
mkdir -p /tmp/w
python3 -I tools/ui_prepare_cfg.py "$FW" /tmp/w/L0 0 &
python3 -I tools/ui_prepare_cfg.py "$FW" /tmp/w/L1 1 &
python3 -I tools/ui_prepare_cfg.py "$FW" /tmp/w/L3 3 &
wait
python3 -I tools/ui_prepare_cfg.py "$FW" /tmp/w/LC3 3 0x350C=1 0x3525=1 0x351A=2
echo "OK: /tmp/w/{L0,L1,L3,LC3} gotowe; wezly N_screen/N_settings powstaja leniwie (action_probe.enter_node)"
