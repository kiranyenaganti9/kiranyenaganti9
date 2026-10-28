# MCP audience boundary: educational contribution

Kiran Yenaganti / DataGovernAI. Prepared with material AI assistance, October 28, 2026.

## Files and running

- `audience_gate.py`: typed policy decision function, trusted identity context and local dispatch wrapper.
- `test_audience_gate.py`: 18 standard-library tests, including observed local dispatch.
- `Medium_2026-10-28.md`: editorial source for the companion technical note.
- `MCP_Audience_Boundary.svg`: editable conceptual figure.
- `TEST_RESULTS.txt`: actual local run output.

Run `python3 -m unittest -v test_audience_gate.py` from this folder. No external libraries, real credentials or network calls are needed.

## What is original here

This package contributes an educational implementation, a concrete delegation scenario and tests exposing assumptions about caller identity and dispatch. Audience validation, least privilege and token-passthrough restrictions are existing MCP/OAuth requirements, not new discoveries. No literature-wide novelty claim is made.

The revision adds explicit authenticated caller context, authorized root agents per subject, resource-specific delegation and cycle checks. Positive and negative dispatch tests observe an independent in-memory list supplied as the destination. The original uploaded archive is retained separately for provenance.

## Trust boundary and limitations

`TrustedClaims` must be created only after appropriate token validation. `TrustedIdentity` must come from an authenticated integration, not agent arguments. Neither class validates signatures or proves trust. Python callers can construct these records; this example does not isolate them from malicious code.

The wrapper honors its decision before invoking the injected transport, but direct access to that transport bypasses it. There is no live MCP server, network enforcement, token exchange, refresh/revocation, durable audit store, concurrency protection or independent deployment evaluation. It accepts one exact audience identifier and intentionally does not implement every OAuth audience representation.

No additional license grant is made. This repository contains the educational source; publication does not imply production validation.

Primary sources are linked in the technical note. The illustration shows the audience check only; ALLOW remains subject to the other checks.
