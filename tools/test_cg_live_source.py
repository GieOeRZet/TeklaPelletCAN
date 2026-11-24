ROWS=[("0x2001","Boiler temperature"),("0x2277","Boiler pump state"),("0x3333","Boiler pressure"),("0x4000","Boiler return temperature"),("0x3628","Statistics total energy produced")]
assert len(ROWS)==5
assert all(pid.startswith("0x") for pid,_ in ROWS)
