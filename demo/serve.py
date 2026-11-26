#!/usr/bin/env python3
"""Serve only the three public demo assets, never the repository or registry."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ASSETS = {'/': ('index.html', 'text/html'), '/index.html': ('index.html', 'text/html'),
          '/app.js': ('app.js', 'text/javascript'), '/style.css': ('style.css', 'text/css')}
ROOT = Path(__file__).resolve().parent


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        asset = ASSETS.get(urlsplit(self.path).path)
        if not asset:
            self.send_error(404)
            return
        data = (ROOT / asset[0]).read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', asset[1] + '; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Security-Policy', "default-src 'self'; connect-src 'none'; frame-ancestors 'none'")
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(data)


if __name__ == '__main__':
    print('Dispatch demo: http://127.0.0.1:4173 — local fixture; no real orders.', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 4173), Handler).serve_forever()
