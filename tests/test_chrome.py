"""Real Chrome lifecycle/CDP check. Runs in Linux CI; no Kane credits required."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
import unittest
from urllib.request import Request, urlopen

from skillforge.kane import browser, chrome_binary, page_identity


@unittest.skipUnless(chrome_binary(), 'Desktop Chrome is unavailable on this device.')
class ChromeIntegrationTests(unittest.TestCase):
    def test_fresh_owned_browser_page_identity_and_shutdown(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'<!doctype html><title>SkillForge CDP test</title><h1>Local fixture</h1>')
            def log_message(self, *_):
                pass
        app = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=app.serve_forever, daemon=True).start()
        self.addCleanup(app.server_close)
        self.addCleanup(app.shutdown)
        origin = f'http://127.0.0.1:{app.server_port}'
        with browser() as endpoint:
            with urlopen(Request(endpoint + '/json/new?' + origin, method='PUT'), timeout=3) as response:
                opened = json.load(response)
            identity = page_identity(endpoint, origin)
            self.assertEqual(identity['id'], opened['id'])
            self.assertEqual(page_identity(endpoint, origin), identity)
        with self.assertRaises(OSError):
            urlopen(endpoint + '/json/list', timeout=1)


if __name__ == '__main__':
    unittest.main()
