#!/usr/bin/env bash
# Rownolegly render dialogow (max 4 procesow): run_dialogs_par.sh OUTROOT [dialog ...]; wyniki OUTROOT/<dialog>/ + podsumowanie
cd "$(dirname "$0")/.."; export ESTYMA_IDLE_FAST=1; OUT=${1:-/tmp/w/dr}; shift
L=${@:-pin program_day program_copy internet_editor number_dialog home_paliwo home_zasilanie home_auto home_czas home_data}
printf '%s\n' $L | xargs -P4 -I{} sh -c "mkdir -p $OUT/{} && python3 -I tools/dialog_render_eval.py FW2213TK_kopia.bin /tmp/w/L0 /tmp/w/L1 /tmp/w/L3 $OUT/{} {} > $OUT/{}.log 2>&1"
cat $OUT/*.log
