from tools.cg_catalog23 import BASE, COUNT, STEP, decode
assert BASE == 0x20008C50
assert COUNT == 23
assert STEP == 0x10
ram=bytearray(0x10000)
base=0x20000000
for i in range(COUNT):
    ptr=0x20008AE0+i*STEP
    ram[BASE-base+i*4:BASE-base+i*4+4]=ptr.to_bytes(4,"little")
    ram[ptr+8-base:ptr+12-base]=(i+100).to_bytes(4,"little")
assert decode(ram,base)[-1] == (22,0x20008C40,122)
