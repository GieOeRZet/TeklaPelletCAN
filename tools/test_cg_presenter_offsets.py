import csv, tempfile, os
from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location("cg","tools/cg_presenter_offsets.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
assert m.BASE==0x08010000
assert m.scan
print("PASS cg_presenter_offsets: import/base/scan API OK")
