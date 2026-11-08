// Warstwa zgodności: z API urządzenia buduje obiekt `hass` taki, jakiego oczekuje oryginalna karta PelletCAN.
// Karta czyta hass.states i woła hass.callService – to wszystko, czego używa (+ opcjonalnie callWS do historii).
const SERVICE_DOMAIN = 'teklapelletcan';
const NODE = 'tekla_estyma';
const ACTIONS = ['unlock', 'set_setpoint', 'set_boiler_mode', 'set_param', 'set_schedule', 'set_output', 'set_output_pct',
  'test_refresh', 'test_reset', 'alarm_refresh', 'param_refresh', 'schedule_refresh', 'sdo_read', 'sdo_scan',
  'sdo_scan_stop', 'sdo_write', 'sdo_poll_add', 'sdo_poll_clear'];

export class DeviceHass {
  constructor(base = '') {
    this.base = base;
    this.states = {};
    this.language = (navigator.language || 'pl').slice(0, 2);
    this.locale = { language: this.language };
    this.services = { [SERVICE_DOMAIN]: Object.fromEntries(ACTIONS.map(a => [NODE + '_' + a, {}])) };
    this.listeners = new Set();
    this.online = false;
    this.level = 0;
  }

  onUpdate(fn) { this.listeners.add(fn); return () => this.listeners.delete(fn); }

  async refresh() {
    try {
      const r = await fetch(this.base + '/api/v1/states', { cache: 'no-store' });
      if (!r.ok) throw new Error('HTTP ' + r.status);
      const j = await r.json();
      const next = {};
      for (const s of j.states) next[s.entity_id] = s;
      this.states = next;
      this.online = true;
      this.level = j.level || 0;
    } catch (e) {
      this.online = false;
    }
    this.listeners.forEach(fn => fn(this));
  }

  start(periodMs = 2000) {
    this.refresh();
    this._t = setInterval(() => this.refresh(), periodMs);
  }

  get clientId() {
    let id = '';
    try { id = localStorage.getItem('tpc_client_id') || ''; } catch (e) { /* brak localStorage */ }
    if (!id) {
      id = 'web-' + Math.random().toString(16).slice(2) + Date.now().toString(16);
      try { localStorage.setItem('tpc_client_id', id); } catch (e) { /* ignoruj */ }
    }
    return id;
  }

  get token() { try { return localStorage.getItem('tpc_token') || ''; } catch (e) { return ''; } }
  set token(v) { try { localStorage.setItem('tpc_token', v); } catch (e) { /* ignoruj */ } }

  async _post(path, body, withToken = true) {
    const headers = { 'Content-Type': 'application/json' };
    if (withToken && this.token) headers.Authorization = 'Bearer ' + this.token;
    const r = await fetch(this.base + path, { method: 'POST', headers, body: JSON.stringify(body) });
    return { status: r.status, json: await r.json().catch(() => ({})) };
  }

  // Parowanie przeglądarki z urządzeniem: hasło urządzenia -> token (pamiętany w tej przeglądarce).
  async pair() {
    const info = await (await fetch(this.base + '/api/v1/info', { cache: 'no-store' })).json();
    let pw;
    if (!info.password_set) {
      pw = (window.prompt('Ustaw hasło urządzenia (min. 4 znaki). Będzie potrzebne do sterowania kotłem:') || '').trim();
      if (!pw) throw new Error('anulowano');
      const r = await this._post('/api/v1/password', { password: pw }, false);
      if (r.status !== 200) throw new Error('hasło: ' + (r.json.error || r.status));
    } else {
      pw = window.prompt('Hasło urządzenia:') || '';
      if (!pw) throw new Error('anulowano');
    }
    const r = await this._post('/api/v1/pair', { password: pw, client_id: this.clientId, name: 'Przeglądarka' }, false);
    if (r.status !== 200) throw new Error('parowanie: ' + (r.json.error || r.status));
    this.token = r.json.token;
  }

  async callService(domain, service, data = {}) {
    // Zapisy wymagają tokenu; odczyty (stany) są otwarte. Przy braku/nieważnym tokenie – jednorazowo sparuj i ponów.
    let r = await this._post('/api/v1/call', { domain, service, data });
    if (r.status === 401 || (r.status === 403 && r.json.error === 'setup_required')) {
      try { await this.pair(); } catch (e) { return Promise.reject(e); }
      r = await this._post('/api/v1/call', { domain, service, data });
    }
    setTimeout(() => this.refresh(), 400);   // szybkie odświeżenie po akcji
    return r.status < 300 ? r.json : Promise.reject(Object.assign(new Error(r.json.result || r.json.error || ('HTTP ' + r.status)), { status: r.status }));
  }

  // Historia (używana przez kartę tylko jako zapas dla alarmów) – urządzenie nie ma historii; karta czyta wpisy z encji.
  async callWS() { return {}; }
}
