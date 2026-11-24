/* estyma-panel-card v0.1 (prototyp, E7): karta Lovelace pokazujaca panel Estyma igneoTouch (HOME, menu, ekrany, nastawy) z danych firmware.
   Instalacja: skopiuj katalog web/estyma_prototype/ do /config/www/estyma/ i ten plik do /config/www/estyma-panel-card.js; zasob: /local/estyma-panel-card.js (modul).
   Konfiguracja karty:  type: custom:estyma-panel-card
                        base_url: /local/estyma/            # gdzie lezy index.html prototypu
                        entities: { boiler_temp: sensor.tekla_boiler_temp, hw_temp: sensor.tekla_hw_temp }   # opcjonalnie; bez tego szukamy encji sensor.*_<id>
   TYLKO ODCZYT: karta nie wywoluje zadnych uslug HA i nic nie wysyla do urzadzenia. */
class EstymaPanelCard extends HTMLElement {
  setConfig(c) { this._cfg = Object.assign({ base_url: "/local/estyma/", entities: {} }, c || {}); this._build(); }
  _build() {
    if (!this._root) { this._root = this.attachShadow({ mode: "open" }); }
    const base = this._cfg.base_url.replace(/\/?$/, "/");
    this._root.innerHTML = '<ha-card style="overflow:hidden"><iframe style="border:0;width:100%;height:560px;display:block;background:#0f1218"></iframe></ha-card>';
    this._frame = this._root.querySelector("iframe"); this._frame.src = base + "index.html";
    this._frame.addEventListener("load", () => this._push());
  }
  set hass(h) { this._hass = h; this._push(); }
  _push() {
    if (!this._hass || !this._frame || !this._frame.contentWindow) return;
    const out = {}, st = this._hass.states, map = this._cfg.entities || {};
    Object.keys(map).forEach(id => { const e = st[map[id]]; if (e) out[id] = e.state; });
    if (!Object.keys(map).length) Object.keys(st).forEach(eid => { if (eid.startsWith("sensor.")) out[eid.slice(7)] = st[eid].state; });      // id = nazwa encji bez domeny; karta dopasowuje koncowke
    this._frame.contentWindow.postMessage({ type: "estyma-states", states: out }, "*");
  }
  getCardSize() { return 8; }
  static getStubConfig() { return { base_url: "/local/estyma/" }; }
}
customElements.define("estyma-panel-card", EstymaPanelCard);
window.customCards = window.customCards || []; window.customCards.push({ type: "estyma-panel-card", name: "Estyma panel (prototyp)", description: "Panel igneoTouch z danych firmware, tylko odczyt" });
