"""Bot-layer data structures for Repo Readiness Agent."""

from __future__ import annotations

from dataclasses import dataclass

from ..contract import ProductReport


@dataclass
class TelegramUserRecord:
    id: int
    telegram_user_id: str
    username: str | None
    first_name: str | None
    last_name: str | None
    created_at: str
    updated_at: str
    last_seen_at: str


@dataclass
class TrackedRepositoryRecord:
    id: int
    user_id: int
    repo_url: str
    repo_normalized: str
    default_branch: str | None
    status: str
    created_at: str
    updated_at: str
    last_checked_at: str | None


@dataclass
class InspectionReportRecord:
    id: int
    tracked_repository_id: int
    trigger_kind: str
    report_json: str
    stage: str
    confidence: str
    verdict: str
    top_risks_json: str
    top_fixes_json: str
    demo_safe: str | None
    launch_ready: str | None
    handoff_ready: str | None
    created_at: str


@dataclass
class RepoSummary:
    tracking_id: int
    repo_normalized: str
    status: str
    last_checked_at: str | None
    latest_stage: str | None = None
    latest_confidence: str | None = None


@dataclass
class InspectResult:
    tracking_id: int
    report: ProductReport
    rendered_text: str


@dataclass
class LatestAnalysisContext:
    tracked_repo: TrackedRepositoryRecord
    report: ProductReport
