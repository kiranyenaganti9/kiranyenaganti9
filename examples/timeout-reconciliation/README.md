# Timeout and reconciliation

Run `python3 -m unittest -v` and `python3 example.py` from this directory. Standard-library Python only; no network calls, external services or real payments.

This sequential teaching example commits a fake effect and then loses the reply. The caller can reconcile a known completion, preserve UNKNOWN when readback is unavailable, or retry with the same key under the fake service's contract. Reusing a key with changed parameters is rejected. A new key can duplicate the business action.

This is AI-assisted educational code, not a production idempotency implementation or validation of a research paper or DataGovernAI prototype. It lacks durable storage, atomic concurrency control, authenticated readback, expiration, crash recovery and distributed transactions. A real service must atomically couple deduplication to its effect, define retention/scope, and document status and retry semantics. A missing operation record does not prove that a delayed original request cannot still arrive. This example does not automatically retry unknown outcomes.

Actual local test output is in test-output.txt; demonstration output is example-output.json.
