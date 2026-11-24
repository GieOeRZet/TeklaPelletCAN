// Prototyp karty Estyma igneoTouch z ui_model. Dane przykladowe (domyslne z firmware). NIE laczy sie z urzadzeniem.
let M, stack = ["SCR:HOME:Ekran glowny:HOME:-1"];
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
  if (cur.startsWith("SCR:")){ const [, node, title, target, row] = cur.split(":"); screenView(s, node, title, target, row); return; }
  if (cur.startsWith("LISTA:")){ const [, key, title] = cur.split(":"); s.append(head(title + " - nastawy"));
    const rows = (M.lists[key]||[]).filter(r => r.pid && (r.level_min||0) <= lvl());
    if (!rows.length) s.append(msg("Brak wierszy dla tego poziomu/listy w ui_model."));
    rows.forEach(r => row(s, r.name, fmt(r), null)); return; }
  s.append(head((M.nodes[cur]||{}).title || cur)); s.append(msg("Ekran w przygotowaniu (szkielet E7)."));
}
const FONT_PX = [12, 20, 26, 36, 64, 92], DEMO = {"0x2001": 653, "0x2110": 480, "0x2112": 400, "0x2113": 400, "0x226C": 62};     // dane przykladowe: PID -> wartosc SUROWA (tak jak w pamieci panelu); prawdziwe: /api/v1/states przez pid_to_point.json
const SCREENS = {}, SCREEN_BY_ROW = {0:"KOCIOL",1:"PALNIK",2:"OGRZEWANIE1",3:"OGRZEWANIE2",4:"OGRZEWANIE3",5:"OGRZEWANIE4",6:"CWU",7:"SOLARY",8:"BUFOR",9:"KASKADA",10:"MAGAZYN",11:"ALARMY",12:"INFO",17:"TEST_WYJSC",18:"STATYSTYKI",19:"SIEC",20:"INTERNET"}; let tick = 0;
function liveText(f){ const b = (f.bind || []).find(x => DEMO[x.pid] !== undefined && x.scale); if (!b) return f.template.replace("{}", ""); const m = /(\d+\.(\d+))/.exec(f.sample || ""), dec = m ? m[2].length : 0; const v = (DEMO[b.pid] + (b.pid === "0x2001" ? 8 * Math.sin(tick / 5) : 0)) * b.scale; return (f.sample || "").replace(/-?\d+(\.\d+)?/, v.toFixed(dec)); }
function listKey(target, row){ const ks = Object.keys(M.lists).filter(k => k.split("|")[1] === target).sort(); return ks[target === "OGRZEWANIE" ? Math.min(Math.max(row - 2, 0), ks.length - 1) : 0]; }
function screenView(s, node, title, target, row){
  const sc = SCREENS[node]; const box = document.createElement("div"); box.className = "scr"; box.style.backgroundImage = "url(screens/" + node + ".png)";
  (sc.dynamic || []).forEach(f => { const e = document.createElement("div"); e.className = "dyn"; Object.assign(e.style, {left: f.rect[0]+"px", top: f.rect[1]+"px", width: f.rect[2]+"px", height: f.rect[3]+"px", color: f.color, font: FONT_PX[f.font]+"px/"+f.rect[3]+"px 'Roboto Condensed','Arial Narrow',sans-serif", textAlign: ["left","center","right"][f.align]}); e.textContent = liveText(f); e._f = f; box.append(e); });
  box.onclick = ev => { const r = box.getBoundingClientRect(), k = 480 / r.width, x = (ev.clientX - r.left) * k, y = (ev.clientY - r.top) * k;
    if (node === "HOME") { const dlg = box.querySelector(".dlg"); if (dlg) { if (x > 385 && y > 205 && y < 250) dlg.remove(); return; }
      const hit = [["home_paliwo", x < 135 && y > 195], ["home_zasilanie", x > 415 && y > 195], ["home_auto", x > 340 && y < 100 && y > 50], ["home_czas", x < 90 && y < 45], ["home_data", x > 160 && x < 320 && y < 45]].find(h => h[1]);
      if (hit) { const d = document.createElement("div"); d.className = "dlg"; d.style.backgroundImage = "url(dialogs/" + hit[0] + ".png)"; box.append(d); return; }
      if (x < 70 && y > 195) { stack = ["SCR:HOME:Ekran glowny:HOME:-1", "MENU"]; render(); } return; }
    if (x > 420 && y < 45) { stack = ["SCR:HOME:Ekran glowny:HOME:-1"]; render(); } else if (x < 130 && y < 45) { stack.pop(); render(); } else if (x > 240 && y > 225) { const k = listKey(target, +row); if (k) { stack.push("LISTA:" + k + ":" + title); render(); } } };
  s.append(box);
}
setInterval(() => { tick++; document.querySelectorAll(".dyn").forEach(e => e.textContent = liveText(e._f)); }, 1000);
function open(r){
  const sn = SCREEN_BY_ROW[r.row];
  if (sn && SCREENS[sn]){ stack.push("SCR:" + sn + ":" + r.title_pl + ":" + r.target + ":" + r.row); }
  else if (r.target === "KOCIOL"){ stack.push("LISTA:0x00|KOCIOL|inst1:" + r.title_pl); }
  else if (r.target) stack.push(r.target);
  render();
}
Promise.all(["HOME"].concat(Object.values(SCREEN_BY_ROW)).map(n => fetch("screens/" + n + ".json").then(r => r.ok ? r.json() : null).then(j => { if (j) SCREENS[n] = j; }).catch(() => {}))).then(() => fetch("model.json")).then(r=>r.json()).then(m=>{ M=m; document.querySelectorAll("#bar select").forEach(x=>x.onchange=()=>{stack=["SCR:HOME:Ekran glowny:HOME:-1"];render()}); render(); }).catch(e=>{$("scr").textContent="Blad ladowania model.json: "+e});
