#!/usr/bin/env python3
"""Regression tests for ETAP3 coverage evidence rules."""
import coverage_matrix as C

assert C.filename_provenance("L2_0_screen") == (2, 0, "screen", "DEFAULT", "default")
assert C.filename_provenance("L2_0_screen__350C=1") == (2, 0, "screen", "350C=1", "default")
assert C.filename_provenance("L2_0_screen__350C=1,3525=1") == (2, 0, "screen", "350C=1,3525=1", "default")
assert C.filename_provenance("L2_0_screen_alarm__350C=1") == (2, 0, "screen", "350C=1", "alarm")
assert C.filename_provenance("random_screen") is None
print("PASS: coverage provenance rules")
