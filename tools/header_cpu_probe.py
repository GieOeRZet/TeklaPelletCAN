import sys,pickle
sys.path.insert(0,"/home/user/teklapelletcan/tools")
import ui_session as U
from PIL import Image
from unicorn import UC_HOOK_MEM_WRITE, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1
out=sys.argv[1]; fw=sys.argv[2]; idx=int(sys.argv[3])
rows=pickle.load(open(out+"/rows.pkl","rb"))
s=U.UiSession.from_checkpoint(fw,out+"/menu.state",None); s.wait(120)
nav=U.ListNav(s); nav.tall=Image.open(out+"/menu_tall.png"); nav.rows=rows
print(nav.tap_row_from_top(idx)); s.wait(200)
VP=0x808F638
for base in range(0x20000000,0x20030000,4):
    if s.b.rd(base,4)==VP: inst=base
o=inst+0x23C; buf=s.b.rd(o+0x34,4); print("inst",hex(inst),"obj",hex(o),"buf",hex(buf),[hex(s.b.rd(buf+k,2)) for k in range(0,16,2)])
log=[]
from unicorn.arm_const import UC_ARM_REG_SP
stk=[]
def w(uc,t,ad,sz,v,ud):
    if not stk:
        sp=uc.reg_read(UC_ARM_REG_SP); stk.extend(hex(x) for x in [s.b.rd(sp+k,4) for k in range(0,0x140,4)] if 0x08010001<=x<0x080A0000 and x&1)
    log.append((hex(uc.reg_read(UC_ARM_REG_PC)),hex(uc.reg_read(UC_ARM_REG_LR)),hex(ad),hex(v)))
s.b.mu.hook_add(UC_HOOK_MEM_WRITE,w,begin=buf,end=buf+15)
calls=[]
from unicorn.arm_const import UC_ARM_REG_R2,UC_ARM_REG_R3
def sn(uc,a,sz,ud):
    if uc.reg_read(UC_ARM_REG_R0)==buf:
        calls.append((hex(uc.reg_read(UC_ARM_REG_LR)),uc.reg_read(UC_ARM_REG_R1),hex(uc.reg_read(UC_ARM_REG_R2)),hex(uc.reg_read(UC_ARM_REG_R3))))
for a in (0x08041134,0x0804115E): s.b.mu.hook_add(UC_HOOK_CODE,sn,begin=a,end=a)
s.wait(1500)
print('SNPRINTF',calls[:6])
print(len(log)); 
seen=set()
for l in log:
    if l[:2] not in seen: seen.add(l[:2]); print(l)
print([hex(s.b.rd(buf+k,2)) for k in range(0,16,2)])

print('stack-returns',stk)
