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
    name = first_name or username or "there"
    await update.effective_message.reply_text(
        f"Hi {name} — welcome to RepoReadinessAgent.\n\n"
        "I help you inspect a GitHub repository, judge its readiness stage, and track its progress over time.\n\n"
        "What you can do here:\n"
        "- inspect a repo and get a founder-friendly readiness report\n"
        "- save that repo under your own tracking record\n"
        "- re-check later and compare whether it improved\n\n"
        "Best first step:\n"
        "1. Send /inspect https://github.com/owner/repo\n"
        "2. Review the stage, verdict, top risks, and top fixes\n"
        "3. If you want monitoring, use /track https://github.com/owner/repo\n\n"
        "Use /help to see all commands."
    )


async def help_handler(update: Any, context: Any) -> None:
    del context
    await update.effective_message.reply_text(
        "RepoReadinessAgent commands:\n\n"
        "/start — introduction and first steps\n"
        "/help — show this command list\n"
        "/inspect <github_url> — inspect a repo and generate a readiness report\n"
        "/track <github_url> — save a repo and enable tracking for it\n"
        "/myrepos — list your tracked repositories\n"
        "/report <tracking_id> — show the latest saved report\n"
        "/followup <tracking_id> — re-check a tracked repo and compare progress\n"
        "/untrack <tracking_id> — disable tracking for a repo\n\n"
        "Recommended flow:\n"
        "1. /inspect a GitHub repo\n"
        "2. If useful, /track it\n"
        "3. Later, use /followup to see whether readiness improved"
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


async def track_handler(update: Any, context: Any) -> None:
    user_id, username, first_name, last_name = _telegram_user_parts(update)
    service: RepoTrackingService = context.application.bot_data["repo_tracking_service"]
    if not context.args:
        await update.effective_message.reply_text("Usage: /track https://github.com/owner/repo")
        return
    repo_url = context.args[0]
    try:
        tracked = service.enable_tracking(
            telegram_user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            repo_url=repo_url,
        )
        await update.effective_message.reply_text(
            f"Tracking enabled.\nTracking ID: {tracked.id}\nRepo: {tracked.repo_normalized}"
        )
    except ValidationError as exc:
        await update.effective_message.reply_text(str(exc))
    except Exception as exc:
        await update.effective_message.reply_text(f"Could not enable tracking: {exc}")


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


async def followup_handler(update: Any, context: Any) -> None:
    user_id, username, first_name, last_name = _telegram_user_parts(update)
    service: RepoTrackingService = context.application.bot_data["repo_tracking_service"]
    if not context.args:
        await update.effective_message.reply_text("Usage: /followup <tracking_id>")
        return
    try:
        tracking_id = int(context.args[0])
    except ValueError:
        await update.effective_message.reply_text("Tracking ID must be a number.")
        return
    try:
        result = service.run_followup_for_tracking(
            telegram_user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            tracking_id=tracking_id,
        )
        await update.effective_message.reply_text(
            f"Tracking ID: {result.tracked_repo.id}\nRepo: {result.tracked_repo.repo_normalized}\n\n{result.rendered_text}"
        )
    except (ValidationError, NotFoundError) as exc:
        await update.effective_message.reply_text(str(exc))
    except Exception as exc:
        await update.effective_message.reply_text(f"Could not run follow-up: {exc}")


async def untrack_handler(update: Any, context: Any) -> None:
    user_id, username, first_name, last_name = _telegram_user_parts(update)
    service: RepoTrackingService = context.application.bot_data["repo_tracking_service"]
    if not context.args:
        await update.effective_message.reply_text("Usage: /untrack <tracking_id>")
        return
    try:
        tracking_id = int(context.args[0])
    except ValueError:
        await update.effective_message.reply_text("Tracking ID must be a number.")
        return
    try:
        tracked = service.disable_tracking(
            telegram_user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            tracking_id=tracking_id,
        )
        await update.effective_message.reply_text(
            f"Tracking disabled.\nTracking ID: {tracked.id}\nRepo: {tracked.repo_normalized}"
        )
    except (ValidationError, NotFoundError) as exc:
        await update.effective_message.reply_text(str(exc))
    except Exception as exc:
        await update.effective_message.reply_text(f"Could not disable tracking: {exc}")
