#!/usr/bin/env python3
"""Data-only renderer for Estyma dialog windows. Unknown data is BRAK_DANYCH."""
import argparse,json,sys
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"analiza"/"FW2213TK-2026-11-22"/"data"
BG=(41,40,41)
def locate(name):
    for p in (ROOT/"ui_model"/name,DATA/"ui_model"/name,ROOT/"NewEstyma"/"ui_model"/name):
        if p.exists(): return p
    return None
def rgb565(v):
    r,g,b=(v>>11)&31,(v>>5)&63,v&31
    return (r<<3|r>>2,g<<2|g>>4,b<<3|b>>2)
def render_home(name,out):
    src=locate("home_dialogs_widgets.json")
    if not src: raise FileNotFoundError("home_dialogs_widgets.json")
    widgets=json.loads(src.read_text())[name]["widgets"]
    sys.path.insert(0,str(ROOT/"tools")); import ui_render as R
    img=Image.new("RGB",(480,272),BG); d=ImageDraw.Draw(img); missing=[]
    for w in widgets:
        x,y,ww,hh=w["rect"]
        if w["cls"]=="box" and w.get("box") is not None:
            d.rectangle([x,y,x+ww-1,y+hh-1],fill=rgb565(int(w["box"])))
        elif w.get("bmp") is not None:
            b=R.bitmap(int(w["bmp"]))
            if b is None: missing.append("bitmap:"+str(w["bmp"]))
            else: img.paste(b.convert("RGB"),(x,y),b.getchannel("A"))
        elif w["cls"]=="text" and w.get("text"):
            missing.append("font mapping:"+str(w["this"]))
    img.save(out); return sorted(set(missing))
def partial(name,out):
    img=Image.new("RGB",(480,272),BG); d=ImageDraw.Draw(img); m=[]
    if name=="number":
        m+=["full widget inventory","exact button/slider assets","font IDs/positions"]
        d.rectangle([140,202,295,238],outline=(100,100,100))
    elif name=="enum":
        m+=["full widget inventory","radio/OK assets","font IDs/positions"]
        for y in (87,125): d.rectangle([120,y,152,y+32],outline=(100,100,100))
    elif name=="pin":
        m+=["full widget inventory","keypad assets","font IDs/positions"]
        for x in (90,171,250,329): d.rectangle([x-18,81,x+18,117],outline=(100,100,100))
    elif name=="internet":
        m+=["full keyboard overlay inventory","keyboard assets","font/color mapping"]
        for box in [(287,170,323,206),(336,170,372,206),(386,170,422,206),(436,170,472,206),(285,209,321,245),(336,209,372,245),(386,209,422,245),(436,209,472,245)]: d.rectangle(box,outline=(100,100,100))
    elif name=="program_day":
        m+=["full day-dialog widget inventory","eco/comfort/copy/OK assets","exact title/value fonts"]
        d.rectangle([169,136,221,172],outline=(100,100,100)); d.rectangle([249,136,301,172],outline=(100,100,100)); d.rectangle([168,182,302,218],outline=(100,100,100))
    elif name=="program_copy":
        m+=["full copy-dialog widget inventory","checkbox states/assets","exact title font"]
        for x,y in ((170,92),(170,136),(170,182),(170,226),(320,92),(320,136),(320,182)): d.rectangle([x-15,y-15,x+15,y+15],outline=(100,100,100))
    else: m+=["dialog definition"]
    img.save(out); return sorted(set(m))
def render_dialog(name,out):
    return render_home(name,out) if name in {"paliwo","zasilanie","auto","czas","data"} else partial(name,out)
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("name"); ap.add_argument("out"); a=ap.parse_args()
    print(json.dumps({"name":a.name,"missing":render_dialog(a.name,a.out)},ensure_ascii=False))
