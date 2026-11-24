#!/usr/bin/env python3
import sys as _s,pathlib as _p; _s.path.insert(0,str(_p.Path(__file__).resolve().parent)); import paths as _paths
"""PASS 98: Kocioł presenter/PID binding reconciliation audit."""
import csv,pathlib
p=_paths.DATA/'cg_kociol_bindings_reconciled.csv'
print('static reconciliation dataset:',p)
