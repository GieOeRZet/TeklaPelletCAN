#!/usr/bin/env python3
import sys as _s,pathlib as _p; _s.path.insert(0,str(_p.Path(__file__).resolve().parent)); import paths as _paths
"""PASS 100: normalize recovered alarm raise/clear site inventory."""
import pathlib
p=_paths.DATA/"cg_alarm_catalog_sites.csv"
print(p)
