const app=document.getElementById("app");
const demo={name:"TeklaPellet Demo",base:"demo",online:true,state:{temp:64.8,set:60,returnTemp:41.9,power:0,burn:"Wyłączony",fuel:21,co1:49.8,co2:36.0,cwu:53.9,outside:-3}};
let devices=[]; let selected=null;

function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]})}
function fmt(v){return v==null||v===""?"—":typeof v==="number"?v.toFixed(1):esc(v)}
function load(){try{devices=JSON.parse(TPC.devices()||"[]")}catch(e){devices=[]}render()}
function persist(){TPC.saveDevices(JSON.stringify(devices))}
function stateFor(d){return d.base==="demo"?demo.state:(d.state||{temp:null,set:null,returnTemp:null,power:null,burn:"Brak danych",fuel:null,co1:null,co2:null,cwu:null,outside:null})}

function render(){
  if(!selected){
    app.innerHTML='<main class="wrap"><header class="top"><div class="logo">♨</div><div><div class="title">TeklaPellet</div><div class="sub">Nowa aplikacja • niezależny silnik</div></div></header>'+
    '<section class="card"><div class="empty"><strong>Brak dodanego modułu</strong>Najpierw dodaj urządzenie. Tryb demo jest dostępny tylko tutaj, dopóki nie dodasz prawdziwego modułu.</div>'+
    '<div class="actions"><button class="primary" onclick="openAdd()">＋ Dodaj moduł</button><button onclick="useDemo()">Uruchom demo</button></div></section>'+
    '<section class="card"><div class="label">Urządzenia</div><div class="list" id="list"></div></section></main>';
    renderList(); return;
  }
  const s=stateFor(selected);
  app.innerHTML='<main class="wrap"><header class="top"><div class="logo">♨</div><div><div class="title">'+esc(selected.name)+'</div><div class="sub"><span class="dot"></span>'+(selected.base==="demo"?"TRYB DEMO":esc(selected.base))+'</div></div></header>'+
  '<section class="card hero"><div><div class="temp">'+fmt(s.temp)+'<span class="unit">°C</span></div><div class="state">'+esc(s.burn)+'</div><div class="muted">zadana '+fmt(s.set)+' °C</div></div>'+
  '<div><div class="metric">Moc palnika <b>'+fmt(s.power)+' %</b></div><div class="metric">Powrót <b>'+fmt(s.returnTemp)+' °C</b></div><div class="metric">Paliwo <b>'+fmt(s.fuel)+' kg</b></div></div></section>'+
  '<section class="grid">'+tile("Zewn.",s.outside,"°C")+tile("Zasilanie",s.power===null?"Brak danych":"Włączone","")+tile("CO1",s.co1,"° / 45°")+tile("CO2",s.co2,"° / 35°")+tile("CWU",s.cwu,"° / 55°")+tile("Paliwo",s.fuel,"kg")+'</section>'+
  '<section class="card"><div class="label">Moduł</div><div class="actions"><button onclick="back()">‹ Urządzenia</button><button onclick="openAdd()">＋ Dodaj kolejny</button><button class="danger" onclick="removeSelected()">Usuń moduł</button></div></section></main>';
}
function tile(label,v,suf){return '<div class="card tile"><div class="label">'+label+'</div><div class="value">'+fmt(v)+' <small>'+suf+'</small></div></div>'}
function renderList(){
  const el=document.getElementById("list"); if(!el)return;
  if(!devices.length){el.innerHTML='<div class="empty">Brak zapisanych urządzeń.</div>';return}
  el.innerHTML=devices.map(function(d,i){return '<div class="device '+(d.online?"online":"")+'"><div><strong><span class="dot"></span>'+esc(d.name)+'</strong><span>'+esc(d.base)+'</span></div><button onclick="selectDevice('+i+')">Otwórz</button></div>'}).join("");
}
function openAdd(){
  app.insertAdjacentHTML("beforeend",'<div class="modal" id="modal"><div class="sheet"><h2>Dodaj moduł</h2><p>Podaj nazwę i adres IP modułu. Demo nie jest zapisywane jako urządzenie.</p><input id="dn" placeholder="Nazwa, np. Kocioł"><input id="dip" placeholder="http://192.168.1.50"><div class="actions"><button onclick="closeAdd()">Anuluj</button><button class="primary" onclick="addDevice()">Dodaj i sprawdź</button></div></div></div>');
}
function closeAdd(){var m=document.getElementById("modal");if(m)m.remove()}
function addDevice(){
  var name=(document.getElementById("dn").value||"TeklaPellet").trim();
  var base=(document.getElementById("dip").value||"").trim().replace(/\/$/,"");
  if(!/^https?:\/\//i.test(base)){alert("Adres musi zaczynać się od http:// lub https://");return}
  var d={name:name,base:base,online:false,state:null}; devices.push(d); persist(); closeAdd(); selected=d; render(); TPC.ping(String(devices.length-1),base);
}
window.nativePing=function(id,res){
  var i=Number(id),d=devices[i]; if(!d)return;
  d.online=!!res.ok;
  if(res.ok){try{var j=JSON.parse(res.body);d.name=j.name||d.name;d.state=j.state||d.state}catch(e){}}
  persist(); selected=d; render();
};
function selectDevice(i){selected=devices[i];render()}
function useDemo(){selected=demo;render()}
function back(){selected=null;render()}
function removeSelected(){var i=devices.indexOf(selected);if(i>=0){devices.splice(i,1);persist()}selected=null;render()}
load();
