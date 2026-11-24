// Prototyp karty Estyma igneoTouch z ui_model. Dane przykladowe (domyslne z firmware). NIE laczy sie z urzadzeniem.
let M, stack = ["MENU"];
const $ = id => document.getElementById(id);
const cfg = () => ({"0x2105":+$("c2105").value,"0x2106":+$("c2106").value,"0x2107":+$("c2107").value,"0x2108":+$("c2108").value,"0x350C":+$("c350C").value,"0x3525":+$("c3525").value});
const lvl = () => +$("lvl").value;
const ops = {">=":(a,b)=>a>=b,"!=":(a,b)=>a!=b,"==":(a,b)=>a==b,"<=":(a,b)=>a<=b,">":(a,b)=>a>b,"<":(a,b)=>a<b};
function visible(r){ if ((r.level_min||0) > lvl()) return false; const c = cfg(); return (r.config_cond||[]).every(x => (ops[x.op]||(()=>true))(c[x.pid]??0, x.val)); }
function fmt(r){ const v = r.def ?? 0, f = r.fmt || {}, d = f.decimals || 0, s = f.scale || 1; return (v*s).toFixed(d); }
function head(t){ const e = document.createElement("div"); e.className="hd"; if (stack.length>1){ const b=document.createElement("button"); b.textContent="<"; b.onclick=()=>{stack.pop();render()}; e.append(b);} e.append(t); return e; }
function row(p, n, v, cb){ const e = document.createElement("div"); e.className="row"; e.innerHTML = '<span class="n"></span><span class="v"></span>'; e.children[0].textContent=n; e.children[1].textContent=v; if(cb) e.onclick=cb; p.append(e); }
function msg(t){ const e = document.createElement("div"); e.className="mut"; e.textContent=t; return e; }
function render(){
  const s = $("scr"), cur = stack[stack.length-1]; s.innerHTML = "";
  if (cur === "MENU"){ s.append(head("MENU")); M.menu_rows.filter(visible).forEach(r => row(s, r.title_pl, "", () => open(r))); return; }
  if (cur.startsWith("SCR:")){ const [, node, title] = cur.split(":"); screenView(s, node, title); return; }
  if (cur.startsWith("LISTA:")){ const [, key, title] = cur.split(":"); s.append(head(title + " - nastawy"));
    const rows = (M.lists[key]||[]).filter(r => r.pid && (r.level_min||0) <= lvl());
    if (!rows.length) s.append(msg("Brak wierszy dla tego poziomu/listy w ui_model."));
    rows.forEach(r => row(s, r.name, fmt(r), null)); return; }
  s.append(head((M.nodes[cur]||{}).title || cur)); s.append(msg("Ekran w przygotowaniu (szkielet E7)."));
}
const FONT_PX = [12, 20, 26, 36, 64, 92], DEMO = {"0x2001": 65.3, "0x2004": 70};     // dane przykladowe (PID -> wartosc); prawdziwe: /api/v1/states przez pid_to_point.json
const SCREENS = {}; let tick = 0;
function liveText(f){ const b = (f.bind || []).find(x => DEMO[x.pid] !== undefined); if (!b) return f.template.replace("{}", ""); const v = DEMO[b.pid] + (b.pid === "0x2001" ? Math.sin(tick / 5) : 0); return f.template.replace("{}", v.toFixed(1)); }
function screenView(s, node, title){
  const sc = SCREENS[node]; const box = document.createElement("div"); box.className = "scr"; box.style.backgroundImage = "url(screens/" + node + ".png)";
  (sc.dynamic || []).forEach(f => { const e = document.createElement("div"); e.className = "dyn"; Object.assign(e.style, {left: f.rect[0]+"px", top: f.rect[1]+"px", width: f.rect[2]+"px", height: f.rect[3]+"px", color: f.color, font: FONT_PX[f.font]+"px/"+f.rect[3]+"px 'Roboto Condensed','Arial Narrow',sans-serif", textAlign: ["left","center","right"][f.align]}); e.textContent = liveText(f); e._f = f; box.append(e); });
  box.onclick = ev => { const r = box.getBoundingClientRect(), k = 480 / r.width, x = (ev.clientX - r.left) * k, y = (ev.clientY - r.top) * k;
    if (x < 130 && y < 45) { stack.pop(); render(); } else if (x > 240 && y > 225) { stack.push("LISTA:0x00|" + node + "|inst1:" + title); render(); } };
  s.append(box);
}
setInterval(() => { tick++; document.querySelectorAll(".dyn").forEach(e => e.textContent = liveText(e._f)); }, 1000);
function open(r){
  if (r.target === "KOCIOL" && SCREENS.KOCIOL){ stack.push("SCR:KOCIOL:" + r.title_pl); }
  else if (r.target === "KOCIOL"){ stack.push("LISTA:0x00|KOCIOL|inst1:" + r.title_pl); }
  else if (r.target) stack.push(r.target);
  render();
}
fetch("screens/KOCIOL.json").then(r => r.ok ? r.json() : null).then(j => { if (j) SCREENS.KOCIOL = j; }).catch(() => {}).then(() => fetch("model.json")).then(r=>r.json()).then(m=>{ M=m; document.querySelectorAll("#bar select").forEach(x=>x.onchange=()=>{stack=["MENU"];render()}); render(); }).catch(e=>{$("scr").textContent="Blad ladowania model.json: "+e});
