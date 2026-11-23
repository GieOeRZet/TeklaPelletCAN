import json,sys
A=json.load(open('/tmp/w/out/kociol.json')); B=json.load(open('/tmp/w/out/kociolB.json'))
print("K1 identyczne:", A==B)
W={w['this']:w for w in A['widgets']}
ctl=A['control']
for pid,d in A['pids'].items():
    if 'runs' not in d: print(pid,d);continue
    dep={}
    for t in W:
        sts=[json.dumps(r['state'][t],sort_keys=True) for r in d['runs']]
        if len(set(sts))>1: dep[t]=[(r['value'],r['state'][t].get('text',r['state'][t].get('bmp')),r['state'][t]['vis']) for r in d['runs']]
    print(pid,d['name'],'stored',[r['stored'] for r in d['runs']],'zal.widgetow',len(dep))
    for t,v in dep.items():
        w=W[t];print('   ',t,w['role'],(w['ax'],w['ay'],w['w'],w['h']),'bmp0=',w.get('bitmap_id'),v)
