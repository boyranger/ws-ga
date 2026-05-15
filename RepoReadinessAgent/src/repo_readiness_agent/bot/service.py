"""Application service for the public Repo Readiness Agent Telegram bot."""

from __future__ import annotations

import re
import json

from ..contract import ProductReport, product_report_from_dict
from ..engine import build_product_report, run_engine
from ..formatter import render_text_report
from . import repository as repo_db
from .storage import Database
from .types import InspectResult, RepoSummary, TelegramUserRecord, TrackedRepositoryRecord

_GITHUB_REPO_RE = re.compile(r"^https://github\.com/(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?/?$")


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
            raise ValidationError("Only GitHub repository URLs are supported right now. Use format: https://github.com/owner/repo")
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
                raise NotFoundError("Tracking record not found.")
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
                raise NotFoundError("Tracking record not found.")
            latest = repo_db.get_latest_report_for_repo(connection, tracked_repository_id=tracked_repo.id)
            if not latest:
                raise NotFoundError("No report has been saved for that tracking record yet.")
            return tracked_repo, product_report_from_dict(json.loads(latest.report_json))
