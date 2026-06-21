from __future__ import annotations

from dataclasses import dataclass
import shlex


LOW_RISK_IN_SCOPE_ACTIONS = frozenset(
    {
        "copy_local_edit",
        "test_file_edit",
        "contract_file_edit",
        "runtime_helper_edit",
        "unittest",
        "py_compile",
        "git_diff_check",
        "dev_server_restart",
        "pane_recovery",
        "bounded_approval_retry",
        "browser_evidence_rerun",
        "local_browser_verification",
        "chromium_firefox_matrix",
        "local_simulator_verification",
        "ios_simulator_smoke",
        "ios_build_smoke",
        "mobile_route_evidence",
        "mobile_interactive_evidence",
    }
)
TRUE_USER_NEEDED_ACTIONS = frozenset(
    {
        "credential",
        "account_provider_setup",
        "payment",
        "physical_device",
        "production_public_release_approval",
        "destructive_irreversible",
        "legal_security_judgment",
        "scope_expansion",
    }
)


@dataclass(frozen=True)
class ActionClassification:
    action: str
    category: str
    ledger_status: str
    rationale: str


@dataclass(frozen=True)
class CleanupClassification:
    resource: str
    category: str
    ledger_status: str
    allowed: bool
    rationale: str


@dataclass(frozen=True)
class ServiceE2EApprovalReplayObservation:
    defect_id: str
    command: str
    expected_category: str
    current_run_scope: str = "too_restore_e2e_20260621"
    process_identity_known: bool = True
    port_owned: bool = True


_REPLAY = ServiceE2EApprovalReplayObservation
SERVICE_E2E_APPROVAL_REPLAY_OBSERVATIONS: tuple[ServiceE2EApprovalReplayObservation, ...] = (
    _REPLAY("chromium-firefox-matrix", "pnpm test:chromium-firefox", "agent_autonomous"),
    _REPLAY("ios-simulator-smoke", "pnpm mobile:ios-smoke", "agent_autonomous"),
    _REPLAY("ios-build-smoke", "TOO_IOS_SMOKE_BUILD=true pnpm mobile:ios-smoke", "agent_autonomous"),
    _REPLAY("mobile-route-evidence", "pnpm mobile:ios-route-evidence", "agent_autonomous"),
    _REPLAY("mobile-interactive-evidence", "pnpm mobile:ios-interactive-evidence", "agent_autonomous"),
    _REPLAY("browser-evidence-rerun", "PLAYWRIGHT_PORT=3227 pnpm test:browser", "agent_autonomous"),
    _REPLAY(
        "chromium-firefox-matrix-port",
        "PLAYWRIGHT_PORT=3228 CHROMIUM_FIREFOX_MATRIX_PORT=3228 pnpm test:chromium-firefox",
        "agent_autonomous",
    ),
    _REPLAY("run-scoped-process-cleanup", "kill 81302", "run_scoped_cleanup"),
    _REPLAY(
        "run-scoped-docker-volume-cleanup",
        "docker volume rm too_restore_e2e_20260621_too-restore-postgres-data",
        "run_scoped_cleanup",
    ),
)
def classify_action(action: str, *, approval_prompt_seen: bool = False) -> ActionClassification:
    normalized = action.strip().casefold().replace("-", "_").replace(" ", "_")
    if normalized in TRUE_USER_NEEDED_ACTIONS:
        return ActionClassification(
            action=normalized,
            category="true_user_needed",
            ledger_status="needs_user",
            rationale="external or irreversible human decision is required",
        )
    if normalized in LOW_RISK_IN_SCOPE_ACTIONS:
        if approval_prompt_seen:
            return ActionClassification(
                action=normalized,
                category="autonomy_defect",
                ledger_status="open",
                rationale="low-risk in-scope work hit an approval prompt and must remain a SelfE2E issue",
            )
        return ActionClassification(
            action=normalized,
            category="agent_autonomous",
            ledger_status="satisfied",
            rationale="low-risk in-scope work should proceed autonomously",
        )
    return ActionClassification(
        action=normalized,
        category="requires_agent_classification",
        ledger_status="open",
        rationale="unknown action must be classified before finalization",
    )


def classify_process_cleanup(
    *,
    process_identity_known: bool,
    run_owned: bool = False,
    port_owned: bool = False,
) -> CleanupClassification:
    if process_identity_known and (run_owned or port_owned):
        ownership = "run" if run_owned else "port"
        return CleanupClassification(
            resource="process",
            category="run_scoped_cleanup",
            ledger_status="satisfied",
            allowed=True,
            rationale=f"helper process identity is known and {ownership} ownership is proven",
        )
    if not process_identity_known:
        rationale = "process identity is unknown"
    else:
        rationale = "process is not proven to belong to the current run or recorded port"
    return CleanupClassification(
        resource="process",
        category="requires_user_needed_or_blocked",
        ledger_status="blocked",
        allowed=False,
        rationale=rationale,
    )


def classify_docker_cleanup(
    *,
    resource_type: str,
    resource_name: str,
    current_run_scope: str,
    compose_project: str | None = None,
) -> CleanupClassification:
    resource = _normalize(resource_type or "docker")
    name = _normalize(resource_name)
    scope = _normalize(current_run_scope)
    project = _normalize(compose_project or "")
    if scope and (project == scope or name == scope or name.startswith(f"{scope}_") or name.startswith(f"{scope}-")):
        return CleanupClassification(
            resource=f"docker_{resource}",
            category="run_scoped_cleanup",
            ledger_status="satisfied",
            allowed=True,
            rationale="Docker resource matches the current run scope or compose project",
        )
    return CleanupClassification(
        resource=f"docker_{resource}",
        category="requires_user_needed_or_blocked",
        ledger_status="blocked",
        allowed=False,
        rationale="Docker resource is not proven to match the current run scope or compose project",
    )


def classify_service_e2e_approval_prompt(
    command: str,
    *,
    current_run_scope: str = "",
    process_identity_known: bool = False,
    run_owned: bool = False,
    port_owned: bool = False,
    compose_project: str | None = None,
) -> ActionClassification | CleanupClassification:
    normalized = _normalize_command(command)
    docker = _docker_cleanup_from_command(command, current_run_scope=current_run_scope, compose_project=compose_project)
    if docker is not None:
        return docker
    if _is_kill_command(command):
        return classify_process_cleanup(
            process_identity_known=process_identity_known,
            run_owned=run_owned,
            port_owned=port_owned,
        )
    if "pnpm_test_chromium_firefox" in normalized or "test_chromium_firefox" in normalized:
        return classify_action("chromium_firefox_matrix")
    if "pnpm_test_browser" in normalized or "test_browser" in normalized:
        return classify_action("browser_evidence_rerun")
    if "pnpm_mobile_ios_route_evidence" in normalized or "mobile_ios_route_evidence" in normalized:
        return classify_action("mobile_route_evidence")
    if "pnpm_mobile_ios_interactive_evidence" in normalized or "mobile_ios_interactive_evidence" in normalized:
        return classify_action("mobile_interactive_evidence")
    if "pnpm_mobile_ios_smoke" in normalized or "mobile_ios_smoke" in normalized:
        if "too_ios_smoke_build_true" in normalized:
            return classify_action("ios_build_smoke")
        return classify_action("ios_simulator_smoke")
    return classify_action(command)
def classify_service_e2e_approval_replay() -> tuple[
    tuple[ServiceE2EApprovalReplayObservation, ActionClassification | CleanupClassification],
    ...,
]:
    return tuple(
        (
            observation,
            classify_service_e2e_approval_prompt(
                observation.command,
                current_run_scope=observation.current_run_scope,
                process_identity_known=observation.process_identity_known,
                port_owned=observation.port_owned,
            ),
        )
        for observation in SERVICE_E2E_APPROVAL_REPLAY_OBSERVATIONS
    )


def autonomy_policy_diagnostic_lines() -> list[str]:
    examples = [
        classify_action("browser evidence rerun"),
        classify_action("ios simulator smoke"),
        classify_service_e2e_approval_prompt("PLAYWRIGHT_PORT=3227 pnpm test:browser"),
        classify_process_cleanup(process_identity_known=True, run_owned=True),
        classify_docker_cleanup(
            resource_type="volume",
            resource_name="agent_orchestra_20260621_postgres_data",
            current_run_scope="agent_orchestra_20260621",
        ),
        classify_action("credential"),
    ]
    lines = ["autonomy policy classifications:"]
    for example in examples:
        if isinstance(example, ActionClassification):
            lines.append(
                f"  action {example.action}: category={example.category} "
                f"ledger_status={example.ledger_status}"
            )
        else:
            lines.append(
                f"  cleanup {example.resource}: category={example.category} "
                f"allowed={str(example.allowed).lower()} ledger_status={example.ledger_status}"
            )
    lines.append("service e2e approval replay:")
    for observation, result in classify_service_e2e_approval_replay():
        lines.append(
            f"  {observation.defect_id}: command={shlex.quote(observation.command)} "
            f"category={result.category} ledger_status={result.ledger_status}"
        )
    return lines


def _normalize(value: str) -> str:
    return value.strip().casefold().replace("-", "_").replace(" ", "_")


def _normalize_command(value: str) -> str:
    return _normalize(value.replace(":", "_").replace("=", "_"))


def _is_kill_command(command: str) -> bool:
    try:
        tokens = shlex.split(command)
    except ValueError:
        return False
    return len(tokens) == 2 and tokens[0] == "kill" and tokens[1].isdigit()


def _docker_cleanup_from_command(
    command: str,
    *,
    current_run_scope: str,
    compose_project: str | None,
) -> CleanupClassification | None:
    try:
        tokens = shlex.split(command)
    except ValueError:
        return None
    if len(tokens) < 4 or tokens[0] != "docker":
        return None
    resource_type = tokens[1]
    operation = tokens[2]
    if resource_type not in {"volume", "container"} or operation not in {"rm", "remove"}:
        return None
    return classify_docker_cleanup(
        resource_type=resource_type,
        resource_name=tokens[-1],
        current_run_scope=current_run_scope,
        compose_project=compose_project,
    )
