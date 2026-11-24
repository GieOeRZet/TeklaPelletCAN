import sys,os,json
import os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
FW,STATE,OUT=sys.argv[1:4]    # FW.bin  node_17_screen.state (SIEC)  katalog wyjsciowy
os.makedirs(OUT,exist_ok=True)
import ui_session as U; from PIL import Image
def new(): s=U.UiSession.from_checkpoint(FW,STATE,None); s.wait(200); return s
def feed(s,nodes,rounds=6):
    for _ in range(rounds):
        for n in nodes:
            s.can(0x700+n,[5]); s.wait(12); s.can(0x580+n,[0x43,0x18,0x10,2,0,0,0,0]); s.wait(12)
        s.wait(120)
cases=[('empty',[]),('56',[0x56]),('57',[0x57]),('56+57',[0x56,0x57]),('57+56',[0x57,0x56]),('5B',[0x5B]),('45',[0x45]),('22 unknown',[0x22])]
ims=[]
for name,nodes in cases:
    s=new(); feed(s,nodes); im=s.shot(); im.crop((0,40,480,272)).save(OUT+'/c_%s.png'%name.replace('+','_').replace(' ','_')); ims.append(im.crop((0,40,480,272)))
# timeout: after 56 appears, stop feeding 700 ticks, then re-appear
s=new(); feed(s,[0x56]); a=s.shot(); s.wait(1500); b=s.shot(); feed(s,[0x56],3); c=s.shot()
for k,i in (('t_present',a),('t_timeout',b),('t_reappear',c)): ims.append(i.crop((0,40,480,272)))
W,H=ims[0].size; m=Image.new('RGB',(W*2,H*((len(ims)+1)//2)))
for i,im in enumerate(ims): m.paste(im,((i%2)*W,(i//2)*H))
m.save(OUT+'/all.png'); print(len(ims))
