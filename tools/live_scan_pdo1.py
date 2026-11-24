import sys
sys.path.insert(0,'/home/user/TeklaPelletCAN/tools')
import ui_session as U, action_probe as AP
cfg=[(0x350A,1),(0x350D,1),(0x362B,1),(0x3629,1),(0x3605,1),(0x3707,1)]
nodes=[int(x,16) for x in sys.argv[1:]]
s=U.UiSession.from_checkpoint('/home/user/TeklaPelletCAN/FW2213TK_kopia.bin','/tmp/w/L0/menu.state',None)
s.wait(4500)
for p,v in cfg: s.inject_param(p,v)
s.wait(300); st='/tmp/w/ls/lv4_%s.state'%sys.argv[1]; s.checkpoint(st)
recs=AP.pid_records(s); BG={0x3726,0x2311,0x2312,0x2313,0x2314,0x2167,0x229A}
def go(node,val,bases):
    s.b.load_state(st)
    if node:
        for _ in range(10):
            for b in bases:
                s.can(b+node,b"".join(val.to_bytes(2,'little') for _ in range(4))); s.wait(12)
            s.wait(40)
    s.wait(300); return AP.pid_snap(s,recs)
b0=go(None,0,[])
for n in nodes:
    for bases in ([0x180],[0x280,0x380,0x480],[0x180,0x280,0x380,0x480]):
        for v in (500,2000):
            sn=go(n,v,bases); d={hex(p):sn[p] for p in sn if p not in BG and sn[p]!=b0.get(p)}
            print(hex(n),[hex(b) for b in bases],v,d,flush=True)
