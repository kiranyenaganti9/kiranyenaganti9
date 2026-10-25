"""Local teaching example. No network, real payment, or product integration."""
from dataclasses import dataclass
import json

@dataclass(frozen=True)
class Record:
    request_id: str
    amount_cents: int
    version: int

@dataclass(frozen=True)
class Approval:
    request_id: str
    amount_cents: int
    version: int

class FakePaymentAdapter:
    def __init__(self, confirm=True):
        self.confirm = confirm
        self.effects = []

    def submit(self, record):
        if self.confirm:
            self.effects.append(record)
        return {'accepted': True}

    def observed(self, record):
        return record in self.effects

def execute(approval, current, adapter):
    audit = {'request_id': current.request_id,
             'approved_amount_cents': approval.amount_cents,
             'current_amount_cents': current.amount_cents,
             'approved_version': approval.version,
             'current_version': current.version}
    if (approval.request_id, approval.amount_cents, approval.version) != (
            current.request_id, current.amount_cents, current.version):
        return dict(audit, decision='HOLD', reason='Approval scope differs from current record', submitted=False, observed_effect=False)
    if current.amount_cents <= 0:
        return dict(audit, decision='HOLD', reason='Invalid amount', submitted=False, observed_effect=False)
    receipt = adapter.submit(current)
    observed = adapter.observed(current)
    return dict(audit, decision='COMPLETED' if observed else 'UNCONFIRMED',
                reason='Fake adapter state observed' if observed else 'API acceptance alone does not confirm an effect',
                submitted=receipt['accepted'], observed_effect=observed)

if __name__ == '__main__':
    approval = Approval('refund-1', 8000, 7)
    changed = execute(approval, Record('refund-1', 12000, 8), FakePaymentAdapter())
    accepted_only = execute(approval, Record('refund-1', 8000, 7), FakePaymentAdapter(confirm=False))
    confirmed = execute(approval, Record('refund-1', 8000, 7), FakePaymentAdapter())
    print(json.dumps({'changed_evidence': changed, 'acceptance_only': accepted_only, 'observed_fake_effect': confirmed}, indent=2))
