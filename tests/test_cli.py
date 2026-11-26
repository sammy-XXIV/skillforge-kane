import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_core import contract


ROOT = Path(__file__).resolve().parents[1]


class CLITests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.env = os.environ | {'SKILLFORGE_HOME': str(self.folder / 'registry')}
        self.spec = self.folder / 'contract.json'
        self.spec.write_text(json.dumps(contract()))
        self.objective = self.folder / 'objective.md'
        self.objective.write_text('Open {{order_id}} and click Mark shipped.')

    def invoke(self, *args):
        proc = subprocess.run([sys.executable, str(ROOT / 'forge.py'), *args],
                              capture_output=True, text=True, env=self.env)
        self.assertNotIn('Traceback', proc.stderr)
        return proc.returncode, json.loads(proc.stdout)

    def test_create_author_discover_and_read_frozen_contract_in_new_processes(self):
        code, result = self.invoke('create', str(self.spec))
        self.assertEqual(code, 0)
        self.assertEqual(result['status'], 'draft')
        code, result = self.invoke('author', 'ship-order', '--objective', str(self.objective))
        self.assertEqual(code, 0)
        self.assertEqual(result['status'], 'candidate')
        code, result = self.invoke('find', 'ship')
        self.assertEqual(result, [])
        code, result = self.invoke('list', '--all')
        self.assertEqual(result[0]['status'], 'candidate')
        code, result = self.invoke('repair', 'ship-order')
        self.assertEqual(result['contract']['conditions'], contract()['conditions'])

    def test_refusals_are_machine_readable(self):
        code, result = self.invoke('run', '../escape', '--set', 'order_id=ORD-104')
        self.assertEqual(code, 2)
        self.assertFalse(result['ok'])

    def test_invalid_json_is_machine_readable(self):
        self.spec.write_text('{')
        code, result = self.invoke('create', str(self.spec))
        self.assertEqual(code, 2)
        self.assertIn('error', result)

    def test_malformed_contract_fields_are_json_refusals(self):
        for changes in [{'url': 123}, {'url': 'https://[broken'}, {'variables': []},
                        {'variables': {'order_id': None}}, {'conditions': [12]},
                        {'keywords': [None]}, {'id': None}]:
            with self.subTest(changes=changes):
                self.spec.write_text(json.dumps(contract() | changes))
                code, result = self.invoke('create', str(self.spec))
                self.assertEqual(code, 2)
                self.assertFalse(result['ok'])

    def test_no_live_mock_mode_exists(self):
        proc = subprocess.run([sys.executable, str(ROOT / 'forge.py'), 'verify', '--help'],
                              capture_output=True, text=True, env=self.env)
        self.assertNotIn('--mock', proc.stdout)
        self.assertNotIn('--fake', proc.stdout)


if __name__ == '__main__':
    unittest.main()
