// Tryb DEMO w aplikacji: żądania /api/ z tej samej strony trafiają do wirtualnego urządzenia (rdzeń firmware przez JNI),
// bo WebView nie przekazuje ciała żądań POST do shouldInterceptRequest. Wstrzykiwane przed skryptami strony.
(function () {
  if (window.__tpcDemoFetch || !window.TPCDemo) return;
  window.__tpcDemoFetch = true;
  const realFetch = window.fetch.bind(window);
  function headerOf(init, name) {
    const h = init && init.headers; if (!h) return '';
    if (typeof h.get === 'function') return h.get(name) || '';
    for (const k of Object.keys(h)) if (k.toLowerCase() === name.toLowerCase()) return String(h[k]);
    return '';
  }
  window.fetch = async function (input, init) {
    const url = new URL(typeof input === 'string' ? input : (input && input.url) || String(input), location.href);
    if (url.origin !== location.origin || !url.pathname.startsWith('/api/')) return realFetch(input, init);
    const method = ((init && init.method) || (input && input.method) || 'GET').toUpperCase();
    let body = '';
    const b = init && init.body;
    if (typeof b === 'string') body = b;
    const raw = window.TPCDemo.request(method, url.pathname, url.search.replace(/^\?/, ''), headerOf(init, 'Authorization'), body);
    const r = JSON.parse(raw);
    return new Response(r.status === 204 ? null : r.body, { status: r.status, headers: { 'Content-Type': r.ctype || 'application/json' } });
  };
})();
