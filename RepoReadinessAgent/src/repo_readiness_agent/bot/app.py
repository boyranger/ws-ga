"""Runtime entrypoint for the public Repo Readiness Agent Telegram bot."""

from __future__ import annotations

import os
from pathlib import Path

from .handlers import (
    followup_handler,
    inspect_handler,
    myrepos_handler,
    report_handler,
    start_handler,
    track_handler,
    untrack_handler,
)
from .service import RepoTrackingService
from .storage import Database

DEFAULT_DB_PATH = Path(__file__).resolve().parents[3] / "data" / "repo_readiness_agent.sqlite3"


def build_service() -> RepoTrackingService:
    db_path = Path(os.getenv("REPO_READINESS_DB_PATH", DEFAULT_DB_PATH))
    return RepoTrackingService(Database(db_path))


def main() -> None:
    try:
        from telegram.ext import Application, CommandHandler
    except ImportError as exc:
        raise SystemExit(
            "python-telegram-bot is not installed. Install it before running the public bot runtime."
        ) from exc

    token = os.getenv("REPO_READINESS_TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("REPO_READINESS_TELEGRAM_BOT_TOKEN is required.")

    application = Application.builder().token(token).build()
    application.bot_data["repo_tracking_service"] = build_service()

    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("inspect", inspect_handler))
    application.add_handler(CommandHandler("track", track_handler))
    application.add_handler(CommandHandler("myrepos", myrepos_handler))
    application.add_handler(CommandHandler("report", report_handler))
    application.add_handler(CommandHandler("followup", followup_handler))
    application.add_handler(CommandHandler("untrack", untrack_handler))

    application.run_polling()


if __name__ == "__main__":
    main()
