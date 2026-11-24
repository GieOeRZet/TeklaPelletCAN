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
  if (cur.startsWith("LISTA:")){ const [, key, title] = cur.split(":"); s.append(head(title + " - nastawy"));
    const rows = (M.lists[key]||[]).filter(r => r.pid && (r.level_min||0) <= lvl());
    if (!rows.length) s.append(msg("Brak wierszy dla tego poziomu/listy w ui_model."));
    rows.forEach(r => row(s, r.name, fmt(r), null)); return; }
  s.append(head((M.nodes[cur]||{}).title || cur)); s.append(msg("Ekran w przygotowaniu (szkielet E7)."));
}
function open(r){
  if (r.target === "KOCIOL"){ stack.push("LISTA:0x00|KOCIOL|inst1:" + r.title_pl); }
  else if (r.target) stack.push(r.target);
  render();
}
fetch("model.json").then(r=>r.json()).then(m=>{ M=m; document.querySelectorAll("#bar select").forEach(x=>x.onchange=()=>{stack=["MENU"];render()}); render(); }).catch(e=>{$("scr").textContent="Blad ladowania model.json: "+e});
