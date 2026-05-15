"""Cron-friendly follow-up runner for Repo Readiness Agent."""

from __future__ import annotations

import json
import os
from dataclasses import asdict

from ..formatter import render_text_report
from .app import build_service
from .handlers import _chunk_text


def _send_telegram_message(token: str, chat_id: str, text: str) -> None:
    try:
        import requests
    except ImportError as exc:
        raise SystemExit("requests is required for Telegram follow-up delivery.") from exc

    for chunk in _chunk_text(text):
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": chunk},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        if not payload.get("ok"):
            raise RuntimeError(f"Telegram sendMessage failed: {payload}")


def main() -> None:
    service = build_service()
    results = service.run_due_followups()
    token = os.getenv("REPO_READINESS_TELEGRAM_BOT_TOKEN")

    delivered = 0
    delivery_errors: list[dict[str, str | int]] = []

    if token:
        for item in results:
            message = (
                f"Autocheck harian RepoReadinessAgent\n"
                f"Tracking ID: {item.tracking_id}\n"
                f"Repo: {item.repo_url}\n\n"
                f"{render_text_report(item.report)}"
            )
            try:
                _send_telegram_message(token, item.telegram_user_id, message)
                delivered += 1
            except Exception as exc:
                delivery_errors.append(
                    {
                        "telegram_user_id": item.telegram_user_id,
                        "tracking_id": item.tracking_id,
                        "repo_url": item.repo_url,
                        "error": str(exc),
                    }
                )

    payload = {
        "processed": len(results),
        "delivered": delivered,
        "delivery_errors": delivery_errors,
        "items": [
            {
                "telegram_user_id": item.telegram_user_id,
                "tracking_id": item.tracking_id,
                "repo_url": item.repo_url,
                "report": asdict(item.report),
            }
            for item in results
        ],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
