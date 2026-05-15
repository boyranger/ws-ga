"""Telegram command handlers for Repo Readiness Agent."""

from __future__ import annotations

from typing import Any

from ..formatter import render_text_report
from .service import NotFoundError, RepoTrackingService, ValidationError


def _telegram_user_parts(update: Any) -> tuple[str, str | None, str | None, str | None]:
    user = update.effective_user
    if user is None:
        raise ValidationError("Could not resolve Telegram user identity.")
    return str(user.id), user.username, user.first_name, user.last_name


async def start_handler(update: Any, context: Any) -> None:
    user_id, username, first_name, last_name = _telegram_user_parts(update)
    service: RepoTrackingService = context.application.bot_data["repo_tracking_service"]
    service._upsert_user(user_id, username, first_name, last_name)
    await update.effective_message.reply_text(
        "RepoReadinessAgent is ready.\n\n"
        "Try: /inspect https://github.com/owner/repo\n"
        "Then use /myrepos to see your tracked repositories."
    )


async def inspect_handler(update: Any, context: Any) -> None:
    user_id, username, first_name, last_name = _telegram_user_parts(update)
    service: RepoTrackingService = context.application.bot_data["repo_tracking_service"]
    if not context.args:
        await update.effective_message.reply_text("Usage: /inspect https://github.com/owner/repo")
        return
    repo_url = context.args[0]
    try:
        result = service.inspect_repo(
            telegram_user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            repo_url=repo_url,
        )
        await update.effective_message.reply_text(
            f"Tracking ID: {result.tracking_id}\n\n{result.rendered_text}"
        )
    except ValidationError as exc:
        await update.effective_message.reply_text(str(exc))
    except Exception as exc:
        await update.effective_message.reply_text(f"Inspection failed: {exc}")


async def myrepos_handler(update: Any, context: Any) -> None:
    user_id, username, first_name, last_name = _telegram_user_parts(update)
    service: RepoTrackingService = context.application.bot_data["repo_tracking_service"]
    repos = service.list_repos_for_user(
        telegram_user_id=user_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
    )
    if not repos:
        await update.effective_message.reply_text("You do not have any tracked repositories yet. Use /inspect first.")
        return
    lines = ["Your tracked repositories:"]
    for item in repos:
        latest = f"{item.latest_stage} / {item.latest_confidence}" if item.latest_stage else "no report yet"
        lines.append(f"- #{item.tracking_id} {item.repo_normalized} [{item.status}] — {latest}")
    await update.effective_message.reply_text("\n".join(lines))


async def report_handler(update: Any, context: Any) -> None:
    user_id, username, first_name, last_name = _telegram_user_parts(update)
    service: RepoTrackingService = context.application.bot_data["repo_tracking_service"]
    if not context.args:
        await update.effective_message.reply_text("Usage: /report <tracking_id>")
        return
    try:
        tracking_id = int(context.args[0])
    except ValueError:
        await update.effective_message.reply_text("Tracking ID must be a number.")
        return
    try:
        tracked_repo, report = service.get_report_for_tracking(
            telegram_user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            tracking_id=tracking_id,
        )
        await update.effective_message.reply_text(
            f"Tracking ID: {tracked_repo.id}\nRepo: {tracked_repo.repo_normalized}\n\n{render_text_report(report)}"
        )
    except (ValidationError, NotFoundError) as exc:
        await update.effective_message.reply_text(str(exc))
    except Exception as exc:
        await update.effective_message.reply_text(f"Could not load report: {exc}")
