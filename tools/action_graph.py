#!/usr/bin/env python3
"""PASS 60: budowa grafu akcji UI z UI-MODEL i logu zdarzen.

Wejscie:
  ui_model.json
  actions.json - lista zdarzen. Minimalne pola: widget/this albo node/tap,
               handler, effects. Dodatkowe pola sa zachowane.

Nie wyprowadzamy akcji z samej geometrii. Brak identyfikatora widgetu oznacza
UNRESOLVED_ACTION_TARGET.
"""
import argparse, json
from collections import Counter, defaultdict

def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def items(model):
    return model.get("items", model if isinstance(model, list) else [])

def target_index(model_items):
    by_this, by_node_tap = {}, defaultdict(list)
    for i,w in enumerate(model_items):
        for k in ("this","addr"):
            if w.get(k) is not None:
                by_this[str(w[k]).lower()] = i
        key=(str(w.get("node")),str(w.get("tap")))
        by_node_tap[key].append(i)
    return by_this, by_node_tap

def resolve(a, by_this, by_node_tap):
    for k in ("widget","this","addr"):
        v=a.get(k)
        if v is not None and str(v).lower() in by_this:
            return [by_this[str(v).lower()]], "EXACT_WIDGET"
    key=(str(a.get("node")),str(a.get("tap")))
    xs=by_node_tap.get(key,[])
    if len(xs)==1 and a.get("node") is not None:
        return xs, "EXACT_NODE_TAP"
    if len(xs)>1:
        return xs, "AMBIGUOUS_NODE_TAP"
    return [], "UNRESOLVED_ACTION_TARGET"

def build(model, actions):
    ws=items(model); by_this, by_node_tap=target_index(ws)
    graph=[]
    for i,a in enumerate(actions):
        ids, evidence=resolve(a,by_this,by_node_tap)
        g=dict(action_index=i,evidence=evidence,widget_indices=ids,action=dict(a))
        g["presenter_candidates"]=[]
        for wi in ids:
            for p in ws[wi].get("presenter_candidates",[]):
                if p not in g["presenter_candidates"]:
                    g["presenter_candidates"].append(p)
        graph.append(g)
    return graph

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("ui_model")
    ap.add_argument("actions")
    ap.add_argument("out")
    ap.add_argument("--report")
    a=ap.parse_args()
    model=load(a.ui_model); actions=load(a.actions)
    if isinstance(actions,dict): actions=actions.get("actions",[])
    graph=build(model,actions)
    result={"schema":"NewEstyma.UIActionGraph/1","items":graph}
    with open(a.out,"w",encoding="utf-8") as f: json.dump(result,f,ensure_ascii=False,indent=2)
    c=Counter(x["evidence"] for x in graph)
    if a.report:
        with open(a.report,"w",encoding="utf-8") as f:
            f.write("# PASS 60 — UI ACTION GRAPH\n\n")
            f.write(f"- akcje: {len(graph)}\n")
            for k,v in sorted(c.items()): f.write(f"- {k}: {v}\n")
            f.write("\nTarget widgetu jest rozstrzygany po this/addr lub node+tap. ")
            f.write("Efekty akcji sa tylko danymi wejściowymi; narzedzie ich nie zgaduje.\n")
    print(json.dumps(dict(actions=len(graph),counts=dict(c))))

if __name__=="__main__":
    main()
