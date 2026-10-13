from jarvis_noc.policy import Capability, Decision, PolicyContext, decide


def context(**changes):
    values = {"tenant_id": "a", "target_tenant_id": "a", "roles": frozenset({"operator"})}
    values.update(changes)
    return PolicyContext(**values)


def test_cross_tenant_access_is_denied():
    assert decide(Capability.READ_INCIDENT, context(target_tenant_id="b")) == Decision.DENY


def test_secrets_and_shell_are_always_denied():
    assert decide(Capability.READ_SECRET, context(roles=frozenset({"admin"}))) == Decision.DENY
    assert decide(Capability.RAW_SHELL, context(roles=frozenset({"admin"}))) == Decision.DENY


def test_execution_requires_verified_approval_and_privileged_role():
    assert decide(Capability.EXECUTE_ACTION, context()) == Decision.APPROVAL
    assert decide(Capability.EXECUTE_ACTION, context(approval_verified=True)) == Decision.APPROVAL
    assert decide(Capability.EXECUTE_ACTION, context(roles=frozenset({"supervisor"}), approval_verified=True)) == Decision.ALLOW


def test_unknown_role_cannot_read():
    assert decide(Capability.READ_INCIDENT, context(roles=frozenset({"guest"}))) == Decision.DENY
