"""Sequential, in-memory teaching model; no external effects or real payments."""
class FakeService:
    def __init__(self):
        self.operations = {}
        self.effects = []

    def submit(self, key, amount, lose_reply=False):
        if key in self.operations:
            saved = self.operations[key]
            if saved['amount'] != amount:
                raise ValueError('Same operation key, different parameters')
            return dict(saved)
        if amount <= 0:
            raise ValueError('Amount must be positive')
        receipt = {'operation': key, 'amount': amount, 'status': 'COMPLETED'}
        self.effects.append(receipt)
        self.operations[key] = receipt
        if lose_reply:
            raise TimeoutError('Effect committed; reply lost')
        return dict(receipt)

    def lookup(self, key, unavailable=False):
        if unavailable:
            return {'status': 'UNKNOWN'}
        # Absence is not a durable guarantee that no delayed request can arrive.
        return dict(self.operations.get(key, {'status': 'UNKNOWN'}))

def reconcile(service, key, unavailable=False):
    result = service.lookup(key, unavailable)
    if result['status'] == 'COMPLETED':
        return {'decision': 'DO_NOT_REPEAT', 'evidence': result}
    return {'decision': 'RECONCILE_OR_ESCALATE', 'evidence': result}

if __name__ == '__main__':
    import json
    service = FakeService()
    try:
        service.submit('refund-42', 8000, lose_reply=True)
    except TimeoutError:
        pass
    print(json.dumps({'after_timeout': reconcile(service, 'refund-42'),
                      'readback_unavailable': reconcile(service, 'refund-42', True),
                      'fake_effects': len(service.effects)}, indent=2))
