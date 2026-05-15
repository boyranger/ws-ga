from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from repo_readiness_agent.contract import FollowUpStatus, FounderGates, ProductReport
from repo_readiness_agent.followup import build_follow_up

BASE = Path(__file__).resolve().parent


def load_report(path: Path) -> ProductReport:
    data = json.loads(path.read_text())
    gates = data.get("gates")
    follow_up = data.get("follow_up")
    return ProductReport(
        stage=data["stage"],
        verdict=data["verdict"],
        confidence=data["confidence"],
        top_risks=data["top_risks"],
        top_fixes=data["top_fixes"],
        gates=FounderGates(**gates) if gates else None,
        follow_up=FollowUpStatus(**follow_up) if follow_up else None,
    )


def main() -> None:
    before = load_report(BASE / "qris_payment_bot_followup_before.json")
    after = load_report(BASE / "qris_payment_bot_followup_after.json")
    result = build_follow_up(before, after)

    output = {
        "before_stage": before.stage,
        "after_stage": after.stage,
        "before_confidence": before.confidence,
        "after_confidence": after.confidence,
        "follow_up": asdict(result),
    }
    (BASE / "qris_payment_bot_followup_result.json").write_text(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
