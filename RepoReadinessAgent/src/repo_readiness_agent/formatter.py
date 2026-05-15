"""Formatting helpers for Repo Readiness Agent product output."""

from __future__ import annotations

from .contract import ProductReport


def render_text_report(report: ProductReport) -> str:
    lines = [
        f"Stage: {report.stage}",
        f"Verdict: {report.verdict}",
        f"Confidence: {report.confidence}",
        "",
        "Top risks:",
    ]
    lines.extend(f"- {risk}" for risk in report.top_risks)
    lines.append("")
    lines.append("Top 3 fixes:")
    lines.extend(f"- {fix}" for fix in report.top_fixes)

    if report.gates:
        lines.extend(
            [
                "",
                "Founder gates:",
                f"- Demo-safe? {report.gates.demo_safe}",
                f"- Launch-ready? {report.gates.launch_ready}",
                f"- Handoff-ready? {report.gates.handoff_ready}",
            ]
        )

    if report.follow_up:
        lines.extend(
            [
                "",
                "Follow-up:",
                f"- Status: {report.follow_up.status}",
                f"- Stop condition: {report.follow_up.stop_condition}",
            ]
        )

    return "\n".join(lines)
