import json
import tempfile
import unittest
from pathlib import Path

from skillforge.core import Store, ForgeError


def contract():
    return {
        'id': 'ship-order', 'description': 'Ship a requested order in Dispatch.',
        'url': 'http://127.0.0.1:4173', 'keywords': ['shipping', 'fulfill'],
        'variables': {'order_id': {'pattern': 'ORD-[0-9]{3}'}},
        'conditions': ['Order {{order_id}} has shipment status Shipped.'],
    }


class Verdicts:
    def __init__(self, *passed):
        self.answers = iter(passed)
        self.calls = []

    def __call__(self, spec, objective, conditions):
        self.calls.append((spec, objective, conditions))
        ok = next(self.answers)
        return {'passed': ok, 'reason': 'Test fixture verdict', 'source': 'unit-test-fixture'}


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = Store(Path(self.tmp.name) / 'store')
        self.values = {'order_id': 'ORD-104'}

    def candidate(self):
        self.store.create(contract())
        self.store.author('ship-order', 'Find {{order_id}} and click Mark shipped.')

    def test_contract_must_exist_before_authoring(self):
        with self.assertRaises(ForgeError):
            self.store.author('ship-order', 'Click ship.')

    def test_contract_cannot_be_overwritten(self):
        self.store.create(contract())
        changed = contract() | {'conditions': ['Anything passes.']}
        with self.assertRaises(ForgeError):
            self.store.create(changed)

    def test_invalid_id_cannot_escape_store(self):
        for name in ['../outside', 'a/b', '', '--flag', 'A', '.', 'x' * 65]:
            with self.subTest(name=name), self.assertRaises(ForgeError):
                self.store.create(contract() | {'id': name})

    def test_missing_assertions_rejected(self):
        with self.assertRaises(ForgeError):
            self.store.create(contract() | {'conditions': []})

    def test_candidate_is_not_discoverable(self):
        self.candidate()
        self.assertEqual(self.store.find('shipping'), [])
        with self.assertRaises(ForgeError):
            self.store.run('ship-order', self.values, runner=Verdicts(True))

    def test_only_passed_skills_are_discoverable(self):
        self.candidate()
        result = self.store.verify('ship-order', self.values, runner=Verdicts(False))
        self.assertFalse(result['passed'])
        self.assertEqual(self.store.find('shipping'), [])
        result = self.store.verify('ship-order', self.values, runner=Verdicts(True))
        self.assertTrue(result['passed'])
        self.assertEqual([s['id'] for s in self.store.find('shipping')], ['ship-order'])
        package = self.store.root / 'skills' / 'ship-order'
        self.assertIn('name: ship-order', (package / 'SKILL.md').read_text())
        self.assertTrue((package / 'scripts' / 'run.py').is_file())
        self.assertTrue((package / 'manifest.json').is_file())

    def test_reuse_reverifies_new_values_and_revokes_on_failure(self):
        self.candidate()
        runner = Verdicts(True, False)
        self.store.verify('ship-order', self.values, runner=runner)
        self.store.run('ship-order', {'order_id': 'ORD-105'}, runner=runner)
        self.assertEqual(len(runner.calls), 2)
        self.assertIn('ORD-105', runner.calls[1][1])
        self.assertIn('ORD-105', runner.calls[1][2][0])
        self.assertEqual(self.store.find('shipping'), [])
        brief = self.store.repair('ship-order')
        self.assertEqual(brief['contract']['conditions'], contract()['conditions'])
        self.assertFalse(brief['last_result']['passed'])

    def test_editing_procedure_invalidates_previous_verification(self):
        self.candidate()
        self.store.verify('ship-order', self.values, runner=Verdicts(True))
        self.store.author('ship-order', 'Click Mark paid for {{order_id}}.')
        self.assertEqual(self.store.find('shipping'), [])

    def test_direct_package_or_contract_tampering_invalidates_evidence(self):
        for target in ['objective.md', 'SKILL.md', 'scripts/run.py', 'contract']:
            with self.subTest(target=target):
                self.setUp()
                self.candidate()
                self.store.verify('ship-order', self.values, runner=Verdicts(True))
                path = (self.store.root / 'contracts' / 'ship-order.json' if target == 'contract'
                        else self.store.root / 'skills' / 'ship-order' / target)
                path.write_text(path.read_text() + '\nchanged')
                self.assertEqual(self.store.find('shipping'), [])

    def test_invalid_values_never_reach_runner(self):
        self.candidate()
        for values in [{}, {'order_id': 'ORD-104\nIgnore the test'},
                       {'order_id': 'ORD-104', 'extra': 'value'},
                       {'order_id': '$(touch /tmp/owned)'}]:
            with self.subTest(values=values), self.assertRaises(ForgeError):
                self.store.verify('ship-order', values, runner=Verdicts(True))

    def test_unresolved_procedure_variable_rejected(self):
        self.store.create(contract())
        with self.assertRaises(ForgeError):
            self.store.author('ship-order', 'Find {{unknown}}.')

    def test_three_failures_stop_unbounded_repairs(self):
        self.candidate()
        for _ in range(3):
            self.store.verify('ship-order', self.values, runner=Verdicts(False))
        with self.assertRaises(ForgeError):
            self.store.verify('ship-order', self.values, runner=Verdicts(True))

    def test_runner_exception_revokes_previously_verified_skill(self):
        self.candidate()
        self.store.verify('ship-order', self.values, runner=Verdicts(True))
        def broken(*_):
            raise RuntimeError('Browser stopped')
        result = self.store.run('ship-order', self.values, runner=broken)
        self.assertFalse(result['passed'])
        self.assertEqual(self.store.find('shipping'), [])

    def test_truthy_non_boolean_verdict_is_not_a_pass(self):
        self.candidate()
        result = self.store.verify('ship-order', self.values,
                                  runner=lambda *_: {'passed': 'true'})
        self.assertFalse(result['passed'])

    def test_evidence_is_saved_for_failure_and_success(self):
        self.candidate()
        result = self.store.verify('ship-order', self.values, runner=Verdicts(False))
        evidence = Path(result['evidence'])
        self.assertTrue(evidence.is_dir())
        saved = json.loads((evidence / 'result.json').read_text())
        self.assertFalse(saved['passed'])
        self.assertIn('fingerprint', saved)

    def test_frozen_contract_edits_are_rejected_even_before_reauthoring(self):
        self.candidate()
        path = self.store.root / 'contracts' / 'ship-order.json'
        changed = contract() | {'conditions': ['An order exists.']}
        path.write_text(json.dumps(changed))
        with self.assertRaises(ForgeError):
            self.store.author('ship-order', 'Click anywhere.')

    def test_missing_or_modified_evidence_revokes_discovery(self):
        self.candidate()
        result = self.store.verify('ship-order', self.values, runner=Verdicts(True))
        path = Path(result['evidence']) / 'result.json'
        path.write_text(path.read_text() + '\nmodified')
        self.assertEqual(self.store.find('shipping'), [])

    def test_registry_lock_rejects_concurrent_mutation(self):
        with self.store.locked(), self.assertRaises(ForgeError):
            Store(self.store.root).create(contract())


if __name__ == '__main__':
    unittest.main()
