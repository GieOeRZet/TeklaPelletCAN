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

  async callService(domain, service, data = {}) {
    const r = await fetch(this.base + '/api/v1/call', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ domain, service, data }),
    });
    setTimeout(() => this.refresh(), 400);   // szybkie odświeżenie po akcji
    return r.ok ? r.json().catch(() => ({})) : Promise.reject(new Error('HTTP ' + r.status));
  }

  // Historia (używana przez kartę tylko jako zapas dla alarmów) – urządzenie nie ma historii; karta czyta wpisy z encji.
  async callWS() { return {}; }
}
