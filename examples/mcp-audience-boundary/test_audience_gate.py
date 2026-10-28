"""Fictional identities; no tokens, networking or real side effects."""
from dataclasses import replace
import unittest
from audience_gate import (CRM, TICKETS, SAMPLE_POLICY, ToolCall, TrustedClaims,
                           TrustedIdentity, admit, dispatch)
NOW = 1700000000
CLAIMS = TrustedClaims('user-1', 'https://auth.example.org/crm', CRM,
                       'tenant-17', frozenset({'records:read'}), NOW + 500)
CALL = ToolCall('account-agent', CRM, 'tenant-17', 'records:read', ('account-agent',))
IDENTITY = TrustedIdentity('user-1', 'account-agent')

class AudienceGateTests(unittest.TestCase):
    def result(self, claims=CLAIMS, call=CALL, identity=IDENTITY, policy=SAMPLE_POLICY, now=NOW):
        return admit(claims, call, policy, now, identity)

    def test_allow_direct(self):
        self.assertTrue(self.result().allow)

    def test_allow_delegated(self):
        c = replace(CALL, actor='support-agent', delegation_chain=('account-agent', 'support-agent'))
        self.assertTrue(self.result(call=c, identity=replace(IDENTITY, actor='support-agent')).allow)

    def test_unregistered_direct_actor(self):
        c = replace(CALL, actor='unknown', delegation_chain=('unknown',))
        self.assertEqual(self.result(call=c, identity=replace(IDENTITY, actor='unknown')).code, 'root_not_authorized')

    def test_changed_claim_subject(self):
        self.assertEqual(self.result(claims=replace(CLAIMS, subject='user-2')).code, 'subject_mismatch')

    def test_other_authenticated_subject_has_no_root(self):
        self.assertEqual(self.result(claims=replace(CLAIMS, subject='user-2'), identity=replace(IDENTITY, subject='user-2')).code, 'root_not_authorized')

    def test_actor_cannot_override_authenticated_context(self):
        self.assertEqual(self.result(call=replace(CALL, actor='support-agent')).code, 'caller_actor_mismatch')

    def test_empty_chain(self):
        self.assertEqual(self.result(call=replace(CALL, delegation_chain=())).code, 'actor_chain_mismatch')

    def test_cycle(self):
        self.assertEqual(self.result(call=replace(CALL, delegation_chain=('account-agent', 'support-agent', 'account-agent'))).code, 'delegation_cycle')

    def test_wrong_audience(self):
        self.assertEqual(self.result(claims=replace(CLAIMS, audience=TICKETS)).code, 'audience_mismatch')

    def test_wrong_issuer(self):
        self.assertEqual(self.result(claims=replace(CLAIMS, issuer='unknown')).code, 'issuer_mismatch')

    def test_wrong_tenant(self):
        self.assertEqual(self.result(call=replace(CALL, tenant='tenant-18')).code, 'tenant_mismatch')

    def test_expiry_boundary(self):
        self.assertEqual(self.result(now=CLAIMS.expires_at).code, 'expired')

    def test_missing_scope(self):
        self.assertEqual(self.result(claims=replace(CLAIMS, scopes=frozenset())).code, 'scope_missing')

    def test_unknown_resource(self):
        self.assertEqual(self.result(call=replace(CALL, resource='https://unknown.invalid')).code, 'unknown_resource')

    def test_unknown_operation(self):
        self.assertEqual(self.result(call=replace(CALL, operation='records:delete')).code, 'unknown_operation')

    def test_delegation_is_resource_specific(self):
        claims = replace(CLAIMS, issuer='https://auth.example.org/tickets', audience=TICKETS, scopes=frozenset({'tickets:create'}))
        call = replace(CALL, actor='support-agent', resource=TICKETS, operation='tickets:create', delegation_chain=('account-agent', 'support-agent'))
        self.assertEqual(self.result(claims, call, replace(IDENTITY, actor='support-agent')).code, 'delegation_denied')

    def test_allowed_dispatch_reaches_observed_sink_once(self):
        ledger = []
        decision, result = dispatch(CLAIMS, CALL, SAMPLE_POLICY, NOW, IDENTITY, lambda c: ledger.append(c.operation))
        self.assertTrue(decision.allow)
        self.assertEqual(ledger, ['records:read'])

    def test_denied_dispatch_does_not_reach_sink(self):
        ledger = []
        decision, result = dispatch(replace(CLAIMS, audience=TICKETS), CALL, SAMPLE_POLICY, NOW, IDENTITY, lambda c: ledger.append(c.operation))
        self.assertFalse(decision.allow)
        self.assertIsNone(result)
        self.assertEqual(ledger, [])

if __name__ == '__main__':
    unittest.main(verbosity=2)
