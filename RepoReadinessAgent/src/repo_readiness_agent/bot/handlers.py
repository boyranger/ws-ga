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
    name = first_name or username or "teman"
    await update.effective_message.reply_text(
        f"Halo {name} — selamat datang di RepoReadinessAgent.\n\n"
        "Saya membantu kamu menginspeksi repository GitHub, menilai tahap kesiapan repo, dan melacak progresnya dari waktu ke waktu.\n\n"
        "Yang bisa kamu lakukan di sini:\n"
        "- inspeksi repo dan dapatkan readiness report yang mudah dipahami\n"
        "- simpan repo itu ke tracking milikmu sendiri\n"
        "- cek ulang nanti dan bandingkan apakah repo-nya membaik\n\n"
        "Langkah awal yang disarankan:\n"
        "1. Kirim /inspect https://github.com/owner/repo\n"
        "2. Lihat stage, verdict, top risks, dan top fixes\n"
        "3. Kalau mau dimonitor, pakai /track https://github.com/owner/repo\n\n"
        "Ketik /help untuk melihat semua command."
    )


async def help_handler(update: Any, context: Any) -> None:
    del context
    await update.effective_message.reply_text(
        "Command RepoReadinessAgent:\n\n"
        "/start — pengantar dan langkah pertama\n"
        "/help — tampilkan daftar command ini\n"
        "/inspect <github_url> — inspeksi repo dan buat readiness report\n"
        "/track <github_url> — simpan repo dan aktifkan tracking\n"
        "/myrepos — lihat daftar repo yang kamu track\n"
        "/report <tracking_id> — tampilkan report terakhir yang tersimpan\n"
        "/followup <tracking_id> — cek ulang repo yang di-track dan bandingkan progresnya\n"
        "/untrack <tracking_id> — nonaktifkan tracking repo\n\n"
        "Alur yang disarankan:\n"
        "1. Jalankan /inspect untuk repo GitHub\n"
        "2. Kalau berguna, lanjut /track\n"
        "3. Nanti pakai /followup untuk lihat apakah readiness-nya membaik"
    )


async def inspect_handler(update: Any, context: Any) -> None:
    user_id, username, first_name, last_name = _telegram_user_parts(update)
    service: RepoTrackingService = context.application.bot_data["repo_tracking_service"]
    if not context.args:
        await update.effective_message.reply_text("Cara pakai: /inspect https://github.com/owner/repo")
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
        await update.effective_message.reply_text(f"Inspect gagal: {exc}")


async def track_handler(update: Any, context: Any) -> None:
    user_id, username, first_name, last_name = _telegram_user_parts(update)
    service: RepoTrackingService = context.application.bot_data["repo_tracking_service"]
    if not context.args:
        await update.effective_message.reply_text("Cara pakai: /track https://github.com/owner/repo")
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
            f"Tracking aktif.\nTracking ID: {tracked.id}\nRepo: {tracked.repo_normalized}"
        )
    except ValidationError as exc:
        await update.effective_message.reply_text(str(exc))
    except Exception as exc:
        await update.effective_message.reply_text(f"Gagal mengaktifkan tracking: {exc}")


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
        await update.effective_message.reply_text("Kamu belum punya repo yang di-track. Jalankan /inspect dulu.")
        return
    lines = ["Daftar repo yang kamu track:"]
    for item in repos:
        latest = f"{item.latest_stage} / {item.latest_confidence}" if item.latest_stage else "belum ada report"
        lines.append(f"- #{item.tracking_id} {item.repo_normalized} [{item.status}] — {latest}")
    await update.effective_message.reply_text("\n".join(lines))


async def report_handler(update: Any, context: Any) -> None:
    user_id, username, first_name, last_name = _telegram_user_parts(update)
    service: RepoTrackingService = context.application.bot_data["repo_tracking_service"]
    if not context.args:
        await update.effective_message.reply_text("Cara pakai: /report <tracking_id>")
        return
    try:
        tracking_id = int(context.args[0])
    except ValueError:
        await update.effective_message.reply_text("Tracking ID harus berupa angka.")
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
        await update.effective_message.reply_text(f"Gagal memuat report: {exc}")


async def followup_handler(update: Any, context: Any) -> None:
    user_id, username, first_name, last_name = _telegram_user_parts(update)
    service: RepoTrackingService = context.application.bot_data["repo_tracking_service"]
    if not context.args:
        await update.effective_message.reply_text("Cara pakai: /followup <tracking_id>")
        return
    try:
        tracking_id = int(context.args[0])
    except ValueError:
        await update.effective_message.reply_text("Tracking ID harus berupa angka.")
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
        await update.effective_message.reply_text(f"Gagal menjalankan follow-up: {exc}")


async def untrack_handler(update: Any, context: Any) -> None:
    user_id, username, first_name, last_name = _telegram_user_parts(update)
    service: RepoTrackingService = context.application.bot_data["repo_tracking_service"]
    if not context.args:
        await update.effective_message.reply_text("Cara pakai: /untrack <tracking_id>")
        return
    try:
        tracking_id = int(context.args[0])
    except ValueError:
        await update.effective_message.reply_text("Tracking ID harus berupa angka.")
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
            f"Tracking dimatikan.\nTracking ID: {tracked.id}\nRepo: {tracked.repo_normalized}"
        )
    except (ValidationError, NotFoundError) as exc:
        await update.effective_message.reply_text(str(exc))
    except Exception as exc:
        await update.effective_message.reply_text(f"Gagal mematikan tracking: {exc}")
