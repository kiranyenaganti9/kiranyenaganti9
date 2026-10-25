import unittest
from example import FakeService, reconcile

class RetryTests(unittest.TestCase):
    def test_timeout_can_follow_a_committed_effect(self):
        service = FakeService()
        with self.assertRaises(TimeoutError):
            service.submit('a', 8000, lose_reply=True)
        self.assertEqual(len(service.effects), 1)
        self.assertEqual(reconcile(service, 'a')['decision'], 'DO_NOT_REPEAT')

    def test_same_key_same_parameters_does_not_duplicate(self):
        service = FakeService()
        with self.assertRaises(TimeoutError):
            service.submit('a', 8000, lose_reply=True)
        self.assertEqual(service.submit('a', 8000)['status'], 'COMPLETED')
        self.assertEqual(len(service.effects), 1)

    def test_new_key_can_duplicate_the_business_action(self):
        service = FakeService()
        service.submit('a', 8000)
        service.submit('b', 8000)
        self.assertEqual(len(service.effects), 2)

    def test_changed_parameters_rejected(self):
        service = FakeService()
        service.submit('a', 8000)
        with self.assertRaises(ValueError):
            service.submit('a', 12000)
        self.assertEqual(len(service.effects), 1)

    def test_unavailable_readback_preserves_uncertainty(self):
        service = FakeService()
        service.submit('a', 8000)
        self.assertEqual(reconcile(service, 'a', True)['decision'], 'RECONCILE_OR_ESCALATE')

    def test_absent_record_is_not_proof_of_safe_retry(self):
        self.assertEqual(reconcile(FakeService(), 'missing')['decision'], 'RECONCILE_OR_ESCALATE')

if __name__ == '__main__':
    unittest.main()
