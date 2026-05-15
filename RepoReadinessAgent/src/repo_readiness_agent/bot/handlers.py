"""Telegram command handlers for Repo Readiness Agent."""

from __future__ import annotations

import re
from typing import Any

from ..formatter import build_fix_prompts, build_founder_relays, render_text_report
from .service import NotFoundError, RepoTrackingService, ValidationError

_GITHUB_URL_RE = re.compile(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?/?")
_TELEGRAM_TEXT_LIMIT = 3800


def _chunk_text(text: str, limit: int = _TELEGRAM_TEXT_LIMIT) -> list[str]:
    text = text.strip()
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    remaining = text
    while len(remaining) > limit:
        split_at = remaining.rfind("\n\n", 0, limit)
        if split_at == -1:
            split_at = remaining.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = remaining.rfind(" ", 0, limit)
        if split_at == -1 or split_at < int(limit * 0.6):
            split_at = limit
        chunk = remaining[:split_at].strip()
        if chunk:
            chunks.append(chunk)
        remaining = remaining[split_at:].strip()

    if remaining:
        chunks.append(remaining)
    return chunks


async def _reply_text_safe(message: Any, text: str) -> None:
    for chunk in _chunk_text(text):
        await message.reply_text(chunk)


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
    await _reply_text_safe(
        update.effective_message,
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
    await _reply_text_safe(
        update.effective_message,
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
        await _reply_text_safe(
            update.effective_message,
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
    await _reply_text_safe(update.effective_message, "\n".join(lines))


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
        await _reply_text_safe(
            update.effective_message,
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
        await _reply_text_safe(
            update.effective_message,
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


def _extract_github_url(text: str) -> str | None:
    match = _GITHUB_URL_RE.search(text)
    return match.group(0) if match else None


def _has_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


async def conversational_message_handler(update: Any, context: Any) -> None:
    if not update.effective_message or not update.effective_message.text:
        return

    text = update.effective_message.text.strip()
    if text.startswith("/"):
        return

    lowered = text.lower()
    user_id, username, first_name, last_name = _telegram_user_parts(update)
    service: RepoTrackingService = context.application.bot_data["repo_tracking_service"]
    repo_url = _extract_github_url(text)

    try:
        state = service.get_conversation_state(
            telegram_user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        active_repo_url = repo_url or (state.active_repo_url if state else None)
        active_tracking_id = state.active_tracking_id if state else None

        wants_track = _has_any(lowered, ["track", "pantau", "monitor", "ikuti repo ini"])
        wants_inspect = _has_any(lowered, ["inspect", "inspeksi", "cek", "review", "nilai", "analyze", "analisa", "lihat readiness", "cek repo ini"])
        wants_followup = _has_any(lowered, ["cek lagi", "followup", "follow up", "review lagi", "cek ulang", "yang tadi cek lagi"])
        wants_list = _has_any(lowered, ["repo saya", "my repos", "myrepo", "myrepos", "repos saya", "tracked repo"])
        wants_help = _has_any(lowered, ["help", "bantuan", "cara pakai", "gimana pakainya"])
        wants_risks = _has_any(lowered, ["risk utama", "risiko utama", "masalah utama", "top risk"])
        wants_prompts = _has_any(lowered, ["prompt", "prompt perbaikan", "prompt fix", "prompt rekomendasi"])
        wants_fixes = _has_any(lowered, ["fix", "perbaikan", "langkah berikutnya", "next step", "apa yang harus dilakukan"])
        wants_summary = _has_any(lowered, ["summary", "ringkas", "ringkasan", "jelaskan hasil", "hasil terakhir"])
        wants_gates = _has_any(lowered, ["launch-ready", "launch ready", "handoff-ready", "handoff ready", "demo-safe", "demo safe", "siap launch", "siap handoff", "aman buat demo"])
        wants_confidence = _has_any(lowered, ["confidence", "keyakinan", "seberapa yakin", "yakin ga"])
        wants_latest_repo = _has_any(lowered, ["repo terakhir", "analisis terakhir", "repo yang terakhir dicek"])
        wants_founder_relay = _has_any(lowered, ["relay", "delegasikan", "solo founder", "kerjakan sendiri", "delegasi ke engineer"])

        if wants_track and active_repo_url:
            tracked = service.enable_tracking(
                telegram_user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                repo_url=active_repo_url,
            )
            await _reply_text_safe(
                update.effective_message,
                f"Siap, repo ini sekarang saya track.\nTracking ID: {tracked.id}\nRepo: {tracked.repo_normalized}\n\nKalau mau cek update nanti, bilang saja 'cek lagi repo ini' atau pakai /followup {tracked.id}."
            )
            return

        if wants_followup and active_tracking_id:
            result = service.run_followup_for_tracking(
                telegram_user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                tracking_id=active_tracking_id,
            )
            await _reply_text_safe(
                update.effective_message,
                f"Saya sudah cek ulang repo aktif kamu.\nTracking ID: {result.tracked_repo.id}\nRepo: {result.tracked_repo.repo_normalized}\n\n{result.rendered_text}"
            )
            return

        if wants_inspect and active_repo_url:
            result = service.inspect_repo(
                telegram_user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                repo_url=active_repo_url,
            )
            await _reply_text_safe(
                update.effective_message,
                f"Saya sudah cek repo ini.\nTracking ID: {result.tracking_id}\n\n{result.rendered_text}\n\nKalau kamu mau, lanjut bilang 'track repo ini'."
            )
            return

        if wants_list:
            repos = service.list_repos_for_user(
                telegram_user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
            if not repos:
                await update.effective_message.reply_text("Kamu belum punya repo yang di-track. Kirim link GitHub dan bilang mau saya cek atau track.")
                return
            lines = ["Ini repo yang sedang kamu track:"]
            for item in repos:
                latest = f"{item.latest_stage} / {item.latest_confidence}" if item.latest_stage else "belum ada report"
                lines.append(f"- #{item.tracking_id} {item.repo_normalized} [{item.status}] — {latest}")
            await _reply_text_safe(update.effective_message, "\n".join(lines))
            return

        if wants_help:
            await help_handler(update, context)
            return

        latest_analysis = service.get_latest_analysis_for_user(
            telegram_user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        if latest_analysis:
            report = latest_analysis.report
            tracked_repo = latest_analysis.tracked_repo

            if wants_risks:
                risks = "\n".join(f"- {risk}" for risk in report.top_risks)
                await update.effective_message.reply_text(
                    f"Dari analisis terakhir untuk {tracked_repo.repo_normalized}, risiko utamanya adalah:\n{risks}"
                )
                return

            if wants_prompts:
                prompts = build_fix_prompts(report)
                await _reply_text_safe(
                    update.effective_message,
                    f"Ini prompt rekomendasi untuk {tracked_repo.repo_normalized}:\n\n" + "\n\n".join(prompts)
                )
                return

            if wants_fixes:
                fixes = "\n".join(f"- {fix}" for fix in report.top_fixes)
                await update.effective_message.reply_text(
                    f"Untuk repo {tracked_repo.repo_normalized}, langkah perbaikan yang paling disarankan sekarang:\n{fixes}"
                )
                return

            if wants_summary:
                await _reply_text_safe(
                    update.effective_message,
                    f"Ini ringkasan analisis terakhir untuk {tracked_repo.repo_normalized}:\n\n{render_text_report(report)}"
                )
                return

            if wants_gates:
                if report.gates:
                    await update.effective_message.reply_text(
                        f"Untuk {tracked_repo.repo_normalized}:\n"
                        f"- Demo-safe: {report.gates.demo_safe}\n"
                        f"- Launch-ready: {report.gates.launch_ready}\n"
                        f"- Handoff-ready: {report.gates.handoff_ready}"
                    )
                    return

            if wants_confidence:
                await update.effective_message.reply_text(
                    f"Confidence analisis terakhir untuk {tracked_repo.repo_normalized}: {report.confidence}.\nVerdict-nya: {report.verdict}"
                )
                return

            if wants_latest_repo:
                await update.effective_message.reply_text(
                    f"Repo terakhir yang kamu cek adalah {tracked_repo.repo_normalized}.\nTracking ID: {tracked_repo.id}"
                )
                return

            if wants_founder_relay:
                relays = build_founder_relays(report)
                await _reply_text_safe(
                    update.effective_message,
                    f"Ini relay founder-facing untuk {tracked_repo.repo_normalized}:\n\n" + "\n\n".join(relays)
                )
                return

        if repo_url:
            await update.effective_message.reply_text(
                "Saya lihat kamu kirim link repo GitHub.\n\n"
                "Kamu bisa bilang misalnya:\n"
                f"- cek repo ini {repo_url}\n"
                f"- track repo ini {repo_url}\n\n"
                "Atau pakai command:\n"
                f"- /inspect {repo_url}\n"
                f"- /track {repo_url}"
            )
            return

        await update.effective_message.reply_text(
            "Aku bisa bantu secara lebih natural, bukan cuma lewat command.\n\n"
            "Contoh yang bisa kamu bilang:\n"
            "- cek repo ini https://github.com/owner/repo\n"
            "- track repo ini\n"
            "- cek lagi repo yang tadi\n"
            "- apa risiko utamanya?\n"
            "- beri prompt perbaikannya\n"
            "- relay buat solo founder dong\n\n"
            "Command tetap ada sebagai fallback. Ketik /help kalau mau lihat semuanya."
        )
    except (ValidationError, NotFoundError) as exc:
        await update.effective_message.reply_text(str(exc))
    except Exception as exc:
        await update.effective_message.reply_text(f"Maaf, saya gagal memproses pesan itu: {exc}")
