"""Persistence helpers for Repo Readiness Agent bot."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from sqlite3 import Connection, Row

from ..contract import ProductReport, product_report_to_json
from .types import InspectionReportRecord, RepoSummary, TelegramUserRecord, TrackedRepositoryRecord


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _next_run_for_cadence(cadence: str) -> str:
    base = datetime.now(UTC).replace(microsecond=0)
    if cadence == "daily":
        return (base + timedelta(days=1)).isoformat()
    return base.isoformat()


def _row_to_user(row: Row) -> TelegramUserRecord:
    return TelegramUserRecord(**dict(row))


def _row_to_repo(row: Row) -> TrackedRepositoryRecord:
    return TrackedRepositoryRecord(**dict(row))


def _row_to_report(row: Row) -> InspectionReportRecord:
    return InspectionReportRecord(**dict(row))


def upsert_telegram_user(
    connection: Connection,
    *,
    telegram_user_id: str,
    username: str | None,
    first_name: str | None,
    last_name: str | None,
) -> TelegramUserRecord:
    now = utc_now()
    connection.execute(
        """
        insert into telegram_users (
          telegram_user_id, username, first_name, last_name, created_at, updated_at, last_seen_at
        ) values (?, ?, ?, ?, ?, ?, ?)
        on conflict(telegram_user_id) do update set
          username=excluded.username,
          first_name=excluded.first_name,
          last_name=excluded.last_name,
          updated_at=excluded.updated_at,
          last_seen_at=excluded.last_seen_at
        """,
        (telegram_user_id, username, first_name, last_name, now, now, now),
    )
    row = connection.execute(
        "select * from telegram_users where telegram_user_id = ?",
        (telegram_user_id,),
    ).fetchone()
    assert row is not None
    return _row_to_user(row)


def get_or_create_tracked_repo(
    connection: Connection,
    *,
    user_id: int,
    repo_url: str,
    repo_normalized: str,
    default_branch: str | None = None,
) -> TrackedRepositoryRecord:
    now = utc_now()
    connection.execute(
        """
        insert into tracked_repositories (
          user_id, repo_url, repo_normalized, default_branch, status, created_at, updated_at
        ) values (?, ?, ?, ?, 'active', ?, ?)
        on conflict(user_id, repo_normalized) do update set
          repo_url=excluded.repo_url,
          default_branch=coalesce(excluded.default_branch, tracked_repositories.default_branch),
          status='active',
          updated_at=excluded.updated_at
        """,
        (user_id, repo_url, repo_normalized, default_branch, now, now),
    )
    row = connection.execute(
        "select * from tracked_repositories where user_id = ? and repo_normalized = ?",
        (user_id, repo_normalized),
    ).fetchone()
    assert row is not None
    return _row_to_repo(row)


def touch_tracked_repo(connection: Connection, tracked_repository_id: int) -> None:
    connection.execute(
        "update tracked_repositories set last_checked_at = ?, updated_at = ? where id = ?",
        (utc_now(), utc_now(), tracked_repository_id),
    )


def list_user_tracked_repos(connection: Connection, *, user_id: int) -> list[RepoSummary]:
    rows = connection.execute(
        """
        select
          tr.id as tracking_id,
          tr.repo_normalized,
          tr.status,
          tr.last_checked_at,
          ir.stage as latest_stage,
          ir.confidence as latest_confidence
        from tracked_repositories tr
        left join inspection_reports ir on ir.id = (
          select id from inspection_reports where tracked_repository_id = tr.id order by id desc limit 1
        )
        where tr.user_id = ?
        order by tr.updated_at desc, tr.id desc
        """,
        (user_id,),
    ).fetchall()
    return [RepoSummary(**dict(row)) for row in rows]


def get_tracked_repo_for_user(connection: Connection, *, user_id: int, tracking_id: int) -> TrackedRepositoryRecord | None:
    row = connection.execute(
        "select * from tracked_repositories where id = ? and user_id = ?",
        (tracking_id, user_id),
    ).fetchone()
    return _row_to_repo(row) if row else None


def insert_report(
    connection: Connection,
    *,
    tracked_repository_id: int,
    trigger_kind: str,
    report: ProductReport,
) -> InspectionReportRecord:
    now = utc_now()
    connection.execute(
        """
        insert into inspection_reports (
          tracked_repository_id, trigger_kind, report_json, stage, confidence, verdict,
          top_risks_json, top_fixes_json, demo_safe, launch_ready, handoff_ready, created_at
        ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            tracked_repository_id,
            trigger_kind,
            product_report_to_json(report),
            report.stage,
            report.confidence,
            report.verdict,
            json.dumps(report.top_risks, ensure_ascii=False),
            json.dumps(report.top_fixes, ensure_ascii=False),
            report.gates.demo_safe if report.gates else None,
            report.gates.launch_ready if report.gates else None,
            report.gates.handoff_ready if report.gates else None,
            now,
        ),
    )
    row = connection.execute(
        "select * from inspection_reports where tracked_repository_id = ? order by id desc limit 1",
        (tracked_repository_id,),
    ).fetchone()
    assert row is not None
    return _row_to_report(row)


def replace_latest_report_payload(connection: Connection, *, tracked_repository_id: int, report: ProductReport) -> None:
    connection.execute(
        """
        update inspection_reports
        set report_json = ?,
            stage = ?,
            confidence = ?,
            verdict = ?,
            top_risks_json = ?,
            top_fixes_json = ?,
            demo_safe = ?,
            launch_ready = ?,
            handoff_ready = ?
        where id = (
          select id from inspection_reports where tracked_repository_id = ? order by id desc limit 1
        )
        """,
        (
            product_report_to_json(report),
            report.stage,
            report.confidence,
            report.verdict,
            json.dumps(report.top_risks, ensure_ascii=False),
            json.dumps(report.top_fixes, ensure_ascii=False),
            report.gates.demo_safe if report.gates else None,
            report.gates.launch_ready if report.gates else None,
            report.gates.handoff_ready if report.gates else None,
            tracked_repository_id,
        ),
    )


def get_latest_report_for_repo(connection: Connection, *, tracked_repository_id: int) -> InspectionReportRecord | None:
    row = connection.execute(
        "select * from inspection_reports where tracked_repository_id = ? order by id desc limit 1",
        (tracked_repository_id,),
    ).fetchone()
    return _row_to_report(row) if row else None


def set_followup_config(
    connection: Connection,
    *,
    tracked_repository_id: int,
    cadence: str = 'daily',
    target_stage: str = 'Handoff-ready',
    target_confidence: str = 'High',
    enabled: bool = True,
) -> None:
    now = utc_now()
    connection.execute(
        """
        insert into followup_jobs (
          tracked_repository_id, enabled, cadence, target_stage, target_confidence, last_run_at, next_run_at, created_at, updated_at
        ) values (?, ?, ?, ?, ?, NULL, ?, ?, ?)
        on conflict(tracked_repository_id) do update set
          enabled=excluded.enabled,
          cadence=excluded.cadence,
          target_stage=excluded.target_stage,
          target_confidence=excluded.target_confidence,
          next_run_at=excluded.next_run_at,
          updated_at=excluded.updated_at
        """,
        (tracked_repository_id, 1 if enabled else 0, cadence, target_stage, target_confidence, _next_run_for_cadence(cadence), now, now),
    )


def list_due_followup_jobs(connection: Connection) -> list[Row]:
    return connection.execute(
        """
        select
          fj.tracked_repository_id,
          fj.target_stage,
          fj.target_confidence,
          fj.cadence,
          tr.repo_normalized,
          tr.default_branch,
          tu.telegram_user_id,
          tu.username,
          tu.first_name,
          tu.last_name,
          ir.report_json
        from followup_jobs fj
        join tracked_repositories tr on tr.id = fj.tracked_repository_id
        join telegram_users tu on tu.id = tr.user_id
        join inspection_reports ir on ir.id = (
          select id from inspection_reports where tracked_repository_id = tr.id order by id desc limit 1
        )
        where fj.enabled = 1
          and tr.status = 'active'
          and (fj.next_run_at is null or fj.next_run_at <= ?)
        order by fj.next_run_at asc, fj.tracked_repository_id asc
        """,
        (utc_now(),),
    ).fetchall()


def mark_followup_job_run(connection: Connection, *, tracked_repository_id: int, stop_reached: bool) -> None:
    now = utc_now()
    if stop_reached:
        connection.execute(
            "update followup_jobs set enabled = 0, last_run_at = ?, next_run_at = NULL, updated_at = ? where tracked_repository_id = ?",
            (now, now, tracked_repository_id),
        )
    else:
        row = connection.execute(
            "select cadence from followup_jobs where tracked_repository_id = ?",
            (tracked_repository_id,),
        ).fetchone()
        cadence = row[0] if row else "daily"
        connection.execute(
            "update followup_jobs set last_run_at = ?, next_run_at = ?, updated_at = ? where tracked_repository_id = ?",
            (now, _next_run_for_cadence(cadence), now, tracked_repository_id),
        )


def archive_tracking(connection: Connection, *, tracked_repository_id: int) -> None:
    connection.execute(
        "update tracked_repositories set status = 'archived', updated_at = ? where id = ?",
        (utc_now(), tracked_repository_id),
    )
    connection.execute(
        "update followup_jobs set enabled = 0, updated_at = ? where tracked_repository_id = ?",
        (utc_now(), tracked_repository_id),
    )


def get_latest_report_for_user(connection: Connection, *, user_id: int) -> tuple[TrackedRepositoryRecord, InspectionReportRecord] | None:
    row = connection.execute(
        """
        select
          tr.id as tr_id,
          tr.user_id as tr_user_id,
          tr.repo_url as tr_repo_url,
          tr.repo_normalized as tr_repo_normalized,
          tr.default_branch as tr_default_branch,
          tr.status as tr_status,
          tr.created_at as tr_created_at,
          tr.updated_at as tr_updated_at,
          tr.last_checked_at as tr_last_checked_at,
          ir.id as ir_id,
          ir.tracked_repository_id as ir_tracked_repository_id,
          ir.trigger_kind as ir_trigger_kind,
          ir.report_json as ir_report_json,
          ir.stage as ir_stage,
          ir.confidence as ir_confidence,
          ir.verdict as ir_verdict,
          ir.top_risks_json as ir_top_risks_json,
          ir.top_fixes_json as ir_top_fixes_json,
          ir.demo_safe as ir_demo_safe,
          ir.launch_ready as ir_launch_ready,
          ir.handoff_ready as ir_handoff_ready,
          ir.created_at as ir_created_at
        from tracked_repositories tr
        join inspection_reports ir on ir.id = (
          select id from inspection_reports where tracked_repository_id = tr.id order by id desc limit 1
        )
        where tr.user_id = ?
        order by ir.id desc
        limit 1
        """,
        (user_id,),
    ).fetchone()
    if not row:
        return None

    tracked_repo = TrackedRepositoryRecord(
        id=row["tr_id"],
        user_id=row["tr_user_id"],
        repo_url=row["tr_repo_url"],
        repo_normalized=row["tr_repo_normalized"],
        default_branch=row["tr_default_branch"],
        status=row["tr_status"],
        created_at=row["tr_created_at"],
        updated_at=row["tr_updated_at"],
        last_checked_at=row["tr_last_checked_at"],
    )
    report = InspectionReportRecord(
        id=row["ir_id"],
        tracked_repository_id=row["ir_tracked_repository_id"],
        trigger_kind=row["ir_trigger_kind"],
        report_json=row["ir_report_json"],
        stage=row["ir_stage"],
        confidence=row["ir_confidence"],
        verdict=row["ir_verdict"],
        top_risks_json=row["ir_top_risks_json"],
        top_fixes_json=row["ir_top_fixes_json"],
        demo_safe=row["ir_demo_safe"],
        launch_ready=row["ir_launch_ready"],
        handoff_ready=row["ir_handoff_ready"],
        created_at=row["ir_created_at"],
    )
    return tracked_repo, report
