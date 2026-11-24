import hashlib, pathlib, subprocess, sys
p=pathlib.Path('/mnt/data/FW2213TK (1).bin')
assert hashlib.sha256(p.read_bytes()).hexdigest()=='1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071'
r=subprocess.run([sys.executable,'tools/cg_pin_rtc_scan.py',str(p)],capture_output=True,text=True,check=True)
for needle in ['0x8039599','0x800f332','0x8019090','0x08028F78','0x08028FF8','OPEN']:
    assert needle in r.stdout, needle
print('PASS test_cg_pin_rtc_scan')
