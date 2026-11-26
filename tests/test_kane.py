import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading

from skillforge.kane import parse_result, process, Kane, page_identity
from skillforge.core import ForgeError


def stream(status='passed', **fields):
    return '\n'.join(json.dumps(event) for event in [
        {'type': 'stream_start', 'surface': 'run', 'v': 1, 'cli_version': '0.10.9'},
        {'step': 1, 'status': 'done', 'remark': 'clicked', 'v': 1},
        {'type': 'run_end', 'status': status, 'v': 1, **fields},
    ])


class ParsingTests(unittest.TestCase):
    def test_complete_pass_with_zero_exit(self):
        self.assertTrue(parse_result(stream(), 0)['passed'])

    def test_missing_completion_nonzero_exit_and_malformed_stream_fail(self):
        cases = [('', 0), (stream(), 2), ('{"type":"stream_start","v":1}', 0),
                 (stream('failed'), 0), ('{"type":"run_end","status":"passed","v":1}', 0),
                 (stream().replace('"v": 1', '"v": 2'), 0),
                 (stream() + '\n' + json.dumps({'type': 'error', 'v': 1}), 0),
                 (stream() + '\n' + stream(), 0)]
        for stdout, code in cases:
            with self.subTest(stdout=stdout, code=code):
                self.assertFalse(parse_result(stdout, code)['passed'])

    def test_non_json_lines_and_unknown_events_are_tolerated(self):
        output = 'a diagnostic\n' + stream().replace(
            '{"step": 1', '{"type":"future_event","v":1}\n{"step": 1')
        self.assertTrue(parse_result(output, 0)['passed'])

    def test_analysis_requires_exact_explicit_true_verdicts(self):
        for values in [None, [], [True], [True, False], [1, True], ['true', True], [True, True, True]]:
            with self.subTest(values=values):
                output = stream(condition_results=values)
                self.assertFalse(parse_result(output, 0, expected_conditions=2)['passed'])
        self.assertTrue(parse_result(stream(condition_results=[True, True]), 0,
                                     expected_conditions=2)['passed'])


class ProcessTests(unittest.TestCase):
    def test_real_child_output_exit_and_literal_arguments(self):
        text = '$(touch /tmp/skillforge-should-not-exist); --headless'
        result = process([sys.executable, '-c',
                          'import sys; print(sys.argv[1]); print("diagnostic", file=sys.stderr)', text], 5)
        self.assertEqual(result['exit_code'], 0)
        self.assertEqual(result['stdout'].strip(), text)
        self.assertIn('diagnostic', result['stderr'])

    def test_timeout_terminates_child(self):
        result = process([sys.executable, '-c', 'import time; time.sleep(10)'], 0.1)
        self.assertTrue(result['timed_out'])
        self.assertNotEqual(result['exit_code'], 0)

    def test_missing_binary_returns_failure(self):
        result = process(['/skillforge/no-such-program'], 1)
        self.assertNotEqual(result['exit_code'], 0)

    def test_timeout_kills_pipe_inheriting_descendant_after_leader_exits(self):
        child = 'import time; time.sleep(4)'
        parent = 'import subprocess,sys; subprocess.Popen([sys.executable,"-c",sys.argv[1]])'
        started = time.monotonic()
        result = process([sys.executable, '-c', parent, child], .1)
        self.assertTrue(result['timed_out'])
        self.assertLess(time.monotonic() - started, 2)

    def test_adapter_uses_distinct_action_and_analyzer_on_same_browser(self):
        with tempfile.TemporaryDirectory() as folder:
            fixture = Path(folder) / 'fixture.py'
            log = Path(folder) / 'arguments.jsonl'
            fixture.write_text('''import json, sys
from pathlib import Path
with Path(sys.argv[1]).open('a') as f: f.write(json.dumps(sys.argv[2:]) + '\\n')
print(json.dumps({'type':'stream_start','surface':'run','v':1}))
event = {'type':'run_end','status':'passed','v':1}
if '--analyzer-only' in sys.argv:
    event['condition_results'] = [True] * sys.argv.count('--condition')
print(json.dumps(event))
''')
            kane = Kane(command=[sys.executable, str(fixture), str(log)],
                        inspect_page=lambda *_: {'id': 'same-page', 'url': 'http://127.0.0.1:4173/'})
            result = kane.execute({'url': 'http://127.0.0.1:4173'}, 'Ship order ORD-104',
                                  ['Shipment says Shipped'], 'http://127.0.0.1:9222')
            self.assertTrue(result['passed'])
            calls = [json.loads(line) for line in log.read_text().splitlines()]
            self.assertEqual(len(calls), 2)
            self.assertNotIn('--analyzer-only', calls[0])
            self.assertIn('--analyzer-only', calls[1])
            self.assertEqual(calls[0][calls[0].index('--cdp-endpoint') + 1],
                             calls[1][calls[1].index('--cdp-endpoint') + 1])
            self.assertEqual(calls[1].count('--condition'), 2)  # target-origin check too


class PageIdentityTests(unittest.TestCase):
    def test_one_authorized_page_is_required_and_unused_blank_tabs_are_closed(self):
        pages = [{'type': 'page', 'id': 'blank', 'url': 'about:blank'},
                 {'type': 'page', 'id': 'task', 'url': 'http://127.0.0.1:4173/orders'}]
        closed = set()
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path.startswith('/json/close/'):
                    name = self.path.rsplit('/', 1)[1]
                    if name in closed:
                        self.send_error(404)
                        return
                    closed.add(name)
                    data = b'closed'
                else:
                    data = json.dumps(pages).encode()
                    # Chrome may expose a stale target once after accepting close.
                    pages[:] = [p for p in pages if p['id'] not in closed]
                self.send_response(200)
                self.end_headers()
                self.wfile.write(data)
            def log_message(self, *_):
                pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        endpoint = f'http://127.0.0.1:{server.server_port}'
        self.assertEqual(page_identity(endpoint, 'http://127.0.0.1:4173')['id'], 'task')
        self.assertEqual(page_identity(endpoint, 'http://127.0.0.1:4173')['id'], 'task')
        self.assertEqual(len(pages), 1)
        pages.append({'type': 'page', 'id': 'other', 'url': 'http://127.0.0.1:4173/other'})
        with self.assertRaises(ForgeError):
            page_identity(endpoint, 'http://127.0.0.1:4173')
        pages[:] = [{'type': 'page', 'id': 'outside', 'url': 'https://example.com'}]
        with self.assertRaises(ForgeError):
            page_identity(endpoint, 'http://127.0.0.1:4173')


if __name__ == '__main__':
    unittest.main()
