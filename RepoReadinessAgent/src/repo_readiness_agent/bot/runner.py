"""Cron-friendly follow-up runner for Repo Readiness Agent."""

from __future__ import annotations

import json
from dataclasses import asdict

from .app import build_service


def main() -> None:
    service = build_service()
    results = service.run_due_followups()
    payload = {
        "processed": len(results),
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
