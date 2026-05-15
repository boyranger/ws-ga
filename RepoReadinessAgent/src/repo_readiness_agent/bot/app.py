"""Runtime entrypoint for the public Repo Readiness Agent Telegram bot."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from .handlers import (
    conversational_message_handler,
    followup_handler,
    help_handler,
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

logger = logging.getLogger(__name__)

BOT_COMMANDS = [
    ("start", "Mulai dan lihat pengantar bot"),
    ("help", "Lihat daftar command"),
    ("inspect", "Inspeksi repo GitHub"),
    ("track", "Simpan repo dan aktifkan tracking"),
    ("myrepos", "Lihat daftar repo yang kamu track"),
    ("report", "Lihat report terakhir berdasarkan tracking ID"),
    ("followup", "Cek ulang repo yang di-track"),
    ("untrack", "Matikan tracking repo"),
]


def build_service() -> RepoTrackingService:
    db_path = Path(os.getenv("REPO_READINESS_DB_PATH", DEFAULT_DB_PATH))
    return RepoTrackingService(Database(db_path))


async def _error_handler(update: object, context: object) -> None:
    logger.exception("Unhandled Telegram bot error", exc_info=getattr(context, "error", None))
    try:
        message = getattr(update, "effective_message", None)
        if message is not None:
            await message.reply_text("Maaf, terjadi error saat memproses pesanmu. Coba lagi dengan pesan yang lebih singkat atau command yang lebih spesifik.")
    except Exception:
        logger.exception("Failed to send Telegram error fallback")


def main() -> None:
    try:
        from telegram import BotCommand
        from telegram.ext import Application, CommandHandler, MessageHandler, filters
    except ImportError as exc:
        raise SystemExit(
            "python-telegram-bot is not installed. Install it before running the public bot runtime."
        ) from exc

    token = os.getenv("REPO_READINESS_TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("REPO_READINESS_TELEGRAM_BOT_TOKEN is required.")

    async def _post_init(application: Application) -> None:
        await application.bot.set_my_commands(
            [BotCommand(command=name, description=description) for name, description in BOT_COMMANDS]
        )

    logging.basicConfig(level=logging.INFO)

    application = Application.builder().token(token).post_init(_post_init).build()
    application.bot_data["repo_tracking_service"] = build_service()

    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("inspect", inspect_handler))
    application.add_handler(CommandHandler("track", track_handler))
    application.add_handler(CommandHandler("myrepos", myrepos_handler))
    application.add_handler(CommandHandler("report", report_handler))
    application.add_handler(CommandHandler("followup", followup_handler))
    application.add_handler(CommandHandler("untrack", untrack_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, conversational_message_handler))
    application.add_error_handler(_error_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
