"""Educational, local tool-dispatch policy. NOT an OAuth/JWT verifier.

Inputs are TRUSTED, PRE-VALIDATED claims created by an external identity
verifier, not user-supplied dictionaries, model completions, or tool arguments.
No secret/token processing, network enforcement, or production guarantees.
"""

from dataclasses import dataclass
from typing import FrozenSet, Mapping, Tuple


@dataclass(frozen=True)
class TrustedClaims:
    subject: str
    issuer: str
    audience: str
    tenant: str
    scopes: FrozenSet[str]
    expires_at: int


@dataclass(frozen=True)
class TrustedIdentity:
    """Authenticated caller context, supplied by trusted integration code."""
    subject: str
    actor: str


@dataclass(frozen=True)
class ToolCall:
    actor: str
    resource: str
    tenant: str
    operation: str
    delegation_chain: Tuple[str, ...]


@dataclass(frozen=True)
class Policy:
    # Configured by the operator: exact resource identifier -> trusted issuer.
    trusted_issuer_by_resource: Mapping[str, str]
    # (resource, operation) -> scope required to perform the operation.
    required_scope_by_action: Mapping[Tuple[str, str], str]
    # Subject -> permitted initiating agents. No default access.
    roots_by_subject: Mapping[str, FrozenSet[str]]
    # (subject, parent, child, resource) -> allowed delegated operations.
    delegation_caps: Mapping[Tuple[str, str, str, str], FrozenSet[str]]


@dataclass(frozen=True)
class Decision:
    allow: bool
    code: str


def admit(claims: TrustedClaims, call: ToolCall, policy: Policy, now: int, identity: TrustedIdentity) -> Decision:
    """Pure decision only. A real dispatcher MUST enforce the returned result.

    Intentionally requires a single exact audience. Real OAuth deployments may
    use opaque tokens, mapped identifiers, or multiple audiences: validate all
    that at the resource server using the established protocol stack instead.
    """
    if claims.subject != identity.subject:
        return Decision(False, "subject_mismatch")
    if call.actor != identity.actor:
        return Decision(False, "caller_actor_mismatch")
    if not call.delegation_chain or call.delegation_chain[-1] != call.actor:
        return Decision(False, "actor_chain_mismatch")
    if call.delegation_chain[0] not in policy.roots_by_subject.get(claims.subject, frozenset()):
        return Decision(False, "root_not_authorized")
    if len(set(call.delegation_chain)) != len(call.delegation_chain):
        return Decision(False, "delegation_cycle")
    if call.resource not in policy.trusted_issuer_by_resource:
        return Decision(False, "unknown_resource")
    if now >= claims.expires_at:
        return Decision(False, "expired")
    if claims.issuer != policy.trusted_issuer_by_resource[call.resource]:
        return Decision(False, "issuer_mismatch")
    if claims.audience != call.resource:
        return Decision(False, "audience_mismatch")
    if claims.tenant != call.tenant:
        return Decision(False, "tenant_mismatch")
    scope = policy.required_scope_by_action.get((call.resource, call.operation))
    if scope is None:
        return Decision(False, "unknown_operation")
    if scope not in claims.scopes:
        return Decision(False, "scope_missing")
    for parent, child in zip(call.delegation_chain, call.delegation_chain[1:]):
        if call.operation not in policy.delegation_caps.get((claims.subject, parent, child, call.resource), frozenset()):
            return Decision(False, "delegation_denied")
    return Decision(True, "allow")


# Fixed fictional test configuration. No real endpoints, secrets, or identities.
CRM = "https://mcp.example.org/crm"
TICKETS = "https://mcp.example.org/tickets"
SAMPLE_POLICY = Policy(
    trusted_issuer_by_resource={CRM: "https://auth.example.org/crm", TICKETS: "https://auth.example.org/tickets"},
    required_scope_by_action={(CRM, "records:read"): "records:read", (TICKETS, "tickets:create"): "tickets:create"},
    roots_by_subject={"user-1": frozenset({"account-agent"})},
    delegation_caps={("user-1", "account-agent", "support-agent", CRM): frozenset({"records:read"})},
)


def dispatch(claims, call, policy, now, identity, transport):
    """Enforce this local decision by calling the supplied transport only on allow.

    A caller that can invoke transport directly can bypass this wrapper. This
    function does not establish a network or process security boundary.
    """
    decision = admit(claims, call, policy, now, identity)
    if not decision.allow:
        return decision, None
    return decision, transport(call)
