#!/usr/bin/env bash
# E3: rownolegle (4 procesy) automat pokrycia dla poziomow 0,1,3 i wszystkich konfiguracji: run_coverage_par.sh OUTROOT
cd "$(dirname "$0")/.."; export ESTYMA_IDLE_FAST=1; OUT=${1:-/tmp/w/cov}; mkdir -p $OUT
for L in 1 3 0; do for C in DEFAULT FULL 2105=0 2105=1 2105=2 2105=3 0x2106=0 0x2107=0 0x2108=0 350C=1 3525=1 350C=1,3525=1; do echo "$L $C"; done; done | \
  xargs -P4 -L1 sh -c 'python3 -I tools/coverage_gen.py $0 $1 '"$OUT"' > '"$OUT"'/log_$0_$(echo $1 | tr -c "A-Za-z0-9\n" _).txt 2>&1'
