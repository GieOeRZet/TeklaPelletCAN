#!/usr/bin/env python3
"""Atrapa urzadzenia do testow karty w przegladarce: serwuje web/ i API z plikow JSON."""
import json, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent
STATES = Path(__file__).resolve().parent / "states.json"
CALLS = []


class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(WEB), **k)

    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path.startswith("/api/v1/states"):
            return self._json(json.loads(STATES.read_text()))
        if self.path.startswith("/api/v1/calls"):
            return self._json(CALLS)
        return super().do_GET()

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        if self.path.startswith("/api/v1/call"):
            CALLS.append(body)
            return self._json({"ok": True})
        self._json({"error": "nie ma"}, 404)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8099
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
