"""Product-facing contracts for Repo Readiness Agent."""

from dataclasses import dataclass
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
class ProductReport:
    stage: Stage
    verdict: str
    confidence: Confidence
    top_risks: list[str]
    top_fixes: list[str]
    gates: FounderGates | None = None
    follow_up: FollowUpStatus | None = None
