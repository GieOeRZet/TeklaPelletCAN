// Atrapa mostu natywnego (TPCNative) do testów interfejsu w przeglądarce. Odwzorowuje zasady z Kotlina (WriteGate, SecurityStore, Proxy):
// blokada zapisu, PIN, wygasanie po 5 min, cache ostatnich odczytów. Urządzenie = DemoDevice za /__demo.
(() => {
  const LS = k => { try { return localStorage.getItem('fn_' + k); } catch (e) { return null; } };
  const setLS = (k, v) => { try { if (v === null) localStorage.removeItem('fn_' + k); else localStorage.setItem('fn_' + k, v); } catch (e) { /* ignoruj */ } };
  const now = () => Date.now() + (window.__skew || 0);
  let unlockedAt = 0, open = false, fails = 0, lockUntil = 0;
  const cache = {};
  let device = '', base = '', wasOpen = false;
  const calls = window.__nativeCalls = [];
  const isOpen = () => { if (open && now() - unlockedAt >= 300000) open = false; return open; };
  const ro = /_(param_refresh|alarm_refresh|schedule_refresh|test_refresh|sdo_read|sdo_scan_stop)$/;
  const allowed = (m, p, b) => {
    if (m === 'GET') return true; if (p === '/api/v1/pair') return true;
    if (p === '/api/v1/call') { const s = /"service"\s*:\s*"([^"]+)"/.exec(b); return !!s && ro.test(s[1]); }
    return false;
  };
  const resp = (id, o) => setTimeout(() => window.__tpcResp && window.__tpcResp(id, o), 5);
  const ev = e => window.__tpcEvent && window.__tpcEvent(e);
  const lock = reason => { const was = isOpen(); open = false; wasOpen = false; if (was) { calls.push(['dropLevel']); fetchDev('POST', '/api/v1/call', '', '{"domain":"teklapelletcan","service":"tekla_estyma_unlock","data":{"pin":0}}'); ev({ type: 'locked', reason }); } };
  function fetchDev(method, path, query, body) {
    const x = new XMLHttpRequest(); x.open('POST', '/__demo', false);
    x.send(JSON.stringify({ method, path, query, authorization: '', body: body || '' })); return JSON.parse(x.responseText);
  }
  setInterval(() => {
    const o = isOpen();
    if (wasOpen && !o) { calls.push(['dropLevel']); fetchDev('POST', '/api/v1/call', '', '{"domain":"teklapelletcan","service":"tekla_estyma_unlock","data":{"pin":0}}'); ev({ type: 'locked', reason: 'idle' }); }
    wasOpen = o;
  }, 400);
  window.addEventListener('pointerdown', () => { if (isOpen()) unlockedAt = now(); }, true);

  window.TPCNative = {
    state: () => JSON.stringify({ hasPin: !!LS('pin'), bio: LS('bio') === '1', bioAsked: LS('bioasked') === '1', bioAvailable: window.__bioAvailable !== false, lockOnStart: LS('los') === '1',
      unlocked: isOpen(), remainingMs: isOpen() ? Math.max(0, 300000 - (now() - unlockedAt)) : 0, deviceName: device, demo: base === 'demo', version: '9.9.9+1', sdk: 35 }),
    getDevices: () => LS('devices') || '[]', saveDevices: j => setLS('devices', j),
    startDiscovery: () => { calls.push(['disc']); setTimeout(() => window.tpcDiscovered && window.tpcDiscovered({ name: 'tekla', host: '192.168.1.50', port: 80, id: 'A1B2C3D4E5F6', fw: '0.3.1' }), 150); },
    stopDiscovery: () => calls.push(['stopdisc']),
    ping: (id, b) => setTimeout(() => window.tpcPing && window.tpcPing(id, /192\.168\.1\.(50|77)/.test(b) ? { id: b.endsWith('77') ? 'FFEEDDCCBBAA' : 'A1B2C3D4E5F6', fw: '0.3.1' } : null), 80),
    selectDevice: (b, n) => { open = false; wasOpen = false; base = b; device = n; calls.push(['select', b, n]); },
    deselect: () => { open = false; device = ''; base = ''; },
    deviceSummary: b => { const c = cache['/api/v1/states']; return JSON.stringify(c && b !== 'demo' ? { at: c.at, body: c.body } : {}); },
    request: (id, method, pq, body) => setTimeout(() => {
      const path = pq.split('?')[0];
      if (!isOpen() && !allowed(method, path, body)) return resp(id, { status: 403, ctype: 'application/json', body: '{"ok":false,"error":"app_locked"}', cachedAt: 0 });
      if (window.__offline) {
        const c = cache[path];
        if (method === 'GET' && c) return resp(id, { status: 200, ctype: 'application/json', body: c.body, cachedAt: c.at });
        return resp(id, { status: 503, ctype: 'application/json', body: '{"ok":false,"error":"offline"}', cachedAt: 0 });
      }
      const r = fetchDev(method, path, pq.split('?')[1] || '', body);
      if (method === 'GET' && r.status === 200 && ['/api/v1/states', '/api/v1/info', '/api/v1/points', '/api/v1/config'].includes(path)) cache[path] = { body: r.body, at: now() };
      resp(id, { status: r.status, ctype: r.ctype, body: r.body, cachedAt: 0 });
    }, 3),
    setupPin: pin => { if (!/^\d{4,12}$/.test(pin)) return JSON.stringify({ ok: false, error: 'PIN: 4–12 cyfr' }); setLS('pin', pin); fails = 0; return JSON.stringify({ ok: true, error: '' }); },
    changePin: (a, b) => { if (LS('pin') !== a) return JSON.stringify({ ok: false, attemptsLeft: 4 }); setLS('pin', b); return JSON.stringify({ ok: true, error: '' }); },
    unlockPin: pin => {
      if (lockUntil > Date.now()) return JSON.stringify({ ok: false, lockedUntil: lockUntil, waitMs: lockUntil - Date.now() });
      if (pin === LS('pin')) { open = true; unlockedAt = now(); wasOpen = true; fails = 0; return JSON.stringify({ ok: true }); }
      fails++; if (fails >= 5) { lockUntil = Date.now() + 30000; return JSON.stringify({ ok: false, lockedUntil: lockUntil, waitMs: 30000 }); }
      return JSON.stringify({ ok: false, attemptsLeft: 5 - fails });
    },
    unlockBio: () => { calls.push(['bio']); setTimeout(() => { if (window.__bioResult) { open = true; unlockedAt = now(); wasOpen = true; ev({ type: 'bio', ok: true }); } else ev({ type: 'bio', ok: false, cancel: true }); }, 100); },
    lock: () => lock('user'), setBio: on => { setLS('bio', on ? '1' : '0'); setLS('bioasked', '1'); }, setLockOnStart: on => setLS('los', on ? '1' : '0'),
    clearCache: () => { for (const k of Object.keys(cache)) delete cache[k]; calls.push(['clearCache']); },
    resetSecurity: () => { setLS('pin', null); setLS('bio', null); open = false; calls.push(['reset']); },
    openOriginal: () => { if (!isOpen()) ev({ type: 'needs_unlock' }); else calls.push(['original']); },
    openDeviceSettings: () => { if (!isOpen()) ev({ type: 'needs_unlock' }); else calls.push(['settings']); },
    openSetup: () => calls.push(['setup']), openExternalUrl: u => calls.push(['ext', u]), now: () => now(),
  };
})();
