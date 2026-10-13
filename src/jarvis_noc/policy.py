"""Política determinística. El modelo nunca decide sus propios permisos."""

from dataclasses import dataclass
from enum import StrEnum


class Decision(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    APPROVAL = "approval"


class Capability(StrEnum):
    READ_INCIDENT = "read_incident"
    READ_EVENT = "read_event"
    READ_ASSET = "read_asset"
    READ_RUNBOOK = "read_runbook"
    PROPOSE_ACTION = "propose_action"
    EXECUTE_ACTION = "execute_action"
    READ_SECRET = "read_secret"
    RAW_SHELL = "raw_shell"


@dataclass(frozen=True)
class PolicyContext:
    tenant_id: str
    target_tenant_id: str
    roles: frozenset[str]
    approval_verified: bool = False


def decide(capability: Capability, context: PolicyContext) -> Decision:
    """Default-deny; approval_verified must come from a trusted API, never a model."""
    if not context.tenant_id or context.tenant_id != context.target_tenant_id:
        return Decision.DENY
    if capability in {Capability.READ_SECRET, Capability.RAW_SHELL}:
        return Decision.DENY
    if not context.roles.intersection({"operator", "supervisor", "admin"}):
        return Decision.DENY
    if capability in {
        Capability.READ_INCIDENT,
        Capability.READ_EVENT,
        Capability.READ_ASSET,
        Capability.READ_RUNBOOK,
        Capability.PROPOSE_ACTION,
    }:
        return Decision.ALLOW
    if capability == Capability.EXECUTE_ACTION:
        if context.approval_verified and context.roles.intersection({"supervisor", "admin"}):
            return Decision.ALLOW
        return Decision.APPROVAL
    return Decision.DENY
