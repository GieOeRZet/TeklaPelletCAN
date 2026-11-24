import pathlib,subprocess,sys
csv=pathlib.Path('analiza/FW2213TK-2026-11-22/data/access_gates_scan.csv')
assert csv.exists()
r=subprocess.run([sys.executable,'tools/cg_gate_inventory.py',str(csv)],capture_output=True,text=True,check=True)
for x in ['0x08054AB8','0x0805A9EC','0x0805B1D4','0x0805F400','0x0805FE9C','0x0806125C','0x08061518']: assert x in r.stdout,x
print('PASS test_cg_gate_inventory')
