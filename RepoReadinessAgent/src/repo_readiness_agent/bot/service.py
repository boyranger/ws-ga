"""Application service for the public Repo Readiness Agent Telegram bot."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from ..contract import ProductReport, product_report_from_dict
from ..engine import build_product_report, run_engine
from ..followup import build_follow_up
from ..formatter import render_text_report
from . import repository as repo_db
from .storage import Database
from .types import InspectResult, RepoSummary, TelegramUserRecord, TrackedRepositoryRecord

_GITHUB_REPO_RE = re.compile(r"^https://github\.com/(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?/?$")


@dataclass
class FollowUpRunResult:
    tracked_repo: TrackedRepositoryRecord
    previous_report: ProductReport
    latest_report: ProductReport
    rendered_text: str


@dataclass
class ScheduledFollowUpResult:
    telegram_user_id: str
    tracking_id: int
    repo_url: str
    report: ProductReport
    rendered_text: str


class ServiceError(Exception):
    pass


class ValidationError(ServiceError):
    pass


class NotFoundError(ServiceError):
    pass


class RepoTrackingService:
    def __init__(self, database: Database) -> None:
        self.database = database
        self.database.initialize()

    def normalize_repo_url(self, repo_url: str) -> str:
        candidate = repo_url.strip()
        match = _GITHUB_REPO_RE.match(candidate)
        if not match:
            raise ValidationError("Saat ini bot hanya mendukung URL repository GitHub. Gunakan format: https://github.com/owner/repo")
        owner = match.group("owner")
        repo = match.group("repo")
        return f"https://github.com/{owner}/{repo}"

    def _upsert_user(self, telegram_user_id: str, username: str | None, first_name: str | None, last_name: str | None) -> TelegramUserRecord:
        with self.database.connect() as connection:
            user = repo_db.upsert_telegram_user(
                connection,
                telegram_user_id=telegram_user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
            connection.commit()
            return user

    def inspect_repo(
        self,
        *,
        telegram_user_id: str,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
        repo_url: str,
        branch: str | None = None,
        subdir: str | None = None,
        strictness: str = "balanced",
        language_hint: str | None = None,
        trigger_kind: str = "manual_inspect",
    ) -> InspectResult:
        user = self._upsert_user(telegram_user_id, username, first_name, last_name)
        normalized = self.normalize_repo_url(repo_url)
        score_report = run_engine(
            normalized,
            branch=branch,
            subdir=subdir,
            strictness=strictness,
            language_hint=language_hint,
        )
        product_report = build_product_report(score_report)

        with self.database.connect() as connection:
            tracked_repo = repo_db.get_or_create_tracked_repo(
                connection,
                user_id=user.id,
                repo_url=repo_url.strip(),
                repo_normalized=normalized,
                default_branch=branch,
            )
            repo_db.insert_report(
                connection,
                tracked_repository_id=tracked_repo.id,
                trigger_kind=trigger_kind,
                report=product_report,
            )
            repo_db.touch_tracked_repo(connection, tracked_repo.id)
            connection.commit()

        rendered = render_text_report(product_report)
        return InspectResult(tracking_id=tracked_repo.id, report=product_report, rendered_text=rendered)

    def list_repos_for_user(
        self,
        *,
        telegram_user_id: str,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
    ) -> list[RepoSummary]:
        user = self._upsert_user(telegram_user_id, username, first_name, last_name)
        with self.database.connect() as connection:
            return repo_db.list_user_tracked_repos(connection, user_id=user.id)

    def enable_tracking(
        self,
        *,
        telegram_user_id: str,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
        repo_url: str,
        cadence: str = "daily",
        target_stage: str = "Handoff-ready",
        target_confidence: str = "High",
    ) -> TrackedRepositoryRecord:
        user = self._upsert_user(telegram_user_id, username, first_name, last_name)
        normalized = self.normalize_repo_url(repo_url)
        with self.database.connect() as connection:
            tracked_repo = repo_db.get_or_create_tracked_repo(
                connection,
                user_id=user.id,
                repo_url=repo_url.strip(),
                repo_normalized=normalized,
            )
            repo_db.set_followup_config(
                connection,
                tracked_repository_id=tracked_repo.id,
                cadence=cadence,
                target_stage=target_stage,
                target_confidence=target_confidence,
                enabled=True,
            )
            connection.commit()
            return tracked_repo

    def disable_tracking(
        self,
        *,
        telegram_user_id: str,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
        tracking_id: int,
    ) -> TrackedRepositoryRecord:
        user = self._upsert_user(telegram_user_id, username, first_name, last_name)
        with self.database.connect() as connection:
            tracked_repo = repo_db.get_tracked_repo_for_user(connection, user_id=user.id, tracking_id=tracking_id)
            if not tracked_repo:
                raise NotFoundError("Data tracking tidak ditemukan.")
            repo_db.archive_tracking(connection, tracked_repository_id=tracked_repo.id)
            connection.commit()
            refreshed = repo_db.get_tracked_repo_for_user(connection, user_id=user.id, tracking_id=tracking_id)
            assert refreshed is not None
            return refreshed

    def get_report_for_tracking(
        self,
        *,
        telegram_user_id: str,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
        tracking_id: int,
    ) -> tuple[TrackedRepositoryRecord, ProductReport]:
        user = self._upsert_user(telegram_user_id, username, first_name, last_name)
        with self.database.connect() as connection:
            tracked_repo = repo_db.get_tracked_repo_for_user(connection, user_id=user.id, tracking_id=tracking_id)
            if not tracked_repo:
                raise NotFoundError("Data tracking tidak ditemukan.")
            latest = repo_db.get_latest_report_for_repo(connection, tracked_repository_id=tracked_repo.id)
            if not latest:
                raise NotFoundError("Belum ada report yang tersimpan untuk data tracking itu.")
            return tracked_repo, product_report_from_dict(json.loads(latest.report_json))

    def run_followup_for_tracking(
        self,
        *,
        telegram_user_id: str,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
        tracking_id: int,
        strictness: str = "balanced",
        language_hint: str | None = None,
    ) -> FollowUpRunResult:
        user = self._upsert_user(telegram_user_id, username, first_name, last_name)
        with self.database.connect() as connection:
            tracked_repo = repo_db.get_tracked_repo_for_user(connection, user_id=user.id, tracking_id=tracking_id)
            if not tracked_repo:
                raise NotFoundError("Data tracking tidak ditemukan.")
            latest_record = repo_db.get_latest_report_for_repo(connection, tracked_repository_id=tracked_repo.id)
            if not latest_record:
                raise NotFoundError("Belum ada report sebelumnya. Jalankan /inspect dulu.")
            previous_report = product_report_from_dict(json.loads(latest_record.report_json))

        inspect_result = self.inspect_repo(
            telegram_user_id=telegram_user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            repo_url=tracked_repo.repo_normalized,
            branch=tracked_repo.default_branch,
            strictness=strictness,
            language_hint=language_hint,
            trigger_kind="manual_followup",
        )
        inspect_result.report.follow_up = build_follow_up(previous_report, inspect_result.report)

        with self.database.connect() as connection:
            repo_db.replace_latest_report_payload(
                connection,
                tracked_repository_id=tracked_repo.id,
                report=inspect_result.report,
            )
            connection.commit()

        return FollowUpRunResult(
            tracked_repo=tracked_repo,
            previous_report=previous_report,
            latest_report=inspect_result.report,
            rendered_text=render_text_report(inspect_result.report),
        )

    def run_due_followups(self, *, strictness: str = "balanced") -> list[ScheduledFollowUpResult]:
        results: list[ScheduledFollowUpResult] = []
        with self.database.connect() as connection:
            due_jobs = repo_db.list_due_followup_jobs(connection)

        for job in due_jobs:
            previous_report = product_report_from_dict(json.loads(job["report_json"]))
            inspect_result = self.inspect_repo(
                telegram_user_id=job["telegram_user_id"],
                username=job["username"],
                first_name=job["first_name"],
                last_name=job["last_name"],
                repo_url=job["repo_normalized"],
                branch=job["default_branch"],
                strictness=strictness,
                trigger_kind="scheduled_followup",
            )
            inspect_result.report.follow_up = build_follow_up(
                previous_report,
                inspect_result.report,
                target_stage=job["target_stage"],
                target_confidence=job["target_confidence"],
            )
            with self.database.connect() as connection:
                repo_db.replace_latest_report_payload(
                    connection,
                    tracked_repository_id=job["tracked_repository_id"],
                    report=inspect_result.report,
                )
                repo_db.mark_followup_job_run(
                    connection,
                    tracked_repository_id=job["tracked_repository_id"],
                    stop_reached=inspect_result.report.follow_up.stop_condition == "Target reached",
                )
                connection.commit()
            results.append(
                ScheduledFollowUpResult(
                    telegram_user_id=job["telegram_user_id"],
                    tracking_id=job["tracked_repository_id"],
                    repo_url=job["repo_normalized"],
                    report=inspect_result.report,
                    rendered_text=render_text_report(inspect_result.report),
                )
            )

        return results
