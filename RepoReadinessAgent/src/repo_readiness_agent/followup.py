"""Follow-up logic for Repo Readiness Agent.

This module owns the canonical follow-up vocabulary and comparison rules so
monitoring behavior has a single source of truth.
"""

from __future__ import annotations

from .contract import FollowUpStatus, ProductReport

FOLLOW_UP_STATUSES = [
    "Improved",
    "Unchanged",
    "Still blocked",
]

STOP_CONDITIONS = [
    "Target reached",
    "Keep monitoring",
]

_STAGE_ORDER = {"Prototype": 1, "MVP": 2, "Handoff-ready": 3}
_CONFIDENCE_ORDER = {"Low": 1, "Medium": 2, "High": 3}


def build_follow_up(
    previous_report: ProductReport,
    latest_report: ProductReport,
    *,
    target_stage: str = "Handoff-ready",
    target_confidence: str = "High",
) -> FollowUpStatus:
    previous_stage = _STAGE_ORDER.get(previous_report.stage, 0)
    latest_stage = _STAGE_ORDER.get(latest_report.stage, 0)
    previous_confidence = _CONFIDENCE_ORDER.get(previous_report.confidence, 0)
    latest_confidence = _CONFIDENCE_ORDER.get(latest_report.confidence, 0)

    if latest_stage > previous_stage or latest_confidence > previous_confidence:
        status = "Improved"
    elif latest_stage == previous_stage and latest_confidence == previous_confidence:
        status = "Unchanged"
    else:
        status = "Still blocked"

    stop_condition = "Target reached" if (
        latest_report.stage == target_stage
        and latest_confidence >= _CONFIDENCE_ORDER.get(target_confidence, 0)
    ) else "Keep monitoring"

    return FollowUpStatus(status=status, stop_condition=stop_condition)
