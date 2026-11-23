#!/usr/bin/env python3
"""PASS 98: Kocioł presenter/PID binding reconciliation audit."""
import csv,pathlib
p=pathlib.Path(__file__).resolve().parents[1]/'analiza/FW2213TK-2026-11-22/data/cg_kociol_bindings_reconciled.csv'
print('static reconciliation dataset:',p)
