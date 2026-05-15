"""Product-facing contracts for Repo Readiness Agent."""

from dataclasses import dataclass
from typing import List


@dataclass
class FounderGates:
    demo_safe: str
    launch_ready: str
    handoff_ready: str


@dataclass
class FollowUpStatus:
    status: str
    stop_condition: str


@dataclass
class ProductReport:
    stage: str
    verdict: str
    confidence: str
    top_risks: List[str]
    top_fixes: List[str]
    gates: FounderGates | None = None
    follow_up: FollowUpStatus | None = None
