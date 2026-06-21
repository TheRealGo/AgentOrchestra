from __future__ import annotations

from dataclasses import dataclass


LOCAL_TWO_USER_PRODUCTION_LIKE = "local_two_user_production_like"
PUBLIC_RELEASE = "public_release"
SELF_IMPROVEMENT = "self_improvement"

KNOWN_PROFILES = frozenset(
    {
        LOCAL_TWO_USER_PRODUCTION_LIKE,
        PUBLIC_RELEASE,
        SELF_IMPROVEMENT,
    }
)

LOCAL_EVIDENCE = frozenset(
    {
        "local_safari",
        "iphone_safari",
        "direct_ios_install",
        "local_db_persistence",
        "local_two_person_use",
        "production_compatible_architecture",
    }
)
PUBLIC_RELEASE_EVIDENCE = frozenset(
    {
        "app_store",
        "public_domain",
        "production_provider",
        "legal_review",
        "store_review",
        "public_release_approval",
    }
)
SELF_IMPROVEMENT_EVIDENCE = frozenset(
    {
        "self_improvement_status_file",
        "task_file_finalization",
        "professional_agent_review",
        "zero_issue_finalization",
    }
)


@dataclass(frozen=True)
class GateClassification:
    profile: str
    evidence_kind: str
    disposition: str
    rationale: str


def normalize_profile(profile: str | None) -> str:
    candidate = (profile or "").strip().casefold().replace("-", "_")
    if candidate in KNOWN_PROFILES:
        return candidate
    if not candidate:
        return LOCAL_TWO_USER_PRODUCTION_LIKE
    raise ValueError(f"unknown completion profile {profile!r}")


def infer_profile(user_intent: str) -> str:
    text = " ".join(user_intent.casefold().replace("-", "_").split())
    local_intent = any(
        token in text
        for token in (
            "local two",
            "two_person",
            "two-person",
            "local_first",
            "local-first",
            "ローカル2人",
            "2人運用",
        )
    )
    public_release_mentioned = any(
        token in text
        for token in (
            "public release",
            "app store",
            "store/legal",
            "公開リリース",
            "本番公開",
        )
    )
    public_release_deferred = public_release_mentioned and any(
        token in text
        for token in (
            "deferred",
            "not immediate",
            "later",
            "先に",
            "後で",
            "延期",
        )
    )
    if any(token in text for token in ("self_improvement", "self improvement", "自己改善")):
        return SELF_IMPROVEMENT
    if local_intent and public_release_deferred:
        return LOCAL_TWO_USER_PRODUCTION_LIKE
    if public_release_mentioned:
        return PUBLIC_RELEASE
    if local_intent:
        return LOCAL_TWO_USER_PRODUCTION_LIKE
    return LOCAL_TWO_USER_PRODUCTION_LIKE


def classify_gate(profile: str, evidence_kind: str) -> GateClassification:
    normalized_profile = normalize_profile(profile)
    normalized_kind = evidence_kind.strip().casefold().replace("-", "_")
    if normalized_kind in PUBLIC_RELEASE_EVIDENCE:
        if normalized_profile == PUBLIC_RELEASE:
            return GateClassification(
                normalized_profile,
                normalized_kind,
                "blocking",
                "public release evidence is required for the public_release profile",
            )
        return GateClassification(
            normalized_profile,
            normalized_kind,
            "deferred",
            "public release evidence is not a blocker for this completion profile",
        )
    if normalized_kind in LOCAL_EVIDENCE:
        if normalized_profile == PUBLIC_RELEASE:
            return GateClassification(
                normalized_profile,
                normalized_kind,
                "supporting",
                "local evidence supports release readiness but does not replace public release gates",
            )
        return GateClassification(
            normalized_profile,
            normalized_kind,
            "blocking",
            "local operation evidence is required for the local production-like profile",
        )
    if normalized_kind in SELF_IMPROVEMENT_EVIDENCE:
        return GateClassification(
            normalized_profile,
            normalized_kind,
            "blocking" if normalized_profile == SELF_IMPROVEMENT else "supporting",
            "self-improvement evidence blocks only self_improvement completion",
        )
    return GateClassification(
        normalized_profile,
        normalized_kind,
        "needs-classification",
        "unknown evidence kind must be explicitly classified before finalization",
    )


def status_for_gate(classification: GateClassification) -> str:
    if classification.disposition == "deferred":
        return "not-applicable"
    return "open"


def service_defect_intake_items(defect_brief: str) -> list[str]:
    text = defect_brief.casefold()
    items: list[str] = []
    if "completion profile" in text or "local_two_user_production_like" in text:
        items.append("completion-profile-user-intent-gates")
    if "task file" in text or "duplicate sections" in text or "malformed" in text:
        items.append("task-file-finalization-validation")
    if "tmux" in text or "composer residue" in text or "submit key" in text:
        items.append("tmux-delivery-confirmation")
    if "approval" in text or "userneeded" in text or "user needed" in text:
        items.append("approval-userneeded-classification")
    if "usage limit" in text or "stale" in text or "pane recovery" in text:
        items.append("usage-limit-pane-recovery")
    if "defect intake" in text or "self-improvement" in text:
        items.append("service-e2e-defect-intake")
    return list(dict.fromkeys(items))
