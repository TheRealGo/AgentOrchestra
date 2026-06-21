from __future__ import annotations

from dataclasses import dataclass

from .autonomy_policy import ActionClassification, CleanupClassification, classify_action, classify_service_e2e_approval_prompt


TRUE_USER_NEEDED_REASONS = frozenset(
    {
        "credential",
        "account_provider_setup",
        "payment",
        "physical_device",
        "production_public_release_approval",
        "destructive_irreversible",
        "destructive_irreversible_action",
        "legal_security_judgment",
        "scope_expansion",
    }
)


@dataclass(frozen=True)
class InterventionClassification:
    disposition: str
    reason: str
    ledger_status: str
    zero_issue_blocker: bool
    rationale: str


def classify_intervention(
    *,
    reason: str,
    in_edit_root: bool,
    low_risk: bool,
    external_action: bool = False,
    action: str | None = None,
    command: str | None = None,
    current_run_scope: str = "",
    process_identity_known: bool = False,
    run_owned: bool = False,
    port_owned: bool = False,
    compose_project: str | None = None,
) -> InterventionClassification:
    normalized = reason.strip().casefold().replace("-", "_").replace(" ", "_")
    policy = _policy_classification(
        action=action,
        command=command,
        current_run_scope=current_run_scope,
        process_identity_known=process_identity_known,
        run_owned=run_owned,
        port_owned=port_owned,
        compose_project=compose_project,
    )
    if normalized in TRUE_USER_NEEDED_REASONS or external_action:
        return InterventionClassification(
            disposition="needs_user",
            reason=normalized,
            ledger_status="needs_user",
            zero_issue_blocker=True,
            rationale="requires concrete external user action outside AgentTeam autonomy",
        )
    if normalized in {"approval_prompt", "codex_approval_prompt", "sandbox_approval_prompt"}:
        if policy is not None:
            return _from_policy_approval_prompt(normalized, policy)
        if in_edit_root and low_risk:
            return InterventionClassification(
                disposition="autonomy_blocker",
                reason=normalized,
                ledger_status="open",
                zero_issue_blocker=True,
                rationale="low-risk in-scope work should continue autonomously or remain an unresolved SelfE2E issue",
            )
        return InterventionClassification(
            disposition="blocked",
            reason=normalized,
            ledger_status="blocked",
            zero_issue_blocker=True,
            rationale="approval prompt could not be classified as low-risk in-scope work",
        )
    return InterventionClassification(
        disposition="needs_classification",
        reason=normalized or "unknown",
        ledger_status="open",
        zero_issue_blocker=True,
        rationale="intervention must be classified before zero-issue finalization",
    )


def _policy_classification(
    *,
    action: str | None,
    command: str | None,
    current_run_scope: str,
    process_identity_known: bool,
    run_owned: bool,
    port_owned: bool,
    compose_project: str | None,
) -> ActionClassification | CleanupClassification | None:
    if command:
        return classify_service_e2e_approval_prompt(
            command,
            current_run_scope=current_run_scope,
            process_identity_known=process_identity_known,
            run_owned=run_owned,
            port_owned=port_owned,
            compose_project=compose_project,
        )
    if action:
        return classify_action(action)
    return None


def _from_policy_approval_prompt(
    reason: str,
    policy: ActionClassification | CleanupClassification,
) -> InterventionClassification:
    category = policy.category
    if category in {"agent_autonomous", "run_scoped_cleanup"}:
        return InterventionClassification(
            disposition="autonomy_blocker",
            reason=reason,
            ledger_status="open",
            zero_issue_blocker=True,
            rationale=(
                "approval prompt interrupted work classified by autonomy_policy "
                f"as {category}; this must be fixed or kept as SelfE2E evidence"
            ),
        )
    if category == "true_user_needed":
        return InterventionClassification(
            disposition="needs_user",
            reason=reason,
            ledger_status="needs_user",
            zero_issue_blocker=True,
            rationale=policy.rationale,
        )
    return InterventionClassification(
        disposition="blocked",
        reason=reason,
        ledger_status=policy.ledger_status,
        zero_issue_blocker=True,
        rationale=policy.rationale,
    )
