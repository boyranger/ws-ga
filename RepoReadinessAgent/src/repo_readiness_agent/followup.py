"""Follow-up logic for Repo Readiness Agent.

This module owns the canonical follow-up vocabulary and comparison rules so
monitoring behavior has a single source of truth.
"""

from __future__ import annotations

from .contract import (
    CONFIDENCE_LEVELS,
    FOLLOW_UP_KINDS,
    STAGES,
    STOP_CONDITIONS,
    DeltaBrief,
    FollowUpStatus,
    ProductReport,
)

FOLLOW_UP_STATUSES = list(FOLLOW_UP_KINDS)

_STAGE_ORDER = {stage: index for index, stage in enumerate(STAGES, start=1)}
_CONFIDENCE_ORDER = {level: index for index, level in enumerate(CONFIDENCE_LEVELS, start=1)}


def build_delta_brief(previous_report: ProductReport, latest_report: ProductReport) -> DeltaBrief:
    previous_fixes = set(previous_report.top_fixes)
    latest_fixes = set(latest_report.top_fixes)
    previous_risks = set(previous_report.top_risks)
    latest_risks = set(latest_report.top_risks)

    resolved_fixes = [item for item in previous_report.top_fixes if item not in latest_fixes]
    remaining_fixes = list(latest_report.top_fixes[:2])
    reduced_risks = [item for item in previous_report.top_risks if item not in latest_risks]
    still_blocked_risks = list(latest_report.top_risks[:2])

    previous_stage = _STAGE_ORDER.get(previous_report.stage, 0)
    latest_stage = _STAGE_ORDER.get(latest_report.stage, 0)
    previous_confidence = _CONFIDENCE_ORDER.get(previous_report.confidence, 0)
    latest_confidence = _CONFIDENCE_ORDER.get(latest_report.confidence, 0)

    if latest_stage > previous_stage:
        summary = f"Repo naik dari {previous_report.stage} ke {latest_report.stage}."
    elif latest_confidence > previous_confidence:
        summary = f"Confidence repo naik dari {previous_report.confidence} ke {latest_report.confidence}."
    elif resolved_fixes or reduced_risks:
        summary = "Ada sinyal perbaikan pada sebagian area, meski readiness keseluruhan belum naik penuh."
    else:
        summary = "Belum terlihat perubahan signifikan sejak pemeriksaan sebelumnya."

    what_improved = resolved_fixes[:2] + reduced_risks[:2]
    if not what_improved:
        what_improved = ["Belum ada indikator perbaikan yang cukup kuat dari scan saat ini."]

    what_still_blocked = remaining_fixes[:2] + still_blocked_risks[:2]
    if not what_still_blocked:
        what_still_blocked = ["Tidak ada blocker utama yang menonjol pada follow-up ini."]

    priority_now = latest_report.top_fixes[0] if latest_report.top_fixes else "Lanjutkan monitoring sampai ada sinyal perubahan yang lebih jelas."
    founder_action = (
        f"Fokus dulu memastikan perbaikan '{priority_now}' benar-benar dikerjakan dan diverifikasi pada iterasi berikutnya."
    )
    engineer_action = (
        f"Minta engineer mengirim patch sempit untuk '{priority_now}', lengkap dengan file yang diubah dan bukti verifikasi hasilnya."
    )

    return DeltaBrief(
        summary=summary,
        what_improved=what_improved,
        what_still_blocked=what_still_blocked,
        priority_now=priority_now,
        founder_action=founder_action,
        engineer_action=engineer_action,
    )


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
