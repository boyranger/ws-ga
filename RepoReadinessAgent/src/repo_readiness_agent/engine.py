"""Engine adapter for Repo Readiness Agent.

This module bridges the lower-level repo_quality_scorer engine into the
product-facing report contract used by Repo Readiness Agent.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from .contract import FollowUpStatus, FounderGates, ProductReport

PACKAGE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_ROOT.parent.parent
SCORER_PATH = REPO_ROOT / "tools" / "repo_quality_scorer" / "repo_quality_scorer.py"


def run_engine(
    repo: str,
    *,
    branch: str | None = None,
    subdir: str | None = None,
    strictness: str = "balanced",
    language_hint: str | None = None,
) -> dict[str, Any]:
    cmd = [sys.executable, str(SCORER_PATH), repo, "--format", "json", "--strictness", strictness]
    if branch:
        cmd.extend(["--branch", branch])
    if subdir:
        cmd.extend(["--subdir", subdir])
    if language_hint:
        cmd.extend(["--language-hint", language_hint])

    completed = subprocess.run(cmd, text=True, capture_output=True, check=True)
    return json.loads(completed.stdout)


def derive_founder_gates(score_report: dict[str, Any]) -> FounderGates:
    stage = score_report["maturity_level"]
    production_score = float(score_report["production_readiness_score"])
    code_score = float(score_report["code_quality_score"])
    confidence = score_report["confidence"]

    demo_safe = "yes" if stage in {"MVP", "Handoff-ready"} or production_score >= 6.0 else "not yet"
    launch_ready = "yes" if stage == "Handoff-ready" and production_score >= 7.5 and confidence != "Low" else "not yet"
    handoff_ready = "yes" if stage == "Handoff-ready" and code_score >= 7.0 and confidence == "High" else "not yet"

    return FounderGates(
        demo_safe=demo_safe,
        launch_ready=launch_ready,
        handoff_ready=handoff_ready,
    )


def build_product_report(score_report: dict[str, Any]) -> ProductReport:
    risks = list(score_report.get("risks") or [])[:3]
    fixes = list(score_report.get("top_improvements") or [])[:3]

    if not risks:
        risks = ["No major risks were surfaced by the current lightweight scan."]
    if not fixes:
        fixes = ["No specific next fixes were surfaced by the current lightweight scan."]

    return ProductReport(
        stage=score_report["maturity_level"],
        verdict=score_report["verdict"],
        confidence=score_report["confidence"],
        top_risks=risks,
        top_fixes=fixes,
        gates=derive_founder_gates(score_report),
    )


def build_follow_up(
    previous_report: ProductReport,
    latest_report: ProductReport,
    *,
    target_stage: str = "Handoff-ready",
    target_confidence: str = "High",
) -> FollowUpStatus:
    stage_order = {"Prototype": 1, "MVP": 2, "Handoff-ready": 3}
    confidence_order = {"Low": 1, "Medium": 2, "High": 3}

    previous_stage = stage_order.get(previous_report.stage, 0)
    latest_stage = stage_order.get(latest_report.stage, 0)
    previous_confidence = confidence_order.get(previous_report.confidence, 0)
    latest_confidence = confidence_order.get(latest_report.confidence, 0)

    if latest_stage > previous_stage or latest_confidence > previous_confidence:
        status = "Improved"
    elif latest_stage == previous_stage and latest_confidence == previous_confidence:
        status = "Unchanged"
    else:
        status = "Still blocked"

    stop_condition = "Target reached" if (
        latest_report.stage == target_stage
        and confidence_order.get(latest_report.confidence, 0) >= confidence_order.get(target_confidence, 0)
    ) else "Keep monitoring"

    return FollowUpStatus(status=status, stop_condition=stop_condition)
