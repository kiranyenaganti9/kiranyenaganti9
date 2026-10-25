import unittest
from example import Approval, Record, FakePaymentAdapter, execute

class ScopeTests(unittest.TestCase):
    def test_amount_change_holds_without_effect(self):
        adapter = FakePaymentAdapter()
        result = execute(Approval('a', 8000, 7), Record('a', 12000, 7), adapter)
        self.assertEqual(result['decision'], 'HOLD')
        self.assertFalse(result['submitted'])
        self.assertEqual(adapter.effects, [])

    def test_version_change_holds_even_when_amount_matches(self):
        adapter = FakePaymentAdapter()
        result = execute(Approval('a', 8000, 7), Record('a', 8000, 8), adapter)
        self.assertEqual(result['decision'], 'HOLD')
        self.assertEqual(adapter.effects, [])

    def test_other_request_cannot_reuse_approval(self):
        adapter = FakePaymentAdapter()
        result = execute(Approval('a', 8000, 7), Record('b', 8000, 7), adapter)
        self.assertEqual(result['decision'], 'HOLD')
        self.assertEqual(adapter.effects, [])

    def test_acceptance_does_not_prove_effect(self):
        adapter = FakePaymentAdapter(confirm=False)
        result = execute(Approval('a', 8000, 7), Record('a', 8000, 7), adapter)
        self.assertTrue(result['submitted'])
        self.assertFalse(result['observed_effect'])
        self.assertEqual(result['decision'], 'UNCONFIRMED')

    def test_matching_scope_observes_fake_effect(self):
        adapter = FakePaymentAdapter()
        record = Record('a', 8000, 7)
        result = execute(Approval('a', 8000, 7), record, adapter)
        self.assertEqual(result['decision'], 'COMPLETED')
        self.assertEqual(adapter.effects, [record])

    def test_invalid_amount_never_submits(self):
        adapter = FakePaymentAdapter()
        result = execute(Approval('a', -1, 7), Record('a', -1, 7), adapter)
        self.assertEqual(result['decision'], 'HOLD')
        self.assertEqual(adapter.effects, [])

if __name__ == '__main__':
    unittest.main()
