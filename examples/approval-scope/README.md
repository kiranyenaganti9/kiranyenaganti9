# Approval scope and observed completion

A small educational example prepared for Kiran Yenaganti's research communication. It uses Python's standard library and a fake, in-memory payment adapter. It sends no payments and makes no network requests.

Run `python3 example.py` for three contrasting outcomes and `python3 -m unittest -v` for the checks, from this directory.

An approval records a request, amount and version. A mismatch holds the action before calling the adapter. For matching scope, an accepted API response and an observed effect remain separate fields. When acceptance occurs without an effect in the fake adapter, the result remains UNCONFIRMED.

## Limits

This is a teaching model, not a production control or validation of any manuscript, benchmark or unreleased product. The in-memory observation is a synthetic fixture, not independent verification. It does not implement authentication, signed evidence, atomic compare-and-act, expiration, persistence, concurrency, replay protection, idempotency or crash recovery. A real integration requires those controls and independent evaluation. Checking state before a real action without an atomic boundary can introduce a race; this example does not solve that problem.

Status: locally implemented and tested; publicly shared as educational code. AI-assisted engineering. See test-output.txt and example-output.json for actual run evidence.
