#!/usr/bin/env python3
"""PASS 70: sklada wyniki list_scale.py (n_<node>.json) w ui_model/list_scales.json. Uzycie: list_scales_build.py WYNIKI_DIR"""
import json, collections, sys, os
SRC = sys.argv[1]
INV = {n['node']: {w['this']: w for w in n['widgets']} for n in json.load(open('analiza/FW2213TK-2026-11-22/data/widgets_inv_pass65_L3.json'))}
M = {'0_settings': '0x00', '1_settings': '0x0A', '2_settings': '0x01', '3_settings': '0x02', '4_settings': '0x03', '5_settings': '0x04', '6_settings': '0x05', '7_settings': '0x06', '8_settings': '0x07', '11_screen': '0x10', '16_screen': '0x11'}
out = dict(evidence='MEASURED (PASS 70, tools/list_scale.py, emulator, poziom 3, CO2-4: PID bazowy + (k-1)): dla kazdego wiersza wstrzykniete surowe wartosci PID (min, min+1, srodek, domyslna, max), odczytany tekst wyswietlany w widgecie wartosci (jedyny widget, ktorego tekst sie zmienil)', lists={})
stat = collections.Counter()
def ctrl(c):
    ch = c['changed']; return dict(pid=c['pid'], values=c['values'], stored=c['stored'], slot=(ch[0]['slot'] if ch else None), widgets=[dict(role=x['role'], ax=x['ax'], ay=x['ay'], w=x['w'], h=x['h'], per_value=x['per_value']) for x in ch])
for node, key in M.items():
    p = os.path.join(SRC, 'n_%s.json' % node)
    if not os.path.exists(p): continue
    d = json.load(open(p)); rows = []; W = INV[node]
    sp = os.path.join(SRC, 's_%s.json' % node); SW = json.load(open(sp)) if os.path.exists(sp) else {}
    for k, e in sorted(d.items(), key=lambda x: int(x[0])):
        slot = (W[e['value_widget']]['ay'] - 59) // 50 if e.get('value_widget') in W else None
        r = dict(idx=int(k), name_en=e['name_en'], pid=e['pid'], kind=e['kind'], raw_min=e['raw_min'], raw_max=e['raw_max']); s = e.get('samples', [])
        if slot is not None and slot < int(k):
            r['slot'] = slot; r['display'] = 'zaleznosc: zmiana PID zmienia widget wartosci WCZESNIEJSZEGO wiersza (slot %d), nie wlasna wartosc wiersza' % slot; stat['zaleznosc'] += 1
            if k in SW: r['control'] = ctrl(SW[k])
            rows.append(r); continue
        if slot is not None: r['slot'] = slot; r['slot_shift'] = slot - int(k)
        if not s: r['display'] = 'nie zmierzone (wiersz bez PID lub przelacznik)'; stat['brak'] += 1
        elif all('text' not in x for x in s): r['display'] = 'widget wartosci niejednoznaczny'; r['bound_candidates'] = e.get('bound_candidates'); stat['niejednoznaczne'] += 1
        else:
            tx = [(x['raw'], x['text'].strip()) for x in s]; nums = []
            for raw, t in tx:
                try: nums.append((raw, float(t)))
                except Exception: nums = None; break
            if nums:
                ratios = {round(v / raw, 4) for raw, v in nums if raw}
                dec = max((len(t.split('.')[1]) if '.' in t else 0) for _, t in tx)
                r.update(display='number', scale=(sorted(ratios)[0] if len(ratios) == 1 else None), ratios=sorted(ratios), decimals=dec, leading_space=any(x['text'].startswith(' ') for x in s), samples=[dict(raw=a, text=b) for a, b in tx]); stat['liczba'] += 1
            else: r.update(display='text', samples=[dict(raw=a, text=b) for a, b in tx]); stat['tekst'] += 1
        if k in SW:
            c = SW[k]; ch = c['changed']; r['control'] = ctrl(c)
            if c['kind'] == 'enum':
                tx = [x for x in ch if x['role'] == 'text']
                if tx: r['enum_text_id_candidates_UNRELIABLE'] = {v: tx[0]['per_value'][v].get('label') or '' for v in tx[0]['per_value']}
        rows.append(r)
    out['lists'][key] = dict(node=node, rows=rows)
out['summary'] = dict(stat)
json.dump(out, open('analiza/FW2213TK-2026-11-22/data/ui_model/list_scales.json', 'w'), ensure_ascii=False, indent=1); print(dict(stat))
