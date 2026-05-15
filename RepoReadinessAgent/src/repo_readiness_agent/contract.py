"""Product-facing contracts for Repo Readiness Agent."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

Stage = Literal["Prototype", "MVP", "Handoff-ready"]
Confidence = Literal["Low", "Medium", "High"]
GateValue = Literal["yes", "not yet"]
FollowUpKind = Literal["Improved", "Unchanged", "Still blocked"]
StopCondition = Literal["Target reached", "Keep monitoring"]

STAGES: tuple[Stage, ...] = ("Prototype", "MVP", "Handoff-ready")
CONFIDENCE_LEVELS: tuple[Confidence, ...] = ("Low", "Medium", "High")
GATE_VALUES: tuple[GateValue, ...] = ("yes", "not yet")
FOLLOW_UP_KINDS: tuple[FollowUpKind, ...] = ("Improved", "Unchanged", "Still blocked")
STOP_CONDITIONS: tuple[StopCondition, ...] = ("Target reached", "Keep monitoring")


@dataclass
class FounderGates:
    demo_safe: GateValue
    launch_ready: GateValue
    handoff_ready: GateValue


@dataclass
class FollowUpStatus:
    status: FollowUpKind
    stop_condition: StopCondition


@dataclass
class DeltaBrief:
    summary: str
    what_improved: list[str]
    what_still_blocked: list[str]
    priority_now: str
    founder_action: str
    engineer_action: str


@dataclass
class RemediationHint:
    fix: str
    target_files: list[str]
    why: str
    line_hints: list[str]


@dataclass
class ImprovementBrief:
    fix: str
    objective: str
    target_files: list[str]
    why_now: str
    do_it_yourself: list[str]
    delegate_to_engineer: list[str]
    acceptance_criteria: list[str]
    verification_steps: list[str]


@dataclass
class ProductReport:
    stage: Stage
    verdict: str
    confidence: Confidence
    top_risks: list[str]
    top_fixes: list[str]
    remediation_hints: list[RemediationHint] | None = None
    improvement_briefs: list[ImprovementBrief] | None = None
    delta_brief: DeltaBrief | None = None
    gates: FounderGates | None = None
    follow_up: FollowUpStatus | None = None


def product_report_to_dict(report: ProductReport) -> dict:
    return asdict(report)


def product_report_to_json(report: ProductReport) -> str:
    return json.dumps(product_report_to_dict(report), indent=2, ensure_ascii=False)


def product_report_from_dict(data: dict) -> ProductReport:
    gates = data.get("gates")
    follow_up = data.get("follow_up")
    remediation_hints = data.get("remediation_hints")
    improvement_briefs = data.get("improvement_briefs")
    delta_brief = data.get("delta_brief")
    return ProductReport(
        stage=data["stage"],
        verdict=data["verdict"],
        confidence=data["confidence"],
        top_risks=data["top_risks"],
        top_fixes=data["top_fixes"],
        remediation_hints=[RemediationHint(**item) for item in remediation_hints] if remediation_hints else None,
        improvement_briefs=[ImprovementBrief(**item) for item in improvement_briefs] if improvement_briefs else None,
        delta_brief=DeltaBrief(**delta_brief) if delta_brief else None,
        gates=FounderGates(**gates) if gates else None,
        follow_up=FollowUpStatus(**follow_up) if follow_up else None,
    )


def load_product_report(path: str | Path) -> ProductReport:
    data = json.loads(Path(path).read_text())
    return product_report_from_dict(data)
