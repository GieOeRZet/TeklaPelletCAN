// teklapelletclassic-card: karta Lovelace WYŁĄCZNIE dla integracji TeklaPelletCAN (domena "teklapelletcan").
// Nie zgaduje encji po całym Home Assistant jak oryginalna pelletcan-card (entity_prefix/auto) – urządzenie
// znajduje przez rejestr urządzeń HA (identifiers[0] === "teklapelletcan"), więc nie myli się z ESPHome
// ani z innymi integracjami. Renderuje się przez silnik teklapelletclassic-engine.js (ta sama baza co pelletcan-card),
// żeby mieć 1:1 tę samą funkcjonalność (ekrany, PIN-y, grafiki), bez przepisywania 1500 linii renderowania.
// JEDYNY zasób dashboardu tej karty: ten plik sam dociąga silnik (dynamic import, ten sam katalog HACS) –
// nie trzeba osobno dodawać drugiego zasobu w Ustawienia → Panele → Zasoby.
// Konfiguracja: tylko urządzenie (gdy więcej niż jedno), grafiki (domyślnie pełne), obraz kotła, język, ekran startowy.
(async () => {
  const DIR = new URL('.', import.meta.url).pathname;
  if (!customElements.get('tekla-panel-card')) { try { await import(DIR + 'teklapelletclassic-engine.js'); } catch (e) { console.error('teklapelletclassic-card: nie udało się załadować silnika renderowania', e); } }
  await customElements.whenDefined('tekla-panel-card').catch(() => {});
  const Base = customElements.get('tekla-panel-card');
  if (!Base) { console.warn('teklapelletclassic-card: brak silnika renderowania (teklapelletclassic-engine.js)'); return; }
  for (let i = 0; i < 50 && !window.__igneoFind; i++) await new Promise(r => setTimeout(r, 100));
  const IF = window.__igneoFind || {};

  const DOMAIN = 'teklapelletcan';

  // Urządzenia TYLKO tej integracji (identifiers = [["teklapelletcan", device_id]]). hass.devices/hass.entities
  // są standardowo dostarczane każdej karcie przez frontend HA – nie trzeba żadnych dodatkowych uprawnień.
  function ourDevices(hass) {
    if (!hass || !hass.devices) return [];
    return Object.values(hass.devices)
      .filter(d => Array.isArray(d.identifiers) && d.identifiers.some(id => Array.isArray(id) && id[0] === DOMAIN))
      .map(d => ({ id: d.id, name: (d.name_by_user || d.name || d.id) }))
      .sort((a, b) => a.name.localeCompare(b.name));
  }
  function deviceEntityIds(hass, deviceId) {
    if (!hass || !hass.entities) return [];
    return Object.values(hass.entities).filter(e => e.device_id === deviceId).map(e => e.entity_id);
  }
  // prefiks encji tego konkretnego urządzenia, wyliczony tym samym algorytmem co oryginalna karta (kotwice
  // typu "..._poziom_dostepu"), ale ograniczony wyłącznie do encji należących do wybranego urządzenia.
  function prefixOf(hass, deviceId) {
    const ids = deviceEntityIds(hass, deviceId);
    if (!ids.length || typeof IF.devices !== 'function') return '';
    const d = IF.devices(ids);
    return d.length ? d[0].p : '';
  }

  class TeklaPelletCanCard extends Base {
    setConfig(c) {
      if (!c || typeof c !== 'object') throw new Error('Nieprawidłowa konfiguracja karty');
      this._tcfg = Object.assign({ grafiki: 'pelne', boiler_image: '13', screen: 'main', language: 'auto' }, c);
      this._resolvedDevId = undefined;   // wymusza ponowne rozwiazanie urzadzenia/prefiksu (ale nie na kazdym tyknieciu hass!)
      if (this._lastHass) this._apply(this._lastHass); else super.setConfig(this._innerConfig({}));
    }
    _innerConfig(extra) {
      const t = this._tcfg || {};
      return Object.assign({
        type: 'custom:pelletcan-card',
        service_domain: DOMAIN,
        screen: t.screen || 'main',
        language: t.language || 'auto',
        grafiki: t.grafiki === 'domyslne' ? 'domyslne' : 'pelne',
        boiler_image: ['11', '12', '13', '14'].includes(String(t.boiler_image)) ? String(t.boiler_image) : '13',
      }, extra);
    }
    // WAZNE: tekla-panel-card.setConfig() resetuje biezacy ekran karty (this._scr = ...screen...). Dlatego
    // setConfig wolno wywolac ponownie TYLKO gdy faktycznie zmienilo sie urzadzenie (albo konfiguracja karty
    // z edytora) – NIGDY przy zwyklym odswiezeniu stanow z HA (co ~2 s), bo inaczej kazde klikniecie w karcie
    // cofa sie po chwili do ekranu glownego (dokladnie taki byl zglaszany blad).
    _apply(hass) {
      const devs = ourDevices(hass);
      if (!devs.length) {
        this._resolvedDevId = null;
        this.innerHTML = '<ha-card><div style="padding:16px;color:var(--error-color,#db4437);font-size:14px;line-height:1.5">' +
          '<b>TeklaPelletCAN</b><br>Nie znaleziono żadnego urządzenia tej integracji. Dodaj ją w ' +
          '<b>Ustawienia → Urządzenia i usługi → Dodaj integrację → TeklaPelletCAN</b>.</div></ha-card>';
        return;
      }
      const want = this._tcfg && this._tcfg.device_id;
      const dev = (want && devs.find(d => d.id === want)) || devs[0];
      this._multi = devs.length > 1;
      this._devName = dev.name;
      if (dev.id !== this._resolvedDevId || this._resolvedCfg !== this._tcfg) {
        this._resolvedDevId = dev.id;
        this._resolvedCfg = this._tcfg;
        this._pf = prefixOf(hass, dev.id);   // raz na urzadzenie: nazwa encji sie nie zmienia w trakcie dzialania karty
        if (this._warnEl) { this._warnEl.remove(); this._warnEl = null; }
        super.setConfig(this._innerConfig(this._pf ? { entity_prefix: this._pf } : {}));
      }
      super.hass = hass;
      if (this._multi && !want && !this._warnEl) {
        this._warnEl = document.createElement('div');
        this._warnEl.style.cssText = 'font-size:11px;opacity:.65;text-align:center;padding:4px 0 0';
        this._warnEl.textContent = 'Wykryto kilka urządzeń TeklaPelletCAN – pokazuję „' + this._devName + '” (wybierz właściwe w ustawieniach karty).';
        this.appendChild(this._warnEl);
      }
    }
    set hass(h) { this._lastHass = h; if (this._tcfg) this._apply(h); }
    get hass() { return this._lastHass; }
    static getConfigElement() { return document.createElement('teklapelletclassic-card-editor'); }
    static getStubConfig() { return { screen: 'main', grafiki: 'pelne' }; }
  }
  if (!customElements.get('teklapelletclassic-card')) customElements.define('teklapelletclassic-card', TeklaPelletCanCard);

  // ---- edytor: tylko urządzenie (gdy >1), grafiki, obraz kotła, język, ekran – bez ręcznego mapowania encji ----
  class TeklaPelletCanCardEditor extends HTMLElement {
    setConfig(c) { this._cfg = Object.assign({ grafiki: 'pelne', boiler_image: '13', screen: 'main', language: 'auto' }, c || {}); this._draw(); }
    set hass(h) { this._hass = h; this._draw(); }
    _draw() {
      if (!this._cfg) return;
      if (!this._form) {
        const info = document.createElement('div');
        info.style.cssText = 'font-size:13px;line-height:1.45;margin:0 0 10px;opacity:.9';
        info.textContent = 'Karta pokazuje wyłącznie urządzenia integracji TeklaPelletCAN i sama dobiera ich encje – nie trzeba nic mapować ręcznie.';
        this.appendChild(info);
        this._form = document.createElement('ha-form');
        this._form.computeLabel = s => s.label || s.name;
        this._form.addEventListener('value-changed', ev => this._changed(ev.detail.value));
        this.appendChild(this._form);
      }
      const devs = this._hass ? ourDevices(this._hass) : [];
      const D = window.__teklaDefs || { SCREEN_OPTS: [] };
      const schema = [
        { name: 'screen', label: 'Ekran startowy karty', selector: { select: { mode: 'dropdown', options: (D.SCREEN_OPTS || []).map(o => ({ value: o[0], label: o[1] })) } } },
        { name: 'language', label: 'Język / Language', selector: { select: { mode: 'dropdown', options: [{ value: 'auto', label: 'Auto (język Home Assistant)' }].concat(Object.keys((window.__pcLang || {}).names || {}).map(k => ({ value: k, label: window.__pcLang.names[k] }))) } } },
        { name: 'grafiki', label: 'Grafiki panela', selector: { select: { mode: 'dropdown', options: [{ value: 'pelne', label: 'Pełne (domyślne, oryginalne grafiki Estymy)' }, { value: 'domyslne', label: 'Domyślne karty (tylko zbiornik paliwa)' }] } } },
        { name: 'boiler_image', label: 'Obraz kotła (grafiki pełne)', selector: { select: { mode: 'dropdown', options: [{ value: '11', label: 'Typ 11' }, { value: '12', label: 'Typ 12' }, { value: '13', label: 'Typ 13' }, { value: '14', label: 'Typ 14' }] } } },
      ];
      if (devs.length > 1) {
        schema.unshift({
          name: 'device_id', label: 'Urządzenie',
          selector: { select: { mode: 'dropdown', options: [{ value: 'auto', label: 'Automatycznie (pierwsze znalezione)' }].concat(devs.map(d => ({ value: d.id, label: d.name }))) } },
        });
      }
      this._form.schema = schema;
      this._form.data = Object.assign({}, this._cfg, { device_id: this._cfg.device_id || 'auto' });
      if (this._hass) this._form.hass = this._hass;
    }
    _changed(v) {
      const cfg = Object.assign({}, this._cfg, {
        screen: v.screen || 'main', language: v.language || 'auto', grafiki: v.grafiki === 'domyslne' ? 'domyslne' : 'pelne',
        boiler_image: v.boiler_image || '13',
      });
      if (v.device_id && v.device_id !== 'auto') cfg.device_id = v.device_id; else delete cfg.device_id;
      this._cfg = cfg;
      this.dispatchEvent(new CustomEvent('config-changed', { detail: { config: cfg }, bubbles: true, composed: true }));
    }
  }
  if (!customElements.get('teklapelletclassic-card-editor')) customElements.define('teklapelletclassic-card-editor', TeklaPelletCanCardEditor);

  window.customCards = window.customCards || [];
  if (!window.customCards.some(c => c.type === 'teklapelletclassic-card')) {
    window.customCards.push({
      type: 'teklapelletclassic-card',
      name: 'TeklaPelletClassic-card',
      description: 'Panel kotła Tekla/Estyma (replika panelu) – wyłącznie dla integracji TeklaPelletCAN (encje dobierane automatycznie).',
      preview: true,
    });
  }
})();
